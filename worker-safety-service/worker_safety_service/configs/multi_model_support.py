import functools
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Awaitable, Callable, TypeVar
from uuid import UUID

from pydantic import ValidationError

from worker_safety_service.configs.base_configuration_model import (
    BaseConfigurationModel,
    load,
    store_partial,
)
from worker_safety_service.integrations.pwc.factory import (
    PWCMaximoClientConfig,
    PWCMaximoClientConfigShort,
)
from worker_safety_service.risk_model.configs import KNOWN_CONFIGURATIONS

if TYPE_CHECKING:
    from worker_safety_service.dal.configurations import ConfigurationsManager

T = TypeVar("T")


class ConfigurationModelNotFound(Exception):
    def __init__(self, label: str):
        self.label = label
        super().__init__(
            f"Could not find the configuration property for label: {label}"
        )


@dataclass(frozen=True)
class ConfigurationModelInfo:
    configuration_path: str
    schema: int


# All the available configurations in the system.
# TODO: This will need to be populated automatically otherwise it's going to be a pain.
CONFIG_CLASSES: list[type[BaseConfigurationModel]] = [
    PWCMaximoClientConfig,
    PWCMaximoClientConfigShort,
    *KNOWN_CONFIGURATIONS,
]


def available_models() -> list[type[BaseConfigurationModel]]:
    """
    Returns the schemas for all the known configuration models.
    """
    return CONFIG_CLASSES


async def load_for_label(
    configurations_manager: "ConfigurationsManager",
    label: str,
    tenant_id: UUID,
) -> Any:
    """
    Loads the configurations for the given label into the appropriate model.
    """

    label = label.upper()
    config_obj = await __try_over_configuration(
        label, functools.partial(load, configurations_manager, tenant_id=tenant_id)
    )
    return config_obj


async def store_partial_configuration_for_label(
    configurations_manager: "ConfigurationsManager",
    label: str,
    tenant_id: UUID,
    to_store_fields: dict,
) -> BaseConfigurationModel:
    """
    Stores the given configuration for the label.
    Accepts a partial object because values are interpolated with the application defaults.
    """
    label = label.upper()

    async def store_partial_object(
        klass: type[BaseConfigurationModel],
    ) -> type[BaseConfigurationModel]:
        await store_partial(configurations_manager, klass, tenant_id, **to_store_fields)
        return klass

    config_klass = await __try_over_configuration(label, store_partial_object)
    return await load(configurations_manager, config_klass, tenant_id)


async def __try_over_configuration(
    label: str, operation: Callable[[type[BaseConfigurationModel]], Awaitable[T]]
) -> T:
    error: ValidationError | None = None
    for _config_class in CONFIG_CLASSES:
        if _config_class.__config_path__ == label:
            try:
                ret = await operation(_config_class)
                return ret
            except ValidationError as ex:
                if error is None or len(error.errors()) > len(ex.errors()):
                    error = ex

    if error:
        raise error
    else:
        raise ConfigurationModelNotFound(label)
