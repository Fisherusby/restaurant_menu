from typing import Optional, Union
from uuid import UUID

from pydantic import field_validator

from core.schemas.base import APISchema, BaseIdSchema


def validate_price(v):
    if float(v) <= 0:
        raise ValueError("Price must be greater than zero")
    return v


class DishSchema(APISchema):
    """Schema model for dish's data.

    Used for request to create dish.
    """

    title: str
    description: str
    price: Union[str, float]

    @field_validator('price')
    def price_validator(cls, v):
        return validate_price(v)


class UpdateDishSchema(APISchema):
    """Schema model for dish's data.

    Used for update dish.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Union[str, float]] = None

    @field_validator('price')
    def price_validator(cls, v):
        if v is None:
            return v
        return validate_price(v)


class DishWithSubmenuIdSchema(DishSchema):
    """Schema model for dish's data with submenu ID.

    Used for create dish.
    """

    submenu_id: UUID


class ResponseDishSchema(DishWithSubmenuIdSchema, BaseIdSchema):
    """Schema model for dish's data with dish ID.

    Used for response dish`s data.
    """
