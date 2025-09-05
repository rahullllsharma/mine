import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.graphql.data_loaders.library_tasks import LibraryTasksLoader
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import LibraryTask
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.loaders import (
    get_library_tasks_loader,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_library_tasks_manager,
    get_tenant_library_task_settings_manager,
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

# TODO: Check the depends, we need to have a "master token" to be able to execute these methods.
router = APIRouter(dependencies=[Depends(authenticate_integration)])

logger = get_logger(__name__)


class WorkTypeRelationshipData(BaseModel):
    type: str = Field(default="work-type", const=True)
    id: uuid.UUID


class LibraryTaskAttributes(BaseModel):
    __entity_name__ = "library-task"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "library-tasks")

    name: str = Field(description="The task name as displayed in the App")
    hesp_score: int = Field(description="HESP Score associated with the task")
    is_critical: Optional[bool] = Field(
        description="To Determine the criticality of the task.", default=False
    )
    category: Optional[str] = Field(default=None)
    unique_task_id: Optional[str] = Field(
        description="An unique identifier for the task. Currently, this is not enforced.",
        default=None,
    )

    work_type_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="work-type",
            url_supplier=functools.partial(
                entity_array_url_supplier, "work-types", "library-task"
            ),
        ),
    )

    activity_group_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="activity-group",
            url_supplier=functools.partial(
                entity_array_url_supplier,
                "activity-groups",
                "library-task",
            ),
        ),
    )

    recommended_hazards_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="library-task-hazards-recommendation",
            url_supplier=functools.partial(
                entity_array_url_supplier,
                "library-task-hazards-recommendations",
                "library-task",
            ),
        ),
    )


(
    LibraryTaskRequest,
    LibraryTaskBulkRequest,
    LibraryTaskResponse,
    _,
    LibraryTaskPaginatedResponse,
) = create_models(LibraryTaskAttributes)


class LibraryTaskInput(LibraryTaskAttributes):
    work_types: Optional[list] = Field(default=None)


(
    LibraryTaskInputRequest,
    LibraryTaskInputBulkRequest,
    LibraryTaskInputResponse,
    _,
    LibraryTaskInputPaginatedResponse,
) = create_models(LibraryTaskInput)


# TODO: Extract these args to a common place
@router.get(
    "/library-tasks",
    response_model=LibraryTaskPaginatedResponse,
    status_code=200,
    tags=["library-tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_tasks(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    unique_task_ids: Optional[list[str]] = Query(
        default=None, alias="filter[uniqueTaskId]"
    ),
    library_task_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-task]"
    ),
    library_tasks_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
) -> LibraryTaskPaginatedResponse | ErrorResponse:  # type: ignore
    lt = await library_tasks_manager.get_library_tasks(
        after=after,
        limit=limit,
        unique_task_ids=unique_task_ids,
        ids=library_task_ids,
        use_seek_pagination=True,
    )

    library_tasks = [
        (
            library_task.id,
            LibraryTaskAttributes(
                name=library_task.name,
                is_critical=library_task.is_critical,
                hesp_score=library_task.hesp,
                category=library_task.category,
                unique_task_id=library_task.unique_task_id,
            ),
        )
        for library_task in lt
    ]

    meta = PaginationMetaData(limit=limit)

    return LibraryTaskPaginatedResponse.pack_many(  # type: ignore
        elements=library_tasks,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_tasks
        ),
        pagination_meta=meta,
    )


@router.get(
    "/library-tasks/{library_task_id}",
    response_model=LibraryTaskResponse,
    status_code=200,
    tags=["library-tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_task(
    library_task_id: uuid.UUID,
    library_tasks_loader: LibraryTasksLoader = Depends(get_library_tasks_loader),
) -> LibraryTaskResponse | ErrorResponse:  # type: ignore
    lt = await library_tasks_loader.get_by_id(library_task_id)
    if lt is None:
        return EntityNotFoundResponse(
            LibraryTaskAttributes.__entity_name__, library_task_id
        )

    lt_attributes = LibraryTaskAttributes(
        name=lt.name,
        is_critical=lt.is_critical,
        hesp_score=lt.hesp,
        category=lt.category,
        unique_task_id=lt.unique_task_id,
    )

    return LibraryTaskResponse.pack(lt.id, lt_attributes)  # type: ignore


@router.post(
    "/library-tasks/{library_task_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["library-tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_library_task(
    library_task_id: uuid.UUID,
    library_task_request: LibraryTaskInputRequest,  # type: ignore
    library_tasks_loader: LibraryTasksLoader = Depends(get_library_tasks_loader),
    tenant_library_task_settings_manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
    work_type_manager: WorkTypeManager = Depends(get_work_types_manager),
) -> EmptyResponse:
    """
    Creates a new Library Task.
    """
    lt_attributes: LibraryTaskInput = library_task_request.unpack()  # type: ignore
    to_create_lt = LibraryTask(
        id=library_task_id,
        name=lt_attributes.name,
        is_critical=lt_attributes.is_critical,
        hesp=lt_attributes.hesp_score,
        category=lt_attributes.category,
        unique_task_id=lt_attributes.unique_task_id,
    )
    await library_tasks_loader.create_library_task(to_create_lt)
    await tenant_library_task_settings_manager.add_library_entities_for_tenants(
        primary_key_values=[library_task_id]
    )
    if lt_attributes.work_types:
        await work_type_manager.link_work_types_to_task(
            library_task_id, lt_attributes.work_types
        )

    # TODO: Check if we want to make a commit by default in the with session method
    return EmptyResponse()


@router.put(
    "/library-tasks/{library_task_id}",
    response_model=LibraryTaskResponse,
    status_code=200,
    tags=["library-tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_library_task(
    library_task_id: uuid.UUID,
    library_task_request: LibraryTaskRequest,  # type: ignore
    library_tasks_loader: LibraryTasksLoader = Depends(get_library_tasks_loader),
) -> LibraryTaskResponse | ErrorResponse:  # type: ignore
    """
    Allows updating a Library Task.
    Currently, only the name, HESP Score, Criticality and WorkType is allowed to be updated.

    Be careful, changing library task has implications to the existing tasks.
    The name should not be changed into something semantically different, otherwise previous tasks will have their meaning changed as well.
    """
    lt_attributes: LibraryTaskAttributes = library_task_request.unpack()  # type: ignore
    to_update_lt = LibraryTask(
        id=library_task_id,
        name=lt_attributes.name,
        is_critical=lt_attributes.is_critical,
        hesp=lt_attributes.hesp_score,
        category=lt_attributes.category,
        unique_task_id=lt_attributes.unique_task_id,
    )

    await library_tasks_loader.update_library_task(to_update_lt)
    lt = await get_library_task(library_task_id, library_tasks_loader)
    return lt


@router.delete(
    "/library-tasks/{library_task_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["library-tasks"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_library_task(
    library_task_id: uuid.UUID,
    library_tasks_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
    tenant_library_task_settings_manager: TenantLibraryTaskSettingsManager = Depends(
        get_tenant_library_task_settings_manager
    ),
) -> EmptyResponse | ErrorResponse:
    try:
        await library_tasks_manager.archive(library_task_id)
        await tenant_library_task_settings_manager.delete_all_settings_by_id(
            primary_key_value=library_task_id
        )
        return EmptyResponse()
    except Exception:
        logger.exception(f"error archiving library task with id {library_task_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
