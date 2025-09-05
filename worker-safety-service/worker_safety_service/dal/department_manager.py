from logging import getLogger
from typing import Optional
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service.dal.crua_manager import CRUDManager
from worker_safety_service.models import (
    AsyncSession,
    Department,
    DepartmentCreate,
    DepartmentDelete,
)

logger = getLogger(__name__)


class DepartmentManager(CRUDManager[Department]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=Department)

    async def create_department(self, input: DepartmentCreate) -> Department:
        # create the new department
        department_instance = Department(**input.dict())
        await self.create(department_instance)

        return department_instance

    async def get_departments_by_opco_id(
        self, opco_ids: list[UUID]
    ) -> dict[UUID, list[Department]]:
        query = select(Department).where(col(Department.opco_id).in_(opco_ids))

        department_data = (
            await self.session.exec(query.order_by(Department.name))
        ).all()

        department_map: dict[UUID, list[Department]] = {}
        for department in department_data:
            if department.opco_id in department_map:
                department_map[department.opco_id].append(department)
            else:
                department_map[department.opco_id] = [department]

        return department_map

    async def get_all_departments(
        self,
        opco_id: Optional[UUID] = None,
        limit: Optional[int] = None,
        after: Optional[UUID] = None,
    ) -> list[Department]:
        query = select(Department)

        if opco_id is not None:
            query = query.where(Department.opco_id == opco_id)
        if after is not None:
            after_department = await self.get_by_id(after)
            if after_department is not None:
                query = query.where(Department.created_at > after_department.created_at)
        if limit:
            query = query.limit(limit)

        departments = await self.session.exec(query.order_by(Department.name))

        return departments.all()

    async def edit_department(self, department: Department) -> Optional[Department]:
        await super().update(department)

        return await self.get_by_id(department.id)

    async def delete_department(self, id: UUID) -> DepartmentDelete:
        await super().delete(id)
        return DepartmentDelete(error=None)
