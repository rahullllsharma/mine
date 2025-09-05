import datetime
from typing import Any, Dict, Optional, TypedDict
from uuid import UUID

from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Column, DateTime, Field, SQLModel


class MetricModelConfig(TypedDict, total=False):
    # Columns used to group metric on fetch
    entity_id_fields: list[str]
    # Column that links entity model
    entity_column: str
    average_class: type["TenantRiskModelBase"]
    stddev_class: type["TenantRiskModelBase"]


class RiskModelBase(SQLModel):
    calculated_at: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            primary_key=True,
            nullable=False,
            default=func.now(),
        ),
    )
    value: float
    inputs: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB, index=False))
    params: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB, index=False))


class GenericRiskModelBase(
    RiskModelBase
):  # TODO delete when all have __metric_config__
    __metric_config__: MetricModelConfig


class TenantRiskModelBase(RiskModelBase):
    __metric_config__ = MetricModelConfig(entity_id_fields=["tenant_id"])

    tenant_id: UUID = Field(foreign_key="tenants.id", nullable=False)


class GblContractorProjectHistoryBaselineModel(RiskModelBase, table=True):
    __tablename__ = "rm_gbl_contractor_project_history_bsl"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)
    tenant_id: UUID = Field(nullable=False)  # Could create a foreign key in the future


class GblContractorProjectHistoryBaselineModelStdDev(RiskModelBase, table=True):
    __tablename__ = "rm_gbl_contractor_project_history_bsl_stddev"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)
    tenant_id: UUID = Field(nullable=False)  # Could create a foreign key in the future


class ContractorSafetyHistoryModel(RiskModelBase, table=True):
    __tablename__ = "rm_contractor_safety_history"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "contractor_id"),)
    contractor_id: UUID = Field(primary_key=True, nullable=False)


class ContractorProjectExecutionModel(RiskModelBase, table=True):
    __tablename__ = "rm_contractor_project_execution"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "contractor_id"),)
    contractor_id: UUID = Field(primary_key=True, nullable=False)


class ContractorSafetyRatingModel(RiskModelBase, table=True):
    __tablename__ = "rm_contractor_safety_rating"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "contractor_id"),)
    contractor_id: UUID = Field(primary_key=True, nullable=False)


class AverageContractorSafetyScoreModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_average_contractor_safety_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class StdDevContractorSafetyScoreModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_stddev_contractor_safety_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class ContractorSafetyScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_contractor_safety_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "contractor_id"),)
    __metric_config__ = MetricModelConfig(
        entity_column="contractor_id",
        average_class=AverageContractorSafetyScoreModel,
        stddev_class=StdDevContractorSafetyScoreModel,
    )

    contractor_id: UUID = Field(primary_key=True, nullable=False)


class AverageSupervisorEngagementFactorModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_average_supervisor_engagement_factor"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class StdDevSupervisorEngagementFactorModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_stddev_supervisor_engagement_factor"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class SupervisorEngagementFactorModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_supervisor_engagement_factor"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "supervisor_id"),)
    __metric_config__ = MetricModelConfig(
        entity_column="supervisor_id",
        average_class=AverageSupervisorEngagementFactorModel,
        stddev_class=StdDevSupervisorEngagementFactorModel,
    )

    # todo: Update this to be a foreign key when the table exists
    supervisor_id: UUID = Field(primary_key=True, nullable=False)


class AverageSupervisorRelativePrecursorRiskModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_average_supervisor_relative_precursor_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class StdDevSupervisorRelativePrecursorRiskModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_stddev_supervisor_relative_precursor_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class SupervisorRelativePrecursorRiskModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_supervisor_relative_precursor_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "supervisor_id"),)
    __metric_config__ = MetricModelConfig(
        entity_column="supervisor_id",
        average_class=AverageSupervisorRelativePrecursorRiskModel,
        stddev_class=StdDevSupervisorRelativePrecursorRiskModel,
    )

    # todo: Update this to be a foreign key when the table exists
    supervisor_id: UUID = Field(primary_key=True, nullable=False)


class AverageCrewRiskModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_average_crew_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class StdDevCrewRiskModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_stddev_crew_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id"),)


class CrewRiskModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_crew_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "crew_id"),)
    __metric_config__ = MetricModelConfig(
        entity_column="crew_id",
        average_class=AverageCrewRiskModel,
        stddev_class=StdDevCrewRiskModel,
    )
    crew_id: UUID = Field(primary_key=True, foreign_key="crew.id", nullable=False)


class TaskSpecificSiteConditionsMultiplierModel(RiskModelBase, table=True):
    __tablename__ = "rm_task_specific_site_conditions_multiplier"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_task_id", "date"),)
    project_task_id: UUID = Field(foreign_key="tasks.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class TaskSpecificSafetyClimateMultiplierModel(TenantRiskModelBase, table=True):
    __tablename__ = "rm_task_specific_safety_climate_multiplier"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "library_task_id"),)
    library_task_id: UUID = Field(foreign_key="library_tasks.id", nullable=False)


class TaskSpecificRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_task_specific_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_task_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="project_task_id")
    project_task_id: UUID = Field(foreign_key="tasks.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class ProjectTotalTaskRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_project_total_task_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_id"),)
    __metric_config__ = MetricModelConfig(entity_column="project_id")
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class ProjectLocationTotalTaskRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_project_location_total_task_risk_score"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "project_location_id", "date"),
    )
    __metric_config__ = MetricModelConfig(entity_column="project_location_id")
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class ManuallyAddedSiteConditionModel(RiskModelBase, table=True):
    __tablename__ = "rm_manually_added_site_conditions"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_location_id"),)
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )


class TotalProjectLocationRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_total_project_location_risk_score"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "project_location_id", "date"),
    )
    __metric_config__ = MetricModelConfig(entity_column="project_location_id")
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class TotalProjectRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_total_project_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="project_id")
    project_id: UUID = Field(foreign_key="projects.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class ProjectLocationSiteConditionsMultiplierModel(RiskModelBase, table=True):
    __tablename__ = "rm_project_site_conditions_multiplier"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "project_location_id", "date"),
    )
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class ProjectSafetyClimateMultiplierModel(RiskModelBase, table=True):
    __tablename__ = "rm_project_location_safety_climate_multiplier"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_location_id"),)
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    contractor_id: Optional[UUID] = None
    supervisor_id: Optional[UUID] = None


class LibraryTaskRelativePrecursorRiskModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_librarytask_relative_precursor_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "library_task_id"),)
    __metric_config__ = MetricModelConfig(entity_column="library_task_id")

    library_task_id: UUID = Field(
        primary_key=True, foreign_key="library_tasks.id", nullable=False
    )


class StochasticTaskSpecificRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_stochastic_task_specific_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_task_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="project_task_id")
    project_task_id: UUID = Field(
        primary_key=True, foreign_key="tasks.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class StochasticLocationTotalTaskRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_stochastic_location_total_task_risk_score"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "project_location_id", "date"),
    )
    __metric_config__ = MetricModelConfig(entity_column="project_location_id")
    project_location_id: UUID = Field(
        foreign_key="project_locations.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class LibrarySiteConditionRelativePrecursorRiskModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_library_site_condition_relative_precursor_risk"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "tenant_id", "library_site_condition_id"),
    )
    __metric_config__ = MetricModelConfig(entity_column="library_site_condition_id")

    tenant_id: UUID = Field(foreign_key="tenants.id", primary_key=True, nullable=False)
    library_site_condition_id: UUID = Field(
        primary_key=True, foreign_key="library_site_conditions.id", nullable=False
    )


class StochasticActivitySiteConditionRelativePrecursorRiskScoreModel(
    GenericRiskModelBase, table=True
):
    __tablename__ = "rm_stochastic_activity_sc_relative_precursor_risk_score"
    __table_args__ = (
        Index("rm_stochastic_activity_sc_entity_idx", "activity_id", "date"),
    )
    __metric_config__ = MetricModelConfig(entity_column="activity_id")
    activity_id: UUID = Field(foreign_key="activities.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class StochasticActivityTotalTaskRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_stochastic_activity_total_task_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "activity_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="activity_id")
    activity_id: UUID = Field(foreign_key="activities.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class DivisionRelativePrecursorRiskModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_division_relative_precursor_risk"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "tenant_id", "division_id"),)
    __metric_config__ = MetricModelConfig(entity_column="division_id")

    tenant_id: UUID = Field(foreign_key="tenants.id", primary_key=True, nullable=False)
    division_id: UUID = Field(
        primary_key=True, foreign_key="library_divisions.id", nullable=False
    )


class TotalActivityRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_total_activity_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "activity_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="activity_id")

    activity_id: UUID = Field(foreign_key="activities.id", nullable=False)
    date: datetime.date = Field(nullable=False)


class StochasticTotalLocationRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_stochastic_total_location_risk_score"
    __table_args__ = (
        Index(f"{__tablename__}_entity_idx", "project_location_id", "date"),
    )
    __metric_config__ = MetricModelConfig(entity_column="project_location_id")
    project_location_id: UUID = Field(
        primary_key=True, foreign_key="project_locations.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


class StochasticTotalWorkPackageRiskScoreModel(GenericRiskModelBase, table=True):
    __tablename__ = "rm_stochastic_total_work_package_risk_score"
    __table_args__ = (Index(f"{__tablename__}_entity_idx", "project_id", "date"),)
    __metric_config__ = MetricModelConfig(entity_column="project_id")
    project_id: UUID = Field(
        primary_key=True, foreign_key="projects.id", nullable=False
    )
    date: datetime.date = Field(nullable=False)


# TODO: Name and tenant must be PK
class RiskModelParameters(SQLModel, table=True):
    __tablename__ = "rm_calc_parameters"

    name: str = Field(..., primary_key=True, nullable=False)
    tenant_id: Optional[UUID] = Field(foreign_key="tenants.id")
    value: str
