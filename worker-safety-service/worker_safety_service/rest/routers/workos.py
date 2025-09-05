import functools
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.dal.workos import WorkOSManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.permissions import CanConfigureTheApplication
from worker_safety_service.keycloak import IsAuthorized
from worker_safety_service.models import WorkOSCreateInput, WorkOSUpdateInput
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import get_workos_manager
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.urbint_logging import get_logger

can_configure_app = IsAuthorized(CanConfigureTheApplication)

router = APIRouter(prefix="/workos")

logger = get_logger(__name__)


class WorkOSAttributes(BaseModel):
    __entity_name__ = "workos"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "workos")

    tenant_id: Optional[UUID] = Field(description="WorkOS tenant id", default=None)
    workos_org_id: Optional[str] = Field(description="WorkOS org id", default=None)
    workos_directory_id: Optional[str] = Field(
        description="WorkOS directory id", default=None
    )


(
    WorkOSRequest,
    WorkOSBulkRequest,
    WorkOSResponse,
    WorkOSBulkResponse,
    WorkOSPaginationResponse,
) = create_models(WorkOSAttributes)

ERROR_500_TITLE = "An exception has occurred"
ERROR_500_DETAIL = "An exception has occurred"


@router.post(
    "",
    response_model=WorkOSResponse,
    status_code=201,
    tags=["workos"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def create_workos(
    workos_request: WorkOSRequest,  # type: ignore
    workos_manager: WorkOSManager = Depends(get_workos_manager),
) -> WorkOSResponse | ErrorResponse:  # type: ignore
    try:
        data = workos_request.unpack()  # type: ignore
        logger.info(f"input data for workos creation -- {data}")
        create_input = WorkOSCreateInput(**data.dict())
        created_workos = await workos_manager.create_workos(input=create_input)
        workos = WorkOSAttributes(**created_workos.dict())
        logger.info("returning created workos...")
        return WorkOSResponse.pack(id=created_workos.id, attributes=workos)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating workos not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except EntityAlreadyExistsException as e:
        logger.exception("Duplicate workos")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating workos with attributes {workos_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{workos_id}",
    response_model=WorkOSResponse,
    status_code=200,
    tags=["workos"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def update_workos(
    workos_id: UUID,
    workos_update: WorkOSRequest,  # type: ignore
    workos_manager: WorkOSManager = Depends(get_workos_manager),
) -> WorkOSResponse | ErrorResponse:  # type: ignore
    try:
        data: WorkOSAttributes = workos_update.unpack()  # type: ignore
        logger.info(f"input data for workos update -- {data}")
        update_input = WorkOSUpdateInput(**data.dict())
        updated_workos_db = await workos_manager.update_workos(
            id=workos_id, input=update_input
        )
        updated_workos = WorkOSAttributes(**updated_workos_db.dict())
        return WorkOSResponse.pack(id=updated_workos_db.id, attributes=updated_workos)  # type: ignore
    except ResourceReferenceException as e:
        return ErrorResponse(400, "WorkOS not found", str(e))
    except EntityAlreadyExistsException as e:
        logger.exception("Duplicate workos")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(f"Error updating workos for {workos_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{workos_id}",
    response_model=None,
    status_code=204,
    tags=["workos"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_configure_app)],
)
async def delete_workos(
    workos_id: UUID,
    workos_manager: WorkOSManager = Depends(get_workos_manager),
) -> None | ErrorResponse:
    try:
        await workos_manager.delete(entity_id=workos_id)
        return None
    except ResourceReferenceException as e:
        return ErrorResponse(400, "WorkOS not found", str(e))
    except Exception:
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
