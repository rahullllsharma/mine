import functools
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from worker_safety_service.dal.exceptions import EntityNotFoundException
from worker_safety_service.dal.user import UserManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.permissions import CanConfigureTheApplication
from worker_safety_service.keycloak import IsAuthorized
from worker_safety_service.rest.api_models.new_jsonapi import (
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import get_user_manager
from worker_safety_service.rest.exception_handlers import (
    EntityNotFoundResponse,
    ErrorResponse,
)
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.urbint_logging import get_logger

can_configure_the_application = IsAuthorized(CanConfigureTheApplication)
router = APIRouter(
    prefix="/users", dependencies=[Depends(can_configure_the_application)]
)


logger = get_logger(__name__)


class UsersAttributes(BaseModel):
    __entity_name__ = "user"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "users")

    tenant_id: Optional[UUID] = Field(
        relationship=RelationshipFieldAttributes(
            type="tenant",
            url_supplier=functools.partial(entity_array_url_supplier, "tenant", "user"),
        ),
        description="Tenant ID",
    )

    keycloak_id: Optional[UUID] = Field(index=True)
    archived_at: Optional[datetime] = Field(description="Archived at", default=None)
    external_id: Optional[str] = Field(description="users external id")


(
    UserRequest,
    UserBulkRequest,
    UserResponse,
    UserBulkResponse,
    UserPaginationResponse,
) = create_models(UsersAttributes)


@router.put(
    "/{user_id}",
    response_model=None,
    status_code=200,
    tags=["users"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_user(
    user_id: UUID,
    external_id: str,
    user_manager: UserManager = Depends(get_user_manager),
) -> bool | ErrorResponse:
    try:
        return await user_manager.update_external_id(
            user_id=user_id, external_id=external_id
        )
    except ResourceReferenceException as e:
        return ErrorResponse(400, "User not found", str(e))
    except Exception:
        logger.exception(f"Error updating user for {user_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=200,
    tags=["users"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_user(
    user_id: uuid.UUID,
    user_manager: UserManager = Depends(get_user_manager),
) -> bool | ErrorResponse:
    try:
        return await user_manager.archive_user(user_id)
    except EntityNotFoundException:
        return EntityNotFoundResponse(UsersAttributes.__entity_name__, user_id)
    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")
