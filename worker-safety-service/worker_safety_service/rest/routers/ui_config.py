import functools
from copy import deepcopy
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from pydantic.error_wrappers import ValidationError

from worker_safety_service.dal.ui_config import UIConfigManager
from worker_safety_service.graphql.permissions import (
    CanConfigureTheApplication,
    CanReadReports,
)
from worker_safety_service.keycloak import IsAuthorized, get_tenant
from worker_safety_service.models import FormType, Tenant
from worker_safety_service.models.concepts import (
    DocumentsProvided,
    GeneralReferenceMaterial,
    UIConfigClearanceTypes,
    UIConfigEnergySourceControl,
    UIConfigEnergyWheelColors,
    UIConfigMinimumApproachDistances,
    UIConfigMinimumApproachDistancesLinks,
    UIConfigNotificationSettings,
    UIConfigPointsOfProtection,
    UIConfigStatusWorkflow,
)
from worker_safety_service.rest.api_models.new_jsonapi import create_models
from worker_safety_service.rest.dependency_injection.managers import (
    get_ui_config_manager,
)
from worker_safety_service.rest.exception_handlers import ErrorResponse
from worker_safety_service.rest.routers.utils.entity_url_supplier import (
    entity_url_supplier,
)
from worker_safety_service.urbint_logging import get_logger

# Route Permissions
can_read_location = IsAuthorized(CanReadReports)
can_configure_location = IsAuthorized(CanConfigureTheApplication)

router = APIRouter(prefix="/ui-config")

logger = get_logger(__name__)


class UIConfigContents(BaseModel):
    clearance_types: list[UIConfigClearanceTypes]
    status_workflow: list[UIConfigStatusWorkflow]
    documents_provided: list[DocumentsProvided]
    points_of_protection: list[UIConfigPointsOfProtection]
    energy_source_control: list[UIConfigEnergySourceControl]
    notification_settings: UIConfigNotificationSettings
    minimum_approach_distances: list[UIConfigMinimumApproachDistances]
    general_reference_materials: list[GeneralReferenceMaterial]
    minimum_approach_distances_links: list[UIConfigMinimumApproachDistancesLinks]
    energy_wheel_color: list[UIConfigEnergyWheelColors]


class UIConfigAttributes(BaseModel):
    contents: UIConfigContents | None
    form_type: FormType


class UIConfigAttribute(BaseModel):
    __entity_name__ = "ui_config"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "ui_config")

    id: UUID
    tenant_id: UUID
    contents: UIConfigContents
    form_type: FormType


(
    _,
    _,
    UIConfigResponse,
    _,
    _,
) = create_models(UIConfigAttribute)


class UIConfigInputRequestAttributes(BaseModel):
    __entity_name__ = "ui_config_input"
    __entity_url_supplier__ = functools.partial(entity_url_supplier, "ui_config_input")
    contents: UIConfigContents
    form_type: FormType


(
    UIConfigInputRequest,
    _,
    _,
    _,
    _,
) = create_models(UIConfigInputRequestAttributes)


ERROR_500_TITLE = "An exception has occurred"
ERROR_500_DETAIL = "An exception has occurred"


def merge_dicts_iteratively(source: dict, target: dict) -> dict:
    """
    Iteratively merge source dictionary into target dictionary and return the result.

    Args:
        source (dict): The dictionary with new data to merge.
        target (dict): The dictionary to update with data from the source.

    Returns:
        dict: The merged dictionary.
    """
    # Create a copy of the target to avoid modifying it directly
    result = deepcopy(target)
    stack = [(source, result)]  # Stack to keep track of dictionaries to merge

    while stack:
        current_source, current_target = stack.pop()

        for key, value in current_source.items():
            if (
                key in current_target
                and isinstance(value, dict)
                and isinstance(current_target[key], dict)
            ):
                # If both source and target have a dictionary for the same key, add them to the stack
                stack.append((value, current_target[key]))
            else:
                # Otherwise, overwrite or add the key-value pair in the target
                current_target[key] = value

    return result


@router.post(
    "",
    response_model=UIConfigResponse,
    status_code=201,
    tags=["ui-config"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def create_ui_config_data(
    ui_config_request: dict,
    ui_config_manager: UIConfigManager = Depends(get_ui_config_manager),
    tenant: Tenant = Depends(get_tenant),
) -> UIConfigResponse | ErrorResponse:  # type: ignore
    """
    Create or update UI configuration data.

    This endpoint handles both creating new UI configuration data and updating
    existing data based on the provided form type and tenant ID.

    Args:
        ui_config_request (dict): The request body containing the UI configuration data.
        ui_config_manager (UIConfigManager, optional):  Defaults to Depends(get_ui_config_manager).
        tenant (Tenant, optional): The tenant information. Defaults to Depends(get_tenant).

    Returns:
        UIConfigResponse | ErrorResponse: The created or updated UI configuration data,
                                          or an error response.
    """
    try:
        data = ui_config_request["data"]
        data = UIConfigAttributes(**data["attributes"])
        input_contents = data.contents.dict()
        form_type = data.form_type
        # Fetch existing configuration based on form_type and tenant_id
        existing_config = await ui_config_manager.get_ui_config_based_on_form_type(
            form_type=form_type, tenant_id=tenant.id
        )

        if existing_config:
            existing_contents = existing_config.contents or {}

            # Iteratively merge input_contents into existing_contents and return the result
            merged_contents = merge_dicts_iteratively(input_contents, existing_contents)

            # Update the existing configuration
            updated_config = await ui_config_manager.update_config_data(
                existing_config.id, merged_contents
            )
            if updated_config:
                config_data = UIConfigAttribute(**updated_config.dict())
                return UIConfigResponse.pack(  # type: ignore
                    id=updated_config.id, attributes=config_data
                )
        else:
            created_config_data = await ui_config_manager.create_ui_config_data(
                contents=input_contents, tenant_id=tenant.id, form_type=form_type
            )
            config_data = UIConfigAttribute(**created_config_data.dict())
            return UIConfigResponse.pack(  # type: ignore
                id=created_config_data.id, attributes=config_data
            )

    except ValidationError as e:
        logger.exception("Inputs provided for creating config data are not valid")
        return ErrorResponse(400, "Bad Input", str(e))
    except Exception:
        logger.exception(
            f"error creating config data with attributes {ui_config_request.data.attributes}"  # type: ignore
        )
        return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
    return ErrorResponse(500, ERROR_500_TITLE, ERROR_500_DETAIL)
