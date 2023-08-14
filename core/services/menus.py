import itertools
from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import constants, models, repositories, schemas, services
from core.services.base import BaseObjectService


class MenusService(BaseObjectService):
    @staticmethod
    def gen_key(menu_id: UUID | None = None, many: bool = False) -> str:
        """Generate a key of cache for menu and a list of menus"""
        return f"menu_{'list' if many else menu_id}"

    async def get_menu_list(self, db: AsyncSession) -> list[schemas.ResponseMenuSchema]:
        """Get a list of menus."""

        menu_list_key: str = self.gen_key(many=True)
        menu_list_cache: list[schemas.ResponseMenuSchema] = await services.redis_service.get(menu_list_key)
        if menu_list_cache is not None:
            return menu_list_cache

        menu_list: list[models.MenuDBModel] = await self.repository.get_all(db=db)
        response_menu_list: list[schemas.ResponseMenuSchema] = [
            schemas.ResponseMenuSchema(**obj.to_dict()) for obj in menu_list
        ]
        await services.redis_service.set(menu_list_key, response_menu_list)

        return response_menu_list

    async def get_menu(self, db: AsyncSession, menu_id: UUID) -> schemas.ResponseMenuWithCountSchema:
        """Get menu data by ID."""

        menu_key: str = self.gen_key(menu_id=menu_id)
        cache_menu: schemas.ResponseMenuWithCountSchema = await services.redis_service.get(menu_key)
        if cache_menu is not None:
            return cache_menu

        menu: tuple[models.MenuDBModel, int, int] | None = await self.repository.get_menu_with_counts(
            db=db, menu_id=menu_id
        )

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        menu_response: schemas.ResponseMenuWithCountSchema = schemas.ResponseMenuWithCountSchema(
            **menu[0].to_dict(),
            submenus_count=menu[1] if menu[1] is not None else 0,
            dishes_count=menu[2] if menu[2] is not None else 0
        )

        await services.redis_service.set(menu_key, menu_response)

        return menu_response

    async def create_menu(
            self, db: AsyncSession, data: schemas.MenuSchema, bgtask: BackgroundTasks
    ) -> schemas.ResponseMenuSchema:
        """Create menu."""
        menu: models.MenuDBModel = await self.repository.create(db=db, obj_in=data)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.CREATE
        )

        return schemas.ResponseMenuSchema(**menu.to_dict())

    async def update_menu(
        self, db: AsyncSession, menu_id: UUID, data: schemas.UpdateMenuSchema, bgtask: BackgroundTasks
    ) -> schemas.ResponseMenuSchema:
        """Update menu data."""
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        updated_menu = await self.repository.update(db=db, obj_in=data, db_obj=menu)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.UPDATE,
            menu_id=menu_id
        )

        return schemas.ResponseMenuSchema(**updated_menu.to_dict())

    async def delete_menu(self, db: AsyncSession, menu_id: UUID, bgtask: BackgroundTasks) -> None:
        """Delete menu."""
        await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        await self.repository.delete_by_id(db=db, obj_id=menu_id)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.DELETE,
            menu_id=menu_id
        )

    async def get_menu_by_id_or_404(self, db: AsyncSession, menu_id: UUID) -> models.MenuDBModel:
        """Get menu data by ID or rise http 404 if non-exist."""
        menu: models.MenuDBModel | None = await self.repository.get_by_id(db=db, obj_id=menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        return menu

    async def clearing_cache_process(self, operation: str, menu_id: UUID | None = None) -> None:
        """Clear cache after create, update, delete."""
        patterns: list[str] = await self.clearing_cache_patterns(operation=operation, menu_id=menu_id)
        await services.redis_service.del_by_pattens(*patterns)

    async def clearing_cache_patterns(self, operation: str, menu_id: UUID | None) -> list[str]:
        """Generate patterns for key by operation type (create, update, delete)"""
        if operation == constants.CREATE:
            return [self.gen_key(many=True)]

        if menu_id is None:
            return []

        if operation == constants.UPDATE:
            return [
                self.gen_key(many=True),
                self.gen_key(menu_id=menu_id),
            ]

        if operation == constants.DELETE:
            return [
                self.gen_key(many=True),
                self.gen_key(menu_id=menu_id),
                services.dishes_service.gen_key(menu_id=menu_id),
                services.submenus_service.gen_key(menu_id=menu_id),
            ]
        return []

    async def get_all_in_one(self, db: AsyncSession) -> list[schemas.ResponseMenuWitSubmenusSchema]:
        all_data: list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]] = (
            await self.repository.get_all_in_one(db=db)
        )
        response_data: list[schemas.ResponseMenuWitSubmenusSchema] = []
        for menu, menu_group in itertools.groupby(all_data, key=lambda x: x[0]):
            submenus: list[schemas.ResponseSubmenuWithDishesSchema] = []
            for submenu, submenu_group in itertools.groupby(menu_group, key=lambda x: x[1]):
                if submenu is None:
                    continue
                dishes: list[schemas.ResponseDishSchema] = []
                for _, _, dish in submenu_group:
                    if dish is None:
                        continue
                    dishes.append(
                        services.dishes_service.to_schema_with_discount(dish)
                    )
                submenus.append(schemas.ResponseSubmenuWithDishesSchema(**submenu.to_dict(), dishes=dishes))
            response_data.append(schemas.ResponseMenuWitSubmenusSchema(**menu.to_dict(), submenus=submenus))
        return response_data


menus_service: MenusService = MenusService(repositories.menus)
