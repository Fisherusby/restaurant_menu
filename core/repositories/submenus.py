from core.repositories.base import BaseRepository
from core import models

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select, func

from typing import Optional


class SubmenuRepository(BaseRepository):
    async def get_counts(self, db: AsyncSession, submenu_id: int) -> Optional[int]:
        query = select(func.count(models.DishDBModel.id)) \
            .filter(models.DishDBModel.submenu_id == submenu_id) \
            .group_by(models.DishDBModel.submenu_id)
        result = (await db.execute(query)).first()
        return result[0] if result is not None else 0


submenus = SubmenuRepository(models.SubmenuDBModel)
