from core.repositories.base import BaseRepository
from core import models


class SubmenuRepository(BaseRepository):
    pass


submenus = SubmenuRepository(models.SubmenuDBModel)
