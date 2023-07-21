from pydantic import BaseModel, BaseConfig


class APISchema(BaseModel):
    class Config(BaseConfig):
        from_attributes = True
        population_by_name = True


class BaseIdSchema(APISchema):
    id: str
