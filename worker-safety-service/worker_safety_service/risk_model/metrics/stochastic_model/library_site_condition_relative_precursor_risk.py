from datetime import datetime
from uuid import UUID

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models.risk_model import (
    LibrarySiteConditionRelativePrecursorRiskModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)


class LibrarySiteConditionRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        library_site_condition_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self.tenant_id = tenant_id
        self.library_site_condition_id = library_site_condition_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, LibrarySiteConditionRelativePrecursorRiskModel):
            return NotImplemented
        elif self is o:
            return True
        else:
            return (
                self.tenant_id == o.tenant_id
                and self.library_site_condition_id == o.library_site_condition_id
            )

    def __hash__(self) -> int:
        return hash((self.tenant_id, self.library_site_condition_id))

    async def run(self) -> None:
        # For the time being, these precursors will only be imported from the models team.
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        library_site_condition_id: UUID,
        value: float,
    ) -> None:
        to_store = LibrarySiteConditionRelativePrecursorRiskModel(
            tenant_id=tenant_id,
            library_site_condition_id=library_site_condition_id,
            value=value,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: UUID,
        library_site_condition_id: UUID,
        calculated_before: datetime | None = None,
    ) -> LibrarySiteConditionRelativePrecursorRiskModel:
        return await metrics_manager.load_unwrapped(
            LibrarySiteConditionRelativePrecursorRiskModel,
            tenant_id=tenant_id,
            library_site_condition_id=library_site_condition_id,
            calculated_before=calculated_before,
        )


TaskSpecificRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=None,
        metrics=[
            LibrarySiteConditionRelativePrecursorRisk,
        ],
    ),
)
