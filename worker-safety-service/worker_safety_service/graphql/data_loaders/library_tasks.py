import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service import get_logger
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import LibraryTask
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import LibraryTaskDataChanged
from worker_safety_service.types import OrderBy

logger = get_logger(__name__)


class LibraryTasksLoader:
    """Loader for orchestrating library task actions"""

    def __init__(
        self,
        manager: LibraryTasksManager,
        risk_model_reactor: RiskModelReactorInterface,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.__risk_model_reactor = risk_model_reactor
        self.me = DataLoader(load_fn=self.load_tasks)

    async def create_library_task(self, library_task: LibraryTask) -> None:
        """Create library task"""
        await self.__manager.create(library_task)
        try:
            await self.__risk_model_reactor.add(
                LibraryTaskDataChanged(library_task_id=library_task.id)
            )
        except Exception:
            logger.error(
                "Failed to add LibraryTaskDataChanged trigger for newly created library task",
                library_task_id=library_task.id,
            )

    async def update_library_task(self, library_task: LibraryTask) -> None:
        """Update library task"""
        await self.__manager.update(library_task)
        try:
            await self.__risk_model_reactor.add(
                LibraryTaskDataChanged(library_task_id=library_task.id)
            )
        except Exception:
            logger.error(
                "Failed to add LibraryTaskDataChanged trigger for updated library task",
                library_task_id=library_task.id,
            )

    async def get_by_id(self, library_task_id: uuid.UUID) -> LibraryTask | None:
        """Get library task by id"""
        return await self.__manager.get_by_id(library_task_id)

    async def load_tasks(
        self, library_task_ids: list[uuid.UUID]
    ) -> list[LibraryTask | None]:
        # TODO: Check why this does not filter by tenant??
        # TODO: Perhaps change the signature of the inner method
        items = await self.__manager.get_library_tasks_by_id(
            ids=library_task_ids, allow_archived=True
        )
        return [items.get(i) for i in library_task_ids]

    async def get_tasks(
        self,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryTask]:
        return await self.__manager.get_library_tasks(
            tenant_id=self.tenant_id,
            ids=ids,
            order_by=order_by,
            allow_archived=allow_archived,
        )

    async def get_tenant_and_work_type_linked_library_tasks(
        self,
        tenant_work_type_ids: list[uuid.UUID],
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibraryTask]:
        return await self.__manager.get_tenant_and_work_type_linked_library_tasks(
            order_by=order_by,
            tenant_id=self.tenant_id,
            tenant_work_type_ids=tenant_work_type_ids,
            ids=ids,
        )
