import functools
import uuid
from typing import Optional

import mmh3
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models.base import (
    ApplicabilityLevel,
    LibraryTaskLibraryHazardLink,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import get_library_manager
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links


class TaskHazardApplicabilityLink(BaseModel):
    __entity_name__ = "library_task_library_hazard_link"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "library_task_library_hazard_links"
    )

    library_task_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="library-task",
            url_supplier=functools.partial(
                entity_url_supplier,
                "library-tasks",
            ),
        ),
    )

    library_hazard_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="library-hazard",
            url_supplier=functools.partial(
                entity_url_supplier,
                "library-hazards",
            ),
        ),
    )
    applicability_level: ApplicabilityLevel = Field(
        description="Applicability Level of Hazard", default=ApplicabilityLevel.NEVER
    )


(
    TaskAndHazardApplicabilityRequest,
    TaskAndHazardApplicabilityBulkRequest,
    TaskAndHazardApplicabilityResponse,
    TaskAndHazardApplicabilityBulkResponse,
    TaskAndHazardApplicabilityPaginationResponse,
) = create_models(TaskHazardApplicabilityLink)

router = APIRouter(
    prefix="/library-task-hazard-applicability",
    dependencies=[Depends(authenticate_integration)],
    tags=["Library Task Hazard Applicability"],
)

logger = get_logger(__name__)


@router.get(
    "",
    response_model=TaskAndHazardApplicabilityPaginationResponse,
    status_code=200,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_applicability(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    library_task_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-task]"
    ),
    library_hazard_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-hazard]"
    ),
    manager: LibraryManager = Depends(get_library_manager),
) -> TaskAndHazardApplicabilityPaginationResponse | ErrorResponse:  # type: ignore
    """Library task- Library hazard-Applicability-Link Pagination"""
    ltlhl = await manager.get_task_hazard_applicabilities(
        after=after,
        limit=limit,
        library_task_ids=library_task_ids,
        library_hazard_ids=library_hazard_ids,
        use_seek_pagination=True,
    )

    library_task_hazard_applicability_links = [
        (
            library_task_hazard_applicability_link.mmh3_hash_id,
            TaskHazardApplicabilityLink(
                **library_task_hazard_applicability_link.dict()
            ),
        )
        for library_task_hazard_applicability_link in ltlhl
    ]

    meta = PaginationMetaData(limit=limit)
    return TaskAndHazardApplicabilityPaginationResponse.pack_many(  # type: ignore
        elements=library_task_hazard_applicability_links,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_task_hazard_applicability_links
        ),
        pagination_meta=meta,
    )


@router.post(
    "",
    response_model=TaskAndHazardApplicabilityResponse,
    status_code=201,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_applicability(
    applicability_request: TaskAndHazardApplicabilityRequest,  # type: ignore
    library_task_hazard_applicability_manager: LibraryManager = Depends(
        get_library_manager
    ),
) -> TaskAndHazardApplicabilityResponse | ErrorResponse:  # type: ignore
    """
    Allows creating a new applicability request.
    """
    req: TaskHazardApplicabilityLink = applicability_request.unpack()  # type: ignore
    create_applicability_link = LibraryTaskLibraryHazardLink(
        library_task_id=req.library_task_id,
        library_hazard_id=req.library_hazard_id,
        applicability_level=req.applicability_level,
    )

    _id_str = (
        str(create_applicability_link.library_task_id)
        + "_"
        + str(create_applicability_link.library_hazard_id)
    )
    _id_hash = mmh3.hash_bytes(_id_str)
    _id = uuid.UUID(bytes=_id_hash)

    await library_task_hazard_applicability_manager.add_task_hazard_applicability(
        create_applicability_link
    )

    return TaskAndHazardApplicabilityResponse.pack(_id, create_applicability_link)  # type: ignore


@router.put(
    "",
    status_code=201,
    response_model=TaskAndHazardApplicabilityResponse,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_applicability(
    library_task_id: uuid.UUID = Query(default=None, alias="filter[library_task_id]"),
    library_hazard_id: uuid.UUID = Query(
        default=None, alias="filter[library_hazard_id]"
    ),
    applicability_level: ApplicabilityLevel = Query(
        default="never", alias="filter[applicability_level]"
    ),
    manager: LibraryManager = Depends(get_library_manager),
) -> TaskAndHazardApplicabilityResponse | ErrorResponse:  # type: ignore
    """
    Updates the applicability.
    By default 'never' is set.
    """
    update_applicability = LibraryTaskLibraryHazardLink(
        library_task_id=library_task_id,
        library_hazard_id=library_hazard_id,
        applicability_level=applicability_level,
    )

    await manager.update_task_hazard_applicability(update_applicability)

    ltlha = await manager.get_task_hazard_applicabilities(
        library_task_ids=[library_task_id], library_hazard_ids=[library_hazard_id]
    )

    _id_str = str(library_task_id) + "_" + str(library_hazard_id)
    _id_hash = mmh3.hash_bytes(_id_str)
    _id = uuid.UUID(bytes=_id_hash)

    return TaskAndHazardApplicabilityResponse.pack(_id, ltlha[0])  # type: ignore
