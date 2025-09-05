import functools
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.device_details import DeviceDetailsManager
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.permissions import CanViewNotifications
from worker_safety_service.keycloak import IsAuthorized, get_user
from worker_safety_service.models import CreateDeviceDetailsInput, DeviceType
from worker_safety_service.models.user import User
from worker_safety_service.notifications.api_models.new_jsonapi import create_models
from worker_safety_service.notifications.dependency_injection.managers import (
    get_device_details_manager,
)
from worker_safety_service.notifications.exception_handlers import ErrorResponse
from worker_safety_service.notifications.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.notifications.routers.utils.pagination import (
    create_pagination_links,
)
from worker_safety_service.urbint_logging import get_logger

resource_name = "device-details"
resource_uri = f"{resource_name}"

router = APIRouter(
    prefix=f"/{resource_uri}",
    tags=[resource_name],
    dependencies=[Depends(IsAuthorized(CanViewNotifications))],
)


logger = get_logger(__name__)


class DeviceDetailsAttributes(BaseModel):
    __entity_name__ = "device_details"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, resource_uri)

    user_id: UUID = Field(description="Id of the user")
    device_type: Optional[DeviceType] = Field(
        description=" Type of the device", default=None
    )
    device_id: str = Field(description="Unique Id of the device")
    device_os: str = Field(description="Operating System of the device")
    device_make: str = Field(description="Device Manufacturer")
    device_model: str = Field(description="Device Model Name")
    app_name: str = Field(description="Name of the Application DP/WS")
    app_version: str = Field(description="Application Version")
    fcm_push_notif_token: str = Field(description="Notification Token")
    created_at: datetime = Field(description="Created at Timestamp")
    updated_at: datetime = Field(description="Created at Timestamp")


(
    _,
    _,
    DeviceDetailsResponse,
    _,
    DeviceDetailsPaginationResponse,
) = create_models(DeviceDetailsAttributes)


class DeviceDetailsInputAttributes(BaseModel):
    __entity_name__ = "input_device_details"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, resource_uri)

    device_type: Optional[DeviceType] = Field(
        description=" Type of the device", default=None
    )
    device_id: str = Field(description="Unique Id of the device")
    device_os: str = Field(description="Operating System of the device")
    device_make: str = Field(description="Device Manufacturer")
    device_model: str = Field(description="Device Model Name")
    app_name: str = Field(description="Name of the Application DP/WS")
    app_version: str = Field(description="Application Version")
    fcm_push_notif_token: str = Field(description="Notification Token")


(
    DeviceDetailsInputRequest,
    _,
    _,
    _,
    _,
) = create_models(DeviceDetailsInputAttributes)


@router.put(
    "",
    response_model=DeviceDetailsResponse,
    responses={
        200: {
            "description": "Device updated successfully.",
            "model": DeviceDetailsResponse,
        },
        201: {
            "description": "Device created successfully.",
            "model": DeviceDetailsResponse,
        },
    },
)
async def update_device_detail(
    response: Response,
    device_detail_request: DeviceDetailsInputRequest,  # type: ignore
    device_detail_manager: DeviceDetailsManager = Depends(get_device_details_manager),
    user: User = Depends(get_user),
) -> DeviceDetailsResponse | ErrorResponse:  # type: ignore
    """
    Create or updated a new device detail
    """
    try:
        data = device_detail_request.unpack()  # type: ignore
        create_input = CreateDeviceDetailsInput(user_id=user.id, **data.dict())
        (
            created_device_detail,
            is_created,
        ) = await device_detail_manager.create_or_update_device_detail(
            input=create_input
        )
        device_detail = DeviceDetailsAttributes(**created_device_detail.dict())
        response.status_code = (
            status.HTTP_201_CREATED if is_created else status.HTTP_200_OK
        )
        return DeviceDetailsResponse.pack(id=created_device_detail.id, attributes=device_detail)  # type: ignore
    except ValidationError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.exception(
            f"error creating device detail with attributes {device_detail_request.data.attributes}"  # type: ignore
        )
        raise HTTPException(500, str(e))


@router.get("", response_model=DeviceDetailsPaginationResponse, status_code=200)
async def get_device_details(
    request: Request,
    manager: DeviceDetailsManager = Depends(get_device_details_manager),
    user: User = Depends(get_user),
    device_id: str = Query(
        default=None,
        description="Filter results to those related to this device id",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        alias="page[offset]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
) -> DeviceDetailsPaginationResponse | ErrorResponse:  # type: ignore
    """
    Get a paginated list of device details.
    """
    try:
        elements = [
            (
                device_detail.id,
                DeviceDetailsAttributes(**device_detail.dict()),
            )
            for device_detail in (
                await manager.get_all_device_details(
                    user_id=user.id,
                    device_id=device_id,
                    offset=offset,
                    limit=limit,
                )
            )
        ]
        return DeviceDetailsPaginationResponse.pack_many(  # type: ignore
            elements,
            paginated_links=create_pagination_links(
                limit=limit, url=request.url, elements=elements
            ),
            pagination_meta=None,
        )
    except Exception as e:
        logger.exception("Error getting device details")
        raise HTTPException(500, str(e))


@router.get(
    "/{id}",
    response_model=DeviceDetailsResponse,
    status_code=200,
)
async def get_device_detail_by_id(
    id: uuid.UUID,
    manager: DeviceDetailsManager = Depends(get_device_details_manager),
    user: User = Depends(get_user),
) -> DeviceDetailsResponse | ErrorResponse:  # type: ignore
    """
    Get device detail by id
    """
    try:
        device_detail = await manager.get_device_detail_by_id(user_id=user.id, id=id)
        if not device_detail:
            raise EntityNotFoundException(
                entity_id=id, entity_type=DeviceDetailsAttributes
            )
        return DeviceDetailsResponse.pack(  # type: ignore
            device_detail.id,
            DeviceDetailsAttributes(**device_detail.dict()),
        )
    except EntityNotFoundException:
        raise
    except Exception as e:
        logger.exception("Error getting device detail by id")
        raise HTTPException(500, str(e))


@router.delete(
    "/{id}",
    response_model=None,
    status_code=204,
)
async def delete_device_details(
    id: uuid.UUID,
    manager: DeviceDetailsManager = Depends(get_device_details_manager),
    user: User = Depends(get_user),
) -> bool | ErrorResponse:
    try:
        device_detail = await manager.get_device_detail_by_id(user_id=user.id, id=id)
        if not device_detail:
            raise EntityNotFoundException(
                entity_id=id, entity_type=DeviceDetailsAttributes
            )
        return await manager.archive_device_detail(device_detail)
    except ResourceReferenceException:
        raise EntityNotFoundException(entity_id=id, entity_type=DeviceDetailsAttributes)
    except EntityNotFoundException:
        raise
    except Exception as e:
        logger.exception("Device detail couldn't be archived")
        raise HTTPException(500, str(e))
