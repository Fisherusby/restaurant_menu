from fastapi import APIRouter

from core.endpoints.all_in_one import router as all_in_one_router
from core.endpoints.dishes import router as dishes_router
from core.endpoints.menus import router as menus_router
from core.endpoints.submenus import router as submenus_router

router: APIRouter = APIRouter()

router.include_router(dishes_router, prefix='/menus', tags=['dishes'])
router.include_router(menus_router, prefix='/menus', tags=['menus'])
router.include_router(submenus_router, prefix='/menus', tags=['submenus'])
router.include_router(all_in_one_router, prefix='/celery', tags=['celery'])

tags_metadata = [
    {
        'name': 'celery',
        'description': 'Operations for testing celery tasks.',
    },
    {
        'name': 'dishes',
        'description': 'Operations with **dishes** of submenu.',
    },
    {
        'name': 'menus',
        'description': 'Operations with **menus**.',
    },
    {
        'name': 'submenus',
        'description': 'Operations with **submenus** of menu.',
    },
]
