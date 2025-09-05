import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tenant_settings.tenant_library_site_condition_settings import (
    TenantLibrarySiteConditionSettingsManager,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibrarySiteConditionSettings,
)


class TenantLibrarySiteConditionSettingsLoader:
    def __init__(
        self,
        manager: TenantLibrarySiteConditionSettingsManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_tenant_library_site_condition_setting)

    async def load_tenant_library_site_condition_setting(
        self, library_site_condition_ids: list[uuid.UUID]
    ) -> list[TenantLibrarySiteConditionSettings | None]:
        items = await self.__manager.get_settings(
            tenant_id=self.tenant_id, primary_key_values=library_site_condition_ids
        )
        return [items.get(i) for i in library_site_condition_ids]

    async def get_tenant_library_site_condition_setting(
        self, site_condition_id: uuid.UUID
    ) -> TenantLibrarySiteConditionSettings | None:
        return await self.__manager.get(
            self.tenant_id, primary_key_value=site_condition_id
        )

    async def get_tenant_library_site_condition_settings(
        self,
    ) -> list[TenantLibrarySiteConditionSettings]:
        tenant_settings = await self.__manager.get_all(
            additional_where_clause=[
                TenantLibrarySiteConditionSettings.tenant_id == self.tenant_id
            ],
            order_by_attribute="library_site_condition_id",
        )

        return tenant_settings
