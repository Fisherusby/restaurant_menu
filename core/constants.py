# CRUD operation
CREATE: str = 'create'
UPDATE: str = 'update'
DELETE: str = 'delete'

# Entities
MENU: str = 'menu'
SUBMENU: str = 'submenu'
DISH: str = 'dish'

ENTITIES = (MENU, SUBMENU, DISH)

# mapping
mapping_menu = ('id', 'title', 'description')
mapping_submenu = ('id', 'title', 'description')
mapping_dish = ('id', 'title', 'description', 'price')

# mapping to create
mapping_entity_to_create = {
    MENU: mapping_menu,
    SUBMENU: (*mapping_submenu, 'menu_id'),
    DISH: (*mapping_dish, 'submenu_id'),
}

# entity relationship
entity_child = {
    MENU: SUBMENU,
    SUBMENU: DISH,
    DISH: None
}

entity_parents = {
    DISH: SUBMENU,
    SUBMENU: MENU,
    MENU: None
}

# ordering operations for sync xls
order_operation = (DELETE, UPDATE, CREATE)
order_entity = (MENU, SUBMENU, DISH)
