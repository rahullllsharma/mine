import functools
import uuid

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import get_tenant_manager
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)

router = APIRouter(
    prefix="/realm-details",
)
logger = get_logger(__name__)


class RealmDetailsAttributes(BaseModel):
    __entity_name__ = "realm-detail"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "realm-details")

    realm_name: str = Field(description="The name of the realm in keycloak")
    client_id: str = Field(
        description="The client id to use to authenticate with the realm"
    )


(
    _,
    _,
    RealmDetailsResponse,
    _,
    _,
) = create_models(RealmDetailsAttributes)


@router.get(
    "",
    response_model=RealmDetailsResponse,
    openapi_extra={"security": []},
)
async def get_realm_details(
    name: str = Query(),
    tenant_manager: TenantManager = Depends(get_tenant_manager),
) -> RealmDetailsResponse | ErrorResponse:  # type: ignore
    """Get realm details"""
    try:
        realm_details = await tenant_manager.get_realm_details_by_tenant_name(name)

        return RealmDetailsResponse.pack(uuid.uuid4(), realm_details)  # type: ignore
    except ResourceReferenceException as e:
        logger.warning(str(e))
        return ErrorResponse(404, "Not Found", "Not found")
    except Exception:
        logger.exception(f"Error getting realm details for name: {name}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
