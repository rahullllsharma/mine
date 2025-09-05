import asyncio
import datetime
import uuid
from statistics import fmean, pstdev
from typing import Optional, Tuple

from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import (
    AverageSupervisorEngagementFactorModel,
    StdDevSupervisorEngagementFactorModel,
    SupervisorEngagementFactorModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    SupervisorRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class GlobalSupervisorEngagementFactor:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        supervisors_manager: SupervisorsManager,
        tenant_id: uuid.UUID,
    ):
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self._supervisors_manager = supervisors_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalSupervisorEngagementFactor):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id

    def __hash__(self) -> int:
        return hash(self.tenant_id)

    def calc(self, scores: list[float]) -> Tuple[float, float]:
        if len(scores) > 0:
            mean = fmean(scores)
            stddev = pstdev(scores)
            return mean, stddev
        return 0.0, 0.0

    async def run(self) -> None:
        # Grab all known supervisors in the tenant
        supervisors = await self._supervisors_manager.get_supervisors(
            tenant_id=self.tenant_id
        )
        supervisors_ids: list[uuid.UUID] = list(map(lambda s: s.id, supervisors))

        # Retrieve their contractor safety score
        metrics = await self._metrics_manager.load_bulk(
            SupervisorEngagementFactorModel, supervisor_id=supervisors_ids
        )
        scores = list(map(lambda m: m.value, metrics))

        if len(scores) > 0:
            new_avg, new_stddev = self.calc(scores)
            await self.store(self._metrics_manager, self.tenant_id, new_avg, new_stddev)

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        avg: float,
        stddev: float,
    ) -> None:
        avg_to_store = AverageSupervisorEngagementFactorModel(
            tenant_id=tenant_id, value=avg
        )

        stddev_to_store = StdDevSupervisorEngagementFactorModel(
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
        calculated_before: Optional[datetime.datetime] = None,
    ) -> Tuple[
        AverageSupervisorEngagementFactorModel, StdDevSupervisorEngagementFactorModel
    ]:
        loaded_average = await metrics_manager.load_unwrapped(
            AverageSupervisorEngagementFactorModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        loaded_stddev = await metrics_manager.load_unwrapped(
            StdDevSupervisorEngagementFactorModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        return loaded_average, loaded_stddev

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        supervisors_manager: SupervisorsManager,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[SupervisorEngagementFactorModel] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            avg, stddev = await GlobalSupervisorEngagementFactor.load(
                metrics_manager, tenant_id, calculated_before=calculated_before
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Global Supervisor Engagement Factor Average", None, [], []
                ),
                ExplainMethodOutput(
                    "Global Supervisor Engagement Factor Std Dev",
                    None,
                    inputs,
                    [e],
                ),
            ]
        if avg is not None and stddev is not None:
            supervisors = await supervisors_manager.get_supervisors(tenant_id=tenant_id)

            metrics = await metrics_manager.load_bulk(
                SupervisorEngagementFactorModel,
                supervisor_id=[x.id for x in supervisors],
                calculated_before=avg.calculated_at,
            )

            inputs = metrics

        return [
            ExplainMethodOutput(
                "Global Supervisor Engagement Factor Average", avg, [], []
            ),
            ExplainMethodOutput(
                "Global Supervisor Engagement Factor Std Dev", stddev, inputs, errors
            ),
        ]


SupervisorRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=None,
        metrics=[GlobalSupervisorEngagementFactor],
    ),
)
