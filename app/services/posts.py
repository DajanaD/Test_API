from fastapi import HTTPException, status
from app.utils.unitofwork import UnitOfWork
from app.models import Post
from app.schemas.posts import PostResponse, PostLiteResponse, PostPeriod

class PostService:
    """
    Service class for managing post operations, including adding, updating, retrieving, and deleting posts.
    """

    async def add_post(self, uow: UnitOfWork, post_data: dict) -> int:
        """
        Adds a new post to the system.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            post_data (dict): The data required to add a new post.

        Returns:
            int: The ID of the newly created post.

        Raises:
            HTTPException: If the comment related to the post is not found.
        """
        async with uow:
            comment = await uow.comments.find_one_or_none(id=post_data['comment_id'])
            if not comment:
                raise HTTPException(status_code=404, detail="Comment not found")

            post_id = await uow.posts.add_one(post_data)
            return post_id

    async def get_posts(self, uow: UnitOfWork) -> list[PostLiteResponse]:
        """
        Retrieves a list of all posts.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.

        Returns:
            list[PostLiteResponse]: A list of all posts.
        """
        async with uow:
            posts = await uow.posts.find_all()
            return [PostLiteResponse.from_orm(post) for post in posts]

    async def get_post_by_id(self, uow: UnitOfWork, post_id: int) -> PostResponse:
        """
        Retrieves a post by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            post_id (int): The ID of the post to retrieve.

        Returns:
            PostResponse: The response object containing post details.

        Raises:
            HTTPException: If the post is not found.
        """
        async with uow:
            post = await uow.posts.find_one_or_none(id=post_id)
            if post is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
                )
            return PostResponse.from_orm(post)

    async def update_post(self, uow: UnitOfWork, post_id: int, post_data: dict) -> PostResponse:
        """
        Updates details of an existing post.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            post_id (int): The ID of the post to update.
            post_data (dict): The new data for updating the post.

        Returns:
            PostResponse: The updated post details.

        Raises:
            HTTPException: If the post to update is not found.
        """
        async with uow:
            post = await uow.posts.find_one_or_none(id=post_id)
            if post is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
                )

            for key, value in post_data.items():
                setattr(post, key, value)

            await uow.commit()
            return PostResponse.from_orm(post)

    async def delete_post(self, uow: UnitOfWork, post_id: int) -> PostResponse:
        """
        Deletes a post by its ID.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            post_id (int): The ID of the post to delete.

        Returns:
            PostResponse: The deleted post details.

        Raises:
            HTTPException: If the post is not found.
        """
        async with uow:
            post = await uow.posts.find_one_or_none(id=post_id)
            if post is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
                )
            await uow.posts.delete_one(id=post_id)
            return post

    async def get_posts_by_period(self, uow: UnitOfWork, period: PostPeriod) -> list[PostLiteResponse]:
        """
        Retrieves all posts within a specific time period.

        Args:
            uow (UnitOfWork): The unit of work instance for database transactions.
            period (PostPeriod): The period to filter the posts by.

        Returns:
            list[PostLiteResponse]: A list of posts from the specified period.
        """
        async with uow:
            posts = await uow.posts.find_by_period(period)
            return [PostLiteResponse.from_orm(post) for post in posts]
