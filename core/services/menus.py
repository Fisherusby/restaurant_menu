from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas
from core.services.base import BaseObjectService


class MenusService(BaseObjectService):
    async def get_menu_list(self, db: AsyncSession) -> List[schemas.ResponseMenuSchema]:
        """Get a list of menus."""
        menu_list: List[models.MenuDBModel] = await self.repository.get_all(db=db)
        return [schemas.ResponseMenuSchema(**obj.to_dict()) for obj in menu_list]

    async def get_menu(self, db: AsyncSession, menu_id: UUID) -> schemas.ResponseMenuWithCountSchema:
        """Get menu data by ID."""
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        submenus_count, dishes_count = await self.repository.get_counts(db=db, menu_id=menu_id)
        return schemas.ResponseMenuWithCountSchema(
            **menu.to_dict(), submenus_count=submenus_count, dishes_count=dishes_count
        )

    async def create_menu(self, db: AsyncSession, data: schemas.MenuSchema) -> schemas.ResponseMenuSchema:
        """Create menu."""
        menu: models.MenuDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseMenuSchema(**menu.to_dict())

    async def update_menu(
        self, db: AsyncSession, menu_id: UUID, data: schemas.UpdateMenuSchema
    ) -> schemas.ResponseMenuSchema:
        """Update menu data."""
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        updated_menu = await self.repository.update(db=db, obj_in=data, db_obj=menu)
        return schemas.ResponseMenuSchema(**updated_menu.to_dict())

    async def delete_menu(self, db: AsyncSession, menu_id: UUID) -> None:
        """Delete menu."""
        await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        await self.repository.delete_by_id(db=db, obj_id=menu_id)

    async def get_menu_by_id_or_404(self, db: AsyncSession, menu_id: UUID) -> models.MenuDBModel:
        """Get menu data by ID or rise http 404 if non-exist."""
        menu: models.MenuDBModel = await self.repository.get_by_id(db=db, obj_id=menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail="menu not found")

        return menu


menus_service = MenusService(repositories.menus)
