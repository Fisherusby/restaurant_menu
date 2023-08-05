import pytest
from httpx import AsyncClient, Response
from sqlalchemy import select

from core import models
from tests.base import BaseTestCase
from tests.utils import CRUDDataBase, uuid_or_none


class TestMenus(BaseTestCase):
    fields_for_assert = ('id', 'title', 'description')
    model = models.MenuDBModel

    @staticmethod
    async def get_ids_submenus_dishes_by_menu_id(crud: CRUDDataBase, menu_id: str):
        query_submenus = select(models.SubmenuDBModel.id).filter(models.SubmenuDBModel.menu_id == uuid_or_none(menu_id))
        submenus_ids = (await crud.db.execute(query_submenus)).scalars().all()

        query_dishes = select(models.DishDBModel.id).filter(models.DishDBModel.submenu_id.in_(submenus_ids))
        dishes_ids = (await crud.db.execute(query_dishes)).scalars().all()

        return submenus_ids, dishes_ids

    @pytest.mark.asyncio
    async def test_get_list_menus_empty_menu(self, async_client: AsyncClient, async_crud: CRUDDataBase):
        """Testing get an empty list of menus."""
        url: str = self.reverse('get_menu_list')
        response: Response = await async_client.get(url=url)
        assert response.status_code == 200
        menu_count: int = await async_crud.get_count(model=models.MenuDBModel)
        assert menu_count == 0
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_list_menus(self, async_client: AsyncClient, async_crud_with_data: CRUDDataBase):
        """Testing get a list of menus."""
        url: str = self.reverse('get_menu_list')
        response: Response = await async_client.get(url=url)
        assert response.status_code == 200
        resp_json: dict = response.json()

        menu_count = await async_crud_with_data.get_count(model=models.MenuDBModel)

        assert len(resp_json) == menu_count > 0
        for resp_obj in resp_json:
            db_obj: models.MenuDBModel = await async_crud_with_data.get_by_id(models.MenuDBModel, resp_obj['id'])
            assert resp_obj['title'] == db_obj.title
            assert resp_obj['description'] == db_obj.description

    @pytest.mark.parametrize(
        'created_data,expected_status_code',
        (
            pytest.param({'title': 'Menu 1', 'description': 'Description menu 1'}, 201, id='Menu 1'),
            pytest.param({'title': '', 'description': 'Description menu 1'}, 201, id='Empty title'),
            pytest.param({'title': 'Menu 1', 'description': ''}, 201, id='Empty description'),
            pytest.param({'title': '', 'description': ''}, 201, id='Empty title and description'),
            pytest.param({'description': 'Description menu 1'}, 422, id='Without title'),
            pytest.param({'title': 'Menu 1'}, 422, id='Without description'),
            pytest.param(None, 422, id='Empty payload'),
        ),
    )
    @pytest.mark.asyncio
    async def test_create_menu(
        self,
        created_data: dict[str, str],
        expected_status_code: int,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing create menu."""
        url: str = self.reverse('create_menu')
        response: Response = await async_client.post(url=url, json=created_data)
        assert response.status_code == expected_status_code

        if response.status_code != 201:
            return

        resp_json: dict = response.json()
        assert 'id' in resp_json

        self.assert_payload_in_response(response, **created_data)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

    @pytest.mark.parametrize(
        'menu_id,expected_response,expected_status_code',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': 'Menu A',
                    'description': 'Description menu A',
                    'submenus_count': 2,
                    'dishes_count': 5,
                },
                200,
                id='Menu A',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                {
                    'id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                    'title': 'Menu B',
                    'description': 'Description menu B',
                    'submenus_count': 1,
                    'dishes_count': 0,
                },
                200,
                id='Menu B',
            ),
            pytest.param(
                'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                {
                    'id': 'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                    'title': 'Menu C',
                    'description': 'Description menu C',
                    'submenus_count': 0,
                    'dishes_count': 0,
                },
                200,
                id='Menu C',
            ),
            pytest.param('ffffffff', None, 422, id='Bad menu id'),
            pytest.param(None, None, 422, id='Empty menu id'),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff', {'detail': 'menu not found'}, 404, id='Non-exist menu id'
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_menu_detail(
        self,
        menu_id: str,
        expected_response: dict[str, str],
        expected_status_code: int,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing get menu's detail."""
        url: str = self.reverse('get_menu', menu_id=menu_id)
        response: Response = await async_client.get(url=url)
        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert response.json() == expected_response

        if response.status_code != 200:
            return

        await self.assert_equal_response_db_object(response, async_crud_with_data)
        rest_json: dict[str, str] = response.json()
        submenus_ids, dishes_ids = await self.get_ids_submenus_dishes_by_menu_id(async_crud_with_data, menu_id)

        assert len(submenus_ids) == rest_json['submenus_count']
        assert len(dishes_ids) == rest_json['dishes_count']

    @pytest.mark.parametrize(
        'menu_id,updated_data,expected_response,expected_status_code',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {
                    'title': 'Menu A updated',
                    'description': 'Description menu A updated',
                },
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': 'Menu A updated',
                    'description': 'Description menu A updated',
                },
                200,
                id='Title and description',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {
                    'title': 'Menu A updated',
                },
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': 'Menu A updated',
                    'description': 'Description menu A',
                },
                200,
                id='Only title',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {
                    'description': 'Description menu A updated',
                },
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': 'Menu A',
                    'description': 'Description menu A updated',
                },
                200,
                id='Only description',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {},
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': 'Menu A',
                    'description': 'Description menu A',
                },
                200,
                id='Empty payload',
            ),
            pytest.param('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', None, None, 422, id='Without payload'),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {
                    'title': '',
                    'description': '',
                },
                {
                    'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'title': '',
                    'description': '',
                },
                200,
                id='Empty title and description',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {
                    'title': 'Menu A updated',
                    'description': 'Description menu A updated',
                },
                {'detail': 'menu not found'},
                404,
                id='Non-exist menu id',
            ),
            pytest.param(
                None,
                {
                    'title': 'Menu A updated',
                    'description': 'Description menu A updated',
                },
                None,
                422,
                id='Empty menu id',
            ),
            pytest.param(
                'ffffffff',
                {
                    'title': 'Menu A updated',
                    'description': 'Description menu A updated',
                },
                None,
                422,
                id='Bad menu id',
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_update_menu(
        self,
        menu_id: str,
        updated_data: dict[str, str],
        expected_response: dict[str, str] | None,
        expected_status_code: int,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing update menu's parameters."""
        url: str = self.reverse('update_menu', menu_id=menu_id)
        response: Response = await async_client.patch(url=url, json=updated_data)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert response.json() == expected_response

        if response.status_code != 200:
            return

        self.assert_payload_in_response(response, **updated_data)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

    @pytest.mark.parametrize(
        'menu_id,expected_status_code,expected_response',
        (
            pytest.param('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', 200, None, id='Menu A'),
            pytest.param('70eb2363-c1de-4daa-b7cd-6b98db17e841', 200, None, id='Menu B'),
            pytest.param('aafe18cc-7986-4f72-9e37-adafa0f1f5b3', 200, None, id='Menu C'),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff', 404, {'detail': 'menu not found'}, id='Non exist menu id'
            ),
            pytest.param('ffffffff', 422, None, id='Bad menu id'),
        ),
    )
    @pytest.mark.asyncio
    async def test_delete_menu(
        self,
        menu_id: str,
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing delete menu."""

        submenus_ids, dishes_ids = await self.get_ids_submenus_dishes_by_menu_id(async_crud_with_data, menu_id)
        before_obj_count: int = await async_crud_with_data.get_count(models.MenuDBModel)
        url: str = self.reverse('delete_menu', menu_id=menu_id)
        response: Response = await async_client.delete(url=url)
        after_obj_count: int = await async_crud_with_data.get_count(models.MenuDBModel)
        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert response.json() == expected_response

        if response.status_code != 200:
            assert before_obj_count == after_obj_count
            return

        assert before_obj_count - 1 == after_obj_count

        db_obj: models.MenuDBModel = await async_crud_with_data.get_by_id(models.MenuDBModel, menu_id)
        assert db_obj is None

        after_submenus_count = await async_crud_with_data.get_count_exist_ids(models.SubmenuDBModel, submenus_ids)
        assert after_submenus_count == 0

        after_dishes_count = await async_crud_with_data.get_count_exist_ids(models.DishDBModel, dishes_ids)
        assert after_dishes_count == 0
