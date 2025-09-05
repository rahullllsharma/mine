import functools
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import (
    CreateCrewLeaderInput,
    Tenant,
    UpdateCrewLeaderInput,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_crew_leader_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(
    prefix="/crew-leaders",
    dependencies=[Depends(authenticate_integration)],
)

logger = get_logger(__name__)


class CrewLeaderAttributes(BaseModel):
    __entity_name__ = "crew-leader"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "crew-leaders")

    name: Optional[str] = Field(description="Crew Leader Name", default=None)
    lanid: Optional[str] = Field(description="", default=None)
    company_name: Optional[str] = Field(description="", default=None)
    created_at: Optional[datetime] = Field(description="Created at", default=None)


(
    CrewLeaderRequest,
    CrewLeaderBulkRequest,
    CrewLeaderResponse,
    CrewLeaderBulkResponse,
    CrewLeaderPaginationResponse,
) = create_models(CrewLeaderAttributes)


@router.post(
    "",
    response_model=CrewLeaderResponse,
    status_code=201,
    tags=["crew-leaders"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_crew_leader(
    crew_leader_request: CrewLeaderRequest,  # type: ignore
    crew_leader_manager: CrewLeaderManager = Depends(get_crew_leader_manager),
    tenant: Tenant = Depends(get_tenant),
) -> CrewLeaderResponse | ErrorResponse:  # type: ignore
    try:
        data = crew_leader_request.unpack()  # type: ignore
        logger.info(f"input data for crew leader creation -- {data}")
        create_input = CreateCrewLeaderInput(**data.dict())
        created_crew_leader = await crew_leader_manager.create(
            input=create_input, tenant_id=tenant.id
        )
        crew_leader = CrewLeaderAttributes(**created_crew_leader.dict())
        logger.info("returning created crew leader...")
        return CrewLeaderResponse.pack(id=created_crew_leader.id, attributes=crew_leader)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating crew leader not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate crew leader")
        return ErrorResponse(400, "External Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating crew leader with attributes {crew_leader_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "",
    response_model=CrewLeaderBulkResponse,
    status_code=200,
    tags=["crew-leaders"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_crew_leaders(
    request: Request,
    crew_leader_manager: CrewLeaderManager = Depends(get_crew_leader_manager),
    tenant: Tenant = Depends(get_tenant),
    limit: int = Query(default=40, alias="page[limit]"),
    offset: int = Query(default=0, alias="page[offset]"),
) -> CrewLeaderBulkResponse | ErrorResponse:  # type: ignore
    try:
        db_crew_leaders = await crew_leader_manager.get_all(
            tenant_id=tenant.id, limit=limit, offset=offset
        )
        crew_leaders = [
            (crew_leader.id, CrewLeaderAttributes(**crew_leader.dict()))
            for crew_leader in db_crew_leaders
        ]
        meta = PaginationMetaData(limit=limit)

        return CrewLeaderPaginationResponse.pack_many(  # type: ignore
            elements=crew_leaders,
            paginated_links=create_pagination_links(
                None, limit, request.url, crew_leaders
            ),
            pagination_meta=meta,
        )
    except Exception:
        logger.exception("Error getting crew_leaders")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{crew_leader_id}",
    response_model=CrewLeaderResponse,
    status_code=200,
    tags=["crew-leaders"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_crew_leader(
    crew_leader_id: UUID,
    crew_leader_update: CrewLeaderRequest,  # type: ignore
    tenant: Tenant = Depends(get_tenant),
    crew_leader_manager: CrewLeaderManager = Depends(get_crew_leader_manager),
) -> CrewLeaderResponse | ErrorResponse:  # type: ignore
    try:
        data: CrewLeaderAttributes = crew_leader_update.unpack()  # type: ignore
        logger.info(f"input data for crew leader update -- {data}")
        update_input = UpdateCrewLeaderInput(
            **data.dict(),
            tenant_id=tenant.id,
        )
        updated_crew_leader_db = await crew_leader_manager.update(
            id=crew_leader_id, input=update_input, tenant_id=tenant.id
        )
        updated_crew_leader = CrewLeaderAttributes(**updated_crew_leader_db.dict())
        return CrewLeaderResponse.pack(id=updated_crew_leader_db.id, attributes=updated_crew_leader)  # type: ignore
    except ResourceReferenceException as e:
        return ErrorResponse(400, "crew leader not found", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate crew leader")
        return ErrorResponse(400, "External Key already in use", str(e))
    except Exception:
        logger.exception(f"Error updating crew leader for {crew_leader_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{crew_leader_id}",
    response_model=None,
    status_code=204,
    tags=["crew-leaders"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def archive_crew_leader(
    crew_leader_id: UUID,
    crew_leader_manager: CrewLeaderManager = Depends(get_crew_leader_manager),
    tenant: Tenant = Depends(get_tenant),
) -> bool | ErrorResponse:
    try:
        return await crew_leader_manager.archive(id=crew_leader_id, tenant_id=tenant.id)
    except ResourceReferenceException as e:
        logger.exception(e)
        return ErrorResponse(400, "crew leader not found", str(e))
    except Exception as e:
        logger.exception(e)
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
