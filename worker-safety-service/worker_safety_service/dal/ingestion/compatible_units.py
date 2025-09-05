import uuid

from sqlalchemy.sql.operators import is_not
from sqlmodel import col, select

from worker_safety_service.models import AsyncSession, set_order_by
from worker_safety_service.models.ingest import CompatibleUnit, ElementLibraryTaskLink
from worker_safety_service.types import OrderBy


class CompatibleUnitManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_library_tasks_for_cu(
        self, tenant_id: uuid.UUID, compatible_unit_id: str
    ) -> set[uuid.UUID]:
        """
        Returns Library Task IDs
        """
        statement = (
            select(ElementLibraryTaskLink.library_task_id)
            .join_from(
                CompatibleUnit,
                ElementLibraryTaskLink,
                CompatibleUnit.element_id == ElementLibraryTaskLink.element_id,
            )
            .where(CompatibleUnit.compatible_unit_id == compatible_unit_id)
            .where(CompatibleUnit.tenant_id == tenant_id)
            .where(is_not(CompatibleUnit.element_id, None))
        )

        library_task_ids = set((await self.session.exec(statement)))
        return library_task_ids

    async def get_compatible_units(
        self,
        tenant_id: uuid.UUID,
        compatible_unit_ids: list[str] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[CompatibleUnit]:
        """
        Retrieve Compatible Units
        """
        if compatible_unit_ids is not None and not compatible_unit_ids:
            return []

        statement = select(CompatibleUnit).where(CompatibleUnit.tenant_id == tenant_id)
        if compatible_unit_ids:
            statement = statement.where(
                col(CompatibleUnit.compatible_unit_id).in_(compatible_unit_ids)
            )

        statement = set_order_by(CompatibleUnit, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_compatible_units_by_id(
        self,
        tenant_id: uuid.UUID,
        compatible_unit_ids: list[str] | None = None,
    ) -> dict[str, CompatibleUnit]:
        return {
            cu.compatible_unit_id: cu
            for cu in await self.get_compatible_units(
                tenant_id=tenant_id, compatible_unit_ids=compatible_unit_ids
            )
        }

    async def create_compatible_unit(
        self,
        tenant_id: uuid.UUID,
        compatible_unit_id: str,
        element_id: str | None = None,
        description: str | None = None,
    ) -> CompatibleUnit:
        cu = CompatibleUnit(
            tenant_id=tenant_id,
            compatible_unit_id=compatible_unit_id,
            element_id=element_id,
            description=description,
        )

        self.session.add(cu)
        await self.session.commit()

        return cu
