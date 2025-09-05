import datetime
import uuid
from operator import attrgetter
from typing import TYPE_CHECKING, List, Optional

from pydantic import BaseModel, StrictInt
from sqlalchemy import Index, desc
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, Field, Relationship

import worker_safety_service.utils as utils
from worker_safety_service.models.base import DictModel, Location, RiskLevel
from worker_safety_service.models.concepts import (
    Completion,
    DailySourceInformationConcepts,
)
from worker_safety_service.models.forms import FormBase
from worker_safety_service.models.google_cloud_storage import File

if TYPE_CHECKING:
    from worker_safety_service.models.user import User


class DailyReportWorkSchedule(BaseModel):
    start_datetime: Optional[datetime.datetime]
    end_datetime: Optional[datetime.datetime]
    section_is_valid: bool | None


class DailyReportTaskSelection(BaseModel):
    id: uuid.UUID
    name: str
    risk_level: RiskLevel


class DailyReportTaskSelectionSection(BaseModel):
    selected_tasks: List[DailyReportTaskSelection]
    section_is_valid: bool | None


class DailyReportControlAnalysis(BaseModel):
    id: uuid.UUID
    implemented: bool | None
    not_implemented_reason: str | None
    further_explanation: str | None


class DailyReportHazardAnalysis(BaseModel):
    id: uuid.UUID
    isApplicable: bool
    not_applicable_reason: str | None
    controls: List[DailyReportControlAnalysis]


class DailyReportSiteConditionAnalysis(BaseModel):
    id: uuid.UUID
    isApplicable: bool
    hazards: List[DailyReportHazardAnalysis]


class DailyReportTaskAnalysis(BaseModel):
    id: uuid.UUID
    notes: Optional[str]
    not_applicable_reason: str | None
    performed: bool
    hazards: List[DailyReportHazardAnalysis]
    section_is_valid: bool | None


class DailyReportJobHazardAnalysisSection(BaseModel):
    site_conditions: List[DailyReportSiteConditionAnalysis]
    tasks: List[DailyReportTaskAnalysis]
    section_is_valid: bool | None


class CrewInt(StrictInt):
    ge = 0


class DailyReportCrewSection(BaseModel):
    contractor: Optional[str]
    foreman_name: Optional[str]
    n_welders: Optional[CrewInt]
    n_safety_prof: Optional[CrewInt]
    n_operators: Optional[CrewInt]
    n_flaggers: Optional[CrewInt]
    n_laborers: Optional[CrewInt]
    n_other_crew: Optional[CrewInt]
    documents: Optional[List[File]]
    section_is_valid: bool | None


class DailyReportAttachmentSection(BaseModel):
    documents: Optional[List[File]]
    photos: Optional[List[File]]
    section_is_valid: bool | None


class DailyReportAdditionalInformationSection(BaseModel):
    progress: Optional[str]
    lessons: Optional[str]
    section_is_valid: bool | None
    operating_hq: str | None


class DailyReportSections(BaseModel):
    work_schedule: Optional[DailyReportWorkSchedule]
    task_selection: Optional[DailyReportTaskSelectionSection]
    job_hazard_analysis: Optional[DailyReportJobHazardAnalysisSection]
    safety_and_compliance: Optional[DictModel]
    crew: Optional[DailyReportCrewSection]
    attachments: Optional[DailyReportAttachmentSection]
    additional_information: Optional[DailyReportAdditionalInformationSection]
    completions: Optional[list[Completion]]
    dailySourceInfo: Optional[DailySourceInformationConcepts]


class DailyReport(FormBase, table=True):
    __tablename__ = "daily_reports"
    __table_args__ = (
        Index(f"{__tablename__}_tenant_id_idx", "tenant_id"),
        Index("daily_report_pl_fkey", "project_location_id"),
        Index("daily_reports_created_by_id_ix", "created_by_id"),
        Index("daily_reports_completed_by_id_ix", "completed_by_id"),
        Index("daily_reports_date_for_ix", desc("date_for")),
    )

    created_by: "User" = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "DailyReport.created_by_id==User.id",
            "lazy": "joined",
        }
    )
    project_location_id: uuid.UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    location: Location = Relationship(back_populates="daily_reports")
    completed_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "DailyReport.completed_by_id==User.id",
            "lazy": "joined",
        }
    )

    sections: Optional[dict] = Field(sa_column=Column(JSONB, index=False))

    def sections_to_pydantic(self) -> DailyReportSections | None:
        if self.sections is not None:
            # treat date+time=datetime if necessary
            if self.sections.get("work_schedule") is not None:
                start_date = None
                start_time = None
                end_date = None
                end_time = None

                if "start_time" in self.sections["work_schedule"]:
                    start_time = self.sections["work_schedule"].pop("start_time")
                    if isinstance(start_time, str):
                        start_time = datetime.time.fromisoformat(start_time)
                if "start_date" in self.sections["work_schedule"]:
                    start_date = self.sections["work_schedule"].pop("start_date")
                    if isinstance(start_date, str):
                        start_date = datetime.date.fromisoformat(start_date)
                if "end_time" in self.sections["work_schedule"]:
                    end_time = self.sections["work_schedule"].pop("end_time")
                    if isinstance(end_time, str):
                        end_time = datetime.time.fromisoformat(end_time)
                if "end_date" in self.sections["work_schedule"]:
                    end_date = self.sections["work_schedule"].pop("end_date")
                    if isinstance(end_date, str):
                        end_date = datetime.date.fromisoformat(end_date)

                # Per WS-1641, drop field if information is incomplete
                if start_date and start_time:
                    self.sections["work_schedule"][
                        "start_datetime"
                    ] = datetime.datetime.combine(start_date, start_time)
                if end_date and end_time:
                    self.sections["work_schedule"][
                        "end_datetime"
                    ] = datetime.datetime.combine(end_date, end_time)

            return DailyReportSections.parse_obj(self.sections)
        else:
            return None


def applicable_controls_analyses_by_id(
    reports: List[DailyReport],
) -> dict[uuid.UUID, List[DailyReportControlAnalysis]]:
    """
    Returns task_hazard_controls and site_condition_hazard_controls, indexed
    by uuid, for the passed reports.
    """
    report_controls: List[DailyReportControlAnalysis] = []
    for rep in reports:
        sections = DailyReport.sections_to_pydantic(rep)

        if sections:
            if sections.job_hazard_analysis:
                if sections.job_hazard_analysis.tasks:
                    for t in sections.job_hazard_analysis.tasks:
                        if t.performed is True:
                            for h in t.hazards:
                                if h.isApplicable is True:
                                    report_controls.extend(h.controls)
                if sections.job_hazard_analysis.site_conditions:
                    for c in sections.job_hazard_analysis.site_conditions:
                        if c.isApplicable is True:
                            for h in c.hazards:
                                if h.isApplicable is True:
                                    report_controls.extend(h.controls)

    return utils.groupby(report_controls, key=attrgetter("id"))


def applicable_hazard_analyses_by_id(
    reports: List[DailyReport],
) -> dict[uuid.UUID, List[DailyReportHazardAnalysis]]:
    """
    Returns task_hazards and site_condition_hazards, indexed
    by uuid, for the passed reports.
    """
    report_hazards: List[DailyReportHazardAnalysis] = []
    for rep in reports:
        sections = DailyReport.sections_to_pydantic(rep)

        if sections:
            if sections.job_hazard_analysis:
                if sections.job_hazard_analysis.tasks:
                    for t in sections.job_hazard_analysis.tasks:
                        if t.performed is True:
                            for h in t.hazards:
                                if h.isApplicable is True:
                                    report_hazards.append(h)
                if sections.job_hazard_analysis.site_conditions:
                    for c in sections.job_hazard_analysis.site_conditions:
                        if c.isApplicable is True:
                            for h in c.hazards:
                                if h.isApplicable is True:
                                    report_hazards.append(h)

    return utils.groupby(report_hazards, key=attrgetter("id"))
