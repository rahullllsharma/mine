import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.models.standard_operating_procedures import (
    StandardOperatingProcedure,
)


class StandardOperatingProceduresLoader:
    def __init__(
        self,
        manager: StandardOperatingProcedureManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.by_library_task = DataLoader(load_fn=self.load_by_library_task)

    async def load_by_library_task(
        self,
        library_task_ids: list[uuid.UUID],
    ) -> list[list[StandardOperatingProcedure]]:
        return [
            await self.__manager.get_standard_operating_procedures_by_library_task(
                library_task_id=library_task_id, tenant_id=self.tenant_id
            )
            for library_task_id in library_task_ids
        ]
