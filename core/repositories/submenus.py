from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models
from core.repositories.base import BaseRepository


class SubmenuRepository(BaseRepository):
    async def get_submenu_with_dish_count(
        self, db: AsyncSession, submenu_id: UUID, menu_id: UUID
    ) -> Optional[Tuple[models.SubmenuDBModel, int]]:
        """Get submenu with counts of dishes in submenu from database."""
        query = (
            select(self.model, func.count(distinct(models.DishDBModel.id)))
            .filter(self.model.id == submenu_id, self.model.menu_id == menu_id)
            .join(models.DishDBModel, isouter=True)
            .group_by(self.model)
        )
        result = (await db.execute(query)).first()
        return result


submenus = SubmenuRepository(models.SubmenuDBModel)
