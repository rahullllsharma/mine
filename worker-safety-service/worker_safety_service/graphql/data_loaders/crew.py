import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.models import Crew


class TenantCrewLoader:
    def __init__(self, manager: CrewManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_crew)
        self.__manager = manager

    async def load_crew(self, ids: list[uuid.UUID]) -> list[Crew | None]:
        items = await self.__manager.get_crew_by_id(ids=ids, tenant_id=self.tenant_id)
        return [items.get(i) for i in ids]
