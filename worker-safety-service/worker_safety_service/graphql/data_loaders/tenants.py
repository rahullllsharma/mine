import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models.tenants import Tenant, TenantCreate, TenantEdit


class TenantLoader:
    """
    Given tenant ids, load objects
    """

    def __init__(self, manager: TenantManager):
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_tenants)
        self.me_by_id = DataLoader(load_fn=self.load_tenants_by_id)

    async def load_tenants(self, tenant_names: list[str]) -> list[Tenant | None]:
        tenants = await self.__manager.get_tenants_by_name(tenant_names)
        return [tenants.get(name) for name in tenant_names]

    async def load_tenants_by_id(
        self, tenant_ids: list[uuid.UUID]
    ) -> list[Tenant | None]:
        tenants = await self.__manager.get_tenants_by_id(tenant_ids)
        return [tenants.get(id) for id in tenant_ids]

    async def create_tenant(self, tenant_create: TenantCreate) -> Tenant | None:
        tenant = await self.__manager.create(tenant_create)
        return tenant

    async def edit_tenant(self, tenant_edit: TenantEdit) -> Tenant:
        tenant = await self.__manager.edit(tenant_edit)
        return tenant
