import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service import get_logger
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models.risk_model import (
    StochasticTotalLocationRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TotalActivityRiskScoreMetricConfig,
    TotalLocationRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.stochastic_model.total_activity_risk_score import (
    TotalActivityRiskScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput, assert_date_type

logger = get_logger(__name__)


class StochasticTotalLocationRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        work_package_manager: WorkPackageManager,
        activity_manager: ActivityManager,
        project_location_id: UUID,  # project location task
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._work_package_manager = work_package_manager
        self._activity_manager = activity_manager
        self.project_location_id = project_location_id
        assert_date_type(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticTotalLocationRiskScore):
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

    async def run(self) -> None:
        # TODO: TEST
        project = await self._work_package_manager.get_work_package_by_location(
            self.project_location_id
        )
        if project is None:
            raise ValueError(
                f"WorkPackage for location not found: {self.project_location_id}"
            )

        activities = await self._activity_manager.get_activities(
            location_ids=[self.project_location_id], date=self.date
        )
        if len(activities) == 0:
            # TODO: Ask the model team what to do in this scenario.
            # TODO: Check if there is a better exception for this.
            raise ValueError(
                f"No Activity scores found for location: {self.project_location_id} on {self.date}"
            )

        activity_scores = []
        for activity in activities:
            # TODO: Complete once the metric is done
            try:
                metric = await TotalActivityRiskScore.load(
                    self._metrics_manager, activity.id, self.date
                )
                activity_scores.append(metric.value)
            except MissingMetricError:
                logger.warning(
                    "Skipping activity score for location: {}",
                    location_id=self.project_location_id,
                    exc_info=True,
                )

        if len(activity_scores) == 0:
            # TODO: Ask the model team what to do in this scenario.
            # TODO: Check if there is a better exception for this.
            raise ValueError(
                f"No valid activity scores found for location: {self.project_location_id} on {self.date}"
            )

        new_value = await calculate_weighted_average(
            self._configurations_manager,
            TotalActivityRiskScoreMetricConfig,
            project.tenant_id,
            activity_scores,
        )

        await StochasticTotalLocationRiskScore.store(
            self._metrics_manager,
            self.project_location_id,
            self.date,
            new_value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = StochasticTotalLocationRiskScoreModel(
            project_location_id=project_location_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> StochasticTotalLocationRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticTotalLocationRiskScoreModel,
            project_location_id=project_location_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        project_task_id: UUID,  # project location task
        date: datetime.date,
    ) -> list[ExplainMethodOutput]:
        # TODO: Implement in the future
        raise NotImplementedError()


TotalLocationRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=StochasticTotalLocationRiskScoreModel,
        metrics=[StochasticTotalLocationRiskScore],
    ),
)
