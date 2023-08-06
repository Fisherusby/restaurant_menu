import pickle
from typing import Any

import aioredis

from core.services.base import BaseCacheService
from core.settings import settings


class RadisCacheService(BaseCacheService):
    def __init__(self, url: str, password: str, port: int):
        self.client: aioredis.client.Redis = aioredis.from_url(url, password=password, port=port)

    async def get(self, key: str) -> Any:
        """Get value from redis by key"""
        dict_bytes: bytes | None = await self.client.get(key)
        if dict_bytes is None:
            return None
        return pickle.loads(dict_bytes)

    async def set(self, key: str, value: Any) -> None:
        """Set value to redis by key"""
        if value is None:
            return
        await self.client.set(key, pickle.dumps(value), ex=settings.CACHE_LIFETIME)

    async def delete(self, key: str) -> None:
        """Delete value from redis by key"""
        await self.client.delete(key)

    async def find_keys(self, pattern: str) -> list[str]:
        """Return all found keys in redis by pattern"""
        return await self.client.keys(pattern)

    async def del_by_pattens(self, *patterns: str) -> None:
        """Delete all values from redis by patterns of keys"""
        keys: set = set()
        for pattern in patterns:
            keys.update(
                await self.find_keys(pattern)
            )
        for key in keys:
            await self.delete(key)


redis_service = RadisCacheService(
    url=f'redis://{settings.REDIS_CACHE_HOST}', password=settings.REDIS_CACHE_PASSWORD, port=settings.REDIS_CACHE_PORT
)
