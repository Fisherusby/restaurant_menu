from sqlalchemy.ext.asyncio import AsyncSession
from core.services.base import BaseObjectService
from core import schemas, services, models, repositories
from typing import List

from fastapi import HTTPException


class DishesService(BaseObjectService):
    async def get_dish_list(self, db: AsyncSession, menu_id: int, submenu_id: int) -> List[schemas.ResponseDishSchema]:

        # Postman tests expect empty list in non-existent submenu...
        # await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        dish_list: List[models.DishDBModel] = await self.repository.get_by_fields(
            db=db, fields={'submenu_id': submenu_id}
        )
        return [schemas.ResponseDishSchema(**obj.dict()) for obj in dish_list]

    async def get_dish(
            self, db: AsyncSession, menu_id: int, submenu_id: int, dish_id: int
    ) -> schemas.ResponseDishSchema:
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        return schemas.ResponseDishSchema(**dish.dict())

    async def get_dish_by_id_or_404(
            self, db: AsyncSession, menu_id: int, submenu_id: int, dish_id: int
    ) -> models.DishDBModel:
        dish: models.DishDBModel = await self.repository.get_by_fields(
            db=db,
            fields={
                'id': dish_id,
                'submenu_id': submenu_id
            },
            only_one=True
        )

        if dish is None:
            raise HTTPException(status_code=404, detail=f"dish not found")

        return dish

    async def create_dish(
            self, db: AsyncSession, menu_id: int, submenu_id: int, data: schemas.DishSchema
    ) -> schemas.ResponseDishSchema:
        await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        data = schemas.DishWithSubmenuIdSchema(**data.model_dump(), submenu_id=submenu_id)
        dish: models.DishDBModel = await self.repository.create(db=db, obj_in=data)
        return schemas.ResponseDishSchema(**dish.dict())

    async def update_dish(
            self, db: AsyncSession, menu_id: int, submenu_id: int, dish_id: int, data: schemas.UpdateDishSchema
    ) -> schemas.ResponseDishSchema:
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        updated_dish: models.DishDBModel = await self.repository.update(
            db=db, db_obj=dish, obj_in=data
        )
        return schemas.ResponseDishSchema(**updated_dish.dict())

    async def delete_dish(
            self, db: AsyncSession, menu_id: int, submenu_id: int, dish_id: int
    ) -> None:
        await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )

        await self.repository.delete_by_id(db=db, id=dish_id)


dishes_service = DishesService(repositories.dishes)
