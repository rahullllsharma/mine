import datetime
import uuid
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    ProjectLocationTotalTaskRiskScoreModel,
    RiskModelBase,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    LocationTotalTaskRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)

# WS-383
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


class ProjectLocationTotalTaskRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        work_package_manager: WorkPackageManager,
        task_manager: TaskManager,
        project_location_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._work_package_manager = work_package_manager
        self._task_manager = task_manager
        self.project_location_id = project_location_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProjectLocationTotalTaskRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return (
                self.project_location_id == o.project_location_id
                and self.date == o.date
            )

    def __hash__(self) -> int:
        return hash((self.project_location_id, self.date))

    async def calc(
        self,
        tenant_id: UUID,
        task_specific_scores: list[float],
    ) -> float:
        return await calculate_weighted_average(
            self._configurations_manager,
            LocationTotalTaskRiskScoreMetricConfig,
            tenant_id,
            task_specific_scores,
        )

    async def run(self) -> None:
        location = await self._work_package_manager.get_location(
            self.project_location_id, load_project=True
        )
        assert location
        if not location.project:
            raise ValueError(f"location {self.project_location_id} has no project id")
        tenant_id = location.project.tenant_id

        project_tasks = await self._task_manager.get_tasks(
            location_ids=[self.project_location_id], date=self.date
        )

        task_specific_scores: list[float] = []
        task_ids: list[str] = []
        for _, task in project_tasks:
            metric = await TaskSpecificRiskScore.load(
                self._metrics_manager, task.id, self.date
            )
            task_ids.append(str(task.id))
            if metric is not None:
                task_specific_scores.append(metric.value)

        new_value = await self.calc(tenant_id, task_specific_scores)

        await self.store(
            self._metrics_manager,
            self.project_location_id,
            self.date,
            new_value,
            inputs=dict(task_ids=task_ids),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        value: float,
        inputs: Optional[dict[str, list[str]]] = None,
    ) -> None:
        to_store = ProjectLocationTotalTaskRiskScoreModel(
            project_location_id=project_location_id,
            date=date,
            value=value,
            inputs=inputs,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ProjectLocationTotalTaskRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            ProjectLocationTotalTaskRiskScoreModel,
            project_location_id=project_location_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        project_location_id: UUID,
        date: datetime.date,
        verbose: bool = True,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[RiskModelBase] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []
        try:
            metric = await ProjectLocationTotalTaskRiskScore.load(
                metrics_manager,
                project_location_id,
                date,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Project Location Total Task Risk Score", None, [], [e]
                )
            ]
        if metric.inputs is not None:
            task_ids = metric.inputs.get("task_ids", [])
            for _id in task_ids:
                try:
                    inputs.append(
                        await TaskSpecificRiskScore.load(
                            metrics_manager,
                            uuid.UUID(_id),
                            date,
                            calculated_before=metric.calculated_at,
                        )
                    )
                    if verbose:
                        explains.append(
                            await TaskSpecificRiskScore.explain(
                                metrics_manager,
                                uuid.UUID(_id),
                                date,
                                task_manager=task_manager,
                                verbose=verbose,
                            )
                        )
                except MissingMetricError as e:
                    errors.append(e)

        return [
            ExplainMethodOutput(
                "Project Location Total Task Risk Score",
                metric,
                inputs,
                errors,
                dependencies=explains,
            )
        ]


LocationTotalTaskRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=ProjectLocationTotalTaskRiskScoreModel,
        metrics=[ProjectLocationTotalTaskRiskScore],
    ),
)
