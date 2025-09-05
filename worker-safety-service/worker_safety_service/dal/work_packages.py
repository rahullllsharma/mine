import uuid
from datetime import date, datetime, timezone
from typing import Optional, Sequence, TypeVar

from sqlalchemy import lateral
from sqlalchemy import select as sa_select
from sqlalchemy import true
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import Label
from sqlmodel import case, func, or_, select
from sqlmodel.sql.expression import SelectOfScalar, col

from worker_safety_service.clustering.utils import Coordinates
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.audit_events import AuditContext, create_audit_event
from worker_safety_service.dal.configurations import (
    WORK_PACKAGE_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager, LocationUpdate
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.models import (
    AsyncSession,
    AuditEventType,
    LibraryProjectType,
    LibraryRegion,
    Location,
    LocationCreate,
    LocationEdit,
    ProjectStatus,
    RiskLevel,
    Task,
    User,
    WorkPackage,
    WorkPackageCreate,
    WorkPackageEdit,
    WorkType,
    set_item_order_by,
    unique_order_by_fields,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.types import (
    OrderBy,
    OrderByDirection,
    ProjectLocationOrderByField,
    ProjectOrderByField,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.urbint_logging.fastapi_utils import Stats

TP = TypeVar("TP")
TL = TypeVar("TL")
logger = get_logger(__name__)


class WorkPackageManager:
    def __init__(
        self,
        session: AsyncSession,
        risk_model_metrics_manager: RiskModelMetricsManager,
        contractor_manager: ContractorsManager,
        library_manager: LibraryManager,
        locations_manager: LocationsManager,
        task_manager: TaskManager,
        site_condition_manager: SiteConditionManager,
        user_manager: UserManager,
        daily_report_manager: DailyReportManager,
        activity_manager: ActivityManager,
        configurations_manager: ConfigurationsManager,
        location_clustering: LocationClustering,
        work_type_manager: WorkTypeManager,
    ):
        self.session = session
        self.risk_manager = risk_model_metrics_manager
        self.contractor_manager = contractor_manager
        self.library_manager = library_manager
        self.locations_manager = locations_manager
        self.task_manager = task_manager
        self.site_condition_manager = site_condition_manager
        self.user_manager = user_manager
        self.daily_report_manager = daily_report_manager
        self.activity_manager = activity_manager
        self.configurations_manager = configurations_manager
        self.location_clustering = location_clustering
        self.work_type_manager = work_type_manager

    ################################################################################
    # Fetching projects
    ################################################################################

    async def apply_projects_filters(
        self,
        statement: SelectOfScalar[TP],
        search: Optional[str] = None,
        tenant_id: Optional[uuid.UUID] = None,
        risk_level_date: Optional[date] = None,
        ids: list[uuid.UUID] | None = None,
        location_ids: list[uuid.UUID] | None = None,
        external_keys: list[str] | None = None,
        status: ProjectStatus | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        load_contractor: bool = False,
        with_archived: bool = False,
        after: uuid.UUID | None = None,
        use_seek_pagination: bool | None = False,
    ) -> tuple[SelectOfScalar[TP] | None, Label | None]:
        if ids is not None and not ids:
            return None, None
        elif location_ids is not None and not location_ids:
            return None, None

        if load_contractor:
            statement = statement.options(selectinload(WorkPackage.contractor))

        if not with_archived:
            statement = statement.filter(col(WorkPackage.archived_at).is_(None))
        if tenant_id:
            statement = statement.where(WorkPackage.tenant_id == tenant_id)
        if ids:
            statement = statement.where(col(WorkPackage.id).in_(ids))
        if location_ids:
            statement = statement.where(WorkPackage.id == Location.project_id).where(
                col(Location.id).in_(location_ids)
            )
        if external_keys:
            statement = statement.where(
                col(WorkPackage.external_key).in_(external_keys)
            )
        if status:
            statement = statement.where(WorkPackage.status == status)

        unique_order_by = list(unique_order_by_fields(order_by))
        order_by_risk: bool = any(
            [
                order_by_item.field == ProjectLocationOrderByField.RISK_LEVEL.value
                for order_by_item in unique_order_by
            ]
        )

        risk_column_label: Label | None = None
        if search or order_by_risk or risk_level_date:
            assert tenant_id
            risk_level_date = risk_level_date or datetime.utcnow().date()
            (
                statement,
                metric_query,
                risk_column_label,
                risk_column_value,
            ) = await self.risk_manager.build_risk_rankings_statement(  # type: ignore
                risk_level_date,
                TotalProjectRiskScoreMetricConfig,
                tenant_id,
                statement=statement,
            )

        if search:
            assert risk_column_label is not None
            # ignore spaces
            search = f'%{search.replace(" ", "%").lower()}%'

            # NOTE:
            # Lateral Join (wt_subq): For each WorkPackage, the lateral subquery aggregates all matching
            # WorkType names into one string column (aggregated_work_type_names).
            # Using outerjoin(wt_subq, true()): This ensures the lateral subquery is executed for each row of
            # WorkPackage, joining the aggregated work types without multiplying rows.

            wt_subq = lateral(
                sa_select(
                    func.string_agg(WorkType.name, ", ").label(
                        "aggregated_work_type_names"
                    )
                ).where(WorkType.id == func.any(WorkPackage.work_type_ids))
            ).alias("wt")

            statement = (
                statement.outerjoin(LibraryRegion)
                .outerjoin(LibraryProjectType)
                .outerjoin(wt_subq, true())
                .outerjoin(User, WorkPackage.primary_assigned_user_id == User.id)
                .filter(
                    or_(
                        func.lower(col(WorkPackage.name)).like(search),
                        func.lower(col(LibraryRegion.name)).like(search),
                        func.lower(col(LibraryProjectType.name)).like(search),
                        # TODO: The below commented line will allow us to filter with work type name once
                        # the UI integration for work type name filter is worked upon.
                        # func.lower(literal_column("wt.aggregated_work_type_names")).like(search),
                        func.lower(User.get_name_sql()).like(search),
                        func.lower(risk_column_label).like(search),
                    )
                )
            )

        risk_value_order_by = None
        for order_by_item in unique_order_by:
            if order_by_item.field == ProjectOrderByField.RISK_LEVEL.value:
                risk_value_order_by = metric_query.c.value
                if order_by_item.direction == OrderByDirection.DESC:
                    risk_column_value = risk_column_value.desc()  # type: ignore
                    risk_value_order_by = risk_value_order_by.desc()
                statement = statement.order_by(risk_column_value)
            else:
                statement = set_item_order_by(statement, WorkPackage, order_by_item)
        if risk_value_order_by is not None:
            statement = statement.order_by(risk_value_order_by)

        if use_seek_pagination:
            if limit:
                statement = statement.limit(max(1, limit))
            if after:
                statement = statement.where(WorkPackage.id > after)
            statement = statement.order_by(WorkPackage.id)
        else:
            if limit:
                statement = statement.limit(max(1, limit)).offset(max(0, offset or 0))

        return statement, risk_column_label

    async def get_projects(
        self,
        search: Optional[str] = None,
        tenant_id: Optional[uuid.UUID] = None,
        risk_level_date: Optional[date] = None,
        ids: list[uuid.UUID] | None = None,
        external_keys: list[str] | None = None,
        status: ProjectStatus | None = None,
        order_by: list[OrderBy] | None = None,
        with_archived: bool = False,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[WorkPackage]:
        """
        Retrieve all projects
        """
        statement, _ = await self.apply_projects_filters(
            select(WorkPackage),
            search=search,
            tenant_id=tenant_id,
            risk_level_date=risk_level_date,
            ids=ids,
            external_keys=external_keys,
            status=status,
            order_by=order_by,
            with_archived=with_archived,
            limit=limit,
            after=after,
            use_seek_pagination=use_seek_pagination,
        )
        if statement is None:
            return []
        else:
            return (await self.session.exec(statement)).all()

    async def get_projects_by_id(
        self,
        ids: list[uuid.UUID],
        tenant_id: uuid.UUID | None = None,
        with_archived: bool = False,
    ) -> dict[uuid.UUID, WorkPackage]:
        return {
            i.id: i
            for i in await self.get_projects(
                ids=ids, tenant_id=tenant_id, with_archived=with_archived
            )
        }

    async def get_projects_with_risk(
        self,
        search: Optional[str] = None,
        tenant_id: Optional[uuid.UUID] = None,
        risk_level_date: Optional[date] = None,
        ids: list[uuid.UUID] | None = None,
        status: ProjectStatus | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        with_archived: bool = False,
    ) -> tuple[bool, list[tuple[WorkPackage, str] | list[WorkPackage]]]:
        """
        Retrieve all projects with risk
        """
        statement, risk_column = await self.apply_projects_filters(
            select(WorkPackage),
            search=search,
            tenant_id=tenant_id,
            risk_level_date=risk_level_date,
            ids=ids,
            status=status,
            order_by=order_by,
            limit=limit,
            offset=offset,
            with_archived=with_archived,
        )
        if statement is None:
            return False, []
        elif risk_column is not None:
            statement = statement.add_columns(risk_column.label("risk_value"))
            return (
                True,
                (await self.session.execute(statement)).all(),  # type: ignore
            )
        else:
            return (
                False,
                (await self.session.exec(statement)).all(),  # type: ignore
            )

    async def get_project(
        self,
        id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None,
        load_locations: bool = False,
    ) -> Optional[WorkPackage]:
        """
        Retrieve a project
        """
        statement, _ = await self.apply_projects_filters(
            select(WorkPackage),
            tenant_id=tenant_id,
            ids=[id],
        )
        if statement is None:
            return None
        else:
            if load_locations:
                statement = statement.options(selectinload(WorkPackage.locations))
            return (await self.session.exec(statement)).first()

    async def get_work_package_by_location(
        self,
        location_id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> Optional[WorkPackage]:
        """
        Retrieve a work package by location
        """
        statement, _ = await self.apply_projects_filters(
            select(WorkPackage),
            tenant_id=tenant_id,
            location_ids=[location_id],
            load_contractor=True,
        )
        if statement is None:
            return None
        else:
            return (await self.session.exec(statement)).first()

    ################################################################################
    # Archiving projects
    ################################################################################

    async def archive_project(self, project_id: uuid.UUID, user: User | None) -> None:
        with AuditContext(self.session):
            statement = select(WorkPackage).where(WorkPackage.id == project_id)
            project = (await self.session.exec(statement)).one()
            locations = await self.locations_manager.get_locations(
                project_ids=[project_id], with_lock=True
            )
            if locations:
                await self.locations_manager.archive_locations(locations)
            project.archived_at = datetime.now(timezone.utc)
            create_audit_event(self.session, AuditEventType.project_archived, user)

            await self.location_clustering.delete(project.tenant_id, locations)
            await self.session.commit()

        logger.info(
            "Project archived",
            project_id=str(project.id),
            by_user_id=f"{(user.id) if user else 'system'}",
        )

    async def archive_all_tenant_projects(
        self, tenant_id: uuid.UUID, user: User | None
    ) -> int:
        all_tenant_active_projects = await self.get_projects(tenant_id=tenant_id)
        for project in all_tenant_active_projects:
            await self.archive_project(project_id=project.id, user=user)

        return len(all_tenant_active_projects)

    ################################################################################
    # Creating and Updating projects
    ################################################################################

    async def validate_relations(
        self,
        project: WorkPackageCreate | WorkPackageEdit,
        locations: Optional[list[LocationCreate]] | list[LocationEdit] | None = None,
        db_project: WorkPackage | None = None,
        db_locations: dict[uuid.UUID, Location] | None = None,
    ) -> None:
        tenant_id = (
            db_project.tenant_id if db_project else project.tenant_id  # type: ignore
        )

        if db_project:
            assert db_locations is not None
        else:
            db_locations = {}

        # Find users we need to check
        user_ids: set[uuid.UUID] = set()
        check_manager = project.manager_id is not None and (
            not db_project or project.manager_id != db_project.manager_id
        )
        if check_manager:
            assert project.manager_id
            user_ids.add(project.manager_id)

        supervisors_ids_to_check = set()
        if (
            not db_project
            or project.primary_assigned_user_id != db_project.primary_assigned_user_id
        ):
            if project.primary_assigned_user_id:
                supervisors_ids_to_check.add(project.primary_assigned_user_id)
        if not db_project:
            supervisors_ids_to_check.update(project.additional_assigned_users_ids)
        else:
            # Check only what's new
            supervisors_ids_to_check.update(
                set(project.additional_assigned_users_ids).difference(
                    db_project.additional_assigned_users_ids
                )
            )
        if locations:
            for location in locations:
                db_location = None
                if db_locations:
                    db_location = db_locations.get(location.id)  # type: ignore
                if (
                    not db_location
                    or location.supervisor_id != db_location.supervisor_id
                ):
                    if location.supervisor_id:
                        supervisors_ids_to_check.add(location.supervisor_id)
                if not db_location:
                    supervisors_ids_to_check.update(location.additional_supervisor_ids)
                else:
                    # Check only what's new
                    supervisors_ids_to_check.update(
                        set(location.additional_supervisor_ids).difference(
                            db_location.additional_supervisor_ids
                        )
                    )
        user_ids.update(supervisors_ids_to_check)

        if user_ids:
            users = await self.user_manager.get_users_by_id(
                user_ids, tenant_id=tenant_id
            )
        else:
            users = {}

        # Check if users are valid
        if check_manager:
            assert project.manager_id
            manager = users.get(project.manager_id)
            if not manager:
                raise ValueError(f"Manager {project.manager_id} not found")
            elif manager.role != "manager":
                raise ValueError(f"Not a manager {project.manager_id}")

        if supervisors_ids_to_check:
            for supervisor_id in supervisors_ids_to_check:
                supervisor = users.get(supervisor_id)
                if not supervisor:
                    raise ValueError(f"Supervisor {supervisor_id} not found")
                elif supervisor.role != "supervisor":
                    raise ValueError(f"Not a supervisor {supervisor_id}")

        if project.contractor_id is not None and (
            not db_project or project.contractor_id != db_project.contractor_id
        ):
            if not await self.contractor_manager.get_contractor(
                project.contractor_id, tenant_id=tenant_id
            ):
                raise ValueError(f"Contractor {project.contractor_id} not found")

    async def validate_and_update_work_type_ids(
        self, work_package: WorkPackageCreate, tenant_id: uuid.UUID
    ) -> WorkPackageCreate:
        # Retrieve work types for the tenant
        wts = await self.work_type_manager.get_work_types_for_tenant(
            tenant_id=tenant_id
        )
        wt_ids = [wt.id for wt in wts]

        # Get work_type_ids from the request work_package, if it exists
        requested_work_type_ids = work_package.work_type_ids

        # Determine the valid work type IDs
        if not requested_work_type_ids:
            # If no work_type_ids are provided in the request, use all tenant work type IDs
            work_package.work_type_ids = wt_ids
        else:
            # Find the intersection of valid work type IDs and requested work type IDs
            valid_ids = list(set(wt_ids).intersection(requested_work_type_ids))
            work_package.work_type_ids = valid_ids if valid_ids else wt_ids

        return work_package

    async def create_work_packages_for_tenant(
        self,
        work_packages: list[WorkPackageCreate],
        tenant_id: uuid.UUID,
        with_audit: bool = True,
        audit_user: User | None = None,
    ) -> list[WorkPackage]:
        logger.info(f"Validating work type ids for {len(work_packages)} work packages")
        for work_package in work_packages:
            work_package = await self.validate_and_update_work_type_ids(
                work_package=work_package, tenant_id=tenant_id
            )

        logger.info(f"Validating {len(work_packages)} work packages")
        await self.configurations_manager.validate_models(
            WORK_PACKAGE_CONFIG,
            [work_package for work_package in work_packages],
            tenant_id,
        )

        logger.info(f"Validating {len(work_packages)} work package relations")
        # TODO: create bulk validate relations call
        for work_package in work_packages:
            await self.validate_relations(
                project=work_package, locations=work_package.location_creates
            )
        wps: list[WorkPackage] = []
        for work_package in work_packages:
            wp = WorkPackage.from_orm(work_package)
            if work_package.location_creates:
                new_locs = [
                    Location.from_orm(
                        loc, update={"project_id": wp.id, "clustering": []}
                    )
                    for loc in work_package.location_creates
                ]
                wp.locations.extend(new_locs)
            wps.append(wp)
        self.session.add_all(wps)

        if with_audit:
            create_audit_event(
                self.session,
                AuditEventType.project_created,
                audit_user,
            )

        await self.location_clustering.update(tenant_id, *(i.locations for i in wps))
        return wps

    async def create_work_packages(
        self,
        projects: list[WorkPackageCreate],
        user: Optional[User] = None,
    ) -> Sequence[WorkPackage]:
        work_packages = await self.create_work_packages_for_tenant(
            projects, projects[0].tenant_id, audit_user=user
        )

        await self.session.commit()

        for wp in work_packages:
            logger.info(
                "Project created",
                project_id=str(wp.id),
                by_user_id=str(user.id) if user else None,
            )
        return work_packages

    async def edit_project_with_locations(
        self,
        db_project: WorkPackage,
        project: WorkPackageEdit,
        locations: list[LocationEdit] | None = None,
        user: User | None = None,
    ) -> None:
        db_locations = {
            i.id: i
            for i in await self.locations_manager.get_locations(
                project_ids=[db_project.id], with_lock=True
            )
        }

        await self.validate_relations(
            project, locations, db_project=db_project, db_locations=db_locations
        )

        with AuditContext(self.session) as audit:
            # Check if we have work package updates
            work_package_updated = False
            for key, value in project.dict().items():
                if key != "id" and getattr(db_project, key) != value:
                    setattr(db_project, key, value)
                    work_package_updated = True
            updates = LocationUpdate(added=[], updated=[], geom_updated=[], deleted=[])
            if locations:
                updates = await self.locations_manager.edit_locations(
                    db_project, db_locations, locations
                )
            locations_added = len(updates.added) > 0
            locations_updated = len(updates.updated) > 0
            locations_deleted = len(updates.deleted) > 0
            locations_geom_updated = len(updates.geom_updated) > 0
            if (
                work_package_updated
                or locations_added
                or locations_updated
                or locations_deleted
                or locations_geom_updated
            ):
                await audit.create(AuditEventType.project_updated, user)

                if locations_added or locations_geom_updated or locations_deleted:
                    await self.location_clustering.batch(
                        db_project.tenant_id,
                        added=updates.added,
                        updated=updates.geom_updated,
                        deleted=updates.deleted,
                    )

                await self.session.commit()
                logger.info(
                    "Project updated",
                    project_id=str(db_project.id),
                    by_user_id=str(user.id) if user else None,
                    added_location_ids=[str(i.id) for i in updates.added],
                    updated_location_ids=[str(i.id) for i in updates.updated],
                    deleted_location_ids=[str(i.id) for i in updates.deleted],
                )

    ################################################################################
    # Fetching Locations
    ################################################################################
    async def get_locations_with_risk(
        self,
        ids: list[uuid.UUID] | None = None,
        date: date | None = None,
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
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        load_project: bool = False,
        with_archived: bool = False,
        x_max_map_extent: Optional[float] = None,
        y_max_map_extent: Optional[float] = None,
        x_min_map_extent: Optional[float] = None,
        y_min_map_extent: Optional[float] = None,
    ) -> tuple[bool, int, list[tuple[Location, str] | list[Location]]]:
        return await self.locations_manager.get_locations_with_risk(
            ids,
            date,
            project_ids,
            project_status,
            library_region_ids,
            library_division_ids,
            library_project_type_ids,
            work_type_ids,
            contractor_ids,
            supervisor_ids,
            all_supervisor_ids,
            search,
            order_by,
            limit,
            offset,
            risk_level_date,
            risk_levels,
            tenant_id,
            load_project,
            with_archived,
            x_max_map_extent,
            y_max_map_extent,
            x_min_map_extent,
            y_min_map_extent,
        )

    async def get_locations_by_id(
        self,
        ids: list[uuid.UUID],
        tenant_id: Optional[uuid.UUID] = None,
        load_project: bool = False,
    ) -> dict[uuid.UUID, Location]:
        return await self.locations_manager.get_locations_by_id(
            ids, tenant_id, load_project
        )

    async def get_location(
        self,
        id: uuid.UUID,
        tenant_id: Optional[uuid.UUID] = None,
        load_project: bool = False,
    ) -> Optional[Location]:
        """
        Retrieve an individual project location by ID. Excludes archived locations.
        """
        return await self.locations_manager.get_location(id, tenant_id, load_project)

    async def get_locations_tile(
        self,
        tile_box: tuple[int, int, int],
        ids: list[uuid.UUID] | None = None,
        date: date | None = None,
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
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> bytes:
        clusters_info = await self.get_locations_clusters_for_tile(
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
            tenant_id=tenant_id,
        )
        if clusters_info is None:
            return b""
        clusters, ignored_cluster_ids = clusters_info

        locations = await self.get_locations_for_tile(
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
            tenant_id=tenant_id,
            with_cluster_ids=ignored_cluster_ids,
        )
        if not clusters and not locations:
            return b""

        with Stats("tile"):
            tile = self.location_clustering.build_tile("locations")
            tile.add_keys(
                "locationId",
                "projectId",
                "risk",
                "clusterId",
                "length",
                *(level.name for level in RiskLevel),
            )

            if locations:
                for point_hex, location_id, project_id, risk_str in locations:
                    feature = tile.add_hex_point(point_hex)
                    feature.tags.extend(
                        (
                            0,
                            tile.get_index(str(location_id)),
                            1,
                            tile.get_index(str(project_id)),
                            2,
                            tile.get_index(risk_str),
                        )
                    )

            if clusters:
                for tile_geom, cluster_id, length, risk_length in clusters:
                    feature = tile.add_point(tile_geom)
                    feature.tags.extend(
                        (
                            3,
                            tile.get_index(str(cluster_id)),
                            4,
                            tile.get_int_index(length),
                        )
                    )
                    for index, i_risk_length in enumerate(risk_length):
                        feature.tags.extend(
                            (5 + index, tile.get_int_index(i_risk_length))
                        )

            return tile.build()

    async def get_locations_for_tile(
        self,
        tile_box: tuple[int, int, int],
        ids: list[uuid.UUID] | None = None,
        date: date | None = None,
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
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        with_cluster_ids: list[uuid.UUID] | None = None,
    ) -> list[tuple[str, uuid.UUID, uuid.UUID, str]] | None:
        main_statement: SelectOfScalar[tuple[str, uuid.UUID, uuid.UUID]] = select(  # type: ignore
            self.location_clustering.tile_geom_column(tile_box, Location.geom),
            Location.id,
            Location.project_id,
            case(
                (Location.risk == "recalculating", "RECALCULATING"),
                (Location.risk == "unknown", "UNKNOWN"),
                (Location.risk == "low", "LOW"),
                (Location.risk == "medium", "MEDIUM"),
                else_="HIGH",
            ).label("risk"),
        )

        limit_with_clustering: int | None = None
        if self.location_clustering.with_clustering(tile_box):
            c_column = self.location_clustering.clustering_id_column(tile_box[0])
            or_clauses = [c_column.is_(None)]
            if with_cluster_ids:
                or_clauses.append(c_column.in_(with_cluster_ids))
            main_statement = main_statement.where(or_(*or_clauses))

            # When clustering, make sure we don't send a lot of single points
            # It shouldn't happen, but if for some reason the clustering is missing
            # we don't send all points in the tile
            limit_with_clustering = 1000
            main_statement = main_statement.limit(limit_with_clustering)

        statement, _ = await self.locations_manager.apply_locations_filters(
            main_statement,
            tile_box=tile_box,
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
            tenant_id=tenant_id,
            join_with_risk=True,
        )
        if statement is None:
            return None
        else:
            # assert risk_column is not None
            # statement = statement.add_columns(risk_column.label("risk"))
            items = (await self.session.exec(statement)).all()

            if limit_with_clustering and len(items) == limit_with_clustering:
                logger.critical(f"Too many locations on clustering for tile {tile_box}")

            return items  # type: ignore

    async def get_locations_clusters_for_tile(
        self,
        tile_box: tuple[int, int, int],
        ids: list[uuid.UUID] | None = None,
        date: date | None = None,
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
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> (
        tuple[list[tuple[Coordinates, uuid.UUID, int, list[int]]], list[uuid.UUID]]
        | None
    ):
        cluster_tile_data: list[tuple[Coordinates, uuid.UUID, int, list[int]]] = []
        ignored_cluster_ids: list[uuid.UUID] = []

        clusters = await self.location_clustering.get_clusters(
            tile_box, tenant_id=tenant_id
        )
        if not clusters:
            return cluster_tile_data, ignored_cluster_ids

        clustering_column = self.location_clustering.clustering_id_column(tile_box[0])
        main_statement: SelectOfScalar[tuple[uuid.UUID, int]] = select(  # type: ignore
            Location.id, clustering_column.label("clustering_id")
        ).where(clustering_column.in_(clusters.keys()))

        statement, risk_column = await self.locations_manager.apply_locations_filters(
            main_statement,
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
            tenant_id=tenant_id,
            join_with_risk=True,
        )
        if statement is None:
            return None

        assert risk_column is not None
        statement = statement.add_columns(risk_column.label("risk"))
        items = statement.alias()

        group_statement = (
            select(  # type: ignore
                items.c.clustering_id,
                func.count(items.c.id).label("length"),
                # Find all risk count
                *(
                    func.count(items.c.id)
                    .filter(items.c.risk == level.name)
                    .label(level.name)
                    for level in RiskLevel
                ),
            ).group_by(items.c.clustering_id)
            # In case we have a empty cluster (bug)
            .having(func.count(items.c.id) > 0)
        )

        for item in (await self.session.exec(group_statement)).all():
            cluster_id, length, *risk_length = item
            if length == 1:
                # In case we have filters applied or a bug
                # we could have a cluster with only one location
                ignored_cluster_ids.append(cluster_id)
            else:
                cluster_tile_data.append(
                    (clusters[cluster_id], cluster_id, length, risk_length)
                )
        return cluster_tile_data, ignored_cluster_ids

    ################################################################################
    # Misc Project Data
    ################################################################################

    async def get_minimum_task_start_date_for_projects(
        self, project_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, date]:
        statement = (
            select(WorkPackage.id, func.min(col(Task.start_date)))  # type: ignore
            .select_from(WorkPackage)
            .join(Location)
            .join(Task)
            .where(col(WorkPackage.id).in_(project_ids))
            .where(Task.archived_at == None)  # noqa: E711
            .group_by(WorkPackage.id)
        )
        items = dict((await self.session.exec(statement)).all())
        return items

    async def get_maximum_task_end_date_for_projects(
        self, project_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, date]:
        statement = (
            select(WorkPackage.id, func.max(Task.end_date))  # type: ignore
            .select_from(WorkPackage)
            .join(Location)
            .join(Task)
            .where(col(WorkPackage.id).in_(project_ids))
            .where(Task.archived_at == None)  # noqa: E711
            .group_by(WorkPackage.id)
        )
        items = dict((await self.session.exec(statement)).all())
        return items
