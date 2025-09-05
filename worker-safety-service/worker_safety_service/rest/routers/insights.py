import functools
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, Request
from pydantic import BaseModel, Field, HttpUrl
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.insight_manager import InsightManager
from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.permissions import (
    CanConfigureTheApplication,
    CanReadReports,
)
from worker_safety_service.keycloak import IsAuthorized, get_tenant
from worker_safety_service.models import CreateInsightInput, Tenant, UpdateInsightInput
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import get_insight_manager
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

# Route Permissions
can_read_reports = IsAuthorized(CanReadReports)
can_configure_app = IsAuthorized(CanConfigureTheApplication)

router = APIRouter(prefix="/insights")

logger = get_logger(__name__)


class InsightAttributes(BaseModel):
    __entity_name__ = "insight"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "insights")

    name: Optional[str] = Field(description="Insight Name", default=None)
    url: Optional[HttpUrl] = Field(description="URL", default=None)
    description: Optional[str] = Field(description="Description", default=None)
    visibility: bool = Field(description="Visibility", default=True)
    created_at: Optional[datetime] = Field(description="Created at", default=None)


(
    InsightRequest,
    InsightBulkRequest,
    InsightResponse,
    InsightBulkResponse,
    InsightPaginationResponse,
) = create_models(InsightAttributes)


@router.post(
    "",
    response_model=InsightResponse,
    status_code=201,
    tags=["insights"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def create_insight(
    insight_request: InsightRequest,  # type: ignore
    insight_manager: InsightManager = Depends(get_insight_manager),
    tenant: Tenant = Depends(get_tenant),
) -> InsightResponse | ErrorResponse:  # type: ignore
    try:
        data = insight_request.unpack()  # type: ignore
        logger.info(f"input data for insight creation -- {data}")
        create_input = CreateInsightInput(**data.dict())
        created_insight = await insight_manager.create(
            input=create_input, tenant_id=tenant.id
        )
        insight = InsightAttributes(**created_insight.dict())
        logger.info("returning created insight...")
        return InsightResponse.pack(id=created_insight.id, attributes=insight)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating insights not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate insight")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating insight with attributes {insight_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "",
    response_model=InsightPaginationResponse,
    status_code=200,
    tags=["insights"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_read_reports)],
)
async def get_insights(
    request: Request,
    tenant: Tenant = Depends(get_tenant),
    insight_manager: InsightManager = Depends(get_insight_manager),
    limit: int = query_params.limit,
    after: Optional[UUID] = Query(
        default=None,
        alias="page[after]",
    ),
) -> InsightPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_insights = await insight_manager.get_all(
            tenant_id=tenant.id, limit=limit, after=after
        )
        insights = [
            (insight.id, InsightAttributes(**insight.dict())) for insight in db_insights
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=after, limit=limit, url=request.url, elements=insights
        )
        return InsightPaginationResponse.pack_many(elements=insights, paginated_links=links, pagination_meta=meta)  # type: ignore
    except Exception:
        logger.exception(f"Error getting insights for {tenant.tenant_name}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{insight_id}",
    response_model=InsightResponse,
    status_code=200,
    tags=["insights"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def update_insight(
    insight_id: UUID,
    insight_update: InsightRequest,  # type: ignore
    tenant: Tenant = Depends(get_tenant),
    insight_manager: InsightManager = Depends(get_insight_manager),
) -> InsightResponse | ErrorResponse:  # type: ignore
    try:
        data: InsightAttributes = insight_update.unpack()  # type: ignore
        logger.info(f"input data for insight update -- {data}")
        update_input = UpdateInsightInput(
            **data.dict(),
            tenant_id=tenant.id,
        )
        updated_insight_db = await insight_manager.update(
            id=insight_id, input=update_input, tenant_id=tenant.id
        )
        updated_insight = InsightAttributes(**updated_insight_db.dict())
        return InsightResponse.pack(id=updated_insight_db.id, attributes=updated_insight)  # type: ignore
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Insight not found", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate insight")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(f"Error updating insight for {insight_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{insight_id}",
    response_model=None,
    status_code=204,
    tags=["insights"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def archive_insight(
    insight_id: UUID,
    insight_manager: InsightManager = Depends(get_insight_manager),
    tenant: Tenant = Depends(get_tenant),
) -> bool | ErrorResponse:
    try:
        return await insight_manager.archive(id=insight_id, tenant_id=tenant.id)
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Insight not found", str(e))
    except Exception:
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/reorder/",
    response_model=InsightPaginationResponse,
    status_code=200,
    tags=["insights"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def reorder_insight(
    request: Request,
    ordered_ids: Annotated[
        list[UUID],
        Body(
            description="Provide all the insight UUIDs in the custom order."
            " It's mandatory to provide all the UUID's."
        ),
    ],
    limit: int = query_params.limit,
    tenant: Tenant = Depends(get_tenant),
    insight_manager: InsightManager = Depends(get_insight_manager),
) -> InsightPaginationResponse | ErrorResponse:  # type: ignore
    try:
        logger.info(f"input data for insight reorder -- {ordered_ids}")
        db_reordered_insights = await insight_manager.reorder(
            ordered_ids=ordered_ids, tenant_id=tenant.id, limit=limit
        )
        reordered_insights = [
            (insight.id, InsightAttributes(**insight.dict()))
            for insight in db_reordered_insights
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=None, limit=limit, url=request.url, elements=reordered_insights
        )
        return InsightPaginationResponse.pack_many(elements=reordered_insights, paginated_links=links, pagination_meta=meta)  # type: ignore
    except RuntimeError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception("Error reordering insights")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
