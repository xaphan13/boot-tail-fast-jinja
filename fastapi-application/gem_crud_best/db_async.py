from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)

from sqlalchemy.orm import DeclarativeBase


# sqlite database test_fast_api.db
DATABASE_URL_ASYNC = f"sqlite+aiosqlite:///.app22/test_fast_api.db"
# DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# ========= base class for models =========== #
class Base(DeclarativeBase):
    __abstract__ = True


class AsyncSessionDB:
    async_engine: AsyncEngine
    async_session: async_sessionmaker[AsyncSession]

    def __init__(self, url: str, echo: bool = False):
        self.async_engine = create_async_engine(
            url,
            echo=echo,
            future=True,
        )

        self.async_session = async_sessionmaker(
            bind=self.async_engine,
            autoflush=False,
            expire_on_commit=False,
        )

    async def get_db(self) -> AsyncGenerator[AsyncSession]:
        """Dependency for getting session"""
        session: AsyncSession = self.async_session()
        try:
            yield session
        finally:
            await session.close()


async_session_factory = AsyncSessionDB(url=DATABASE_URL_ASYNC, echo=True)
