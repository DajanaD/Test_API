from abc import ABC, abstractmethod

from app.db.database import async_session
from app.repositories.comments import CommentsRepository
from app.repositories.posts import PostRepository
from app.repositories.users import UsersRepository
from app.repositories.black_list import BlackListRepository


class AuthRepository:
    pass


class IUnitOfWork(ABC):
    users: UsersRepository
    comments: CommentsRepository
    posts: PostRepository
    black_list: BlackListRepository

    @abstractmethod
    def __init__(self): ...

    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UsersRepository(self.session)
        self.comments = CommentsRepository(self.session)
        self.posts = PostRepository(self.session)
        self.black_list = BlackListRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
