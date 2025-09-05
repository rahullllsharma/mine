import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_controls import LibraryControlManager
from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models.library import LibraryControl as DBLibraryControl
from worker_safety_service.models.library import (
    OSHAControlsClassification,
    TypeOfControl,
)
from worker_safety_service.rest.api_models.empty_response import EmptyResponse
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection import (
    get_library_control_manager,
    get_tenant_library_control_settings_manager,
)
from worker_safety_service.rest.exception_handlers import (
    EntityNotFoundResponse,
    ErrorResponse,
)
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links

router = APIRouter(dependencies=[Depends(authenticate_integration)])

logger = get_logger(__name__)


class LibraryControl(BaseModel):
    __entity_name__ = "library-control"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "library-controls")

    name: str = Field(description="Name of Control")
    for_tasks: bool = Field(description="Is this Control for a Task")
    for_site_conditions: bool = Field(
        description="Is this Control for a Site Condition"
    )
    ppe: Optional[bool] = Field(
        default=None, description="TODO: Not sure what this is ATM."
    )
    type: Optional[TypeOfControl] = Field(
        default=None, description="TODO: Not sure what this is ATM."
    )
    osha_classification: Optional[OSHAControlsClassification] = Field(
        default=None, description="OSHA Classification for the Control."
    )


(
    LibraryControlRequest,
    LibraryControlBulkRequest,
    LibraryControlResponse,
    _,
    LibraryControlPaginationResponse,
) = create_models(LibraryControl)


@router.get(
    "/library-controls",
    response_model=LibraryControlPaginationResponse,
    status_code=200,
    tags=["library-controls"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_controls(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=10, alias="page[limit]"),
    ids: Optional[list[uuid.UUID]] = Query(default=None, alias="filter[ids]"),
    library_hazard_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library_hazard]"
    ),
    library_site_condition_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library_site_condition]"
    ),
    library_task_ids: Optional[list[uuid.UUID]] = Query(
        default=None, alias="filter[library_task]"
    ),
    library_control_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
) -> LibraryControlPaginationResponse | ErrorResponse:  # type: ignore
    lc = await library_control_manager.get_library_controls(
        ids=ids,
        library_hazard_ids=library_hazard_ids,
        library_site_condition_ids=library_site_condition_ids,
        library_task_ids=library_task_ids,
        after=after,
        limit=limit,
        use_seek_pagination=True,
    )

    library_controls = [
        (
            library_control.id,
            LibraryControl(**library_control.dict()),
        )
        for library_control in lc
    ]

    meta = PaginationMetaData(limit=limit)

    return LibraryControlPaginationResponse.pack_many(  # type: ignore
        elements=library_controls,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_controls
        ),
        pagination_meta=meta,
    )


@router.post(
    "/library-controls/{library_control_id}",
    response_model=EmptyResponse,
    status_code=201,
    tags=["library-controls"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_library_control(
    library_control_id: uuid.UUID,
    library_control_request: LibraryControlRequest,  # type: ignore
    library_control_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
    tenant_library_control_settings_manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> EmptyResponse:
    req: LibraryControl = library_control_request.unpack()  # type: ignore
    to_create = DBLibraryControl(
        id=library_control_id,
        name=req.name,
        for_tasks=req.for_tasks,
        for_site_conditions=req.for_site_conditions,
        ppe=req.ppe,
        type=req.type,
        osha_classification=req.osha_classification,
    )

    await library_control_manager.create(to_create)
    await tenant_library_control_settings_manager.add_library_entities_for_tenants(
        primary_key_values=[library_control_id]
    )
    return EmptyResponse()


@router.get(
    "/library-controls/{library_control_id}",
    response_model=LibraryControlResponse,
    status_code=200,
    tags=["library-controls"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_control(
    library_control_id: uuid.UUID,
    library_control_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
) -> LibraryControlResponse | ErrorResponse:  # type: ignore
    lc = await library_control_manager.get_by_id(library_control_id)
    if lc is None:
        return EntityNotFoundResponse(
            LibraryControl.__entity_name__, library_control_id
        )

    resp = DBLibraryControl(
        id=library_control_id,
        name=lc.name,
        for_tasks=lc.for_tasks,
        for_site_conditions=lc.for_site_conditions,
        ppe=lc.ppe,
        type=lc.type,
        osha_classification=lc.osha_classification,
    )

    return LibraryControlResponse.pack(lc.id, resp)  # type: ignore


@router.put(
    "/library-controls/{library_control_id}",
    response_model=LibraryControlResponse,
    status_code=200,
    tags=["library-controls"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def edit_library_control(
    library_control_id: uuid.UUID,
    library_control_request: LibraryControlRequest,  # type: ignore
    library_control_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
) -> LibraryControlResponse | ErrorResponse:  # type: ignore
    req: LibraryControl = library_control_request.unpack()  # type: ignore
    to_update = DBLibraryControl(
        id=library_control_id,
        name=req.name,
        for_tasks=req.for_tasks,
        for_site_conditions=req.for_site_conditions,
        ppe=req.ppe,
        type=req.type,
        osha_classification=req.osha_classification,
    )

    await library_control_manager.update(to_update)
    actual_entity = await library_control_manager.get_by_id(library_control_id)
    assert actual_entity

    return LibraryControlResponse.pack(  # type: ignore
        library_control_id,
        LibraryControl(
            name=actual_entity.name,
            for_tasks=actual_entity.for_tasks,
            for_site_conditions=actual_entity.for_site_conditions,
            ppe=actual_entity.ppe,
            type=actual_entity.type,
            osha_classification=actual_entity.osha_classification,
        ),
    )


@router.delete(
    "/library-controls/{library_control_id}",
    status_code=204,
    tags=["library-controls"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_library_controls(
    library_control_id: uuid.UUID,
    library_control_manager: LibraryControlManager = Depends(
        get_library_control_manager
    ),
    tenant_library_control_settings_manager: TenantLibraryControlSettingsManager = Depends(
        get_tenant_library_control_settings_manager
    ),
) -> None:
    await library_control_manager.archive(library_control_id)
    await tenant_library_control_settings_manager.delete_all_settings_by_id(
        primary_key_value=library_control_id
    )
