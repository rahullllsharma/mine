import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tenant_settings.tenant_library_task_settings import (
    TenantLibraryTaskSettingsManager,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryTaskSettings,
)


class TenantLibraryTaskSettingsLoader:
    def __init__(
        self,
        manager: TenantLibraryTaskSettingsManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_tenant_library_task_setting)

    async def load_tenant_library_task_setting(
        self, library_task_ids: list[uuid.UUID]
    ) -> list[TenantLibraryTaskSettings | None]:
        items = await self.__manager.get_settings(
            tenant_id=self.tenant_id, primary_key_values=library_task_ids
        )
        return [items.get(i) for i in library_task_ids]

    async def get_tenant_library_task_setting(
        self, task_id: uuid.UUID
    ) -> TenantLibraryTaskSettings | None:
        return await self.__manager.get(self.tenant_id, primary_key_value=task_id)

    async def get_tenant_library_task_settings(
        self,
    ) -> list[TenantLibraryTaskSettings]:
        tenant_settings = await self.__manager.get_all(
            additional_where_clause=[
                TenantLibraryTaskSettings.tenant_id == self.tenant_id
            ],
            order_by_attribute="library_task_id",
        )

        return tenant_settings
