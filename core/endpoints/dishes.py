from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session

router = APIRouter()


@router.get('/{menu_id}/submenus/{submenu_id}/dishes', status_code=200, response_model=List[schemas.ResponseDishSchema])
async def get_dish_list(
    menu_id: int, submenu_id: int, db: AsyncSession = Depends(get_session)
) -> List[schemas.ResponseDishSchema]:
    dish_list: List[schemas.ResponseDishSchema] = await services.dishes_service.get_dish_list(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )
    return dish_list


@router.post('/{menu_id}/submenus/{submenu_id}/dishes', status_code=201, response_model=schemas.ResponseDishSchema)
async def create_dish(
    menu_id: int, submenu_id: int, data: schemas.DishSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseDishSchema:
    dish: schemas.ResponseDishSchema = await services.dishes_service.create_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, data=data
    )
    return dish


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', status_code=200, response_model=schemas.ResponseDishSchema
)
async def detail_dish(
    menu_id: int, submenu_id: int, dish_id: int, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseDishSchema:
    dish: schemas.ResponseDishSchema = await services.dishes_service.get_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
    )
    return dish


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', status_code=200, response_model=schemas.ResponseDishSchema
)
async def update_dish(
    menu_id: int, submenu_id: int, dish_id: int, data: schemas.UpdateDishSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseDishSchema:
    dish: schemas.ResponseDishSchema = await services.dishes_service.update_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, data=data
    )
    return dish


@router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', status_code=200)
async def delete_dish(menu_id: int, submenu_id: int, dish_id: int, db: AsyncSession = Depends(get_session)) -> None:
    await services.dishes_service.delete_dish(db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id)
