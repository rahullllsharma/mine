from datetime import datetime
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import SupervisorRelativePrecursorRiskModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    SupervisorRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class SupervisorRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        supervisors_manager: SupervisorsManager,
        supervisor_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._supervisors_manager = supervisors_manager
        self.supervisor_id = supervisor_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SupervisorRelativePrecursorRiskModel):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.supervisor_id == o.supervisor_id

    def __hash__(self) -> int:
        return hash(self.supervisor_id)

    async def run(self) -> None:
        # For the time being, these precursors will only be imported from the models team.
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        value: float,
    ) -> None:
        to_store = SupervisorRelativePrecursorRiskModel(
            supervisor_id=supervisor_id, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        calculated_before: datetime | None = None,
    ) -> SupervisorRelativePrecursorRiskModel:
        return await metrics_manager.load_unwrapped(
            SupervisorRelativePrecursorRiskModel,
            supervisor_id=supervisor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        calculated_before: datetime | None = None,
    ) -> list[ExplainMethodOutput]:
        return []


SupervisorRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=SupervisorRelativePrecursorRiskModel,
        metrics=[
            SupervisorRelativePrecursorRisk,
        ],
    ),
)
