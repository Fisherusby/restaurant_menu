import asyncio
import contextlib
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from core.db import async_engine
from core.main import app
from core.models.base import BaseDBModel
from core.settings import settings
from tests.utils import INIT_DATA_ALL, ApiTestService, CRUDDataBase


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Generator for test request client."""
    async with AsyncClient(app=app, base_url=f'http://{settings.API_PREFIX}') as client:
        yield client


def get_table_names(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


@contextlib.asynccontextmanager
async def async_session_generator(clear_db: bool = True) -> AsyncGenerator[AsyncSession, None]:
    """Generator for database sessions with drop/create objects in the database.

    Created before using and dropping after using.
    """
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            exist_tables = await conn.run_sync(get_table_names)
            if not {'menus', 'submenus', 'dishes'}.issubset(exist_tables):
                await conn.run_sync(BaseDBModel.metadata.create_all)  # type: ignore[attr-defined]
        yield s

    if clear_db:
        async with async_engine.begin() as conn:
            await conn.run_sync(BaseDBModel.metadata.drop_all)  # type: ignore[attr-defined]

    await async_engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def async_session(mock_redis) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_generator() as s:
        yield s


@pytest_asyncio.fixture
async def async_session_without_clear() -> AsyncGenerator[AsyncGenerator, None]:
    async with async_session_generator(clear_db=False) as s:
        yield s


@pytest_asyncio.fixture(scope='function')
async def async_crud(async_session: AsyncSession) -> AsyncGenerator[CRUDDataBase, None]:
    """Generator crud fixture with non-data DB."""
    yield CRUDDataBase(async_session)


@pytest.fixture(scope='session')
def init_db_data():
    """Prepare date for init test DB"""
    data_obj = []
    for table in INIT_DATA_ALL.values():
        tb_model = table['model']
        table_data: list[tuple] = table['data']
        for obj_data in table_data:
            data: dict[str, str] = dict(zip(table['mapping'], obj_data))
            data_obj.append([tb_model, data])
    return data_obj


@pytest.fixture(scope='function')
def generate_test_data(init_db_data) -> list:
    """Generate objects for init test DB with data."""
    return [obj[0](**obj[1]) for obj in init_db_data]


@pytest_asyncio.fixture(scope='function')
async def async_crud_with_data(generate_test_data, async_session: AsyncSession) -> AsyncGenerator[CRUDDataBase, None]:
    """Generator crud fixture with initialized data in DB."""
    for obj in generate_test_data:
        async_session.add(obj)
    await async_session.commit()
    yield CRUDDataBase(async_session)


@pytest_asyncio.fixture
async def api(async_client: AsyncClient) -> AsyncGenerator[ApiTestService, None]:
    """Fixture client for API test."""
    yield ApiTestService(async_client)


@pytest_asyncio.fixture(scope='class')
def buffer() -> Generator[dict[str, dict], None, None]:
    """Storage value between tests."""
    buffer_data: dict[str, dict] = {}
    yield buffer_data


@pytest_asyncio.fixture
async def mock_redis(monkeypatch) -> list:
    """Mocking redis services."""

    call_lst = []

    async def set_(*args, **kwargs):
        call_lst.append(('set', kwargs))

    async def get_(*args, **kwargs):
        call_lst.append(('get', kwargs))
        return None

    async def del_(*args, **kwargs):
        call_lst.append(('delete', kwargs))

    monkeypatch.setattr('core.services.redis.RadisCacheService.set', set_)
    monkeypatch.setattr('core.services.redis.RadisCacheService.get', get_)
    monkeypatch.setattr('core.services.redis.RadisCacheService.delete', del_)

    return call_lst
