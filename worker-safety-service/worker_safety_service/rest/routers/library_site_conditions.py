import functools
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsManager,
)
from worker_safety_service.keycloak import authenticate_integration
from worker_safety_service.models import (
    LibrarySiteCondition as LibrarySiteConditionModel,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection import (
    get_library_site_condition_manager,
    get_tenant_library_site_condition_settings_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links

LIBRARY_SITE_CONDITION_PREFIX = "/library-site-conditions"
LIBRARY_SITE_CONDITION_ROUTE = (
    f"http://127.0.0.1:8000/rest{LIBRARY_SITE_CONDITION_PREFIX}"
)

router = APIRouter(
    prefix=LIBRARY_SITE_CONDITION_PREFIX,
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class LibrarySiteConditionAttributes(BaseModel):
    __entity_name__ = "library-site-conditions"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "library-site-conditions"
    )

    id: uuid.UUID = Field(description="ID")
    name: str = Field(description="Name of Site Condition")
    handle_code: str = Field(
        description="Used to identify the code handler for this site condition"
    )
    default_multiplier: float | None = Field(
        description="Default multiplier for this site condition", default=0
    )
    archived_at: datetime | None = Field(description="Archived At", default=None)

    recommended_hazards_ids: list[uuid.UUID] = Field(
        default_factory=list,
        relationship=RelationshipFieldAttributes(
            type="library-site-condition-hazards-recommendation",
            url_supplier=functools.partial(
                entity_array_url_supplier,
                "library-site-condition-hazards-recommendations",
                "library-site-condition",
            ),
        ),
    )


(
    LibrarySiteConditionRequest,
    LibrarySiteConditionBulkRequest,
    LibrarySiteConditionResponse,
    _,
    LibrarySiteConditionPaginationResponse,
) = create_models(LibrarySiteConditionAttributes)


@router.get(
    "",
    response_model=LibrarySiteConditionPaginationResponse,
    status_code=200,
    tags=["library-site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_site_conditions(
    request: Request,
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
    ids: Optional[list[uuid.UUID]] = Query(default=None, alias="filter[ids]"),
    library_site_conditions_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
) -> LibrarySiteConditionPaginationResponse | ErrorResponse:  # type: ignore
    try:
        lsc = await library_site_conditions_manager.get_library_site_conditions(
            after=after, limit=limit, ids=ids, use_seek_pagination=True
        )
    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")

    library_site_conditions = [
        (
            library_site_condition.id,
            LibrarySiteConditionAttributes(**library_site_condition.dict()),
        )
        for library_site_condition in lsc
    ]

    meta = PaginationMetaData(limit=limit)

    return LibrarySiteConditionPaginationResponse.pack_many(  # type: ignore
        elements=library_site_conditions,
        paginated_links=create_pagination_links(
            after, limit, request.url, library_site_conditions
        ),
        pagination_meta=meta,
    )


@router.post(
    "/{library_site_condition_id}",
    response_model=LibrarySiteConditionResponse,
    status_code=201,
    tags=["library-site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_library_site_condition(
    library_site_condition_id: uuid.UUID,
    library_site_condition: LibrarySiteConditionRequest,  # type: ignore
    library_site_condition_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
    tenant_library_sc_settings_manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> LibrarySiteConditionResponse | ErrorResponse:  # type: ignore
    library_site_condition_data = LibrarySiteConditionModel(
        **library_site_condition.unpack().dict()  # type: ignore
    )
    library_site_condition_data.id = library_site_condition_id

    try:
        created_library_site_condition = (
            await library_site_condition_manager.add_library_site_condition(
                library_site_condition_data
            )
        )
        await tenant_library_sc_settings_manager.add_library_entities_for_tenants(
            primary_key_values=[library_site_condition_id]
        )

        if not created_library_site_condition:
            return ErrorResponse(404, "Not Found", "Not found")

    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")

    return LibrarySiteConditionResponse.pack(  # type: ignore
        id=created_library_site_condition.id,
        attributes=LibrarySiteConditionAttributes(
            **created_library_site_condition.dict()
        ),
    )


@router.get(
    "/{library_site_condition_id}",
    response_model=LibrarySiteConditionResponse,
    status_code=200,
    tags=["library-site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_library_site_condition(
    library_site_condition_id: uuid.UUID,
    library_site_condition_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
) -> LibrarySiteConditionResponse | ErrorResponse:  # type: ignore
    try:
        library_site_condition = (
            await library_site_condition_manager.get_library_site_condition(
                library_site_condition_id
            )
        )
    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")

    if not library_site_condition:
        return ErrorResponse(404, "Not Found", "Not found")

    return LibrarySiteConditionResponse.pack(  # type: ignore
        id=library_site_condition.id,
        attributes=LibrarySiteConditionAttributes(**library_site_condition.dict()),
    )


@router.put(
    "/{library_site_condition_id}",
    response_model=LibrarySiteConditionResponse,
    status_code=200,
    tags=["library-site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def edit_library_site_condition(
    library_site_condition_id: uuid.UUID,
    library_site_condition: LibrarySiteConditionRequest,  # type: ignore
    library_site_condition_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
) -> LibrarySiteConditionResponse | ErrorResponse:  # type: ignore
    library_site_condition_data = LibrarySiteConditionModel(
        **library_site_condition.unpack().dict()  # type: ignore
    )
    library_site_condition_data.id = library_site_condition_id

    try:
        updated_library_site_condition = (
            await library_site_condition_manager.edit_library_site_condition(
                library_site_condition_id, library_site_condition_data
            )
        )

        if not updated_library_site_condition:
            return ErrorResponse(404, "Not Found", "Not found")

    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")

    return LibrarySiteConditionResponse.pack(  # type: ignore
        id=updated_library_site_condition.id,
        attributes=LibrarySiteConditionAttributes(
            **updated_library_site_condition.dict()
        ),
    )


@router.delete(
    "/{library_site_condition_id}",
    status_code=204,
    tags=["library-site-conditions"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_library_site_condition(
    library_site_condition_id: uuid.UUID,
    library_site_condition_manager: LibrarySiteConditionManager = Depends(
        get_library_site_condition_manager
    ),
    tenant_library_sc_settings_manager: TenantLibrarySiteConditionSettingsManager = Depends(
        get_tenant_library_site_condition_settings_manager
    ),
) -> (
    None
):  # can't include ErrorResponse as a return type as this conflicts with fastapi implementation of 204
    try:
        library_site_condition = (
            await library_site_condition_manager.get_library_site_condition(
                library_site_condition_id
            )
        )

        if not library_site_condition:
            return ErrorResponse(404, "Not Found", "Not found")  # type: ignore

        await library_site_condition_manager.archive_library_site_condition(
            library_site_condition_id
        )
        await tenant_library_sc_settings_manager.delete_all_settings_by_id(
            primary_key_value=library_site_condition_id
        )

    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")  # type: ignore
