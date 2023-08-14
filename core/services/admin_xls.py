import contextlib
import logging
import os
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Any, Generic, TypeVar
from uuid import UUID

import aiohttp
import pandas as pd
from pandas.errors import ParserError
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core import constants as const
from core import models, repositories, schemas, services
from core.db import session_generator
from core.repositories.base import BaseRepository, ModelType
from core.services.dishes import DishesService
from core.services.menus import MenusService
from core.services.submenus import SubmenusService

ParsingSchemaType = TypeVar('ParsingSchemaType', bound=BaseModel)


class ParsingXLSError(Exception):
    pass


class XLSAdminService(Generic[ParsingSchemaType, ModelType]):

    repositories: dict[str, BaseRepository] = {
        const.MENU: repositories.menus,
        const.SUBMENU: repositories.submenus,
        const.DISH: repositories.dishes,
    }

    services: dict[str, DishesService | MenusService | SubmenusService] = {
        const.MENU: services.menus_service,
        const.SUBMENU: services.submenus_service,
        const.DISH: services.dishes_service,
    }

    schemas: dict[str, type[ParsingSchemaType]] = {
        const.MENU: schemas.ParsingFileMenuSchema,
        const.SUBMENU: schemas.ParsingFileSubmenuSchema,
        const.DISH: schemas.ParsingFileDishSchema,
    }

    mapping = {
        const.MENU: const.mapping_menu,
        const.SUBMENU: const.mapping_submenu,
        const.DISH: const.mapping_dish,
    }

    entities_offset: list[str] = [const.MENU, const.SUBMENU, const.DISH]

    def __init__(self, source: str, logger: logging.Logger | None = None):
        self.source: str = source
        self.db_gen = session_generator
        self.__to_db: list[tuple[str, str, UUID, dict[str, str] | None, Any, dict[str, UUID]]] = []
        self.__file_discount: dict[UUID, Decimal] = {}
        self.__DB_discount: dict[UUID, models.DiscountDBModel] = {}
        self.logger: logging.Logger = logger if logger is not None else logging.getLogger(__name__)

    async def run(self):
        """Runner to compare data in source and DB"""
        self.logger.info('Check for update DB started')
        self.__clear_before_run()
        incoming_data = await self.read_from_source()
        if incoming_data is None:
            return False
        try:
            data_in_file = await self.worksheet_data_process(incoming_data)
        except ParsingXLSError:
            return False

        data_in_db = await self.get_db_data()
        await self.__compare_process(in_db=data_in_db, in_file=data_in_file)
        await self.apply_changes_process()
        self.logger.info('Check for update DB finished')
        return True

    def __clear_before_run(self):
        self.__to_db: list[tuple[str, str, UUID, dict[str, str] | None, Any, dict[str, UUID]]] = []
        self.__file_discount: dict[UUID, Decimal] = {}
        self.__DB_discount: dict[UUID, models.DiscountDBModel] = {}

    async def read_from_source(self) -> pd.DataFrame | None:
        """Read data from source to pandas DataFrame"""
        if self.source.startswith('https://docs.google.com/spreadsheets/'):
            self.source = self.source.replace('edit#gid', 'export?format=csv&gid')
            self.logger.info('Source is Google Sheets')
            data = await self.read_google_sheet(
                url=self.source,
            )
            return data

        is_file_exist = os.path.isfile(self.source)
        if not is_file_exist:
            self.logger.error(f'Source does not exist: {self.source}')
            return None

        self.logger.info('Source is file')
        return await self.read_file_data()

    async def read_google_sheet(self, url: str) -> pd.DataFrame | None:
        """Read data from request to pandas DataFrame"""
        self.logger.info('Get data from Google Sheets started')
        self.logger.info('Remote source is: %s', url)
        data: bytes | None = await self.request_google_sheet(url=url)
        if data is None:
            return None
        try:
            worksheet: pd.DataFrame = pd.read_csv(BytesIO(data), header=None, )
        except (UnboundLocalError, ParserError):
            self.logger.error('Failure to read downloaded data from Google Sheet')
            return None

        self.logger.info('Get data from Google Sheets finished')
        return worksheet

    async def request_google_sheet(self, url: str) -> bytes | None:
        """Request data from Google Sheets"""
        self.logger.info('Request data from Google Sheets started')
        with contextlib.suppress(Exception):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data: bytes = await self.read_stream_content(response)
                    else:
                        self.logger.error(
                            'Failure to request data from Google Sheets. Response status is %s', response.status
                        )
                        return None
        self.logger.info('Request data from Google Sheets finished')
        return data

    async def read_stream_content(self, response: aiohttp.ClientResponse) -> bytes:
        """Download data from stream"""
        buffer: bytes = b''
        async for data, end_of_http_chunk in response.content.iter_chunks():
            buffer += data
            if end_of_http_chunk:
                break
        return buffer

    async def read_file_data(self) -> pd.DataFrame | None:
        """Read data from file to pandas DataFrame"""
        self.logger.info('Read xlsx started')
        try:
            worksheet: pd.DataFrame = pd.read_excel(self.source, sheet_name=0, header=None, )
        except ValueError as e:
            self.logger.error('Failure to read data from file: %s', e)
            return None
        self.logger.info('Read xlsx finished')
        return worksheet

    async def apply_changes_process(self) -> None:
        """Runner for apply changes to DB"""
        async with self.db_gen() as db:
            await self.__apply_changes_process(db=db)
            await self.__apply_discount(db=db)

    async def __apply_changes_process(self, db: AsyncSession) -> None:
        """Apply changes to DB"""
        if not self.__to_db:
            self.logger.info('Data in source and database are equal')
            return None
        self.logger.info('Apply changes started')
        patterns = set()
        for entity, operation, obj_id, data, db_obj, ids in self.__to_db:
            if operation == const.DELETE:
                await self.repositories[entity].delete_by_id(db=db, obj_id=obj_id)

            if operation == const.UPDATE:
                await self.repositories[entity].update(db=db, db_obj=db_obj, obj_in=data)
            if operation == const.CREATE:
                await self.repositories[entity].create(db=db, obj_in=data)
            self.logger.info('Applied %s %s[%s]', operation, entity, obj_id)
            patterns.update(await self.services[entity].clearing_cache_patterns(operation, **ids))
        if patterns:
            self.logger.info('Clearing cache')
            await services.redis_service.del_by_pattens(*patterns)
        self.logger.info('Apply changes finished')

    async def __compare_process(self, in_db, in_file):
        """Compare DB and file objects to find differences."""
        self.logger.info('Comparison process started')
        await self.__compare_entity(entity=const.MENU, in_db=in_db, in_file=in_file)
        self.__to_db = sorted(
            self.__to_db,
            key=lambda x: (const.order_operation.index(x[1]), const.order_entity.index(x[0])),
        )
        self.logger.info('Comparison process finished')

    async def __compare_entity(
            self, entity: str, in_db: dict[UUID, Any], in_file: dict[UUID, Any], ids: dict[str, UUID] = {}
    ) -> None:
        """Compare entities. Creating the required tasks."""
        for entity_id, entity_in_db in in_db.items():
            entity_ids: dict[str, UUID] = dict(**ids)
            entity_ids[f'{entity}_id'] = entity_id
            if entity_id not in in_file:
                self.logger.info('Need to delete %s[%s]', entity, entity_id)
                self.__to_db.append((entity, const.DELETE, entity_id, None, None, entity_ids))
                continue
            entity_in_file: dict[str, Any] = in_file.pop(entity_id)
            is_entity_change: dict[str, Any] = self.is_changed(entity_in_db['db_obj'], entity_in_file)
            if is_entity_change:
                self.logger.info(
                    'Need to change %s[%s]: %s', entity, entity_id, is_entity_change
                )
                self.__to_db.append((entity, const.UPDATE, entity_id, is_entity_change,
                                    entity_in_db['db_obj'], entity_ids))

            entity_child: str | None = const.entity_child[entity]
            if entity_child is not None:
                await self.__compare_entity(
                    entity_child, in_db=entity_in_db['child'], in_file=entity_in_file['child'], ids=entity_ids
                )
        if in_file:
            await self.__entity_to_create(entity=entity, in_file=in_file, ids=ids)

    @staticmethod
    def is_changed(db_obj: ModelType, file_obj: dict[str, Any]) -> dict[str, str]:
        """Compare entities. Return dict of differences"""
        changed: dict[str, str] = {}
        for field in file_obj:
            if isinstance(file_obj[field], dict):
                continue
            if getattr(db_obj, field) != file_obj[field]:
                changed[field] = str(file_obj[field])
        return changed

    async def __entity_to_create(self, entity: str, in_file: dict[UUID, dict[str, Any]], ids: dict[str, UUID]) -> None:
        """Create tasks for create entity objects in DB"""
        for entity_in_file in in_file.values():
            entity_ids: dict[str, UUID] = dict(**ids)
            entity_ids[f'{entity}_id'] = entity_in_file['id']
            data: dict[str, Any] = {k: entity_in_file[k] for k in const.mapping_entity_to_create[entity]}
            self.logger.info(
                'Need to create %s: %s', entity, data
            )
            self.__to_db.append((entity, const.CREATE, entity_in_file['id'], data, None, entity_ids))
            entity_child: str | None = const.entity_child[entity]
            if entity_child is None or not entity_in_file['child']:
                continue
            await self.__entity_to_create(entity=entity_child, in_file=entity_in_file['child'], ids=entity_ids)

    async def get_db_data(self) -> dict[UUID, dict]:
        """Convert all DB objects to dict"""
        all_data: list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]] = (
            await self.__get_db_data()
        )
        result: dict[UUID, dict] = {}

        for menu, submenu, dish in all_data:
            menu_id: UUID = menu.id
            if menu_id not in result:
                result[menu_id] = {
                    'db_obj': menu,
                    'child': {}
                }
            if submenu is None:
                continue
            submenu_id: UUID = submenu.id
            if submenu_id not in result[menu_id]['child']:
                result[menu_id]['child'][submenu_id] = {
                    'db_obj': submenu,
                    'child': {}
                }
            if dish is None:
                continue
            dish_id: UUID = dish.id
            result[menu_id]['child'][dish.submenu_id]['child'][dish_id] = {
                'db_obj': dish,
            }
            if dish.discount is not None:
                self.__DB_discount[dish_id] = dish.discount

        return result

    async def __get_db_data(
            self
    ) -> list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]]:
        """Get all DB objects"""
        async with self.db_gen() as db:
            result: list[tuple[models.MenuDBModel, models.SubmenuDBModel | None, models.DishDBModel | None]] = (
                await repositories.menus.get_all_in_one(db=db)
            )
        return result

    def __row_to_entity_dict(self, entity: str, row: pd.Series, **kwargs: UUID | None) -> dict[str, Any]:
        """Converting data from a row to the entity dict"""
        parsing_data: dict[str, Any] = dict(zip(self.mapping[entity], row), **kwargs)
        return self.schemas[entity](**parsing_data).model_dump()

    def __find_entity(self, row, **ids) -> tuple[str | None, dict[str, Any] | None]:
        """Finding entity in a row of data received from the source"""
        for offset, entity in enumerate(self.entities_offset):
            if not pd.isna(row[offset]):
                if const.entity_parents[entity] is not None and not ids.get(f'{const.entity_parents[entity]}_id'):
                    continue
                try:
                    entity_obj: dict[str, str | UUID] = self.__row_to_entity_dict(entity, row[offset:], **ids)
                    return entity, entity_obj
                except ValidationError as e:
                    return f'there is a parsing error for {entity}: {e}', None

        return None, None

    async def worksheet_data_process(self, worksheet: pd.DataFrame) -> dict[UUID, dict[str, Any]]:
        """Parsings data from pandas DataFrame"""
        current_row_index: int = -1

        all_data: dict[Any, dict[str, Any]] = {}

        current_menu_id: UUID | None = None
        current_submenu_id: UUID | None = None

        entity_ids: dict[str, list] = {
            const.MENU: [],
            const.SUBMENU: [],
            const.DISH: [],
        }
        errors: list[str] = []
        skip_rows: list[str] = []
        while current_row_index + 1 < len(worksheet):
            current_row_index += 1

            row_cells: pd.Series = worksheet.iloc[current_row_index]

            is_entity, entity_obj = self.__find_entity(
                row_cells, menu_id=current_menu_id, submenu_id=current_submenu_id
            )
            if is_entity is not None and is_entity not in const.ENTITIES:
                errors.append(f'{is_entity} in {current_row_index + 1} row')
                continue

            if is_entity is None or entity_obj is None:
                skip_rows.append(str(current_row_index + 1))
                continue

            if entity_obj['id'] not in entity_ids[is_entity]:
                entity_ids[is_entity].append(entity_obj['id'])
            else:
                errors.append(f'duplicate {is_entity} id={entity_obj["id"]} in {current_row_index + 1} row')

            if is_entity == const.MENU:
                menu: dict[str, Any] = dict(
                    **entity_obj,
                    child={},
                )
                current_menu_id = menu['id']
                all_data[current_menu_id] = menu
            elif is_entity == const.SUBMENU and current_menu_id is not None:
                submenu: dict[str, Any] = dict(
                    **entity_obj,
                    child={},
                )
                current_submenu_id = submenu['id']
                all_data[current_menu_id]['child'][current_submenu_id] = submenu
            elif is_entity == const.DISH and current_submenu_id is not None and current_menu_id is not None:
                dish_id = entity_obj['id']
                try:
                    self.__find_discount(row_cells, dish_id)
                except (ValueError, InvalidOperation):
                    errors.append(
                        f'there is a parsing error for dish discount in {current_row_index + 1} row.'
                        'Discount value can be only between 0 and 100.'
                    )
                all_data[current_menu_id]['child'][current_submenu_id]['child'][dish_id] = entity_obj

        if skip_rows:
            logging.warning('PARSE FILE: missed rows: %s', ', '.join(skip_rows))

        if errors:
            for error in errors:
                self.logger.error('PARSE FILE: %s', error)
            raise ParsingXLSError('\n'.join(errors))

        return all_data

    def __find_discount(self, row: pd.Series, dish_id: UUID) -> None:
        """Read discount from file data."""
        if not pd.isna(row[6]):
            discount: Decimal = Decimal(row[6]).quantize(Decimal('.01'))
            if discount < 0 or discount > 100:
                raise ValueError
            self.__file_discount[dish_id] = discount

    async def __apply_discount(self, db: AsyncSession):
        """Apply discount changes to DB"""
        for dish_id, value in self.__file_discount.items():
            if dish_id not in self.__DB_discount:
                await repositories.discount.create(
                    db=db,
                    obj_in={
                        'dish_id': dish_id,
                        'value': value,
                    }
                )
                self.logger.info('Added discount %s percent for dish[%s]', value, dish_id)
                continue

            db_obj: models.DiscountDBModel = self.__DB_discount.pop(dish_id)
            if db_obj.value != value:
                self.logger.info(
                    'Updated discount from %s fo %s percent for dish[%s]', db_obj.value, value, dish_id
                )
                await repositories.discount.update(db=db, db_obj=db_obj, obj_in={'value': value})

        for db_obj in self.__DB_discount.values():
            await repositories.discount.delete_by_id(db=db, obj_id=db_obj.id)
            self.logger.info(
                'Deleted discount %s percent for dish[%s]', db_obj.value, db_obj.id
            )
