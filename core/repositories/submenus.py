from uuid import UUID

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, schemas
from core.repositories.base import BaseRepository


class SubmenuRepository(
    BaseRepository[models.SubmenuDBModel, schemas.SubmenuWithMenuIdSchema, schemas.UpdateSubmenuSchema]
):
    async def get_submenu_with_dish_count(
        self, db: AsyncSession, submenu_id: UUID, menu_id: UUID
    ) -> tuple[models.SubmenuDBModel, int] | None:
        """Get submenu with counts of dishes in submenu from database."""
        query = (
            select(models.SubmenuDBModel, func.count(distinct(models.DishDBModel.id)))
            .filter(models.SubmenuDBModel.id == submenu_id, models.SubmenuDBModel.menu_id == menu_id)
            .join(models.DishDBModel, isouter=True)
            .group_by(models.SubmenuDBModel)
        )
        return (await db.execute(query)).first()


submenus: SubmenuRepository = SubmenuRepository(models.SubmenuDBModel)
