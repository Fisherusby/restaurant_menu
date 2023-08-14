import contextlib
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings

async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, future=True)


@contextlib.asynccontextmanager
async def session_generator() -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def get_session() -> AsyncSession:
    async with session_generator() as session:
        yield session
