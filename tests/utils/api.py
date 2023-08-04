from httpx import AsyncClient


class ApiTestService:
    MENU = 'menu'
    SUBMENU = 'submenu'
    DISH = 'dish'

    urls = {
        MENU: ('/menus', '/menus/{menu_id}'),
        SUBMENU: ('/menus/{menu_id}/submenus', '/menus/{menu_id}/submenus/{submenu_id}'),
        DISH: (
            '/menus/{menu_id}/submenus/{submenu_id}/dishes',
            '/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
        ),
    }

    fields = {
        MENU: ['title', 'description'],
        SUBMENU: ['title', 'description', 'menu_id'],
        DISH: ['title', 'description', 'price', 'submenu_id'],
    }

    def __init__(self, async_client: AsyncClient):
        self.client: AsyncClient = async_client

    async def get_list(self, entity: str, status_code: int = 200, **ids):
        """Call API for test a list of entities."""
        url = self.urls[entity][0].format(**ids)
        response = await self.client.get(url=url)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json = response.json()
            for resp_obj in resp_json:
                assert 'id' in resp_obj
                for field in self.fields[entity]:
                    assert field in resp_obj
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}
        else:
            return response

    async def create(self, entity, json, status_code=201, **ids):
        """Call API for create entity."""
        url = self.urls[entity][0].format(**ids)
        response = await self.client.post(url=url, json=json)
        assert response.status_code == status_code
        if response.status_code == 201:
            resp_json = response.json()
            payload = dict(**json, **ids)
            for field in self.fields[entity]:
                assert resp_json[field] == payload[field]
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}
        else:
            return response

    async def read(self, entity, status_code=200, **ids):
        """Call API for get the entity."""
        url = self.urls[entity][1].format(**ids)
        response = await self.client.get(url=url)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json = response.json()
            assert 'id' in resp_json
            for field in self.fields[entity]:
                assert field in resp_json
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}
        else:
            return response

    async def update(self, entity, json, status_code=200, **ids):
        """Call API for update the entity."""
        url = self.urls[entity][1].format(**ids)
        response = await self.client.patch(url=url, json=json)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json = response.json()
            for field, value in resp_json.items():
                assert resp_json[field] == value
            assert 'id' in resp_json
            for field in self.fields[entity]:
                assert field in resp_json
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}
        else:
            return response

    async def delete(self, entity, status_code=200, **ids):
        """Call API for delete the entity."""
        url = self.urls[entity][1].format(**ids)
        response = await self.client.delete(url=url)
        assert response.status_code == status_code
        if response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}
        return response
