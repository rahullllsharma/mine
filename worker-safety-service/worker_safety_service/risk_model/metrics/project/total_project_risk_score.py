import datetime
import uuid
from typing import Optional

from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import (
    CouldNotComputeError,
    MetricNotAvailableForDateError,
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


class TotalProjectRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        work_package_manager: WorkPackageManager,
        task_manager: TaskManager,
        locations_manager: LocationsManager,
        project_id: uuid.UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._work_package_manager = work_package_manager
        self._task_manager = task_manager
        self.project_id = project_id
        assert_date(date)
        self.date = date
        self._locations_manager = locations_manager

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TotalProjectRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_id == o.project_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.project_id, self.date))

    async def calc(
        self,
        tenant_id: uuid.UUID,
        project_location_risk_scores: list[float],
    ) -> float:
        return await calculate_weighted_average(
            self._configurations_manager,
            TotalProjectRiskScoreMetricConfig,
            tenant_id,
            project_location_risk_scores,
        )

    async def run(self) -> None:
        """
        Need to fetch all project location risk scores, then simply average them.
        1. Find all project locations associated with the current project
        2. Get the project_location_risk_score associated with each location and the date
        3. Pass the list into the calc function
        """
        project = await self._work_package_manager.get_project(self.project_id)
        if not project:
            raise ValueError(f"Project {self.project_id} not found")
        elif project.start_date > self.date or project.end_date < self.date:
            raise MetricNotAvailableForDateError(self, project)

        project_locations = await self._locations_manager.get_locations(
            project_ids=[self.project_id]
        )

        project_location_risk_scores = []
        for location in project_locations:
            # Will try to load the metric before checking for the tasks in the location because this is the most likely
            # path
            try:
                loaded_metric = await TotalProjectLocationRiskScore.load(
                    self._metrics_manager, location.id, self.date
                )
                project_location_risk_scores.append(loaded_metric.value)
            except CouldNotComputeError as ex:
                tasks = await self._task_manager.get_tasks(
                    location_ids=[location.id], date=self.date
                )
                if len(tasks) > 0:
                    raise ex

        if len(project_location_risk_scores) == 0:
            raise RuntimeError(f"Project has no active tasks: {self.project_id}")

        new_value = await self.calc(project.tenant_id, project_location_risk_scores)

        await self.store(
            self._metrics_manager,
            self.project_id,
            self.date,
            new_value,
            dict(project_location_ids=[str(x.id) for x in project_locations]),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_id: uuid.UUID,
        date: datetime.date,
        value: float,
        inputs: Optional[dict[str, list[str]]] = None,
    ) -> None:
        to_store = TotalProjectRiskScoreModel(
            project_id=project_id,
            date=date,
            value=value,
            inputs=inputs,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_id: uuid.UUID,
        date: datetime.date,
    ) -> TotalProjectRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            TotalProjectRiskScoreModel, project_id=project_id, date=date
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        work_package_manager: WorkPackageManager,
        contractors_manager: ContractorsManager,
        task_manager: TaskManager,
        project_id: uuid.UUID,
        date: datetime.date,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        inputs: list[TotalProjectLocationRiskScoreModel] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []

        try:
            metric = await TotalProjectRiskScore.load(metrics_manager, project_id, date)
        except MissingMetricError as e:
            return [ExplainMethodOutput("Total Project Risk Score", None, [], [e])]

        project_locations_ids: list[uuid.UUID] = []
        if metric is not None and metric.inputs is not None:
            project_locations_ids = list(
                map(lambda x: uuid.UUID(x), metric.inputs["project_location_ids"])
            )

        for _id in project_locations_ids:
            try:
                inputs.append(
                    await TotalProjectLocationRiskScore.load(
                        metrics_manager, _id, date, metric.calculated_at
                    )
                )

                if verbose:
                    explains.append(
                        await TotalProjectLocationRiskScore.explain(
                            metrics_manager,
                            work_package_manager,
                            contractors_manager,
                            task_manager,
                            _id,
                            date,
                            verbose=verbose,
                        )
                    )

            except MissingMetricError as e:
                errors.append(e)

        return [
            ExplainMethodOutput(
                "Total Project Risk Score",
                metric,
                inputs,
                errors,
                dependencies=explains,
            )
        ]


TotalProjectRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=TotalProjectRiskScoreModel,
        metrics=[TotalProjectRiskScore],
    ),
)
