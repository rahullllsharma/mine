from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, TypeVar
from uuid import UUID

from httpx import AsyncClient, Limits
from pydantic import BaseModel

from ws_customizable_workflow.configs.config import Settings
from ws_customizable_workflow.models.base import BaseDocument
from ws_customizable_workflow.models.form_models import FormStatus
from ws_customizable_workflow.urbint_logging import get_logger

T = TypeVar("T", bound=BaseDocument)

settings = Settings.get_settings()

logger = get_logger(__name__)


class ObjectType(Enum):
    CWF = "cwf"


class EventType(Enum):
    CREATE = "create"
    UPDATE = "update"
    ARCHIVE = "archive"
    COMPLETE = "complete"
    REOPEN = "reopen"


class AuditLogRequest(BaseModel):
    created_at: datetime
    object_id: UUID
    object_type: ObjectType = ObjectType.CWF
    location: Optional[str]
    source_app: str = "ws-customizable-workflow"
    event_type: EventType
    new_value: Optional[dict[str, Any]] = None
    old_value: Optional[dict[str, Any]] = None


def _generate_request(
    event_type: EventType,
    object_body: T,
) -> AuditLogRequest:
    match event_type:
        case EventType.COMPLETE:
            _audit_datetime = object_body.completed_at
        case EventType.UPDATE | EventType.REOPEN:
            _audit_datetime = object_body.updated_at
        case EventType.CREATE:
            _audit_datetime = object_body.created_at
        case EventType.ARCHIVE:
            _audit_datetime = object_body.archived_at

    request_body = AuditLogRequest(
        created_at=_audit_datetime,
        object_id=object_body.id,
        location=None,
        event_type=event_type,
    )
    return request_body


async def _post_audit_log(data: AuditLogRequest, token: str) -> Any:
    """Makes an API call to ATS to create/register an audit log event"""
    async with AsyncClient(
        timeout=settings.HTTP_TIMEOUT,
        limits=Limits(
            max_connections=settings.HTTP_MAX_CONNECTIONS,
            max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
        ),
    ) as client:
        response = await client.post(
            url=f"{settings.AUDIT_TRAIL_URL}/logs/",
            json=data.model_dump(mode="json"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code != 201:
            logger.exception(
                f"Some error occurred while saving audit logs. - {response.status_code} - {response.json()}"
            )
        return response.json()


async def call_audit(
    cls: object,
    func: Callable[..., Awaitable[Optional[T]]],
    event_type: EventType,
    *args: Any,
    **kwargs: Any,
) -> Optional[T]:
    # Remove token as not needed by FormManager operations, only API call to ATS
    token = kwargs.pop("token")
    data: T | None = await func(cls, *args, **kwargs)
    if not token:
        logger.error("auth token not found for audit log")
        return data
    try:
        if data:
            if data.properties.status == FormStatus.COMPLETE:
                event_type = EventType.COMPLETE
            request_body = _generate_request(
                event_type=event_type,
                object_body=data,
            )
            result = await _post_audit_log(request_body, token)
            if not result:
                logger.error(
                    f"Error occurred while saving audit logs for form {data.id}"
                )
    except Exception as e:
        logger.error(e)
    return data


def audit_create(
    func: Callable[..., Awaitable[Optional[T]]],
) -> Callable[..., Awaitable[Optional[T]]]:
    @wraps(func)
    async def wrapper(cls: object, *args: Any, **kwargs: Any) -> Optional[T]:
        return await call_audit(cls, func, EventType.CREATE, *args, **kwargs)

    return wrapper


def audit_reopen(
    func: Callable[..., Awaitable[Optional[T]]],
) -> Callable[..., Awaitable[Optional[T]]]:
    @wraps(func)
    async def wrapper(cls: object, *args: Any, **kwargs: Any) -> Optional[T]:
        return await call_audit(cls, func, EventType.REOPEN, *args, **kwargs)

    return wrapper


def audit_update(
    func: Callable[..., Awaitable[Optional[T]]],
) -> Callable[..., Awaitable[Optional[T]]]:
    @wraps(func)
    async def wrapper(cls: object, *args: Any, **kwargs: Any) -> Optional[T]:
        return await call_audit(cls, func, EventType.UPDATE, *args, **kwargs)

    return wrapper


def audit_archive(
    func: Callable[..., Awaitable[Optional[T]]],
) -> Callable[..., Awaitable[Optional[T]]]:
    @wraps(func)
    async def wrapper(cls: object, *args: Any, **kwargs: Any) -> Optional[T]:
        return await call_audit(cls, func, EventType.ARCHIVE, *args, **kwargs)

    return wrapper
