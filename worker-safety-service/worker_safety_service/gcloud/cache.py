from datetime import timedelta
from typing import Any, Optional, Protocol

from worker_safety_service.config import settings
from worker_safety_service.gcloud import FileStorage
from worker_safety_service.redis_client import with_redis_client


class Cache(Protocol):
    async def get(self, key: Any) -> Any | None:
        ...

    async def set(
        self, key: Any, value: Any, expiration: Optional[int | timedelta]
    ) -> None:
        ...

    async def delete(self, key: Any) -> None:
        ...


class RedisCache:
    async def get(self, key: str) -> Any:
        async with with_redis_client() as redis:
            return await redis.get(key)

    async def set(
        self, key: str, value: Any, expiration: Optional[int | timedelta]
    ) -> None:
        async with with_redis_client() as redis:
            if expiration:
                await redis.setex(key, expiration, value)
            else:
                await redis.set(key, value)

    async def delete(self, key: str) -> None:
        async with with_redis_client() as redis:
            await redis.delete(key)

    async def setex(self, key: str, value: Any, ex: int | timedelta) -> None:
        async with with_redis_client() as redis:
            await redis.setex(key, ex, value)


def get_cache_impl() -> Cache:
    return RedisCache()


class CachedFileStorage:
    def __init__(self, file_storage: FileStorage, cache: Cache):
        self.file_storage = file_storage
        self.cache = cache

    async def get_cached_signed_url(
        self,
        blob_id: str,
        expiration: timedelta = settings.GS_URL_EXPIRATION,
    ) -> str:
        _key = f"__CachedFileStorage__{blob_id}"
        _value = await self.cache.get(_key)
        if isinstance(_value, bytes):
            _value = _value.decode("UTF-8", "replace")
        if not _value:
            try:
                _value = self.file_storage._url(blob_id, expiration)
                # To be safe, the cached url expires 5 sec before the signed_url
                # This is to counter any lag in the call above and cache set op below
                await self.cache.set(_key, _value, expiration - timedelta(seconds=5))
            except Exception:
                await self.cache.delete(_key)
                raise
        return _value
