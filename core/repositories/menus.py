from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models
from core.repositories.base import BaseRepository


class MenuRepository(BaseRepository):
    async def get_counts(self, db: AsyncSession, menu_id: int) -> Optional[Tuple[int, int]]:
        """Get counts of dishes and submenus in menu from database."""
        subquery_submenus = (
            select(models.SubmenuDBModel.menu_id, func.count(models.SubmenuDBModel.id).label('submenus_count'))
            .filter(models.SubmenuDBModel.menu_id == menu_id)
            .group_by(models.SubmenuDBModel.menu_id)
            .subquery()
        )

        subquery_dishes = (
            select(models.SubmenuDBModel.menu_id, func.count(models.DishDBModel.id).label('dishes_count'))
            .filter(models.SubmenuDBModel.menu_id == menu_id)
            .join(models.SubmenuDBModel.dishes)
            .group_by(models.SubmenuDBModel.menu_id)
            .subquery()
        )

        query = select(subquery_submenus.c.submenus_count, subquery_dishes.c.dishes_count).where(
            subquery_submenus.c.menu_id == subquery_dishes.c.menu_id
        )
        result = (await db.execute(query)).first()
        return result if result is not None else (0, 0)


menus = MenuRepository(models.MenuDBModel)
