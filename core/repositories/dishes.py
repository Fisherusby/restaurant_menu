from core import models
from core.repositories.base import BaseRepository


class DishesRepository(BaseRepository):
    pass


dishes = DishesRepository(models.DishDBModel)
