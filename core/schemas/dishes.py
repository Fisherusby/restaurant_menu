from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import field_validator

from core.schemas.base import APISchema, BaseIdSchema


def validating_price(v):
    if Decimal(v) < 0:
        raise ValueError('Price cannot be lese that zero')
    return v


class DishSchema(APISchema):
    """Schema model for dish's data.

    Used for request to create dish.
    """

    title: str
    description: str
    price: Decimal

    @field_validator('price')
    def price_validate(cls, v):
        return validating_price(v)


class UpdateDishSchema(APISchema):
    """Schema model for dish's data.

    Used for update dish.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None

    @field_validator('price')
    def price_validate(cls, v):
        if v is None:
            return v
        return validating_price(v)


class DishWithSubmenuIdSchema(DishSchema):
    """Schema model for dish's data with submenu ID.

    Used for create dish.
    """

    submenu_id: UUID


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    """Schema model for dish's data with dish ID.

    Used for response dish`s data.
    """
