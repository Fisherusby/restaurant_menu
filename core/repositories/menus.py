from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models
from core.repositories.base import BaseRepository


class MenuRepository(BaseRepository):
    async def get_menu_with_counts(
        self, db: AsyncSession, menu_id: UUID
    ) -> Optional[Tuple[models.MenuDBModel, int, int]]:
        """Get menu with counts of dishes and submenus in menu from database."""

        query = (
            select(
                self.model, func.count(distinct(models.SubmenuDBModel.id)), func.count(distinct(models.DishDBModel.id))
            )
            .select_from(self.model, models.SubmenuDBModel)
            .filter(self.model.id == menu_id)
            .join(models.SubmenuDBModel, isouter=True)
            .join(models.DishDBModel, models.SubmenuDBModel.id == models.DishDBModel.submenu_id, isouter=True)
            .group_by(self.model)
        )
        result = (await db.execute(query)).first()
        return result


menus = MenuRepository(models.MenuDBModel)
