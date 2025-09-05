from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service.configs.base_configuration_model import load_many
from worker_safety_service.dal.configurations import (
    ConfigurationsManager,
    EntityConfiguration,
    EntityConfigurationExt,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    RankedMetricConfig,
)


class TenantConfigurationsLoader:
    def __init__(
        self,
        configurations_manager: ConfigurationsManager,
        tenant_id: UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = configurations_manager
        self.me = DataLoader(load_fn=self.load_configurations)

    async def get_section(self, section_name: str) -> EntityConfigurationExt:
        return await self.__manager.get_section(self.tenant_id, section_name)

    async def get_entities(self) -> list[EntityConfigurationExt]:
        return await self.__manager.get_entities(self.tenant_id)

    async def update_section(self, entity_config: EntityConfiguration) -> None:
        await self.__manager.update_section(entity_config, self.tenant_id)

    async def update_default_section(self, entity_config: EntityConfiguration) -> None:
        await self.__manager.update_section(entity_config, None)

    async def load_configurations(
        self, config_types: list[type[RankedMetricConfig]]
    ) -> list[RankedMetricConfig]:
        unique_config_types = list(set(config_types))
        items = await load_many(self.__manager, unique_config_types, self.tenant_id)

        return items
