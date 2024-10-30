from fastapi import APIRouter, Depends, status, BackgroundTasks
import asyncio
from app.models.users import User
from app.models.comments import Comment, CommentStatus, CommentStatus
from app.schemas.comments import CommentSchemaAdd, CommentSchemaUpdate, CommentResponse,  CommentDailyBreakdown
from app.services.comments import CommentService
from app.services.auth import auth_service
from app.utils.dependencies import UOWDep
from app.utils.guard import guard
from datetime import date
import time

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=list[CommentResponse])
async def get_comment(
        uow: UOWDep,
        comment_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a list of all comments.

    This endpoint returns a list of all comments from the database. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        comment_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        list[CommentResponse]: A list of comment objects with details.
    """
    comments = await comment_service.get_comments(uow)
    return comments


@router.get("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def get_comment(
        comment_id: int,
        uow: UOWDep,
        comments_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a specific comment by its ID.

    This endpoint returns details of a comment identified by its unique ID. Access is restricted to admin users only.

    Args:
        comment_id (int): The ID of the comment to retrieve.
        uow (UOWDep): Dependency for unit of work management.
        comments_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CommentResponse: Details of the comment with the specified ID.
    """
    return await comments_service.get_comment_by_id(uow, comment_id)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
        uow: UOWDep,
        comment_data: CommentSchemaAdd,
        comments_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Add a new comment to the database.

    This endpoint adds a new comment based on the provided data and returns the details of the newly created comment. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        comment_data (CommentSchemaAdd): Data required to create a new comment.
        comments_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CommentResponse: Details of the newly created comment.
    """
    comment_id = await comments_service.add_comment(uow, comment_data)
    return await comments_service.get_comment_by_id(uow, comment_id)


@router.put("/{comment_id}", response_model=CommentResponse, status_code=status.HTTP_200_OK)
async def update_comment(
        comment_id: int,
        comment_data: CommentSchemaUpdate,
        uow: UOWDep,
        comments_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Update details of an existing comment.

    This endpoint updates the details of a comment identified by its ID. Access is restricted to admin users only. The current user must be the owner of the comment.

    Args:
        comment_id (int): The ID of the comment to update.
        comment_data (CommentSchemaUpdate): Updated data for the comment.
        uow (UOWDep): Dependency for unit of work management.
        comments_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CommentResponse: Details of the updated comment.
    """
    comment = await comments_service.get_comment_by_id(uow, comment_id)
    await guard.is_owner(current_user, comment)
    return await comments_service.update_comment(uow, comment_id, comment_data)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int,
        uow: UOWDep,
        comments_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Delete a comment by its ID.

    This endpoint deletes a comment identified by its ID from the database. Access is restricted to admin users only.

    Args:
        comment_id (int): The ID of the comment to delete.
        uow (UOWDep): Dependency for unit of work management.
        comments_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        None: No content is returned upon successful deletion.
    """
    await comments_service.delete_comment(uow, comment_id)
# Comment Analytics
@router.get("/daily-breakdown", response_model=list[CommentDailyBreakdown])
async def get_comments_daily_breakdown(
    date_from: date,
    date_to: date,
    uow: UOWDep,
    comment_service: CommentService = Depends(),
):
    """
    Retrieve daily breakdown of comments.

    This endpoint returns the count of created and blocked comments
    over a specified time period.

    Args:
        date_from (date): The starting date for analysis.
        date_to (date): The ending date for analysis.
        uow (UOWDep): Dependency for unit of work management.
        comment_service (CommentService): Service for managing comment-related operations.

    Returns:
        list[CommentDailyBreakdown]: A list of objects containing the count of created and blocked comments by day.
    """
    return await comment_service.get_comments_daily_breakdown(uow, date_from, date_to)

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment_with_autoreply(
    uow: UOWDep,
    comment_data: CommentSchemaAdd,
    comments_service: CommentService = Depends(),
    current_user: User = Depends(guard.is_admin),
    background_tasks: BackgroundTasks = Depends()
):
    """
    Add a new comment to the database.

    This endpoint creates a new comment based on the provided data and 
    returns the details of the created comment. If the user has 
    auto-replies enabled, a task to send the reply is added to the background.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        comment_data (CommentSchemaAdd): Data required to create a new comment.
        comments_service (CommentService): Service for managing comment-related operations.
        current_user (User): The currently authenticated user, required for access control.
        background_tasks (BackgroundTasks): Dependency for managing background tasks.

    Returns:
        CommentResponse: Details of the newly created comment.
    """
    comment_id = await comments_service.add_comment(uow, comment_data)

    # If auto-reply is enabled, add a task
    user = await comments_service.get_user_by_id(comment_data.owner_id)
    if user.auto_reply_enabled:
        delay = user.auto_reply_delay
        background_tasks.add_task(send_auto_reply, uow, comment_id, delay)

    return await comments_service.get_comment_by_id(uow, comment_id)

async def send_auto_reply(uow: UOWDep, comment_id: int, delay: int):
    """
    Send an automatic reply after a delay.

    This function sends an automatic reply to a comment after the specified delay.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        comment_id (int): The ID of the comment to which the reply is sent.
        delay (int): The delay in seconds before sending the reply.
    """
    await asyncio.sleep(delay)
    
    # Logic for sending the reply
    async with uow:
        comment = await uow.comments.get(comment_id)
        if comment:
            auto_reply_content = f"Спасибо за ваш комментарий: '{comment.description}'."
            await uow.comments.add(Comment(description=auto_reply_content, owner_id=comment.owner_id, status=CommentStatus.CREATED))
