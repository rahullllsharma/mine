import functools
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Query, Request

from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import Tenant
from worker_safety_service.models.standard_operating_procedures import (
    StandardOperatingProcedure,
    StandardOperatingProcedureBase,
)
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import (
    get_standard_operating_procedure_manager,
)
from worker_safety_service.rest.exception_handlers import (
    EntityNotFoundResponse,
    ErrorResponse,
)
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links
from worker_safety_service.urbint_logging import get_logger

router = APIRouter(dependencies=[Depends(authenticate_integration)])

logger = get_logger(__name__)


TAG = "Standard Operating Procedures"


class StandardOperatingProcedureAttributes(StandardOperatingProcedureBase):
    __entity_name__ = "standard-operating-procedure"
    __entity_url_supplier__ = functools.partial(
        entity_url_supplier, "standard-operating-procedures"
    )


(
    StandardOperatingProcedureRequest,
    _,
    StandardOperatingProcedureResponse,
    _,
    StandardOperatingProcedurePaginationResponse,
) = create_models(StandardOperatingProcedureAttributes)


@router.post(
    "/standard-operating-procedures",
    response_model=StandardOperatingProcedureResponse,
    status_code=201,
    tags=[TAG],
)
async def create_standard_operating_procedure(
    request: StandardOperatingProcedureRequest,  # type: ignore
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> StandardOperatingProcedureResponse | ErrorResponse:  # type: ignore
    """Create a new standard operating procedure"""
    try:
        standard_operating_procedure = await manager.create(
            StandardOperatingProcedure(**request.unpack().dict(), tenant_id=tenant.id)  # type: ignore
        )
        return StandardOperatingProcedureResponse.pack(  # type: ignore
            id=standard_operating_procedure.id, attributes=standard_operating_procedure
        )
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error creating standard operating procedure with attributes {request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/standard-operating-procedures",
    response_model=StandardOperatingProcedurePaginationResponse,
    status_code=200,
    tags=[TAG],
)
async def get_standard_operating_procedures(
    request: Request,
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
    after: Optional[uuid.UUID] = Query(
        default=None,
        alias="page[after]",
    ),
    limit: int = Query(default=20, le=200, ge=1, alias="page[limit]"),
) -> StandardOperatingProcedureResponse | ErrorResponse:  # type: ignore
    """
    Get a paginated list of Standard Operating Procedures.
    """
    elements = [
        (
            standard_operating_procedure.id,
            StandardOperatingProcedureAttributes(**standard_operating_procedure.dict()),
        )
        for standard_operating_procedure in (
            await manager.get_all(
                tenant_id=tenant.id,
                after=after,
                limit=limit,
            )
        )
    ]
    return StandardOperatingProcedurePaginationResponse.pack_many(  # type: ignore
        elements,
        paginated_links=create_pagination_links(
            after=after, limit=limit, url=request.url, elements=elements
        ),
        pagination_meta=None,
    )


@router.get(
    "/standard-operating-procedures/{standard_operating_procedure_id}",
    response_model=StandardOperatingProcedureResponse,
    status_code=200,
    tags=[TAG],
)
async def get_standard_operating_procedure_by_id(
    standard_operating_procedure_id: uuid.UUID,
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> StandardOperatingProcedureResponse | ErrorResponse:  # type: ignore
    """
    Get Standard Operating Procedure by id
    """
    standard_operating_procedure = await manager.get_by_id(
        id=standard_operating_procedure_id, tenant_id=tenant.id
    )
    if not standard_operating_procedure:
        return EntityNotFoundResponse(
            "StandardOperatingProcedure",
            standard_operating_procedure_id,
        )
    return StandardOperatingProcedureResponse.pack(  # type: ignore
        standard_operating_procedure.id,
        StandardOperatingProcedureAttributes(**standard_operating_procedure.dict()),
    )


@router.put(
    "/standard-operating-procedures/{standard_operating_procedure_id}",
    response_model=StandardOperatingProcedureResponse,
    status_code=200,
    tags=[TAG],
)
async def update_standard_operating_procedure(
    standard_operating_procedure_id: uuid.UUID,
    request: StandardOperatingProcedureRequest,  # type: ignore
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> StandardOperatingProcedureResponse | ErrorResponse:  # type: ignore
    """
    Allows update a Standard Operating Procedure.
    """
    try:
        await manager.check_standard_operating_procedure_exists(
            standard_operating_procedure_id, tenant.id
        )
        standard_operating_procedure = StandardOperatingProcedure(
            **request.unpack().dict(),  # type: ignore
            tenant_id=tenant.id,
            id=standard_operating_procedure_id,
        )
        await manager.update(standard_operating_procedure)
        return StandardOperatingProcedureResponse.pack(  # type: ignore
            id=standard_operating_procedure.id, attributes=standard_operating_procedure
        )
    except ValueError as e:
        return ErrorResponse(400, "Bad Input", str(e))
    except EntityNotFoundException as e:
        return EntityNotFoundResponse(e.entity_type.__name__, e.entity_id)
    except Exception:
        logger.exception(
            f"error updating standard operating procedure with attributes {request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/standard-operating-procedures/{standard_operating_procedure_id}",
    response_model=None,
    status_code=204,
    tags=[TAG],
)
async def delete_standard_operating_procedure(
    standard_operating_procedure_id: uuid.UUID,
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> None | ErrorResponse:
    """
    Deletes a given Standard Operating Procedure.
    It must not be assigned to any LibraryTasks.
    """
    try:
        await manager.delete(standard_operating_procedure_id, tenant.id)
        return None
    except EntityNotFoundException as e:
        return EntityNotFoundResponse(
            e.entity_type.__name__,
            e.entity_id,
        )
    except Exception:
        logger.exception(
            f"error deleting Standard Operating Procedure {standard_operating_procedure_id}"
        )
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")


@router.put(
    "/standard-operating-procedures/{standard_operating_procedure_id}/relationships/library-tasks/{library_task_id}",
    response_model=None,
    status_code=204,
    tags=[TAG],
)
async def link_standard_operating_procedure_to_library_task(
    standard_operating_procedure_id: uuid.UUID,
    library_task_id: uuid.UUID,
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> None | ErrorResponse:
    """
    Links a Standard Operating Procedure to a Library Task.
    """
    try:
        await manager.link_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=standard_operating_procedure_id,
            library_task_id=library_task_id,
            tenant_id=tenant.id,
        )
        return None
    except EntityNotFoundException as e:
        return EntityNotFoundResponse(
            e.entity_type.__name__,
            e.entity_id,
        )
    except Exception:
        logger.exception(
            "error creating Standard Operating Procedure link with library task"
        )
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")


@router.delete(
    "/standard-operating-procedures/{standard_operating_procedure_id}/relationships/library-tasks/{library_task_id}",
    response_model=None,
    status_code=204,
    tags=[TAG],
)
async def unlink_standard_operating_procedure_to_library_task(
    standard_operating_procedure_id: uuid.UUID,
    library_task_id: uuid.UUID,
    manager: StandardOperatingProcedureManager = Depends(
        get_standard_operating_procedure_manager
    ),
    tenant: Tenant = Depends(get_tenant),
) -> None | ErrorResponse:
    """
    Unlinks a Standard Operating Procedure to a Library Task.
    """
    try:
        await manager.unlink_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=standard_operating_procedure_id,
            library_task_id=library_task_id,
            tenant_id=tenant.id,
        )
        return None
    except EntityNotFoundException as e:
        return EntityNotFoundResponse(
            e.entity_type.__name__,
            e.entity_id,
        )
    except Exception:
        logger.exception(
            "error deleting Standard Operating Procedure link with library task"
        )
        return ErrorResponse(500, "An exception has occurred", "An exception occurred")
