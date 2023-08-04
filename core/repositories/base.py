from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.models.base import BaseDBModel

ModelType = TypeVar('ModelType', bound=BaseDBModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""

    def __init__(self, model: type[ModelType]):
        self.model: type[ModelType] = model

    async def get_all(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ModelType]:
        """Select all objects in database."""
        return (await db.execute(select(self.model).offset(skip).limit(limit))).scalars().all()

    async def get_by_id(self, db: AsyncSession, *, obj_id: UUID) -> ModelType | None:
        """Select an object in database by ID."""
        query = select(self.model).filter(self.model.id == obj_id)
        return (await db.execute(query)).scalar_one_or_none()

    def query_by_field(self, fields: dict) -> Any:
        """Query for select objects in database by fields value."""
        query = select(self.model)
        for field_name, value in fields.items():
            query = query.filter(getattr(self.model, field_name, None) == value)
        return query

    async def get_one_by_fields(
        self, db: AsyncSession, *, fields: dict
    ) -> ModelType | None:
        """Select an object in database by fields value."""

        return (await db.execute(self.query_by_field(fields))).scalar_one_or_none()

    async def get_mul_by_fields(
        self, db: AsyncSession, *, fields: dict, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Select objects in database by fields value."""

        return (await db.execute(self.query_by_field(fields).offset(skip).limit(limit))).scalars().all()

    async def get_all_by_fields(
        self, db: AsyncSession, *, fields: dict, only_one: bool = False, skip: int = 0, limit: int = 100
    ) -> ModelType | None | list[ModelType]:
        """Select objects in database by fields value.

        only_one set True if you want an objects or None as result.
        """

        query = select(self.model)
        for field_name, value in fields.items():
            query = query.filter(getattr(self.model, field_name, None) == value)

        if only_one:
            return (await db.execute(query)).scalar_one_or_none()
        else:
            return (await db.execute(query.offset(skip).limit(limit))).scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType | dict):
        """Create an object in database."""
        obj_dict: dict = dict(obj_in)

        db_obj = self.model(**obj_dict)
        db.add(db_obj)
        await db.flush()
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    async def delete_by_id(self, db: AsyncSession, *, obj_id: UUID):
        """Delete an object in database by ID."""
        query = delete(self.model).where(self.model.id == obj_id)

        await db.execute(query)
        await db.commit()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Update an object in database.

        :param db_obj: Modifiable object
        :param obj_in: Updated data
        :return:
        """
        obj_data = dict(db_obj.__dict__)
        obj_data.pop('_sa_instance_state')

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        db.add(db_obj)
        await db.flush()
        await db.commit()
        await db.refresh(db_obj)
        return db_obj


RepositoryType = TypeVar('RepositoryType', bound=BaseRepository)
