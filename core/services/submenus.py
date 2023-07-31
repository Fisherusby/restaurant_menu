from typing import List, Optional, Tuple
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas, services
from core.services.base import BaseObjectService


class SubmenusService(BaseObjectService):
    async def get_submenu(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> schemas.ResponseSubmenuWithCountSchema:
        """Get submenu data by IDs of menu and submenu."""
        submenu: Optional[Tuple[models.SubmenuDBModel, int]] = await self.repository.get_submenu_with_dish_count(
            db=db, submenu_id=submenu_id, menu_id=menu_id
        )

        if submenu is None:
            raise HTTPException(status_code=404, detail="submenu not found")
        return schemas.ResponseSubmenuWithCountSchema(
            **submenu[0].to_dict(), dishes_count=submenu[1] if submenu[1] is not None else 0
        )

    async def get_submenu_list(self, db: AsyncSession, menu_id: UUID) -> List[schemas.ResponseSubmenuSchema]:
        """Get a list of submenus in menu."""
        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        submenu_list: List[models.SubmenuDBModel] = await self.repository.get_by_fields(
            db=db, fields={'menu_id': menu_id}
        )
        return [schemas.ResponseSubmenuSchema(**obj.to_dict()) for obj in submenu_list]

    async def get_submenu_by_id_or_404(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> models.SubmenuDBModel:
        """Get submenu data by IDs of menu and submenu or rise http 404 if non-exist."""
        submenu: Optional[models.SubmenuDBModel] = await self.repository.get_by_fields(
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
        self, db: AsyncSession, menu_id: UUID, data: schemas.SubmenuSchema
    ) -> schemas.ResponseSubmenuSchema:
        """Create submenu in menu."""
        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        data = schemas.SubmenuWithMenuIdSchema(**data.model_dump(), menu_id=menu_id)
        submenu: models.SubmenuDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseSubmenuSchema(**submenu.to_dict())

    async def update_submenu(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, data: schemas.UpdateSubmenuSchema
    ) -> schemas.ResponseSubmenuSchema:
        """Update submenu data."""
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )
        updated_submenu: models.SubmenuDBModel = await self.repository.update(db=db, db_obj=sub_menu, obj_in=data)
        return schemas.ResponseSubmenuSchema(**updated_submenu.to_dict())

    async def delete_submenu(self, db: AsyncSession, menu_id: UUID, submenu_id: UUID):
        """Delete submenu by IDs of menu adn submenu."""
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )

        await self.repository.delete_by_id(db=db, obj_id=sub_menu.id)


submenus_service = SubmenusService(repositories.submenus)
