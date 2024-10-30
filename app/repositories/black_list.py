from sqlalchemy import select
from app.models.black_list import BlackList
from app.utils.repositories import SQLAlchemyRepository


class BlackListRepository(SQLAlchemyRepository):
    """Repository class for managing BlackList objects in the database.
    """


    model = BlackList

    async def get_blacklisted_words(self):
        """
        Retrieves a list of blacklisted words from the database.

        Returns:
            list[str]: A list of blacklisted words.
        """
        async with self.session() as session:
            result = await session.execute(select(self.model.reason))
            return [row[0] for row in result.fetchall()]