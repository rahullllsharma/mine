from typing import Optional
from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.jsb_supervisors import JSBSupervisorsManager
from worker_safety_service.models.concepts import CrewInformation
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink


class JSBSupervisorLoader:
    def __init__(self, manager: JSBSupervisorsManager):
        self.manager = manager
        self.jsb_supervisors = DataLoader(load_fn=self.get_jsb_supervisors_by_jsb_ids)

    async def get_jsb_supervisors_by_jsb_ids(
        self,
        jsb_ids: list[UUID],
    ) -> list[list[JSBSupervisorLink] | None]:
        supervisor_data = await self.manager.get_jsb_supervisors_by_jsb_ids(
            jsb_ids=jsb_ids
        )

        return [supervisor_data[jsb_id] for jsb_id in jsb_ids]

    async def get_jsb_supervisors(
        self, limit: Optional[int] = None, offset: int | None = None
    ) -> list[JSBSupervisorLink]:
        return await self.manager.get_jsb_supervisors(limit=limit, offset=offset)

    async def update_supervisor_jsb_data(
        self, jsb_id: UUID, crew_infos: list[CrewInformation]
    ) -> None:
        return await self.manager.update_supervisor_jsb_data(jsb_id, crew_infos)
