import functools

from fastapi import APIRouter, Depends, Request
from pydantic import ValidationError

from worker_safety_service.config import settings
from worker_safety_service.dal.feature_flag import FeatureFlagManager
from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.graphql.permissions import CanGetFeatureFlagDetails
from worker_safety_service.keycloak import (
    IsAuthorized,
    authenticate_integration,
    get_tenant,
)
from worker_safety_service.launch_darkly import (
    LaunchDarklyClient,
    get_launch_darkly_client,
)
from worker_safety_service.models import (
    FeatureFlagAttributesBase,
    FeatureFlagCreateInput,
    FeatureFlagUpdateInput,
    Tenant,
)
from worker_safety_service.rest.api_models.new_jsonapi import (
    PaginationMetaData,
    create_models,
)
from worker_safety_service.rest.dependency_injection.managers import (
    get_feature_flag_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers import query_params
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.rest.routers.utils.error_codes import (
    ERROR_500_DETAIL,
    ERROR_500_TITLE,
)
from worker_safety_service.rest.routers.utils.pagination import create_pagination_links
from worker_safety_service.urbint_logging import get_logger

can_get_feature_flag_details = IsAuthorized(CanGetFeatureFlagDetails)
router = APIRouter(prefix="/feature-flags")

logger = get_logger(__name__)


class FeatureFlagAttributes(FeatureFlagAttributesBase):
    __entity_name__ = "feature-flag"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "feature-flag")


(
    FeatureFlagRequest,
    FeatureFlagBulkRequest,
    FeatureFlagResponse,
    FeatureFlagBulkResponse,
    FeatureFlagPaginationResponse,
) = create_models(FeatureFlagAttributes)


@router.post(
    "",
    response_model=FeatureFlagResponse,
    status_code=201,
    tags=["feature-flags"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(authenticate_integration)],
    deprecated=True,
)
async def create_feature_flag(
    feature_flag_request: FeatureFlagRequest,  # type: ignore
    feature_flag_manager: FeatureFlagManager = Depends(get_feature_flag_manager),
) -> FeatureFlagResponse | ErrorResponse:  # type: ignore
    try:
        data: FeatureFlagAttributes = feature_flag_request.unpack()  # type: ignore
        logger.info(f"input data for feature_flag creation -- {data}")
        create_input = FeatureFlagCreateInput(**data.dict())
        created_feature_flag = await feature_flag_manager.create_feature_flag(
            input=create_input
        )
        feature_flag = FeatureFlagAttributes(**created_feature_flag.dict())
        logger.info("returning created feature_flag...")
        return FeatureFlagResponse.pack(id=created_feature_flag.id, attributes=feature_flag)  # type: ignore
    except ValidationError as e:
        logger.exception("Inputs provided for creating Feature Flagging not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate Feature Flag")
        return ErrorResponse(400, "Key already in use", str(e))
    except Exception:
        logger.exception(
            f"Error creating feature_flag with attributes {feature_flag_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.put(
    "/{feature_name}",
    response_model=FeatureFlagResponse,
    status_code=200,
    tags=["feature-flags"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(authenticate_integration)],
    deprecated=True,
)
async def update_feature_flag(
    feature_name: str,
    feature_flag_update: FeatureFlagRequest,  # type: ignore
    feature_flag_manager: FeatureFlagManager = Depends(get_feature_flag_manager),
) -> FeatureFlagResponse | ErrorResponse:  # type: ignore
    try:
        data: FeatureFlagAttributes = feature_flag_update.unpack()  # type: ignore
        logger.info(f"input data for feature_flag update -- {data}")
        update_input = FeatureFlagUpdateInput(**data.dict())
        updated_feature_flag_db = await feature_flag_manager.update_feature_flag(
            feature_name=feature_name, input=update_input
        )
        updated_feature_flag = FeatureFlagAttributes(**updated_feature_flag_db.dict())
        return FeatureFlagResponse.pack(  # type: ignore
            id=updated_feature_flag_db.id,
            attributes=updated_feature_flag,
        )
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Feature Flag not found", str(e))
    except DuplicateKeyException as e:
        logger.exception("Duplicate Feature Flag")
        return ErrorResponse(400, "Key already in use", str(e))
    except ValueError as e:
        logger.exception("Inputs provided for creating Feature Flagging not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(f"Error updating Feature Flag for {feature_name}")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "",
    response_model=FeatureFlagPaginationResponse,
    status_code=200,
    tags=["feature-flags"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_get_feature_flag_details)],
    deprecated=True,
)
async def get_feature_flag(
    request: Request,
    feature_names: list[str] = query_params.feature_names,
    limit: int = query_params.limit,
    feature_flag_manager: FeatureFlagManager = Depends(get_feature_flag_manager),
    tenant: Tenant = Depends(get_tenant),
    launch_darkly_client: LaunchDarklyClient = Depends(get_launch_darkly_client),
) -> FeatureFlagPaginationResponse | ErrorResponse:  # type: ignore
    try:
        feature_flag_dicts = await feature_flag_manager.get_configs_from_ld(
            feature_names=feature_names,
            tenant_key=tenant.tenant_name.lower().replace(" ", "_"),
            launch_darkly_client=launch_darkly_client,
        )
        feature_flags = [
            (feature_flag_dict["id"], FeatureFlagAttributes(**feature_flag_dict))
            for feature_flag_dict in feature_flag_dicts
        ]
        meta = PaginationMetaData(limit=limit)
        links = create_pagination_links(
            after=None, limit=limit, url=request.url, elements=feature_flags
        )

        return FeatureFlagPaginationResponse.pack_many(elements=feature_flags, paginated_links=links, pagination_meta=meta)  # type: ignore
    except ResourceReferenceException as e:
        return ErrorResponse(400, "Feature Flag not found", str(e))
    except RuntimeError as e:
        return ErrorResponse(400, "Error fetching feature flag", str(e))
    except Exception:
        logger.exception(f"Error getting Feature Flag with names '{feature_names}'")
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)


@router.get(
    "/mobile-key",
    status_code=200,
    tags=["feature-flags"],
    openapi_extra={"security": [{"OAuth2": []}]},
    dependencies=[Depends(can_get_feature_flag_details)],
)
async def get_mobile_sdk_key(request: Request) -> str:
    return settings.LAUNCH_DARKLY_MOBILE_KEY
