from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.department_manager import DepartmentManager
from worker_safety_service.models import Department


class DepartmentLoader:
    def __init__(self, manager: DepartmentManager):
        self.__manager = manager
        self.by_opco = DataLoader(load_fn=self.load_departments_by_opco)

    async def load_departments_by_opco(
        self, opco_ids: list[UUID]
    ) -> list[list[Department]]:
        items = await self.__manager.get_departments_by_opco_id(opco_ids=opco_ids)
        return [items.get(i) or [] for i in opco_ids]
