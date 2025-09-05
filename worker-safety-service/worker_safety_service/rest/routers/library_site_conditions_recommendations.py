import functools
import uuid
from typing import Optional

import mmh3
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_site_conditions_recommendations import (
    LibrarySiteConditionRecommendationManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import LibrarySiteConditionRecommendations
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection import (
    get_library_site_condition_recommendation_manager,
    get_tenant_library_control_settings_manager,
    get_tenant_library_hazard_settings_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links

LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE = (
    "/library-site-condition-hazards-recommendations"
)


class SiteConditionHazardAndControlRecommendation(BaseModel):
    __entity_name__ = "library-site-condition-hazards-recommendation"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "library-site-condition-hazards-recommendations"
    )

    library_site_condition_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="library-site-condition",
            url_supplier=functools.partial(
                entity_url_supplier,
                "library-site-conditions",
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
    SiteConditionHazardAndControlRecommendationRequest,
    SiteConditionHazardAndControlRecommendationBulkRequest,
    SiteConditionHazardAndControlRecommendationResponse,
    SiteConditionHazardAndControlRecommendationBulkResponse,
    SiteConditionHazardAndControlRecommendationPaginationResponse,
) = create_models(SiteConditionHazardAndControlRecommendation)

# TODO: Check the depends, we need to have a "master token" to be able to execute these methods.
router = APIRouter(
    prefix=LIBRARY_SITE_CONDITION_RECOMMENDATIONS_ROUTE,
    dependencies=[Depends(authenticate_integration)],
    tags=["Library Site Condition Hazard Recommendations"],
)

logger = get_logger(__name__)


@router.get(
    "",
    response_model=SiteConditionHazardAndControlRecommendationPaginationResponse,
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
    library_site_condition_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[site_conditions]"
    ),
    library_hazard_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library_hazards]"
    ),
    library_control_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library_controls]"
    ),
    library_site_condition_recommendations_manager: LibrarySiteConditionRecommendationManager = Depends(
        get_library_site_condition_recommendation_manager
    ),
) -> SiteConditionHazardAndControlRecommendationPaginationResponse | ErrorResponse:  # type: ignore
    """
    Allows retrieving the recommendations for a given Library Site Condition.
    """

    lscr = await library_site_condition_recommendations_manager.get_library_site_conditions_recommendations(
        after=after,
        limit=limit,
        library_site_condition_ids=library_site_condition_ids,
        library_hazard_ids=library_hazard_ids,
        library_control_ids=library_control_ids,
        use_seek_pagination=True,
    )

    library_site_condition_recommendations = [
        (
            library_site_condition_recommendation.mmh3_hash_id,
            SiteConditionHazardAndControlRecommendation(
                **library_site_condition_recommendation.dict()
            ),
        )
        for library_site_condition_recommendation in lscr
    ]

    meta = PaginationMetaData(limit=limit)

    return SiteConditionHazardAndControlRecommendationPaginationResponse.pack_many(  # type: ignore
        elements=library_site_condition_recommendations,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_site_condition_recommendations
        ),
        pagination_meta=meta,
    )


@router.post(
    "",
    response_model=SiteConditionHazardAndControlRecommendationResponse,
    status_code=201,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_recommendation(
    recommendation_request: SiteConditionHazardAndControlRecommendationRequest,  # type: ignore
    library_site_condition_recommendations_manager: LibrarySiteConditionRecommendationManager = Depends(
        get_library_site_condition_recommendation_manager
    ),
    tlhs_manager: TenantLibraryHazardSettingsManager = Depends(
        get_tenant_library_hazard_settings_manager
    ),
    tlcs_manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> SiteConditionHazardAndControlRecommendationResponse | ErrorResponse:  # type: ignore
    """
    Allows creating a new recommendation request.
    """
    req: SiteConditionHazardAndControlRecommendation = recommendation_request.unpack()  # type: ignore
    create_recommendation = LibrarySiteConditionRecommendations(
        library_site_condition_id=req.library_site_condition_id,
        library_control_id=req.library_control_id,
        library_hazard_id=req.library_hazard_id,
    )

    _id_str = (
        str(create_recommendation.library_site_condition_id)
        + ","
        + str(create_recommendation.library_hazard_id)
        + ","
        + str(create_recommendation.library_control_id)
    )
    _id_hash = mmh3.hash_bytes(_id_str)
    _id = uuid.UUID(bytes=_id_hash)

    await library_site_condition_recommendations_manager.add_library_site_condition_recommendation(
        create_recommendation
    )
    await tlhs_manager.add_library_entities_for_tenants(
        primary_key_values=[create_recommendation.library_hazard_id]
    )
    await tlcs_manager.add_library_entities_for_tenants(
        primary_key_values=[create_recommendation.library_control_id]
    )
    return SiteConditionHazardAndControlRecommendationResponse.pack(_id, create_recommendation)  # type: ignore


@router.get(
    "/{recommendation_id}",
    response_model=SiteConditionHazardAndControlRecommendationResponse,
    status_code=200,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_recommendation(
    recommendation_id: uuid.UUID,
    library_site_condition_recommendations_manager: LibrarySiteConditionRecommendationManager = Depends(
        get_library_site_condition_recommendation_manager
    ),
) -> SiteConditionHazardAndControlRecommendationResponse | ErrorResponse:  # type: ignore
    """
    Allows retrieving a given recommendation by id.
    The recommendation id will be calculated using a 128-bit MurmurHash3 of the tuple
    (library-site-condition-id, library-hazard-id, library-control-id).
    This algorithm was chosen because its proven record of consistent hashing.
    """
    raise NotImplementedError()


@router.delete(
    "",
    status_code=204,
    response_model=None,
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_recommendation(
    library_site_condition_id: uuid.UUID = Query(
        default=None, alias="filter[library_site_condition_id]"
    ),
    library_hazard_id: uuid.UUID = Query(
        default=None, alias="filter[library_hazard_id]"
    ),
    library_control_id: uuid.UUID = Query(
        default=None, alias="filter[library_control_id]"
    ),
    library_site_condition_recommendations_manager: LibrarySiteConditionRecommendationManager = Depends(
        get_library_site_condition_recommendation_manager
    ),
) -> None:
    """
    Deletes a given recommendation.
    """
    delete_recommendation = LibrarySiteConditionRecommendations(
        library_site_condition_id=library_site_condition_id,
        library_hazard_id=library_hazard_id,
        library_control_id=library_control_id,
    )

    existing_library_site_condition_hazard_recommendation = await library_site_condition_recommendations_manager.get_library_site_conditions_recommendations(
        library_site_condition_ids=[library_site_condition_id],
        library_hazard_ids=[library_hazard_id],
        library_control_ids=[library_control_id],
    )

    if not existing_library_site_condition_hazard_recommendation:
        return ErrorResponse(404, "Not Found", "Not found")  # type: ignore

    await library_site_condition_recommendations_manager.delete_library_site_condition_recommendation(
        delete_recommendation
    )
