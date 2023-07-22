from core.schemas.base import BaseIdSchema, APISchema
from typing import Optional, Union


class DishSchema(APISchema):
    title: str
    description: str
    price: Union[str, float]


class UpdateDishSchema(APISchema):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Union[str, float]] = None


class DishWithSubmenuIdSchema(DishSchema):
    submenu_id: int


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    price: Union[str, float]


