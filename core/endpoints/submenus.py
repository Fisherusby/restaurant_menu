from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session

router = APIRouter()


@router.get('/{menu_id}/submenus', status_code=200, response_model=List[schemas.ResponseSubmenuSchema])
async def get_submenu_list(
    menu_id: UUID, db: AsyncSession = Depends(get_session)
) -> List[schemas.ResponseSubmenuSchema]:
    """Get menu's submenu."""

    submenu_list: List[schemas.ResponseSubmenuSchema] = await services.submenus_service.get_submenu_list(
        db=db, menu_id=menu_id
    )
    return submenu_list


@router.post('/{menu_id}/submenus', status_code=201, response_model=schemas.ResponseSubmenuSchema)
async def create_submenus(
    menu_id: UUID, data: schemas.SubmenuSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseSubmenuSchema:
    """Create submenu for menu."""

    submenu: schemas.ResponseSubmenuSchema = await services.submenus_service.create_submenu(
        db=db, menu_id=menu_id, data=data
    )
    return submenu


@router.get('/{menu_id}/submenus/{submenu_id}', status_code=200, response_model=schemas.ResponseSubmenuWithCountSchema)
async def detail_submenu(
    menu_id: UUID, submenu_id: UUID, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseSubmenuWithCountSchema:
    """Get submenu's detail."""

    submenu: schemas.ResponseSubmenuWithCountSchema = await services.submenus_service.get_submenu(
        db=db, menu_id=menu_id, submenu_id=submenu_id
    )
    return submenu


@router.patch('/{menu_id}/submenus/{submenu_id}', status_code=200, response_model=schemas.ResponseSubmenuSchema)
async def update_submenu(
    menu_id: UUID, submenu_id: UUID, data: schemas.UpdateSubmenuSchema, db: AsyncSession = Depends(get_session)
) -> schemas.ResponseSubmenuSchema:
    """Update submenu's properties:

    title and description.
    """

    submenu: schemas.ResponseSubmenuSchema = await services.submenus_service.update_submenu(
        db=db, menu_id=menu_id, submenu_id=submenu_id, data=data
    )
    return submenu


@router.delete('/{menu_id}/submenus/{submenu_id}', status_code=200)
async def delete_submenu(menu_id: UUID, submenu_id: UUID, db: AsyncSession = Depends(get_session)) -> None:
    """Delete submenu."""

    await services.submenus_service.delete_submenu(db=db, menu_id=menu_id, submenu_id=submenu_id)
