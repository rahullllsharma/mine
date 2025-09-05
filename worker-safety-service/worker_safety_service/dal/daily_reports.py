import asyncio
import datetime
import uuid
from collections import Counter, defaultdict
from typing import TYPE_CHECKING, Any, Collection, Coroutine, Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.sql.expression import col

from worker_safety_service.audit_trail import (
    audit_archive,
    audit_complete,
    audit_create,
    audit_reopen,
)
from worker_safety_service.dal.audit_events import create_audit_event
from worker_safety_service.models import (
    AsyncSession,
    AuditEventType,
    DailyReport,
    DailyReportAdditionalInformationSection,
    DailyReportAttachmentSection,
    DailyReportCrewSection,
    DailyReportJobHazardAnalysisSection,
    DailyReportSections,
    DailyReportSiteConditionAnalysis,
    DailyReportTaskAnalysis,
    DailyReportTaskSelection,
    DailyReportTaskSelectionSection,
    DailyReportWorkSchedule,
    DictModel,
    FormStatus,
    LibraryRegion,
    Location,
    User,
    WorkPackage,
    set_order_by,
)
from worker_safety_service.models.concepts import (
    Completion,
    DailySourceInformationConcepts,
)
from worker_safety_service.types import OrderBy

if TYPE_CHECKING:
    from worker_safety_service.dal.tasks import TaskManager
    from worker_safety_service.dal.site_conditions import SiteConditionManager

from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)


class DailyReportManager:
    def __init__(
        self,
        session: AsyncSession,
        task_manager: "TaskManager",
        site_condition_manager: "SiteConditionManager",
    ):
        self.session = session
        self.task_manager = task_manager
        self.site_condition_manager = site_condition_manager

    async def get_daily_reports_by_ids(
        self,
        ids: list[uuid.UUID],
        status: Optional[FormStatus] = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> dict[uuid.UUID, DailyReport]:
        statement = select(DailyReport).where(col(DailyReport.id).in_(ids))
        if status:
            statement = statement.where(DailyReport.status == status)
        if tenant_id:
            statement = (
                statement.join(Location)
                .join(WorkPackage)
                .where(WorkPackage.tenant_id == tenant_id)
            )
        return {i.id: i for i in (await self.session.exec(statement)).all()}

    async def get_daily_report(
        self,
        id: uuid.UUID,
        status: Optional[FormStatus] = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> DailyReport | None:
        items = await self.get_daily_reports_by_ids(
            [id], status=status, tenant_id=tenant_id
        )
        return items.get(id)

    async def get_daily_reports(
        self,
        *,
        id: uuid.UUID | None = None,
        project_location_ids: Collection[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        updated_at_start_date: datetime.datetime | None = None,
        updated_at_end_date: datetime.datetime | None = None,
        tenant_id: uuid.UUID | None = None,
        status: FormStatus | None = None,
        created_by: User | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        skip: int | None = None,
        initial_load: bool = False,
    ) -> list[DailyReport]:
        if project_location_ids is not None and not project_location_ids:
            return []

        statement = select(DailyReport).where(col(DailyReport.archived_at).is_(None))

        if tenant_id:
            statement = (
                statement.join(Location)
                .join(WorkPackage)
                .where(WorkPackage.tenant_id == tenant_id)
            )
        if id:
            statement = statement.where(DailyReport.id == id)
        if project_location_ids:
            statement = statement.where(
                col(DailyReport.project_location_id).in_(project_location_ids)
            )
        if date:
            assert_date(date)
            statement = statement.where(DailyReport.date_for == date)
        if start_date:
            assert_date(start_date)
            statement = statement.where(DailyReport.date_for >= start_date)
        if end_date:
            assert_date(end_date)
            statement = statement.where(DailyReport.date_for <= end_date)
        if updated_at_start_date:
            statement = statement.where(DailyReport.updated_at >= updated_at_start_date)
        if updated_at_end_date:
            statement = statement.where(DailyReport.updated_at <= updated_at_end_date)
        if status:
            statement = statement.where(DailyReport.status == status)

        if filter_start_date and filter_end_date:
            assert_date(filter_start_date)
            assert_date(filter_end_date)
            statement = statement.where(
                (DailyReport.date_for >= filter_start_date)
                & (DailyReport.date_for <= filter_end_date)
            )
        if created_by:
            statement = statement.where(DailyReport.created_by_id == created_by.id)
        if order_by:
            statement = set_order_by(DailyReport, statement, order_by=order_by)
        else:
            statement = statement.order_by(desc(DailyReport.updated_at))
        if skip:
            statement = statement.offset(skip)
        if limit and not initial_load:
            statement = statement.limit(limit)

        return (await self.session.exec(statement)).all()

    async def get_daily_reports_by_location(
        self,
        project_location_ids: list[uuid.UUID],
        date: datetime.date | None = None,
        filter_start_date: datetime.date | None = None,
        filter_end_date: datetime.date | None = None,
        tenant_id: uuid.UUID | None = None,
    ) -> defaultdict[uuid.UUID, list[DailyReport]]:
        items: defaultdict[uuid.UUID, list[DailyReport]] = defaultdict(list)
        for daily_report in await self.get_daily_reports(
            project_location_ids=project_location_ids,
            date=date,
            filter_start_date=filter_start_date,
            filter_end_date=filter_end_date,
            tenant_id=tenant_id,
        ):
            items[daily_report.project_location_id].append(daily_report)
        return items

    async def validate_task_selection(
        self, daily_report: DailyReport, task_selection: list[DailyReportTaskSelection]
    ) -> None:
        task_ids = [i.id for i in task_selection]
        if not task_ids:
            return None

        # Let see if we have something new before checking the DB
        task_ids_set = set(task_ids)
        sections = daily_report.sections_to_pydantic()
        if sections and sections.task_selection:
            existing_ids = {i.id for i in sections.task_selection.selected_tasks}
            if existing_ids == task_ids_set:
                return None

        invalid_task_ids = task_ids_set.difference(
            task.id
            for _, task in await self.task_manager.get_tasks(
                location_ids=[daily_report.project_location_id], with_archived=True
            )
        )
        if invalid_task_ids:
            invalid_ids_str = ", ".join(map(str, invalid_task_ids))
            raise ValueError(
                f"Task IDs {invalid_ids_str} don't exist in project location"
            )
        else:
            return None

    def _validate_lists(
        self,
        ids: list[uuid.UUID],
        allowed_ids: set[uuid.UUID],
        duplicated_msg: str = "Duplicated id: {duplicated_id}",
        invalid_msg: str = "Invalid ids: {invalid_ids_str}",
    ) -> None:
        """
        Checks generic lists of ids for:
          - no duplication
          - no disallowed
        """
        if not ids:
            return None

        duplicated_id, length = Counter(ids).most_common(1)[0]
        if length > 1:
            raise ValueError(duplicated_msg.format(duplicated_id=duplicated_id))

        invalid_ids = set(ids).difference(allowed_ids)
        if invalid_ids:
            invalid_ids_str = ", ".join(map(str, invalid_ids))
            raise ValueError(invalid_msg.format(invalid_ids_str=invalid_ids_str))

    async def validate_job_hazard_analysis_site_conditions(
        self,
        daily_report: DailyReport,
        site_conditions: list[DailyReportSiteConditionAnalysis],
    ) -> None:
        site_condition_ids = [i.id for i in site_conditions]
        if not site_condition_ids:
            return None

        allowed_ids = {
            i.id
            for _, i in await self.site_condition_manager.get_site_conditions(
                location_ids=[daily_report.project_location_id],
                date=daily_report.date_for,
                with_archived=True,
            )
        }

        self._validate_lists(
            site_condition_ids,
            allowed_ids,
            "SiteCondition ID {duplicated_id} duplicated on site condition analysis",
            "Site condition IDs {invalid_ids_str} don't exist in project location",
        )

        for site_condition in site_conditions:
            hazard_ids = [i.id for i in site_condition.hazards]
            if not hazard_ids:
                continue

            allowed_hazard_ids = {
                i.id
                for _, i in await self.site_condition_manager.get_hazards(
                    site_condition_ids=[site_condition.id], with_archived=True
                )
            }

            self._validate_lists(
                hazard_ids,
                allowed_hazard_ids,
                "Hazard ID {duplicated_id} duplicated on site condition analysis hazard",
                "Hazard IDs {invalid_ids_str} don't exist on site condition",
            )

            for hazard in site_condition.hazards:
                control_ids = [i.id for i in hazard.controls]
                if not control_ids:
                    continue

                allowed_control_ids = {
                    i.id
                    for _, i in await self.site_condition_manager.get_controls(
                        site_condition_id=site_condition.id, with_archived=True
                    )
                }

                self._validate_lists(
                    control_ids,
                    allowed_control_ids,
                    "Control ID {duplicated_id} duplicated on site condition analysis hazard controls",
                    "Control IDs {invalid_ids_str} don't exist on site condition hazard",
                )

        return None

    async def validate_job_hazard_analysis_tasks(
        self, daily_report: DailyReport, tasks: list[DailyReportTaskAnalysis]
    ) -> None:
        task_ids = [i.id for i in tasks]
        if not task_ids:
            return None

        allowed_ids = {
            task.id
            for _, task in await self.task_manager.get_tasks(
                location_ids=[daily_report.project_location_id], with_archived=True
            )
        }

        self._validate_lists(
            task_ids,
            allowed_ids,
            "Task ID {duplicated_id} duplicated in task analysis",
            "Task IDs {invalid_ids_str} don't exist in project location",
        )

        for task in tasks:
            hazard_ids = [i.id for i in task.hazards]
            if not hazard_ids:
                continue

            allowed_hazard_ids = {
                i.id
                for _, i in await self.task_manager.get_hazards(
                    task_ids=[task.id], with_archived=True
                )
            }

            self._validate_lists(
                hazard_ids,
                allowed_hazard_ids,
                "Hazard ID {duplicated_id} duplicated on task analysis hazard",
                "Hazard IDs {invalid_ids_str} don't exist on task",
            )

            for hazard in task.hazards:
                control_ids = [i.id for i in hazard.controls]
                if not control_ids:
                    continue

                allowed_control_ids = {
                    i.id
                    for _, i in await self.task_manager.get_controls(
                        task_id=task.id, with_archived=True
                    )
                }

                self._validate_lists(
                    control_ids,
                    allowed_control_ids,
                    "Control ID {duplicated_id} duplicated on task analysis hazard controls",
                    "Control IDs {invalid_ids_str} don't exist on task hazard",
                )

        return None

    async def ensure_location_exists(
        self, location_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> bool:
        statement = select(Location).where(
            Location.id == location_id,
            col(Location.archived_at).is_(None),
            Location.project_id == WorkPackage.id,
            WorkPackage.tenant_id == tenant_id,
        )

        loc = (await self.session.exec(statement)).first()
        return True if loc else False

    async def save_daily_report(
        self,
        tenant_id: uuid.UUID,
        daily_report_id: uuid.UUID | None,
        project_location_id: uuid.UUID,
        date: datetime.date,
        created_by: User,
        work_schedule: DailyReportWorkSchedule | None = None,
        task_selection: DailyReportTaskSelectionSection | None = None,
        job_hazard_analysis: DailyReportJobHazardAnalysisSection | None = None,
        safety_and_compliance: DictModel | None = None,
        crew: DailyReportCrewSection | None = None,
        attachments: DailyReportAttachmentSection | None = None,
        additional_information: DailyReportAdditionalInformationSection | None = None,
        dailySourceInfo: DailySourceInformationConcepts | None = None,
        token: Optional[str] = None,
    ) -> DailyReport:
        daily_report: DailyReport | None
        audit_type = AuditEventType.daily_report_updated
        completions: list[Completion] | None
        if not daily_report_id:
            exists = await self.ensure_location_exists(
                project_location_id, tenant_id=tenant_id
            )
            if not exists:
                raise ValueError("Project location ID not found")

            assert_date(date)
            daily_report = DailyReport(
                project_location_id=project_location_id,
                date_for=date,
                created_by_id=created_by.id,
                tenant_id=tenant_id,
            )
            audit_type = AuditEventType.daily_report_created
            completions = []
        else:
            daily_report = await self.get_daily_report(
                daily_report_id, tenant_id=tenant_id
            )
            if daily_report is None:
                raise ValueError("Daily Report ID not found")
            elif project_location_id != daily_report.project_location_id:
                raise ValueError(
                    "Not allowed to update Daily Report project location id"
                )

            if daily_report.date_for != date:
                daily_report.date_for = date
            daily_report.updated_at = datetime.datetime.now(datetime.timezone.utc)
            sections = daily_report.sections_to_pydantic()
            completions = sections.completions if sections else None

        # Validations
        if task_selection:
            await self.validate_task_selection(
                daily_report, task_selection.selected_tasks
            )

        if job_hazard_analysis:
            await self.validate_job_hazard_analysis_tasks(
                daily_report, job_hazard_analysis.tasks
            )
            await self.validate_job_hazard_analysis_site_conditions(
                daily_report, job_hazard_analysis.site_conditions
            )

        if (
            additional_information is None
            or additional_information.operating_hq is None
        ):
            statement = (
                select(LibraryRegion)
                .join(WorkPackage)
                .join(Location)
                .where(
                    Location.id == project_location_id,
                    col(Location.archived_at).is_(None),
                    Location.project_id == WorkPackage.id,
                    WorkPackage.tenant_id == tenant_id,
                    LibraryRegion.id == WorkPackage.region_id,
                )
            )

            library_region = (await self.session.exec(statement)).first()

            if additional_information is None:
                additional_information = DailyReportAdditionalInformationSection()

            if library_region is not None:
                additional_information.operating_hq = library_region.name

        daily_report.sections = jsonable_encoder(
            DailyReportSections(
                work_schedule=work_schedule,
                task_selection=task_selection,
                job_hazard_analysis=job_hazard_analysis,
                safety_and_compliance=safety_and_compliance,
                crew=crew,
                attachments=attachments,
                additional_information=additional_information,
                completions=completions,
                dailySourceInfo=dailySourceInfo,
            )
        )

        if not daily_report_id:
            if daily_report is not None:
                daily_report = await self.create_daily_report_db(
                    daily_report=daily_report, token=token
                )
        # Set status back to IN_PROGRESS if user tries to update
        previous_status = daily_report.status
        if previous_status == FormStatus.COMPLETE:
            daily_report.status = FormStatus.IN_PROGRESS

        create_audit_event(self.session, audit_type, created_by)

        await self.session.commit()

        logger.info(
            "Daily report saved",
            is_new=bool(daily_report_id),
            daily_report_id=str(daily_report.id),
            previous_status=previous_status.value,
            status=daily_report.status.value,
        )

        return daily_report

    @audit_create
    async def create_daily_report_db(
        self, daily_report: DailyReport, **kwargs: Any
    ) -> DailyReport:
        self.session.add(daily_report)
        return daily_report

    @audit_complete
    async def complete_daily_report_db(
        self, daily_report: DailyReport, **kwargs: Any
    ) -> DailyReport:
        await self.session.commit()
        return daily_report

    @audit_reopen
    async def reopen_daily_report_db(
        self, daily_report: DailyReport, **kwargs: Any
    ) -> DailyReport:
        await self.session.commit()
        return daily_report

    async def update_status(
        self,
        user: User,
        daily_report: DailyReport,
        new_status: FormStatus,
        token: Optional[str] = None,
    ) -> None:
        previous_status = daily_report.status
        if previous_status != new_status:
            daily_report.status = new_status
            now = datetime.datetime.now(datetime.timezone.utc)
            if new_status == FormStatus.COMPLETE:
                completion = Completion(
                    completed_by_id=user.id,
                    completed_at=now,
                )
                if daily_report.completed_at is None:
                    daily_report.completed_by_id = completion.completed_by_id
                    daily_report.completed_at = completion.completed_at

                sections = daily_report.sections_to_pydantic() or DailyReportSections(
                    **{}
                )
                sections.completions = sections.completions or []
                sections.completions.append(completion)
                daily_report.sections = jsonable_encoder(sections)

            daily_report.updated_at = now
            create_audit_event(self.session, AuditEventType.daily_report_updated, user)

            if new_status == FormStatus.COMPLETE:
                daily_report = await self.complete_daily_report_db(
                    daily_report=daily_report, token=token
                )
            elif (
                previous_status == FormStatus.COMPLETE
                and new_status == FormStatus.IN_PROGRESS
            ):
                daily_report = await self.reopen_daily_report_db(
                    daily_report=daily_report, token=token
                )
            else:
                await self.session.commit()

            logger.info(
                "Daily report status updated",
                daily_report_id=str(daily_report.id),
                previous_status=previous_status.value,
                status=daily_report.status.value,
                completed_by_id=(
                    str(daily_report.completed_by_id)
                    if daily_report.completed_by_id
                    else None
                ),
            )

    async def archive_daily_report(
        self,
        daily_report: DailyReport,
        user: User | None = None,
        skip_commit: bool = False,
        skip_audit_event: bool = False,
        token: str | None = None,
    ) -> None:
        daily_report.archived_at = datetime.datetime.now(datetime.timezone.utc)
        daily_report.updated_at = datetime.datetime.now(datetime.timezone.utc)
        if not skip_audit_event:
            create_audit_event(self.session, AuditEventType.daily_report_archived, user)
        if not skip_commit:
            await self.archive_daily_report_db(daily_report=daily_report, token=token)
        logger.info("Daily report archived", daily_report_id=str(daily_report.id))

    @audit_archive
    async def archive_daily_report_db(
        self, daily_report: DailyReport, **kwargs: Any
    ) -> DailyReport:
        await self.session.commit()
        return daily_report

    async def archive_daily_reports(self, location_ids: list[uuid.UUID]) -> None:
        statement = select(DailyReport).where(
            col(DailyReport.project_location_id).in_(location_ids)
        )
        daily_reports = (await self.session.exec(statement)).all()
        for rep in daily_reports:
            await self.archive_daily_report(
                rep, skip_commit=True, skip_audit_event=True
            )

    async def inject_job_hazard_analysis_names(
        self, job_hazard_analysis: DailyReportJobHazardAnalysisSection
    ) -> None:
        # Find all ids
        task_ids: list[uuid.UUID] = []
        task_hazard_ids: list[uuid.UUID] = []
        task_control_ids: list[uuid.UUID] = []
        for task in job_hazard_analysis.tasks:
            task_ids.append(task.id)
            for task_hazard in task.hazards:
                task_hazard_ids.append(task_hazard.id)
                task_control_ids.extend(i.id for i in task_hazard.controls)
        site_condition_ids: list[uuid.UUID] = []
        site_condition_hazard_ids: list[uuid.UUID] = []
        site_condition_control_ids: list[uuid.UUID] = []
        for site_condition in job_hazard_analysis.site_conditions:
            site_condition_ids.append(site_condition.id)
            for site_condition_hazard in site_condition.hazards:
                site_condition_hazard_ids.append(site_condition_hazard.id)
                site_condition_control_ids.extend(
                    i.id for i in site_condition_hazard.controls
                )

        # Fetch data
        futures: list[Coroutine] = []
        if task_ids:
            futures.append(
                self.task_manager.get_tasks(ids=task_ids, with_archived=True)
            )
        if task_hazard_ids:
            futures.append(
                self.task_manager.get_hazards(ids=task_hazard_ids, with_archived=True)
            )
        if task_control_ids:
            futures.append(
                self.task_manager.get_controls(ids=task_control_ids, with_archived=True)
            )
        if site_condition_ids:
            futures.append(
                self.site_condition_manager.get_site_conditions_by_id(
                    site_condition_ids, with_archived=True
                )
            )
        if site_condition_hazard_ids:
            futures.append(
                self.site_condition_manager.get_hazards(
                    ids=site_condition_hazard_ids, with_archived=True
                )
            )
        if site_condition_control_ids:
            futures.append(
                self.site_condition_manager.get_controls(
                    ids=site_condition_control_ids, with_archived=True
                )
            )
        if futures:
            data = await asyncio.gather(*futures)
            next_index = 0

            # Build references
            task_names: dict[uuid.UUID, str] = {}
            if task_ids:
                task_names = {i[1].id: i[0].name for i in data[next_index]}
                next_index += 1
            task_hazard_names: dict[uuid.UUID, str] = {}
            if task_hazard_ids:
                task_hazard_names = {i[1].id: i[0].name for i in data[next_index]}
                next_index += 1
            task_control_names: dict[uuid.UUID, str] = {}
            if task_control_ids:
                task_control_names = {i[1].id: i[0].name for i in data[next_index]}
                next_index += 1
            site_condition_names: dict[uuid.UUID, str] = {}
            if site_condition_ids:
                site_condition_names = {i[1].id: i[0].name for i in data[next_index]}
                next_index += 1
            site_condition_hazard_names: dict[uuid.UUID, str] = {}
            if site_condition_hazard_ids:
                site_condition_hazard_names = {
                    i[1].id: i[0].name for i in data[next_index]
                }
                next_index += 1
            site_condition_control_names: dict[uuid.UUID, str] = {}
            if site_condition_control_ids:
                site_condition_control_names = {
                    i[1].id: i[0].name for i in data[next_index]
                }
                next_index += 1

            # Inject names
            for task in job_hazard_analysis.tasks:
                inject_jha_name(task, task_names)
                for task_hazard in task.hazards:
                    inject_jha_name(task_hazard, task_hazard_names)
                    for task_control in task_hazard.controls:
                        inject_jha_name(task_control, task_control_names)
            for site_condition in job_hazard_analysis.site_conditions:
                inject_jha_name(site_condition, site_condition_names)
                for site_condition_hazard in site_condition.hazards:
                    inject_jha_name(site_condition_hazard, site_condition_hazard_names)
                    for site_condition_control in site_condition_hazard.controls:
                        inject_jha_name(
                            site_condition_control, site_condition_control_names
                        )


def inject_jha_name(obj: Any, names: dict[uuid.UUID, str]) -> None:
    name = names.get(obj.id)
    if not name:
        logger.error("Missing name on JHA daily report", id=obj.id)
        obj.name = "-"
    else:
        obj.name = name
