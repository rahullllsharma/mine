from datetime import datetime
from uuid import UUID

from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import CrewRiskModel
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class CrewRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        crew_manager: CrewManager,
        crew_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._crew_manager = crew_manager
        self.crew_id = crew_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, CrewRiskModel):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.crew_id == o.crew_id

    def __hash__(self) -> int:
        return hash(self.crew_id)

    async def run(self, date: datetime | None = None) -> None:
        # TODO: Check implementation after: WSAPP-1015
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        crew_id: UUID,
        value: float,
    ) -> None:
        to_store = CrewRiskModel(crew_id=crew_id, value=value)
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        crew_id: UUID,
        calculated_before: datetime | None = None,
    ) -> CrewRiskModel:
        return await metrics_manager.load_unwrapped(
            CrewRiskModel,
            crew_id=crew_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        crew_id: UUID,
        calculated_before: datetime | None = None,
    ) -> list[ExplainMethodOutput]:
        return []
