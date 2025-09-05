import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.dal.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import (
    CreateTenantLibrarySiteConditionSettingInput,
    TenantLibrarySiteConditionSettings,
    UpdateTenantLibrarySiteConditionSettingInput,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_tenant_library_site_condition_settings_manager,
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


class TenantLibrarySiteConditionSettingsAttributes(BaseModel):
    __entity_name__ = "tenant-library-site-condition-settings"

    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "tenant-library-site-condition-settings"
    )

    alias: Optional[str] = Field(
        description="The custom name for the library site_condition", default=None
    )


(
    TenantLibrarySiteConditionSettingsRequest,
    _,
    TenantLibrarySiteConditionSettingsResponse,
    _,
    TenantLibrarySiteConditionSettingsPaginationResponse,
) = create_models(TenantLibrarySiteConditionSettingsAttributes)


@router.post(
    "/{tenant_id}/library-site-conditions/{library_site_condition_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["library-site-conditions", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def set_tenant_library_site_condition_settings(
    tenant_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    tenant_library_site_condition_settings: TenantLibrarySiteConditionSettingsRequest,  # type: ignore
    manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    try:
        data = tenant_library_site_condition_settings.unpack()  # type: ignore

        logger.info(f"input data for creation -- {data}")

        create_input = CreateTenantLibrarySiteConditionSettingInput(
            tenant_id=tenant_id,
            library_site_condition_id=library_site_condition_id,
            **data.dict(),
        )

        await manager.create_setting(input=create_input)

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error setting tenant library site_condition settings for tenant: {tenant_id} library site_condition: {library_site_condition_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-site-conditions/{library_site_condition_id}",
    response_model=TenantLibrarySiteConditionSettingsResponse,
    status_code=200,
    tags=["library-site-conditions", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_site_condition_setting(
    tenant_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> TenantLibrarySiteConditionSettingsResponse | ErrorResponse:  # type: ignore
    try:
        tlts = await manager.get(
            tenant_id=tenant_id, primary_key_value=library_site_condition_id
        )

        if tlts is None:
            return ErrorResponse(
                status_code=404,
                title="Not Found",
                detail="Settings not found for the specified tenant and library site_condition",
            )

        tlts_attributes = TenantLibrarySiteConditionSettingsAttributes(alias=tlts.alias)

        return TenantLibrarySiteConditionSettingsResponse.pack(uuid.uuid4(), tlts_attributes)  # type: ignore

    except Exception:
        logger.exception(
            f"error getting tenant library site_condition settings for tenant: {tenant_id} library site_condition: {library_site_condition_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-site-conditions",
    response_model=TenantLibrarySiteConditionSettingsPaginationResponse,
    status_code=200,
    tags=["library-site-conditions", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_site_condition_settings(
    request: Request,
    tenant_id: uuid.UUID,
    manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
    limit: int = query_params.limit,
) -> TenantLibrarySiteConditionSettingsPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_tenant_library_site_condition_settings = await manager.get_all(
            additional_where_clause=[
                TenantLibrarySiteConditionSettings.tenant_id == tenant_id
            ],
            limit=limit,
            order_by_attribute="library_site_condition_id",
        )
        tenant_library_site_condition_settings = [
            (
                uuid.uuid4(),
                TenantLibrarySiteConditionSettingsAttributes(
                    **tenant_library_site_condition_setting.dict()
                ),
            )
            for tenant_library_site_condition_setting in db_tenant_library_site_condition_settings
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=None,
            limit=limit,
            url=request.url,
            elements=tenant_library_site_condition_settings,
        )
        return TenantLibrarySiteConditionSettingsPaginationResponse.pack_many(elements=tenant_library_site_condition_settings, paginated_links=links, pagination_meta=meta)  # type: ignore
    except Exception:
        logger.exception(
            f"Error getting tenant_library_site_condition_settings for {tenant_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{tenant_id}/library-site-conditions/{library_site_condition_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-site-conditions", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_tenant_library_site_condition_settings(
    tenant_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    tenant_library_site_condition_settings: TenantLibrarySiteConditionSettingsRequest,  # type: ignore
    manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        data = tenant_library_site_condition_settings.unpack()  # type: ignore

        logger.info(f"input data for creation -- {data}")

        update_input = UpdateTenantLibrarySiteConditionSettingInput(**data.dict())

        await manager.update_setting(
            tenant_id=tenant_id,
            primary_key_value=library_site_condition_id,
            input=update_input,
        )

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error updating tenant library site_condition settings for tenant: {tenant_id} library site_condition: {library_site_condition_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{tenant_id}/library-site-conditions/{library_site_condition_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-site-conditions", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_tenant_library_site_condition_settings(
    tenant_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        await manager.delete_setting(
            tenant_id=tenant_id, primary_key_value=library_site_condition_id
        )

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error deleting tenant library site_condition settings for tenant: {tenant_id} library site_condition: {library_site_condition_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
