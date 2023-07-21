from sqlalchemy.ext.asyncio import AsyncSession
from core.services.base import BaseObjectService
from core import schemas, services, models, repositories


class DishesService(BaseObjectService):
    pass


dishes_service = DishesService(repositories.dishes)
