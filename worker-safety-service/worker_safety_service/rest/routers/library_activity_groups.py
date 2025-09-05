import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.library_activity_groups import (
    LibraryActivityGroupManager,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models.library import (
    LibraryActivityGroup as LibraryActivityGroupDB,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_library_activity_group_manager,
    get_library_tasks_manager,
)
from worker_safety_service.rest.exception_handlers import (
    EntityNotFoundResponse,
    ErrorResponse,
)
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links

# TODO: Check the depends, we need to have a "master token" to be able to execute these methods.
router = APIRouter(
    prefix="/activity-groups",
    dependencies=[Depends(authenticate_integration)],
    tags=["Activity Group"],
)

logger = get_logger(__name__)


class LibraryActivityGroup(BaseModel):
    __entity_name__ = "activity-group"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "activity-groups")

    name: str = Field(description="Name of the ActivityGroup")

    library_task_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="library-task",
            url_supplier=functools.partial(
                entity_array_url_supplier, "library-tasks", "activity-group"
            ),
        ),
    )


(
    LibraryActivityGroupRequest,
    LibraryActivityGroupBulkRequest,
    LibraryActivityGroupResponse,
    _,
    LibraryActivityGroupBulkResponse,
) = create_models(LibraryActivityGroup)


# TODO: Extract these args to a common place
@router.get(
    "",
    response_model=LibraryActivityGroupBulkResponse,
    status_code=200,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_activity_groups(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    activity_group_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[activity-group]"
    ),
    library_activity_group_manager: LibraryActivityGroupManager = Depends(
        get_library_activity_group_manager
    ),
) -> LibraryActivityGroupBulkResponse | ErrorResponse:  # type: ignore
    """
    Allows searching for ActivityGroups.
    """
    lag = await library_activity_group_manager.get_library_activity_groups(
        after=after,
        limit=limit,
        use_seek_pagination=True,
        ids=activity_group_ids,
    )

    library_activity_groups = [
        (
            activity_group.id,
            LibraryActivityGroup(**activity_group.dict()),
        )
        for activity_group in lag
    ]

    meta = PaginationMetaData(limit=limit)

    return LibraryActivityGroupBulkResponse.pack_many(  # type: ignore
        elements=library_activity_groups,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_activity_groups
        ),
        pagination_meta=meta,
    )


@router.get(
    "/{activity_group_id}",
    response_model=LibraryActivityGroupResponse,
    status_code=200,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_activity_group_by_id(
    activity_group_id: uuid.UUID,
    library_activity_group_manager: LibraryActivityGroupManager = Depends(
        get_library_activity_group_manager
    ),
) -> LibraryActivityGroupResponse | ErrorResponse:  # type: ignore
    """
    Retrieve a ActivityGroup.
    """
    try:
        activity_group = await library_activity_group_manager.get_by_id(
            entity_id=activity_group_id
        )
        if activity_group is None:
            return EntityNotFoundResponse(
                LibraryActivityGroup.__entity_name__, activity_group_id
            )

        resp = LibraryActivityGroup(**activity_group.dict())

        return LibraryActivityGroupResponse.pack(activity_group_id, resp)  # type: ignore
    except Exception:
        logger.exception(f"error retrieving activity group {activity_group_id}")
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")


@router.post(
    "/{activity_group_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_activity_group(
    activity_group_id: uuid.UUID,
    activity_group_request: LibraryActivityGroupRequest,  # type: ignore
    library_activity_group_manager: LibraryActivityGroupManager = Depends(
        get_library_activity_group_manager
    ),
) -> LibraryActivityGroupResponse | ErrorResponse:  # type: ignore
    """
    Creates a new Activity Group.
    The UUID must be supplied in order to keep consistency across environments.
    """
    attributes: LibraryActivityGroup = activity_group_request.unpack()  # type: ignore
    to_create = LibraryActivityGroupDB(
        id=activity_group_id,
        name=attributes.name,
    )
    await library_activity_group_manager.create(to_create)
    return EmptyResponse()


@router.put(
    "/{activity_group_id}",
    response_model=LibraryActivityGroupResponse,
    status_code=200,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_activity_group(
    activity_group_id: uuid.UUID,
    activity_group_request: LibraryActivityGroupRequest,  # type: ignore
    library_activity_group_manager: LibraryActivityGroupManager = Depends(
        get_library_activity_group_manager
    ),
) -> LibraryActivityGroupResponse | ErrorResponse:  # type: ignore
    """
    Allows changing the name of a ActivityGroup.
    """
    attributes = activity_group_request.unpack()  # type: ignore
    to_update = LibraryActivityGroupDB(
        id=activity_group_id,
        name=attributes.name,
    )

    await library_activity_group_manager.update(to_update)
    ret = await get_activity_group_by_id(
        activity_group_id, library_activity_group_manager
    )
    return ret


@router.delete(
    "/{activity_group_id}",
    status_code=204,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_activity_group(
    activity_group_id: uuid.UUID,
    library_activity_group_manager: LibraryActivityGroupManager = Depends(
        get_library_activity_group_manager
    ),
) -> None:
    """
    Deletes a given ActivityGroup.
    """
    try:
        await library_activity_group_manager.archive(activity_group_id)
    except EntityNotFoundException:
        return EntityNotFoundResponse(LibraryActivityGroup.__entity_name__, activity_group_id)  # type: ignore
    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")  # type: ignore


@router.put(
    "/{activity_group_id}/relationships/library-tasks/{library_task_id}",
    status_code=204,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def add_library_task(
    activity_group_id: uuid.UUID,
    library_task_id: uuid.UUID,
    library_tasks_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
) -> None:
    """
    Adds a library task to this activity group.
    """
    await library_tasks_manager.register_in_activity_group(
        library_task_id, activity_group_id
    )


@router.delete(
    "/{activity_group_id}/relationships/library-tasks/{library_task_id}",
    status_code=204,
    tags=["activity-groups"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def remove_library_task(
    activity_group_id: uuid.UUID,
    library_task_id: uuid.UUID,
    library_tasks_manager: LibraryTasksManager = Depends(get_library_tasks_manager),
) -> None:
    """
    Removes a library task from this activity group.
    """
    await library_tasks_manager.unregister_in_activity_group(
        library_task_id, activity_group_id
    )
