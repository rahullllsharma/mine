import datetime
import uuid
from typing import Any, Optional, Type, TypeVar

import typer

from worker_safety_service.cli.utils import run_async
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.library import LibraryManager
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.dal.location_clustering import LocationClustering
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.user import UserManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.models import get_session
from worker_safety_service.models.utils import get_sessionmaker
from worker_safety_service.risk_model.metrics.contractor.contractor_project_execution import (
    ContractorProjectExecution,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_history import (
    ContractorSafetyHistory,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_rating import (
    ContractorSafetyRating,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.contractor.gbl_contractor_project_history_bsl import (
    GlobalContractorProjectHistoryBaseline,
    GlobalContractorProjectHistoryBaselineStdDev,
)
from worker_safety_service.risk_model.metrics.contractor.global_contractor_safety_score import (
    GlobalContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.crew.crew_relative_precursor_risk import (
    CrewRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.crew.global_crew_relative_precursor_risk import (
    GlobalCrewRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.global_supervisor_relative_precursor_risk import (
    GlobalSupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.project.project_safety_climate_multiplier import (
    ProjectSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.supervisor_relative_precursor_risk import (
    SupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.project_total_task_riskscore import (
    ProjectTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation

explain_app = typer.Typer()


T = TypeVar("T", bound=MetricCalculation)


# TODO: refactor this (likely into separate methods)
#  to better handle for dynamic insertion of managers
async def explain(metric: Type[T], *args, **kwargs) -> None:  # type: ignore
    async with get_session() as session:
        try:
            configurations_manager = ConfigurationsManager(session)
            metrics_manager = RiskModelMetricsManager(
                get_sessionmaker(), configurations_manager
            )
            contractor_manager = ContractorsManager(session)
            library_manager = LibraryManager(session)
            library_site_condition_manager = LibrarySiteConditionManager(session)
            task_manager = TaskManager(session, library_manager)
            activity_manager = ActivityManager(
                session, task_manager, configurations_manager
            )
            site_condition_manager = SiteConditionManager(
                session, library_manager, library_site_condition_manager
            )
            user_manager = UserManager(session)
            work_type_manager = WorkTypeManager(session)

            if kwargs.get("task_manager"):
                kwargs["task_manager"] = task_manager
            if kwargs.get("contractors_manager"):
                kwargs["contractors_manager"] = contractor_manager
            if kwargs.get("supervisors_manager"):
                kwargs["supervisors_manager"] = SupervisorsManager(session)
            if kwargs.get("work_package_manager"):
                daily_report_manager = DailyReportManager(
                    session, task_manager, site_condition_manager
                )
                locations_manager = LocationsManager(
                    session,
                    activity_manager,
                    daily_report_manager,
                    metrics_manager,
                    site_condition_manager,
                    task_manager,
                    LocationClustering(session),
                )
                kwargs["work_package_manager"] = WorkPackageManager(
                    session,
                    metrics_manager,
                    contractor_manager,
                    library_manager,
                    locations_manager,
                    task_manager,
                    site_condition_manager,
                    user_manager,
                    daily_report_manager,
                    activity_manager,
                    configurations_manager,
                    LocationClustering(session),
                    work_type_manager,
                )
            explains = await metric.explain(metrics_manager, *args, **kwargs)  # type: ignore
            typer.echo()
            typer.echo(
                "****************************** Results ******************************"
            )
            for item in explains:
                typer.echo(item.__repr__())
            typer.echo(
                "*********************************************************************"
            )
        except Exception as e:
            typer.echo(
                "****************************** Results ******************************"
            )
            typer.echo(str(e))
            typer.echo(
                "*********************************************************************"
            )
            # typer.echo(f"Data not found for project {project_id} on date {date}")
            raise typer.Exit()


methods = {
    "total-project-risk-score": {
        "class": TotalProjectRiskScore,
        "managers": ["work_package_manager", "contractors_manager", "task_manager"],
    },
    "total-project-location-risk-score": {
        "class": TotalProjectLocationRiskScore,
        "managers": [
            "work_package_manager",
            "contractors_manager",
            "task_manager",
        ],
    },
    "task-specific-risk-score": {
        "class": TaskSpecificRiskScore,
        "managers": ["task_manager"],
    },
    "project-total-task-risk-score": {
        "class": ProjectTotalTaskRiskScore,
        "managers": ["task_manager"],
    },
    "project-location-total-task-risk-score": {
        "class": ProjectLocationTotalTaskRiskScore,
        "managers": ["task_manager"],
    },
    "contractor-project-execution": {
        "class": ContractorProjectExecution,
        "managers": ["contractors_manager"],
    },
    "contractor-safety-history": {"class": ContractorSafetyHistory, "managers": []},
    "project-location-site-conditions-multiplier": {
        "class": ProjectLocationSiteConditionsMultiplier,
        "managers": [],
    },
    "project-safety-climate-multiplier": {
        "class": ProjectSafetyClimateMultiplier,
        "managers": ["work_package_manager", "contractors_manager"],
    },
    "global-contractor-project-history-baseline": {
        "class": GlobalContractorProjectHistoryBaseline,
        "managers": [],
    },
    "global-contractor-project-history-baseline-stddev": {
        "class": GlobalContractorProjectHistoryBaselineStdDev,
        "managers": [],
    },
    "global-contractor-safety-score": {
        "class": GlobalContractorSafetyScore,
        "managers": ["contractors_manager"],
    },
    "contractor-safety-rating": {"class": ContractorSafetyRating, "managers": []},
    "contractor-safety-score": {
        "class": ContractorSafetyScore,
        "managers": ["contractors_manager"],
    },
    "task-specific-safety-climate-multiplier": {
        "class": TaskSpecificSafetyClimateMultiplier,
        "managers": [],
    },
    "task-specific-site-conditions-multiplier": {
        "class": TaskSpecificSiteConditionsMultiplier,
        "managers": [],
    },
    "global-supervisor-engagement-factor": {
        "class": GlobalSupervisorEngagementFactor,
        "managers": ["supervisors_manager"],
    },
    "supervisor-engagement-factor": {
        "class": SupervisorEngagementFactor,
        "managers": [],
    },
    "global-supervisor-relative-precursor-risk": {
        "class": GlobalSupervisorRelativePrecursorRisk,
        "managers": [],
    },
    "supervisor-relative-precursor-risk": {
        "class": SupervisorRelativePrecursorRisk,
        "managers": [],
    },
    "global-crew-factor": {
        "class": GlobalCrewRelativePrecursorRisk,
        "managers": [],
    },
    "crew-risk": {
        "class": CrewRelativePrecursorRisk,
        "managers": [],
    },
}


async def run(
    metric: str,
    **kwargs: Any,
) -> None:
    """
    Needed to create a separate `run` method that could be called from tests

    This takes in a string (the string that is passed to the CLI) and fetches the
    corresponding class from the dictionary above. Then it cycles through the
    necessary managers and creates kwargs that include <manager>=True, along with
    any kwargs passed into the CLI tool. It is this method that then calls the `explain`
    method.
    """

    instance = methods.get(metric)
    if instance is not None:
        managers = instance.get("managers")
        if managers is not None:
            for manager in managers:  # type: ignore
                kwargs[manager] = True
        metric_class = instance.get("class")
        if metric_class is not None:
            await explain(metric_class, **kwargs)  # type: ignore


@explain_app.command(name="total-project-risk-score")
@run_async
async def total_project_risk_score(
    project_id: uuid.UUID = typer.Argument(
        ..., help="The ID of the project in question."
    ),
    date: datetime.datetime = typer.Argument(
        ..., help="The date for which you want to fetch the data"
    ),
) -> None:
    await run("total-project-risk-score", project_id=project_id, date=date)


@explain_app.command(name="total-project-location-risk-score")
@run_async
async def total_project_location_risk_score(
    project_location_id: uuid.UUID = typer.Argument(
        ..., help="The project location ID for this metric."
    ),
    date: datetime.datetime = typer.Argument(
        ..., help="The date for which you want to fetch the data."
    ),
) -> None:
    await run(
        "total-project-location-risk-score",
        project_location_id=project_location_id,
        date=date,
    )


@explain_app.command(name="task-specific-risk-score")
@run_async
async def task_specific_risk_score(
    project_task_id: uuid.UUID = typer.Argument(...),
    date: datetime.datetime = typer.Argument(...),
) -> None:
    await run("task-specific-risk-score", project_task_id=project_task_id, date=date)


@explain_app.command(name="project-total-task-risk-score")
@run_async
async def project_total_task_risk_score(
    project_id: uuid.UUID = typer.Argument(...),
    date: datetime.datetime = typer.Argument(...),
) -> None:
    await run("project-total-task-risk-score", project_id=project_id, date=date)


@explain_app.command(name="project-location-total-task-risk-score")
@run_async
async def project_location_total_task_risk_score(
    project_location_id: uuid.UUID = typer.Argument(...),
    date: datetime.datetime = typer.Argument(...),
) -> None:
    await run(
        "project-location-total-task-risk-score",
        project_location_id=project_location_id,
        date=date,
    )


@explain_app.command(name="contractor-project-execution")
@run_async
async def contractor_project_execution(
    contractor_id: uuid.UUID = typer.Argument(...),
) -> None:
    await run("contractor-project-execution", contractor_id=contractor_id)


@explain_app.command(name="contractor-safety-history")
@run_async
async def contractor_safety_history(
    contractor_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "contractor-safety-history",
        contractor_id=contractor_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="project-location-site-conditions-multiplier")
@run_async
async def project_location_site_conditions_multiplier(
    project_location_id: uuid.UUID = typer.Argument(...),
    date: datetime.datetime = typer.Argument(...),
) -> None:
    await run(
        "project-location-site-conditions-multiplier",
        project_location_id=project_location_id,
        date=date,
    )


@explain_app.command(name="project-safety-climate-multiplier")
@run_async
async def project_safety_climate_multiplier(
    project_location_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "project-safety-climate-multiplier",
        project_location_id=project_location_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="global-contractor-project-history-baseline")
@run_async
async def global_contractor_project_history_baseline(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-contractor-project-history-baseline",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="global-contractor-project-history-baseline-stddev")
@run_async
async def global_contractor_project_history_baseline_stddev(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-contractor-project-history-baseline-stddev",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="global-contractor-safety-score")
@run_async
async def global_contractor_safety_score(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-contractor-safety-score",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="contractor-safety-rating")
@run_async
async def contractor_safety_rating(
    contractor_id: uuid.UUID = typer.Argument(...),
) -> None:
    """
    Note: As of 16-Mar-2022 this metric does nothing.

    It should only return 0 as of that date.
    """
    await run("contractor-safety-rating", contractor_id=contractor_id)


@explain_app.command(name="contractor-safety-score")
@run_async
async def contractor_safety_score(
    contractor_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "contractor-safety-score",
        contractor_id=contractor_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="task-specific-safety-climate-multiplier")
@run_async
async def task_specific_safety_climate_multiplier(
    library_task_id: uuid.UUID = typer.Argument(...),
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "task-specific-safety-climate-multiplier",
        library_task_id=library_task_id,
        calculated_before=calculated_before,
        tenant_id=tenant_id,
    )


@explain_app.command(name="task-specific-site-conditions-multiplier")
@run_async
async def task_specific_site_conditions_multiplier(
    project_task_id: uuid.UUID = typer.Argument(...),
    date: datetime.datetime = typer.Argument(...),
) -> None:
    await run(
        "task-specific-site-conditions-multiplier",
        project_task_id=project_task_id,
        date=date.date(),
    )


@explain_app.command(name="global-supervisor-engagement-factor")
@run_async
async def global_supervisor_engagement_factor(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-supervisor-engagement-factor",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="supervisor-engagement-factor")
@run_async
async def supervisor_engagement_factor(
    supervisor_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "supervisor-engagement-factor",
        supervisor_id=supervisor_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="global-supervisor-relative-precursor-risk")
@run_async
async def global_supervisor_relative_precursor_risk(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-supervisor-relative-precursor-risk",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="supervisor-relative-precursor-risk")
@run_async
async def supervisor_relative_precursor_risk(
    supervisor_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "supervisor-relative-precursor-risk",
        supervisor_id=supervisor_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="global-crew-factor")
@run_async
async def global_crew_factor(
    tenant_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "global-crew-factor",
        tenant_id=tenant_id,
        calculated_before=calculated_before,
    )


@explain_app.command(name="crew-risk")
@run_async
async def crew_risk(
    crew_id: uuid.UUID = typer.Argument(...),
    calculated_before: Optional[datetime.datetime] = typer.Option(
        None, help="Optional date for which you want to filter results."
    ),
) -> None:
    await run(
        "crew-risk",
        crew_id=crew_id,
        calculated_before=calculated_before,
    )
