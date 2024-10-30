from sqlalchemy import select
from app.utils.repositories import SQLAlchemyRepository
from app.models.comments import Comment


class CommentsRepository(SQLAlchemyRepository):
    """Repository class for managing Comment objects in the database.

    Inherits from:
        SQLAlchemyRepository: Base repository class providing common database operations.
    """
    model = Comment

    async def find_by_owner_id(self, owner_id: int) -> list[Comment]:
        """Finds all comments associated with a specific owner ID.

        Args:
            owner_id (int): The ID of the owner.

        Returns:
            list[Comment]: A list of Comment objects.
        """
        stmt = select(self.model).where(self.model.owner_id == owner_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()
