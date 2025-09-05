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
from worker_safety_service.models.risk_model import (
    StochasticActivityTotalTaskRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    ActivityTotalTaskRiskScoreMetricConfig,
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput, assert_date_type
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class StochasticActivityTotalTaskRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        activity_manager: ActivityManager,
        task_manager: TaskManager,
        activity_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._activity_manager = activity_manager
        self._task_manager = task_manager
        self.activity_id = activity_id
        assert_date_type(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticActivityTotalTaskRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.activity_id == o.activity_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.activity_id, self.date))

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
        activity = await self._activity_manager.get_activity(
            self.activity_id, load_work_package=True
        )
        if not activity:
            raise ValueError(f"Activity {self.activity_id} not found")

        task_ids: list[str] = []
        task_specific_scores: list[float] = []
        for _, task in await self._task_manager.get_tasks(
            activities_ids=[activity.id],
        ):
            try:
                metric = await StochasticTaskSpecificRiskScore.load(
                    self._metrics_manager, task.id, self.date
                )
            except MissingMetricError:
                logger.warning(
                    f"Missing StochasticTaskSpecificRiskScore for activity:{activity.id} task:{task.id}"
                )
                metric = None

            task_ids.append(str(task.id))
            if metric is not None:
                task_specific_scores.append(metric.value)

        if activity.location.project is None:
            raise ValueError(f"Activity {activity.location.id} has no project id")

        new_value = await self.calc(
            activity.location.project.tenant_id, task_specific_scores
        )

        await self.store(
            self._metrics_manager,
            self.activity_id,
            self.date,
            new_value,
            inputs=dict(task_ids=task_ids),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        activity_id: UUID,
        date: datetime.date,
        value: float,
        inputs: Optional[dict[str, list[str]]] = None,
    ) -> None:
        to_store = StochasticActivityTotalTaskRiskScoreModel(
            activity_id=activity_id,
            date=date,
            value=value,
            inputs=inputs,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        activity_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> StochasticActivityTotalTaskRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticActivityTotalTaskRiskScoreModel,
            activity_id=activity_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        activity_id: UUID,
        date: datetime.date,
    ) -> list[ExplainMethodOutput]:
        # TODO: Implement in the future
        raise NotImplementedError()


ActivityTotalTaskRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=StochasticActivityTotalTaskRiskScoreModel,
        metrics=[StochasticActivityTotalTaskRiskScore],
    ),
)
