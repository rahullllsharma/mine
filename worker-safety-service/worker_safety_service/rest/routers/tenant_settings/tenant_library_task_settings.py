import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import (
    CreateTenantLibraryTaskSettingInput,
    TenantLibraryTaskSettings,
    UpdateTenantLibraryTaskSettingInput,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_tenant_library_task_settings_manager,
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


class TenantLibraryTaskSettingsAttributes(BaseModel):
    __entity_name__ = "tenant-library-task-settings"

    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "tenant-library-task-settings"
    )

    alias: Optional[str] = Field(
        description="The custom name for the library task", default=None
    )


(
    TenantLibraryTaskSettingsRequest,
    _,
    TenantLibraryTaskSettingsResponse,
    _,
    TenantLibraryTaskSettingsPaginationResponse,
) = create_models(TenantLibraryTaskSettingsAttributes)


@router.post(
    "/{tenant_id}/library-tasks/{library_task_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["library-tasks", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def set_tenant_library_task_settings(
    tenant_id: uuid.UUID,
    library_task_id: uuid.UUID,
    tenant_library_task_settings: TenantLibraryTaskSettingsRequest,  # type: ignore
    manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    try:
        data = tenant_library_task_settings.unpack()  # type: ignore

        logger.info(f"input data for creation -- {data}")

        create_input = CreateTenantLibraryTaskSettingInput(
            tenant_id=tenant_id, library_task_id=library_task_id, **data.dict()
        )

        await manager.create_setting(input=create_input)

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error setting tenant library task settings for tenant: {tenant_id} library task: {library_task_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-tasks/{library_task_id}",
    response_model=TenantLibraryTaskSettingsResponse,
    status_code=200,
    tags=["library-tasks", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_task_setting(
    tenant_id: uuid.UUID,
    library_task_id: uuid.UUID,
    manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> TenantLibraryTaskSettingsResponse | ErrorResponse:  # type: ignore
    try:
        tlts = await manager.get(tenant_id=tenant_id, primary_key_value=library_task_id)

        if tlts is None:
            return ErrorResponse(
                status_code=404,
                title="Not Found",
                detail="Settings not found for the specified tenant and library task",
            )

        tlts_attributes = TenantLibraryTaskSettingsAttributes(alias=tlts.alias)

        return TenantLibraryTaskSettingsResponse.pack(uuid.uuid4(), tlts_attributes)  # type: ignore

    except Exception:
        logger.exception(
            f"error getting tenant library task settings for tenant: {tenant_id} library task: {library_task_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{tenant_id}/library-tasks",
    response_model=TenantLibraryTaskSettingsPaginationResponse,
    status_code=200,
    tags=["library-tasks", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_tenant_library_task_settings(
    request: Request,
    tenant_id: uuid.UUID,
    manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
    limit: int = query_params.limit,
) -> TenantLibraryTaskSettingsPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_tenant_library_task_settings = await manager.get_all(
            additional_where_clause=[TenantLibraryTaskSettings.tenant_id == tenant_id],
            limit=limit,
            order_by_attribute="library_task_id",
        )
        tenant_library_task_settings = [
            (
                uuid.uuid4(),
                TenantLibraryTaskSettingsAttributes(
                    **tenant_library_task_setting.dict()
                ),
            )
            for tenant_library_task_setting in db_tenant_library_task_settings
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=None,
            limit=limit,
            url=request.url,
            elements=tenant_library_task_settings,
        )
        return TenantLibraryTaskSettingsPaginationResponse.pack_many(elements=tenant_library_task_settings, paginated_links=links, pagination_meta=meta)  # type: ignore
    except Exception:
        logger.exception(f"Error getting tenant_library_task_settings for {tenant_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{tenant_id}/library-tasks/{library_task_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-tasks", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_tenant_library_task_settings(
    tenant_id: uuid.UUID,
    library_task_id: uuid.UUID,
    tenant_library_task_settings: TenantLibraryTaskSettingsRequest,  # type: ignore
    manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        data = tenant_library_task_settings.unpack()  # type: ignore

        logger.info(f"input data for creation -- {data}")

        update_input = UpdateTenantLibraryTaskSettingInput(**data.dict())

        await manager.update_setting(
            tenant_id=tenant_id, primary_key_value=library_task_id, input=update_input
        )

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error updating tenant library task settings for tenant: {tenant_id} library task: {library_task_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{tenant_id}/library-tasks/{library_task_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-tasks", "settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_tenant_library_task_settings(
    tenant_id: uuid.UUID,
    library_task_id: uuid.UUID,
    manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> ErrorResponse | EmptyResponse:
    try:
        await manager.delete_setting(
            tenant_id=tenant_id, primary_key_value=library_task_id
        )

        return EmptyResponse()

    except Exception:
        logger.exception(
            f"error deleting tenant library task settings for tenant: {tenant_id} library task: {library_task_id}"
        )

        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
