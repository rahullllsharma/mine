import functools
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.first_aid_aed_locations import (
    FirstAIDAEDLocationsManager,
)
from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.permissions import (
    CanConfigureTheApplication,
    CanReadReports,
)
from worker_safety_service.keycloak import IsAuthorized, get_tenant
from worker_safety_service.models import (
    CreateFirstAidAEDLocationsInput,
    Tenant,
    UpdateFirstAidAEDLocationsInput,
)
from worker_safety_service.models.base import LocationType
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import (
    get_first_aid_aed_locations_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.urbint_logging import get_logger

# Route Permissions
can_read_location = IsAuthorized(CanReadReports)
can_configure_location = IsAuthorized(CanConfigureTheApplication)

router = APIRouter(prefix="/first-aid-aed-locations")

logger = get_logger(__name__)


class FirstAidAedLocationsAttribute(BaseModel):
    __entity_name__ = "first_aid_aed_locations"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "first_aid_aed_locations"
    )

    location_name: str = Field(description="Location Name")
    location_type: LocationType = Field(description="Type of Location")


(
    FirstAidAedLocationsRequest,
    FirstAidAedLocationsBulkRequest,
    FirstAidAedLocationsResponse,
    FirstAidAedLocationsBulkResponse,
    FirstAidAedLocationsPaginationResponse,
) = create_models(FirstAidAedLocationsAttribute)

ERROR_500_TITLE = "An exception has occurred"
ERROR_500_DETAIL = "An exception has occurred"


@router.post(
    "",
    response_model=FirstAidAedLocationsResponse,
    status_code=201,
    tags=["first-aid-aed-locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_first_aid_locations(
    location_request: FirstAidAedLocationsRequest,  # type: ignore
    first_aid_aed_location_manager: FirstAIDAEDLocationsManager = Depends(
        get_first_aid_aed_locations_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> FirstAidAedLocationsResponse | ErrorResponse:  # type: ignore
    try:
        data = location_request.unpack()  # type: ignore
        create_input = CreateFirstAidAEDLocationsInput(**data.dict())
        created_location = (
            await first_aid_aed_location_manager.create_first_aid_and_aed_location(
                input=create_input, tenant_id=tenant.id
            )
        )
        location = FirstAidAedLocationsAttribute(**created_location.dict())
        return FirstAidAedLocationsResponse.pack(id=created_location.id, attributes=location)  # type: ignore
    except ValidationError as e:
        logger.exception(
            "Inputs provided for creating First AID location and AED locations are not valid"
        )
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error creating first aid and aed locations with attributes {location_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/{location_id}",
    response_model=FirstAidAedLocationsResponse,
    status_code=200,
    tags=["first-aid-aed-locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_first_aid_and_aed_location_by_id(
    location_id: UUID,
    first_aid_aed_location_manager: FirstAIDAEDLocationsManager = Depends(
        get_first_aid_aed_locations_manager
    ),
) -> FirstAidAedLocationsResponse | ErrorResponse:  # type: ignore
    try:
        db_first_aid_and_aed_location = (
            await first_aid_aed_location_manager.get_first_aid_aed_location_by_id(
                location_id=location_id
            )
        )
        if db_first_aid_and_aed_location is None:
            return ErrorResponse(
                404, "Not Found", f"The Location {location_id} could not be found."
            )

        first_aid_aed_location = FirstAidAedLocationsAttribute(
            **db_first_aid_and_aed_location.dict()
        )
        return FirstAidAedLocationsResponse.pack(id=db_first_aid_and_aed_location.id, attributes=first_aid_aed_location)  # type: ignore
    except DuplicateKeyException as e:
        logger.exception("Duplicate location")
        return ErrorResponse(400, "External Key already in use", str(e))
    except Exception:
        logger.exception("Error getting location")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{location_id}",
    response_model=FirstAidAedLocationsResponse,
    status_code=200,
    tags=["first-aid-aed-locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_first_aid_aed_location(
    location_id: UUID,
    location_request: FirstAidAedLocationsRequest,  # type: ignore
    first_aid_aed_location_manager: FirstAIDAEDLocationsManager = Depends(
        get_first_aid_aed_locations_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> FirstAidAedLocationsResponse | ErrorResponse:  # type: ignore
    try:
        data = location_request.unpack()  # type: ignore
        update_input = UpdateFirstAidAEDLocationsInput(**data.dict())
        updated_location = (
            await first_aid_aed_location_manager.update_first_aid_and_aed_location(
                location_id=location_id, update_input=update_input
            )
        )
        if updated_location is None:
            return ErrorResponse(
                404, "Not Found", f"The Location {location_id} could not be found."
            )
        location = FirstAidAedLocationsAttribute(**updated_location.dict())
        return FirstAidAedLocationsResponse.pack(id=updated_location.id, attributes=location)  # type: ignore
    except ValidationError as e:
        logger.exception(
            "Inputs provided for updating First AID location and AED locations are not valid"
        )
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error updating first aid and aed locations with attributes {location_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{location_id}",
    response_model=None,
    status_code=204,
    tags=["first-aid-aed-locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_first_aid_aed_location(
    location_id: UUID,
    first_aid_aed_location_manager: FirstAIDAEDLocationsManager = Depends(
        get_first_aid_aed_locations_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> bool | ErrorResponse:
    try:
        return await first_aid_aed_location_manager.archive_first_aid_and_aed_location(
            location_id=location_id, tenant_id=tenant.id
        )
    except ResourceReferenceException as e:
        logger.exception(e)
        return ErrorResponse(400, "first aid and aed location not found", str(e))
    except Exception as e:
        logger.exception(e)
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
