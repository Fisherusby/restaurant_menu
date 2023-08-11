from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, schemas
from core.repositories.base import BaseRepository


class MenuRepository(BaseRepository[models.MenuDBModel, schemas.MenuSchema, schemas.UpdateMenuSchema]):
    async def get_menu_with_counts(
        self, db: AsyncSession, menu_id: UUID
    ) -> tuple[models.MenuDBModel, int, int] | None:
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
        return (await db.execute(query)).first()

    async def get_all_in_one(
            self, db: AsyncSession
    ) -> list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]]:
        query = (
            select(models.MenuDBModel, models.SubmenuDBModel, models.DishDBModel)
            .join(models.SubmenuDBModel, models.MenuDBModel.id == models.SubmenuDBModel.menu_id, isouter=True)
            .join(models.DishDBModel, models.SubmenuDBModel.id == models.DishDBModel.submenu_id, isouter=True)
        )

        return (await db.execute(query)).all()


menus: MenuRepository = MenuRepository(models.MenuDBModel)
