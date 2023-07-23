from typing import Optional
from uuid import UUID

from core.schemas.base import APISchema, BaseIdSchema


class SubmenuSchema(APISchema):
    """Schema model for submenu's data.

    Used for request to create submenu.
    """

    title: str
    description: str


class SubmenuWithMenuIdSchema(SubmenuSchema):
    """Schema model for submenu's data with menu ID.

    Used for create submenu.
    """

    menu_id: UUID


class UpdateSubmenuSchema(APISchema):
    """Schema model for submenu's data.

    Used for update submenu's data.
    """

    title: Optional[str] = None
    description: Optional[str] = None


class ResponseSubmenuSchema(SubmenuWithMenuIdSchema, BaseIdSchema):
    """Schema model for submenu's data with submenu ID.

    Used for response submenu's data.
    """

    pass


class ResponseSubmenuWithCountSchema(ResponseSubmenuSchema):
    """Schema model for submenu's data with a counts of dishes.

    Used for response submenu's detail data.
    """

    dishes_count: int
