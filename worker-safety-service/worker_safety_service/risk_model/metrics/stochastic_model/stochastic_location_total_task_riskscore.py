import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models.risk_model import (
    StochasticLocationTotalTaskRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    LocationTotalTaskRiskScoreMetricConfig,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


class StochasticLocationTotalTaskRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        work_package_manager: WorkPackageManager,
        activity_manager: ActivityManager,
        task_manager: TaskManager,
        project_location_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._work_package_manager = work_package_manager
        self._activity_manager = activity_manager
        self._task_manager = task_manager
        self.project_location_id = project_location_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticLocationTotalTaskRiskScore):
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
            TaskSpecificRiskScoreMetricConfig,
            tenant_id,
            task_specific_scores,
        )

    async def run(self) -> None:
        # TODO: TEST
        location = await self._work_package_manager.get_location(
            self.project_location_id, load_project=True
        )
        if not location:
            raise ValueError(f"Location {self.project_location_id} not found")

        if not location.project:
            raise ValueError(f"Location {self.project_location_id} has no project id")

        tenant_id = location.project.tenant_id

        activity_ids = [
            activity.id
            for activity in await self._activity_manager.get_activities(
                location_ids=[self.project_location_id],
                tenant_id=tenant_id,
                date=self.date,
            )
        ]
        tasks = await self._task_manager.get_tasks(
            tenant_id=tenant_id,
            activities_ids=activity_ids,
        )
        task_specific_scores: list[float] = []
        task_ids: list[str] = []

        for _, task in tasks:
            try:
                metric = await StochasticTaskSpecificRiskScore.load(
                    self._metrics_manager, task.id, self.date
                )
            except MissingMetricError:
                metric = None

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
        to_store = StochasticLocationTotalTaskRiskScoreModel(
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
    ) -> StochasticLocationTotalTaskRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticLocationTotalTaskRiskScoreModel,
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
    ) -> list[ExplainMethodOutput]:
        # TODO: Implement in the future
        raise NotImplementedError()


LocationTotalTaskRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=StochasticLocationTotalTaskRiskScoreModel,
        metrics=[StochasticLocationTotalTaskRiskScore],
    ),
)
