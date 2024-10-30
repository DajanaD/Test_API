from fastapi import APIRouter, Depends, status
from app.models.users import User
from app.schemas.posts import PostSchemaAdd, PostResponse, PostLiteResponse
from app.services.posts import PostService
from app.services.auth import auth_service
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=list[PostLiteResponse])
async def get_posts(
        uow: UOWDep,
        post_service: PostService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """
    Retrieve a list of all posts.

    This endpoint returns a list of all posts from the database. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        post_service (PostService): Service for managing post-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        list[PostLiteResponse]: A list of post objects with brief details.
    """
    posts = await post_service.get_posts(uow)
    return posts


@router.get("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def get_post(
        post_id: int,
        uow: UOWDep,
        post_service: PostService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """
    Retrieve a specific post by its ID.

    This endpoint returns details of a post identified by its unique ID. Access is restricted to admin users only.

    Args:
        post_id (int): The ID of the post to retrieve.
        uow (UOWDep): Dependency for unit of work management.
        post_service (PostService): Service for managing post-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        PostResponse: Details of the post with the specified ID.
    """
    return await post_service.get_post_by_id(uow, post_id)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def add_post(
        uow: UOWDep,
        post_data: PostSchemaAdd,
        post_service: PostService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """
    Add a new post to the database.

    This endpoint adds a new post based on the provided data and returns the details of the newly created post. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        post_data (PostSchemaAdd): Data required to create a new post.
        post_service (PostService): Service for managing post-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        PostResponse: Details of the newly created post.
    """
    post_id = await post_service.add_post(uow, post_data)
    return await post_service.get_post_by_id(uow, post_id)


@router.put("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def update_post(
        post_id: int,
        post_data: PostSchemaAdd,  # You may change this to a dedicated update schema
        uow: UOWDep,
        post_service: PostService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """
    Update details of an existing post.

    This endpoint updates the details of a post identified by its ID. Access is restricted to admin users only. The current user must be the owner of the post.

    Args:
        post_id (int): The ID of the post to update.
        post_data (PostSchemaAdd): Updated data for the post.
        uow (UOWDep): Dependency for unit of work management.
        post_service (PostService): Service for managing post-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        PostResponse: Details of the updated post.
    """
    post = await post_service.get_post_by_id(uow, post_id)
    await guard.is_owner(current_user, post)
    return await post_service.update_post(uow, post_id, post_data)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
        post_id: int,
        uow: UOWDep,
        post_service: PostService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """
    Delete a post by its ID.

    This endpoint deletes a post identified by its ID from the database. Access is restricted to admin users only.

    Args:
        post_id (int): The ID of the post to delete.
        uow (UOWDep): Dependency for unit of work management.
        post_service (PostService): Service for managing post-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        None: No content is returned upon successful deletion.
    """
    await post_service.delete_post(uow, post_id)
