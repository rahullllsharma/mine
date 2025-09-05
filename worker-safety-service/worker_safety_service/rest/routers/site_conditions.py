import functools
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.exceptions import EntityNotFoundException
from worker_safety_service.graphql.data_loaders.site_conditions import (
    TenantSiteConditionLoader,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import SiteConditionCreate
from worker_safety_service.rest.api_models.new_jsonapi import (
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection import get_site_condition_loader
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)

SITE_CONDITIONS_PREFIX = "/site-conditions"
SITE_CONDITION_ROUTE = f"http://127.0.0.1:8000/rest{SITE_CONDITIONS_PREFIX}"

router = APIRouter(
    prefix=SITE_CONDITIONS_PREFIX,
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class SiteCondition(BaseModel):
    __entity_name__ = "site-conditions"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "site-conditions")

    library_site_condition_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="library-site-condition",
            url_supplier=functools.partial(
                entity_array_url_supplier, "library-site-conditions", "site-condition"
            ),
        ),
        description="Library Site Condition ID",
    )

    location_id: uuid.UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="location",
            url_supplier=functools.partial(
                entity_array_url_supplier,
                "locations",
                "site-condition",
            ),
        ),
    )


(
    SiteConditionRequest,
    SiteConditionBulkRequest,
    SiteConditionResponse,
    _,
    SiteConditionPaginationResponse,
) = create_models(SiteCondition)


@router.get(
    "/{site_condition_id}",
    response_model=SiteConditionResponse,
    status_code=200,
    tags=["site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_site_condition(
    site_condition_id: uuid.UUID,
    site_condition_loader: TenantSiteConditionLoader = Depends(
        get_site_condition_loader
    ),
) -> SiteConditionResponse:  # type: ignore
    try:
        lsc_sc_tuple = await site_condition_loader.get_site_conditions(
            ids=[site_condition_id]
        )
        if lsc_sc_tuple == []:
            raise EntityNotFoundException(
                entity_id=site_condition_id, entity_type=SiteCondition
            )
        _, site_condition = lsc_sc_tuple[0]
        return SiteConditionResponse.pack(site_condition_id, site_condition)  # type: ignore
    except EntityNotFoundException as e:
        raise e
    except Exception:
        raise HTTPException(500, "Internal Server Error")


@router.post(
    "",
    response_model=SiteConditionResponse,
    status_code=201,
    tags=["site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_site_condition(
    site_condition_request: SiteConditionRequest,  # type: ignore
    site_condition_loader: TenantSiteConditionLoader = Depends(
        get_site_condition_loader
    ),
) -> SiteConditionResponse:  # type: ignore
    sc_relationships: SiteCondition = site_condition_request.unpack()  # type: ignore
    try:
        sc_create = SiteConditionCreate(
            library_site_condition_id=sc_relationships.library_site_condition_id,
            location_id=sc_relationships.location_id,
            is_manually_added=True,
        )
        result = await site_condition_loader.create_site_condition(
            site_condition=sc_create,
            hazards=[],
            user=None,
        )

        return SiteConditionResponse.pack(result.id, result)  # type: ignore
    except ValueError as e:
        # TODO: This does not currently work correctly: WORK-887
        # https://urbint.atlassian.net/jira/software/c/projects/WORK/issues/WORK-887
        raise HTTPException(
            400,
            str(e),
        )
    except Exception:
        logger.exception("Error creating site condition")
        raise HTTPException(500, "Internal Server Error")


@router.delete(
    "/{site_condition_id}",
    status_code=204,
    tags=["site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_site_condition(
    site_condition_id: uuid.UUID,
    site_condition_loader: TenantSiteConditionLoader = Depends(
        get_site_condition_loader
    ),
) -> None:
    try:
        await site_condition_loader.archive_site_condition(site_condition_id, user=None)
    except EntityNotFoundException as e:
        raise e
    except Exception:
        logger.exception(f"Error archiving site condition {site_condition_id}")
        raise HTTPException(500, "Internal Server Error")
