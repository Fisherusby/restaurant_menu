import pytest


class TestApiFlow:
    @pytest.mark.order(1)
    @pytest.mark.asyncio
    async def test_create_menu(self, api, async_session_without_clear, buffer):
        buffer['menu_1'] = await api.create(
            api.MENU,
            {'title': 'menu 1', 'description': 'description menu 1'},
        )

    @pytest.mark.order(2)
    @pytest.mark.asyncio
    async def test_create_submenu(self, api, async_session_without_clear, buffer):
        buffer['submenu_1'] = await api.create(
            api.SUBMENU,
            {'title': 'submenu 1', 'description': 'description menu 1'},
            menu_id=buffer['menu_1']['id'],
        )

    @pytest.mark.order(3)
    @pytest.mark.asyncio
    async def test_create_dish_1(self, api, async_session_without_clear, buffer):
        buffer['dish_1'] = await api.create(
            api.DISH,
            {'title': 'menu 1', 'description': 'description menu 1', 'price': '11.11'},
            menu_id=buffer['submenu_1']['menu_id'],
            submenu_id=buffer['submenu_1']['id'],
        )

    @pytest.mark.order(4)
    @pytest.mark.asyncio
    async def test_create_dish_2(self, api, async_session_without_clear, buffer):
        buffer['dish_2'] = await api.create(
            api.DISH,
            {'title': 'menu 1', 'description': 'description menu 1', 'price': '22.22'},
            menu_id=buffer['submenu_1']['menu_id'],
            submenu_id=buffer['submenu_1']['id'],
        )

    @pytest.mark.order(5)
    @pytest.mark.asyncio
    async def test_detail_menu_1(self, api, async_session_without_clear, buffer):
        detail_menu = await api.read(api.MENU, menu_id=buffer['menu_1']['id'])
        assert detail_menu['id'] == buffer['menu_1']['id']
        assert detail_menu['submenus_count'] == 1
        assert detail_menu['dishes_count'] == 2

    @pytest.mark.order(6)
    @pytest.mark.asyncio
    async def test_detail_submenu_1(self, api, async_session_without_clear, buffer):
        detail_submenu = await api.read(
            api.SUBMENU, menu_id=buffer['menu_1']['id'], submenu_id=buffer['submenu_1']['id']
        )
        assert detail_submenu['id'] == buffer['submenu_1']['id']
        assert detail_submenu['dishes_count'] == 2

    @pytest.mark.order(7)
    @pytest.mark.asyncio
    async def test_delete_submenu_1(self, api, async_session_without_clear, buffer):
        await api.delete(api.SUBMENU, menu_id=buffer['menu_1']['id'], submenu_id=buffer['submenu_1']['id'])

    @pytest.mark.order(8)
    @pytest.mark.asyncio
    async def test_list_submenus_menu_1(self, api, async_session_without_clear, buffer):
        submenu_list = await api.list(api.SUBMENU, menu_id=buffer['menu_1']['id'])
        assert submenu_list == []

    @pytest.mark.order(9)
    @pytest.mark.asyncio
    async def test_list_dishes_submenu_1(self, api, async_session_without_clear, buffer):
        dish_list = await api.list(api.DISH, menu_id=buffer['menu_1']['id'], submenu_id=buffer['submenu_1']['id'])
        assert dish_list == []

    @pytest.mark.order(10)
    @pytest.mark.asyncio
    async def test_detail_menu_1_after_delete(self, api, async_session_without_clear, buffer):
        detail_menu = await api.read(api.MENU, menu_id=buffer['menu_1']['id'])
        assert detail_menu['id'] == buffer['menu_1']['id']
        assert detail_menu['submenus_count'] == 0
        assert detail_menu['dishes_count'] == 0

    @pytest.mark.order(11)
    @pytest.mark.asyncio
    async def test_delete_menu_1(self, api, async_session_without_clear, buffer):
        await api.delete(api.MENU, menu_id=buffer['menu_1']['id'])

    @pytest.mark.order(12)
    @pytest.mark.asyncio
    async def test_list_menus(self, api, async_session_without_clear, buffer):
        menu_list = await api.list(api.MENU)
        assert menu_list == []

    @pytest.mark.order(99)
    @pytest.mark.asyncio
    async def test_clear_db(self, api, async_session, buffer):
        buffer.clear()
