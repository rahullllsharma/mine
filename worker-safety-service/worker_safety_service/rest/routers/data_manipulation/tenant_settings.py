import uuid
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_controls import LibraryControlManager
from worker_safety_service.dal.library_hazards import LibraryHazardManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.dependency_injection.managers import (
    get_library_control_manager,
    get_library_hazard_manager,
    get_library_site_condition_manager,
    get_library_tasks_manager,
    get_tenant_library_control_settings_manager,
    get_tenant_library_hazard_settings_manager,
    get_tenant_library_site_condition_settings_manager,
    get_tenant_library_task_settings_manager,
    get_tenant_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)

router = APIRouter(
    prefix="/data_manipulation/tenant-settings",
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class SimpleTenantRequest(BaseModel):
    tenant_id: Optional[uuid.UUID] = Field(
        description="Optional Tenant ID. If provided, settings will be created only for this tenant",
        default=None,
    )


@router.post(
    "/library-tasks",
    status_code=201,
    response_model=EmptyResponse,
    tags=["Tenant Settings Data Manipulation"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_tenant_library_task_settings(
    request: SimpleTenantRequest,
    tenant_manager: TenantManager = Depends(get_tenant_manager),
    library_tasks_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
    tlts_manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    """
    Create tenant settings for library tasks. If tenant_id is provided in the request,
    settings will be created only for that tenant. Otherwise, settings will be created
    for all tenants.
    """
    try:
        tenant_ids = None
        tenant_id = request.tenant_id
        if tenant_id:
            tenant_results = await tenant_manager.get_tenants_by_id([tenant_id])
            if not tenant_results:
                return ErrorResponse(400, "Bad Request", "Invalid tenant id")
            tenant_ids = [tenant_id]

        # Get all library tasks
        library_tasks = await library_tasks_manager.get_library_tasks()
        library_task_ids = [task.id for task in library_tasks]

        if not library_task_ids:
            return ErrorResponse(400, "Bad Request", "No library tasks found")

        await tlts_manager.add_library_entities_for_tenants(
            primary_key_values=library_task_ids, tenant_ids=tenant_ids
        )

        return EmptyResponse()

    except ResourceReferenceException as e:
        return ErrorResponse(400, "Invalid Reference", str(e))

    except Exception as e:
        logger.exception("Error creating tenant library task settings")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL, str(e))


@router.post(
    "/library-site-conditions",
    status_code=201,
    response_model=EmptyResponse,
    tags=["Tenant Settings Data Manipulation"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_tenant_library_site_condition_settings(
    request: SimpleTenantRequest,
    tenant_manager: TenantManager = Depends(get_tenant_manager),
    library_site_conditions_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
    tlscs_manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    """
    Create tenant settings for library site conditions. If tenant_id is provided in the request,
    settings will be created only for that tenant. Otherwise, settings will be created
    for all tenants.
    """
    try:
        # Get all library site conditions
        site_conditions = (
            await library_site_conditions_manager.get_library_site_conditions()
        )
        site_condition_ids = [sc.id for sc in site_conditions]

        if not site_condition_ids:
            return ErrorResponse(400, "Bad Request", "No library site conditions found")

        # Get tenants to process
        tenant_ids = None
        tenant_id = request.tenant_id
        if tenant_id:
            tenant_results = await tenant_manager.get_tenants_by_id([tenant_id])
            if not tenant_results:
                return ErrorResponse(400, "Bad Request", "Invalid tenant id")
            tenant_ids = [tenant_id]

        # Create settings for each tenant
        await tlscs_manager.add_library_entities_for_tenants(
            primary_key_values=site_condition_ids, tenant_ids=tenant_ids
        )

        return EmptyResponse()
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Invalid Reference", str(e))
    except Exception as e:
        logger.exception("Error creating tenant library site condition settings")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL, str(e))


@router.post(
    "/library-hazards",
    status_code=201,
    response_model=EmptyResponse,
    tags=["Tenant Settings Data Manipulation"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_tenant_library_hazard_settings(
    request: SimpleTenantRequest,
    tenant_manager: TenantManager = Depends(get_tenant_manager),
    library_hazards_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
    tlhs_manager: TenantLibraryHazardSettingsManager = Depends(
        get_tenant_library_hazard_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    """
    Create tenant settings for library hazards. If tenant_id is provided in the request,
    settings will be created only for that tenant. Otherwise, settings will be created
    for all tenants.
    """
    try:
        tenant_ids = None
        tenant_id = request.tenant_id
        if tenant_id:
            tenant_results = await tenant_manager.get_tenants_by_id([tenant_id])
            if not tenant_results:
                return ErrorResponse(400, "Bad Request", "Invalid tenant id")
            tenant_ids = [tenant_id]

        library_hazards = await library_hazards_manager.get_library_hazards()
        if not library_hazards:
            return ErrorResponse(400, "Bad Request", "No library hazards found")

        library_hazard_ids = [library_hazard.id for library_hazard in library_hazards]
        await tlhs_manager.add_library_entities_for_tenants(
            primary_key_values=library_hazard_ids, tenant_ids=tenant_ids
        )
        return EmptyResponse()
    except Exception as e:
        logger.exception(
            f"error setting tenant library hazard settings for tenant: {e}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.post(
    "/library-controls",
    status_code=201,
    response_model=EmptyResponse,
    tags=["Tenant Settings Data Manipulation"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_tenant_library_control_settings(
    request: SimpleTenantRequest,
    tenant_manager: TenantManager = Depends(get_tenant_manager),
    library_controls_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
    tlcs_manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    """
    Create tenant settings for library controls. If tenant_id is provided in the request,
    settings will be created only for that tenant. Otherwise, settings will be created
    for all tenants.
    """
    try:
        tenant_id = request.tenant_id
        # Get all library controls
        controls = await library_controls_manager.get_library_controls()
        control_ids = [c.id for c in controls]

        if not control_ids:
            return ErrorResponse(400, "Bad Request", "No library controls found")

        # Get tenants to process
        tenant_ids = None
        if tenant_id:
            tenant_results = await tenant_manager.get_tenants_by_id([tenant_id])
            if not tenant_results:
                return ErrorResponse(400, "Bad Request", "Invalid tenant id")
            tenant_ids = [tenant_id]

        # Create settings for each tenant
        await tlcs_manager.add_library_entities_for_tenants(
            primary_key_values=control_ids, tenant_ids=tenant_ids
        )

        return EmptyResponse()
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Invalid Reference", str(e))
    except Exception:
        logger.exception("Error creating tenant library control settings")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
