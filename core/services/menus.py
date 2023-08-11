import itertools
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import models, repositories, schemas, services
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

    async def create_menu(self, db: AsyncSession, data: schemas.MenuSchema) -> schemas.ResponseMenuSchema:
        """Create menu."""
        menu: models.MenuDBModel = await self.repository.create(db=db, obj_in=data)
        await services.redis_service.del_by_pattens(self.gen_key(many=True))

        return schemas.ResponseMenuSchema(**menu.to_dict())

    async def update_menu(
        self, db: AsyncSession, menu_id: UUID, data: schemas.UpdateMenuSchema
    ) -> schemas.ResponseMenuSchema:
        """Update menu data."""
        menu: models.MenuDBModel = await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)

        await services.redis_service.del_by_pattens(
            self.gen_key(menu_id),
            self.gen_key(many=True)
        )
        updated_menu = await self.repository.update(db=db, obj_in=data, db_obj=menu)
        return schemas.ResponseMenuSchema(**updated_menu.to_dict())

    async def delete_menu(self, db: AsyncSession, menu_id: UUID) -> None:
        """Delete menu."""
        await self.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        await self.repository.delete_by_id(db=db, obj_id=menu_id)

        await self.clear_cache(menu_id)

    async def get_menu_by_id_or_404(self, db: AsyncSession, menu_id: UUID) -> models.MenuDBModel:
        """Get menu data by ID or rise http 404 if non-exist."""
        menu: models.MenuDBModel | None = await self.repository.get_by_id(db=db, obj_id=menu_id)

        if menu is None:
            raise HTTPException(status_code=404, detail='menu not found')

        return menu

    async def clear_cache(self, menu_id: UUID) -> None:
        """Clearing cache when delete menu"""
        await services.redis_service.del_by_pattens(
            services.dishes_service.gen_key(menu_id=menu_id),
            services.submenus_service.gen_key(menu_id=menu_id),
            self.gen_key(menu_id=menu_id),
            self.gen_key(many=True)
        )

    async def get_all_in_one(self, db: AsyncSession) -> list[schemas.ResponseMenuWitSubmenusSchema]:
        all_data: list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]] = (
            await self.repository.get_all_in_one(db=db)
        )
        response_data: list[schemas.ResponseMenuWitSubmenusSchema] = []
        for menu, menu_group in itertools.groupby(all_data, key=lambda x: x[0]):
            submenus: list[schemas.ResponseSubmenuWithDishesSchema] = []
            for submenu, dishes_group in itertools.groupby(menu_group, key=lambda x: x[1]):
                if submenu is None:
                    continue
                dishes: list[schemas.ResponseDishSchema] = []
                for _, _, dish in dishes_group:
                    if dish is None:
                        continue
                    dishes.append(schemas.ResponseDishSchema(**dish.to_dict()))
                submenus.append(schemas.ResponseSubmenuWithDishesSchema(**submenu.to_dict(), dishes=dishes))
            response_data.append(schemas.ResponseMenuWitSubmenusSchema(**menu.to_dict(), submenus=submenus))
        return response_data


menus_service: MenusService = MenusService(repositories.menus)
