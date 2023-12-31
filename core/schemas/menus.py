from core.schemas.base import APISchema, BaseIdSchema


class MenuSchema(APISchema):
    """Schema model for menu's data.

    Used for request to create menu.
    """

    title: str
    description: str


class UpdateMenuSchema(APISchema):
    """Schema model for menu's data.

    Used for update menu.
    """

    title: str | None = None
    description: str | None = None


class ResponseMenuSchema(MenuSchema, BaseIdSchema):
    """Schema model for menu's data with menu ID.

    Used for response menu's data.
    """

    pass


class ParsingFileMenuSchema(MenuSchema, BaseIdSchema):
    pass


class ResponseMenuWithCountSchema(ResponseMenuSchema):
    """Schema model for menu's data with counts of submenu and dishes.

    Used for response menu's detail data.
    """

    submenus_count: int
    dishes_count: int
