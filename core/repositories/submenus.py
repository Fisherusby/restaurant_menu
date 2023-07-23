from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models
from core.repositories.base import BaseRepository


class SubmenuRepository(BaseRepository):
    async def get_counts(self, db: AsyncSession, submenu_id: int) -> Optional[int]:
        """Get counts of dishes in submenu from database."""
        query = (
            select(func.count(models.DishDBModel.id))
            .filter(models.DishDBModel.submenu_id == submenu_id)
            .group_by(models.DishDBModel.submenu_id)
        )
        result = (await db.execute(query)).first()
        return result[0] if result is not None else 0


submenus = SubmenuRepository(models.SubmenuDBModel)
