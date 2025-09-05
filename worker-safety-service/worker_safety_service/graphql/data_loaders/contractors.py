import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.models import Contractor
from worker_safety_service.types import OrderBy


class TenantContractorsLoader:
    def __init__(self, manager: ContractorsManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_contractors)
        self.__manager = manager

    async def load_contractors(self, ids: list[uuid.UUID]) -> list[Contractor | None]:
        items = await self.__manager.get_contractors_by_id(
            ids=ids, tenant_id=self.tenant_id
        )
        return [items.get(i) for i in ids]

    async def get_contractors(
        self, order_by: list[OrderBy] | None = None
    ) -> list[Contractor]:
        return await self.__manager.get_contractors(
            tenant_id=self.tenant_id, order_by=order_by
        )
