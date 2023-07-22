from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas, services
from core.services.base import BaseObjectService


class SubmenusService(BaseObjectService):
    async def get_submenu(
        self, db: AsyncSession, menu_id: int, submenu_id: int
    ) -> schemas.ResponseSubmenuWithCountSchema:
        submenu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, submenu_id=submenu_id, menu_id=menu_id
        )
        dishes_count = await self.repository.get_counts(db=db, submenu_id=submenu_id)
        return schemas.ResponseSubmenuWithCountSchema(**submenu.to_dict(), dishes_count=dishes_count)

    async def get_submenu_list(self, db: AsyncSession, menu_id: int) -> List[schemas.ResponseSubmenuSchema]:
        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        submenu_list: List[models.SubmenuDBModel] = await self.repository.get_by_fields(
            db=db, fields={'menu_id': menu_id}
        )
        return [schemas.ResponseSubmenuSchema(**obj.to_dict()) for obj in submenu_list]

    async def get_submenu_by_id_or_404(self, db: AsyncSession, menu_id: int, submenu_id: int) -> models.SubmenuDBModel:
        submenu: models.SubmenuDBModel = await self.repository.get_by_fields(
            db=db,
            fields={
                'id': submenu_id,
                'menu_id': menu_id,
            },
            only_one=True,
        )

        if submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")

        return submenu

    async def create_submenu(
        self, db: AsyncSession, menu_id: int, data: schemas.SubmenuSchema
    ) -> schemas.ResponseSubmenuSchema:
        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        data = schemas.SubmenuWithMenuIdSchema(**data.model_dump(), menu_id=menu_id)
        submenu: models.SubmenuDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseSubmenuSchema(**submenu.to_dict())

    async def update_submenu(
        self, db: AsyncSession, menu_id: int, submenu_id: int, data: schemas.UpdateSubmenuSchema
    ) -> schemas.ResponseSubmenuSchema:
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )
        updated_submenu: models.SubmenuDBModel = await self.repository.update(db=db, db_obj=sub_menu, obj_in=data)
        return schemas.ResponseSubmenuSchema(**updated_submenu.to_dict())

    async def delete_submenu(self, db: AsyncSession, menu_id: int, submenu_id: int):
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )

        await self.repository.delete_by_id(db=db, obj_id=sub_menu.id)


submenus_service = SubmenusService(repositories.submenus)
