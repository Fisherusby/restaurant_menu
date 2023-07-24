from decimal import Decimal
from typing import Optional
from uuid import UUID

from core.schemas.base import APISchema, BaseIdSchema


class DishSchema(APISchema):
    """Schema model for dish's data.

    Used for request to create dish.
    """

    title: str
    description: str
    price: Decimal


class UpdateDishSchema(APISchema):
    """Schema model for dish's data.

    Used for update dish.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None


class DishWithSubmenuIdSchema(DishSchema):
    """Schema model for dish's data with submenu ID.

    Used for create dish.
    """

    submenu_id: UUID


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    """Schema model for dish's data with dish ID.

    Used for response dish`s data.
    """
