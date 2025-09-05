from uuid import UUID

from pydantic import Field, HttpUrl

from worker_safety_service.configs.base_configuration_model import (
    BaseConfigurationModel,
    load,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.integrations.pwc.pwd_maximo_client import PwCMaximoClient
from worker_safety_service.site_conditions.world_data import HTTPClient


class PWCMaximoClientConfigShort(BaseConfigurationModel):
    __config_path__ = "INTEGRATIONS.PWC_MAXIMO"
    enabled: bool


class PWCMaximoClientConfig(PWCMaximoClientConfigShort):
    client_id: str = Field(
        description="Client Credentials used to authenticate in the maximo server."
    )
    client_secret: str = Field(
        description="Client Secret used to authenticate in the maximo server."
    )
    url: HttpUrl = Field(description="The PWC Maximo server URL.")
    worker_safety_base_url: HttpUrl = Field(
        description="The worker safety base URL used in the entities links."
    )


async def get_pwc_client(
    configurations_manager: ConfigurationsManager, tenant_id: UUID
) -> PwCMaximoClient:
    is_enabled_cfg = await load(
        configurations_manager, PWCMaximoClientConfigShort, tenant_id
    )
    if not is_enabled_cfg.enabled:
        raise RuntimeError(
            "Could not fetch the configurations for the PwC Maximo Client"
        )

    client_configs = await load(
        configurations_manager, PWCMaximoClientConfig, tenant_id
    )
    return PwCMaximoClient(
        HTTPClient,
        client_configs.client_id,
        client_configs.client_secret,
        client_configs.url,
        client_configs.worker_safety_base_url,
    )
