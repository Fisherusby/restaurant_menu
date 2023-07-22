from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session

router = APIRouter()


@router.get('', status_code=200, response_model=List[schemas.ResponseMenuSchema])
async def get_menu_list(db: AsyncSession = Depends(get_session)) -> List[schemas.ResponseMenuSchema]:
    menu_list: List[schemas.ResponseMenuSchema] = await services.menus_service.get_menu_list(db=db)
    return menu_list


@router.post('', status_code=201, response_model=schemas.ResponseMenuSchema)
async def create_menu(data: schemas.MenuSchema, db: AsyncSession = Depends(get_session)) -> schemas.ResponseMenuSchema:
    menu: schemas.ResponseMenuSchema = await services.menus_service.create_menu(db=db, data=data)
    return menu


@router.get('/{menu_id}', status_code=200, response_model=schemas.ResponseMenuWithCountSchema)
async def detail_menu(menu_id: int, db: AsyncSession = Depends(get_session)) -> schemas.ResponseMenuWithCountSchema:
    menu: schemas.ResponseMenuWithCountSchema = await services.menus_service.get_menu(db=db, menu_id=menu_id)
    return menu


@router.patch('/{menu_id}', status_code=200, response_model=schemas.ResponseMenuSchema)
async def update_menu(
    menu_id: int, data: schemas.UpdateMenuSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseMenuSchema:
    menu: schemas.ResponseMenuSchema = await services.menus_service.update_menu(db=db, menu_id=menu_id, data=data)
    return menu


@router.delete('/{menu_id}', status_code=200)
async def delete_menu(menu_id: int, db: AsyncSession = Depends(get_session)) -> None:
    await services.menus_service.delete_menu(db=db, menu_id=menu_id)
