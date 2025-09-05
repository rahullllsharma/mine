import functools
import uuid
from typing import Optional

import mmh3
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_tasks_recomendations import (
    LibraryTaskHazardRecommendationsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import LibraryTaskRecommendations
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_library_tasks_hazard_recommendations_manager,
    get_tenant_library_control_settings_manager,
    get_tenant_library_hazard_settings_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links


class HazardAndControlRecommendation(BaseModel):
    __entity_name__ = "library-task-hazards-recommendation"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "library-task-hazards-recommendations"
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

    library_control_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="library-control",
            url_supplier=functools.partial(
                entity_url_supplier,
                "library-controls",
            ),
        ),
    )


(
    HazardAndControlRecommendationRequest,
    HazardAndControlRecommendationBulkRequest,
    HazardAndControlRecommendationResponse,
    HazardAndControlRecommendationBulkResponse,
    HazardAndControlRecommendationPaginationResponse,
) = create_models(HazardAndControlRecommendation)

# TODO: Check the depends, we need to have a "master token" to be able to execute these methods.
router = APIRouter(
    prefix="/library-task-hazards-recommendations",
    dependencies=[Depends(authenticate_integration)],
    tags=["Library Task Hazard Recommendations"],
)

logger = get_logger(__name__)


# TODO: Extract these args to a common place
@router.get(
    "/",
    response_model=HazardAndControlRecommendationBulkResponse,
    status_code=200,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_recommendations(
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
    library_control_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-control]"
    ),
    manager: LibraryTaskHazardRecommendationsManager = Depends(
        get_library_tasks_hazard_recommendations_manager
    ),
) -> HazardAndControlRecommendationBulkResponse | ErrorResponse:  # type: ignore
    """
    Allows retrieving the recommendations for a given Library Task.
    """

    lthr = await manager.get_library_task_recommendations(
        after=after,
        limit=limit,
        use_seek_pagination=True,
        library_task_ids=library_task_ids,
        library_hazard_ids=library_hazard_ids,
        library_control_ids=library_control_ids,
    )

    library_task_hazard_recommendations = [
        (
            library_task_hazard_recommendation.mmh3_hash_id,
            HazardAndControlRecommendation(**library_task_hazard_recommendation.dict()),
        )
        for library_task_hazard_recommendation in lthr
    ]

    meta = PaginationMetaData(limit=limit)

    return HazardAndControlRecommendationPaginationResponse.pack_many(  # type: ignore
        elements=library_task_hazard_recommendations,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_task_hazard_recommendations
        ),
        pagination_meta=meta,
    )


@router.post(
    "/",
    response_model=HazardAndControlRecommendationResponse,
    status_code=201,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_recommendation(
    recommendation_request: HazardAndControlRecommendationRequest,  # type: ignore
    manager: LibraryTaskHazardRecommendationsManager = Depends(
        get_library_tasks_hazard_recommendations_manager
    ),
    tlhs_manager: TenantLibraryHazardSettingsManager = Depends(
        get_tenant_library_hazard_settings_manager
    ),
    tlcs_manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> HazardAndControlRecommendationResponse | ErrorResponse:  # type: ignore
    """
    Allows creating a new recommendation request. This operation is idempotent.

    The recommendation id will be calculated using a 128-bit MurmurHash3 of the string representation of the tuple
    (library-task-id, library-hazard-id, library-control-id) joined by ','.

    The string representation was chosen to allow less powerful clients to be able to use the API.
    This algorithm was chosen because its proven record of consistent hashing.
    """
    req: HazardAndControlRecommendation = recommendation_request.unpack()  # type: ignore
    to_create = LibraryTaskRecommendations(
        library_task_id=req.library_task_id,
        library_hazard_id=req.library_hazard_id,
        library_control_id=req.library_control_id,
    )

    _id_str = (
        str(to_create.library_task_id)
        + ","
        + str(to_create.library_hazard_id)
        + ","
        + str(to_create.library_control_id)
    )
    _id_hash = mmh3.hash_bytes(_id_str)
    _id = uuid.UUID(bytes=_id_hash)

    await manager.create(to_create)
    await tlhs_manager.add_library_entities_for_tenants(
        primary_key_values=[to_create.library_hazard_id]
    )
    await tlcs_manager.add_library_entities_for_tenants(
        primary_key_values=[to_create.library_control_id]
    )
    return HazardAndControlRecommendationResponse.pack(_id, req)  # type: ignore


@router.delete(
    "/",
    response_model=None,
    status_code=204,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_recommendation(
    recommendation_request: HazardAndControlRecommendationRequest,  # type: ignore
    manager: LibraryTaskHazardRecommendationsManager = Depends(
        get_library_tasks_hazard_recommendations_manager
    ),
) -> EmptyResponse:
    """
    Allows deleting a recommendation request. This operation is idempotent.
    """
    req: HazardAndControlRecommendation = recommendation_request.unpack()  # type: ignore
    to_delete = LibraryTaskRecommendations(
        library_task_id=req.library_task_id,
        library_hazard_id=req.library_hazard_id,
        library_control_id=req.library_control_id,
    )

    await manager.delete(to_delete)
    return EmptyResponse()
