import functools
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from worker_safety_service.exceptions import (
    DuplicateExternalKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.data_loaders.project_locations import (
    TenantProjectLocationLoader,
)
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import Location as LocationModel
from worker_safety_service.models import Tenant
from worker_safety_service.rest.api_models import (
    BulkResponse,
    Links,
    ManyToOneRelation,
    Meta,
    ModelRequest,
    ModelResponse,
    OneToOneRelation,
    RelationshipData,
    Response,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection import get_project_locations_loader
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.types import Point
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    prefix="/locations",
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)
LOCATIONS_ROUTE = "/rest/locations"
ACTIVITIES_ROUTE = "/rest/activities"
WORK_PACKAGES_ROUTE = "/rest/work-packages"


class Location(BaseModel):
    class Config:
        validate_all = True
        validate_assignment = True

    __entity_name__ = "location"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "locations")

    id: UUID = Field(description="ID")
    name: str = Field(description="Name of Hazard")
    latitude: Decimal = Field(description="Latitude")
    longitude: Decimal = Field(description="Longitude")
    external_key: Optional[str] = Field(description="External Key", default=None)
    address: Optional[str] = Field(description="Address")
    meta_attributes: Optional[dict] = Field(description="Meta Attributes", default=None)

    project_id: Optional[UUID] = Field(
        allow_mutation=False,
        relationship=RelationshipFieldAttributes(
            type="work-package",
            url_supplier=functools.partial(
                entity_url_supplier,
                "work-packages",
            ),
        ),
    )


(
    LocationsRequest,
    LocationsBulkRequest,
    LocationsResponse,
    _,
    LocationsPaginationResponse,
) = create_models(Location)


class LocationRelationships(BaseModel):
    activities: Optional[ManyToOneRelation] = None
    work_packages: OneToOneRelation


class LocationAttributes(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal
    external_key: Optional[str] = None
    address: Optional[str]
    meta_attributes: Optional[dict] = None


class LocationModelRequest(ModelRequest):
    type: str = "location"
    attributes: LocationAttributes
    relationships: LocationRelationships


class LocationModelResponse(ModelResponse):
    type: str = "location"
    attributes: LocationAttributes
    relationships: Optional[LocationRelationships]


class LocationRequest(BaseModel):
    data: LocationModelRequest


class LocationResponse(Response):
    data: LocationModelResponse


class LocationBulkResponse(BulkResponse):
    data: list[LocationModelResponse] = Field(default_factory=list)


@router.post(
    "",
    response_model=LocationResponse,
    status_code=201,
    tags=["locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_location(
    location_request: LocationRequest,
    locations_loader: TenantProjectLocationLoader = Depends(
        get_project_locations_loader
    ),
    tenant: Tenant = Depends(get_tenant),
) -> LocationResponse | ErrorResponse:
    """Create a location"""
    geom = Point(
        location_request.data.attributes.longitude,
        location_request.data.attributes.latitude,
    )
    project_id = location_request.data.relationships.work_packages.data.id
    location = LocationModel(
        **location_request.data.attributes.dict(),
        additional_supervisor_ids=[],
        geom=geom,
        tenant_id=tenant.id,
        project_id=project_id,
        clustering=[],
    )

    try:
        created_locations = await locations_loader.create_locations([location])
        created_location = created_locations[0]
    except ResourceReferenceException:
        logger.exception(
            f"Tenant id for work package {location.project_id} does not match incoming tenant id, or work package could not be found"
        )
        return ErrorResponse(
            400,
            "Bad request",
            f"No project found for project id {location.project_id}.  Location could not be created.",
        )
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )
    except Exception:
        logger.exception(
            f"error creating location {location_request.data.attributes.external_key}"
        )
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")

    return LocationResponse(
        links=Links(self=f"{LOCATIONS_ROUTE}/{created_location.id}"),
        data=LocationModelResponse(
            id=created_location.id,
            attributes=LocationAttributes(
                **created_location.dict(),
                latitude=location.geom.latitude,
                longitude=location.geom.longitude,
            ),
            relationships=LocationRelationships(
                activities=ManyToOneRelation(
                    links=Links(
                        related=f"{ACTIVITIES_ROUTE}?filter[location_id]={location.id}"
                    ),
                ),
                work_packages=OneToOneRelation(
                    data=RelationshipData(
                        type="work-package", id=created_location.project_id
                    ),
                    links=Links(
                        related=f"{WORK_PACKAGES_ROUTE}/{created_location.project_id}"
                    ),
                ),
            ),
        ),
    )


@router.put(
    "/{location_id}",
    response_model=LocationsResponse,
    status_code=200,
    tags=["locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_location(
    location_id: UUID,
    location_request: LocationsRequest,  # type: ignore
    locations_loader: TenantProjectLocationLoader = Depends(
        get_project_locations_loader
    ),
) -> LocationsResponse | ErrorResponse:  # type: ignore
    geom_changed = False
    location_request_data: Location = location_request.unpack()  # type: ignore

    [existing_location] = await locations_loader.get_locations(ids=[location_id])

    if not existing_location:
        return ErrorResponse(404, "Not Found!", "Location Not Found!")

    new_geom = Point(
        location_request_data.longitude,
        location_request_data.latitude,
    )
    if existing_location.geom != new_geom:
        geom_changed = True

    existing_location.name = location_request_data.name

    existing_location.geom = new_geom
    existing_location.external_key = location_request_data.external_key
    existing_location.address = location_request_data.address

    try:
        updated_location = await locations_loader.edit_location(
            existing_location, geom_changed
        )
    except DuplicateExternalKeyException:
        logger.info("duplicate external key")
        return ErrorResponse(
            400,
            "External Key already in use",
            "External Key already in use",
        )

    return LocationsResponse.pack(  # type: ignore
        id=updated_location.id,
        attributes=Location(
            **updated_location.dict(),
            longitude=updated_location.geom.longitude,
            latitude=updated_location.geom.latitude,
        ),
    )


@router.get(
    "/{location_id}",
    response_model=LocationResponse,
    status_code=200,
    tags=["locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_location(
    location_id: UUID,
    locations_loader: TenantProjectLocationLoader = Depends(
        get_project_locations_loader
    ),
) -> LocationResponse | ErrorResponse:
    """Get a location by id"""
    try:
        locations = await locations_loader.get_locations(ids=[location_id])
        if locations == []:
            return ErrorResponse(
                404, "Not Found", f"The Location {location_id} could not be found."
            )
        location = locations[0]

    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")

    response = LocationResponse(
        links=Links(self=f"{LOCATIONS_ROUTE}/{location.id}"),
        data=LocationModelResponse(
            id=location.id,
            attributes=LocationAttributes(
                **location.dict(),
                latitude=location.geom.latitude,
                longitude=location.geom.longitude,
            ),
            relationships=LocationRelationships(
                activities=ManyToOneRelation(
                    links=Links(
                        related=f"{ACTIVITIES_ROUTE}?filter[location_id]={location.id}"
                    ),
                ),
                work_packages=OneToOneRelation(
                    data=RelationshipData(type="work-package", id=location.project_id),
                    links=Links(related=f"{WORK_PACKAGES_ROUTE}/{location.project_id}"),
                ),
            ),
        ),
    )
    return response


@router.get(
    "",
    response_model=LocationBulkResponse,
    status_code=200,
    tags=["locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_locations(
    request: Request,
    locations_loader: TenantProjectLocationLoader = Depends(
        get_project_locations_loader
    ),
    tenant: Tenant = Depends(get_tenant),
    after: UUID | None = query_params.after,
    limit: int = query_params.limit,
    activity_ids: Optional[list[UUID]] = query_params.activity_ids,
    work_package_ids: Optional[list[UUID]] = query_params.work_package_ids,
    external_keys: Optional[list[str]] = query_params.external_keys,
    location_ids: Optional[list[UUID]] = query_params.location_ids,
) -> LocationBulkResponse | ErrorResponse:
    """Get locations"""
    try:
        locations = await locations_loader.get_locations(
            limit=limit,
            after=after,
            use_seek_pagination=True,
            activity_ids=activity_ids,
            project_ids=work_package_ids,
            external_keys=external_keys,
            ids=location_ids,
        )
    except Exception:
        logger.exception(f"Error getting locations for {tenant.tenant_name}")
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")
    data = [
        LocationModelResponse(
            id=location.id,
            attributes=LocationAttributes(
                **location.dict(),
                latitude=location.geom.latitude,
                longitude=location.geom.longitude,
            ),
            relationships=LocationRelationships(
                activities=ManyToOneRelation(
                    links=Links(
                        related=f"{ACTIVITIES_ROUTE}?filter[location_id]={location.id}"
                    ),
                ),
                work_packages=OneToOneRelation(
                    data=RelationshipData(type="work-package", id=location.project_id),
                    links=Links(related=f"{WORK_PACKAGES_ROUTE}/{location.project_id}"),
                ),
            ),
        )
        for location in locations
    ]
    meta = Meta(limit=limit)
    next_link: str | None = None
    if len(data) == limit:
        next_link = str(
            request.url.include_query_params(
                **{"page[limit]": limit, "page[after]": data[-1].id}
            )
        )

    links = Links(next=next_link)
    return LocationBulkResponse(data=data, meta=meta, links=links)


@router.delete(
    "",
    response_model=None,
    status_code=204,
    tags=["locations"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_work_package(
    location_ids: list[UUID] = query_params.location_ids,
    location_loader: TenantProjectLocationLoader = Depends(
        get_project_locations_loader
    ),
    tenant: Tenant = Depends(get_tenant),
) -> None:
    try:
        locations = await location_loader.get_locations(ids=location_ids)
        if not locations:
            return ErrorResponse(404, "Not Found", f"Locations {location_ids} not found.")  # type: ignore
        assert locations
        await location_loader.archive_locations(locations)
    except Exception:
        return ErrorResponse(500, "Internal Server Error", "An exception occurred")  # type: ignore
