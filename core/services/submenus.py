from uuid import UUID

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core import constants, models, repositories, schemas, services
from core.services.base import BaseObjectService


class SubmenusService(BaseObjectService):
    @staticmethod
    def gen_key(menu_id: UUID | str, submenu_id: UUID | str = '*', many=False) -> str:
        """Generate a key of cache for submenu and a list of submenus"""
        return f'submenu_{menu_id}_{"list" if many else submenu_id}'

    async def get_submenu_list(self, db: AsyncSession, menu_id: UUID) -> list[schemas.ResponseSubmenuSchema]:
        """Get a list of submenus in menu."""

        submenu_list_key: str = self.gen_key(menu_id=menu_id, many=True)
        submenu_list_cache: list[schemas.ResponseSubmenuSchema] = await services.redis_service.get(submenu_list_key)
        if submenu_list_cache is not None:
            return submenu_list_cache

        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        submenu_list: list[models.SubmenuDBModel] = await self.repository.get_mul_by_fields(
            db=db, fields={'menu_id': menu_id}
        )
        response_submenu_list: list[schemas.ResponseSubmenuSchema] = [
            schemas.ResponseSubmenuSchema(**obj.to_dict()) for obj in submenu_list
        ]
        await services.redis_service.set(submenu_list_key, response_submenu_list)

        return response_submenu_list

    async def get_submenu(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> schemas.ResponseSubmenuWithCountSchema:
        """Get submenu data by IDs of menu and submenu."""

        submenu_key: str = self.gen_key(menu_id=menu_id, submenu_id=submenu_id)
        cache_submenu: schemas.ResponseSubmenuWithCountSchema = await services.redis_service.get(submenu_key)
        if cache_submenu is not None:
            return cache_submenu

        submenu: tuple[models.SubmenuDBModel, int] | None = await self.repository.get_submenu_with_dish_count(
            db=db, submenu_id=submenu_id, menu_id=menu_id
        )

        if submenu is None:
            raise HTTPException(status_code=404, detail='submenu not found')

        response_submenu: schemas.ResponseSubmenuWithCountSchema = schemas.ResponseSubmenuWithCountSchema(
            **submenu[0].to_dict(), dishes_count=submenu[1] if submenu[1] is not None else 0
        )
        await services.redis_service.set(submenu_key, response_submenu)

        return response_submenu

    async def get_submenu_by_id_or_404(
        self, db: AsyncSession, menu_id: UUID, submenu_id: UUID
    ) -> models.SubmenuDBModel:
        """Get submenu data by IDs of menu and submenu or rise http 404 if non-exist."""
        submenu: models.SubmenuDBModel | None = await self.repository.get_one_by_fields(
            db=db,
            fields={
                'id': submenu_id,
                'menu_id': menu_id,
            },
        )

        if submenu is None:
            raise HTTPException(status_code=404, detail='submenu not found')

        return submenu

    async def create_submenu(
        self, db: AsyncSession, menu_id: UUID, data: schemas.SubmenuSchema, bgtask: BackgroundTasks
    ) -> schemas.ResponseSubmenuSchema:
        """Create submenu in menu."""
        await services.menus_service.get_menu_by_id_or_404(db=db, menu_id=menu_id)
        obj_in: schemas.SubmenuWithMenuIdSchema = schemas.SubmenuWithMenuIdSchema(**data.model_dump(), menu_id=menu_id)
        submenu: models.SubmenuDBModel = await self.repository.create(db=db, obj_in=obj_in)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.CREATE,
            menu_id=menu_id,
        )

        return schemas.ResponseSubmenuSchema(**submenu.to_dict())

    async def update_submenu(
        self,
        db: AsyncSession,
        menu_id: UUID,
        submenu_id: UUID,
        data: schemas.UpdateSubmenuSchema,
        bgtask: BackgroundTasks
    ) -> schemas.ResponseSubmenuSchema:
        """Update submenu data."""
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )
        updated_submenu: models.SubmenuDBModel = await self.repository.update(db=db, db_obj=sub_menu, obj_in=data)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.UPDATE,
            menu_id=menu_id,
            submenu_id=submenu_id,
        )

        return schemas.ResponseSubmenuSchema(**updated_submenu.to_dict())

    async def delete_submenu(self, db: AsyncSession, menu_id: UUID, submenu_id: UUID, bgtask: BackgroundTasks):
        """Delete submenu by IDs of menu adn submenu."""
        sub_menu: models.SubmenuDBModel = await self.get_submenu_by_id_or_404(
            db=db, menu_id=menu_id, submenu_id=submenu_id
        )

        await self.repository.delete_by_id(db=db, obj_id=sub_menu.id)

        bgtask.add_task(
            self.clearing_cache_process,
            operation=constants.DELETE,
            menu_id=menu_id,
            submenu_id=submenu_id,
        )

    async def clearing_cache_process(self, operation: str, menu_id: UUID, submenu_id: UUID | None = None) -> None:
        """Clear cache after create, update, delete."""
        patterns: list[str] = await self.clearing_cache_patterns(
            operation=operation, menu_id=menu_id, submenu_id=submenu_id)
        await services.redis_service.del_by_pattens(*patterns)

    async def clearing_cache_patterns(self, operation: str, menu_id: UUID, submenu_id: UUID | None) -> list[str]:
        """Generate patterns for key by operation type (create, update, delete)"""
        if operation == constants.CREATE:
            return [
                services.menus_service.gen_key(menu_id=menu_id),
                self.gen_key(menu_id=menu_id, many=True),
            ]

        if submenu_id is None:
            return []

        if operation == constants.UPDATE:
            return [
                self.gen_key(menu_id=menu_id, many=True),
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id),
            ]

        if operation == constants.DELETE:
            return [
                services.menus_service.gen_key(menu_id=menu_id),
                self.gen_key(menu_id=menu_id, many=True),
                self.gen_key(menu_id=menu_id, submenu_id=submenu_id),
                services.dishes_service.gen_key(menu_id=menu_id, submenu_id=submenu_id)
            ]

        return []


submenus_service: SubmenusService = SubmenusService(repositories.submenus)
