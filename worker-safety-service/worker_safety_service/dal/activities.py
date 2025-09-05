import uuid
from collections import defaultdict
from datetime import date as date_type
from typing import Optional, Sequence

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager
from sqlmodel import and_, col, or_, select, update

from worker_safety_service.dal.audit_events import (
    AuditContext,
    AuditEventType,
    archive_and_register_diffs,
    create_audit_event,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.utils import merge_new_values_to_original_db_item
from worker_safety_service.exceptions import DuplicateExternalKeyException
from worker_safety_service.models import (
    Activity,
    ActivityCreate,
    ActivityEdit,
    ActivityTaskCreate,
    AsyncSession,
    Location,
    Task,
    TaskCreate,
    User,
    WorkPackage,
    set_order_by,
)
from worker_safety_service.models.library import LibraryActivityGroup
from worker_safety_service.types import OrderBy
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)


class ActivityManager:
    def __init__(
        self,
        session: AsyncSession,
        task_manager: TaskManager,
        configurations_manager: ConfigurationsManager,
    ):
        self.session = session
        self.task_manager = task_manager
        self.configurations_manager = configurations_manager

    async def get_activities(
        self,
        ids: Optional[list[uuid.UUID]] = None,
        location_ids: Optional[list[uuid.UUID]] = None,
        external_keys: Optional[list[str]] = None,
        tenant_id: Optional[uuid.UUID] = None,
        date: Optional[date_type] = None,
        start_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        with_archived: bool = False,
        load_work_package: bool = False,
        filter_start_date: Optional[date_type] = None,
        filter_end_date: Optional[date_type] = None,
        order_by: Optional[list[OrderBy]] = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
    ) -> list[Activity]:
        # Handle default scenarios
        if location_ids is not None and not location_ids:
            return []
        elif ids is not None and not ids:
            return []
        elif external_keys is not None and not external_keys:
            return []

        # Base Select
        statement = select(Activity)

        # Joins
        if tenant_id or load_work_package:
            statement = statement.join(Location).join(WorkPackage)

        if load_work_package:
            statement = statement.options(
                contains_eager(Activity.location).contains_eager(Location.project)
            )

        # Filters
        if not with_archived:
            statement = statement.where(col(Activity.archived_at).is_(None))

        if ids:
            statement = statement.where(col(Activity.id).in_(ids))

        if location_ids:
            statement = statement.where(col(Activity.location_id).in_(location_ids))

        if external_keys:
            statement = statement.where(col(Activity.external_key).in_(external_keys))

        if tenant_id:
            statement = statement.where(WorkPackage.tenant_id == tenant_id)

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

        if order_by:
            statement = set_order_by(Activity, statement, order_by)

        if limit is not None:
            statement = statement.limit(limit)

        if after is not None:
            statement = statement.where(Activity.id > after)

        if limit is not None or after is not None:
            # must order by at least ID if using pagination
            statement = statement.order_by(Activity.id)

        return (await self.session.exec(statement)).all()

    async def get_activity(
        self,
        id: uuid.UUID,
        load_work_package: bool = False,
        with_archived: bool = False,
    ) -> Activity | None:
        activities = await self.get_activities(
            ids=[id],
            load_work_package=load_work_package,
            with_archived=with_archived,
        )
        return activities[0] if activities else None

    async def get_activity_group_by_id(
        self, id: uuid.UUID
    ) -> LibraryActivityGroup | None:
        """
        Purpose of this method is to fetch activty by id independent of project locations
        """
        statement = select(LibraryActivityGroup).where(LibraryActivityGroup.id == id)
        return (await self.session.execute(statement)).scalars().first()

    async def get_activities_by_id(
        self, ids: list[uuid.UUID], tenant_id: Optional[uuid.UUID]
    ) -> dict[uuid.UUID, Activity]:
        return {
            i.id: i for i in await self.get_activities(ids=ids, tenant_id=tenant_id)
        }

    async def get_activities_by_location(
        self,
        location_ids: list[uuid.UUID] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        date: Optional[date_type] = None,
        start_date: Optional[date_type] = None,
        filter_start_date: Optional[date_type] = None,
        filter_end_date: Optional[date_type] = None,
        end_date: Optional[date_type] = None,
        order_by: Optional[list[OrderBy]] = None,
    ) -> dict[uuid.UUID, list[Activity]]:
        activities_map: defaultdict[uuid.UUID, list[Activity]] = defaultdict(list)
        for activity in await self.get_activities(
            location_ids=location_ids,
            tenant_id=tenant_id,
            date=date,
            start_date=start_date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            end_date=end_date,
            order_by=order_by,
        ):
            activities_map[activity.location_id].append(activity)

        return activities_map

    async def create_activities(
        self,
        activities: Sequence[ActivityCreate],
        user: User | None = None,
        db_commit: bool = False,
    ) -> list[Activity]:
        db_activities = [Activity.from_orm(act) for act in activities]
        self.session.add_all(db_activities)
        create_tasks: list[TaskCreate] = []
        # pairing created DB activity with the input data
        for db_activity, activity_input in zip(db_activities, activities):
            create_tasks.extend(
                [
                    TaskCreate(
                        start_date=db_activity.start_date,
                        end_date=db_activity.end_date,
                        status=db_activity.status,
                        location_id=db_activity.location_id,
                        library_task_id=task.library_task_id,
                        hazards=task.hazards,
                        activity_id=db_activity.id,
                    )
                    for task in activity_input.tasks
                ]
            )
        with self.session.no_autoflush:
            created_tasks: list[Task] = await self.task_manager.create_tasks(
                create_tasks,
                user,
                db_commit=False,
            )

        # associate tasks back to activities
        tasks_by_activity: dict[uuid.UUID, list[Task]] = defaultdict(list)
        for created_task in created_tasks:
            if created_task.activity_id:
                tasks_by_activity[created_task.activity_id].append(created_task)
        for created_activity in db_activities:
            created_activity.tasks = tasks_by_activity[created_activity.id]
        create_audit_event(self.session, AuditEventType.activity_created, user)
        if db_commit:
            try:
                await self.session.commit()
            except DBAPIError as db_err:
                if (
                    db_err.orig.args
                    and "ExternalKey must be unique within a Tenant"
                    in db_err.orig.args[0]
                ):
                    raise DuplicateExternalKeyException()
                else:
                    raise db_err
        return db_activities

    async def create_activity(self, activity: ActivityCreate, user: User) -> Activity:
        activities = await self.create_activities([activity], user=user)
        assert len(activities) == 1
        db_activity = activities[0]

        await self.session.commit()
        logger.info(
            "Project location activity created",
            location_id=str(db_activity.location_id),
            activity_id=str(db_activity.id),
            by_user_id=str(user.id),
        )
        return db_activity

    async def edit_activity_tasks(
        self,
        db_activity: Activity,
        changed_keys: set[str],
    ) -> list[Task]:
        """Allow updating task start and end date
        to keep dates consistent between activity and tasks
        """
        if not changed_keys.intersection({"start_date", "end_date"}):
            return []

        statement = select(Task).where(Task.activity_id == db_activity.id)
        tasks = (await self.session.exec(statement)).all()
        if "start_date" in changed_keys:
            for t in tasks:
                t.start_date = db_activity.start_date
        if "end_date" in changed_keys:
            for t in tasks:
                t.end_date = db_activity.end_date
        for task in tasks:
            self.session.add(task)
        return tasks

    async def edit_activity(
        self, db_activity: Activity, edited_activity: ActivityEdit, user: User | None
    ) -> tuple[Optional[Activity], list[Task]]:
        (
            changed_keys,
            modified_db_activity,
        ) = merge_new_values_to_original_db_item(
            db_activity, edited_activity.dict(), ("id",)
        )

        if changed_keys and modified_db_activity:
            create_audit_event(self.session, AuditEventType.activity_updated, user)
            try:
                updated_tasks = await self.edit_activity_tasks(
                    db_activity=db_activity, changed_keys=changed_keys
                )
                await self.session.commit()
            except DBAPIError as db_err:
                if (
                    db_err.orig.args
                    and "ExternalKey must be unique within a Tenant"
                    in db_err.orig.args[0]
                ):
                    raise DuplicateExternalKeyException
                else:
                    raise db_err

            logger.info(
                "Project location activity updated",
                location_id=str(modified_db_activity.location_id),
                activity_id=str(modified_db_activity.id),
                by_user_id=str(user.id) if user else "",
            )
            return Activity.from_orm(edited_activity), [
                Task.from_orm(ut) for ut in updated_tasks
            ]

        return None, []

    async def archive_activity(self, db_activity: Activity, user: User | None) -> bool:
        with AuditContext(self.session) as audit:
            await self.archive_activities(activity_ids=[db_activity.id])
            await audit.create(AuditEventType.activity_archived, user)
            await self.session.commit()

        # Archive tasks associated with activity
        await self.task_manager.archive_tasks_by_activity(
            activity_id=db_activity.id, user=user
        )

        logger.info(
            "Project location activity archived",
            location_id=str(db_activity.location_id),
            activity_id=str(db_activity.id),
            by_user_id=str(user.id) if user else "",
        )

        return True

    async def archive_activities(
        self,
        location_ids: list[uuid.UUID] | None = None,
        activity_ids: list[uuid.UUID] | None = None,
    ) -> bool:
        statement = update(Activity).where(col(Activity.archived_at).is_(None))
        if location_ids is not None:
            statement = statement.where(col(Activity.location_id).in_(location_ids))
        elif activity_ids is not None:
            statement = statement.where(col(Activity.id).in_(activity_ids))
        else:
            raise NotImplementedError()

        # Archive activities
        await archive_and_register_diffs(self.session, statement, Activity)

        return True

    async def add_new_tasks_to_existing_activity(
        self,
        db_activity: Activity,
        new_tasks: list[ActivityTaskCreate],
        user: User | None,
    ) -> Activity:
        create_tasks: list[TaskCreate] = []

        for task in new_tasks:
            create_tasks.append(
                TaskCreate(
                    start_date=db_activity.start_date,
                    end_date=db_activity.end_date,
                    status=db_activity.status,
                    location_id=db_activity.location_id,
                    library_task_id=task.library_task_id,
                    hazards=task.hazards,
                    activity_id=db_activity.id,
                )
            )
        with self.session.no_autoflush:
            created_tasks: list[Task] = await self.task_manager.create_tasks(
                create_tasks,
                user,
                db_commit=False,
            )
            db_activity.tasks.extend(created_tasks)

        create_audit_event(self.session, AuditEventType.activity_updated, user)
        await self.session.commit()
        await self.session.refresh(db_activity)
        return db_activity

    async def remove_tasks_from_existing_activity(
        self,
        db_activity: Activity,
        tasks: list[Task],
        user: User | None,
    ) -> Activity:
        with self.session.no_autoflush:
            for task in tasks:
                if task in db_activity.tasks:
                    db_activity.tasks.remove(task)
        create_audit_event(self.session, AuditEventType.activity_updated, user)
        await self.session.commit()
        await self.session.refresh(db_activity)

        return db_activity
