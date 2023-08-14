from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import schemas, services
from core.db import get_session
from workers.celery import update_menu_from_file

router = APIRouter()


@router.post(
    '/task_sync_with',
    status_code=200,
    response_model=dict[str, str],
    name='task_sync_with',
)
async def run_task_sync_with(data: schemas.CeleryTaskRunnerRequest) -> dict[str, str]:
    """Runner for celery task for sync DB with source.

    Source is a path for the local xlsx file or an url for the Google Sheets.
    """

    task = update_menu_from_file.delay(data.source)

    return {'task_id': str(task.id)}


@router.get(
    '/tasks/{task_id}',
    status_code=200,
    response_model=dict[str, str],
    name='task_status',
)
async def task_status(task_id: UUID) -> dict[str, str]:
    """Response task status and result by task ID."""

    task = AsyncResult(str(task_id))
    return {
        'state': str(task.state),
        'status': str(task.status),
        'result': str(task.result),
    }


@router.get(
    '/all_in_one',
    status_code=200,
    response_model=list[schemas.ResponseMenuWitSubmenusSchema],
    name='get_all_in_one',
)
async def get_all_in_one(db: AsyncSession = Depends(get_session)) -> list[schemas.ResponseMenuWitSubmenusSchema]:
    """Get all menus with menus' submenus with submenus' dishes."""

    return await services.menus_service.get_all_in_one(db=db)
