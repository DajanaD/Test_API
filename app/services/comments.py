from fastapi import HTTPException, status

from app.models import Comment
from app.utils.unitofwork import UnitOfWork
from app.schemas.comments import CommentSchemaAdd, CommentSchemaUpdate, CommentResponse



class CommentService:
    """
    Service class for managing comment operations, including adding, updating, retrieving, and deleting comments.
    """
    
    async def add_comment(self, uow: UnitOfWork, comment_data: CommentSchemaAdd) -> int:
        """
        Adds a new comment to the system.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            comment_data (CommentSchemaAdd): The data required to add a new comment.

        Returns:
            int: The ID of the newly created comment.

        Raises:
            HTTPException: If the owner is not found.
        """
        async with uow:
            owner = await uow.users.find_one_or_none(id=comment_data.owner_id)
            if not owner:
                raise HTTPException(status_code=404, detail="Owner not found")
            
            comment_dict = comment_data.model_dump()

            comment_id = await uow.comments.add_one(comment_dict)
            return comment_id

    async def get_comments(self, uow: UnitOfWork):
        """
        Retrieves a list of all comments.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[Comment]: A list of all comments.
        """
        async with uow:
            comments = await uow.comments.find_all()
            return comments

    async def get_comment_by_id(self, uow: UnitOfWork, comment_id: int) -> CommentResponse:
        """
        Retrieves a comment by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            comment_id (int): The ID of the comment to retrieve.

        Returns:
            CommentResponse: The response object containing comment details.

        Raises:
            HTTPException: If the comment is not found.
        """
        async with uow:
            comment = await uow.comments.find_one_or_none(id=comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
                )
            return CommentResponse.from_orm(comment)

    async def update_comment(
            self, uow: UnitOfWork, comment_id: int, comment_data: CommentSchemaUpdate
    ) -> CommentResponse:
        """
        Updates details of an existing comment.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            comment_id (int): The ID of the comment to update.
            comment_data (CommentSchemaUpdate): The new data for updating the comment.

        Returns:
            CommentResponse: The updated comment details.

        Raises:
            HTTPException: If the comment to update is not found.
        """
        async with uow:
            comment = await uow.comments.find_one_or_none(id=comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
                )

            for key, value in comment_data.model_dump().items():
                setattr(comment, key, value)

            await uow.commit()
            return CommentResponse.from_orm(comment)

    async def delete_comment(self, uow: UnitOfWork, comment_id: int) -> CommentResponse:
        """
        Deletes a comment by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            comment_id (int): The ID of the comment to delete.

        Returns:
            CommentResponse: The deleted comment details.

        Raises:
            HTTPException: If the comment is not found.
        """
        async with uow:
            comment = await uow.comments.find_one_or_none(id=comment_id)
            if comment is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
                )
            await uow.comments.delete_one(id=comment_id)
            return comment

    async def get_comments_by_owner_id(self, uow: UnitOfWork, owner_id: int) -> list[Comment]:
        """
        Retrieves all comments made by a specific user.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            owner_id (int): The ID of the comment owner.

        Returns:
            list[Comment]: A list of comments made by the specified user.
        """
        async with uow:
            comments = await uow.comments.find_by_owner_id(owner_id)
            return comments
