import datetime
from typing import Optional, Type, Union
from uuid import UUID

from sqlalchemy import and_, cast, literal, null
from sqlalchemy import select as sa_select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import Select
from sqlmodel import col, func, or_, select, text, union_all

from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEvent,
    AuditEventDiff,
    DailyReport,
    EnergyBasedObservation,
    FormBase,
    FormDefinition,
    FormStatus,
    JobSafetyBriefing,
    Location,
    NatGridJobSafetyBriefing,
    OrderBy,
    User,
    WorkPackage,
    set_order_by_raw,
)
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

Form = Union[
    DailyReport, JobSafetyBriefing, EnergyBasedObservation, NatGridJobSafetyBriefing
]


class FormsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_form_definition(
        self, form_definition: FormDefinition
    ) -> FormDefinition:
        self.session.add(form_definition)
        await self.session.commit()
        return form_definition

    async def get_form_definition(
        self, id: UUID, tenant_id: UUID
    ) -> Optional[FormDefinition]:
        statement = (
            select(FormDefinition)
            .where(FormDefinition.id == id)
            .where(FormDefinition.tenant_id == tenant_id)
        )

        return (await self.session.exec(statement)).first()

    async def get_form_definitions(self, tenant_id: UUID) -> list[FormDefinition]:
        statement = select(FormDefinition).where(FormDefinition.tenant_id == tenant_id)

        return (await self.session.exec(statement)).all()

    def build_form_statement(
        self,
        table: Type[FormBase],
        name: str,
        form_id: Optional[list[str]],
        form_status: Optional[list[FormStatus]] = None,
        project_ids: Optional[list[UUID]] = None,
        location_ids: Optional[list[UUID]] = None,
        created_by_ids: Optional[list[UUID]] = None,
        updated_by_ids: Optional[list[UUID]] = None,
        start_created_at: Optional[datetime.date] = None,
        end_created_at: Optional[datetime.date] = None,
        start_updated_at: Optional[datetime.date] = None,
        end_updated_at: Optional[datetime.date] = None,
        search: Optional[str] = None,
        filter_search: Optional[dict] = None,
        ad_hoc: bool = False,
        with_archived: bool = False,
        tenant_id: Optional[UUID] = None,
        with_contents: bool = False,
        start_completed_at: Optional[datetime.date] = None,
        end_completed_at: Optional[datetime.date] = None,
        start_report_date: Optional[datetime.date] = None,
        end_report_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        operating_region_names: Optional[list[str]] = None,
        manager_ids: Optional[list[str]] = None,
        order_by: Optional[list[OrderBy]] = None,
    ) -> Select | None:
        statement = sa_select(
            table.id,
            table.status,
            text(f"\"name\" '{name}'"),
            table.created_at,
            table.created_by_id,
            table.completed_at,
            table.completed_by_id,
            table.date_for,
            table.archived_at,
            table.form_id,
            table.updated_at,
            table.project_location_id
            if hasattr(table, "project_location_id")
            else None,
        )

        contents_column = (
            table.contents.label("contents")
            if hasattr(table, "contents") and with_contents
            else cast(null(), JSONB).label("contents")
        )
        statement = statement.add_columns(contents_column)

        sections_column = (
            table.sections.label("sections")
            if hasattr(table, "sections") and with_contents
            else cast(null(), JSONB).label("sections")
        )
        statement = statement.add_columns(sections_column)

        window_subquery = (
            select(  # type:ignore
                AuditEventDiff.object_id,
                AuditEventDiff.event_id,
                AuditEventDiff.created_at,
                func.row_number()
                .over(
                    partition_by=col(AuditEventDiff.object_id),
                    order_by=col(AuditEventDiff.created_at).desc(),
                )
                .label("rn"),
            )
            .filter(
                AuditEventDiff.object_id == table.id
                and col(AuditEventDiff.diff_type).in_(
                    [AuditDiffType.updated, AuditDiffType.created]
                )
            )
            .subquery()
            .lateral()
        )

        # For forms with work_packages, make appropriate joins
        if hasattr(table, "project_location_id"):
            statement = statement.join(
                Location,
                Location.id == table.project_location_id,
                isouter=True,
            ).join(WorkPackage, Location.project_id == WorkPackage.id, isouter=True)
        else:
            # Can't filter the fields we don't have. Exclude this table from Union. (Currently for EBOs)
            if project_ids is not None or location_ids is not None:
                return None

        statement = statement.join(
            window_subquery,
            and_(window_subquery.c.object_id == table.id, window_subquery.c.rn == 1),
            isouter=True,
        ).add_columns(
            window_subquery.c.event_id.label("event_id"),
        )

        # Create aliases for different user relationships
        created_by_user = aliased(User, name="created_by_user")
        updated_by_user = aliased(User, name="updated_by_user")

        # Only join on AuditEvents if we need to filter by updated by users.
        if filter_search or search or updated_by_ids is not None:
            statement = statement.join(
                AuditEvent, window_subquery.c.event_id == AuditEvent.id, isouter=True
            ).add_columns(AuditEvent.user_id)

        # operating_hq column
        if table == JobSafetyBriefing:
            operating_hq_column = (
                JobSafetyBriefing.contents.op("->")("work_location")  # type: ignore
                .op("->>")("operating_hq")
                .astext.label("operating_hq")
            )
            statement = statement.add_columns(operating_hq_column)
        elif table == NatGridJobSafetyBriefing:
            operating_hq_column = (
                NatGridJobSafetyBriefing.contents.op("->")("barn_location")  # type: ignore
                .op("->>")("name")
                .astext.label("operating_hq")
            )
            statement = statement.add_columns(operating_hq_column)
        elif table == DailyReport:
            operating_hq_column = (
                DailyReport.sections.op("->")("additional_information")  # type: ignore
                .op("->>")("operating_hq")
                .astext.label("operating_hq")
            )
            statement = statement.add_columns(operating_hq_column)
        elif table == EnergyBasedObservation:
            operating_hq_column = (
                EnergyBasedObservation.contents.op("->")("details")  # type: ignore
                .op("->")("opco_observed")
                .op("->>")("name")
                .astext.label("operating_hq")
            )
            statement = statement.add_columns(operating_hq_column)

        # JSBSupervisorLink
        if (manager_ids or search) and table == JobSafetyBriefing:
            statement = statement.join(
                JSBSupervisorLink,
                JSBSupervisorLink.jsb_id == JobSafetyBriefing.id,
                isouter=True,
            )

        # Filters
        if tenant_id is not None:
            statement = statement.where(col(table.tenant_id) == tenant_id)
        if project_ids is not None:
            statement = statement.where(col(Location.project_id).in_(project_ids))
        if location_ids is not None:
            statement = statement.where(col(Location.id).in_(location_ids))
        if created_by_ids is not None:
            statement = statement.where(col(table.created_by_id).in_(created_by_ids))
        if updated_by_ids is not None:
            statement = statement.where(col(AuditEvent.user_id).in_(updated_by_ids))
        if start_date is not None:
            statement = statement.where(col(table.date_for) >= start_date)
        if end_date is not None:
            statement = statement.where(col(table.date_for) <= end_date)
        if start_created_at is not None:
            statement = statement.where(col(table.created_at) >= start_created_at)
        if end_created_at is not None:
            statement = statement.where(
                col(table.created_at) < end_created_at + datetime.timedelta(days=1)
            )
        if start_updated_at is not None:
            statement = statement.where(col(table.updated_at) >= start_updated_at)
        if end_updated_at is not None:
            statement = statement.where(
                col(table.updated_at) < end_updated_at + datetime.timedelta(days=1)
            )
        if form_status is not None:
            statement = statement.where(col(table.status).in_(form_status))
        if form_id is not None:
            statement = statement.where(col(table.form_id).in_(form_id))
        if not with_archived:
            statement = statement.where(col(table.archived_at).is_(None))
        if hasattr(table, "project_location_id") and ad_hoc:
            statement = statement.where(col(table.project_location_id).is_(None))
        if start_completed_at is not None:
            statement = statement.where(col(table.completed_at) >= start_completed_at)
        if end_completed_at is not None:
            statement = statement.where(
                col(table.completed_at) < end_completed_at + datetime.timedelta(days=1)
            )
        if start_report_date is not None:
            statement = statement.where(col(table.date_for) >= start_report_date)
        if end_report_date is not None:
            statement = statement.where(
                col(table.date_for) < end_report_date + datetime.timedelta(days=1)
            )
        if operating_region_names is not None:
            if table == JobSafetyBriefing:
                statement = statement.where(
                    JobSafetyBriefing.contents.op("->")("work_location")  # type: ignore
                    .op("->>")("operating_hq")
                    .astext.in_(operating_region_names)
                )
            elif table == NatGridJobSafetyBriefing:
                statement = statement.where(
                    NatGridJobSafetyBriefing.contents.op("->")("barn_location")  # type: ignore
                    .op("->>")("name")
                    .astext.in_(operating_region_names)
                )
            elif table == DailyReport:
                statement = statement.where(
                    DailyReport.sections.op("->")("additional_information")  # type: ignore
                    .op("->>")("operating_hq")
                    .astext.in_(operating_region_names)
                )
            elif table == EnergyBasedObservation:
                statement = statement.where(
                    EnergyBasedObservation.contents.op("->")("details")  # type: ignore
                    .op("->")("opco_observed")
                    .op("->>")("name")
                    .astext.in_(operating_region_names)
                )
        if manager_ids and table == JobSafetyBriefing:
            statement = statement.where(
                col(JSBSupervisorLink.manager_id).in_(manager_ids)
            )

        if search:
            search = f'%{search.replace(" ", "%").lower()}%'

            # Add the joins with aliases
            statement = statement.join(
                created_by_user,
                created_by_user.id == table.created_by_id,
                isouter=True,
            ).join(
                updated_by_user,
                updated_by_user.id == AuditEvent.user_id,
                isouter=True,
            )

            search_conditions = [
                func.lower(table.form_id).like(search),
                func.lower(
                    func.concat(
                        created_by_user.first_name,
                        literal(" "),
                        created_by_user.last_name,
                    )
                ).like(search),
                func.lower(
                    func.concat(
                        updated_by_user.first_name,
                        literal(" "),
                        updated_by_user.last_name,
                    )
                ).like(search),
            ]

            if table == EnergyBasedObservation:
                value = (
                    table.contents.op("->")("details").op("->>")("work_location").astext  # type: ignore
                )
                search_conditions.append(func.lower(value).like(search))
            elif table == JobSafetyBriefing:
                search_conditions.append(
                    func.lower(JSBSupervisorLink.manager_name).like(search)
                )
                value = (
                    table.contents.op("->")("work_location")  # type: ignore
                    .op("->>")("description")
                    .astext
                )
                search_conditions.append(func.lower(value).like(search))
            elif (
                table == NatGridJobSafetyBriefing
            ):  # changed this since JSB and NGJSB have different fields recording location name
                value = (
                    table.contents.op("->")(  # type: ignore
                        "work_location_with_voltage_info"
                    )
                    .op("->")(0)
                    .op("->>")("address")
                    .astext
                )

                search_conditions.append(func.lower(value).like(search))

            if hasattr(table, "project_location_id"):
                search_conditions.append(func.lower(WorkPackage.name).like(search))
                search_conditions.append(func.lower(Location.name).like(search))

            statement = statement.filter(or_(*search_conditions))

        # filter_search is a dict where the
        # key is the column name and the value is the search term
        # on which we want to filter the results
        # This is used for searching on created_by_user or updated_by_user
        if filter_search:
            search_column = filter_search.get("search_column")
            search_value = filter_search.get("search_value")

            if search_value:  # Ensure search_value is not None
                search_value = f'%{search_value.replace(" ", "%").lower()}%'
                search_condition = []
                if search_column == "created_by_user":
                    statement = statement.join(
                        created_by_user,
                        created_by_user.id == table.created_by_id,
                        isouter=True,
                    )

                    search_condition = [
                        func.lower(
                            func.concat(
                                created_by_user.first_name,
                                literal(" "),
                                created_by_user.last_name,
                            )
                        ).like(search_value)
                    ]

                elif search_column == "updated_by_user":
                    # Add the joins with aliases
                    statement = statement.join(
                        updated_by_user,
                        updated_by_user.id == AuditEvent.user_id,
                        isouter=True,
                    )

                    search_condition = [
                        func.lower(
                            func.concat(
                                updated_by_user.first_name,
                                literal(" "),
                                updated_by_user.last_name,
                            )
                        ).like(search_value)
                    ]

                statement = statement.filter(or_(*search_condition))

        # Remove duplicate JSBs, in case of JSBSupervisorLink join
        # This behaviour can be expended to other cols and orders,
        # but would require some special handling for id,
        # as currently, we are appending that as the last item to
        # distinct and order_by (see in get_forms and get_forms_count)
        if (manager_ids or search) and table == JobSafetyBriefing:
            if order_by is not None:
                # We only support ordering on created_at and updated_at
                cols = []
                for ob in order_by:
                    if ob.field == "created_at":
                        cols.append(JobSafetyBriefing.created_at)
                    elif ob.field == "updated_at":
                        cols.append(JobSafetyBriefing.updated_at)
                cols.append(JobSafetyBriefing.id)  # type: ignore

                statement = statement.distinct(*cols)
            else:
                statement = statement.distinct(
                    JobSafetyBriefing.created_at, JobSafetyBriefing.id
                )

        return statement

    async def get_forms(
        self,
        form_name: Optional[list[str]] = None,
        form_id: Optional[list[str]] = None,
        form_status: Optional[list[FormStatus]] = None,
        project_ids: Optional[list[UUID]] = None,
        location_ids: Optional[list[UUID]] = None,
        created_by_ids: Optional[list[UUID]] = None,
        updated_by_ids: Optional[list[UUID]] = None,
        start_created_at: Optional[datetime.date] = None,
        end_created_at: Optional[datetime.date] = None,
        start_updated_at: Optional[datetime.date] = None,
        end_updated_at: Optional[datetime.date] = None,
        order_by: Optional[list[OrderBy]] = None,
        limit: int | None = 20,
        offset: int | None = None,
        search: Optional[str] = None,
        filter_search: Optional[dict] = None,
        ad_hoc: bool = False,
        with_archived: bool = False,
        tenant_id: Optional[UUID] = None,
        with_contents: bool = False,
        start_completed_at: Optional[datetime.date] = None,
        end_completed_at: Optional[datetime.date] = None,
        start_report_date: Optional[datetime.date] = None,
        end_report_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        operating_region_names: Optional[list[str]] = None,
        manager_ids: Optional[list[str]] = None,
    ) -> list[tuple[Form, Optional[str]]]:
        form_statements: list[Select | None] = []

        # TODO refactor into some sort of enum mapping
        if form_name is None or "JobSafetyBriefing" in form_name:
            form_statements.append(
                self.build_form_statement(
                    table=JobSafetyBriefing,
                    name="JobSafetyBriefing",
                    form_id=form_id,
                    form_status=form_status,
                    project_ids=project_ids,
                    location_ids=location_ids,
                    created_by_ids=created_by_ids,
                    updated_by_ids=updated_by_ids,
                    start_created_at=start_created_at,
                    end_created_at=end_created_at,
                    start_updated_at=start_updated_at,
                    end_updated_at=end_updated_at,
                    search=search,
                    filter_search=filter_search,
                    ad_hoc=ad_hoc,
                    with_archived=with_archived,
                    tenant_id=tenant_id,
                    with_contents=with_contents,
                    start_completed_at=start_completed_at,
                    end_completed_at=end_completed_at,
                    start_report_date=start_report_date,
                    end_report_date=end_report_date,
                    start_date=start_date,
                    end_date=end_date,
                    operating_region_names=operating_region_names,
                    manager_ids=manager_ids,
                    order_by=order_by,
                )
            )

        if form_name is None or "NatGridJobSafetyBriefing" in form_name:
            form_statements.append(
                self.build_form_statement(
                    table=NatGridJobSafetyBriefing,
                    name="NatGridJobSafetyBriefing",
                    form_id=form_id,
                    form_status=form_status,
                    project_ids=project_ids,
                    location_ids=location_ids,
                    created_by_ids=created_by_ids,
                    updated_by_ids=updated_by_ids,
                    start_created_at=start_created_at,
                    end_created_at=end_created_at,
                    start_updated_at=start_updated_at,
                    end_updated_at=end_updated_at,
                    search=search,
                    filter_search=filter_search,
                    ad_hoc=ad_hoc,
                    with_archived=with_archived,
                    tenant_id=tenant_id,
                    with_contents=with_contents,
                    start_completed_at=start_completed_at,
                    end_completed_at=end_completed_at,
                    start_report_date=start_report_date,
                    end_report_date=end_report_date,
                    start_date=start_date,
                    end_date=end_date,
                    operating_region_names=operating_region_names,
                )
            )

        if form_name is None or "DailyReport" in form_name:
            form_statements.append(
                self.build_form_statement(
                    table=DailyReport,
                    name="DailyReport",
                    form_id=form_id,
                    form_status=form_status,
                    project_ids=project_ids,
                    location_ids=location_ids,
                    created_by_ids=created_by_ids,
                    updated_by_ids=updated_by_ids,
                    start_created_at=start_created_at,
                    end_created_at=end_created_at,
                    start_updated_at=start_updated_at,
                    end_updated_at=end_updated_at,
                    search=search,
                    filter_search=filter_search,
                    ad_hoc=ad_hoc,
                    with_archived=with_archived,
                    tenant_id=tenant_id,
                    with_contents=with_contents,
                    start_completed_at=start_completed_at,
                    end_completed_at=end_completed_at,
                    start_report_date=start_report_date,
                    end_report_date=end_report_date,
                    start_date=start_date,
                    end_date=end_date,
                    operating_region_names=operating_region_names,
                )
            )

        if (location_ids is None and project_ids is None) and (
            form_name is None or "EnergyBasedObservation" in form_name
        ):
            form_statements.append(
                self.build_form_statement(
                    table=EnergyBasedObservation,
                    name="EnergyBasedObservation",
                    form_id=form_id,
                    form_status=form_status,
                    project_ids=None,
                    location_ids=None,
                    created_by_ids=created_by_ids,
                    updated_by_ids=updated_by_ids,
                    start_created_at=start_created_at,
                    end_created_at=end_created_at,
                    start_updated_at=start_updated_at,
                    end_updated_at=end_updated_at,
                    search=search,
                    filter_search=filter_search,
                    ad_hoc=ad_hoc,
                    with_archived=with_archived,
                    tenant_id=tenant_id,
                    with_contents=with_contents,
                    start_completed_at=start_completed_at,
                    end_completed_at=end_completed_at,
                    start_report_date=start_report_date,
                    end_report_date=end_report_date,
                    start_date=start_date,
                    end_date=end_date,
                    operating_region_names=operating_region_names,
                )
            )

        # Edge case of requested filters which result in no select statements ran.
        # For example: User requests for only HBOs, but also filters for project locations, which HBOs don't have.
        if not (form_statements := [x for x in form_statements if x is not None]):
            return []

        form_statement = union_all(*form_statements)

        if order_by is not None:
            order_by = order_by + [OrderBy(**{"field": "id", "direction": "asc"})]
            form_statement = set_order_by_raw(form_statement, order_by)
        else:
            # Since we are using pagination, it's critical to have some sort of ordering for consistency.
            form_statement = form_statement.order_by("created_at", "id")

        if limit is not None:
            form_statement = form_statement.limit(limit)

        if offset is not None:
            form_statement = form_statement.offset(offset)

        rows: list[Row] = (await self.session.execute(form_statement)).all()

        # Since we are not selecting SQLModel models directly, the resulting type is sqlalchemy rows.
        # We need to parse as correct types.
        results: list[tuple[Form, Optional[str]]] = []

        for row in rows:
            row_dict = dict(row)
            if row.name == "DailyReport":
                results.append(
                    (DailyReport.parse_obj(row_dict), row_dict.get("operating_hq"))
                )
            elif row.name == "JobSafetyBriefing":
                jsb = JobSafetyBriefing.parse_obj(row_dict)
                results.append((jsb, row_dict.get("operating_hq")))
            elif row.name == "EnergyBasedObservation":
                ebo = EnergyBasedObservation.parse_obj(row_dict)
                results.append((ebo, row_dict.get("operating_hq")))
            elif row.name == "NatGridJobSafetyBriefing":
                natgrid_jsb = NatGridJobSafetyBriefing.parse_obj(row_dict)
                results.append((natgrid_jsb, row_dict.get("operating_hq")))

        return results

    async def get_forms_count(
        self,
        form_name: Optional[list[str]] = None,
        form_id: Optional[list[str]] = None,
        form_status: Optional[list[FormStatus]] = None,
        project_ids: Optional[list[UUID]] = None,
        location_ids: Optional[list[UUID]] = None,
        created_by_ids: Optional[list[UUID]] = None,
        updated_by_ids: Optional[list[UUID]] = None,
        start_created_at: Optional[datetime.date] = None,
        end_created_at: Optional[datetime.date] = None,
        start_updated_at: Optional[datetime.date] = None,
        end_updated_at: Optional[datetime.date] = None,
        search: Optional[str] = None,
        ad_hoc: bool = False,
        with_archived: bool = False,
        tenant_id: Optional[UUID] = None,
        start_completed_at: Optional[datetime.date] = None,
        end_completed_at: Optional[datetime.date] = None,
        start_report_date: Optional[datetime.date] = None,
        end_report_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        operating_region_names: Optional[list[str]] = None,
        manager_ids: Optional[list[str]] = None,
    ) -> int:
        form_statements: list[Select | None] = []

        if form_name is None or "JobSafetyBriefing" in form_name:
            j = self.build_form_statement(
                table=JobSafetyBriefing,
                name="JobSafetyBriefing",
                form_id=form_id,
                form_status=form_status,
                project_ids=project_ids,
                location_ids=location_ids,
                created_by_ids=created_by_ids,
                updated_by_ids=updated_by_ids,
                start_created_at=start_created_at,
                end_created_at=end_created_at,
                start_updated_at=start_updated_at,
                end_updated_at=end_updated_at,
                search=search,
                ad_hoc=ad_hoc,
                with_archived=with_archived,
                tenant_id=tenant_id,
                start_completed_at=start_completed_at,
                end_completed_at=end_completed_at,
                start_report_date=start_report_date,
                end_report_date=end_report_date,
                start_date=start_date,
                end_date=end_date,
                operating_region_names=operating_region_names,
                manager_ids=manager_ids,
            )

            if j is not None:
                if manager_ids:
                    form_statements.append(select(func.count()).select_from(j))  # type: ignore
                else:
                    form_statements.append(
                        j.with_only_columns([func.count()]).order_by(None)
                    )

        if form_name is None or "NatGridJobSafetyBriefing" in form_name:
            natgrid_jsb = self.build_form_statement(
                table=NatGridJobSafetyBriefing,
                name="NatGridJobSafetyBriefing",
                form_id=form_id,
                form_status=form_status,
                project_ids=project_ids,
                location_ids=location_ids,
                created_by_ids=created_by_ids,
                updated_by_ids=updated_by_ids,
                start_created_at=start_created_at,
                end_created_at=end_created_at,
                start_updated_at=start_updated_at,
                end_updated_at=end_updated_at,
                search=search,
                ad_hoc=ad_hoc,
                with_archived=with_archived,
                tenant_id=tenant_id,
                start_completed_at=start_completed_at,
                end_completed_at=end_completed_at,
                start_report_date=start_report_date,
                end_report_date=end_report_date,
                start_date=start_date,
                end_date=end_date,
                operating_region_names=operating_region_names,
            )

            if natgrid_jsb is not None:
                form_statements.append(
                    natgrid_jsb.with_only_columns([func.count()]).order_by(None)
                )

        if form_name is None or "DailyReport" in form_name:
            d = self.build_form_statement(
                table=DailyReport,
                name="DailyReport",
                form_id=form_id,
                form_status=form_status,
                project_ids=project_ids,
                location_ids=location_ids,
                created_by_ids=created_by_ids,
                updated_by_ids=updated_by_ids,
                start_created_at=start_created_at,
                end_created_at=end_created_at,
                start_updated_at=start_updated_at,
                end_updated_at=end_updated_at,
                search=search,
                ad_hoc=ad_hoc,
                with_archived=with_archived,
                tenant_id=tenant_id,
                start_completed_at=start_completed_at,
                end_completed_at=end_completed_at,
                start_report_date=start_report_date,
                end_report_date=end_report_date,
                start_date=start_date,
                end_date=end_date,
                operating_region_names=operating_region_names,
            )

            if d is not None:
                form_statements.append(
                    d.with_only_columns([func.count()]).order_by(None)
                )

        if (location_ids is None and project_ids is None) and (
            form_name is None or "EnergyBasedObservation" in form_name
        ):
            e = self.build_form_statement(
                table=EnergyBasedObservation,
                name="EnergyBasedObservation",
                form_id=form_id,
                form_status=form_status,
                project_ids=None,
                location_ids=None,
                created_by_ids=created_by_ids,
                updated_by_ids=updated_by_ids,
                start_created_at=start_created_at,
                end_created_at=end_created_at,
                start_updated_at=start_updated_at,
                end_updated_at=end_updated_at,
                search=search,
                ad_hoc=ad_hoc,
                with_archived=with_archived,
                tenant_id=tenant_id,
                start_completed_at=start_completed_at,
                end_completed_at=end_completed_at,
                start_report_date=start_report_date,
                end_report_date=end_report_date,
                start_date=start_date,
                end_date=end_date,
                operating_region_names=operating_region_names,
            )

            if e is not None:
                form_statements.append(
                    e.with_only_columns([func.count()]).order_by(None)
                )

        if not (form_statements := [x for x in form_statements if x is not None]):
            return 0

        form_statement = union_all(*form_statements)

        forms_count = (await self.session.execute(form_statement)).all()

        total: int = sum(tup[0] for tup in forms_count)

        return total if total else 0
