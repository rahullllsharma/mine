import uuid
from collections import defaultdict
from datetime import date as date_type
from typing import Iterable, Optional

from sqlalchemy import tuple_
from sqlmodel import String, and_, cast, or_, select, update
from sqlmodel.sql.expression import col

from worker_safety_service.dal.audit_events import (
    AuditContext,
    AuditEventType,
    archive_and_register_diffs,
    create_audit_event,
)
from worker_safety_service.dal.hazards import HazardParentManager
from worker_safety_service.dal.library import LibraryFilterType, LibraryManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    BaseControl,
    BaseHazard,
    BaseHazardEdit,
    LibraryControl,
    LibraryHazard,
    LibraryTask,
    Location,
    Task,
    TaskControl,
    TaskCreate,
    TaskHazard,
    User,
    WorkPackage,
    set_column_order_by,
    set_item_order_by,
    unique_order_by_fields,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibraryControlSettings,
    TenantLibraryHazardSettings,
    TenantLibraryTaskSettings,
)
from worker_safety_service.types import (
    LibraryTaskOrderByField,
    OrderBy,
    TaskOrderByField,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)

LibraryTaskOrderByFields = {i.value for i in LibraryTaskOrderByField if i.value != "id"}


class TaskManager(HazardParentManager):
    def __init__(self, session: AsyncSession, library_manager: LibraryManager):
        self.session = session
        self.library_manager = library_manager

    ################################################################################
    # Fetching Tasks
    ################################################################################

    async def get_tasks(
        self,
        *,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        activities_ids: list[uuid.UUID] | None = None,
        activity_external_keys: list[str] | None = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        date: Optional[date_type] = None,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        filter_start_date: Optional[date_type] = None,
        filter_end_date: Optional[date_type] = None,
        library_task_id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        filter_tenant_settings: Optional[bool] = False,
        with_archived: bool = False,
    ) -> list[tuple[LibraryTask, Task]]:
        """
        Retrieve project location tasks
        """

        if location_ids is not None and not location_ids:
            return []
        elif activities_ids is not None and not activities_ids:
            return []
        elif ids is not None and not ids:
            return []
        elif activity_external_keys is not None and not activity_external_keys:
            return []

        statement = select(LibraryTask, Task).where(
            LibraryTask.id == Task.library_task_id
        )

        # Joins
        if tenant_id or (
            order_by
            and any(i.field == TaskOrderByField.PROJECT_NAME.value for i in order_by)
        ):
            statement = statement.join(Location).join(WorkPackage)
        elif order_by and any(
            i.field == TaskOrderByField.PROJECT_LOCATION_NAME.value for i in order_by
        ):
            statement = statement.join(Location)
        if activity_external_keys:
            statement = statement.join(
                Activity, onclause=Activity.id == Task.activity_id
            )
        if filter_tenant_settings:
            statement = statement.join(
                TenantLibraryTaskSettings,
                onclause=TenantLibraryTaskSettings.library_task_id
                == Task.library_task_id,
            ).where(TenantLibraryTaskSettings.tenant_id == tenant_id)

        # Filters
        if not with_archived:
            statement = statement.where(col(Task.archived_at).is_(None))
        if tenant_id:
            statement = statement.where(WorkPackage.tenant_id == tenant_id)
        if ids:
            statement = statement.where(col(Task.id).in_(ids))
        if location_ids:
            statement = statement.where(col(Task.location_id).in_(location_ids))
        if activities_ids:
            statement = statement.where(col(Task.activity_id).in_(activities_ids))
        if activity_external_keys:
            statement = statement.where(
                col(Activity.external_key).in_(activity_external_keys)
            )
        if date or start_date or end_date or filter_start_date or filter_end_date:
            statement = statement.where(Task.activity_id == Activity.id)
        if date:
            assert_date(date)
            statement = statement.where(Activity.start_date <= date).where(
                Activity.end_date >= date
            )
        if start_date:
            assert_date(start_date)
            statement = statement.where(Activity.end_date >= start_date)
        if end_date:
            assert_date(end_date)
            statement = statement.where(Activity.start_date <= end_date)

        if filter_start_date and filter_end_date:
            assert_date(filter_start_date)
            assert_date(filter_end_date)
            statement = statement.where(
                or_(
                    and_(
                        Activity.start_date >= filter_start_date,
                        Activity.start_date <= filter_end_date,
                    ),
                    and_(
                        Activity.end_date >= filter_start_date,
                        Activity.end_date <= filter_end_date,
                    ),
                    and_(
                        Activity.start_date <= filter_start_date,
                        Activity.end_date >= filter_end_date,
                    ),
                    and_(
                        Activity.start_date <= filter_end_date,
                        Activity.end_date >= filter_end_date,
                    ),
                )
            )

        if library_task_id:
            statement = statement.where(Task.library_task_id == library_task_id)

        # Search
        if search:
            # ignore spaces
            search = f'%{search.replace(" ", "%").lower()}%'
            search_filters = [
                col(LibraryTask.name).ilike(search),
                col(LibraryTask.category).ilike(search),
                cast(col(Task.status), String).ilike(search),
            ]
            # Don't want to replace all hyphens with underscores, but if the
            # search comes in as "In-Progress" it would not work if we don't
            # add in searching for the underscored "in_progress"
            if search == "in-progress":
                search_filters.append(
                    cast(col(Task.status), String).ilike("in_progress")
                )

            statement = statement.filter(or_(*search_filters))

        # Order by
        for order_by_item in unique_order_by_fields(order_by):
            if order_by_item.field in LibraryTaskOrderByFields:
                statement = set_item_order_by(statement, LibraryTask, order_by_item)
            elif order_by_item.field == TaskOrderByField.PROJECT_NAME.value:
                statement = set_column_order_by(
                    statement, WorkPackage.name, order_by_item.direction
                )
            elif order_by_item.field == TaskOrderByField.PROJECT_LOCATION_NAME.value:
                statement = set_column_order_by(
                    statement, Location.name, order_by_item.direction
                )
            else:
                statement = set_item_order_by(statement, Task, order_by_item)

        # Pagination
        if limit is not None:
            statement = statement.limit(limit)
        if after is not None:
            statement = statement.where(Task.id > after)
        if limit is not None or after is not None:
            statement = statement.order_by(Task.id)

        return (await self.session.exec(statement)).all()

    async def get_tasks_by_location(
        self,
        location_ids: list[uuid.UUID],
        date: Optional[date_type] = None,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        filter_start_date: Optional[date_type] = None,
        filter_end_date: Optional[date_type] = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        filter_tenant_settings: Optional[bool] = False,
    ) -> defaultdict[uuid.UUID, list[tuple[LibraryTask, Task]]]:
        items: defaultdict[uuid.UUID, list[tuple[LibraryTask, Task]]] = defaultdict(
            list
        )
        for library_task, task in await self.get_tasks(
            location_ids=location_ids,
            date=date,
            start_date=start_date,
            end_date=end_date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            items[task.location_id].append((library_task, task))
        return items

    async def get_tasks_by_activity(
        self,
        activities_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
        date: Optional[date_type] = None,
        tenant_id: Optional[uuid.UUID] = None,
        filter_tenant_settings: Optional[bool] = False,
    ) -> defaultdict[uuid.UUID, list[Task]]:
        items: defaultdict[uuid.UUID, list[Task]] = defaultdict(list)
        for _, task in await self.get_tasks(
            activities_ids=activities_ids,
            date=date,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            assert task.activity_id
            items[task.activity_id].append(task)
        return items

    async def get_task(
        self,
        task_id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> Optional[tuple[LibraryTask, Task]]:
        statement = (
            select(LibraryTask, Task)
            .where(LibraryTask.id == Task.library_task_id)
            .where(Task.id == task_id)
            .where(col(Task.archived_at).is_(None))
        )

        if tenant_id:
            statement = (
                statement.join(Location)
                .join(WorkPackage)
                .where(WorkPackage.tenant_id == tenant_id)
            )

        return (await self.session.exec(statement)).first()

    async def get_task_with_location(
        self,
        task_id: uuid.UUID,
    ) -> Optional[tuple[LibraryTask, Task, Location]]:
        statement = (
            select(LibraryTask, Task, Location)
            .where(LibraryTask.id == Task.library_task_id)
            .where(Task.id == task_id)
            .where(col(Task.archived_at).is_(None))
            .join(Location)
        )

        return (await self.session.exec(statement)).first()

    ################################################################################
    # Creating Tasks
    ################################################################################
    async def validate_tasks(
        self, tasks: list[TaskCreate], tenant_id: uuid.UUID
    ) -> tuple[list[TaskCreate], list[Task]]:
        """Verify and fix issues related to Task Creation

        start_date, end_date, and location_id are managed on Activities
        but still required in some places to be on Task objects.
        This method populates that activity data on Tasks to support those usages.

        We also do not support creating multiple tasks with the same library_task_id
        on an activity. Split the `TaskCreate` objects into those that need to be created
        and those which already exist (are duplicate)
        """
        if any(t.activity_id is None for t in tasks):
            raise ResourceReferenceException("Task must relate to an activity")
        activity_ids = {t.activity_id for t in tasks if t.activity_id}

        # remove duplicate create objects
        duplicate_check = set()
        to_create: list[TaskCreate] = []
        for task in tasks:
            key = (task.activity_id, task.library_task_id)
            if key not in duplicate_check:
                duplicate_check.add(key)
                to_create.append(task)
        tasks = to_create

        # populate activity data
        get_activities = (
            select(Activity)
            .join(Location)
            .join(WorkPackage)
            .where(col(Activity.id).in_(activity_ids))
            .where(WorkPackage.tenant_id == tenant_id)
        )
        activities = (await self.session.exec(get_activities)).all()
        if len(activity_ids) != len(activities):
            raise ResourceReferenceException("Activity not found")

        activities_by_id = {a.id: a for a in activities}
        for task in tasks:
            if task.activity_id:
                activity = activities_by_id[task.activity_id]
                task.location_id = activity.location_id
                task.start_date = activity.start_date
                task.end_date = activity.end_date

        # filter into new and duplicate entries
        get_duplicate_tasks = select(Task).filter(
            # activity_id will exist per the check at start of method
            tuple_(Task.activity_id, Task.library_task_id).in_(  # type: ignore
                {(t.activity_id, t.library_task_id) for t in tasks}
            )
        )
        existing_tasks = {
            (t.activity_id, t.library_task_id): t
            for t in (await self.session.exec(get_duplicate_tasks)).all()
        }

        duplicate: list[Task] = []
        duplicate.extend(existing_tasks.values())
        tasks = [
            task
            for task in tasks
            if (task.activity_id, task.library_task_id) not in existing_tasks.keys()
        ]

        return tasks, duplicate

    async def create_tasks(
        self, tasks: list[TaskCreate], user: User | None, db_commit: bool = True
    ) -> list[Task]:
        if user is None and any(task.hazards for task in tasks):
            raise ValueError("User required for customized hazards")

        db_tasks = [Task.from_orm(task) for task in tasks]
        self.session.add_all(db_tasks)

        with self.session.no_autoflush:
            for db_task, task in zip(db_tasks, tasks):
                library_task = await self.session.get(LibraryTask, task.library_task_id)
                if library_task:
                    is_critical = library_task.is_critical
                    activity = await self.session.get(Activity, task.activity_id)
                    if activity:
                        activity.is_critical = is_critical
                        self.session.add(activity)

                await self.create_hazards(
                    db_task.id,
                    db_task.library_task_id,
                    task.hazards,
                    user,
                )

        if db_commit:
            create_audit_event(self.session, AuditEventType.task_created, user)
            await self.session.commit()
        logger.info(
            "Project location tasks created",
            tasks_count=str(len(db_tasks)),
            by_user_id=str(user.id if user else "system"),
        )
        return db_tasks

    async def create_task(
        self,
        task: TaskCreate,
        user: User | None,
        db_commit: bool = True,
    ) -> Task:
        tasks = await self.create_tasks([task], user, db_commit)
        assert len(tasks) == 1
        return tasks[0]

    ################################################################################
    # Updating Tasks
    ################################################################################
    async def edit_task(
        self,
        db_task: Task,
        hazards: list[BaseHazardEdit],
        user: User,
    ) -> None:
        with self.session.no_autoflush:
            hazards_updated = await self.edit_hazards(db_task.id, hazards, user)

        if hazards_updated:
            create_audit_event(self.session, AuditEventType.task_updated, user)
            await self.session.commit()
            logger.info(
                "Project location task updated",
                location_id=str(db_task.location_id),
                task_id=str(db_task.id),
                by_user_id=str(user.id),
            )

    ################################################################################
    # Fetching Hazards
    ################################################################################

    async def get_hazards(
        self,
        *,
        ids: list[uuid.UUID] | None = None,
        task_ids: list[uuid.UUID] | None = None,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        with_archived: bool = False,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibraryHazard, TaskHazard]]:
        """
        Retrieve hazards for a project location task
        """
        if task_ids is not None and not task_ids:
            return []
        elif ids is not None and not ids:
            return []

        statement = select(LibraryHazard, TaskHazard).where(
            LibraryHazard.id == TaskHazard.library_hazard_id
        )

        if not with_archived:
            statement = statement.where(col(TaskHazard.archived_at).is_(None))
        if ids:
            statement = statement.where(col(TaskHazard.id).in_(ids))
        if task_ids:
            statement = statement.where(col(TaskHazard.task_id).in_(task_ids))
        if is_applicable is not None:
            statement = statement.where(
                col(TaskHazard.is_applicable).is_(is_applicable)
            )
        if tenant_id:
            statement = (
                statement.where(TaskHazard.task_id == Task.id)
                .where(Task.location_id == Location.id)
                .where(Location.project_id == WorkPackage.id)
                .where(WorkPackage.tenant_id == tenant_id)
            )

        if filter_tenant_settings:
            statement = statement.join(
                TenantLibraryHazardSettings,
                onclause=TenantLibraryHazardSettings.library_hazard_id
                == LibraryHazard.id,
            ).where(TenantLibraryHazardSettings.tenant_id == tenant_id)

        if order_by:
            for order_by_item in unique_order_by_fields(order_by):
                if order_by_item.field == "id":
                    statement = set_item_order_by(statement, TaskHazard, order_by_item)
                else:
                    statement = set_item_order_by(
                        statement, LibraryHazard, order_by_item
                    )
        else:
            statement = statement.order_by(TaskHazard.position)

        return (await self.session.exec(statement)).all()

    async def get_hazards_by_task(
        self,
        task_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> defaultdict[uuid.UUID, list[tuple[LibraryHazard, TaskHazard]]]:
        items: defaultdict[
            uuid.UUID, list[tuple[LibraryHazard, TaskHazard]]
        ] = defaultdict(list)
        for library_hazard, hazard in await self.get_hazards(
            task_ids=task_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            items[hazard.task_id].append((library_hazard, hazard))
        return items

    ################################################################################
    # Fetching Controls
    ################################################################################

    async def get_controls(
        self,
        ids: list[uuid.UUID] | None = None,
        task_id: uuid.UUID | None = None,
        hazard_ids: list[uuid.UUID] | None = None,
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        with_archived: bool = False,
        filter_tenant_settings: bool | None = False,
    ) -> list[tuple[LibraryControl, TaskControl]]:
        """
        Retrieve controls for a project location task
        """
        if hazard_ids is not None and not hazard_ids:
            return []
        elif ids is not None and not ids:
            return []

        statement = select(LibraryControl, TaskControl).where(
            LibraryControl.id == TaskControl.library_control_id
        )
        if not with_archived:
            statement = statement.where(col(TaskControl.archived_at).is_(None))

        if ids:
            statement = statement.where(col(TaskControl.id).in_(ids))
        if task_id or tenant_id:
            statement = statement.where(TaskControl.task_hazard_id == TaskHazard.id)

        if is_applicable is not None:
            statement = statement.where(
                col(TaskControl.is_applicable).is_(is_applicable)
            )
        if task_id:
            statement = statement.where(TaskHazard.task_id == task_id)
        if tenant_id:
            statement = (
                statement.where(TaskHazard.task_id == Task.id)
                .where(Task.location_id == Location.id)
                .where(Location.project_id == WorkPackage.id)
                .where(WorkPackage.tenant_id == tenant_id)
            )
        if hazard_ids:
            statement = statement.where(col(TaskControl.task_hazard_id).in_(hazard_ids))

        if filter_tenant_settings:
            statement = statement.join(
                TenantLibraryControlSettings,
                onclause=TenantLibraryControlSettings.library_control_id
                == LibraryControl.id,
            ).where(TenantLibraryControlSettings.tenant_id == tenant_id)

        if order_by:
            for order_by_item in unique_order_by_fields(order_by):
                if order_by_item.field == "id":
                    statement = set_item_order_by(statement, TaskControl, order_by_item)
                else:
                    statement = set_item_order_by(
                        statement, LibraryControl, order_by_item
                    )
        else:
            statement = statement.order_by(TaskControl.position)

        return (await self.session.exec(statement)).all()

    async def get_controls_by_hazard(
        self,
        hazard_ids: list[uuid.UUID],
        is_applicable: bool | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: uuid.UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> defaultdict[uuid.UUID, list[tuple[LibraryControl, TaskControl]]]:
        items: defaultdict[
            uuid.UUID, list[tuple[LibraryControl, TaskControl]]
        ] = defaultdict(list)
        for library_control, control in await self.get_controls(
            hazard_ids=hazard_ids,
            is_applicable=is_applicable,
            order_by=order_by,
            tenant_id=tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            items[control.task_hazard_id].append((library_control, control))
        return items

    ################################################################################
    # Archiving Tasks, Hazards, Controls
    ################################################################################

    async def archive_task(self, db_task: Task, user: User | None) -> None:
        with AuditContext(self.session) as audit:
            await self.archive_tasks(task_ids=[db_task.id])
            await audit.create(AuditEventType.task_archived, user)
            await self.session.commit()

        logger.info(
            "Project location task archived",
            location_id=str(db_task.location_id),
            task_id=str(db_task.id),
            by_user_id=str(user.id) if user else "",
        )

    async def archive_tasks_by_activity(
        self, activity_id: uuid.UUID, user: User | None
    ) -> None:
        with AuditContext(self.session) as audit:
            await self.archive_tasks(activity_ids=[activity_id])
            await audit.create(AuditEventType.task_archived, user)
            await self.session.commit()

            logger.info(
                "Tasks archived by activity",
                activity_id=str(activity_id),
                by_user_id=str(user.id) if user else "",
            )

    async def archive_tasks(
        self,
        *,
        task_ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        activity_ids: list[uuid.UUID] | None = None,
    ) -> None:
        statement = update(Task).where(col(Task.archived_at).is_(None))
        if task_ids is not None:
            statement = statement.where(col(Task.id).in_(task_ids))
        elif location_ids is not None:
            statement = statement.where(col(Task.location_id).in_(location_ids))
        elif activity_ids is not None:
            statement = statement.where(col(Task.activity_id).in_(activity_ids))
        else:
            raise NotImplementedError()

        # Archive tasks
        await archive_and_register_diffs(self.session, statement, Task)

        # Archive hazards and controls
        await self.archive_hazards(
            location_ids=location_ids, task_ids=task_ids, activity_ids=activity_ids
        )

    async def unarchive_tasks(
        self,
        db_tasks: list[Task],
    ) -> list[Task]:
        """To avoid duplicate tasks (multiple tasks in an activity with the same library_task_id)
        allow an "unarchive" to restore existing tasks with the desired library_task_id
        """
        for task in db_tasks:
            task.archived_at = None
        await self.session.commit()
        return db_tasks

    async def archive_hazards(
        self,
        *,
        hazard_ids: Optional[Iterable[uuid.UUID]] = None,
        task_ids: Optional[Iterable[uuid.UUID]] = None,
        location_ids: Optional[Iterable[uuid.UUID]] = None,
        activity_ids: list[uuid.UUID] | None = None,
    ) -> None:
        statement = update(TaskHazard).where(col(TaskHazard.archived_at).is_(None))
        if hazard_ids is not None:
            statement = statement.where(col(TaskHazard.id).in_(hazard_ids))
        elif task_ids is not None:
            statement = statement.where(col(TaskHazard.task_id).in_(task_ids))
        elif location_ids is not None:
            statement = statement.where(TaskHazard.task_id == Task.id).where(
                col(Task.location_id).in_(location_ids)
            )
        elif activity_ids is not None:
            statement = statement.where(TaskHazard.task_id == Task.id).where(
                col(Task.activity_id).in_(activity_ids)
            )
        else:
            raise NotImplementedError()

        # Archive hazards
        await archive_and_register_diffs(self.session, statement, TaskHazard)

        # Archive controls
        await self.archive_controls(
            hazard_ids=hazard_ids,
            task_ids=task_ids,
            location_ids=location_ids,
            activity_ids=activity_ids,
        )

    async def archive_controls(
        self,
        *,
        control_ids: Optional[Iterable[uuid.UUID]] = None,
        hazard_ids: Optional[Iterable[uuid.UUID]] = None,
        task_ids: Optional[Iterable[uuid.UUID]] = None,
        location_ids: Optional[Iterable[uuid.UUID]] = None,
        activity_ids: list[uuid.UUID] | None = None,
    ) -> None:
        statement = update(TaskControl).where(col(TaskControl.archived_at).is_(None))
        if control_ids is not None:
            statement = statement.where(col(TaskControl.id).in_(control_ids))
        elif hazard_ids is not None:
            statement = statement.where(col(TaskControl.task_hazard_id).in_(hazard_ids))
        else:
            statement = statement.where(TaskControl.task_hazard_id == TaskHazard.id)
            if task_ids is not None:
                statement = statement.where(col(TaskHazard.task_id).in_(task_ids))
            elif location_ids is not None:
                statement = statement.where(TaskHazard.task_id == Task.id).where(
                    col(Task.location_id).in_(location_ids)
                )
            elif activity_ids is not None:
                statement = statement.where(TaskHazard.task_id == Task.id).where(
                    col(Task.activity_id).in_(activity_ids)
                )
            else:
                raise NotImplementedError()

        await archive_and_register_diffs(self.session, statement, TaskControl)

    ################################################################################
    # HazardParentManager impl
    ################################################################################

    filter_type = LibraryFilterType.TASK

    async def get_recommendations(
        self, library_reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> defaultdict[uuid.UUID, set[uuid.UUID]]:
        recommendations: defaultdict[uuid.UUID, set[uuid.UUID]] = defaultdict(set)
        for recommendation in await self.library_manager.get_task_recommendations(
            library_reference_id, tenant_id
        ):
            recommendations[recommendation.library_hazard_id].add(
                recommendation.library_control_id
            )
        return recommendations

    def hazard_orm(
        self,
        reference_id: uuid.UUID,
        library_hazard_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseHazard:
        return TaskHazard(
            task_id=reference_id,
            library_hazard_id=library_hazard_id,
            is_applicable=is_applicable,
            user_id=user_id,
            position=position,
        )

    def control_orm(
        self,
        hazard_id: uuid.UUID,
        library_control_id: uuid.UUID,
        is_applicable: bool,
        user_id: Optional[uuid.UUID],
        position: int,
    ) -> BaseControl:
        return TaskControl(
            task_hazard_id=hazard_id,
            library_control_id=library_control_id,
            is_applicable=is_applicable,
            user_id=user_id,
            position=position,
        )

    async def get_hazards_and_controls(
        self, reference_id: uuid.UUID, tenant_id: uuid.UUID | None = None
    ) -> tuple[
        dict[uuid.UUID, BaseHazard],
        defaultdict[uuid.UUID, dict[uuid.UUID, BaseControl]],
    ]:
        """
        Retrieve hazards and controls for a given task id, optionally filtered by tenant_id.
        """
        filter_tenant_settings: bool = (
            True if tenant_id else False
        )  # Check if filtering by tenant settings is needed based on the existence of tenant_id
        db_hazards: dict[uuid.UUID, BaseHazard] = {
            h.id: h
            for _, h in await self.get_hazards(
                task_ids=[reference_id],
                filter_tenant_settings=filter_tenant_settings,
                tenant_id=tenant_id,
            )
        }

        db_hazards_controls: defaultdict[
            uuid.UUID, dict[uuid.UUID, BaseControl]
        ] = defaultdict(dict)
        for _, db_hazard_control in await self.get_controls(
            task_id=reference_id,
            filter_tenant_settings=filter_tenant_settings,
            tenant_id=tenant_id,
        ):
            db_hazards_controls[db_hazard_control.task_hazard_id][
                db_hazard_control.id
            ] = db_hazard_control

        return db_hazards, db_hazards_controls
