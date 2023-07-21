from core.repositories.base import BaseRepository
from core import models


class MenuRepository(BaseRepository):
    pass


menus = MenuRepository(models.MenuDBModel)
