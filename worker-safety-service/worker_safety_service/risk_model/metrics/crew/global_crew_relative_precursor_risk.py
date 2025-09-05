import asyncio
import datetime
import uuid
from typing import Optional, Tuple

from worker_safety_service.dal.crew import CrewManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import (
    AverageCrewRiskModel,
    CrewRiskModel,
    StdDevCrewRiskModel,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class GlobalCrewRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        crew_manager: CrewManager,
        tenant_id: uuid.UUID,
    ):
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self._crew_manager = crew_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalCrewRelativePrecursorRisk):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id

    def __hash__(self) -> int:
        return hash(self.tenant_id)

    async def run(self) -> None:
        # TODO: Check implementation after: WSAPP-1015
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        avg: float,
        stddev: float,
    ) -> None:
        avg_to_store = AverageCrewRiskModel(tenant_id=tenant_id, value=avg)

        stddev_to_store = StdDevCrewRiskModel(tenant_id=tenant_id, value=stddev)

        # Will execute in parallel, it is possible that only one of the calls is successful
        await asyncio.gather(
            metrics_manager.store(avg_to_store),
            metrics_manager.store(stddev_to_store),
        )

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> Tuple[AverageCrewRiskModel, StdDevCrewRiskModel]:
        loaded_average = await metrics_manager.load_unwrapped(
            AverageCrewRiskModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        loaded_stddev = await metrics_manager.load_unwrapped(
            StdDevCrewRiskModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        return loaded_average, loaded_stddev

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        crew_manager: CrewManager,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[CrewRiskModel] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            avg, stddev = await GlobalCrewRelativePrecursorRisk.load(
                metrics_manager, tenant_id, calculated_before=calculated_before
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput("Global Crew Factor Average", None, [], []),
                ExplainMethodOutput(
                    "Global Crew Factor Std Dev",
                    None,
                    inputs,
                    [e],
                ),
            ]
        if avg is not None and stddev is not None:
            crew = await crew_manager.get_crew(tenant_id=tenant_id)

            metrics = await metrics_manager.load_bulk(
                CrewRiskModel,
                crew_id=[x.id for x in crew],
                calculated_before=avg.calculated_at,
            )

            inputs = metrics

        return [
            ExplainMethodOutput("Global Crew Factor Average", avg, [], []),
            ExplainMethodOutput("Global Crew Factor Std Dev", stddev, inputs, errors),
        ]
