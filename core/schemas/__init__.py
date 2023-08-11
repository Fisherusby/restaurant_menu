from core.schemas.dishes import (
    DishSchema,
    DishWithSubmenuIdSchema,
    ResponseDishSchema,
    UpdateDishSchema,
)
from core.schemas.menus import (
    MenuSchema,
    ResponseMenuSchema,
    ResponseMenuWithCountSchema,
    UpdateMenuSchema,
)
from core.schemas.submenus import (
    ResponseSubmenuSchema,
    ResponseSubmenuWithCountSchema,
    SubmenuSchema,
    SubmenuWithMenuIdSchema,
    UpdateSubmenuSchema,
)

from core.schemas.all_in_one import (
    ResponseMenuWitSubmenusSchema,
    ResponseSubmenuWithDishesSchema,
)

from core.schemas.base import NotFoundSchema
