from uuid import UUID

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import select

from core import models
from tests.base import BaseTestCase
from tests.utils import CRUDDataBase, reverse, uuid_or_none


class TestSubmenus(BaseTestCase):
    fields_for_assert = ('id', 'menu_id', 'title', 'description')
    model = models.SubmenuDBModel

    @staticmethod
    async def get_ids_dishes_by_submenu_id(crud: CRUDDataBase, submenu_id: str):
        query_dishes = select(models.DishDBModel.id).filter(models.DishDBModel.submenu_id == uuid_or_none(submenu_id))
        dishes_ids = (await crud.db.execute(query_dishes)).scalars().all()
        return dishes_ids

    @pytest.mark.parametrize(
        'menu_id,expected_status_code,expected_response',
        (
            pytest.param('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', 200, None, id='Menu A'),
            pytest.param('70eb2363-c1de-4daa-b7cd-6b98db17e841', 200, None, id='Menu B'),
            pytest.param('aafe18cc-7986-4f72-9e37-adafa0f1f5b3', 200, None, id='Menu C'),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff', 404, {'detail': 'menu not found'}, id='Non-exist menu'
            ),
            pytest.param('ffffffff', 422, None, id='Bad menu id'),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_list_submenus(
        self,
        menu_id: str,
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing get a list of submenus."""
        url: str = reverse('get_submenu_list', args=[menu_id])
        response: Response = await async_client.get(url=url)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert response.json() == expected_response

        menu_uuid: UUID | None = uuid_or_none(menu_id)

        menu_obj: models.MenuDBModel = await async_crud_with_data.get_by_id(models.MenuDBModel, menu_uuid)
        submenus_objects: list[models.SubmenuDBModel] = await async_crud_with_data.get_by_field(
            models.SubmenuDBModel, field='menu_id', value=menu_uuid, only_one=False
        )

        if response.status_code != 200:
            assert menu_obj is None
            assert len(submenus_objects) == 0
            return

        resp_json: list[dict[str, str]] = response.json()
        db_objs_dict: dict[str, models.SubmenuDBModel] = {str(obj.id): obj for obj in submenus_objects}

        assert menu_obj is not None
        assert len(resp_json) == len(submenus_objects)

        for resp_obj in resp_json:
            self.assert_resp_and_db_obj(resp_obj, db_objs_dict[resp_obj['id']])

    @pytest.mark.parametrize(
        'menu_id,created_data,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {'title': 'Submenu created', 'description': 'Description submenu created'},
                201,
                None,
                id='All field',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {'title': 'Submenu created', 'description': ''},
                201,
                None,
                id='Empty description',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {'title': '', 'description': 'Description submenu created'},
                201,
                None,
                id='Empty title',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {'description': 'Description submenu created'},
                422,
                None,
                id='Without title field',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                {'title': 'Submenu created'},
                422,
                None,
                id='Without description field',
            ),
            pytest.param('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', {}, 422, None, id='Without all field'),
            pytest.param('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', None, 422, None, id='Without payload data'),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {'title': 'Submenu created', 'description': 'Description submenu created'},
                404,
                {'detail': 'menu not found'},
                id='Non-exist menu_id',
            ),
            pytest.param(
                'ffffffff',
                {'title': 'Submenu created', 'description': 'Description submenu created'},
                422,
                None,
                id='Bad menu_id',
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_create_submenu(
        self,
        menu_id: str,
        created_data: dict[str, str],
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing create submenu."""
        before_obj_count: int = await async_crud_with_data.get_count(models.SubmenuDBModel)
        url: str = reverse('create_submenu', args=[menu_id])
        response: Response = await async_client.post(url=url, json=created_data)
        after_obj_count: int = await async_crud_with_data.get_count(models.SubmenuDBModel)
        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 201:
            assert before_obj_count == after_obj_count
            return

        assert before_obj_count + 1 == after_obj_count

        resp_json: dict[str, str] = response.json()
        assert 'id' in resp_json

        self.assert_payload_in_response(response, **created_data, menu_id=menu_id)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

    @pytest.mark.parametrize(
        'menu_id,submenu_id,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                200,
                {
                    'id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Submenu AA',
                    'description': 'Description submenu AA',
                    'menu_id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'dishes_count': 3,
                },
                id='Submenu AA',
            ),
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                200,
                {
                    'id': 'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                    'title': 'Submenu AB',
                    'description': 'Description submenu AB',
                    'menu_id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                    'dishes_count': 2,
                },
                id='Submenu AB',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                200,
                {
                    'id': 'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                    'title': 'Submenu BA',
                    'description': 'Description submenu BA',
                    'menu_id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                    'dishes_count': 0,
                },
                id='Submenu BA',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                404,
                {'detail': 'submenu not found'},
                id='Submenu not in menu',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                404,
                {'detail': 'submenu not found'},
                id='Non-exist menu id',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {'detail': 'submenu not found'},
                id='Non-exist submenu id',
            ),
            pytest.param('ffffffff-ffff', 'e2564502-0848-42d7-84c1-28bfc84e5ee9', 422, None, id='Bad menu id'),
            pytest.param('70eb2363-c1de-4daa-b7cd-6b98db17e841', 'ffffffff-ffff', 422, None, id='Bad submenu id'),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_submenu_detail(
        self,
        menu_id: str,
        submenu_id: str,
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing get a submenu details."""
        url: str = reverse('get_submenu', args=[menu_id, submenu_id])
        response: Response = await async_client.get(url=url)
        assert response.status_code == expected_status_code

        db_obj: models.SubmenuDBModel = await async_crud_with_data.get_by_mul_field(
            models.SubmenuDBModel,
            fields={
                'id': uuid_or_none(submenu_id),
                'menu_id': uuid_or_none(menu_id),
            },
        )

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 200:
            assert db_obj is None
            return

        await self.assert_equal_response_db_object(response, async_crud_with_data, db_obj)

        dishes_ids = await self.get_ids_dishes_by_submenu_id(async_crud_with_data, submenu_id)

        assert len(dishes_ids) == response.json()['dishes_count']

    @pytest.mark.parametrize(
        'menu_id,submenu_id,updated_data,expected_status_code,expected_response',
        (
            pytest.param(
                '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {
                    'title': 'Submenu AA updated',
                    'description': 'Description submenu AA updated',
                },
                200,
                {
                    'id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                    'title': 'Submenu AA updated',
                    'description': 'Description submenu AA updated',
                    'menu_id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                },
                id='Title and description',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                {
                    'description': 'Description submenu BA updated',
                },
                200,
                {
                    'id': 'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                    'title': 'Submenu BA',
                    'description': 'Description submenu BA updated',
                    'menu_id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                },
                id='Only description',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                {
                    'title': 'Submenu BA updated',
                },
                200,
                {
                    'id': 'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                    'title': 'Submenu BA updated',
                    'description': 'Description submenu BA',
                    'menu_id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                },
                id='Only title',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                {},
                200,
                {
                    'id': 'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                    'title': 'Submenu BA',
                    'description': 'Description submenu BA',
                    'menu_id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                },
                id='Empty pyload data',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'f98d48cb-4383-411c-bc71-ac653ce42e09',
                {
                    'title': 'Submenu CC updated',
                    'description': 'Description submenu CC updated',
                },
                404,
                {'detail': 'submenu not found'},
                id='Submenu not in menu',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                {
                    'title': 'Submenu CC updated',
                    'description': 'Description submenu CC updated',
                },
                404,
                {'detail': 'submenu not found'},
                id='Non-exist menu id',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                {
                    'title': 'Submenu CC updated',
                    'description': 'Description submenu CC updated',
                },
                404,
                {'detail': 'submenu not found'},
                id='Non-exist submenu id',
            ),
            pytest.param(
                'ffffffff-ffff',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                {
                    'title': 'Submenu CC updated',
                    'description': 'Description submenu CC updated',
                },
                422,
                None,
                id='Bad menu id',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'ffffffff-ffff',
                {
                    'title': 'Submenu CC updated',
                    'description': 'Description submenu CC updated',
                },
                422,
                None,
                id='Bad submenu id',
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_update_submenu(
        self,
        menu_id: str,
        submenu_id: str,
        updated_data: dict[str, str],
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing update submenu's parameters."""
        url: str = reverse('update_submenu', args=[menu_id, submenu_id])
        response: Response = await async_client.patch(url=url, json=updated_data)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 200:
            return

        self.assert_payload_in_response(response, **updated_data, menu_id=menu_id)
        await self.assert_equal_response_db_object(response, async_crud_with_data)

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
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                200,
                None,
                id='Submenu BA',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                404,
                {'detail': 'submenu not found'},
                id='Submenu not in menu',
            ),
            pytest.param(
                '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                404,
                {'detail': 'submenu not found'},
                id='Non-exist submenu id',
            ),
            pytest.param(
                'ffffffff-ffff-ffff-ffff-ffffffffffff',
                'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                404,
                {'detail': 'submenu not found'},
                id='Non-exist menu id',
            ),
            pytest.param('ffffffff-ffff', 'e2564502-0848-42d7-84c1-28bfc84e5ee9', 422, None, id='Bab menu id'),
            pytest.param('70eb2363-c1de-4daa-b7cd-6b98db17e841', 'ffffffff-ffff', 422, None, id='Bad submenu id'),
        ),
    )
    @pytest.mark.asyncio
    async def test_delete_submenu(
        self,
        menu_id: str,
        submenu_id: str,
        expected_status_code: int,
        expected_response: dict[str, str] | None,
        async_client: AsyncClient,
        async_crud_with_data: CRUDDataBase,
    ):
        """Testing delete submenu."""
        dishes_ids = await self.get_ids_dishes_by_submenu_id(async_crud_with_data, submenu_id)
        before_obj_count: int = await async_crud_with_data.get_count(models.SubmenuDBModel)
        url: str = reverse('delete_submenu', args=[menu_id, submenu_id])
        response: Response = await async_client.delete(url=url)
        after_obj_count: int = await async_crud_with_data.get_count(models.SubmenuDBModel)

        assert response.status_code == expected_status_code

        if expected_response is not None:
            assert expected_response == response.json()

        if response.status_code != 200:
            assert before_obj_count == after_obj_count
            return

        assert before_obj_count - 1 == after_obj_count

        db_obj: models.SubmenuDBModel | None = await async_crud_with_data.get_by_id(
            models.SubmenuDBModel, submenu_id
        )
        assert db_obj is None

        after_dishes_count = await async_crud_with_data.get_count_exist_ids(models.DishDBModel, dishes_ids)

        assert after_dishes_count == 0
