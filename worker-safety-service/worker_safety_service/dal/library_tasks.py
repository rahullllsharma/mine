import uuid
from typing import Optional

from sqlalchemy import func
from sqlmodel import and_, col, select
from sqlmodel.sql.expression import SelectOfScalar

from worker_safety_service import get_logger
from worker_safety_service.dal.base_relationship_manager import BaseRelationshipManager
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    LibraryTask,
    TenantLibraryTaskSettings,
    set_order_by,
)
from worker_safety_service.models.library import (
    LibraryTaskActivityGroup,
    WorkType,
    WorkTypeTaskLink,
)
from worker_safety_service.models.work_type_settings import ActivityWorkTypeSettings
from worker_safety_service.types import OrderBy

logger = get_logger(__name__)

ERROR_MSG_PATTERN = r"duplicate key value violates unique constraint \"(\S+)\""


class LibraryTasksManager(CRUAManager[LibraryTask]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session, entity_type=LibraryTask, immutable_fields=["id", "unique_task_id"]
        )
        self._activity_groups_manager: BaseRelationshipManager[
            LibraryTaskActivityGroup
        ] = BaseRelationshipManager(session)

    async def get_library_tasks(
        self,
        ids: list[uuid.UUID] | None = None,
        unique_task_ids: list[str] | None = None,
        tenant_id: Optional[uuid.UUID] | None = None,
        allow_archived: bool = False,
        after: uuid.UUID | None = None,
        limit: int | None = None,
        order_by: list[OrderBy] | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[LibraryTask]:
        """
        Retrieve library tasks directly with optional filters and pagination.
        """
        statement = select(LibraryTask)

        conditions = []
        if ids:
            conditions.append(LibraryTask.id.in_(ids))  # type:ignore

        if unique_task_ids:
            conditions.append(
                LibraryTask.unique_task_id.in_(unique_task_ids)  # type:ignore
            )
        if tenant_id:
            statement = statement.join(
                WorkTypeTaskLink, onclause=WorkTypeTaskLink.task_id == LibraryTask.id
            )
            # FIXME This join(WorkTypeTenantLink) should change to WorkType.tenant_id when FE changes are added for 1220.
            # statement = statement.join(
            #     WorkTypeTenantLink,
            #     onclause=WorkTypeTenantLink.work_type_id
            #     == WorkTypeTaskLink.work_type_id,
            # ).where(WorkTypeTenantLink.tenant_id == tenant_id)
            # NOTE: Below changes are part of CTL phase 1.
            statement = statement.join(
                WorkType, onclause=WorkType.id == WorkTypeTaskLink.work_type_id
            ).where(WorkType.tenant_id == tenant_id)

        return await self._execute_library_task_queries(
            statement=statement,
            conditions=conditions,
            after=after,
            limit=limit,
            use_seek_pagination=use_seek_pagination,
            order_by=order_by,
            allow_archived=allow_archived,
        )

    async def get_tenant_and_work_type_linked_library_tasks(
        self,
        tenant_id: uuid.UUID,
        tenant_work_type_ids: list[uuid.UUID],
        ids: list[uuid.UUID] | None = None,
        allow_archived: bool = False,
        after: uuid.UUID | None = None,
        limit: int | None = None,
        order_by: list[OrderBy] | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[LibraryTask]:
        """
        Retrieve library tasks related to a tenant and optionally linked to a specific project type.
        """
        if not tenant_work_type_ids:
            return []

        statement = (
            select(LibraryTask)
            .join(
                TenantLibraryTaskSettings,
                onclause=TenantLibraryTaskSettings.library_task_id == LibraryTask.id,
            )
            .where(TenantLibraryTaskSettings.tenant_id == tenant_id)
            .join(WorkTypeTaskLink, onclause=WorkTypeTaskLink.task_id == LibraryTask.id)
            .where(col(WorkTypeTaskLink.work_type_id).in_(tenant_work_type_ids))
            .join(
                LibraryTaskActivityGroup,
                onclause=LibraryTaskActivityGroup.library_task_id == LibraryTask.id,
            )
            .join(
                ActivityWorkTypeSettings,
                onclause=ActivityWorkTypeSettings.library_activity_group_id
                == LibraryTaskActivityGroup.activity_group_id,
            )
            .where(col(ActivityWorkTypeSettings.work_type_id).in_(tenant_work_type_ids))
            .where(col(ActivityWorkTypeSettings.disabled_at).is_(None))
        )

        conditions = []
        if ids:
            conditions.append(LibraryTask.id.in_(ids))  # type:ignore

        return await self._execute_library_task_queries(
            statement=statement,
            conditions=conditions,
            order_by=order_by,
            allow_archived=allow_archived,
            after=after,
            limit=limit,
            use_seek_pagination=use_seek_pagination,
        )

    async def get_activity_group_linked_library_tasks(
        self,
        activity_group_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryTask]:
        """
        Retrieve library tasks related to specific activity groups.
        """
        statement = select(LibraryTask).join(
            LibraryTaskActivityGroup,
            LibraryTaskActivityGroup.library_task_id == LibraryTask.id,
        )

        return await self._execute_library_task_queries(
            statement=statement,
            conditions=[
                (
                    LibraryTaskActivityGroup.activity_group_id.in_(  # type:ignore
                        activity_group_ids
                    )
                )
            ],
            order_by=order_by,
            allow_archived=allow_archived,
        )

    async def get_library_tasks_by_id(
        self,
        ids: list[uuid.UUID],
        allow_archived: bool = False,
    ) -> dict[uuid.UUID, LibraryTask]:
        return {
            i.id: i
            for i in await self.get_library_tasks(
                ids=ids, allow_archived=allow_archived
            )
        }

    async def get_library_task_by_unique_task_id(
        self, unique_task_id: str
    ) -> LibraryTask | None:
        library_tasks = await self.get_library_tasks(unique_task_ids=[unique_task_id])
        if not library_tasks:
            return None

        if len(library_tasks) > 1:
            logger.warn(
                "Found multiple LibraryTasks with the same unique id",
                unique_task_id=unique_task_id,
                library_tasks=list(map(lambda lt: lt.id, library_tasks)),
            )

        return library_tasks[0]

    async def get_library_tasks_by_activity_group_id(
        self,
        activity_group_ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> dict[uuid.UUID, list[LibraryTask]]:
        # TODO: Check if this should be included in the get_library_tasks main method. Seems a bit duplicated.
        statement: SelectOfScalar[tuple[LibraryTask, list[uuid.UUID]]] = select(
            LibraryTask,
            func.array_agg(LibraryTaskActivityGroup.activity_group_id).label(
                "activity_group_ids"
            ),
        )  # type: ignore
        statement = statement.where(
            LibraryTask.id == LibraryTaskActivityGroup.library_task_id
        ).where(col(LibraryTaskActivityGroup.activity_group_id).in_(activity_group_ids))

        if tenant_id:
            statement = (
                statement.where(WorkTypeTaskLink.work_type_id == WorkType.id)
                .where(WorkType.tenant_id == tenant_id)
                .where(LibraryTask.id == WorkTypeTaskLink.task_id)
            )

        statement = statement.group_by(LibraryTask.id)
        statement = set_order_by(LibraryTask, statement, order_by=order_by)

        result: dict[uuid.UUID, list[LibraryTask]] = {i: [] for i in activity_group_ids}
        for library_task, group_ids in (await self.session.exec(statement)).all():
            for activity_group_id in group_ids:
                result[activity_group_id].append(library_task)
        return result

    async def _convert_constaintname_to_fieldname(self, constraint_name: str) -> str:
        return "id" if constraint_name == "library_tasks_pkey" else "unique_task_id"

    async def update(self, library_task: LibraryTask) -> None:
        """
        Updates some properties of a library task.
        Currently, only the name, category, and HESP Score are mutable.
        An error will be thrown if the user tries to change other properties. Alternatively, we can refactor the method signature.

        You also are not able to update archived tasks.
        """
        await super().update(library_task)

    async def register_in_activity_group(
        self, library_task_id: uuid.UUID, library_activity_group_id: uuid.UUID
    ) -> None:
        # TODO: Add some error handling and validation.
        rec = LibraryTaskActivityGroup(
            library_task_id=library_task_id, activity_group_id=library_activity_group_id
        )
        await self._activity_groups_manager.create(rec)

    async def unregister_in_activity_group(
        self, library_task_id: uuid.UUID, library_activity_group_id: uuid.UUID
    ) -> None:
        # TODO: Add some error handling and validation.
        rec = LibraryTaskActivityGroup(
            library_task_id=library_task_id, activity_group_id=library_activity_group_id
        )
        await self._activity_groups_manager.delete(rec)

    async def _execute_library_task_queries(
        self,
        statement: SelectOfScalar[LibraryTask],
        conditions: list,
        after: uuid.UUID | None = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[LibraryTask]:
        """
        Helper method to execute library task queries with common conditions and pagination.
        """
        if not allow_archived:
            conditions.append(col(LibraryTask.archived_at).is_(None))

        if conditions:
            logger.debug(f"conditions --> {conditions}")
            statement = statement.where(and_(*conditions))

        if order_by:
            statement = set_order_by(LibraryTask, statement, order_by=order_by)
        else:
            statement = statement.order_by(LibraryTask.id)

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibraryTask.id > after)
            if limit is not None:
                statement = statement.limit(limit)

        # To remove duplicate tasks(if any)
        statement = statement.group_by(LibraryTask)

        tasks = (await self.session.exec(statement)).all()
        logger.debug(f"total tasks fetched --> {len(tasks)}")
        return tasks
