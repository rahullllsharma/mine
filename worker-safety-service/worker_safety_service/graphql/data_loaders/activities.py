import datetime
import functools
import uuid
from datetime import date, timedelta
from typing import Optional, Sequence

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import (
    ACTIVITY_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.data_loaders.utils import (
    create_order_by_hash,
    create_tasks_hash,
)
from worker_safety_service.models import (
    Activity,
    ActivityBase,
    ActivityCreate,
    ActivityEdit,
    AddActivityTasks,
    LibraryActivityType,
    Location,
    RemoveActivityTasks,
    Task,
    User,
)
from worker_safety_service.models.library import LibraryActivityGroup
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import (
    ActivityChanged,
    ActivityDeleted,
    TaskChanged,
)
from worker_safety_service.types import OrderBy


class TenantActivityLoader:
    """
    Given project location activity ids, load objects
    """

    def __init__(
        self,
        activity_manager: ActivityManager,
        task_manager: TaskManager,
        library_manager: LibraryManager,
        risk_model_reactor: RiskModelReactorInterface,
        locations_manager: LocationsManager,
        configurations_manager: ConfigurationsManager,
        tenant_id: uuid.UUID,
    ):
        self.__activity_manager = activity_manager
        self.__task_manager = task_manager
        self.__library_manager = library_manager
        self.__risk_model_reactor = risk_model_reactor
        self.__locations_manager = locations_manager
        self.__configurations_manager = configurations_manager
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_activities)
        self.by_id = DataLoader(load_fn=self.load_activity_by_id)
        self.task_count = DataLoader(load_fn=self.load_task_count)
        self.__activities_map: dict[
            tuple[
                date | None,
                date | None,
                date | None,
                int | None,
            ],
            DataLoader,
        ] = {}
        self.__tasks_map: dict[
            int | None,
            DataLoader,
        ] = {}

    def tasks(
        self,
        date: Optional[datetime.date] = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> DataLoader:
        key = create_tasks_hash(order_by, date)
        dataloader = self.__tasks_map.get(key)
        if not dataloader:
            dataloader = self.__tasks_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_tasks,
                    date=date,
                    order_by=order_by,
                    filter_tenant_settings=filter_tenant_settings,
                )
            )
        return dataloader

    async def load_tasks(
        self,
        activity_ids: list[uuid.UUID],
        date: Optional[datetime.date] = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> list[list[Task]]:
        items = await self.__task_manager.get_tasks_by_activity(
            activity_ids,
            date=date,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [items.get(i) or [] for i in activity_ids]

    async def load_task_count(self, activity_ids: list[uuid.UUID]) -> list[int]:
        items = await self.__task_manager.get_tasks_by_activity(
            activity_ids, tenant_id=self.tenant_id
        )
        return [len(items.get(i) or []) for i in activity_ids]

    def by_location(
        self,
        date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> DataLoader:
        key = (date, start_date, end_date, create_order_by_hash(order_by))
        dataloader = self.__activities_map.get(key)
        if not dataloader:
            dataloader = self.__activities_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.get_activities_by_location,
                    date=date,
                    start_date=start_date,
                    end_date=end_date,
                    filter_start_date=filter_start_date,
                    filter_end_date=filter_end_date,
                    order_by=order_by,
                )
            )
        return dataloader

    async def load_activities(self, ids: list[uuid.UUID]) -> list[Optional[Activity]]:
        activities = await self.__activity_manager.get_activities_by_id(
            ids=ids, tenant_id=self.tenant_id
        )
        return [activities.get(i) for i in ids]

    async def load_activity_by_id(
        self, ids: list[uuid.UUID]
    ) -> list[Optional[LibraryActivityGroup]]:
        activities = []
        for id in ids:
            activity = await self.__activity_manager.get_activity_group_by_id(id=id)
            activities.append(activity)
        return activities

    async def get_activities(
        self,
        ids: Optional[list[uuid.UUID]] = None,
        location_ids: Optional[list[uuid.UUID]] = None,
        external_keys: Optional[list[str]] = None,
        date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        with_archived: bool = False,
        load_work_package: bool = False,
        order_by: Optional[list[OrderBy]] = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
    ) -> list[Activity]:
        return await self.__activity_manager.get_activities(
            ids=ids,
            tenant_id=self.tenant_id,
            location_ids=location_ids,
            external_keys=external_keys,
            date=date,
            start_date=start_date,
            end_date=end_date,
            with_archived=with_archived,
            load_work_package=load_work_package,
            order_by=order_by,
            limit=limit,
            after=after,
        )

    async def get_activities_by_location(
        self,
        location_ids: list[uuid.UUID],
        date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        order_by: Optional[list[OrderBy]] = None,
    ) -> list[list[Activity]]:
        activities_by_location = (
            await self.__activity_manager.get_activities_by_location(
                location_ids=location_ids,
                tenant_id=self.tenant_id,
                date=date,
                start_date=start_date,
                end_date=end_date,
                filter_start_date=filter_start_date,
                filter_end_date=filter_end_date,
                order_by=order_by,
            )
        )

        return [activities_by_location.get(i) or [] for i in location_ids]

    async def validate_activities(
        self,
        activities: Sequence[ActivityBase],
    ) -> None:
        location_ids = [a.location_id for a in activities]
        activity_type_ids = [
            a.library_activity_type_id for a in activities if a.library_activity_type_id
        ]

        location_data: dict[
            uuid.UUID, Location
        ] = await self.__locations_manager.get_locations_by_id(
            location_ids,
            tenant_id=self.tenant_id,
            load_project=True,
        )
        activity_types: dict[
            uuid.UUID, LibraryActivityType
        ] = await self.__library_manager.get_activity_types_by_id(
            activity_type_ids, tenant_id=self.tenant_id
        )

        for activity in activities:
            location = location_data.get(activity.location_id)
            work_package = location.project if location else None
            if not location:
                raise ResourceReferenceException("Project location not found")
            elif not work_package:
                raise ResourceReferenceException("Work Package not found")
            elif (
                activity.library_activity_type_id
                and activity.library_activity_type_id not in activity_types
            ):
                raise ResourceReferenceException(
                    "Activity type not found or invalid for tenant"
                )

            if activity.start_date < work_package.start_date:
                raise ValueError(
                    f"Activity start date {activity.start_date} should be bigger than work package start date {work_package.start_date}"
                )
            elif activity.end_date > work_package.end_date:
                raise ValueError(
                    f"Activity end date {activity.end_date} should be lower than work package end date {work_package.end_date}"
                )

    async def trigger_activities_changed(self, activities: Sequence[Activity]) -> None:
        for activity in activities:
            await self.__risk_model_reactor.add(
                ActivityChanged(activity_id=activity.id)
            )
            for task in activity.tasks:
                await self.__risk_model_reactor.add(
                    TaskChanged(project_task_id=task.id)
                )

    async def create_activities(
        self, activities: Sequence[ActivityCreate], user: User | None = None
    ) -> list[Activity]:
        await self.validate_activities(activities)
        await self.__configurations_manager.validate_models(
            ACTIVITY_CONFIG, activities, self.tenant_id
        )
        created_activities = await self.__activity_manager.create_activities(
            activities,
            user=user,
            db_commit=True,
        )
        await self.trigger_activities_changed(created_activities)
        return created_activities

    async def create_activity(
        self, activity: ActivityCreate, user: User | None = None
    ) -> Activity:
        return (await self.create_activities([activity], user=user))[0]

    async def update_activity(
        self,
        edited_activity: ActivityEdit,
        user: User | None = None,
    ) -> Activity | None:
        db_activities = await self.get_activities(ids=[edited_activity.id])
        if not db_activities:
            raise ResourceReferenceException("Activity not found")

        activity, _ = await self.edit_activity(db_activities[0], edited_activity, user)
        return activity

    async def edit_activity(
        self,
        db_activity: Activity,
        edited_activity: ActivityEdit,
        user: User | None,
    ) -> tuple[Optional[Activity], list[Task]]:
        await self.validate_activities([edited_activity])
        await self.__configurations_manager.validate_model(
            ACTIVITY_CONFIG, edited_activity, self.tenant_id
        )
        updated_activity, updated_tasks = await self.__activity_manager.edit_activity(
            db_activity=db_activity, edited_activity=edited_activity, user=user
        )

        if updated_activity:
            await self.trigger_activities_changed([updated_activity])
        return updated_activity, updated_tasks

    def get_critical_activities_for_date_range(
        self,
        activities: list[Activity],
        from_date: datetime.date,
        to_date: datetime.date,
    ) -> dict[datetime.date, bool]:
        result: dict[datetime.date, bool] = {}

        current_date = from_date
        while current_date <= to_date:
            is_critical = any(
                activity.is_critical
                for activity in activities
                if activity.start_date <= current_date <= activity.end_date
            )
            result[current_date] = is_critical

            current_date += timedelta(days=1)

        return result

    async def archive_activity(
        self,
        db_activity: Activity,
        user: User | None,
    ) -> bool:
        activity_archive_is_successful = await self.__activity_manager.archive_activity(
            db_activity=db_activity, user=user
        )

        await self.__risk_model_reactor.add(ActivityDeleted(activity_id=db_activity.id))

        return activity_archive_is_successful

    async def delete_activity(
        self,
        id: uuid.UUID,
        user: User | None,
    ) -> bool:
        activities = await self.get_activities(ids=[id])
        if not activities:
            raise ResourceReferenceException("The activity is not found!")
        activity = activities[0]
        if activity.archived_at is not None:
            return True

        return await self.archive_activity(activities[0], user)

    async def add_new_tasks_to_existing_activity(
        self,
        db_activity: Activity,
        new_tasks: AddActivityTasks,
        user: User | None = None,
    ) -> Activity:
        updated_activity = (
            await self.__activity_manager.add_new_tasks_to_existing_activity(
                db_activity=db_activity,
                new_tasks=new_tasks.tasks_to_be_added,
                user=user,
            )
        )

        if updated_activity:
            await self.trigger_activities_changed([updated_activity])
        return updated_activity

    async def remove_tasks_from_existing_activity(
        self,
        db_activity: Activity,
        task_ids_to_be_removed: RemoveActivityTasks,
        user: User | None = None,
    ) -> Activity:
        tasks_to_be_removed = await self.get_tasks_to_be_removed_from_activity(
            task_ids_to_be_removed.task_ids_to_be_removed
        )
        updated_activity = (
            await self.__activity_manager.remove_tasks_from_existing_activity(
                db_activity=db_activity, tasks=tasks_to_be_removed, user=user
            )
        )

        if updated_activity:
            await self.trigger_activities_changed([updated_activity])
        return updated_activity

    async def get_tasks_to_be_removed_from_activity(
        self, task_ids_to_be_removed: list[uuid.UUID]
    ) -> list[Task]:
        tasks: list[Task] = []
        task_tuples = await self.__task_manager.get_tasks(ids=task_ids_to_be_removed)
        tasks = [tt[1] for tt in task_tuples]
        return tasks
