from typing import Any, List, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models.base import BaseDBModel

ModelType = TypeVar("ModelType", bound=BaseDBModel)


class CRUDDataBase:
    def __init__(self, db: AsyncSession):
        self.db: AsyncSession = db

    async def get_count(self, model: ModelType):
        """Get number of records in table by SQLAlchemy model."""
        query_all = select(func.count(model.id))
        result = (await self.db.execute(query_all)).scalar_one_or_none()
        return result

    async def get_count_exist_ids(self, model: ModelType, ids: List[Any]):
        """Get number of exist ids records in table by SQLAlchemy model."""
        query_all = select(func.count(model.id)).filter(model.id.in_(ids))
        result = (await self.db.execute(query_all)).scalars().first()
        return result

    async def get_all(self, model: ModelType):
        """Get number of records in table by SQLAlchemy model."""
        query_all = select(model)
        result = (await self.db.execute(query_all)).scalars().all()
        return result

    async def get_by_id(self, model: ModelType, obj_id: Any):
        """Get record in table by SQLAlchemy model and id."""
        query_all = select(model).filter(model.id == obj_id)
        result = (await self.db.execute(query_all)).scalar_one_or_none()
        return result

    async def get_by_field(self, model: ModelType, field: Any, value, only_one: bool = True):
        """Get record/records in table by SQLAlchemy model and field value."""
        query = select(model).filter(getattr(model, field, None) == value)
        if only_one:
            result = (await self.db.execute(query)).scalar_one_or_none()
        else:
            result = (await self.db.execute(query.order_by(model.created_at.desc()))).scalars().all()
        return result

    async def get_by_mul_field(self, model: ModelType, fields: dict, only_one: bool = True):
        """Get record/records in table by SQLAlchemy model and fields."""
        query = select(model)
        for field, value in fields.items():
            query = query.filter(getattr(model, field, None) == value)
        if only_one:
            result = (await self.db.execute(query)).scalar_one_or_none()
        else:
            result = (await self.db.execute(query.order_by(model.created_at.desc()))).scalars().all()
        return result

    async def get_last(self, model: ModelType):
        """Get last record in table by SQLAlchemy model."""
        query_all = select(model).order_by(model.created_at.desc())
        result = (await self.db.execute(query_all)).scalars().first()
        return result
