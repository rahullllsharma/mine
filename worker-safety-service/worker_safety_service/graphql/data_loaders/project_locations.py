import datetime
import functools
import uuid
from collections import defaultdict
from typing import Optional, Sequence

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.graphql.data_loaders.activities import TenantActivityLoader
from worker_safety_service.graphql.data_loaders.utils import create_order_by_hash
from worker_safety_service.graphql.data_loaders.work_packages import (
    TenantWorkPackageLoader,
)
from worker_safety_service.models import (
    Activity,
    ActivityCreate,
    BaseHazardCreate,
    BaseHazardEdit,
    DailyReport,
    JobSafetyBriefing,
    LibrarySiteCondition,
    LibraryTask,
    Location,
    ProjectStatus,
    RiskLevel,
    SiteCondition,
    SiteConditionCreate,
    Task,
    TaskCreate,
    User,
)
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import (
    LocationChanged,
    ProjectLocationSiteConditionsChanged,
    TaskChanged,
    TaskDeleted,
)
from worker_safety_service.types import OrderBy


class TenantProjectLocationLoader:
    """
    Given project location ids, load objects
    """

    def __init__(
        self,
        locations_manager: LocationsManager,
        work_package_manager: WorkPackageManager,
        activity_manager: ActivityManager,
        task_manager: TaskManager,
        site_condition_manager: SiteConditionManager,
        daily_reports_manager: DailyReportManager,
        library_manager: LibraryManager,
        risk_model_reactor: RiskModelReactorInterface,
        activity_loader: TenantActivityLoader,
        work_package_loader: TenantWorkPackageLoader,
        job_safety_briefing_manager: JobSafetyBriefingManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_locations)
        self.with_archived = DataLoader(load_fn=self.load_locations_with_archived)
        self.__locations_manager = locations_manager
        self.__manager = work_package_manager
        self.__work_package_loader = work_package_loader
        self.__activity_manager = activity_manager
        self.__activity_loader = activity_loader
        self.__tasks_manager = task_manager
        self.__site_conditions_manager = site_condition_manager
        self.__daily_reports_manager = daily_reports_manager
        self.__job_safety_briefing_manager = job_safety_briefing_manager
        self.__library_manager = library_manager
        self.__risk_model_reactor = risk_model_reactor
        self.__tasks_map: dict[
            tuple[
                datetime.date | None,
                datetime.date | None,
                datetime.date | None,
                int | None,
            ],
            DataLoader,
        ] = {}
        self.__site_conditions_map: dict[
            tuple[datetime.date | None, int | None],
            DataLoader,
        ] = {}
        self.__daily_reports_map: dict[datetime.date | None, DataLoader] = {}
        self.__job_safety_briefings_map: dict[datetime.date | None, DataLoader] = {}

    async def load_locations_with_archived(
        self, ids: list[uuid.UUID]
    ) -> list[Location | None]:
        items = await self.__locations_manager.get_locations(
            ids=ids,
            tenant_id=self.tenant_id,
            load_project=True,
            with_archived=True,
        )
        keyed_items = {i.id: i for i in items}
        return [keyed_items.get(i) for i in ids]

    async def load_locations(self, ids: list[uuid.UUID]) -> list[Location | None]:
        items = await self.__manager.get_locations_by_id(
            ids,
            tenant_id=self.tenant_id,
            load_project=True,
        )
        return [items.get(i) for i in ids]

    async def get_locations(
        self,
        ids: list[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        risk_level_date: datetime.date | None = None,
        risk_levels: list[RiskLevel] | None = None,
        project_ids: list[uuid.UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[uuid.UUID] | None = None,
        library_division_ids: list[uuid.UUID] | None = None,
        library_project_type_ids: list[uuid.UUID] | None = None,
        work_type_ids: list[uuid.UUID] | None = None,
        contractor_ids: list[uuid.UUID] | None = None,
        supervisor_ids: list[uuid.UUID] | None = None,
        all_supervisor_ids: list[uuid.UUID] | None = None,
        search: str | None = None,
        order_by: list[OrderBy] | None = None,
        load_project: bool = False,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        use_seek_pagination: bool | None = False,
        activity_ids: list[uuid.UUID] | None = None,
        external_keys: list[str] | None = None,
    ) -> list[Location]:
        return await self.__locations_manager.get_locations(
            ids=ids,
            date=date,
            project_ids=project_ids,
            project_status=project_status,
            library_region_ids=library_region_ids,
            library_division_ids=library_division_ids,
            library_project_type_ids=library_project_type_ids,
            work_type_ids=work_type_ids,
            contractor_ids=contractor_ids,
            supervisor_ids=supervisor_ids,
            all_supervisor_ids=all_supervisor_ids,
            search=search,
            order_by=order_by,
            risk_level_date=risk_level_date,
            risk_levels=risk_levels,
            tenant_id=self.tenant_id,
            load_project=load_project,
            limit=limit,
            after=after,
            use_seek_pagination=use_seek_pagination,
            activity_ids=activity_ids,
            external_keys=external_keys,
        )

    async def get_locations_with_risk(
        self,
        ids: list[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        risk_level_date: datetime.date | None = None,
        risk_levels: list[RiskLevel] | None = None,
        project_ids: list[uuid.UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[uuid.UUID] | None = None,
        library_division_ids: list[uuid.UUID] | None = None,
        library_project_type_ids: list[uuid.UUID] | None = None,
        work_type_ids: list[uuid.UUID] | None = None,
        contractor_ids: list[uuid.UUID] | None = None,
        supervisor_ids: list[uuid.UUID] | None = None,
        all_supervisor_ids: list[uuid.UUID] | None = None,
        search: str | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        x_max_map_extent: float | None = None,
        x_min_map_extent: float | None = None,
        y_max_map_extent: float | None = None,
        y_min_map_extent: float | None = None,
        load_project: bool = False,
    ) -> tuple[bool, int, list[tuple[Location, str] | list[Location]]]:
        return await self.__manager.get_locations_with_risk(
            ids=ids,
            date=date,
            project_ids=project_ids,
            project_status=project_status,
            library_region_ids=library_region_ids,
            library_division_ids=library_division_ids,
            library_project_type_ids=library_project_type_ids,
            work_type_ids=work_type_ids,
            contractor_ids=contractor_ids,
            supervisor_ids=supervisor_ids,
            all_supervisor_ids=all_supervisor_ids,
            search=search,
            order_by=order_by,
            limit=limit,
            offset=offset,
            risk_level_date=risk_level_date,
            risk_levels=risk_levels,
            tenant_id=self.tenant_id,
            x_max_map_extent=x_max_map_extent,
            x_min_map_extent=x_min_map_extent,
            y_max_map_extent=y_max_map_extent,
            y_min_map_extent=y_min_map_extent,
            load_project=load_project,
        )

    def tasks(
        self,
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> DataLoader:
        key = (date, start_date, end_date, create_order_by_hash(order_by))
        dataloader = self.__tasks_map.get(key)
        if not dataloader:
            dataloader = self.__tasks_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_tasks,
                    date=date,
                    start_date=start_date,
                    end_date=end_date,
                    filter_start_date=filter_start_date,
                    filter_end_date=filter_end_date,
                    filter_tenant_settings=filter_tenant_settings,
                    order_by=order_by,
                )
            )
        return dataloader

    def site_conditions(
        self,
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> DataLoader:
        key = (date, create_order_by_hash(order_by))
        dataloader = self.__site_conditions_map.get(key)
        if not dataloader:
            dataloader = self.__site_conditions_map[key] = DataLoader(
                load_fn=functools.partial(
                    self.load_site_conditions,
                    date=date,
                    filter_start_date=filter_start_date,
                    filter_end_date=filter_end_date,
                    filter_tenant_settings=filter_tenant_settings,
                    order_by=order_by,
                )
            )
        return dataloader

    def daily_reports(
        self,
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
    ) -> DataLoader:
        dataloader = self.__daily_reports_map.get(date)
        if not dataloader:
            dataloader = self.__daily_reports_map[date] = DataLoader(
                load_fn=functools.partial(
                    self.load_daily_reports,
                    date=date,
                    filter_start_date=filter_start_date,
                    filter_end_date=filter_end_date,
                )
            )
        return dataloader

    def job_safety_briefings(
        self,
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
    ) -> DataLoader:
        dataloader = self.__job_safety_briefings_map.get(date)
        if not dataloader:
            dataloader = self.__job_safety_briefings_map[date] = DataLoader(
                load_fn=functools.partial(
                    self.load_job_safety_briefings,
                    date=date,
                    filter_start_date=filter_start_date,
                    filter_end_date=filter_end_date,
                )
            )
        return dataloader

    async def load_tasks(
        self,
        location_ids: list[uuid.UUID],
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> list[list[tuple[LibraryTask, Task]]]:
        tasks = await self.__tasks_manager.get_tasks_by_location(
            location_ids=location_ids,
            date=date,
            start_date=start_date,
            end_date=end_date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )
        return [tasks[i] for i in location_ids]

    async def load_site_conditions(
        self,
        location_ids: list[uuid.UUID],
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        filter_tenant_settings: Optional[bool] = False,
        order_by: list[OrderBy] | None = None,
    ) -> list[list[tuple[LibrarySiteCondition, SiteCondition]]]:
        site_conditions: defaultdict[
            uuid.UUID,
            list[tuple[LibrarySiteCondition, SiteCondition]],
        ] = defaultdict(list)
        for (
            library_site_condition,
            site_condition,
        ) in await self.__site_conditions_manager.get_site_conditions(
            location_ids=location_ids,
            date=date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            order_by=order_by,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        ):
            site_conditions[site_condition.location_id].append(
                (library_site_condition, site_condition)
            )

        return [site_conditions[i] for i in location_ids]

    async def load_daily_reports(
        self,
        location_ids: list[uuid.UUID],
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
    ) -> list[list[DailyReport]]:
        daily_reports = (
            await self.__daily_reports_manager.get_daily_reports_by_location(
                location_ids,
                date=date,
                filter_start_date=filter_start_date,
                filter_end_date=filter_end_date,
                tenant_id=self.tenant_id,
            )
        )
        return [daily_reports[i] for i in location_ids]

    async def load_job_safety_briefings(
        self,
        location_ids: list[uuid.UUID],
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        allow_archived: bool | None = False,
    ) -> list[list[JobSafetyBriefing]]:
        assert allow_archived is not None
        job_safety_briefings = await self.__job_safety_briefing_manager.get_job_safety_briefings_by_location(
            project_location_ids=location_ids,
            date=date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            allow_archived=allow_archived,
            tenant_id=self.tenant_id,
        )

        return [job_safety_briefings[i] for i in location_ids]

    async def create_activity(
        self,
        activity: ActivityCreate,
        user: User,
    ) -> tuple[Activity, list[Task]]:
        created_activity = await self.__activity_loader.create_activity(activity, user)
        return created_activity, created_activity.tasks

    async def create_task(
        self,
        task: TaskCreate,
        user: User,
    ) -> Task:
        if not await self.me.load(task.location_id):
            raise ResourceReferenceException("Project location not found")
        return await self.__tasks_manager.create_task(task, user)

    async def edit_task(
        self,
        db_task: Task,
        hazards: list[BaseHazardEdit],
        user: User,
    ) -> None:
        if not await self.me.load(db_task.location_id):
            raise ResourceReferenceException("Project location not found")
        await self.__tasks_manager.edit_task(db_task, hazards, user)

        await self.__risk_model_reactor.add(TaskChanged(project_task_id=db_task.id))

    async def archive_task(self, db_task: Task, user: User) -> None:
        if not await self.me.load(db_task.location_id):
            raise ResourceReferenceException("Project location not found")
        await self.__tasks_manager.archive_task(db_task, user)

        await self.__risk_model_reactor.add(
            TaskDeleted(
                project_task_id=db_task.id,
            )
        )

    async def create_site_condition(
        self,
        site_condition: SiteConditionCreate,
        hazards: list[BaseHazardCreate],
        user: User,
    ) -> SiteCondition:
        if not await self.me.load(site_condition.location_id):
            raise ResourceReferenceException("Project location not found")

        _site_condition = await self.__site_conditions_manager.create_site_condition(
            site_condition,
            hazards,
            user,
        )

        await self.__risk_model_reactor.add(
            ProjectLocationSiteConditionsChanged(_site_condition.location_id)
        )

        return _site_condition

    async def edit_site_condition(
        self,
        db_site_condition: SiteCondition,
        hazards: list[BaseHazardEdit],
        user: User,
    ) -> None:
        if not await self.me.load(db_site_condition.location_id):
            raise ResourceReferenceException("Project location not found")
        return await self.__site_conditions_manager.edit_site_condition(
            db_site_condition, hazards, user
        )

    async def get_tile(
        self,
        tile_box: tuple[int, int, int],
        ids: list[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        risk_level_date: datetime.date | None = None,
        risk_levels: list[RiskLevel] | None = None,
        project_ids: list[uuid.UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[uuid.UUID] | None = None,
        library_division_ids: list[uuid.UUID] | None = None,
        library_project_type_ids: list[uuid.UUID] | None = None,
        work_type_ids: list[uuid.UUID] | None = None,
        contractor_ids: list[uuid.UUID] | None = None,
        supervisor_ids: list[uuid.UUID] | None = None,
        all_supervisor_ids: list[uuid.UUID] | None = None,
        search: str | None = None,
    ) -> bytes:
        return await self.__manager.get_locations_tile(
            tile_box,
            ids=ids,
            date=date,
            project_ids=project_ids,
            project_status=project_status,
            library_region_ids=library_region_ids,
            library_division_ids=library_division_ids,
            library_project_type_ids=library_project_type_ids,
            work_type_ids=work_type_ids,
            contractor_ids=contractor_ids,
            supervisor_ids=supervisor_ids,
            all_supervisor_ids=all_supervisor_ids,
            search=search,
            risk_level_date=risk_level_date,
            risk_levels=risk_levels,
            tenant_id=self.tenant_id,
        )

    async def create_locations(
        self, locations: Sequence[Location]
    ) -> Sequence[Location]:
        project_ids = set(
            location.project_id
            for location in locations
            if location.project_id is not None
        )

        existing_projects = await self.__work_package_loader.load_projects(
            list(project_ids)
        )
        existing_ids = set()
        for project in existing_projects:
            if project is None:
                raise ResourceReferenceException
            existing_ids.add(project.id)
        if existing_ids != project_ids:
            raise ResourceReferenceException
        for location in locations:
            await self.__risk_model_reactor.add(
                LocationChanged(project_location_id=location.id)
            )
        return await self.__locations_manager.create_locations(locations)

    async def edit_location(
        self, location: Location, geom_changed: bool = False
    ) -> Location:
        location = await self.__locations_manager.edit_location(location, geom_changed)
        await self.__risk_model_reactor.add(
            LocationChanged(project_location_id=location.id)
        )

        return location

    async def archive_locations(self, locations: Sequence[Location]) -> None:
        await self.__locations_manager.archive_locations_rest(locations)
        for location in locations:
            await self.__risk_model_reactor.add(LocationChanged(location.id))
