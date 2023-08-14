from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import constants, models, repositories, schemas, services
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

        dish_list: list[models.DishDBModel] = await self.repository.get_dish_list_by_submenu_id(
            db=db, submenu_id=submenu_id
        )
        response_dish_list: list[schemas.ResponseDishSchema] = [
            self.to_schema_with_discount(dish) for dish in dish_list
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
        response_dish: schemas.ResponseDishSchema = self.to_schema_with_discount(dish)
        await services.redis_service.set(cache_key, response_dish)
        return response_dish

    def to_schema_with_discount(self, dish: models.DishDBModel) -> schemas.ResponseDishSchema:
        """Apply discount if it exists"""
        if dish.discount is not None:
            dish.price = round(dish.price * (1 - dish.discount.value / 100), 2)
        return schemas.ResponseDishSchema(**dish.to_dict())

    async def get_dish_by_id_or_404(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID
    ) -> models.DishDBModel:
        """Get dish data or rise http 404 by IDs of dish, menu and submenu."""
        dish: models.DishDBModel | None = await self.repository.get_dish(
            db=db, dish_id=dish_id, submenu_id=submenu_id
        )

        if dish is None:
            raise HTTPException(status_code=404, detail='dish not found')

        return dish

    async def create_dish(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, data: schemas.DishSchema, bgtask: BackgroundTasks
    ) -> schemas.ResponseDishSchema:
        """Create dish in menu's submenu."""
        await services.submenus_service.get_submenu_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id)
        obj_in: schemas.DishWithSubmenuIdSchema = schemas.DishWithSubmenuIdSchema(
            **data.model_dump(), submenu_id=submenu_id
        )
        dish: models.DishDBModel = await self.repository.create(db=db, obj_in=obj_in)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.CREATE,
            menu_id=menu_id,
            submenu_id=submenu_id,
        )

        return schemas.ResponseDishSchema(**dish.to_dict())

    async def update_dish(
        self,
        db: AsyncSession,
        menu_id: UUID,
        submenu_id: UUID,
        dish_id: UUID,
        data: schemas.UpdateDishSchema,
        bgtask: BackgroundTasks
    ) -> schemas.ResponseDishSchema:
        """Update dish data."""
        dish: models.DishDBModel = await self.get_dish_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        updated_dish: models.DishDBModel = await self.repository.update(db=db, db_obj=dish, obj_in=data)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.UPDATE,
            menu_id=menu_id,
            submenu_id=submenu_id,
            dish_id=dish_id
        )

        return schemas.ResponseDishSchema(**updated_dish.to_dict())

    async def delete_dish(
            self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, dish_id: UUID, bgtask: BackgroundTasks
    ) -> None:
        """Delete dish."""

        await self.get_dish_by_id_or_404(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)

        await self.repository.delete_by_id(db=db, obj_id=dish_id)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.DELETE,
            menu_id=menu_id,
            submenu_id=submenu_id,
            dish_id=dish_id
        )

    async def clearing_cache_process(
            self, operation: str, menu_id: UUID, submenu_id: UUID, dish_id: UUID | None = None
    ) -> None:
        """Clear cache after create, update, delete."""
        patterns: list[str] = await self.clearing_cache_patterns(
            operation=operation, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
        )
        await services.redis_service.del_by_pattens(*patterns)

    async def clearing_cache_patterns(
            self, operation: str, menu_id: UUID, submenu_id: UUID, dish_id: UUID | None
    ) -> list[str]:
        """Generate patterns for key by operation type (create, update, delete)"""
        if operation == constants.CREATE:
            return [
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True),
                services.submenus_service.gen_key(menu_id=menu_id, submenu_id=submenu_id),
                services.menus_service.gen_key(menu_id=menu_id),
            ]

        if dish_id is None:
            return []

        if operation == constants.UPDATE:
            return [
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id),
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True),
            ]

        if operation == constants.DELETE:
            return [
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id, many=True),
                services.submenus_service.gen_key(menu_id=menu_id, submenu_id=submenu_id),
                services.menus_service.gen_key(menu_id=menu_id),
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
            ]

        return []


dishes_service = DishesService(repositories.dishes)
