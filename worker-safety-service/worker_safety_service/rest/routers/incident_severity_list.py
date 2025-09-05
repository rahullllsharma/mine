import functools
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.incident_severity_list_manager import (
    IncidentSeverityManager,
)
from worker_safety_service.exceptions import DuplicateKeyException
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import IncidentSeverityCreate
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import (
    get_incident_severity_list_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    prefix="/incident_severity",
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class IncidentSeverityAttributes(BaseModel):
    __entity_name__ = "incident_severity"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "incident_severities"
    )

    ui_label: Optional[str] = Field(description="UI Label", default=None)
    api_value: Optional[str] = Field(description="API value", default=None)
    old_severity_mapping: Optional[str] = Field(
        description="Old Severity Mapping", default=None
    )
    source: Optional[str] = Field(description="Source", default=None)
    safety_climate_multiplier: Optional[float] = Field(
        description="Safety Climate Multiplier", default=None
    )
    created_at: Optional[datetime] = Field(description="Created at", default=None)


(
    IncidentSeverityRequest,
    IncidentSeverityBulkRequest,
    IncidentSeverityResponse,
    IncidentSeverityBulkResponse,
    IncidentSeverityPaginationResponse,
) = create_models(IncidentSeverityAttributes)


@router.post(
    "",
    response_model=IncidentSeverityResponse,
    status_code=201,
    tags=["incident_severity"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_incident_severity(
    incident_severity_request: IncidentSeverityRequest,  # type: ignore
    incident_severity_manager: IncidentSeverityManager = Depends(
        get_incident_severity_list_manager
    ),
) -> IncidentSeverityResponse | ErrorResponse:  # type: ignore
    try:
        data = incident_severity_request.unpack()  # type: ignore
        logger.debug(f"input data for incident severity creation -- {data}")
        create_input = IncidentSeverityCreate(**data.dict())
        created_incident_severity = await incident_severity_manager.create_severity(
            input=create_input
        )
        incident_severity = IncidentSeverityAttributes(
            **created_incident_severity.dict()
        )
        logger.debug("returning created incident_severity...")
        return IncidentSeverityResponse.pack(id=created_incident_severity.id, attributes=incident_severity)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating incident_severity not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate Incident Severity")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating incident severity with attributes {incident_severity_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
