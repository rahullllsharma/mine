import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.models.risk_model import StochasticTaskSpecificRiskScoreModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.stochastic_model.librarytask_relative_precursor_risk import (
    LibraryTaskRelativePrecursorRisk,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


class StochasticTaskSpecificRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        project_task_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._task_manager = task_manager
        self.project_task_id = project_task_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticTaskSpecificRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_task_id == o.project_task_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.project_task_id, self.date))

    async def run(self) -> None:
        # TODO: TEST
        t = await self._task_manager.get_task(self.project_task_id)
        if not t:
            raise ValueError(f"Task {self.project_task_id} not found")
        library_task = t[0]

        precursor = await LibraryTaskRelativePrecursorRisk.load(
            self._metrics_manager, library_task.id
        )
        await self.store(
            self._metrics_manager,
            self.project_task_id,
            self.date,
            precursor.value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = StochasticTaskSpecificRiskScoreModel(
            project_task_id=project_task_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> StochasticTaskSpecificRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticTaskSpecificRiskScoreModel,
            project_task_id=project_task_id,
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


TaskSpecificRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=StochasticTaskSpecificRiskScoreModel,
        metrics=[
            StochasticTaskSpecificRiskScore,
        ],
    ),
)
