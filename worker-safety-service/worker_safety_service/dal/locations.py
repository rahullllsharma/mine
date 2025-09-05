from datetime import date, datetime, timezone
from typing import Iterable, NamedTuple, Optional, Sequence, TypeVar
from uuid import UUID

from sqlalchemy import String, case, cast, lateral
from sqlalchemy import select as sa_select
from sqlalchemy import true
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import contains_eager
from sqlalchemy.sql.elements import Label
from sqlmodel import func, or_, select, update
from sqlmodel.sql.expression import SelectOfScalar, col

from worker_safety_service.config import settings
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.audit_events import AuditContext, create_audit_event
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.risk_model import (
    RISK_LEVEL_FOR_ORDER,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.exceptions import DuplicateExternalKeyException
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    AuditEventType,
    DailyReport,
    FormStatus,
    LibraryProjectType,
    Location,
    LocationEdit,
    ProjectStatus,
    RiskLevel,
    User,
    WorkPackage,
    WorkType,
    set_item_order_by,
    unique_order_by_fields,
)
from worker_safety_service.types import (
    OrderBy,
    OrderByDirection,
    ProjectLocationOrderByField,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)

TP = TypeVar("TP")
TL = TypeVar("TL")


class LocationUpdate(NamedTuple):
    added: list[Location]
    updated: list[Location]
    geom_updated: list[Location]
    deleted: list[Location]


class LocationsManager:
    def __init__(
        self,
        session: AsyncSession,
        activity_manager: ActivityManager,
        daily_report_manager: DailyReportManager,
        risk_model_metrics_manager: RiskModelMetricsManager,
        site_condition_manager: SiteConditionManager,
        task_manager: TaskManager,
        location_clustering: LocationClustering,
    ):
        self.session = session
        self.activity_manager = activity_manager
        self.daily_report_manager = daily_report_manager
        self.risk_manager = risk_model_metrics_manager
        self.site_condition_manager = site_condition_manager
        self.task_manager = task_manager
        self.location_clustering = location_clustering

    async def create_locations(
        self, locations: Sequence[Location]
    ) -> Sequence[Location]:
        self.session.add_all(locations)
        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            if (
                db_err.orig.args
                and "ExternalKey must be unique within a Tenant" in db_err.orig.args[0]
            ):
                raise DuplicateExternalKeyException()
            else:
                raise db_err

        first_location = locations[0]
        await self.location_clustering.batch(first_location.tenant_id, added=locations)

        return locations

    async def create_location(self, location: Location) -> Location:
        return (await self.create_locations([location]))[0]

    async def apply_locations_filters(
        self,
        statement: SelectOfScalar[TL],
        ids: list[UUID] | None = None,
        date: date | None = None,
        project_ids: list[UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[UUID] | None = None,
        library_division_ids: list[UUID] | None = None,
        library_project_type_ids: list[UUID] | None = None,
        work_type_ids: list[UUID] | None = None,
        contractor_ids: list[UUID] | None = None,
        supervisor_ids: list[UUID] | None = None,
        all_supervisor_ids: list[UUID] | None = None,
        search: str | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tile_box: tuple[int, int, int] | None = None,
        tenant_id: Optional[UUID] = None,
        load_project: bool = False,
        with_archived: bool = False,
        join_with_risk: bool = False,
        with_lock: bool = False,
        after: UUID | None = None,
        x_max_map_extent: float | None = None,
        x_min_map_extent: float | None = None,
        y_max_map_extent: float | None = None,
        y_min_map_extent: float | None = None,
        use_seek_pagination: bool | None = False,
        activity_ids: list[UUID] | None = None,
        external_keys: list[str] | None = None,
    ) -> tuple[SelectOfScalar[TL] | None, Label | None]:
        if limit == 0:
            return None, None
        if ids is not None and not ids:
            return None, None
        elif project_ids is not None and not project_ids:
            return None, None
        elif project_status is not None and not project_status:
            return None, None
        elif library_region_ids is not None and not library_region_ids:
            return None, None
        elif library_division_ids is not None and not library_division_ids:
            return None, None
        elif library_project_type_ids is not None and not library_project_type_ids:
            return None, None
        elif work_type_ids is not None and not work_type_ids:
            return None, None
        elif contractor_ids is not None and not contractor_ids:
            return None, None
        elif supervisor_ids is not None and not supervisor_ids:
            return None, None
        elif all_supervisor_ids is not None and not all_supervisor_ids:
            return None, None
        elif risk_levels is not None and not risk_levels:
            return None, None
        elif activity_ids is not None and not activity_ids:
            return None, None
        elif external_keys is not None and external_keys:
            return None, None

        relate_with_project = bool(
            load_project
            or library_region_ids
            or library_division_ids
            or library_project_type_ids
            or work_type_ids
            or contractor_ids
            or all_supervisor_ids
            or tenant_id
            or date
            or search
            or project_status
        )

        if not with_archived:
            statement = statement.where(col(Location.archived_at).is_(None))
        if relate_with_project:
            statement = statement.join_from(
                Location, WorkPackage, onclause=Location.project_id == WorkPackage.id
            )
        if load_project:
            statement = statement.options(contains_eager(Location.project))
        if tenant_id:
            statement = statement.where(WorkPackage.tenant_id == tenant_id)
        if ids:
            statement = statement.where(col(Location.id).in_(ids))
        if project_ids:
            statement = statement.where(col(Location.project_id).in_(project_ids))
        if project_status:
            statement = statement.where(col(WorkPackage.status).in_(project_status))
        if contractor_ids:
            statement = statement.where(
                col(WorkPackage.contractor_id).in_(contractor_ids)
            )
        if library_region_ids:
            statement = statement.where(
                col(WorkPackage.region_id).in_(library_region_ids)
            )
        if library_division_ids:
            statement = statement.where(
                col(WorkPackage.division_id).in_(library_division_ids)
            )
        if library_project_type_ids:
            statement = statement.where(
                col(WorkPackage.work_type_id).in_(library_project_type_ids)
            )
        if work_type_ids:
            statement = statement.where(
                # func.array_overlap(WorkPackage.work_type_ids, work_type_ids)
                col(WorkPackage.work_type_ids).overlap(work_type_ids)
            )
        if supervisor_ids:
            statement = statement.where(col(Location.supervisor_id).in_(supervisor_ids))
        if all_supervisor_ids:
            statement = statement.where(
                or_(
                    col(WorkPackage.primary_assigned_user_id).in_(all_supervisor_ids),
                    col(Location.supervisor_id).in_(all_supervisor_ids),
                    col(WorkPackage.additional_assigned_users_ids).overlap(
                        all_supervisor_ids
                    ),
                    col(Location.additional_supervisor_ids).overlap(all_supervisor_ids),
                )
            )
        if tile_box:
            statement = statement.where(
                func.ST_Intersects(
                    func.TileBBox(*tile_box, settings.DEFAULT_SRID), Location.geom
                )
            )

        unique_order_by = list(unique_order_by_fields(order_by))
        # order_by_risk: bool = any(
        #     [
        #         order_by_item.field == ProjectLocationOrderByField.RISK_LEVEL.value
        #         for order_by_item in unique_order_by
        #     ]
        # )

        risk_column_label: Label | None = None
        if risk_levels or join_with_risk:
            assert tenant_id
            risk_level_date = risk_level_date or datetime.utcnow().date()
            # statement, metric_query, risk_column_label, risk_column_value = await self.risk_manager.build_risk_rankings_statement(  # type: ignore
            #     risk_level_date,
            #     TotalLocationRiskScoreMetricConfig,
            #     tenant_id,
            #     statement=statement,
            #     ignore_work_package_join=relate_with_project,
            # )
            if risk_levels:
                statement = statement.where(
                    col(Location.risk).in_([i.name.lower() for i in risk_levels])
                )
            # risk_column_label = await self.risk_manager.get_risk_column_label(statement=statement)
            # logger.info(
            #     "Logger for result metric query========================>",
            #     statement=statement,
            #     metric_query=metric_query,
            #     risk_column_label=risk_column_label,
            #     risk_column_value=risk_column_value,
            # )

        if (
            x_max_map_extent is not None
            and y_max_map_extent is not None
            and x_min_map_extent is not None
            and y_min_map_extent is not None
        ):
            polygon = func.ST_MakeEnvelope(
                x_min_map_extent,
                y_min_map_extent,
                x_max_map_extent,
                y_max_map_extent,
                settings.DEFAULT_SRID,
            )
            statement = statement.where(func.ST_Within(Location.geom, polygon))

        if search:
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
                statement.outerjoin(LibraryProjectType)
                .outerjoin(wt_subq, true())
                .outerjoin(User, WorkPackage.primary_assigned_user_id == User.id)
                .filter(
                    or_(
                        func.lower(col(Location.name)).like(search),
                        func.lower(col(WorkPackage.name)).like(search),
                        func.lower(col(LibraryProjectType.name)).like(search),
                        # FIXME: The below commented line will allow us to filter with work type name once
                        # the UI integration of 1220 for work type name filter is worked upon.
                        # func.lower(literal_column("wt.aggregated_work_type_names")).like(search),
                        func.lower(User.get_name_sql()).like(search),
                        func.lower(cast(col(Location.risk), String)).like(search),
                    )
                )
            )
        # if risk_levels:
        #     # assert risk_column_label is not None
        #     statement = statement.where(
        #         risk_column_label.in_({i.name for i in risk_levels})
        #     )

        risk_value_order_by = None
        for order_by_item in unique_order_by:
            if order_by_item.field == ProjectLocationOrderByField.RISK_LEVEL.value:
                risk_value_order_by = "asc"
                if order_by_item.direction == OrderByDirection.DESC:
                    risk_value_order_by = "desc"
                # statement = statement.order_by(risk_column_value)
            else:
                statement = set_item_order_by(statement, Location, order_by_item)
        if risk_value_order_by is not None:
            if risk_value_order_by == "asc":
                statement = statement.order_by(
                    case(
                        *(
                            (Location.risk == RiskLevel[risk_level], priority_value)
                            for risk_level, priority_value in RISK_LEVEL_FOR_ORDER.items()
                        )
                    ).asc()
                )
            else:
                statement = statement.order_by(
                    case(
                        *(
                            (Location.risk == RiskLevel[risk_level], priority_value)
                            for risk_level, priority_value in RISK_LEVEL_FOR_ORDER.items()
                        )
                    ).desc()
                )
        if date:
            assert_date(date)
            statement = statement.where(WorkPackage.start_date <= date).where(
                WorkPackage.end_date >= date
            )

        if activity_ids:
            statement = statement.where(Location.id == Activity.location_id).where(
                col(Activity.id).in_(activity_ids)
            )

        if external_keys:
            statement = statement.where(col(Location.external_key).in_(external_keys))

        if with_lock:
            statement = statement.with_for_update()
        if use_seek_pagination:
            if limit:
                statement = statement.limit(max(1, limit))
            if after:
                statement = statement.where(Location.id > after)
            statement = statement.order_by(Location.id)
        else:
            if limit:
                statement = statement.limit(max(1, limit)).offset(max(0, offset or 0))
        return statement, risk_column_label

    async def get_locations(
        self,
        ids: list[UUID] | None = None,
        date: date | None = None,
        project_ids: list[UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[UUID] | None = None,
        library_division_ids: list[UUID] | None = None,
        library_project_type_ids: list[UUID] | None = None,
        work_type_ids: list[UUID] | None = None,
        contractor_ids: list[UUID] | None = None,
        supervisor_ids: list[UUID] | None = None,
        all_supervisor_ids: list[UUID] | None = None,
        search: str | None = None,
        order_by: list[OrderBy] | None = None,
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[UUID] = None,
        load_project: bool = False,
        with_archived: bool = False,
        with_lock: bool = False,
        limit: int | None = None,
        after: UUID | None = None,
        use_seek_pagination: bool | None = False,
        activity_ids: list[UUID] | None = None,
        external_keys: list[str] | None = None,
    ) -> list[Location]:
        """
        Retrieve project locations.
        """
        statement, _ = await self.apply_locations_filters(
            select(Location),
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
            tenant_id=tenant_id,
            load_project=load_project,
            with_archived=with_archived,
            with_lock=with_lock,
            limit=limit,
            after=after,
            use_seek_pagination=use_seek_pagination,
            activity_ids=activity_ids,
            external_keys=external_keys,
        )
        if statement is None:
            return []
        else:
            return (await self.session.exec(statement)).all()

    async def get_locations_with_risk(
        self,
        ids: list[UUID] | None = None,
        date: date | None = None,
        project_ids: list[UUID] | None = None,
        project_status: list[ProjectStatus] | None = None,
        library_region_ids: list[UUID] | None = None,
        library_division_ids: list[UUID] | None = None,
        library_project_type_ids: list[UUID] | None = None,
        work_type_ids: list[UUID] | None = None,
        contractor_ids: list[UUID] | None = None,
        supervisor_ids: list[UUID] | None = None,
        all_supervisor_ids: list[UUID] | None = None,
        search: str | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        risk_level_date: Optional[date] = None,
        risk_levels: list[RiskLevel] | None = None,
        tenant_id: Optional[UUID] = None,
        load_project: bool = False,
        with_archived: bool = False,
        x_max_map_extent: float | None = None,
        y_max_map_extent: float | None = None,
        x_min_map_extent: float | None = None,
        y_min_map_extent: float | None = None,
    ) -> tuple[bool, int, list[tuple[Location, str] | list[Location]]]:
        statement, risk_column = await self.apply_locations_filters(
            select(Location),
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
            tenant_id=tenant_id,
            x_max_map_extent=x_max_map_extent,
            y_max_map_extent=y_max_map_extent,
            x_min_map_extent=x_min_map_extent,
            y_min_map_extent=y_min_map_extent,
            load_project=load_project,
            with_archived=with_archived,
        )
        if statement is None:
            return False, 0, []
        elif risk_column is not None:
            statement = statement.add_columns(risk_column.label("risk_level"))
            results = (await self.session.execute(statement)).all()
            count = len(list(results))
            return (True, count, results)  # type: ignore
        else:
            results = (await self.session.exec(statement)).all()  # type: ignore
            count = len(list(results))
            return (False, count, results)  # type: ignore

    async def get_locations_by_id(
        self,
        ids: list[UUID],
        tenant_id: Optional[UUID] = None,
        load_project: bool = False,
    ) -> dict[UUID, Location]:
        return {
            i.id: i
            for i in await self.get_locations(
                ids=ids, tenant_id=tenant_id, load_project=load_project
            )
        }

    async def get_location(
        self,
        id: UUID,
        tenant_id: Optional[UUID] = None,
        load_project: bool = False,
    ) -> Optional[Location]:
        """
        Retrieve an individual project location by ID. Excludes archived locations.
        """
        statement, _ = await self.apply_locations_filters(
            select(Location),
            ids=[id],
            tenant_id=tenant_id,
            load_project=load_project,
        )
        if statement is None:
            return None
        else:
            return (await self.session.exec(statement)).first()

    async def validate_location_archive(self, location_ids: Iterable[UUID]) -> bool:
        """
        Raises an error if any of the passed location_ids have active daily reports.
        """
        # TODO: SERV-230 move this query
        statement = (
            select(col(DailyReport.project_location_id), func.count(DailyReport.id))  # type: ignore
            .where(col(DailyReport.project_location_id).in_(location_ids))
            .where(col(DailyReport.archived_at).is_(None))
            .where(
                col(DailyReport.status).in_(
                    [FormStatus.IN_PROGRESS, FormStatus.COMPLETE]
                )
            )
            .group_by(DailyReport.project_location_id)
        )
        items = dict((await self.session.exec(statement)).all())
        if items:
            raise ValueError(
                "\n".join(
                    f"Project location {location_id} has {length} active daily reports."
                    for location_id, length in items.items()
                )
            )
        return True

    async def archive_locations(self, locations: Iterable[Location]) -> None:
        archived_at = datetime.now(timezone.utc)
        for db_location in locations:
            db_location.archived_at = archived_at

        # archive the location's nested objects as well
        ids = [i.id for i in locations]
        await self.daily_report_manager.archive_daily_reports(location_ids=ids)
        await self.task_manager.archive_tasks(location_ids=ids)
        await self.activity_manager.archive_activities(location_ids=ids)
        await self.site_condition_manager.archive_site_conditions(location_ids=ids)

    async def archive_locations_rest(self, locations: Iterable[Location]) -> None:
        with AuditContext(self.session):
            await self.archive_locations(locations)
            create_audit_event(
                self.session, AuditEventType.project_location_archived, user=None
            )
            await self.session.commit()

    async def edit_location(
        self, location: Location, geom_changed: bool = False
    ) -> Location:
        with AuditContext(self.session) as audit:
            if geom_changed is True:
                await self.site_condition_manager.archive_site_conditions(
                    location_ids=[location.id],
                    include_manual_site_conditions=False,
                )
                await audit.create(AuditEventType.site_condition_archived, user=None)
            self.session.add(location)
            try:
                await self.session.commit()
            except DBAPIError as db_err:
                await self.session.rollback()
                if (
                    db_err.orig.args
                    and "ExternalKey must be unique within a Tenant"
                    in db_err.orig.args[0]
                ):
                    raise DuplicateExternalKeyException()
                else:
                    raise db_err
        await self.location_clustering.batch(
            location.tenant_id,
            updated=[location],
        )

        return location

    # TODO: pass project_id, not project
    async def edit_locations(
        self,
        db_project: WorkPackage,
        db_locations: dict[UUID, Location],
        locations: list[LocationEdit],
    ) -> LocationUpdate:
        if not locations:
            raise ValueError("At least one location is required in the project")

        added: list[Location] = []
        updated: list[Location] = []
        geom_updated: list[Location] = []
        deleted: list[Location] = []

        for location in locations:
            if not location.id:
                location_data = location.dict()
                location_data.pop("id")
                new_location = Location(project_id=db_project.id, **location_data)
                self.session.add(new_location)
                added.append(new_location)
            else:
                db_location = db_locations.pop(location.id, None)
                if not db_location:
                    raise ValueError(
                        f"Project location {location.id} not found in project {db_project.id}"
                    )
                else:
                    location_updated = False
                    for key, value in location.dict().items():
                        if (
                            key not in ("id", "project_id")
                            and getattr(db_location, key) != value
                        ):
                            setattr(db_location, key, value)
                            self.session.add(db_location)
                            location_updated = True
                            if key == "geom":
                                geom_updated.append(db_location)
                                await self.site_condition_manager.archive_site_conditions(
                                    location_ids=[location.id],
                                    include_manual_site_conditions=False,
                                )
                    if location_updated:
                        updated.append(db_location)

        # Because the client needs to send all locations, remove what's not defined
        if db_locations:
            await self.validate_location_archive(list(db_locations.keys()))
            await self.archive_locations(db_locations.values())
            deleted.extend(db_locations.values())

        return LocationUpdate(
            added=added,
            updated=updated,
            geom_updated=geom_updated,
            deleted=deleted,
        )

    async def update_location_risk(self, id_to_risk_map: dict[UUID, RiskLevel]) -> None:
        if not id_to_risk_map:  # First check if the map is empty
            return

        for location_id, risk in id_to_risk_map.items():
            statement = (
                update(Location).where(Location.id == location_id).values(risk=risk)
            )
            await self.session.execute(statement)
        await self.session.commit()
