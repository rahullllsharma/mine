import uuid

from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.models.library import WorkType


class WorkTypesLoader:
    def __init__(
        self,
        manager: WorkTypeManager,
        tenant_id: uuid.UUID,
    ):
        self.__manager = manager
        self.tenant_id = tenant_id

    async def load_tenant_work_types(self) -> list[WorkType]:
        return await self.__manager.get_work_types_for_tenant(self.tenant_id)

    async def get_work_type_by_code_and_tenant(
        self, code: str, tenant_id: uuid.UUID
    ) -> uuid.UUID | None:
        return await self.__manager.get_work_type_by_code_and_tenant(code, tenant_id)
