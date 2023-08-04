from typing import Generic

from core.repositories.base import RepositoryType


class BaseObjectService(Generic[RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository: RepositoryType = repository
