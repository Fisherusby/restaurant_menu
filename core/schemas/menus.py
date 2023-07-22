from typing import Optional

from core.schemas.base import APISchema, BaseIdSchema


class MenuSchema(APISchema):
    title: str
    description: str


class UpdateMenuSchema(APISchema):
    title: Optional[str] = None
    description: Optional[str] = None


class ResponseMenuSchema(MenuSchema, BaseIdSchema):
    pass


class ResponseMenuWithCountSchema(ResponseMenuSchema):
    submenus_count: int
    dishes_count: int
