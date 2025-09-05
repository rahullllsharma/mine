import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from worker_safety_service.exceptions import (
    DuplicateExternalKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import (
    Activity,
    ActivityCreate,
    ActivityEdit,
    ActivityStatus,
    Tenant,
)
from worker_safety_service.rest import api_models
from worker_safety_service.rest.dependency_injection import get_activity_loader
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    dependencies=[Depends(get_activity_loader), Depends(authenticate_integration)]
)

logger = get_logger(__name__)


class ActivityAttributes(BaseModel):
    name: str
    start_date: datetime.date
    end_date: datetime.date
    status: ActivityStatus
    external_key: str | None = None
    meta_attributes: dict | None = None


class LocationRelationshipData(BaseModel):
    id: uuid.UUID
    type: str = "location"


class LocationRelationship(BaseModel):
    data: LocationRelationshipData


class ActivityRelationships(BaseModel):
    location: LocationRelationship


class ActivityModelRequest(api_models.ModelRequest):
    type: str = "activity"
    attributes: ActivityAttributes
    relationships: ActivityRelationships


class ActivityModelResponse(api_models.ModelResponse):
    type: str = "activity"
    attributes: ActivityAttributes
    relationships: ActivityRelationships


class ActivityRequest(BaseModel):
    data: ActivityModelRequest


class ActivityResponse(api_models.Response):
    data: ActivityModelResponse


class ActivityBulkRequest(BaseModel):
    data: list[ActivityModelRequest]


class ActivityBulkResponse(api_models.BulkResponse):
    data: list[ActivityModelResponse] = Field(default_factory=list)


@router.get(
    "/activities",
    response_model=ActivityBulkResponse,
    status_code=200,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_activites(
    request: Request,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
    tenant: Tenant = Depends(get_tenant),
    after: Optional[uuid.UUID] = query_params.after,
    limit: int = query_params.limit,
    location_ids: Optional[list[uuid.UUID]] = query_params.location_ids,
    external_keys: Optional[list[str]] = query_params.external_keys,
) -> ActivityBulkResponse | ErrorResponse:
    """Get activities"""
    try:
        activities = await activity_loader.get_activities(
            limit=limit,
            after=after,
            location_ids=location_ids,
            external_keys=external_keys,
        )
    except Exception:
        logger.exception("error getting activities for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = [
        ActivityModelResponse(
            id=activity.id,
            attributes=ActivityAttributes(**activity.dict()),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(id=activity.location_id)
                )
            ),
        )
        for activity in activities
    ]
    meta = api_models.Meta(limit=limit)
    next_link: str | None = None
    if len(data) == limit:
        next_link = str(
            request.url.include_query_params(**{"page[after]": data[-1].id})
        )
    links = api_models.Links(next=next_link)
    return ActivityBulkResponse(data=data, meta=meta, links=links)


@router.get(
    "/activities/{activity_id}",
    response_model=ActivityResponse,
    status_code=200,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_activity(
    activity_id: uuid.UUID,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
) -> ActivityResponse | ErrorResponse:
    """Get an activity by id"""
    activities: list[Activity] | None = None
    try:
        activities = await activity_loader.get_activities(ids=[activity_id])
    except Exception:
        logger.exception("error getting activities for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    if activities:
        activity = activities[0]
        return ActivityResponse(
            data=ActivityModelResponse(
                id=activity.id,
                attributes=ActivityAttributes(**activity.dict()),
                relationships=ActivityRelationships(
                    location=LocationRelationship(
                        data=LocationRelationshipData(id=activity.location_id)
                    )
                ),
            )
        )
    else:
        return ErrorResponse(404, "Activity not found", "Activity not found")


@router.post(
    "/activities",
    response_model=ActivityResponse,
    status_code=201,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_activity(
    activity_request: ActivityRequest,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
) -> ActivityResponse | ErrorResponse:
    """Create an activity"""
    create_activity = ActivityCreate(
        **activity_request.data.attributes.dict(),
        location_id=activity_request.data.relationships.location.data.id,
    )
    try:
        activity = await activity_loader.create_activity(create_activity)
    except ResourceReferenceException as re:
        logger.info(f"related attribute not found : {re}")
        return ErrorResponse(400, "Related attribute not found", f"{re}")
    except ValueError as ve:
        logger.info(f"invalid start or end date : {ve}")
        return ErrorResponse(400, "Bad Request", f"{ve}")
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception("error creating activity for {create_activity}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")
    return ActivityResponse(
        data=ActivityModelResponse(
            id=activity.id,
            attributes=ActivityAttributes(**activity.dict()),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(id=activity.location_id)
                )
            ),
        )
    )


@router.post(
    "/activities/bulk",
    response_model=ActivityBulkResponse,
    status_code=201,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_activities(
    activities: ActivityBulkRequest,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
    tenant: Tenant = Depends(get_tenant),
) -> ActivityBulkResponse | ErrorResponse:
    """Create activities"""
    if len(activities.data) > 200:
        return ErrorResponse(
            400, "Too many activities", "Limit create requests to 200 activities"
        )
    create_activities = [
        ActivityCreate(
            **i.attributes.dict(),
            location_id=i.relationships.location.data.id,
        )
        for i in activities.data
    ]
    try:
        created_activities = await activity_loader.create_activities(create_activities)
    except ResourceReferenceException as re:
        logger.info(f"related attribute not found : {re}")
        return ErrorResponse(400, "Related attribute not found", f"{re}")
    except ValueError as ve:
        logger.info(f"invalid start or end date : {ve}")
        return ErrorResponse(400, "Bad Request", f"{ve}")
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception("error creating activity for {create_activity}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = [
        ActivityModelResponse(
            id=activity.id,
            attributes=ActivityAttributes(**activity.dict()),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(id=activity.location_id)
                )
            ),
        )
        for activity in created_activities
    ]
    return ActivityBulkResponse(data=data)


@router.put(
    "/activities/{activity_id}",
    response_model=ActivityResponse,
    status_code=200,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_activity(
    activity_id: uuid.UUID,
    activity_update: ActivityRequest,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
    tenant: Tenant = Depends(get_tenant),
) -> ActivityResponse | ErrorResponse:
    """Update an activity"""
    activity_edit = ActivityEdit(
        id=activity_id,
        **activity_update.data.attributes.dict(),
        tenant_id=tenant.id,
        location_id=activity_update.data.relationships.location.data.id,
    )
    activity: Activity | None = None
    try:
        activity = await activity_loader.update_activity(activity_edit)
    except ResourceReferenceException as re:
        if "activity" in f"{re}".lower():
            return ErrorResponse(404, "Activity not found", f"{re}")
        return ErrorResponse(400, "Resource not found", f"{re}")

    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception("error updating activity for {activity_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    if activity is None:
        # No changes from current model
        activity = Activity(**activity_edit.dict())
    return ActivityResponse(
        data=ActivityModelResponse(
            id=activity.id,
            attributes=ActivityAttributes(**activity.dict()),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(id=activity.location_id)
                )
            ),
        )
    )


@router.delete(
    "/activities/{activity_id}",
    response_class=Response,
    status_code=204,
    tags=["activities"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_activity(
    activity_id: uuid.UUID,
    activity_loader: TenantActivityLoader = Depends(get_activity_loader),
) -> None:  # can't include ErrorResponse as a return type as this conflicts with fastapi implementation of 204
    """Delete an activity"""
    try:
        await activity_loader.delete_activity(activity_id, None)
    except ResourceReferenceException:
        return ErrorResponse(404, "Activity Not Found", "Activity Not Found")  # type: ignore
    except Exception:
        logger.exception("error deleting activity for {activity_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")  # type: ignore
