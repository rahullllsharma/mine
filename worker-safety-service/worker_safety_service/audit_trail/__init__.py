import functools
from typing import Any, Awaitable, Callable, TypeVar

from sqlmodel import SQLModel

from worker_safety_service.audit_trail.models import EventType, ObjectType
from worker_safety_service.audit_trail.utils import audit_object
from worker_safety_service.models import FormStatus
from worker_safety_service.urbint_logging import get_logger

T = TypeVar("T", bound=SQLModel)

logger = get_logger(__name__)


async def call_audit(
    self: object,
    func: Callable[..., Awaitable[T]],
    event_type: EventType,
    *args: Any,
    **kwargs: Any
) -> T:
    data: T = await func(self, *args, **kwargs)
    token = kwargs.get("token")
    old_entity_data = kwargs.get("old_entity", None)
    if data.status == FormStatus.COMPLETE:  # type: ignore
        event_type = EventType.COMPLETE
    if not token:
        logger.error("auth token not found for audit log")
        return data
    try:
        if data:
            object_type = ObjectType[data.__class__.__name__]
            await audit_object(
                object_type=object_type,
                object_body=data,
                token=token,
                event_type=event_type,
                old_object_body=old_entity_data,
            )
    except Exception as e:
        logger.error(e)
    return data


def audit_create(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> T:
        return await call_audit(self, func, EventType.CREATE, *args, **kwargs)

    return wrapper


def audit_complete(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> T:
        return await call_audit(self, func, EventType.COMPLETE, *args, **kwargs)

    return wrapper


def audit_reopen(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> T:
        return await call_audit(self, func, EventType.REOPEN, *args, **kwargs)

    return wrapper


def audit_update(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> T:
        return await call_audit(self, func, EventType.UPDATE, *args, **kwargs)

    return wrapper


def audit_archive(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
    @functools.wraps(func)
    async def wrapper(self: object, *args: Any, **kwargs: Any) -> T:
        return await call_audit(self, func, EventType.ARCHIVE, *args, **kwargs)

    return wrapper
