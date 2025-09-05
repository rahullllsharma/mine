from uuid import UUID

from sqlalchemy.orm import sessionmaker
from sqlmodel import select

from worker_safety_service.models import WorkPackageCompatibleUnitLink


class WorkPackageToCompatibleUnitManager:
    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    async def get_work_package_compatible_unit_mapping_by_tenant(
        self, tenant_id: UUID
    ) -> list[WorkPackageCompatibleUnitLink]:
        statement = select(WorkPackageCompatibleUnitLink).where(
            WorkPackageCompatibleUnitLink.tenant_id == tenant_id
        )

        async with self.session_factory() as session:
            cursor = await session.exec(statement)
            return list(cursor.all())
