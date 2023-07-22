from core.services.base import BaseObjectService
from core import repositories, schemas, models
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Tuple

from fastapi import HTTPException


class MenusService(BaseObjectService):
    async def get_menu_list(self, db: AsyncSession) -> List[schemas.ResponseMenuSchema]:
        menu_list: List[models.MenuDBModel] = await self.repository.get_all(db=db)
        return [schemas.ResponseMenuSchema(**obj.dict()) for obj in menu_list]

    async def get_menu(self, db: AsyncSession, menu_id: int) -> schemas.ResponseMenuWithCountSchema:
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        submenus_count, dishes_count = await self.repository.get_counts(db=db, menu_id=menu_id)
        return schemas.ResponseMenuWithCountSchema(
            **menu.dict(), submenus_count=submenus_count, dishes_count=dishes_count
        )

    async def create_menu(self, db: AsyncSession, data: schemas.MenuSchema) -> schemas.ResponseMenuSchema:
        menu: models.MenuDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseMenuSchema(**menu.dict())

    async def update_menu(self, db: AsyncSession, menu_id: int, data: schemas.UpdateMenuSchema) -> schemas.ResponseMenuSchema:
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        updated_menu = await self.repository.update(db=db, obj_in=data, db_obj=menu)
        return schemas.ResponseMenuSchema(**updated_menu.dict())

    async def delete_menu(self, db: AsyncSession, menu_id: int) -> None:
        await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        await self.repository.delete_by_id(db=db, id=menu_id)

    async def get_menu_by_id_or_404(self, db: AsyncSession, menu_id: int) -> models.MenuDBModel:
        menu: models.MenuDBModel = await self.repository.get_by_id(db=db, id=menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail=f"menu not found")

        return menu


menus_service = MenusService(repositories.menus)
