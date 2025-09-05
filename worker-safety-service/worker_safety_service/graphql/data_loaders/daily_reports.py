import datetime
import uuid
from typing import Collection, Optional

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    DailyReport,
    DailyReportAdditionalInformationSection,
    DailyReportAttachmentSection,
    DailyReportCrewSection,
    DailyReportJobHazardAnalysisSection,
    DailyReportTaskSelectionSection,
    DailyReportWorkSchedule,
    FormStatus,
    User,
)
from worker_safety_service.models.base import DictModel
from worker_safety_service.models.concepts import DailySourceInformationConcepts
from worker_safety_service.types import (
    DailyReportOrderByField,
    OrderBy,
    OrderByDirection,
)


class TenantDailyReportsLoader:
    def __init__(
        self,
        daily_report_manager: DailyReportManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = daily_report_manager
        self.me = DataLoader(load_fn=self.load_daily_reports)
        self.with_archived = DataLoader(load_fn=self.load_daily_reports)

    async def load_daily_reports(
        self, ids: list[uuid.UUID]
    ) -> list[DailyReport | None]:
        items = await self.__manager.get_daily_reports_by_ids(
            ids, tenant_id=self.tenant_id
        )
        return [items.get(i) for i in ids]

    async def get_daily_report(
        self, id: uuid.UUID, status: Optional[FormStatus] = None
    ) -> DailyReport | None:
        return await self.__manager.get_daily_report(
            id, status=status, tenant_id=self.tenant_id
        )

    async def get_daily_reports(
        self,
        id: uuid.UUID | None = None,
        project_location_ids: Collection[uuid.UUID] | None = None,
        date: datetime.date | None = None,
        start_date: datetime.date | None = None,
        end_date: datetime.date | None = None,
        status: FormStatus | None = None,
        created_by: User | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
    ) -> list[DailyReport]:
        return await self.__manager.get_daily_reports(
            tenant_id=self.tenant_id,
            id=id,
            project_location_ids=project_location_ids,
            date=date,
            start_date=start_date,
            end_date=end_date,
            status=status,
            created_by=created_by,
            order_by=order_by,
            limit=limit,
        )

    async def get_daily_report_recommendation(
        self,
        project_location_id: uuid.UUID,
        created_by: Optional[User] = None,
    ) -> Optional[DailyReport]:
        order_by = OrderBy(
            field=DailyReportOrderByField.COMPLETED_AT.value,
            direction=OrderByDirection.DESC.value,
        )
        reports = await self.get_daily_reports(
            project_location_ids=[project_location_id],
            status=FormStatus.COMPLETE,
            created_by=created_by,
            order_by=[order_by],
            limit=1,
        )
        # recommend most recently completed report
        if reports:
            report: DailyReport = sorted(
                # completed reports always have completed at
                reports,
                key=lambda report: report.completed_at,  # type: ignore
                reverse=True,
            )[0]
            return report
        return None

    async def archive_daily_report(
        self,
        daily_report: DailyReport,
        user: User,
        token: str | None = None,
    ) -> None:
        db_daily_report = await self.get_daily_report(daily_report.id)
        if not db_daily_report:
            raise ResourceReferenceException("Report does not exist.")
        return await self.__manager.archive_daily_report(
            daily_report=daily_report, user=user, token=token
        )

    async def update_status(
        self,
        user: User,
        daily_report: DailyReport,
        new_status: FormStatus,
        token: str | None = None,
    ) -> None:
        db_daily_report = await self.get_daily_report(daily_report.id)
        if not db_daily_report:
            raise ResourceReferenceException("Report does not exist.")
        return await self.__manager.update_status(
            user=user, daily_report=daily_report, new_status=new_status, token=token
        )

    async def save_daily_report(
        self,
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
        token: str | None = None,
        dailySourceInfo: DailySourceInformationConcepts | None = None,
    ) -> DailyReport:
        # TODO: Fix this when the project location loader is in
        return await self.__manager.save_daily_report(
            self.tenant_id,
            daily_report_id,
            project_location_id,
            date,
            created_by,
            work_schedule,
            task_selection,
            job_hazard_analysis,
            safety_and_compliance,
            crew,
            attachments,
            additional_information,
            dailySourceInfo,
            token,
        )

    async def inject_job_hazard_analysis_names(
        self, job_hazard_analysis: DailyReportJobHazardAnalysisSection
    ) -> None:
        await self.__manager.inject_job_hazard_analysis_names(job_hazard_analysis)
