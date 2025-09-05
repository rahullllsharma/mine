import functools
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.activity_work_type_settings import (
    ActivityWorkTypeSettingsManager,
)
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import (
    CreateCoreWorkTypeInput,
    CreateTenantWorkTypeInput,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginatedLinks,
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_activity_work_type_settings_manager,
    get_library_manager,
    get_tenant_library_task_settings_manager,
    get_tenant_manager,
    get_work_types_manager,
)
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
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links


class WorkTypeAttributes(BaseModel):
    __entity_name__ = "work-type"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "work-types")

    name: Optional[str] = Field(description="Name of the WorkType", default=None)
    core_work_type_ids: Optional[list] = Field(
        description="Core Work Type Ids",
        default=None,
    )
    code: Optional[str] = Field(description="Work Type Code", default=None)

    library_task_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="library-task",
            url_supplier=functools.partial(
                entity_array_url_supplier, "library-tasks", "work-type"
            ),
        ),
    )

    tenant_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="tenant",
            url_supplier=functools.partial(
                entity_array_url_supplier, "tenant", "work-type"
            ),
        ),
    )

    library_site_condition_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="library-site-condition",
            url_supplier=functools.partial(
                entity_array_url_supplier, "library-site-conditions", "work-type"
            ),
        ),
    )


(
    WorkTypeRequest,
    WorkTypeBulkRequest,
    WorkTypeResponse,
    _,
    WorkTypeBulkResponse,
) = create_models(WorkTypeAttributes)


class ActivityWorkTypeSettingsAttributes(BaseModel):
    __entity_name__ = "activity-work-type-settings"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "activity-work-type-settings"
    )

    library_activity_group_id: uuid.UUID = Field(
        description="Library Activity Group ID"
    )
    alias: Optional[str] = Field(description="Alias for the settings", default=None)
    disabled_at: Optional[datetime] = Field(
        description="When the settings were disabled", default=None
    )


(
    ActivityWorkTypeSettingsRequest,
    ActivityWorkTypeSettingsBulkRequest,
    ActivityWorkTypeSettingsResponse,
    _,
    ActivityWorkTypeSettingsBulkResponse,
) = create_models(ActivityWorkTypeSettingsAttributes)

# TODO: Check the depends, we need to have a "master token" to be able to execute these methods.
router = APIRouter(dependencies=[Depends(authenticate_integration)])

logger = get_logger(__name__)


# TODO: Extract these args to a common place
@router.get(
    "/work-types",
    response_model=WorkTypeBulkResponse,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_work_types(
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    name: Optional[list[str]] = Query(default=None, alias="filter[name]"),
    tenant_ids: Optional[list[uuid.UUID]] = Query(default=None, alias="filter[tenant]"),
    library_task_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-task]"
    ),
) -> WorkTypeBulkResponse | ErrorResponse:  # type: ignore
    """
    Allows searching for WorkTypes.
    """
    work_types = await work_type_manager.get_work_types(
        work_type_names=name,
        tenant_ids=tenant_ids,
        library_task_ids=library_task_ids,
        after=after,
        limit=limit,
    )
    return WorkTypeBulkResponse.pack_many(  # type: ignore
        list(map(lambda wt: (wt.id, WorkTypeAttributes(name=wt.name)), work_types)),
        paginated_links=PaginatedLinks(self="http://127.0.0.1"),
        pagination_meta=None,
    )


@router.get(
    "/work-types/{work_type_id}",
    response_model=WorkTypeResponse,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_work_type_by_id(
    work_type_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> WorkTypeResponse | ErrorResponse:  # type: ignore
    """
    Retrieve a WorkType.
    """
    wt = await work_type_manager.get_by_id(work_type_id)
    if wt is None:
        return EntityNotFoundResponse(WorkTypeAttributes.__entity_name__, work_type_id)

    return WorkTypeResponse.pack(wt.id, WorkTypeAttributes(name=wt.name))  # type: ignore


@router.post(
    "/work-types/{work_type_id}",
    response_model=None,
    status_code=201,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_work_type_by_id(
    work_type_id: uuid.UUID,
    work_type_request: WorkTypeRequest,  # type: ignore
    tenant_id: uuid.UUID | None = None,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
    tenant_manager: TenantManager = Depends(get_tenant_manager),
    activity_worktype_settings_manager: ActivityWorkTypeSettingsManager = Depends(
        get_activity_work_type_settings_manager
    ),
    library_manager: LibraryManager = Depends(get_library_manager),
) -> str | ErrorResponse:
    """
    Creates a new Core Work Type.
    The UUID must be supplied in order to keep consistency across environments.
    """
    try:
        data = work_type_request.unpack().dict()  # type: ignore
        if data.get("core_work_type_ids") and tenant_id:
            if not await tenant_manager.get_tenants_by_id([tenant_id]):
                raise RuntimeError(f"No tenant found with id {tenant_id}")
            wt_attributes = CreateTenantWorkTypeInput(
                id=work_type_id, tenant_id=tenant_id, **data
            )
        else:
            wt_attributes = CreateCoreWorkTypeInput(id=work_type_id, **data)  # type: ignore
        await work_type_manager.create_work_type(wt_attributes)

        if data.get("core_work_type_ids") and tenant_id:
            total_activity_group_ids: list = []
            activity_group_ids: list = []
            for core_work_type_id in data.get("core_work_type_ids"):
                task_ids = await work_type_manager.get_task_ids_linked_to_work_type(
                    core_work_type_id
                )
                if task_ids and len(task_ids) > 0:
                    activity_group_ids = await library_manager.get_activity_group_ids_by_library_task_ids(
                        task_ids
                    )
                    total_activity_group_ids.extend(activity_group_ids)
            activity_worktype_list = []
            for activity_group_id in total_activity_group_ids:
                if not (activity_group_id and work_type_id):
                    continue
                activity_worktype_list.append(
                    {
                        "library_activity_group_id": activity_group_id,
                        "work_type_id": work_type_id,
                        "alias": None,
                        "disabled_at": None,
                    }
                )
            if activity_worktype_list and len(activity_worktype_list) > 0:
                await activity_worktype_settings_manager.create_bulk_settings(
                    activity_worktype_list
                )

        return "Work Type Created Successfully"
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error creating work type with attributes {work_type_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/work-types/{work_type_id}",
    response_model=WorkTypeResponse,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_work_type(
    work_type_id: uuid.UUID,
    work_type_request: WorkTypeRequest,  # type: ignore
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> WorkTypeResponse | ErrorResponse:  # type: ignore
    """
    Allows changing the name of a WorkType.
    """
    try:
        data = work_type_request.unpack().dict()  # type: ignore
        updated_work_type = await work_type_manager.update_work_type(
            work_type_id=work_type_id, input=data
        )
        return WorkTypeResponse.pack(id=updated_work_type.id, attributes=updated_work_type)  # type: ignore
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except RuntimeError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error updating work type with attributes {work_type_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/work-types/{work_type_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_work_type(
    work_type_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> EmptyResponse | ErrorResponse:
    """
    Archives a given WorkType only if it is empty, i.e. not assigned to any LibraryTasks.
    """
    try:
        await work_type_manager.archive_work_type(work_type_id)
        return EmptyResponse()
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Work Type not found", str(e))
    except Exception:
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/work-types/{work_type_id}/relationships/tenants/{tenant_id}",
    status_code=204,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
    deprecated=True,  # because now we are moving towards tenant_work_types and core_work_types model.
)
async def enable_work_type_for_tenant(
    work_type_id: uuid.UUID,
    tenant_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> None:
    """
    Enables this WorkType for a specific tenant.
    """
    return None
    # await work_type_manager.link_work_types_to_tenant(tenant_id, [work_type_id])


@router.delete(
    "/work-types/{work_type_id}/relationships/tenants/{tenant_id}",
    status_code=204,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
    deprecated=True,  # because now we are moving towards tenant_work_types and core_work_types model.
)
async def disable_work_type_for_tenant(
    work_type_id: uuid.UUID,
    tenant_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> None:
    """
    Disable this WorkType for a specific Tenant.
    """
    return None
    # await work_type_manager.unlink_work_types_to_tenant(tenant_id, [work_type_id])


@router.put(
    "/work-types/{work_type_id}/relationships/library-tasks/{task_id}",
    response_model=None,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def enable_work_type_for_task(
    work_type_id: uuid.UUID,
    task_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
    tlts_manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> str | ErrorResponse:
    """
    Enables this WorkType for a specific tenant.
    """
    try:
        await work_type_manager.link_work_types_to_task(task_id, [work_type_id])
        tenant_ids = await work_type_manager.get_tenant_ids_for_work_types(
            [work_type_id]
        )
        await tlts_manager.add_library_entities_for_tenants(
            primary_key_values=[task_id], tenant_ids=tenant_ids
        )
        return (
            f"work type with id {work_type_id} successfully linked to "
            f"library task with id {task_id}"
        )
    except Exception:
        logger.exception(
            f"Error linking work type {work_type_id} to library task {task_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/work-types/{work_type_id}/relationships/library-tasks/{task_id}",
    response_model=None,
    status_code=204,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def disable_work_type_for_task(
    work_type_id: uuid.UUID,
    task_id: uuid.UUID,
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> str | ErrorResponse:
    """
    Disable this WorkType for a specific Tenant.
    """
    try:
        await work_type_manager.unlink_work_types_from_task(task_id, work_type_id)
        return (
            f"work type with id {work_type_id} successfully un-linked from "
            f"library task with id {task_id}"
        )
    except Exception:
        logger.exception(
            f"Error unlinking work type {work_type_id} from library task {task_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/work-types/{work_type_id}/relationships/library-site-conditions/{library_site_condition_id}",
    response_model=None,
    status_code=200,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def enable_work_type_for_site_condition(
    work_type_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    work_types_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> str | ErrorResponse:
    """
    Enables this WorkType for a specific library site condition.
    """
    try:
        await work_types_manager.link_work_type_to_site_condition(
            library_site_condition_id=library_site_condition_id,
            work_type_id=work_type_id,
        )
        return (
            f"work type with id {work_type_id} successfully linked to "
            f"library site condition with id {library_site_condition_id}"
        )
    except Exception:
        logger.exception(
            f"Error linking work type {work_type_id} to "
            f"library site condition {library_site_condition_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/work-types/{work_type_id}/relationships/library-site-conditions/{library_site_condition_id}",
    response_model=None,
    status_code=204,
    tags=["Work Type"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def disable_work_type_for_site_condition(
    work_type_id: uuid.UUID,
    library_site_condition_id: uuid.UUID,
    work_types_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> str | ErrorResponse:
    """
    Disable this WorkType for a specific library site condition.
    """
    try:
        await work_types_manager.unlink_work_type_from_site_condition(
            library_site_condition_id=library_site_condition_id,
            work_type_id=work_type_id,
        )
        return (
            f"work type with id {work_type_id} de linked from "
            f"library site condition with id {library_site_condition_id}"
        )
    except Exception:
        logger.exception(
            f"Error unlinking work type {work_type_id} from "
            f"library site condition  {library_site_condition_id}"
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


# NOTE: Work Type Activity Settings


@router.post(
    "/work-types/{work_type_id}/activity-settings",
    response_model=ActivityWorkTypeSettingsResponse,
    status_code=201,
    tags=["Activity Work Type Settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_activity_work_type_settings(
    work_type_id: uuid.UUID,
    settings_request: ActivityWorkTypeSettingsRequest,  # type: ignore
    settings_manager: ActivityWorkTypeSettingsManager = Depends(
        get_activity_work_type_settings_manager
    ),
) -> ActivityWorkTypeSettingsResponse | ErrorResponse:  # type: ignore
    """
    Create new Activity Work Type Settings.
    Will fail if a setting with the same activity group and work type combination already exists.
    The disabled_at field cannot be set through this endpoint.
    """
    try:
        data = settings_request.unpack().dict()  # type: ignore
        # Remove disabled_at from data if present
        data.pop("disabled_at", None)
        created_settings = await settings_manager.create_settings(
            work_type_id=work_type_id,
            library_activity_group_id=data["library_activity_group_id"],
            alias=data.get("alias"),
            disabled_at=None,  # Always set to None for new settings
        )
        if not created_settings:
            return ErrorResponse(409, "Invalid Request", "Record already exists!")
        return ActivityWorkTypeSettingsResponse.pack(  # type: ignore
            id=created_settings.id,
            attributes=ActivityWorkTypeSettingsAttributes(
                library_activity_group_id=created_settings.library_activity_group_id,
                alias=created_settings.alias,
                disabled_at=created_settings.disabled_at,
            ),
        )
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception as e:
        logger.exception(
            f"Error creating activity work type settings with attributes {settings_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, str(e))


@router.get(
    "/work-types/{work_type_id}/activity-settings",
    response_model=ActivityWorkTypeSettingsBulkResponse,
    status_code=200,
    tags=["Activity Work Type Settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_activity_work_type_settings(
    request: Request,
    work_type_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager = Depends(
        get_activity_work_type_settings_manager
    ),
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    library_activity_group_id: Optional[uuid.UUID] = Query(default=None),
    alias: Optional[str] = Query(default=None),
    include_disabled: bool = Query(default=False),
) -> ActivityWorkTypeSettingsBulkResponse | ErrorResponse:  # type: ignore
    """
    Get Activity Work Type Settings for a work type.
    """
    try:
        settings = await settings_manager.get_settings(
            work_type_id=work_type_id,
            library_activity_group_id=library_activity_group_id,
            alias=alias,
            include_disabled=include_disabled,
        )

        # Apply pagination
        start_index = 0
        if after:
            # Find the index of the 'after' item
            for i, setting in enumerate(settings):
                if setting.id == after:
                    start_index = i + 1
                    break

        end_index = start_index + limit
        paginated_settings = settings[start_index:end_index]

        settings_data = list(
            map(
                lambda s: (
                    s.id,
                    ActivityWorkTypeSettingsAttributes(
                        library_activity_group_id=s.library_activity_group_id,
                        alias=s.alias,
                        disabled_at=s.disabled_at,
                    ),
                ),
                paginated_settings,
            )
        )

        meta = PaginationMetaData(limit=limit)

        return ActivityWorkTypeSettingsBulkResponse.pack_many(  # type: ignore
            settings_data,
            paginated_links=create_pagination_links(
                after, limit, request.url, settings_data
            ),
            pagination_meta=meta,
        )
    except Exception:
        logger.exception("Error getting activity work type settings")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/work-types/{work_type_id}/activity-settings",
    response_model=ActivityWorkTypeSettingsResponse,
    status_code=200,
    tags=["Activity Work Type Settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_activity_work_type_settings(
    work_type_id: uuid.UUID,
    settings_request: ActivityWorkTypeSettingsRequest,  # type: ignore
    settings_manager: ActivityWorkTypeSettingsManager = Depends(
        get_activity_work_type_settings_manager
    ),
) -> ActivityWorkTypeSettingsResponse | ErrorResponse:  # type: ignore
    """
    Update Activity Work Type Settings.
    If a setting with the same activity group and work type combination doesn't exist,
    it will be created.
    The disabled_at field cannot be updated through this endpoint.
    """
    try:
        data = settings_request.unpack().dict()  # type: ignore
        # Remove disabled_at from data if present
        data.pop("disabled_at", None)
        updated_settings = await settings_manager.update_settings(
            work_type_id=work_type_id,
            library_activity_group_id=data["library_activity_group_id"],
            alias=data.get("alias"),
            disabled_at=None,  # Always set to None for updates
        )
        return ActivityWorkTypeSettingsResponse.pack(  # type: ignore
            id=updated_settings.id,
            attributes=ActivityWorkTypeSettingsAttributes(
                library_activity_group_id=updated_settings.library_activity_group_id,
                alias=updated_settings.alias,
                disabled_at=updated_settings.disabled_at,
            ),
        )
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception as e:
        logger.exception(
            f"Error updating activity work type settings with attributes {settings_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, str(e))


@router.delete(
    "/work-types/{work_type_id}/activity-settings/{library_activity_group_id}",
    response_model=ActivityWorkTypeSettingsResponse,
    status_code=200,
    tags=["Activity Work Type Settings"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def disable_activity_work_type_settings(
    work_type_id: uuid.UUID,
    library_activity_group_id: uuid.UUID,
    settings_manager: ActivityWorkTypeSettingsManager = Depends(
        get_activity_work_type_settings_manager
    ),
) -> ActivityWorkTypeSettingsResponse | ErrorResponse:  # type: ignore
    """
    Disable Activity Work Type Settings by setting disabled_at to current UTC time.
    The settings are identified by the combination of work_type_id and activity_group_id.
    """
    try:
        disabled_settings = await settings_manager.disable_settings(
            work_type_id=work_type_id,
            library_activity_group_id=library_activity_group_id,
        )
        return ActivityWorkTypeSettingsResponse.pack(  # type: ignore
            id=disabled_settings.id,
            attributes=ActivityWorkTypeSettingsAttributes(
                library_activity_group_id=disabled_settings.library_activity_group_id,
                alias=disabled_settings.alias,
                disabled_at=disabled_settings.disabled_at,
            ),
        )
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception as e:
        logger.exception("Error disabling activity work type settings")
        return ErrorResponse(500, ERROR_500_TITLE, str(e))
