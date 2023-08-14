from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core import models, schemas
from core.repositories.base import BaseRepository


class DishesRepository(BaseRepository[models.DishDBModel, schemas.DishWithSubmenuIdSchema, schemas.UpdateDishSchema]):
    async def get_dish(self, db: AsyncSession, dish_id: UUID, submenu_id: UUID) -> models.DishDBModel | None:
        query = (
            select(self.model)
            .filter(self.model.id == dish_id)
            .filter(self.model.submenu_id == submenu_id)
            .options(
                selectinload(models.DishDBModel.discount)
            )
        )
        return (await db.execute(query)).scalar_one_or_none()

    async def get_dish_list_by_submenu_id(self, db: AsyncSession, submenu_id: UUID) -> list[models.DishDBModel]:
        query = (
            select(self.model)
            .filter(self.model.submenu_id == submenu_id)
            .options(
                selectinload(models.DishDBModel.discount)
            )
        )

        return (await db.execute(query)).scalars().all()


class DiscountDishesRepository(BaseRepository[models.DiscountDBModel, None, None]):
    pass


dishes: DishesRepository = DishesRepository(models.DishDBModel)

discount: DiscountDishesRepository = DiscountDishesRepository(models.DiscountDBModel)
