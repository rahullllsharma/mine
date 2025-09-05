from typing import Any, Awaitable, TypeVar

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ValidationError
from starlette.requests import Request

from worker_safety_service.configs.base_configuration_model import (
    BaseConfigurationModel,
    expose,
)
from worker_safety_service.configs.multi_model_support import (
    ConfigurationModelNotFound,
    available_models,
    load_for_label,
    store_partial_configuration_for_label,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.keycloak import authenticate_integration, get_tenant
from worker_safety_service.models import Tenant
from worker_safety_service.rest.dependency_injection import get_configurations_manager
from worker_safety_service.rest.exception_handlers import ErrorResponse

router = APIRouter(dependencies=[Depends(authenticate_integration)])

T = TypeVar("T")


class ConfigurationModelInfo(BaseModel):
    configuration_path: str
    json_schema: dict


class ConfigurationDescription(BaseModel):
    # Actual interpolated values
    actual: dict[str, Any]
    # Values stored as defaults/application specific
    application: dict[str, Any]
    # Values stored as tenant specific
    tenant: dict[str, Any]


@router.get(
    "/configurations/{label}",
    response_model=None,
    status_code=200,
    tags=["configurations"],
)
async def get_configuration_label(
    label: str,
    tenant: Tenant = Depends(get_tenant),
    config_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> BaseConfigurationModel | ErrorResponse:
    """Get the configuration for a label"""
    label = label.upper()
    coro = load_for_label(config_manager, label, tenant.id)
    return await with_exception_handling(coro)


@router.get(
    "/configurations",
    response_model=None,
    status_code=200,
    tags=["configurations"],
)
async def get_configuration_schemas() -> list:
    """Get configurations"""
    models = available_models()
    return [
        ConfigurationModelInfo(
            configuration_path=model.__config_path__, json_schema=model.schema()
        )
        for model in models
    ]


@router.get(
    "/configurations/{label}/describe",
    response_model=ConfigurationDescription,
    status_code=200,
    tags=["configurations"],
)
async def describe_configuration_label(
    label: str,
    tenant: Tenant = Depends(get_tenant),
    config_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> ConfigurationDescription | ErrorResponse:
    """Describe the configuration for a label"""
    actual = await get_configuration_label(label, tenant, config_manager)
    if isinstance(actual, ErrorResponse):
        return actual

    d = await expose(config_manager, type(actual), tenant.id)

    return ConfigurationDescription(
        actual=actual.dict(),
        application=d["defaults"],
        tenant=d["tenant"],
    )


@router.put(
    "/configurations/{label}",
    response_model=None,
    status_code=201,
    tags=["configurations"],
)
async def update_configuration(
    label: str,
    request: Request,
    tenant: Tenant = Depends(get_tenant),
    config_manager: ConfigurationsManager = Depends(get_configurations_manager),
) -> BaseConfigurationModel | ErrorResponse:
    """Update a configuration"""
    label = label.upper()
    body = await request.json()
    coro = store_partial_configuration_for_label(config_manager, label, tenant.id, body)
    return await with_exception_handling(coro)


# This acts like a custom exception handler for this module.
async def with_exception_handling(func: Awaitable[T]) -> T | ErrorResponse:
    try:
        return await func
    except ValidationError as ex:
        return ErrorResponse(
            400,
            "Invalid configuration property.",
            "Errors found in the configuration properties provided. Check the error metadata.",
            meta=ex.errors(),
        )
    except ConfigurationModelNotFound as ex:
        return ErrorResponse(
            404,
            "Could not find the a configuration entity for Label",
            "Label: " + ex.label,
        )
