import uuid

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import as_declarative
from sqlalchemy.sql import func


@as_declarative()
class BaseDBModel:
    # flake8: noqa: A003
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    __name__: str

    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # flake8: noqa: A003
    def to_dict(self):
        return self.__dict__
