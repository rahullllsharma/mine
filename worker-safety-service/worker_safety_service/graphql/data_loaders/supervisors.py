from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import Supervisor


class TenantSupervisorLoader:
    def __init__(self, manager: SupervisorsManager, tenant_id: UUID):
        self.__manager = manager
        self.tenant_id = tenant_id
        self.by_activity = DataLoader(load_fn=self.load_supervisors_by_activity)

    async def load_supervisors_by_activity(
        self, activity_ids: list[UUID]
    ) -> list[list[Supervisor]]:
        items = await self.__manager.get_supervisors_by_activity(
            tenant_id=self.tenant_id, activity_ids=activity_ids
        )
        return [items.get(i) or [] for i in activity_ids]

    async def add_supervisor_to_activity(
        self, activity_id: UUID, supervisor_id: UUID
    ) -> bool:
        return await self.__manager.link_supervisor_to_activity(
            activity_id, supervisor_id=supervisor_id
        )

    async def remove_supervisor_from_activity(
        self, activity_id: UUID, supervisor_id: UUID
    ) -> bool:
        return await self.__manager.unlink_supervisor_to_activity(
            activity_id, supervisor_id=supervisor_id
        )
