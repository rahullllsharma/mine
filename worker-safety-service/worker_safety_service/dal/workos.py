from uuid import UUID

from worker_safety_service.dal.crud_manager import CRUDManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    AsyncSession,
    WorkOS,
    WorkOSCreateInput,
    WorkOSUpdateInput,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class WorkOSManager(CRUDManager[WorkOS]):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        super().__init__(session=session, entity_type=WorkOS)

    async def get_workos_details_by_tenant_id(self, tenant_id: UUID) -> list[WorkOS]:
        return await self.get_all(
            additional_where_clause=[WorkOS.tenant_id == tenant_id]
        )

    async def create_workos(self, input: WorkOSCreateInput) -> WorkOS:
        workos_instance = WorkOS(**input.dict())
        return await self.create(workos_instance)

    async def update_workos(self, id: UUID, input: WorkOSUpdateInput) -> WorkOS:
        workos_instance = await self.get_by_id(id)
        if not workos_instance:
            raise ResourceReferenceException("Could not find requested workos instance")

        if input.workos_directory_id:
            workos_instance.workos_directory_id = input.workos_directory_id
        if input.workos_org_id:
            workos_instance.workos_org_id = input.workos_org_id

        await self.update(workos_instance)
        updated_workos = await self.get_by_id(workos_instance.id)
        assert updated_workos
        return updated_workos
