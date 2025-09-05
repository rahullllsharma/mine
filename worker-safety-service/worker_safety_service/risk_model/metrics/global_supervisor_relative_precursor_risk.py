import asyncio
import datetime
import uuid
from statistics import fmean, pstdev

from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import (
    AverageSupervisorRelativePrecursorRiskModel,
    StdDevSupervisorRelativePrecursorRiskModel,
    SupervisorRelativePrecursorRiskModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    SupervisorRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class GlobalSupervisorRelativePrecursorRisk:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
    ):
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalSupervisorRelativePrecursorRisk):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id

    def __hash__(self) -> int:
        return hash(self.tenant_id)

    def calc(self, scores: list[float]) -> tuple[float, float]:
        if len(scores) > 0:
            mean = fmean(scores)
            stddev = pstdev(scores)
            return mean, stddev
        return 0.0, 0.0

    async def run(self) -> None:
        # TODO WSAPP-1015
        pass

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        avg: float,
        stddev: float,
    ) -> None:
        avg_to_store = AverageSupervisorRelativePrecursorRiskModel(
            tenant_id=tenant_id, value=avg
        )

        stddev_to_store = StdDevSupervisorRelativePrecursorRiskModel(
            tenant_id=tenant_id, value=stddev
        )

        # Will execute in parallel, it is possible that only one of the calls is successful
        await asyncio.gather(
            metrics_manager.store(avg_to_store),
            metrics_manager.store(stddev_to_store),
        )

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: datetime.datetime | None = None,
    ) -> tuple[
        AverageSupervisorRelativePrecursorRiskModel,
        StdDevSupervisorRelativePrecursorRiskModel,
    ]:
        loaded_average = await metrics_manager.load_unwrapped(
            AverageSupervisorRelativePrecursorRiskModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        loaded_stddev = await metrics_manager.load_unwrapped(
            StdDevSupervisorRelativePrecursorRiskModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        return loaded_average, loaded_stddev

    @classmethod
    async def explain(
        cls,
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: datetime.datetime | None = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[SupervisorRelativePrecursorRiskModel] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            avg, stddev = await cls.load(
                metrics_manager, tenant_id, calculated_before=calculated_before
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Global Supervisor Relative Risk Average", None, [], []
                ),
                ExplainMethodOutput(
                    "Global Supervisor Relative Risk Std Dev",
                    None,
                    inputs,
                    [e],
                ),
            ]

        if avg is not None and stddev is not None:
            # TODO WSAPP-1015
            supervisor_ids: list[uuid.UUID] = []

            metrics = await metrics_manager.load_bulk(
                SupervisorRelativePrecursorRiskModel,
                supervisor_id=supervisor_ids,
                calculated_before=avg.calculated_at,
            )
            inputs = metrics

        return [
            ExplainMethodOutput("Global Supervisor Relative Risk Average", avg, [], []),
            ExplainMethodOutput(
                "Global Supervisor Relative Risk Std Dev", stddev, inputs, errors
            ),
        ]


SupervisorRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=None,
        metrics=[
            GlobalSupervisorRelativePrecursorRisk,
        ],
    ),
)
