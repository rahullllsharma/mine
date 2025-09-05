import datetime
import uuid
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.exceptions import (
    DuplicateExternalKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.data_loaders.incidents import IncidentsLoader
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import Incident, Tenant
from worker_safety_service.models.consumer_models import IncidentSeverityEnum
from worker_safety_service.rest import api_models
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.dependency_injection import get_incidents_loader
from worker_safety_service.rest.dependency_injection.managers import (
    get_incidents_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(dependencies=[Depends(authenticate_integration)])

logger = get_logger(__name__)


class IncidentRequestAttributes(BaseModel):
    external_key: Optional[str] = None
    incident_date: datetime.date
    incident_type: str
    task_type: Optional[uuid.UUID] = None
    work_type: Optional[uuid.UUID] = None
    severity: Optional[IncidentSeverityEnum] = None
    description: str
    meta_attributes: Optional[dict] = None
    supervisor_id: Optional[uuid.UUID] = None
    contractor_id: Optional[uuid.UUID] = None


class IncidentsResponseAttributes(BaseModel):
    external_key: Optional[str] = None
    incident_date: datetime.date
    incident_type: str
    task_type_id: Optional[uuid.UUID] = None
    work_type: Optional[uuid.UUID] = None
    severity: Optional[IncidentSeverityEnum] = None
    description: str
    meta_attributes: Optional[dict] = None


class IncidentModelRequest(api_models.ModelRequest):
    type: str = "incident"
    attributes: IncidentRequestAttributes


class IncidentsModelResponse(api_models.ModelResponse):
    type: str = "incident"
    attributes: IncidentsResponseAttributes


class IncidentsRequest(BaseModel):
    data: IncidentModelRequest


class IncidentsResponse(api_models.Response):
    data: IncidentsModelResponse


class IncidentsBulkRequest(BaseModel):
    data: list[IncidentModelRequest]


class IncidentsBulkResponse(api_models.BulkResponse):
    data: list[IncidentsModelResponse] = Field(default_factory=list)


@router.post(
    "/incidents", response_model=IncidentsResponse, status_code=201, tags=["incidents"]
)
async def create_incident(
    incident_request: IncidentsRequest,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
) -> IncidentsResponse | ErrorResponse:
    """Create an incident"""
    incident = Incident(**incident_request.data.attributes.dict(), tenant_id=tenant.id)

    try:
        created_incidents = await incidents_loader.create_incidents([incident])
        if not created_incidents:
            return ErrorResponse(
                500, "An exception has occurred", "An exception occurred"
            )
        created_incident = created_incidents[0]
    except ValueError as ve:
        return ErrorResponse(400, "Invalid Data Attributes", f"{ve}")
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception(
            f"error creating incident {incident_request.data.attributes.external_key}"
        )
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    return IncidentsResponse(
        data=IncidentsModelResponse(
            id=created_incident.id,
            attributes=IncidentsResponseAttributes(**created_incident.dict()),
        )
    )


@router.post(
    "/incidents/bulk",
    response_model=IncidentsBulkResponse,
    status_code=201,
    tags=["incidents"],
)
async def create_incidents(
    incidents: IncidentsBulkRequest,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
) -> IncidentsBulkResponse | ErrorResponse:
    """Create incidents"""
    data = [
        Incident(**i.attributes.dict(), tenant_id=tenant.id) for i in incidents.data
    ]
    try:
        created_incidents = await incidents_loader.create_incidents(data)
    except ValueError as ve:
        return ErrorResponse(400, "Invalid Data Attributes", f"{ve}")
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception("error creating incidents")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    return IncidentsBulkResponse(
        data=(
            IncidentsModelResponse(
                id=incident.id,
                attributes=IncidentsResponseAttributes(**incident.dict()),
            )
            for incident in created_incidents
        )
    )


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentsResponse,
    status_code=200,
    tags=["incidents"],
)
async def get_incident(
    incident_id: UUID,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
) -> IncidentsResponse | ErrorResponse:
    """Get an incident by id"""
    try:
        incident = await incidents_loader.get_incident(incident_id)
    except ResourceReferenceException:
        return ErrorResponse(404, "Not found", f"No item found for id {incident_id}")
    except Exception:
        logger.exception(f"error getting incident {incident_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    return IncidentsResponse(
        data=IncidentsModelResponse(
            attributes=IncidentsResponseAttributes(**incident.dict()),
            id=incident.id,
        )
    )


@router.get(
    "/incidents",
    response_model=IncidentsBulkResponse,
    status_code=200,
    tags=["incidents"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_incidents(
    request: Request,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
    after: Optional[uuid.UUID] = query_params.after,
    limit: int = query_params.limit,
    allow_archived: bool = query_params.include_archived,
    external_keys: Optional[list[str]] = query_params.external_keys,
) -> IncidentsBulkResponse | ErrorResponse:
    """Get incidents"""
    try:
        incidents = await incidents_loader.get_incidents(
            limit=limit,
            after=after,
            allow_archived=allow_archived,
            external_keys=external_keys,
        )
    except Exception:
        logger.exception("error getting incidents for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    data = [
        IncidentsModelResponse(
            id=incident.id,
            attributes=IncidentsResponseAttributes(**incident.dict()),
        )
        for incident in incidents
    ]
    meta = api_models.Meta(limit=limit)
    next_link: str | None = None
    if len(data) == limit:
        next_link = str(
            request.url.include_query_params(**{"page[after]": data[-1].id})
        )
    links = api_models.Links(next=next_link)

    return IncidentsBulkResponse(data=data, meta=meta, links=links)


@router.put(
    "/incidents/{incident_id}",
    response_model=IncidentsResponse,
    status_code=200,
    tags=["incidents"],
)
async def update_incident(
    incident_id: UUID,
    incident_updates: IncidentsRequest,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
) -> IncidentsResponse | ErrorResponse:
    """Update an incident"""
    incident = Incident(
        id=incident_id, **incident_updates.data.attributes.dict(), tenant_id=tenant.id
    )
    try:
        incidents = await incidents_loader.update_incidents([incident])
        if not incidents:
            raise ValueError("incident not found for update")
    except ValueError as ve:
        if "not enough incidents found for update" == str(ve):
            return ErrorResponse(
                404, "Not found", f"No item found for id {incident_id}"
            )
        else:
            return ErrorResponse(400, "Invalid data attributes", f"{ve}")
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception(f"error getting incident {incident_id}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")

    return IncidentsResponse(
        data=IncidentsModelResponse(
            id=incidents[0].id,
            attributes=IncidentsResponseAttributes(**incidents[0].dict()),
        )
    )


@router.delete(
    "/incidents/{incident_id}",
    response_model=EmptyResponse,
    status_code=200,
    tags=["incidents"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_incident(
    incident_id: uuid.UUID,
    incidents_manager: IncidentsManager = Depends(get_incidents_manager),
) -> EmptyResponse:
    await incidents_manager.archive_incident(incident_id)
    return EmptyResponse()


@router.put(
    "/incidents/{incident_id}/relationships/library-tasks/{library_task_id}",
    response_model=None,
    status_code=200,
    tags=["incidents"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def link_incident_to_library_task(
    incident_id: UUID,
    library_task_id: UUID,
    incidents_loader: IncidentsLoader = Depends(get_incidents_loader),
    tenant: Tenant = Depends(get_tenant),
) -> EmptyResponse | ErrorResponse:
    """Link an incident to a library task"""
    try:
        await incidents_loader.link_incident_to_library_task(
            incident_id=incident_id, library_task_id=library_task_id
        )
        return EmptyResponse()
    except ResourceReferenceException:
        return ErrorResponse(
            404,
            "Not found",
            f"No item found for incident_id {incident_id} and library_task_id {library_task_id}",
        )
    except Exception:
        logger.exception(
            f"error linking incident {incident_id} to library task {library_task_id}"
        )
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")
