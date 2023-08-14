from typing import Any

import pytest
from httpx import AsyncClient, Response

from core import models
from core.repositories.base import ModelType
from tests.utils import CRUDDataBase, reverse


class TestAllInOne:
    MENU: str = 'menu'
    SUBMENU: str = 'submenu'
    DISH: str = 'dish'

    fields: dict[str, tuple] = {
        MENU: ('title', 'description'),
        SUBMENU: ('title', 'description', 'menu_id'),
        DISH: ('title', 'description', 'price', 'submenu_id'),
    }

    def assert_resp_db_obj(self, obj_db: ModelType, obj_resp: dict[str, str], entity: str) -> None:
        assert str(obj_resp['id']) == str(obj_db.id)
        for field in self.fields[entity]:
            assert str(obj_resp[field]) == str(getattr(obj_db, field))

    @pytest.mark.asyncio
    async def test_get_empty(self, async_client: AsyncClient, async_crud: CRUDDataBase):
        """Testing get an empty response from all_in_one endpoint."""
        url: str = reverse('get_all_in_one')
        response: Response = await async_client.get(url=url)
        assert response.status_code == 200
        menu_count: int = await async_crud.get_count(model=models.MenuDBModel)
        assert menu_count == 0
        assert response.json() == []

    @pytest.mark.parametrize(
        'expected_response',
        (
            pytest.param(
                [
                    {
                        'id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                        'title': 'Menu B',
                        'description': 'Description menu B',
                        'submenus': [
                            {
                                'id': 'e2564502-0848-42d7-84c1-28bfc84e5ee9',
                                'title': 'Submenu BA',
                                'description': 'Description submenu BA',
                                'menu_id': '70eb2363-c1de-4daa-b7cd-6b98db17e841',
                                'dishes': []
                            }
                        ]
                    },
                    {
                        'id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                        'title': 'Menu A',
                        'description': 'Description menu A',
                        'submenus': [
                            {
                                'id': 'c0861bf3-311d-4db7-8677-d7ee5052adc9',
                                'title': 'Submenu AB',
                                'description': 'Description submenu AB',
                                'menu_id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                                'dishes': [
                                    {
                                        'id': 'dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f',
                                        'title': 'Dish AB2',
                                        'description': 'Description dish AB2',
                                        'price': '55.55',
                                        'submenu_id': 'c0861bf3-311d-4db7-8677-d7ee5052adc9'
                                    },
                                    {
                                        'id': 'ffaa2434-b33d-490f-847d-a29318f4c106',
                                        'title': 'Dish AB1',
                                        'description': 'Description dish AB1',
                                        'price': '44.44',
                                        'submenu_id': 'c0861bf3-311d-4db7-8677-d7ee5052adc9'}
                                ]
                            },
                            {
                                'id': 'f98d48cb-4383-411c-bc71-ac653ce42e09',
                                'title': 'Submenu AA',
                                'description': 'Description submenu AA',
                                'menu_id': '9ea7362e-bab3-4bfc-bab7-71cf9e06f58b',
                                'dishes': [
                                    {
                                        'id': '2bb5b495-6473-463f-9d9a-cb6372e89a3e',
                                        'title': 'Dish AA3',
                                        'description': 'Description dish AA3',
                                        'price': '33.33',
                                        'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09'
                                    },
                                    {
                                        'id': '2ee022d7-7557-44df-a88e-a0bfb102eb53',
                                        'title': 'Dish AA1',
                                        'description': 'Description dish AA1',
                                        'price': '11.11',
                                        'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09'
                                    },
                                    {
                                        'id': '352590fa-434e-4436-b195-ada202625887',
                                        'title': 'Dish AA2',
                                        'description': 'Description dish AA2',
                                        'price': '22.22',
                                        'submenu_id': 'f98d48cb-4383-411c-bc71-ac653ce42e09'
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        'id': 'aafe18cc-7986-4f72-9e37-adafa0f1f5b3',
                        'title': 'Menu C',
                        'description':
                        'Description menu C',
                        'submenus': []
                    }
                ],
                id='DB with init data'
            ),
        ),
    )
    @pytest.mark.asyncio
    async def test_get_with_data(
            self, expected_response: list[dict[str, Any]], async_client: AsyncClient, async_crud_with_data: CRUDDataBase
    ):
        """Testing get response from all_in_one endpoint."""
        url: str = reverse('get_all_in_one')
        response: Response = await async_client.get(url=url)
        assert response.status_code == 200
        assert response.json() == expected_response
        resp_json: list[dict[str, Any]] = response.json()

        db_menus: dict[str, models.MenuDBModel] = {
            str(obj.id): obj for obj in await async_crud_with_data.get_all(models.MenuDBModel)
        }
        db_submenus: dict[str, models.SubmenuDBModel] = {
            str(obj.id): obj for obj in await async_crud_with_data.get_all(models.SubmenuDBModel)
        }
        db_dishes: dict[str, models.DishDBModel] = {
            str(obj.id): obj for obj in await async_crud_with_data.get_all(models.DishDBModel)
        }

        for resp_menu in resp_json:
            db_menu: models.MenuDBModel = db_menus.pop(resp_menu['id'])
            self.assert_resp_db_obj(obj_db=db_menu, obj_resp=resp_menu, entity=self.MENU)
            for resp_submenu in resp_menu['submenus']:
                assert resp_submenu['menu_id'] == resp_menu['id']
                db_submenu: models.SubmenuDBModel = db_submenus.pop(resp_submenu['id'])
                self.assert_resp_db_obj(obj_db=db_submenu, obj_resp=resp_submenu, entity=self.SUBMENU)
                for resp_dish in resp_submenu['dishes']:
                    assert resp_dish['submenu_id'] == resp_submenu['id']
                    db_dish: models.DishDBModel = db_dishes.pop(resp_dish['id'])
                    self.assert_resp_db_obj(obj_db=db_dish, obj_resp=resp_dish, entity=self.DISH)

        assert not db_menus
        assert not db_submenus
        assert not db_dishes
