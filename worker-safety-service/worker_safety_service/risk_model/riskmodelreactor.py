import asyncio
import datetime
import functools
import threading
import uuid
from abc import ABC, abstractmethod
from inspect import signature
from queue import Empty, SimpleQueue
from typing import Any, Callable, Coroutine, Optional, Protocol, Type

import pendulum
from dependency_injector.wiring import Provide, inject
from structlog import wrap_logger

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import (
    MetricNotAvailableForDateError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import LibraryTask, Task
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
from worker_safety_service.risk_model.metrics.stochastic_model.library_site_condition_relative_precursor_risk import (
    LibrarySiteConditionRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.librarytask_relative_precursor_risk import (
    LibraryTaskRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_site_condition_relative_precursor_risk import (
    StochasticActivitySiteConditionRelativePrecursorRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_total_task_riskscore import (
    StochasticActivityTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_location_total_task_riskscore import (
    StochasticLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_total_location_risk_score import (
    StochasticTotalLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_total_work_package_risk_score import (
    StochasticTotalWorkPackageRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.total_activity_risk_score import (
    TotalActivityRiskScore,
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
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.triggers import (
    ActivityChanged,
    ActivityDeleted,
    ContractorChangedForProject,
    ContractorDataChanged,
    ContractorDataChangedForTenant,
    CrewDataChangedForTenant,
    IncidentChanged,
    LibraryTaskDataChanged,
    LocationChanged,
    ProjectChanged,
    ProjectLocationSiteConditionsChanged,
    SupervisorChangedForProjectLocation,
    SupervisorDataChanged,
    SupervisorDataChangedForTenant,
    SupervisorsChangedForProject,
    TaskChanged,
    TaskDeleted,
    UpdateTaskRisk,
)
from worker_safety_service.risk_model.utils.logging import (
    metric_dependency_formatter,
    metric_formatter,
    metric_holder_formatter,
)
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.urbint_logging import get_logger

logger = wrap_logger(
    get_logger(__name__),
    processors=[metric_formatter, metric_dependency_formatter, metric_holder_formatter],
)


class MetricCalculation(Protocol):
    async def run(self) -> None:
        ...


class RiskModelReactorInterface(Protocol):
    async def add(self, calculation: MetricCalculation) -> None:
        ...


###
MetricFactory = Callable[
    [RiskModelMetricsManager, ContractorsManager], MetricCalculation
]


class MetricFactoryBundle(ABC):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        self._nested: Optional[MetricFactoryBundle] = None
        if isinstance(metric, MetricFactoryBundle):
            self.metric = metric.metric  # type: ignore
            self._nested = metric
        else:
            self.metric = metric

    async def unwrap(
        self,
        parent_metric: Optional[MetricCalculation],
        parent_fields: dict[str, Any] = {},
    ) -> list[MetricFactory]:
        injectable_fields_list = await self.injectable_fields(
            self.InjectableContext(parent_metric, parent_fields)
        )

        ret = []
        for _injectable_fields in injectable_fields_list:
            if self._nested is None:
                factory_method = functools.partial(self.metric, **_injectable_fields)
                ret.append(factory_method)
            else:
                assert _injectable_fields.keys().isdisjoint(parent_fields.keys())
                _parent_fields = {**parent_fields, **_injectable_fields}
                for factory in await self._nested.unwrap(parent_metric, _parent_fields):
                    factory_method = functools.partial(factory, **_injectable_fields)
                    ret.append(factory_method)

        return ret  # type: ignore

    class InjectableContext:
        @inject
        def __init__(
            self,
            parent_metric: Optional[MetricCalculation],
            parent_fields: dict[str, Any] = {},
            contractor_manager: ContractorsManager = Provide["contractors_manager"],
            supervisor_manager: SupervisorsManager = Provide["supervisors_manager"],
            task_manager: TaskManager = Provide["task_manager"],
            work_package_manager: WorkPackageManager = Provide["work_package_manager"],
            activity_manager: ActivityManager = Provide["activity_manager"],
            configurations_manager: ConfigurationsManager = Provide[
                "configurations_manager"
            ],
            locations_manager: LocationsManager = Provide["locations_manager"],
            incidents_manager: IncidentsManager = Provide["incidents_manager"],
            tenant_manager: TenantManager = Provide["tenant_manager"],
        ) -> None:
            self.parent_metric = parent_metric
            self.parent_fields = parent_fields
            self.contractor_manager = contractor_manager
            self.supervisor_manager = supervisor_manager
            self.task_manager = task_manager
            self.work_package_manager = work_package_manager
            self.activity_manager = activity_manager
            self.configurations_manager = configurations_manager
            self.locations_manager = locations_manager
            self.incidents_manager = incidents_manager
            self.tenant_manager = tenant_manager

        async def fetch_attribute(self, name: str) -> Optional[Any]:
            if name == "tenant_id":
                return await self.fetch_tenant_id()
            elif name == "project_id":
                return await self.fetch_project_id()
            elif name == "project_location_id":
                return await self.fetch_project_location_id()
            elif name == "activity_id":
                return await self.fetch_activity_id()
            else:
                return self._fetch_attribute(name)

        def _fetch_attribute(self, name: str) -> Optional[Any]:
            ret = None
            if self.parent_metric is not None and hasattr(self.parent_metric, name):
                ret = getattr(self.parent_metric, name)
            if ret is None:
                ret = self.parent_fields.get(name)
            return ret

        async def fetch_tenant_id(self) -> Optional[uuid.UUID]:
            tenant_id: Optional[uuid.UUID] = self._fetch_attribute("tenant_id")
            if tenant_id is not None:
                return tenant_id

            try:
                project_id: Optional[uuid.UUID] = await self.fetch_attribute(
                    "project_id"
                )
                if project_id is not None:
                    _project = await self.work_package_manager.get_project(project_id)
                    if _project is not None:
                        return _project.tenant_id
            except RuntimeError:
                pass

            contractor_id = await self.fetch_attribute("contractor_id")
            if contractor_id is not None:
                contractor = await self.contractor_manager.get_contractor(contractor_id)
                if contractor:
                    return contractor.tenant_id

            sid: Optional[uuid.UUID] = await self.fetch_attribute("supervisor_id")
            if sid is not None:
                supervisor = await self.supervisor_manager.get_supervisor(sid)
                if supervisor is not None:
                    return supervisor.tenant_id

            incident_id: Optional[uuid.UUID] = await self.fetch_attribute("incident_id")
            if incident_id is not None:
                incident = await self.incidents_manager.get_incident_by_id(incident_id)
                if incident is not None:
                    return incident.tenant_id

            project_task_id = await self.fetch_attribute("project_task_id")
            if project_task_id is not None:
                task = await self.fetch_task(project_task_id)
                if task:
                    project_location = await self.work_package_manager.get_location(
                        task.location_id
                    )
                    if project_location is not None:
                        return project_location.tenant_id

            project_location_id = await self.fetch_attribute("project_location_id")
            if project_location_id is not None:
                project_location = await self.work_package_manager.get_location(
                    project_location_id
                )
                if project_location:
                    return project_location.tenant_id

            raise RuntimeError(
                "TODO: Could not find attributes to compute the tenant_id"
            )

        async def fetch_project_id(self) -> uuid.UUID:
            project_id: Optional[uuid.UUID] = self._fetch_attribute("project_id")
            if project_id is not None:
                return project_id

            project_location_id = await self.fetch_attribute("project_location_id")
            if project_location_id is not None:
                project_location = await self.work_package_manager.get_location(
                    project_location_id
                )
                if (
                    project_location is not None
                    and project_location.project_id is not None
                ):
                    return project_location.project_id

            raise RuntimeError(
                "TODO: Could not find attributes to compute the project_id"
            )

        async def fetch_project_location_id(self) -> uuid.UUID:
            project_location_id: Optional[uuid.UUID] = self._fetch_attribute(
                "project_location_id"
            )
            if project_location_id is not None:
                return project_location_id

            try:
                activity_id = await self.fetch_attribute("activity_id")
            except RuntimeError:
                # TODO: Remove once the activity link is mandatory
                activity_id = None

            # Fetch location from the activity
            if activity_id is not None:
                with_archived = False
                if isinstance(self.parent_metric, ActivityDeleted):
                    with_archived = True
                activity = await self.activity_manager.get_activity(
                    activity_id, with_archived=with_archived
                )
                if activity is not None:
                    return activity.location_id

            # TODO: Remove once the activity link is mandatory
            # Fetch location from the task
            project_task_id = await self.fetch_attribute("project_task_id")
            if project_task_id is not None:
                task = await self.fetch_task(project_task_id)
                if task:
                    project_location_id = task.location_id
                    return project_location_id

            raise RuntimeError(
                "TODO: Could not find attributes to compute the project_location_id"
            )

        async def fetch_activity_id(self) -> uuid.UUID:
            activity_id: Optional[uuid.UUID] = self._fetch_attribute("activity_id")
            if activity_id is not None:
                return activity_id

            # Fetch from the task
            project_task_id = await self.fetch_attribute("project_task_id")
            if project_task_id is not None:
                task = await self.fetch_task(project_task_id)
                if task:
                    activity_id = task.activity_id
                    # TODO: Remove once the activity link is mandatory
                    if activity_id is not None:
                        return activity_id

            raise RuntimeError(
                "TODO: Could not find attributes to compute the activity_id"
            )

        async def fetch_task(self, task_id: uuid.UUID) -> Task:
            """fetch archived tasks if processing archive trigger"""
            with_archived = False
            if self.parent_metric and isinstance(self.parent_metric, TaskDeleted):
                with_archived = True
            task = await self.task_manager.get_tasks(
                ids=[task_id], with_archived=with_archived
            )
            if task:
                return task[0][1]
            raise RuntimeError(f"TODO: Could not find task for {task_id}")

    @abstractmethod
    async def injectable_fields(
        self, context: InjectableContext
    ) -> list[dict[str, Any]]:
        ...


class ForAGivenField(MetricFactoryBundle):
    def __init__(
        self, metric: Type[MetricCalculation] | "MetricFactoryBundle", field_name: str
    ) -> None:
        super().__init__(metric)
        self.field_name = field_name

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        value = await context.fetch_attribute(self.field_name)
        # TODO: Create a better exception
        if value is None:
            raise RuntimeError(
                f"Could not derive field from context: {self.field_name}/{context.parent_metric}/{context.parent_fields}"
            )
        return [{self.field_name: value}]


# These will be holders
class ForAGivenTenant(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "tenant_id")


class ForEachContractor(MetricFactoryBundle):
    def __init__(
        self, metric: Type[MetricCalculation], tenant_id: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__(metric)
        self.tenant_id = tenant_id

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        tenant_id: uuid.UUID | None
        if self.tenant_id is not None:
            tenant_id = self.tenant_id
        else:
            tenant_id = await context.fetch_tenant_id()

        ret: list[dict[str, Any]] = []
        contractors = await context.contractor_manager.get_contractors(
            tenant_id=tenant_id
        )
        for c in contractors:
            ret.append({"contractor_id": c.id})

        return ret


class ForAGivenContractor(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "contractor_id")


class ForEachSupervisor(MetricFactoryBundle):
    def __init__(
        self, metric: Type[MetricCalculation], tenant_id: Optional[uuid.UUID] = None
    ) -> None:
        super().__init__(metric)
        self.tenant_id = tenant_id

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        tenant_id: uuid.UUID | None
        if self.tenant_id is not None:
            tenant_id = self.tenant_id
        else:
            tenant_id = await context.fetch_tenant_id()

        ret: list[dict[str, uuid.UUID]] = []
        supervisors = await context.supervisor_manager.get_supervisors(
            tenant_id=tenant_id
        )
        for s in supervisors:
            ret.append({"supervisor_id": s.id})

        return ret


class ForAGivenSupervisor(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "supervisor_id")


class ForAGivenLibraryTask(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "library_task_id")


class ForEachTaskOfAGivenType(MetricFactoryBundle):
    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        library_task_id = await context.fetch_attribute("library_task_id")
        _date = await context.fetch_attribute("date")

        tasks: list[tuple[LibraryTask, Task]] = await context.task_manager.get_tasks(
            library_task_id=library_task_id, date=_date
        )
        return [{"project_task_id": i[1].id} for i in tasks]


class ForEachTaskInTheSystem(MetricFactoryBundle):
    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        _date = await context.fetch_attribute("date")
        assert _date

        # TODO: Check if this query is very expensive, we only really need the id.
        tasks = await context.task_manager.get_tasks(date=_date)
        return [{"project_task_id": i[1].id} for i in tasks]


class ForAGivenActivity(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "activity_id")


class ForAGivenTask(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "project_task_id")


class ForAGivenDate(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "date")


class ForAGivenLocation(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "project_location_id")


class ForAGivenProject(ForAGivenField):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric, "project_id")


class OnTheDateWindow(MetricFactoryBundle):
    def __init__(
        self,
        metric: Type[MetricCalculation] | "MetricFactoryBundle",
        number_of_days: int = 15,
    ) -> None:
        super().__init__(metric)
        self.number_of_days = max(number_of_days - 1, 0)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        ret = []
        today = pendulum.today()
        interval = pendulum.interval(today, today.add(days=self.number_of_days))
        for dt in interval:
            _date = dt.date()  # type: ignore
            ret.append({"date": _date})

        return ret


class ForEachLocationInProject(MetricFactoryBundle):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        project_id = await context.fetch_attribute("project_id")
        assert project_id

        project_locations = await context.locations_manager.get_locations(
            project_ids=[project_id]
        )
        ret = []
        for location in project_locations:
            ret.append({"project_location_id": location.id})

        return ret


class ForEachActivityInLocation(MetricFactoryBundle):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        location_id = await context.fetch_attribute("project_location_id")
        assert location_id

        activities = (
            await context.activity_manager.get_activities_by_location([location_id])
        )[location_id]
        return list(map(lambda activity: {"activity_id": activity.id}, activities))


class ForEachProjectLocationOfContractor(MetricFactoryBundle):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        contractor_id = await context.fetch_attribute("contractor_id")
        assert contractor_id
        return [
            {"project_location_id": location.id}
            for location in await context.locations_manager.get_locations(
                contractor_ids=[contractor_id], with_archived=True
            )
        ]


class ForEachProjectLocationOfSupervisor(MetricFactoryBundle):
    def __init__(self, metric: Type[MetricCalculation] | "MetricFactoryBundle") -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        supervisor_id = await context.fetch_attribute("supervisor_id")
        assert supervisor_id
        return [
            {"project_location_id": location.id}
            for location in await context.locations_manager.get_locations(
                supervisor_ids=[supervisor_id], with_archived=True
            )
        ]


class ForEachProjectLocationInTheSystem(MetricFactoryBundle):
    def __init__(
        self,
        metric: Type[MetricCalculation] | "MetricFactoryBundle",
        date: datetime.date | None = None,
    ) -> None:
        super().__init__(metric)
        self._date = date

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        _date = (
            self._date
            if self._date is not None
            else (await context.fetch_attribute("date"))
        )
        assert _date

        # TODO: Check if this query is not very heavy, we only really need the ID.
        project_locations = await context.locations_manager.get_locations(date=_date)

        ret = []
        for location in project_locations:
            ret.append({"project_location_id": location.id})

        return ret


class ForEachIncidentLibraryTaskLink(MetricFactoryBundle):
    def __init__(
        self,
        metric: Type[MetricCalculation] | "MetricFactoryBundle",
    ) -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        incident_id = await context.fetch_attribute("incident_id")
        incident_ids = []
        if not incident_id or not isinstance(incident_id, uuid.UUID):
            logger.error(f"incident id not found or not correct: {incident_id}")
            return []
        else:
            incident_ids = [incident_id]
        incident_task_links = await context.incidents_manager.get_incident_task_links(
            incident_ids=incident_ids
        )
        return [{"library_task_id": itl.library_task_id} for itl in incident_task_links]


class ForEachTenantInTheSystem(MetricFactoryBundle):
    def __init__(
        self,
        metric: Type[MetricCalculation] | "MetricFactoryBundle",
    ) -> None:
        super().__init__(metric)

    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        tenants = await context.tenant_manager.get_tenants()
        return [{"tenant_id": t.id} for t in tenants]


class IfMetricIsEnabledForTenant(MetricFactoryBundle):
    async def injectable_fields(
        self, context: MetricFactoryBundle.InjectableContext
    ) -> list[dict[str, Any]]:
        tenant_id = await context.fetch_tenant_id()
        assert tenant_id

        from worker_safety_service.risk_model.configs import KNOWN_SCORE_TYPE

        for cfg_type in KNOWN_SCORE_TYPE:
            if await cfg_type.is_metric_disabled_for_tenant(
                context.configurations_manager, self.metric, tenant_id
            ):
                # Will return an empty list and make the factories return nothing.
                return []

        # Will return the identity: It will unwrap same as in the previous MetricFactoryBundle.
        return [{}]


# TODO: SERV-177 Currently done manually, needs to be automic in the future
# The metric classes need to define two methods, one to return the triggers they should respond to,
# the other for other metrics they depend on.
# Then we can compute this graph automatically and optimize it.
i_dependency_graph: dict[Type[MetricCalculation], list[MetricFactoryBundle]] = {
    ContractorDataChangedForTenant: [
        ForAGivenTenant(GlobalContractorProjectHistoryBaseline),
        ForAGivenTenant(GlobalContractorSafetyScore),
    ],
    SupervisorDataChangedForTenant: [
        ForAGivenTenant(IfMetricIsEnabledForTenant(GlobalSupervisorEngagementFactor)),
        ForAGivenTenant(
            IfMetricIsEnabledForTenant(GlobalSupervisorRelativePrecursorRisk)
        ),
    ],
    CrewDataChangedForTenant: [
        ForAGivenTenant(GlobalCrewRelativePrecursorRisk),
    ],
    ContractorDataChanged: [
        ForAGivenContractor(ContractorSafetyHistory),
        ForAGivenContractor(ContractorSafetyRating),
    ],
    SupervisorDataChanged: [
        ForAGivenSupervisor(IfMetricIsEnabledForTenant(SupervisorEngagementFactor)),
        ForAGivenSupervisor(
            IfMetricIsEnabledForTenant(SupervisorRelativePrecursorRisk)
        ),
    ],
    ActivityChanged: [
        OnTheDateWindow(
            ForAGivenActivity(
                IfMetricIsEnabledForTenant(
                    StochasticActivitySiteConditionRelativePrecursorRiskScore
                )
            )
        ),
        OnTheDateWindow(
            ForAGivenActivity(IfMetricIsEnabledForTenant(TotalActivityRiskScore))
        ),
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(StochasticLocationTotalTaskRiskScore)
            )
        ),
    ],
    ActivityDeleted: [
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(ProjectLocationTotalTaskRiskScore)
            )
        ),
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(StochasticTotalLocationRiskScore)
            )
        ),
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(StochasticLocationTotalTaskRiskScore)
            )
        ),
    ],
    IncidentChanged: [
        ForEachIncidentLibraryTaskLink(TaskSpecificSafetyClimateMultiplier)
    ],
    LibraryTaskDataChanged: [
        ForAGivenLibraryTask(
            ForEachTenantInTheSystem(
                IfMetricIsEnabledForTenant(TaskSpecificSafetyClimateMultiplier)
            )
        )
    ],
    UpdateTaskRisk: [
        ForAGivenTask(
            ForAGivenDate(
                IfMetricIsEnabledForTenant(TaskSpecificSiteConditionsMultiplier)
            )
        ),
        ForAGivenTask(
            ForAGivenDate(IfMetricIsEnabledForTenant(StochasticTaskSpecificRiskScore))
        ),
    ],
    TaskChanged: [
        OnTheDateWindow(ForAGivenTask(UpdateTaskRisk)),
    ],
    TaskDeleted: [
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(ProjectLocationTotalTaskRiskScore)
            )
        ),
        OnTheDateWindow(
            ForAGivenActivity(
                IfMetricIsEnabledForTenant(StochasticActivityTotalTaskRiskScore)
            )
        ),
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(StochasticLocationTotalTaskRiskScore)
            )
        ),
    ],
    ProjectChanged: [
        ForEachLocationInProject(ProjectLocationSiteConditionsChanged),
        ForEachLocationInProject(ProjectSafetyClimateMultiplier),
    ],
    LocationChanged: [
        ForAGivenLocation(ProjectLocationSiteConditionsChanged),
        ForAGivenLocation(ProjectSafetyClimateMultiplier),
    ],
    # TODO: Probably it's too much to call the ProjectLocationSiteConditionsChanged & ProjectSafetyClimateMultiplier
    #  for every location. Check if its feasible to inject an array of locations.
    ContractorChangedForProject: [
        ForEachLocationInProject(ProjectSafetyClimateMultiplier)
    ],
    SupervisorsChangedForProject: [
        ForEachLocationInProject(ProjectSafetyClimateMultiplier)
    ],
    SupervisorChangedForProjectLocation: [
        ForAGivenLocation(ProjectSafetyClimateMultiplier)
    ],
    ProjectLocationSiteConditionsChanged: [
        OnTheDateWindow(
            ForAGivenLocation(
                IfMetricIsEnabledForTenant(ProjectLocationSiteConditionsMultiplier)
            )
        ),
        OnTheDateWindow(
            ForEachActivityInLocation(
                IfMetricIsEnabledForTenant(
                    StochasticActivitySiteConditionRelativePrecursorRiskScore
                )
            )
        ),
    ],
    # END TRIGGERS
    GlobalContractorProjectHistoryBaseline: [
        ForAGivenTenant(GlobalContractorProjectHistoryBaselineStdDev)
    ],
    GlobalContractorProjectHistoryBaselineStdDev: [
        ForEachContractor(ContractorProjectExecution)
    ],
    ContractorSafetyHistory: [ForAGivenContractor(ContractorSafetyScore)],
    ContractorSafetyRating: [ForAGivenContractor(ContractorSafetyScore)],
    ContractorProjectExecution: [ForAGivenContractor(ContractorSafetyScore)],
    ContractorSafetyScore: [
        ForEachProjectLocationOfContractor(ProjectSafetyClimateMultiplier)
    ],
    SupervisorEngagementFactor: [
        ForEachProjectLocationOfSupervisor(ProjectSafetyClimateMultiplier)
    ],
    SupervisorRelativePrecursorRisk: [],
    TaskSpecificSafetyClimateMultiplier: [
        OnTheDateWindow(ForEachTaskOfAGivenType(ForAGivenTenant(TaskSpecificRiskScore)))
    ],
    TaskSpecificSiteConditionsMultiplier: [
        ForAGivenTask(ForAGivenTenant(ForAGivenDate(TaskSpecificRiskScore)))
    ],
    TaskSpecificRiskScore: [
        ForAGivenLocation(ForAGivenDate(ProjectLocationTotalTaskRiskScore))
    ],
    ProjectLocationTotalTaskRiskScore: [
        ForAGivenLocation(ForAGivenDate(TotalProjectLocationRiskScore))
    ],
    ProjectSafetyClimateMultiplier: [
        OnTheDateWindow(ForAGivenLocation(TotalProjectLocationRiskScore))
    ],
    ProjectLocationSiteConditionsMultiplier: [
        ForAGivenLocation(ForAGivenDate(TotalProjectLocationRiskScore))
    ],
    TotalProjectLocationRiskScore: [
        ForAGivenProject(ForAGivenDate(TotalProjectRiskScore))
    ],
    TotalProjectRiskScore: [],
    GlobalContractorSafetyScore: [],
    GlobalSupervisorEngagementFactor: [],
    GlobalSupervisorRelativePrecursorRisk: [],
    GlobalCrewRelativePrecursorRisk: [],
    CrewRelativePrecursorRisk: [],
    LibraryTaskRelativePrecursorRisk: [],
    StochasticTaskSpecificRiskScore: [
        ForAGivenActivity(ForAGivenDate(StochasticActivityTotalTaskRiskScore)),
        ForAGivenLocation(ForAGivenDate(StochasticLocationTotalTaskRiskScore)),
    ],
    StochasticActivityTotalTaskRiskScore: [
        ForAGivenActivity(ForAGivenDate(TotalActivityRiskScore)),
    ],
    StochasticLocationTotalTaskRiskScore: [],
    LibrarySiteConditionRelativePrecursorRisk: [],
    StochasticActivitySiteConditionRelativePrecursorRiskScore: [
        ForAGivenActivity(ForAGivenDate(TotalActivityRiskScore)),
    ],
    TotalActivityRiskScore: [
        ForAGivenLocation(ForAGivenDate(StochasticTotalLocationRiskScore))
    ],
    StochasticTotalLocationRiskScore: [
        ForAGivenProject(ForAGivenDate(StochasticTotalWorkPackageRiskScore)),
    ],
    StochasticTotalWorkPackageRiskScore: [],
}


class RiskModelReactor(ABC):
    @inject
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager = Provide[
            "risk_model_metrics_manager"
        ],
        configurations_manager: ConfigurationsManager = Provide[
            "configurations_manager"
        ],
        incidents_manager: IncidentsManager = Provide["incidents_manager"],
        contractors_manager: ContractorsManager = Provide["contractors_manager"],
        supervisors_manager: SupervisorsManager = Provide["supervisors_manager"],
        work_package_manager: WorkPackageManager = Provide["work_package_manager"],
        task_manager: TaskManager = Provide["task_manager"],
        site_conditions_manager: SiteConditionManager = Provide[
            "site_conditions_manager"
        ],
        site_conditions_evaluator: SiteConditionsEvaluator = Provide[
            "site_conditions_evaluator"
        ],
        activity_manager: ActivityManager = Provide["activity_manager"],
        locations_manager: LocationsManager = Provide["locations_manager"],
    ) -> None:
        self._injectables: dict[Type, Any] = {
            RiskModelMetricsManager: metrics_manager,
            ConfigurationsManager: configurations_manager,
            IncidentsManager: incidents_manager,
            ContractorsManager: contractors_manager,
            SupervisorsManager: supervisors_manager,
            WorkPackageManager: work_package_manager,
            TaskManager: task_manager,
            SiteConditionManager: site_conditions_manager,
            SiteConditionsEvaluator: site_conditions_evaluator,
            ActivityManager: activity_manager,
            LocationsManager: locations_manager,
        }

    @abstractmethod
    async def add(self, calculation: MetricCalculation) -> None:
        pass

    async def add_all(
        self,
        metric_holder: MetricFactoryBundle,
        parent_metric: Optional[MetricCalculation] = None,
    ) -> None:
        for metric_constructor in await metric_holder.unwrap(parent_metric):
            # TODO: use DI to create new instance
            kwargs: dict[str, Any] = {}
            for param in signature(metric_constructor).parameters.values():
                if param.annotation in self._injectables:
                    kwargs[param.name] = self._injectables[param.annotation]

            metric_instance = metric_constructor(**kwargs)  # type: ignore

            await self.add(metric_instance)

    @abstractmethod
    async def _fetch(self, timeout: int) -> MetricCalculation:
        pass

    @abstractmethod
    async def _is_empty(self) -> bool:
        pass


class RiskModelReactorLocalImpl(RiskModelReactor):
    @inject
    def __init__(
        self,
    ) -> None:
        super().__init__()

        self.work_queue: SimpleQueue[MetricCalculation] = SimpleQueue()
        self._task_cache: set[MetricCalculation] = set()

    async def add(self, calculation: MetricCalculation) -> None:
        # Assumes that the caller cannot yield execution
        if calculation not in self._task_cache:
            self._task_cache.add(calculation)
            self.work_queue.put_nowait(calculation)

    async def _fetch(self, timeout: int) -> MetricCalculation:
        # Again, assumes atomicity
        metric = self.work_queue.get(timeout=5)
        self._task_cache.remove(metric)
        return metric

    async def _is_empty(self) -> bool:
        return self.work_queue.empty()


class RiskModelReactorWorker(ABC):
    def __init__(self, reaktor: RiskModelReactor) -> None:
        self._reaktor = reaktor

    async def _consume(self) -> None:
        try:
            # This method is marked as protected so that other classes don't use it directly.
            curr_metric = await self._reaktor._fetch(timeout=5)
            log = logger.bind(metric=curr_metric)
        except Empty:
            logger.debug("Failed to fetch metric from the queue")
            return

        try:
            await curr_metric.run()
            log.info("Finished running")
        except MetricNotAvailableForDateError as error:
            log.warning("Metric not active for date", **error.log_kwargs())
            return
        except MissingMetricError as e:
            log.warning(
                "Missing dependency while running metric",
                dependency=e,
                exc_info=True,
            )
            return
        except Exception as e:
            log.exception(
                "Exception while running metric",
                exception_type=e.__class__.__name__,
            )
            return

        dependents = i_dependency_graph.get(type(curr_metric), [])
        for dependent_metric_holder in dependents:
            # Get all the instances in the node
            try:
                await self._reaktor.add_all(
                    dependent_metric_holder, parent_metric=curr_metric
                )
            except Exception as e:
                log.exception(
                    "Exception while unpacking dependents",
                    metric_holder=dependent_metric_holder,
                    exception_type=e.__class__.__name__,
                )

    async def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class RiskModelReactorWorkerBlocking(RiskModelReactorWorker):
    def __init__(self, reaktor: RiskModelReactor) -> None:
        super().__init__(reaktor)

    async def start(self) -> None:
        while not await self._reaktor._is_empty():
            await self._consume()


class RiskModelReactorWorkerDaemon(RiskModelReactorWorker):
    def __init__(self, reaktor: RiskModelReactor) -> None:
        super().__init__(reaktor)
        self._routine: Optional[Coroutine] = None
        self.stop_event = threading.Event()

    async def _work(self) -> None:
        while not self.stop_event.is_set():
            await self._consume()
            # yields the event loop so that other tasks may run as well
            await asyncio.sleep(0)

    async def start(self) -> None:
        if self._routine is not None:
            raise RuntimeError("Worker already started")

        self._routine = self._work()
        await self._routine

    def stop(self) -> None:
        if self._routine is None:
            return

        self.stop_event.set()
