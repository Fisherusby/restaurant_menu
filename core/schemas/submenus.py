from typing import Optional

from core.schemas.base import APISchema, BaseIdSchema


class SubmenuSchema(APISchema):
    title: str
    description: str


class SubmenuWithMenuIdSchema(SubmenuSchema):
    menu_id: int


class UpdateSubmenuSchema(APISchema):
    title: Optional[str] = None
    description: Optional[str] = None


class ResponseSubmenuSchema(SubmenuWithMenuIdSchema, BaseIdSchema):
    pass


class ResponseSubmenuWithCountSchema(ResponseSubmenuSchema):
    dishes_count: int
