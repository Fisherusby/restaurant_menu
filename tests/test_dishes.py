from typing import Dict, List, Optional

import pytest
from httpx import AsyncClient, Response

from core import models
from tests.base import BaseTestCase
from tests.utils.crud import CRUDDataBase
from tests.utils.uuid_tool import uuid_or_none


class TestDishes(BaseTestCase):
    fields_for_assert = ('id', 'submenu_id', 'title', 'description', 'price')
    model = models.DishDBModel

    @pytest.mark.parametrize(
        'menu_id,submenu_id,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                200,
                None,
                id='Submenu AA',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                200,
                None,
                id='Submenu AB',
            ),
            pytest.param(
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                200,
                None,
                id='Submenu BA',
            ),
            pytest.param(
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                200,
                None,
                id='Submenu not in menu',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                200,
                None,
                id='Non-exist menu',
            ),
            pytest.param(
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                200,
                None,
                id='Non-exist submenu',
            ),
            pytest.param('ffffffff', 'f98d48cb-4383-411c-bc71-ac653ce42e09', 422, None, id='Bad menu'),
            pytest.param('e2564502-0848-42d7-84c1-28bfc84e5ee9', 'ffffffff', 422, None, id='Bad submenu'),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_list_dishes(
        self,
        menu_id: str,
        submenu_id: str,
        expected_status_code: int,
        expected_response: Optional[Dict[str, str]],
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing get a list of submenu's dishes."""
        response: Response = await async_client.get(url=f'/menus/{menu_id}/submenus/{submenu_id}/dishes')

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 200:
            return

        db_objs: List[models.DishDBModel] = await async_crud_with_data.get_by_mul_field(
            models.DishDBModel, {'submenu_id': uuid_or_none(submenu_id)}, only_one=False
        )

        resp_json: Dict[str, str] = response.json()
        assert len(resp_json) == len(db_objs)

        db_objs: Dict[str, models.DishDBModel] = {str(obj.id): obj for obj in db_objs}

        for resp_obj in resp_json:
            assert resp_obj['id'] == str(db_objs[resp_obj['id']].id)
            assert resp_obj['submenu_id'] == str(db_objs[resp_obj['id']].submenu_id)
            assert resp_obj['title'] == db_objs[resp_obj['id']].title
            assert resp_obj['description'] == db_objs[resp_obj['id']].description
            assert resp_obj['price'] == str(db_objs[resp_obj['id']].price)

    @pytest.mark.parametrize(
        'menu_id,submenu_id,created_data,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                201,
                None,
                id="All payload data",
            ),
            # wrong payload data
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'description': 'Dish description create', 'price': '55.33'},
                422,
                None,
                id="Without title",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'title': 'Dish create', 'price': '55.33'},
                422,
                None,
                id="Without description",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {
                    'title': 'Dish create',
                    'description': 'Dish description create',
                },
                422,
                None,
                id="Without price",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '-10'},
                422,
                None,
                id="Price lese than zero",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {},
                422,
                None,
                id="Empty payload",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                None,
                422,
                None,
                id="Without payload",
            ),
            # exist IDs but mixed up
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                404,
                {"detail": "submenu not found"},
                id="Submenu not in menu",
            ),
            # non-exist IDs
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                404,
                {"detail": "submenu not found"},
                id="Non-exist menu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                404,
                {"detail": "submenu not found"},
                id="Non-exist submenu id",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                404,
                {"detail": "submenu not found"},
                id="Non-exist ids menu and submenu",
            ),
            # wrong IDs
            pytest.param(
                'ffffffff',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                422,
                None,
                id="Bad menu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                422,
                None,
                id="Bad submenu id",
            ),
            pytest.param(
                'ffffffff',
                'ffffffff',
                {'title': 'Dish create', 'description': 'Dish description create', 'price': '55.33'},
                422,
                None,
                id="Bad ids menu and submenu",
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_create_dish(
        self,
        menu_id: str,
        submenu_id: str,
        created_data: Dict[str, str],
        expected_status_code: int,
        expected_response: Optional[Dict[str, str]],
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing create dish."""
        before_count: int = await async_crud_with_data.get_count(models.DishDBModel)
        response: Response = await async_client.post(
            url=f'/menus/{menu_id}/submenus/{submenu_id}/dishes', json=created_data
        )
        after_count: int = await async_crud_with_data.get_count(models.DishDBModel)
        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 201:
            assert before_count == after_count
            return

        assert before_count + 1 == after_count
        self.assert_payload_in_response(response, **created_data, submenu_id=submenu_id)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

    @pytest.mark.parametrize(
        'menu_id,submenu_id,dish_id,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                200,
                {
                    "id": "2ee022d7-7557-44df-a88e-a0bfb102eb53",
                    "title": "Dish AA1",
                    "description": "Description dish AA1",
                    "price": "11.11",
                    "submenu_id": "f98d48cb-4383-411c-bc71-ac653ce42e09",
                },
                id="Dish AA1",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '352590fa-434e-4436-b195-ada202625887',
                200,
                {
                    "id": "352590fa-434e-4436-b195-ada202625887",
                    "title": "Dish AA2",
                    "description": "Description dish AA2",
                    "price": "22.22",
                    "submenu_id": "f98d48cb-4383-411c-bc71-ac653ce42e09",
                },
                id="Dish AA2",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2bb5b495-6473-463f-9d9a-cb6372e89a3e',
                200,
                {
                    "id": "2bb5b495-6473-463f-9d9a-cb6372e89a3e",
                    "title": "Dish AA3",
                    "description": "Description dish AA3",
                    "price": "33.33",
                    "submenu_id": "f98d48cb-4383-411c-bc71-ac653ce42e09",
                },
                id="Dish AA3",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffaa2434-b33d-490f-847d-a29318f4c106',
                200,
                {
                    "id": "ffaa2434-b33d-490f-847d-a29318f4c106",
                    "title": "Dish AB1",
                    "description": "Description dish AB1",
                    "price": "44.44",
                    "submenu_id": "c0861bf3-311d-4db7-8677-d7ee5052adc9",
                },
                id="Dish AB1",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                {
                    "id": "dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f",
                    "title": "Dish AB2",
                    "description": "Description dish AB2",
                    "price": "55.55",
                    "submenu_id": "c0861bf3-311d-4db7-8677-d7ee5052adc9",
                },
                id="Dish AB2",
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                None,
                id="Dish's submenu not in menu",
            ),  # fix
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id="Dish not in menu's submenu",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                '2bb5b495-6473-463f-9d9a-cb6372e89a3e',
                404,
                {"detail": "dish not found"},
                id="Dish not in menu's submenu",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                None,
                id='Non-exist menu id',
            ),  # fix
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id='Non-exist submenu id',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id='Non-exist dish id',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id='Non-exist ids menu and submenu',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id='Non-exist ids submenu and dish',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id='Non-exist ids menu and dish',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id='Non-exist ids menu, submenu and dish',
            ),
            pytest.param(
                'ffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                422,
                None,
                id='Bad menu id',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                422,
                None,
                id='Bad submenu id',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff',
                422,
                None,
                id='Bad dish id',
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_dish_detail(
        self,
        menu_id: str,
        submenu_id: str,
        dish_id: str,
        expected_status_code: int,
        expected_response: Optional[Dict[str, str]],
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing get dish's detail."""
        response: Response = await async_client.get(url=f'/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')

        assert response.status_code == expected_status_code

        db_obj: Optional[models.DishDBModel] = await async_crud_with_data.get_by_mul_field(
            models.DishDBModel,
            fields={
                'id': uuid_or_none(dish_id),
                'submenu_id': uuid_or_none(submenu_id),
            },
        )

        if expected_response is not None:
            assert response.json() == expected_response

        if response.status_code != 200:
            # assert db_obj is None
            return

        await self.assert_equal_response_db_object(response, async_crud_with_data, db_obj)

    @pytest.mark.parametrize(
        'menu_id,submenu_id,dish_id,updated_data,expected_status_code,expected_response',
        (
            # exist dish-submenu-menu
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Dish description updated',
                    'price': '99.99',
                },
                id="All fields",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'description': 'Dish description updated', 'price': '99.99'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish AA1',
                    'description': 'Dish description updated',
                    'price': '99.99',
                },
                id="Without title",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'price': '99.99'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Description dish AA1',
                    'price': '99.99',
                },
                id="Without description",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Dish description updated',
                    'price': '11.11',
                },
                id="Without price",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish AA1',
                    'description': 'Description dish AA1',
                    'price': '11.11',
                },
                id="Empty payload",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                None,
                422,
                None,
                id="Without pyload",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.999'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Dish description updated',
                    'price': '100.00',
                },
                id="Price's scale more than two digits (round)",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99'},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Dish description updated',
                    'price': '99.00',
                },
                id="Price without scale",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': 99.999},
                200,
                {
                    'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                    'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Dish update',
                    'description': 'Dish description updated',
                    'price': '100.00',
                },
                id="Price as float",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '-10'},
                422,
                None,
                id="Price lese than zero",
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                404,
                {'detail': 'dish not found'},
                id="Dish not in submenu and submenu not in menu",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                404,
                {'detail': 'dish not found'},
                id="Dish not in menu's submenu",
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                200,
                None,
                id="Dish's submenu not in menu",
            ),  # fix
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                200,
                None,
                id="Non-exist menu id",
            ),  # fix
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                404,
                {'detail': 'dish not found'},
                id="Non-exist submenu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                404,
                {'detail': 'dish not found'},
                id="Non-exist dish id",
            ),
            pytest.param(
                'ffffffff',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                422,
                None,
                id="Bad menu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                422,
                None,
                id="Bad submenu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'ffffffff',
                {'title': 'Dish update', 'description': 'Dish description updated', 'price': '99.99'},
                422,
                None,
                id="Bad dish id",
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_update_dish(
        self,
        menu_id: str,
        submenu_id: str,
        dish_id: str,
        updated_data: Dict[str, str],
        expected_status_code: int,
        expected_response: Optional[Dict[str, str]],
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing update dish's parameters."""
        response: Response = await async_client.patch(
            url=f'/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', json=updated_data
        )

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 200:
            return

        self.assert_payload_in_response(response, **updated_data, submenu_id=submenu_id)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

    @pytest.mark.parametrize(
        'menu_id,submenu_id,dish_id,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                200,
                None,
                id='Dish AA1',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '352590fa-434e-4436-b195-ada202625887',
                200,
                None,
                id='Dish AA2',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                '2bb5b495-6473-463f-9d9a-cb6372e89a3e',
                200,
                None,
                id='Dish AA3',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffaa2434-b33d-490f-847d-a29318f4c106',
                200,
                None,
                id='Dish AB1',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                None,
                id='Dish AB2',
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                None,
                id="Dish's submenu non in menu",
            ),  # fix
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id="Dish non in menu's submenu",
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                '2bb5b495-6473-463f-9d9a-cb6372e89a3e',
                404,
                {"detail": "dish not found"},
                id="Dish not in submenu and submenu not in menu",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                200,
                None,
                id="Non-exist menu id",
            ),  # fix
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id="Non-exist submenu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id="Non-exist dish id",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                404,
                {"detail": "dish not found"},
                id="Non-exist menu id and submenu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id="Non-exist submenu id and dish id",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id="Non-exist menu id and dish id",
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {"detail": "dish not found"},
                id="Non-exist ids menu, submenu and dish",
            ),
            pytest.param(
                'ffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                422,
                None,
                id="Bad menu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'ffffffff',
                'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                422,
                None,
                id="Bad submenu id",
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                'ffffffff',
                422,
                None,
                id="Bad dish id",
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_delete_dish(
        self,
        menu_id: str,
        submenu_id: str,
        dish_id: str,
        expected_status_code: int,
        expected_response: Optional[Dict[str, str]],
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing delete dish."""
        before_count: int = await async_crud_with_data.get_count(models.DishDBModel)
        response: Response = await async_client.delete(url=f'/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
        after_count: int = await async_crud_with_data.get_count(models.DishDBModel)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert response.json() == expected_response

        if response.status_code != 200:
            assert before_count == after_count
            return

        assert before_count - 1 == after_count

        db_obj: models.DishDBModel = await async_crud_with_data.get_by_id(models.DishDBModel, dish_id)

        assert db_obj is None
