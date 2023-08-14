import asyncio
from functools import wraps

from celery import Celery

from core.services.admin_xls import XLSAdminService
from core.settings import settings

broker_url = (
    f'{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}'
    f'@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}'
)

celery = Celery(__name__)
celery.conf.broker_url = f'amqp://{broker_url}/'
celery.conf.result_backend = f'rpc://{broker_url}/'

celery.conf.broker_connection_retry_on_startup = True


celery.conf.beat_schedule = {
    'sync_DB_by_source': {
        'task': 'update_menu_from_file',
        'schedule': settings.ADMIN_DATA_UPDATE_PERIODIC,
        'args': (settings.ADMIN_DATA_SOURCE,)
    },
}


def async_as_sync(async_func):
    @wraps(async_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        coroutine = async_func(*args, **kwargs)
        return loop.run_until_complete(coroutine)

    return wrapper


@celery.task(name='ping')
def ping_task() -> str:
    return 'pong'


@celery.task(name='update_menu_from_file')
@async_as_sync
async def update_menu_from_file(source):
    xls_service = XLSAdminService(source=source)
    return await xls_service.run()
