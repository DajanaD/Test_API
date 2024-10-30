from fastapi import APIRouter, Depends, status

from app.models.users import User
from app.models.comments import Comment
from app.schemas.comments import CommentSchemaAdd, CommentSchemaUpdate, CommentResponse
from app.services.comments import CommentService
from app.services.auth import auth_service
from app.utils.dependencies import UOWDep
from app.utils.guard import guard

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=list[CommentResponse])
async def get_comment(
        uow: UOWDep,
        comment_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Retrieve a list of all cars.

    This endpoint returns a list of all cars from the database. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        list[CarResponse]: A list of car objects with details.
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
    """Retrieve a specific car by its ID.

    This endpoint returns details of a car identified by its unique ID. Access is restricted to admin users only.

    Args:
        car_id (int): The ID of the car to retrieve.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the car with the specified ID.
    """
    return await comments_service.get_comment_by_id(uow, comment_id)


@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
        uow: UOWDep,
        comment_data: CommentSchemaAdd,
        comments_service: CommentService = Depends(),
        current_user: User = Depends(guard.is_admin),
):
    """Add a new car to the database.

    This endpoint adds a new car based on the provided data and returns the details of the newly created car. Access is restricted to admin users only.

    Args:
        uow (UOWDep): Dependency for unit of work management.
        car_data (CarSchemaAdd): Data required to create a new car.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the newly created car.
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
    """Update details of an existing car.

    This endpoint updates the details of a car identified by its ID. Access is restricted to admin users only. The current user must be the owner of the car.

    Args:
        car_id (int): The ID of the car to update.
        car_data (CarSchemaUpdate): Updated data for the car.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        CarResponse: Details of the updated car.
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
    """Delete a car by its ID.

    This endpoint deletes a car identified by its ID from the database. Access is restricted to admin users only.

    Args:
        car_id (int): The ID of the car to delete.
        uow (UOWDep): Dependency for unit of work management.
        cars_service (CarsService): Service for managing car-related operations.
        current_user (User): The currently authenticated user, required to be an admin.

    Returns:
        None: No content is returned upon successful deletion.
    """
    await comments_service.delete_comment(uow, comment_id)
