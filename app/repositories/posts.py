from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.posts import Post


class PostRepository(SQLAlchemyRepository):
    """Repository class for managing Post objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = Post

    async def find_all_posts(self, active_only: bool = False) -> list[Post]:
        """Finds all posts, optionally filtering by active status.

        Args:
            active_only (bool, optional): Whether to filter by active posts. Defaults to False.

        Returns:
            list[Post]: A list of Post objects.
        """
        stmt = select(self.model)
        if active_only:
            stmt = stmt.where(self.model.is_active == True)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def find_by_comment_id(self, comment_id: int) -> list[Post]:
        """Finds all posts associated with a specific comment ID.

        Args:
            comment_id (int): The ID of the comment.

        Returns:
            list[Post]: A list of Post objects.
        """
        stmt = select(self.model).where(self.model.comment_id == comment_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
