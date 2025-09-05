import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_hazards import LibraryHazardManager
from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import EnergyLevel, EnergyType
from worker_safety_service.models import LibraryHazard as LibraryHazardModel
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection import (
    get_library_hazard_manager,
    get_tenant_library_hazard_settings_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links

LIBRARY_HAZARD_PREFIX = "/library-hazards"

router = APIRouter(
    prefix=LIBRARY_HAZARD_PREFIX, dependencies=[Depends(authenticate_integration)]
)

logger = get_logger(__name__)


class LibraryHazard(BaseModel):
    __entity_name__ = "library-hazard"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "library-hazards")

    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Name of Hazard")
    energy_type: EnergyType = Field(
        description="Energy Type of this Hazard", default=EnergyType.NOT_DEFINED
    )
    energy_level: EnergyLevel = Field(
        description="High or Low energy level Hazard", default=EnergyLevel.NOT_DEFINED
    )
    for_tasks: bool = Field(description="Is this Hazard for a Task")
    for_site_conditions: bool = Field(description="Is this Hazard for a Site Condition")
    image_url: Optional[str] = Field(
        description="url for the icon of the Hazard", default=None
    )
    image_url_png: Optional[str] = Field(
        description="url for the icon of the Hazard in png format", default=None
    )


(
    LibraryHazardRequest,
    LibraryHazardBulkRequest,
    LibraryHazardResponse,
    _,
    LibraryHazardPaginationResponse,
) = create_models(LibraryHazard)


@router.get(
    "",
    response_model=LibraryHazardPaginationResponse,
    status_code=200,
    tags=["library-hazards"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_hazards(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    library_site_condition_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-site-condition]"
    ),
    library_task_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library-task]"
    ),
    library_hazard_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
) -> LibraryHazardPaginationResponse | ErrorResponse:  # type: ignore
    lh = await library_hazard_manager.get_library_hazards(
        after=after,
        limit=limit,
        library_site_condition_ids=library_site_condition_ids,
        library_task_ids=library_task_ids,
        use_seek_pagination=True,
    )

    library_hazards = [
        (
            library_hazard.id,
            LibraryHazard(**library_hazard.dict()),
        )
        for library_hazard in lh
    ]

    meta = PaginationMetaData(limit=limit)

    return LibraryHazardPaginationResponse.pack_many(  # type: ignore
        elements=library_hazards,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_hazards
        ),
        pagination_meta=meta,
    )


@router.post(
    "/{library_hazard_id}",
    response_model=LibraryHazardResponse,
    status_code=201,
    tags=["library-hazards"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_library_hazard(
    library_hazard_id: uuid.UUID,
    library_hazard: LibraryHazardRequest,  # type: ignore
    library_hazard_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
    tenant_library_hazard_settings_manager: TenantLibraryHazardSettingsManager = Depends(
        get_tenant_library_hazard_settings_manager
    ),
) -> LibraryHazardResponse | ErrorResponse:  # type: ignore
    library_hazard_data = LibraryHazardModel(
        **library_hazard.unpack().dict()  # type: ignore
    )
    library_hazard_data.id = library_hazard_id

    created_library_hazard = await library_hazard_manager.add_library_hazard(
        library_hazard_data
    )
    await tenant_library_hazard_settings_manager.add_library_entities_for_tenants(
        primary_key_values=[library_hazard_id]
    )

    if not created_library_hazard:
        return ErrorResponse(404, "Not Found", "Not found")

    return LibraryHazardResponse.pack(  # type: ignore
        id=created_library_hazard.id,
        attributes=LibraryHazard(**created_library_hazard.dict()),
    )


@router.get(
    "/{library_hazard_id}",
    response_model=LibraryHazardResponse,
    status_code=200,
    tags=["library-hazards"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_hazard(
    library_hazard_id: uuid.UUID,
    library_hazard_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
) -> LibraryHazardResponse | ErrorResponse:  # type: ignore
    library_hazard = await library_hazard_manager.get_library_hazard(library_hazard_id)

    if not library_hazard:
        return ErrorResponse(404, "Not Found", "Not found")

    return LibraryHazardResponse.pack(  # type: ignore
        id=library_hazard.id,
        attributes=LibraryHazard(**library_hazard.dict()),
    )


@router.put(
    "/{library_hazard_id}",
    response_model=LibraryHazardResponse,
    status_code=200,
    tags=["library-hazards"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def edit_library_hazard(
    library_hazard_id: uuid.UUID,
    library_hazard: LibraryHazardRequest,  # type: ignore
    library_hazard_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
) -> LibraryHazardResponse | ErrorResponse:  # type: ignore
    library_hazard_data = LibraryHazardModel(
        **library_hazard.unpack().dict()  # type: ignore
    )
    library_hazard_data.id = library_hazard_id

    updated_library_hazard = await library_hazard_manager.update_library_hazard(
        library_hazard_id, library_hazard_data
    )

    if not updated_library_hazard:
        return ErrorResponse(404, "Not Found", "Not found")

    return LibraryHazardResponse.pack(  # type: ignore
        id=updated_library_hazard.id,
        attributes=LibraryHazard(**updated_library_hazard.dict()),
    )


@router.delete(
    "/{library_hazard_id}",
    status_code=204,
    tags=["library-hazards"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_library_hazards(
    library_hazard_id: uuid.UUID,
    library_hazard_manager: LibraryHazardManager = Depends(get_library_hazard_manager),
    tenant_library_hazard_settings_manager: TenantLibraryHazardSettingsManager = Depends(
        get_tenant_library_hazard_settings_manager
    ),
) -> (
    None
):  # can't include ErrorResponse as a return type as this conflicts with fastapi implementation of 204
    library_hazard = await library_hazard_manager.get_library_hazard(library_hazard_id)

    if not library_hazard:
        return ErrorResponse(404, "Not Found", "Not found")  # type: ignore

    await library_hazard_manager.archive_library_hazard(library_hazard_id)
    await tenant_library_hazard_settings_manager.delete_all_settings_by_id(
        primary_key_value=library_hazard_id
    )
