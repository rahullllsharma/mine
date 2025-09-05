import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service import get_logger
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models.risk_model import (
    StochasticTotalWorkPackageRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TotalLocationRiskScoreMetricConfig,
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_total_location_risk_score import (
    StochasticTotalLocationRiskScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date

logger = get_logger(__name__)


class StochasticTotalWorkPackageRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        configurations_manager: ConfigurationsManager,
        work_package_manager: WorkPackageManager,
        project_id: UUID,  # project location task
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._configurations_manager = configurations_manager
        self._work_package_manager = work_package_manager
        self.project_id = project_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticTotalWorkPackageRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_id == o.project_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.project_id, self.date))

    async def run(self) -> None:
        # TODO: TEST
        project = await self._work_package_manager.get_project(
            self.project_id, load_locations=True
        )
        if project is None:
            raise ValueError(f"WorkPackage not found: {self.project_id}")

        if len(project.locations) == 0:
            raise ValueError(
                f"No Locations scores found for WorkPackage: {self.project_id} on {self.date}"
            )

        location_scores = []
        for location in project.locations:
            try:
                metric = await StochasticTotalLocationRiskScore.load(
                    self._metrics_manager, location.id, self.date
                )
                location_scores.append(metric.value)
            except MissingMetricError:
                logger.warning(
                    "Skipping Location score for: {}",
                    work_package_id=self.project_id,
                    location_id=location.id,
                    exc_info=True,
                )

        if len(location_scores) == 0:
            # TODO: Check if there is a better exception for this.
            raise ValueError(
                f"No valid Location scores found for WorkPackage: {self.project_id} on {self.date}"
            )

        new_value = await calculate_weighted_average(
            self._configurations_manager,
            TotalLocationRiskScoreMetricConfig,
            project.tenant_id,
            location_scores,
        )

        await StochasticTotalWorkPackageRiskScore.store(
            self._metrics_manager,
            self.project_id,
            self.date,
            new_value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = StochasticTotalWorkPackageRiskScoreModel(
            project_id=project_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> StochasticTotalWorkPackageRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticTotalWorkPackageRiskScoreModel,
            project_id=project_id,
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


TotalProjectRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=StochasticTotalWorkPackageRiskScoreModel,
        metrics=[StochasticTotalWorkPackageRiskScore],
    ),
)
