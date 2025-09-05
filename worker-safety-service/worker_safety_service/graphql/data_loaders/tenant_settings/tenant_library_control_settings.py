import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tenant_settings.tenant_library_control_settings import (
    TenantLibraryControlSettingsManager,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryControlSettings,
)


class TenantLibraryControlSettingsLoader:
    def __init__(
        self,
        manager: TenantLibraryControlSettingsManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_tenant_library_control_setting)

    async def load_tenant_library_control_setting(
        self, library_control_ids: list[uuid.UUID]
    ) -> list[TenantLibraryControlSettings | None]:
        items = await self.__manager.get_settings(
            tenant_id=self.tenant_id, primary_key_values=library_control_ids
        )
        return [items.get(i) for i in library_control_ids]

    async def get_tenant_library_control_setting(
        self, control_id: uuid.UUID
    ) -> TenantLibraryControlSettings | None:
        return await self.__manager.get(self.tenant_id, primary_key_value=control_id)

    async def get_tenant_library_control_settings(
        self,
    ) -> list[TenantLibraryControlSettings]:
        tenant_settings = await self.__manager.get_all(
            additional_where_clause=[
                TenantLibraryControlSettings.tenant_id == self.tenant_id,
            ],
            order_by_attribute="library_control_id",
        )

        return tenant_settings
