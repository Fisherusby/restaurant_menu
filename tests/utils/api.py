from httpx import AsyncClient, Response

from core.endpoints.api import router


def reverse(name: str, **kwargs) -> str:
    """Generate API url by endpoint name"""
    return router.url_path_for(name, **kwargs)


class ApiTestService:
    MENU: str = 'menu'
    SUBMENU: str = 'submenu'
    DISH: str = 'dish'

    LIST: str = 'list'
    READ: str = 'get'
    CREATE: str = 'create'
    UPDATE: str = 'update'
    DELETE: str = 'delete'

    URL_NAMES: dict[str, dict[str, str]] = {
        MENU: {
            LIST: 'get_menu_list',
            READ: 'get_menu',
            CREATE: 'create_menu',
            UPDATE: 'update_menu',
            DELETE: 'delete_menu',
        },
        SUBMENU: {
            LIST: 'get_submenu_list',
            READ: 'get_submenu',
            CREATE: 'create_submenu',
            UPDATE: 'update_submenu',
            DELETE: 'delete_submenu',
        },
        DISH: {
            LIST: 'get_dish_list',
            READ: 'get_dish',
            CREATE: 'create_dish',
            UPDATE: 'update_dish',
            DELETE: 'delete_dish',
        },
    }

    fields: dict[str, tuple] = {
        MENU: ('title', 'description'),
        SUBMENU: ('title', 'description', 'menu_id'),
        DISH: ('title', 'description', 'price', 'submenu_id'),
    }

    def __init__(self, async_client: AsyncClient):
        self.client: AsyncClient = async_client

    async def get_list(self, entity: str, status_code: int = 200, **ids) -> Response | list[dict[str, str]]:
        """Call API for test a list of entities."""
        url: str = reverse(self.URL_NAMES[entity][self.LIST], **ids)
        response: Response = await self.client.get(url=url)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json: list[dict[str, str]] = response.json()
            for resp_obj in resp_json:
                assert 'id' in resp_obj
                for field in self.fields[entity]:
                    assert field in resp_obj
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}

        return response

    async def create(
            self, entity: str, json: dict[str, str], status_code: int = 201, **ids
    ) -> Response | dict[str, str]:
        """Call API for create entity."""
        url: str = reverse(self.URL_NAMES[entity][self.CREATE], **ids)
        response: Response = await self.client.post(url=url, json=json)
        assert response.status_code == status_code
        if response.status_code == 201:
            resp_json: dict[str, str] = response.json()
            payload = dict(**json, **ids)
            for field in self.fields[entity]:
                assert resp_json[field] == payload[field]
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}

        return response

    async def read(self, entity: str, status_code: int = 200, **ids) -> Response | dict[str, str]:
        """Call API for get the entity."""
        url: str = reverse(self.URL_NAMES[entity][self.READ], **ids)
        response: Response = await self.client.get(url=url)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json: dict[str, str] = response.json()
            assert 'id' in resp_json
            for field in self.fields[entity]:
                assert field in resp_json
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}

        return response

    async def update(
            self, entity: str, json: dict[str, str], status_code: int = 200, **ids
    ) -> Response | dict[str, str]:
        """Call API for update the entity."""
        url: str = reverse(self.URL_NAMES[entity][self.UPDATE], **ids)
        response: Response = await self.client.patch(url=url, json=json)
        assert response.status_code == status_code
        if response.status_code == 200:
            resp_json: dict[str, str] = response.json()
            for field, value in resp_json.items():
                assert resp_json[field] == value
            assert 'id' in resp_json
            for field in self.fields[entity]:
                assert field in resp_json
            return resp_json
        elif response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}

        return response

    async def delete(self, entity: str, status_code: int = 200, **ids) -> Response:
        """Call API for delete the entity."""
        url: str = reverse(self.URL_NAMES[entity][self.DELETE], **ids)
        response: Response = await self.client.delete(url=url)
        assert response.status_code == status_code
        if response.status_code == 404:
            assert response.json() == {'detail': f'{entity} not found'}

        return response
