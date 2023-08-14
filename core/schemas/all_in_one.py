from pydantic import BaseModel

from core.schemas import ResponseDishSchema, ResponseMenuSchema, ResponseSubmenuSchema


class ResponseSubmenuWithDishesSchema(ResponseSubmenuSchema):
    """ Model a Submenu with Dishes fo the Submenu for all_in_one response"""
    dishes: list[ResponseDishSchema]


class ResponseMenuWitSubmenusSchema(ResponseMenuSchema):
    """ Model a Menu with Submenus fo the Menu for all_in_one response"""
    submenus: list[ResponseSubmenuWithDishesSchema]


class CeleryTaskRunnerRequest(BaseModel):
    source: str
