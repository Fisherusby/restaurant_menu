from decimal import Decimal
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

    title: str | None = None
    description: str | None = None
    price: Decimal | None = None

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


class ParsingFileDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    pass


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    """Schema model for dish's data with dish ID.

    Used for response dish`s data.
    """
    pass
