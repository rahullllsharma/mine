import functools
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.department_manager import DepartmentManager
from worker_safety_service.exceptions import DuplicateKeyException
from worker_safety_service.graphql.permissions import CanConfigureOpcoAndDepartment
from worker_safety_service.keycloak import IsAuthorized
from worker_safety_service.models import Department as DepartmentModel
from worker_safety_service.models import DepartmentCreate
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_department_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_array_url_supplier,
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links
from worker_safety_service.urbint_logging import get_logger

can_configure_opco_and_department = IsAuthorized(CanConfigureOpcoAndDepartment)
router = APIRouter(
    prefix="/departments", dependencies=[Depends(can_configure_opco_and_department)]
)

logger = get_logger(__name__)


class DepartmentAttributes(BaseModel):
    __entity_name__ = "department"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "departments")

    opco_id: UUID = Field(
        relationship=RelationshipFieldAttributes(
            type="opco",
            url_supplier=functools.partial(
                entity_array_url_supplier, "opco", "department"
            ),
        ),
        description="Opco ID",
    )

    name: str = Field(description="Department Name", default="")
    created_at: Optional[datetime] = Field(description="Created at", default=None)


(
    DepartmentRequest,
    DepartmentBulkRequest,
    DepartmentResponse,
    DepartmentBulkResponse,
    DepartmentPaginationResponse,
) = create_models(DepartmentAttributes)


@router.post(
    "",
    response_model=DepartmentResponse,
    status_code=201,
    tags=["departments"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_department(
    department_request: DepartmentRequest,  # type: ignore
    department_manager: DepartmentManager = Depends(get_department_manager),
) -> DepartmentResponse | ErrorResponse:  # type: ignore
    try:
        data = department_request.unpack()  # type: ignore
        logger.info(f"input data for department creation -- {data}")
        create_input = DepartmentCreate(**data.dict())
        created_department = await department_manager.create_department(
            input=create_input
        )
        department = DepartmentAttributes(**created_department.dict())
        logger.info("returning created department...")
        return DepartmentResponse.pack(id=created_department.id, attributes=department)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating departments not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate department")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating department with attributes {department_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "",
    response_model=DepartmentPaginationResponse,
    status_code=200,
    tags=["department"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_departments(
    request: Request,
    opco_id: Optional[UUID] = None,
    department_manager: DepartmentManager = Depends(get_department_manager),
    limit: int = Query(default=10, alias="page[limit]"),
    after: Optional[UUID] = Query(
        default=None,
        alias="page[after]",
    ),
) -> DepartmentPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_departments = await department_manager.get_all_departments(
            opco_id=opco_id, limit=limit, after=after
        )
        departments = [
            (department.id, DepartmentAttributes(**department.dict()))
            for department in db_departments
        ]
        meta = PaginationMetaData(limit=limit)

        return DepartmentPaginationResponse.pack_many(  # type: ignore
            elements=departments,
            paginated_links=create_pagination_links(
                after, limit, request.url, departments
            ),
            pagination_meta=meta,
        )
    except Exception:
        logger.exception(f"Error getting departments for {opco_id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{department_id}",
    response_model=DepartmentResponse,
    status_code=200,
    tags=["departments"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_department(
    department_id: UUID,
    department_request: DepartmentRequest,  # type: ignore
    department_manager: DepartmentManager = Depends(get_department_manager),
) -> DepartmentResponse | ErrorResponse:  # type: ignore
    try:
        data = department_request.unpack()  # type: ignore
        logger.info(f"input data for department update -- {data}")
        update_input = DepartmentModel(**data.dict(), id=department_id)
        updated_department = await department_manager.edit_department(update_input)
        if updated_department is None:
            raise Exception
        department = DepartmentAttributes(**updated_department.dict())
        logger.info("returning updated department...")
        return DepartmentResponse.pack(id=updated_department.id, attributes=department)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for updating departments not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error updating department with attributes {department_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{department_id}",
    status_code=204,
    tags=["departments"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_department(
    department_id: UUID,
    department_manager: DepartmentManager = Depends(get_department_manager),
) -> None:
    try:
        department = await department_manager.get_by_id(department_id)

        if not department:
            return ErrorResponse(404, "Not Found", "Not found")  # type: ignore

        department_delete = await department_manager.delete_department(department_id)

        if department_delete.error:
            return ErrorResponse(409, "Error", department_delete.error)  # type: ignore

    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")  # type: ignore
