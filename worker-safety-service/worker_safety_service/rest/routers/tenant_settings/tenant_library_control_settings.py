import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import (
    CreateTenantLibraryControlSettingInput,
    TenantLibraryControlSettings,
    UpdateTenantLibraryControlSettingInput,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_tenant_library_control_settings_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(prefix="/settings", dependencies=[Depends(authenticate_integration)])


logger = get_logger(__name__)


class TenantLibraryControlSettingsAttributes(BaseModel):
    __entity_name__ = "tenant-library-control-settings"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "tenant-library-control-settings"
    )

    alias: Optional[str] = Field(
        description="The custom name for the library control", default=None
    )


(
    TenantLibraryControlSettingsRequest,
    _,
    TenantLibraryControlSettingsResponse,
    _,
    TenantLibraryControlSettingsPaginationResponse,
) = create_models(TenantLibraryControlSettingsAttributes)


@router.post(
    "/{tenant_id}/library-controls/{library_control_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["library-controls", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def set_tenant_library_control_settings(
    tenant_id: uuid.UUID,
    library_control_id: uuid.UUID,
    tenant_library_control_settings: TenantLibraryControlSettingsRequest,  # type: ignore
    manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    try:
        data = tenant_library_control_settings.unpack()  # type: ignore
        logger.info(f"input data for creation -- {data}")
        create_input = CreateTenantLibraryControlSettingInput(
            tenant_id=tenant_id, library_control_id=library_control_id, **data.dict()
        )
        await manager.create_setting(input=create_input)
        return EmptyResponse()
    except Exception:
        logger.exception(
            f"error setting tenant library control settings for tenant: {tenant_id} library control: {library_control_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-controls/{library_control_id}",
    response_model=TenantLibraryControlSettingsResponse,
    status_code=200,
    tags=["library-controls", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_control_setting(
    tenant_id: uuid.UUID,
    library_control_id: uuid.UUID,
    manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> TenantLibraryControlSettingsResponse | ErrorResponse:  # type: ignore
    try:
        tlts = await manager.get(
            tenant_id=tenant_id, primary_key_value=library_control_id
        )
        if tlts is None:
            return ErrorResponse(
                status_code=404,
                title="Not Found",
                detail="Settings not found for the specified tenant and library control",
            )
        tlts_attributes = TenantLibraryControlSettingsAttributes(alias=tlts.alias)
        return TenantLibraryControlSettingsResponse.pack(uuid.uuid4(), tlts_attributes)  # type: ignore
    except Exception:
        logger.exception(
            f"error getting tenant library control settings for tenant: {tenant_id} library control: {library_control_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-controls",
    response_model=TenantLibraryControlSettingsPaginationResponse,
    status_code=200,
    tags=["library-controls", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_control_settings(
    request: Request,
    tenant_id: uuid.UUID,
    manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
    limit: int = query_params.limit,
) -> TenantLibraryControlSettingsPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_tenant_library_control_settings = await manager.get_all(
            additional_where_clause=[
                TenantLibraryControlSettings.tenant_id == tenant_id
            ],
            limit=limit,
            order_by_attribute="library_control_id",
        )
        tenant_library_control_settings = [
            (
                uuid.uuid4(),
                TenantLibraryControlSettingsAttributes(
                    **tenant_library_control_setting.dict()
                ),
            )
            for tenant_library_control_setting in db_tenant_library_control_settings
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=None,
            limit=limit,
            url=request.url,
            elements=tenant_library_control_settings,
        )
        return TenantLibraryControlSettingsPaginationResponse.pack_many(elements=tenant_library_control_settings, paginated_links=links, pagination_meta=meta)  # type: ignore
    except Exception:
        logger.exception(
            f"Error getting tenant_library_control_settings for {tenant_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{tenant_id}/library-controls/{library_control_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-controls", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_tenant_library_control_settings(
    tenant_id: uuid.UUID,
    library_control_id: uuid.UUID,
    tenant_library_control_settings: TenantLibraryControlSettingsRequest,  # type: ignore
    manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        data = tenant_library_control_settings.unpack()  # type: ignore
        logger.info(f"input data for creation -- {data}")
        update_input = UpdateTenantLibraryControlSettingInput(**data.dict())
        await manager.update_setting(
            tenant_id=tenant_id,
            primary_key_value=library_control_id,
            input=update_input,
        )
        return EmptyResponse()
    except Exception:
        logger.exception(
            f"error updating tenant library control settings for tenant: {tenant_id} library control: {library_control_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{tenant_id}/library-controls/{library_control_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-controls", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_tenant_library_control_settings(
    tenant_id: uuid.UUID,
    library_control_id: uuid.UUID,
    manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        await manager.delete_setting(
            tenant_id=tenant_id, primary_key_value=library_control_id
        )
        return EmptyResponse()
    except Exception:
        logger.exception(
            f"error deleting tenant library control settings for tenant: {tenant_id} library control: {library_control_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
