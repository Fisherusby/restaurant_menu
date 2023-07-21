from core.repositories.base import BaseRepository
from core import models


class DishesRepository(BaseRepository):
    pass


dishes = DishesRepository(models.DishDBModel)
