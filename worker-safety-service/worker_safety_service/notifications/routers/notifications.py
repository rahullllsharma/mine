import functools
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.notifications import NotificationsManager
from worker_safety_service.graphql.permissions import CanViewNotifications
from worker_safety_service.keycloak import IsAuthorized, get_user
from worker_safety_service.keycloak.exceptions import AuthorizationException
from worker_safety_service.models import FormType, NotificationType
from worker_safety_service.models.user import User
from worker_safety_service.notifications.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.notifications.dependency_injection.managers import (
    get_notifications_manager,
)
from worker_safety_service.notifications.exception_handlers import ErrorResponse
from worker_safety_service.notifications.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.notifications.routers.utils.pagination import (
    create_pagination_links,
)
from worker_safety_service.urbint_logging import get_logger

resource_name = "notifications"
resource_uri = "list-notifications"

router = APIRouter(
    tags=[resource_name],
    dependencies=[Depends(IsAuthorized(CanViewNotifications))],
)
logger = get_logger(__name__)


class NotificationsAttributes(BaseModel):
    __entity_name__ = "notifications"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, resource_uri)

    id: UUID = Field(description="Notification ID")
    contents: str = Field(description="Notification content")
    form_type: FormType = Field(description="Form type")
    notification_type: NotificationType = Field(description="Type of notification")
    is_read: bool = Field(description="Read status of notification")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last updated timestamp")


(
    _,
    _,
    NotificationsResponse,
    NotificationsBulkResponse,
    NotificationsPaginationResponse,
) = create_models(NotificationsAttributes)


class NotificationsInputAttributes(BaseModel):
    __entity_name__ = "input_notifications"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, resource_uri)
    form_type: FormType = Field(description="Form type")
    contents: str = Field(description="Notification Content")
    sender_id: UUID = Field(description="Sender ID")
    receiver_id: UUID = Field(description="List of receiver IDs")
    notification_type: NotificationType = Field(description="Type of notification")


(
    NotificationsInputRequest,
    NotificationsInputBulkRequest,
    _,
    _,
    _,
) = create_models(NotificationsInputAttributes)


class NotificationReadInputAttributes(BaseModel):
    __entity_name__ = "notification_read_input"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, resource_uri)
    is_read: bool = Field(description="Read status of notification")


(
    NotificationReadInputRequest,
    _,
    _,
    _,
    _,
) = create_models(NotificationReadInputAttributes)


@router.get(
    "/list-notifications",
    response_model=NotificationsPaginationResponse,
    status_code=200,
)
async def list_notifications(
    request: Request,
    manager: NotificationsManager = Depends(get_notifications_manager),
    user: User = Depends(get_user),
    start_date: Optional[datetime] = Query(
        default=None,
    ),
    end_date: Optional[datetime] = Query(
        default=None,
    ),
    is_read: Optional[bool] = Query(
        default=None,
    ),
    offset: int = Query(
        default=0,
        ge=1,
        alias="page[offset]",
    ),
    limit: int = Query(
        default=50,
        le=200,
        ge=1,
        alias="page[limit]",
    ),
) -> NotificationsPaginationResponse | ErrorResponse:  # type: ignore
    """
    Get a paginated list of Notifications.
    """
    try:
        notifications, total = await manager.get_all(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            is_read=is_read,
            offset=offset,
            limit=limit,
        )
        elements = [
            (notification.id, NotificationsAttributes(**notification.dict()))
            for notification in notifications
        ]
        return NotificationsPaginationResponse.pack_many(  # type: ignore
            elements,
            paginated_links=create_pagination_links(
                limit=limit, url=request.url, elements=elements
            ),
            pagination_meta=PaginationMetaData(limit=limit, total=total),
        )
    except Exception as e:
        logger.exception("Error getting notifications")
        raise HTTPException(500, str(e))


@router.get(
    "/list-notifications/{id}",
    response_model=NotificationsResponse,
    status_code=200,
)
async def get_notification_by_id(
    id: uuid.UUID,
    manager: NotificationsManager = Depends(get_notifications_manager),
    user: User = Depends(get_user),
) -> NotificationsResponse | ErrorResponse:  # type: ignore
    """
    Get notification by id
    """
    try:
        notification = await manager.get_by_id(id=id)
        if not notification:
            raise EntityNotFoundException(
                entity_id=id, entity_type=NotificationsAttributes
            )
        if notification.receiver_id != user.id:
            raise AuthorizationException()
        return NotificationsResponse.pack(  # type: ignore
            notification.id,
            NotificationsAttributes(**notification.dict()),
        )
    except (EntityNotFoundException, AuthorizationException):
        raise
    except Exception as e:
        logger.exception("Error getting device detail by id")
        raise HTTPException(500, str(e))


@router.patch(
    "/list-notifications/{id}/read",
    response_model=NotificationsResponse,
    status_code=200,
)
async def update_notification_is_read(
    id: uuid.UUID,
    request: NotificationReadInputRequest,  # type: ignore
    manager: NotificationsManager = Depends(get_notifications_manager),
    user: User = Depends(get_user),
) -> NotificationsResponse | ErrorResponse:  # type: ignore
    """
    Updated notification is_read status
    """
    try:
        notification = await manager.get_by_id(id=id)
        if not notification:
            raise EntityNotFoundException(
                entity_id=id, entity_type=NotificationsAttributes
            )
        if notification.receiver_id != user.id:
            raise AuthorizationException()
        data = request.unpack()  # type: ignore
        notification.is_read = data.is_read
        notification = await manager.add_and_commit(notification)
        return NotificationsResponse.pack(  # type: ignore
            notification.id,
            NotificationsAttributes(**notification.dict()),
        )
    except (EntityNotFoundException, AuthorizationException):
        raise
    except Exception as e:
        logger.exception("Error updating the is_read status")
        raise HTTPException(500, str(e))
