from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from redis import BusyLoadingError, ConnectionError, TimeoutError
from redis.asyncio import BlockingConnectionPool, Redis, SSLConnection
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from worker_safety_service.config import settings

REDIS: Redis | None = None


def create_redis_client() -> Redis:
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

    return Redis(
        connection_pool=BlockingConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            retry=retry,
            retry_on_error=retry_on_error,
            socket_keepalive=True,
            **kwargs,
        ),
    )


@asynccontextmanager
async def with_redis_client() -> AsyncGenerator[Redis, None]:
    redis = create_redis_client()
    try:
        yield redis
    finally:
        await redis.close()


def get_redis_client() -> Redis:
    global REDIS
    if not REDIS:
        REDIS = create_redis_client()
    return REDIS


async def shutdown_redis() -> None:
    if REDIS:
        await REDIS.close()
