from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from core.repositories.base import RepositoryType

SchemaType = TypeVar('SchemaType', bound=BaseModel)


class BaseCacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> SchemaType:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass


CacheServiceType = TypeVar('CacheServiceType', bound=BaseCacheService)


class BaseObjectService(Generic[RepositoryType]):
    def __init__(self, repository: RepositoryType):
        self.repository: RepositoryType = repository
