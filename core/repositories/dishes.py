from core import models, schemas
from core.repositories.base import BaseRepository


class DishesRepository(BaseRepository[models.DishDBModel, schemas.DishWithSubmenuIdSchema, schemas.UpdateDishSchema]):
    pass


dishes: DishesRepository = DishesRepository(models.DishDBModel)
