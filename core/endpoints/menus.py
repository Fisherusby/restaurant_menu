from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session

router = APIRouter()


@router.get('', status_code=200, response_model=list[schemas.ResponseMenuSchema], name='get_menu_list')
async def get_menu_list(db: AsyncSession = Depends(get_session)) -> list[schemas.ResponseMenuSchema]:
    """Get menus."""

    menu_list: list[schemas.ResponseMenuSchema] = await services.menus_service.get_menu_list(db=db)
    return menu_list


@router.post('', status_code=201, response_model=schemas.ResponseMenuSchema, name='create_menu')
async def create_menu(
        bgtask: BackgroundTasks, data: schemas.MenuSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseMenuSchema:
    """Add menu."""

    menu: schemas.ResponseMenuSchema = await services.menus_service.create_menu(db=db, data=data, bgtask=bgtask)
    return menu


@router.get(
    '/{menu_id}',
    status_code=200,
    response_model=schemas.ResponseMenuWithCountSchema,
    name='get_menu',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def detail_menu(menu_id: UUID, db: AsyncSession = Depends(get_session)) -> schemas.ResponseMenuWithCountSchema:
    """Get menu's detail."""

    menu: schemas.ResponseMenuWithCountSchema = await services.menus_service.get_menu(db=db, menu_id=menu_id)
    return menu


@router.patch(
    '/{menu_id}',
    status_code=200,
    response_model=schemas.ResponseMenuSchema,
    name='update_menu',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def update_menu(
    bgtask: BackgroundTasks, menu_id: UUID, data: schemas.UpdateMenuSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseMenuSchema:
    """Update menu's properties:

    title and description.
    """

    menu: schemas.ResponseMenuSchema = await services.menus_service.update_menu(
        db=db, menu_id=menu_id, data=data, bgtask=bgtask
    )
    return menu


@router.delete(
    '/{menu_id}',
    status_code=200,
    name='delete_menu',
    responses={404: {'model': schemas.NotFoundSchema, 'description': 'Not Found Error'}},
)
async def delete_menu(bgtask: BackgroundTasks, menu_id: UUID, db: AsyncSession = Depends(get_session)) -> None:
    """Delete menu."""

    await services.menus_service.delete_menu(db=db, menu_id=menu_id, bgtask=bgtask)
