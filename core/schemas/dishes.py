from typing import Optional, Union

from core.schemas.base import APISchema, BaseIdSchema


class DishSchema(APISchema):
    """Schema model for dish's data.

    Used for request to create dish.
    """

    title: str
    description: str
    price: Union[str, float]


class UpdateDishSchema(APISchema):
    """Schema model for dish's data.

    Used for update dish.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Union[str, float]] = None


class DishWithSubmenuIdSchema(DishSchema):
    """Schema model for dish's data with submenu ID.

    Used for create dish.
    """

    submenu_id: int


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    """Schema model for dish's data with dish ID.

    Used for response dish`s data.
    """
