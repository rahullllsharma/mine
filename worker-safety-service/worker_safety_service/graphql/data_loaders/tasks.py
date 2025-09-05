import datetime
import functools
import uuid
from typing import Optional

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.data_loaders.utils import create_order_by_hash
from worker_safety_service.models import (
    LibraryControl,
    LibraryHazard,
    LibraryTask,
    Task,
    TaskControl,
    TaskCreate,
    TaskHazard,
    User,
)
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import TaskChanged, TaskDeleted
from worker_safety_service.types import OrderBy
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class TenantTaskLoader:
    """
    Given project location task ids, load objects
    """

    def __init__(
        self,
        manager: TaskManager,
        risk_model_reactor: RiskModelReactorInterface,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_tasks)
        self.with_archived = DataLoader(load_fn=self.load_tasks_with_archived)
        self.__manager = manager
        self.__risk_model_reactor = risk_model_reactor
        self.__hazards_map: dict[
            tuple[bool | None, int | None],
            DataLoader,
        ] = {}
        self.__controls_map: dict[
            tuple[bool | None, int | None],
            DataLoader,
        ] = {}

    async def load_tasks(
        self, ids: list[uuid.UUID]
    ) -> list[tuple[LibraryTask, Task] | None]:
        items = {
            i[1].id: i
            for i in await self.__manager.get_tasks(ids=ids, tenant_id=self.tenant_id)
        }
        return [items.get(i) for i in ids]

    async def load_tasks_with_archived(
        self, ids: list[uuid.UUID]
    ) -> list[tuple[LibraryTask, Task] | None]:
        items = {
            i[1].id: i
            for i in await self.__manager.get_tasks(
                ids=ids, tenant_id=self.tenant_id, with_archived=True
            )
        }
        return [items.get(i) for i in ids]

    async def get_tasks(
        self,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        activities_ids: list[uuid.UUID] | None = None,
        activity_external_keys: list[str] | None = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        search: str | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> list[tuple[LibraryTask, Task]]:
        # some parameters are NOT being received to be passed along
        return await self.__manager.get_tasks(
            ids=ids,
            location_ids=location_ids,
            activities_ids=activities_ids,
            activity_external_keys=activity_external_keys,
            limit=limit,
            after=after,
            date=date,
            start_date=start_date,
            end_date=end_date,
            search=search,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )

    def hazards(
        self,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> DataLoader:
        key = (
            is_applicable,
            create_order_by_hash(order_by),
        )
        dataloader = self.__hazards_map.get(key)
        if not dataloader:
            dataloader = self.__hazards_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_hazards,
                    is_applicable=is_applicable,
                    order_by=order_by,
                    filter_tenant_settings=filter_tenant_settings,
                )
            )
        return dataloader

    async def load_hazards(
        self,
        task_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[list[tuple[LibraryHazard, TaskHazard]]]:
        items = await self.__manager.get_hazards_by_task(
            task_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [items[i] for i in task_ids]

    def controls(
        self,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> DataLoader:
        key = (
            is_applicable,
            create_order_by_hash(order_by),
        )
        dataloader = self.__controls_map.get(key)
        if not dataloader:
            dataloader = self.__controls_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_controls,
                    is_applicable=is_applicable,
                    order_by=order_by,
                    filter_tenant_settings=filter_tenant_settings,
                )
            )
        return dataloader

    async def load_controls(
        self,
        hazard_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[list[tuple[LibraryControl, TaskControl]]]:
        items = await self.__manager.get_controls_by_hazard(
            hazard_ids=hazard_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [items[i] for i in hazard_ids]

    async def create_tasks(
        self,
        tasks: list[TaskCreate],
        user: User | None,
        db_commit: bool = True,
    ) -> list[Task]:
        to_create, existing = await self.__manager.validate_tasks(tasks, self.tenant_id)
        created = await self.__manager.create_tasks(
            to_create, user=user, db_commit=db_commit
        )
        unarchived = await self.__manager.unarchive_tasks(existing)
        created.extend(unarchived)
        for task in created:
            await self.__risk_model_reactor.add(TaskChanged(project_task_id=task.id))
        return created

    async def delete_task(
        self,
        id: uuid.UUID,
        user: User | None,
    ) -> bool:
        tasks = await self.get_tasks(ids=[id])
        if not tasks:
            raise ResourceReferenceException("Task not found")
        _, task = tasks[0]
        if task.archived_at is not None:
            return True

        try:
            await self.__manager.archive_task(task, user)
        except Exception:
            logger.exception(
                "Failed to archive task",
                task_id=str(id),
                user_id=str(user.id) if user else "",
            )
            return False
        await self.__risk_model_reactor.add(TaskDeleted(project_task_id=task.id))
        return True
