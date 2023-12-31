from core import models

MENU: str = 'menu'
MENU_MAPPING: tuple[str, str, str] = ('id', 'title', 'description')
MENUS_DATA: list[tuple[str, str, str]] = [
    ('9ea7362e-bab3-4bfc-bab7-71cf9e06f58b', 'Menu A', 'Description menu A'),
    ('70eb2363-c1de-4daa-b7cd-6b98db17e841', 'Menu B', 'Description menu B'),
    ('aafe18cc-7986-4f72-9e37-adafa0f1f5b3', 'Menu C', 'Description menu C'),
]

SUBMENUS: str = 'submenu'
SUBMENUS_MAPPING: tuple[str, str, str, str] = ('id', 'menu_id', 'title', 'description')
SUBMENUS_DATA: list[tuple[str, str, str, str]] = [
    ('f98d48cb-4383-411c-bc71-ac653ce42e09', MENUS_DATA[0][0], 'Submenu AA', 'Description submenu AA'),
    ('c0861bf3-311d-4db7-8677-d7ee5052adc9', MENUS_DATA[0][0], 'Submenu AB', 'Description submenu AB'),
    ('e2564502-0848-42d7-84c1-28bfc84e5ee9', MENUS_DATA[1][0], 'Submenu BA', 'Description submenu BA'),
]

DISH: str = 'dish'
DISH_MAPPING: tuple[str, str, str, str, str] = ('id', 'submenu_id', 'title', 'description', 'price')
DISHES_DATA: list[tuple[str, str, str, str, str]] = [
    ('2ee022d7-7557-44df-a88e-a0bfb102eb53', SUBMENUS_DATA[0][0], 'Dish AA1', 'Description dish AA1', '11.11'),
    ('352590fa-434e-4436-b195-ada202625887', SUBMENUS_DATA[0][0], 'Dish AA2', 'Description dish AA2', '22.22'),
    ('2bb5b495-6473-463f-9d9a-cb6372e89a3e', SUBMENUS_DATA[0][0], 'Dish AA3', 'Description dish AA3', '33.33'),
    ('ffaa2434-b33d-490f-847d-a29318f4c106', SUBMENUS_DATA[1][0], 'Dish AB1', 'Description dish AB1', '44.44'),
    ('dd0a3fc5-154f-487a-a4bf-b5a90fcaf67f', SUBMENUS_DATA[1][0], 'Dish AB2', 'Description dish AB2', '55.55'),
]

MAPPING: str = 'mapping'
DATA: str = 'data'
MODEL: str = 'model'

INIT_DATA_ALL: dict[str, dict] = {
    MENU: {
        MAPPING: MENU_MAPPING,
        DATA: MENUS_DATA,
        MODEL: models.MenuDBModel,
    },
    SUBMENUS: {
        MAPPING: SUBMENUS_MAPPING,
        DATA: SUBMENUS_DATA,
        MODEL: models.SubmenuDBModel,
    },
    DISH: {
        MAPPING: DISH_MAPPING,
        DATA: DISHES_DATA,
        MODEL: models.DishDBModel,
    },
}
