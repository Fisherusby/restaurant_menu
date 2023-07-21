from typing import TypeVar

from core.repositories.base import BaseRepository

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseObjectService:
    def __init__(self, repository: RepositoryType):
        self.repository: RepositoryType = repository
