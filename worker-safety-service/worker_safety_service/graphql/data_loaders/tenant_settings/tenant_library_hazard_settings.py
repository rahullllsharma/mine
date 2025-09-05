import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tenant_settings.tenant_library_hazard_settings import (
    TenantLibraryHazardSettingsManager,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryHazardSettings,
)


class TenantLibraryHazardSettingsLoader:
    def __init__(
        self,
        manager: TenantLibraryHazardSettingsManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_tenant_library_hazard_setting)

    async def load_tenant_library_hazard_setting(
        self, library_hazard_ids: list[uuid.UUID]
    ) -> list[TenantLibraryHazardSettings | None]:
        items = await self.__manager.get_settings(
            tenant_id=self.tenant_id, primary_key_values=library_hazard_ids
        )
        return [items.get(i) for i in library_hazard_ids]

    async def get_tenant_library_hazard_setting(
        self, hazard_id: uuid.UUID
    ) -> TenantLibraryHazardSettings | None:
        return await self.__manager.get(self.tenant_id, primary_key_value=hazard_id)

    async def get_tenant_library_hazard_settings(
        self,
    ) -> list[TenantLibraryHazardSettings]:
        tenant_settings = await self.__manager.get_all(
            additional_where_clause=[
                TenantLibraryHazardSettings.tenant_id == self.tenant_id
            ],
            order_by_attribute="library_hazard_id",
        )

        return tenant_settings
