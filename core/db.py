from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings

async_engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URL, future=True)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        yield session
