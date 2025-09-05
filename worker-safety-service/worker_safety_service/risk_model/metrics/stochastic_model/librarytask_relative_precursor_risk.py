from datetime import datetime
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models.risk_model import (
    LibraryTaskRelativePrecursorRiskModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)


class LibraryTaskRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self.library_task_id = library_task_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, LibraryTaskRelativePrecursorRisk):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.library_task_id == o.library_task_id

    def __hash__(self) -> int:
        return hash(self.library_task_id)

    async def run(self) -> None:
        # For the time being, these precursors will only be imported from the models team.
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
        value: float,
    ) -> None:
        to_store = LibraryTaskRelativePrecursorRiskModel(
            library_task_id=library_task_id, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
        calculated_before: datetime | None = None,
    ) -> LibraryTaskRelativePrecursorRiskModel:
        return await metrics_manager.load_unwrapped(
            LibraryTaskRelativePrecursorRiskModel,
            library_task_id=library_task_id,
            calculated_before=calculated_before,
        )


TaskSpecificRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=None,
        metrics=[LibraryTaskRelativePrecursorRisk],
    ),
)
