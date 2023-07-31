import contextlib

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from core import models
from core.db import async_engine
from core.main import app
from core.models.base import BaseDBModel
from core.settings import settings
from tests.utils.api import ApiTestService
from tests.utils.crud import CRUDDataBase


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """Generator for test request client."""
    async with AsyncClient(app=app, base_url=f"http://{settings.API_PREFIX}") as client:
        yield client


def get_table_names(conn):
    inspector = inspect(conn)
    return inspector.get_table_names()


@contextlib.asynccontextmanager
async def async_session_generator(clear_db: bool = True) -> AsyncSession:
    """Generator for database sessions with drop/create objects in the database.

    Created before using and dropping after using.
    """
    session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as s:
        async with async_engine.begin() as conn:
            exist_tables = await conn.run_sync(get_table_names)
            if not {'menus', 'submenus', 'dishes'}.issubset(exist_tables):
                await conn.run_sync(BaseDBModel.metadata.create_all)
        yield s

    if clear_db:
        async with async_engine.begin() as conn:
            await conn.run_sync(BaseDBModel.metadata.drop_all)

    await async_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    async with async_session_generator() as s:
        yield s


@pytest_asyncio.fixture
async def async_session_without_clear() -> AsyncSession:
    async with async_session_generator(clear_db=False) as s:
        yield s


@pytest_asyncio.fixture(scope="function")
async def async_crud(async_session):
    """Generator crud fixture with non-data DB."""
    yield CRUDDataBase(async_session)


@pytest.fixture(scope="function")
def generate_test_data():
    menu_mapping = ('id', 'title', 'description')
    submenu_mapping = ('id', 'menu_id', 'title', 'description')
    dish_mapping = ('id', 'submenu_id', 'title', 'description', 'price')
    init_data = {
        'menus': (
            ('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', 'Menu A', "Description menu A"),
            ('70eb2363-c1de-4daa-b7cd-6b98db17e841', 'Menu B', "Description menu B"),
            ('aafe18cc-7986-4f72-9e37-adafa0f1f5b3', 'Menu C', "Description menu C"),
        ),
        'submenus': (
            (
                "f98d48cb-4383-411c-bc71-ac653ce42e09",
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'Submenu AA',
                "Description submenu AA",
            ),
            (
                "c0861bf3-311d-4db7-8677-d7ee5052adc9",
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'Submenu AB',
                "Description submenu AB",
            ),
            (
                "e2564502-0848-42d7-84c1-28bfc84e5ee9",
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'Submenu BA',
                "Description submenu BA",
            ),
        ),
        'dishes': (
            (
                "2ee022d7-7557-44df-a88e-a0bfb102eb53",
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'Dish AA1',
                "Description dish AA1",
                "11.11",
            ),
            (
                "352590fa-434e-4436-b195-ada202625887",
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'Dish AA2',
                "Description dish AA2",
                "22.22",
            ),
            (
                "2bb5b495-6473-463f-9d9a-cb6372e89a3e",
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'Dish AA3',
                "Description dish AA3",
                "33.33",
            ),
            (
                "ffaa2434-b33d-490f-847d-a29318f4c106",
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'Dish AB1',
                "Description dish AB1",
                "44.44",
            ),
            (
                "dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f",
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'Dish AB2',
                "Description dish AB2",
                "55.55",
            ),
        ),
    }
    objs = []
    for obj_data in init_data['menus']:
        objs.append(models.MenuDBModel(**dict(zip(menu_mapping, obj_data))))
    for obj_data in init_data['submenus']:
        objs.append(models.SubmenuDBModel(**dict(zip(submenu_mapping, obj_data))))
    for obj_data in init_data['dishes']:
        objs.append(models.DishDBModel(**dict(zip(dish_mapping, obj_data))))

    return objs


@pytest_asyncio.fixture(scope="function")
async def async_crud_with_data(generate_test_data, async_session):
    """Generator crud fixture with initialized data in DB."""
    for obj in generate_test_data:
        async_session.add(obj)
    await async_session.commit()
    yield CRUDDataBase(async_session)


class RollbackBaseTests:
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass


@pytest_asyncio.fixture
async def api(async_client):
    yield ApiTestService(async_client)


@pytest_asyncio.fixture(scope='class')
def buffer():
    buffer_data = {}
    yield buffer_data
