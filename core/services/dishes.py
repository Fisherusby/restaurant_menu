from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas, services
from core.services.base import BaseObjectService


class DishesService(BaseObjectService):
    """Service for dishes data."""

    async def get_dish_list(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> list[schemas.ResponseDishSchema]:
        """Get a list of dishes in submenu by IDs of menu and submenu."""
        # Postman tests expect empty list in non-existent submenu...
        # await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        dish_list: list[models.DishDBModel] = await self.repository.get_mul_by_fields(
            db=db, fields={'submenu_id': submenu_id}
        )
        return [schemas.ResponseDishSchema(**obj.to_dict()) for obj in dish_list]

    async def get_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID
    ) -> schemas.ResponseDishSchema:
        """Get dish data by IDs of dish, menu and submenu."""
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        return schemas.ResponseDishSchema(**dish.to_dict())

    async def get_dish_by_id_or_404(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID
    ) -> models.DishDBModel:
        """Get dish data or rise http 404 by IDs of dish, menu and submenu."""
        dish: models.DishDBModel | None = await self.repository.get_one_by_fields(
            db=db, fields={'id': dish_id, 'submenu_id': submenu_id}
        )

        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')

        return dish

    async def create_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, data: schemas.DishSchema
    ) -> schemas.ResponseDishSchema:
        """Create dish in menu's submenu."""
        await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        data = schemas.DishWithSubmenuIdSchema(**data.model_dump(), submenu_id=submenu_id)
        dish: models.DishDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseDishSchema(**dish.to_dict())

    async def update_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID, data: schemas.UpdateDishSchema
    ) -> schemas.ResponseDishSchema:
        """Update dish data."""
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        updated_dish: models.DishDBModel = await self.repository.update(db=db, db_obj=dish, obj_in=data)
        return schemas.ResponseDishSchema(**updated_dish.to_dict())

    async def delete_dish(self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
        """Delete dish."""
        await self.get_dish_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

        await self.repository.delete_by_id(db=db, obj_id=dish_id)


dishes_service = DishesService(repositories.dishes)
