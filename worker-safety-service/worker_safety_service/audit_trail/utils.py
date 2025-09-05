from copy import deepcopy
from datetime import datetime
from typing import Any, Optional, TypeVar
from uuid import UUID

from httpx import AsyncClient, Limits
from sqlmodel import SQLModel

from worker_safety_service.audit_trail.models import EventType, ObjectType
from worker_safety_service.audit_trail.request_body import audit_log_body
from worker_safety_service.config import settings
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=SQLModel)

HTTPClient = AsyncClient(
    timeout=settings.HTTP_TIMEOUT,
    limits=Limits(
        max_connections=settings.HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
    ),
)


async def post_audit_log(data: dict, token: str) -> Any:
    response = await HTTPClient.post(
        url=f"{settings.AUDIT_TRAIL_URL}/logs/",
        json=data,
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


def extract_location_from_body(object_type: ObjectType, object_body: T) -> str:
    contents = object_body.contents if hasattr(object_body, "contents") else None
    result = ""
    if contents:
        if object_type.value == "jsb":
            location = contents.get("work_location")
            if location:
                address = location.get("address")
                if address:
                    result = result + address
                city = location.get("city")
                if city:
                    result = result + " " + city
                state = location.get("state")
                if state:
                    result = result + " " + state
        elif object_type.value == "ebo":
            details = contents.get("details")
            if details:
                result = details.get("work_location")
    return result


def get_log_creation_date(object_body: T, event_type: EventType) -> str:
    log_creation_date = datetime.utcnow()
    if hasattr(object_body, "created_at") and event_type == EventType.CREATE:
        log_creation_date = object_body.created_at
    elif hasattr(object_body, "updated_at") and event_type == EventType.REOPEN:
        log_creation_date = object_body.updated_at
    elif hasattr(object_body, "archived_at") and event_type == EventType.ARCHIVE:
        log_creation_date = object_body.archived_at
    elif hasattr(object_body, "updated_at") and event_type == EventType.COMPLETE:
        log_creation_date = object_body.updated_at

    return str(log_creation_date)


def capture_updates(object_type: ObjectType, old_object: T, new_object: T) -> None:
    pass


def generate_audit_request(
    object_type: ObjectType,
    event_type: EventType,
    object_body: T,
    object_id: UUID | None = None,
    old_object_body: Optional[T] = None,
) -> dict:
    request_body = deepcopy(audit_log_body)
    request_body["object_type"] = object_type.value
    if not object_id:
        if hasattr(object_body, "id"):
            request_body["object_id"] = str(object_body.id)
        else:
            logger.error("id not found")
    else:
        request_body["object_id"] = str(object_id)

    request_body["created_at"] = get_log_creation_date(object_body, event_type)

    request_body["event_type"] = event_type.value
    request_body["location"] = extract_location_from_body(object_type, object_body)
    request_body["source_app"] = "worker-safety-service"
    if (
        event_type == EventType.UPDATE
        or event_type == EventType.CREATE
        or event_type == EventType.COMPLETE
    ):
        if old_object_body is None:
            request_body["old_value"] = {}  # type:ignore
        else:
            request_body["old_value"] = old_object_body.contents  # type:ignore
        request_body["new_value"] = object_body.contents  # type:ignore

    return request_body


async def audit_object(
    object_type: ObjectType,
    object_body: T,
    token: str,
    event_type: EventType,
    object_id: UUID | None = None,
    old_object_body: Optional[T] = None,
) -> None:
    request_body = generate_audit_request(
        object_type, event_type, object_body, object_id, old_object_body
    )
    result = await post_audit_log(request_body, token)
    if not result:
        logger.error(
            f"error occurred  while saving audit logs for {object_type} - {request_body.get('object_id')}"
        )
