from uuid import UUID

from pydantic import BaseConfig, BaseModel


class APISchema(BaseModel):
    class Config(BaseConfig):
        from_attributes = True
        population_by_name = True


class BaseIdSchema(APISchema):
    # flake8: noqa: A003
    id: UUID


class NotFoundSchema(BaseModel):
    detail: str
