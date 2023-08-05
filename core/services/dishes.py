from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas, services
from core.services.base import BaseObjectService


class DishesService(BaseObjectService):
    """Service for dishes data."""
    @staticmethod
    def gen_key(menu_id: UUID, submenu_id: UUID | str = '*', dish_id: UUID | str = '*', many=False) -> str:
        """Generate a key of cache for submenu and a list of submenus"""
        return f'dish_{menu_id}_{submenu_id}_{"list" if many else dish_id}'

    async def get_dish_list(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> list[schemas.ResponseDishSchema]:
        """Get a list of dishes in submenu by IDs of menu and submenu."""
        # Postman tests expect empty list in non-existent submenu...
        # await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        cache_list_key: str = self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True)
        cache_dish_list: list[schemas.ResponseDishSchema] = await services.redis_service.get(cache_list_key)
        if cache_dish_list is not None:
            return cache_dish_list

        dish_list: list[models.DishDBModel] = await self.repository.get_mul_by_fields(
            db=db, fields={'submenu_id': submenu_id}
        )
        response_dish_list: list[schemas.ResponseDishSchema] = [
            schemas.ResponseDishSchema(**obj.to_dict()) for obj in dish_list
        ]
        await services.redis_service.set(cache_list_key, response_dish_list)

        return response_dish_list

    async def get_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID
    ) -> schemas.ResponseDishSchema:
        """Get dish data by IDs of dish, menu and submenu."""
        cache_key: str = self.gen_key(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
        cache_dish: schemas.ResponseDishSchema = await services.redis_service.get(cache_key)

        if cache_dish is not None:
            return cache_dish

        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        response_dish: schemas.ResponseDishSchema = schemas.ResponseDishSchema(**dish.to_dict())
        await services.redis_service.set(cache_key, response_dish)
        return response_dish

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
        obj_in: schemas.DishWithSubmenuIdSchema = schemas.DishWithSubmenuIdSchema(
            **data.model_dump(), submenu_id=submenu_id
        )
        dish: models.DishDBModel = await self.repository.create(db=db, obj_in=obj_in)
        await self.clear_cache(menu_id=menu_id, submenu_id=submenu_id)

        return schemas.ResponseDishSchema(**dish.to_dict())

    async def update_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID, data: schemas.UpdateDishSchema
    ) -> schemas.ResponseDishSchema:
        """Update dish data."""
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        updated_dish: models.DishDBModel = await self.repository.update(db=db, db_obj=dish, obj_in=data)

        await services.redis_service.delete(
            self.gen_key(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id),
            self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True),
        )

        return schemas.ResponseDishSchema(**updated_dish.to_dict())

    async def delete_dish(self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID) -> None:
        """Delete dish."""
        await self.get_dish_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

        await self.repository.delete_by_id(db=db, obj_id=dish_id)
        await self.clear_cache(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

    async def clear_cache(self, menu_id: UUID, submenu_id: UUID, dish_id: UUID | None = None) -> None:
        """Clearing cache when create or delete dish"""
        patterns: list[str] = [
            self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True),
            services.submenus_service.gen_key(menu_id=menu_id, submenu_id=submenu_id),
            services.menus_service.gen_key(menu_id=menu_id),
        ]
        if dish_id is not None:
            patterns.append(self.gen_key(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id))

        await services.redis_service.delete(*patterns)


dishes_service = DishesService(repositories.dishes)
