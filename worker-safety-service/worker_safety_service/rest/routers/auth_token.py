import functools
import uuid

from fastapi import APIRouter, Depends

from worker_safety_service.keycloak import get_parsed_token, get_tenant
from worker_safety_service.keycloak.utils import (
    RealmDetails,
    get_realm_details,
    get_token,
    get_token_details,
)
from worker_safety_service.models import TokenDetailsWithPermissions
from worker_safety_service.models.tenants import Tenant
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import ERROR_500_TITLE
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth_token")


class ParsedTokenAttributes(TokenDetailsWithPermissions):
    __entity_name__ = "parsed_token"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "parsed_token")


(_, _, ParsedTokenResponse, _, _) = create_models(ParsedTokenAttributes)


@router.post(
    "/validate-and-parse-token",
    response_model=ParsedTokenResponse,
    status_code=201,
    deprecated=True,
)
async def validate_and_parse_token(
    parsed_auth_token: dict = Depends(get_parsed_token),
    realm_details: RealmDetails = Depends(get_realm_details),
) -> ParsedTokenResponse | ErrorResponse:  # type: ignore
    try:
        token_details = await get_token_details(
            parsed_auth_token=parsed_auth_token,
            realm_details=realm_details,
        )
        token_details_dict = ParsedTokenAttributes(**token_details.dict())
        return ParsedTokenResponse.pack(id=uuid.uuid4(), attributes=token_details_dict)  # type: ignore
    except Exception as e:
        logger.exception("Error validating token")
        return ErrorResponse(500, ERROR_500_TITLE, str(e))


@router.post("/validate-token", response_model=ParsedTokenResponse, status_code=201)
async def validate_token(
    parsed_auth_token: dict = Depends(get_parsed_token),
    realm_details: RealmDetails = Depends(get_realm_details),
    tenant: Tenant = Depends(get_tenant),
) -> ParsedTokenResponse | ErrorResponse:  # type: ignore
    try:
        token_details = await get_token(
            parsed_auth_token=parsed_auth_token,
            realm_details=realm_details,
            tenant=tenant,
        )
        attributes = ParsedTokenAttributes(**token_details.dict())
        return ParsedTokenResponse.pack(id=uuid.uuid4(), attributes=attributes)  # type: ignore
    except Exception as e:
        logger.exception("Error validating token")
        return ErrorResponse(500, ERROR_500_TITLE, str(e))
