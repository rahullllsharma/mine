from datetime import datetime
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models.risk_model import DivisionRelativePrecursorRiskModel


class DivisionRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        division_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self.tenant_id = tenant_id
        self.division_id = division_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DivisionRelativePrecursorRisk):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id and self.division_id == o.division_id

    def __hash__(self) -> int:
        return hash((self.tenant_id, self.division_id))

    async def run(self) -> None:
        # For the time being, these precursors will only be imported from the models team.
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        division_id: UUID,
        value: float,
    ) -> None:
        to_store = DivisionRelativePrecursorRiskModel(
            tenant_id=tenant_id, division_id=division_id, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        division_id: UUID,
        calculated_before: datetime | None = None,
    ) -> DivisionRelativePrecursorRiskModel:
        return await metrics_manager.load_unwrapped(
            DivisionRelativePrecursorRiskModel,
            tenant_id=tenant_id,
            division_id=division_id,
            calculated_before=calculated_before,
        )
