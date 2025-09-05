from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.opco_manager import OpcoManager
from worker_safety_service.models import Opco


class OpcoLoader:
    def __init__(self, manager: OpcoManager, tenant_id: UUID):
        self.__manager = manager
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_opcos)
        self.by_user = DataLoader(load_fn=self.load_opcos_by_user)

    async def load_opcos(self, opco_ids: list[UUID]) -> list[Opco | None]:
        items = await self.__manager.get_all_opco(
            tenant_id=self.tenant_id, opco_ids=opco_ids
        )
        opco_map = {opco.id: opco for opco in items}
        return [opco_map.get(i) for i in opco_ids]

    async def load_opcos_by_user(self, user_ids: list[UUID]) -> list[Opco | None]:
        items = await self.__manager.get_opcos_by_user_id(
            tenant_id=self.tenant_id, user_ids=user_ids
        )
        return [items.get(i) for i in user_ids]
