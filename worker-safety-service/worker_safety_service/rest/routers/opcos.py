import functools
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.opco_manager import OpcoManager
from worker_safety_service.exceptions import DuplicateKeyException
from worker_safety_service.graphql.permissions import CanConfigureOpcoAndDepartment
from worker_safety_service.keycloak import IsAuthorized, get_tenant
from worker_safety_service.models import Opco as OpcoModel
from worker_safety_service.models import OpcoCreate, Tenant
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    RelationshipFieldAttributes,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import get_opco_manager
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
    prefix="/opcos", dependencies=[Depends(can_configure_opco_and_department)]
)

logger = get_logger(__name__)


class OpcoAttributes(BaseModel):
    __entity_name__ = "opco"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "opcos")

    tenant_id: Optional[UUID] = Field(
        relationship=RelationshipFieldAttributes(
            type="tenant",
            url_supplier=functools.partial(entity_array_url_supplier, "tenant", "opco"),
        ),
        description="Tenant ID",
    )

    name: Optional[str] = Field(description="Opco Name", default=None)
    full_name: Optional[str] = Field(description="Opco Long Name", default=None)
    created_at: Optional[datetime] = Field(description="Created at", default=None)
    parent_id: Optional[UUID] = Field(description="Tenant_id", default=None)


(
    OpcoRequest,
    OpcoBulkRequest,
    OpcoResponse,
    OpcoBulkResponse,
    OpcoPaginationResponse,
) = create_models(OpcoAttributes)


@router.post(
    "",
    response_model=OpcoResponse,
    status_code=201,
    tags=["opcos"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_opco(
    opco_request: OpcoRequest,  # type: ignore
    opco_manager: OpcoManager = Depends(get_opco_manager),
) -> OpcoResponse | ErrorResponse:  # type: ignore
    try:
        data = opco_request.unpack()  # type: ignore
        logger.info(f"input data for opco creation -- {data}")
        create_input = OpcoCreate(**data.dict())
        created_opco = await opco_manager.create_opco(input=create_input)
        opco = OpcoAttributes(**created_opco.dict())
        logger.info("returning created opco...")
        return OpcoResponse.pack(id=created_opco.id, attributes=opco)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating opcos not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate Opco")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error creating opco with attributes {opco_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "",
    response_model=OpcoPaginationResponse,
    status_code=200,
    tags=["opcos"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_opcos(
    request: Request,
    tenant: Tenant = Depends(get_tenant),
    opco_manager: OpcoManager = Depends(get_opco_manager),
    limit: int = Query(default=10, alias="page[limit]"),
    after: Optional[UUID] = Query(
        default=None,
        alias="page[after]",
    ),
) -> OpcoPaginationResponse | ErrorResponse:  # type: ignore
    try:
        db_opcos = await opco_manager.get_all_opco(
            tenant_id=tenant.id, limit=limit, after=after
        )
        opcos = [(opco.id, OpcoAttributes(**opco.dict())) for opco in db_opcos]
        meta = PaginationMetaData(limit=limit)
        return OpcoPaginationResponse.pack_many(  # type: ignore
            elements=opcos,
            paginated_links=create_pagination_links(after, limit, request.url, opcos),
            pagination_meta=meta,
        )
    except Exception:
        logger.exception(f"Error getting opcos for {tenant.id}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{opco_id}",
    response_model=OpcoResponse,
    status_code=200,
    tags=["opcos"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def update_opco(
    opco_id: UUID,
    opco_request: OpcoRequest,  # type: ignore
    opco_manager: OpcoManager = Depends(get_opco_manager),
) -> OpcoResponse | ErrorResponse:  # type: ignore
    try:
        data = opco_request.unpack()  # type: ignore
        logger.info(f"input data for opco update -- {data}")
        update_input = OpcoModel(**data.dict(), id=opco_id)
        updated_opco = await opco_manager.edit_opco(update_input)
        if updated_opco is None:
            raise Exception
        opco = OpcoAttributes(**updated_opco.dict())
        logger.info("returning updated opco...")
        return OpcoResponse.pack(id=updated_opco.id, attributes=opco)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for updating opcos not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate Opco")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"error updating opco with attributes {opco_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.delete(
    "/{opco_id}",
    status_code=204,
    tags=["opcos"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def delete_opco(
    opco_id: UUID,
    opco_manager: OpcoManager = Depends(get_opco_manager),
) -> None:
    try:
        opco = await opco_manager.get_by_id(opco_id)

        if not opco:
            return ErrorResponse(404, "Not Found", "Not found")  # type: ignore

        opco_delete = await opco_manager.delete_opco(opco_id)

        if opco_delete.error:
            return ErrorResponse(409, "Error", opco_delete.error)  # type: ignore

    except Exception:
        return ErrorResponse(400, "Bad Request", "Bad request")  # type: ignore
