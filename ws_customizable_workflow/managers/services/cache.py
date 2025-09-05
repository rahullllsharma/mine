from contextlib import AbstractAsyncContextManager
from datetime import timedelta
from typing import Any, Optional, Protocol

from redis import BusyLoadingError, ConnectionError, TimeoutError
from redis.asyncio import BlockingConnectionPool, Redis, SSLConnection
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from ws_customizable_workflow.configs.config import Settings

settings = Settings.get_settings()


class RedisClient(AbstractAsyncContextManager):
    """
    Actual Redis client implementation that can be used as a context manager.
    """

    def __init__(self) -> None:
        self._redis: Optional[Redis] = None

    async def __aenter__(self) -> Redis:
        """Create and return a Redis client upon entering the runtime context."""
        self._redis = self.create_redis_client()
        return self._redis

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        """Close the Redis connection when exiting the runtime context."""
        if self._redis:
            await self._redis.close()
        return None

    @classmethod
    def create_redis_client(cls) -> Redis:
        kwargs: dict[str, Any] = {}
        if settings.REDIS_SSL:
            kwargs.update(
                connection_class=SSLConnection,
                ssl_keyfile=settings.REDIS_KEYFILE,
                ssl_certfile=settings.REDIS_CERTFILE,
                ssl_ca_certs=settings.REDIS_CA_CERTS,
            )

        if settings.REDIS_MAX_RETRIES > 0:
            retry = Retry(
                ExponentialBackoff(base=settings.REDIS_BACKOFF_BASE),
                settings.REDIS_MAX_RETRIES,
            )
            retry_on_error = [BusyLoadingError, ConnectionError, TimeoutError]
        else:
            retry = None
            retry_on_error = None

        # Create connection pool with proper typing
        connection_pool = BlockingConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry=retry,
            retry_on_error=retry_on_error,
            socket_keepalive=True,
            **kwargs,
        )

        return Redis(connection_pool=connection_pool)  # type: ignore


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
        async with RedisClient() as redis:
            return await redis.get(key)

    async def set(
        self, key: str, value: Any, expiration: Optional[int | timedelta]
    ) -> None:
        async with RedisClient() as redis:
            if expiration:
                await redis.setex(key, expiration, value)
            else:
                await redis.set(key, value)

    async def delete(self, key: str) -> None:
        async with RedisClient() as redis:
            await redis.delete(key)

    async def setex(self, key: str, value: Any, ex: int | timedelta) -> None:
        async with RedisClient() as redis:
            await redis.setex(key, ex, value)


def get_cache() -> Cache:
    return RedisCache()
