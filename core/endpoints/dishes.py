from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session

router = APIRouter()


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=200,
    response_model=list[schemas.ResponseDishSchema],
    name='get_dish_list',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def get_dish_list(
    menu_id: UUID, submenu_id: UUID, db: AsyncSession = Depends(get_session)
) -> list[schemas.ResponseDishSchema]:
    """Get submenu's dishes."""

    dish_list: list[schemas.ResponseDishSchema] = await services.dishes_service.get_dish_list(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )
    return dish_list


@router.post(
    '/{menu_id}/submenus/{submenu_id}/dishes',
    status_code=201,
    response_model=schemas.ResponseDishSchema,
    name='create_dish',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def create_dish(
    bgtask: BackgroundTasks,
    menu_id: UUID,
    submenu_id: UUID,
    data: schemas.DishSchema,
    db: AsyncSession = Depends(get_session)
) -> schemas.ResponseDishSchema:
    """Add dish for submenu."""

    dish: schemas.ResponseDishSchema = await services.dishes_service.create_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, data=data, bgtask=bgtask
    )
    return dish


@router.get(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=200,
    response_model=schemas.ResponseDishSchema,
    name='get_dish',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def detail_dish(
    menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseDishSchema:
    """Get dish's detail."""

    dish: schemas.ResponseDishSchema = await services.dishes_service.get_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id
    )
    return dish


@router.patch(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=200,
    response_model=schemas.ResponseDishSchema,
    name='update_dish',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def update_dish(
    bgtask: BackgroundTasks,
    menu_id: UUID,
    submenu_id: UUID,
    dish_id: UUID,
    data: schemas.UpdateDishSchema,
    db: AsyncSession = Depends(get_session),
) -> schemas.ResponseDishSchema:
    """Update dish's properties:

    title, description and price.
    """

    dish: schemas.ResponseDishSchema = await services.dishes_service.update_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, data=data, bgtask=bgtask
    )
    return dish


@router.delete(
    '/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}',
    status_code=200,
    name='delete_dish',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def delete_dish(
        bgtask: BackgroundTasks, menu_id: UUID, submenu_id: UUID, dish_id: UUID, db: AsyncSession = Depends(get_session)
) -> None:
    """Delete dish."""

    await services.dishes_service.delete_dish(
        db=db, menu_id=menu_id, submenu_id=submenu_id, dish_id=dish_id, bgtask=bgtask
    )
