import asyncio
import datetime
import uuid
from statistics import fmean, pstdev
from typing import Optional, Tuple

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import (
    AverageContractorSafetyScoreModel,
    Contractor,
    ContractorSafetyScoreModel,
    RiskModelBase,
    StdDevContractorSafetyScoreModel,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class GlobalContractorSafetyScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        tenant_id: uuid.UUID,
    ):
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self._contractors_manager = contractors_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalContractorSafetyScore):
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
        # Grab all known contractors in the tenant
        contractors = await self._contractors_manager.get_contractors(
            tenant_id=self.tenant_id
        )

        # Retrieve their contractor safety score
        metrics = await self._metrics_manager.load_bulk(
            ContractorSafetyScoreModel, contractor_id=[x.id for x in contractors]
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
        avg_to_store = AverageContractorSafetyScoreModel(tenant_id=tenant_id, value=avg)
        stddev_to_store = StdDevContractorSafetyScoreModel(
            tenant_id=tenant_id, value=stddev
        )

        # Executes in parallel, it is possible that only one call is successful
        await asyncio.gather(
            metrics_manager.store(avg_to_store),
            metrics_manager.store(stddev_to_store),
        )

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> Tuple[AverageContractorSafetyScoreModel, StdDevContractorSafetyScoreModel]:
        loaded_average = await metrics_manager.load_unwrapped(
            AverageContractorSafetyScoreModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        loaded_stddev = await metrics_manager.load_unwrapped(
            StdDevContractorSafetyScoreModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )
        return loaded_average, loaded_stddev

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        contractors_manager: ContractorsManager,
        calculated_before: Optional[datetime.datetime] = None,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        inputs: list[ContractorSafetyScoreModel | RiskModelBase] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []
        try:
            avg, stddev = await GlobalContractorSafetyScore.load(
                metrics_manager,
                tenant_id=tenant_id,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Global Contractor Safety Score Average", None, [], []
                ),
                ExplainMethodOutput(
                    "Global Contractor Safety Score Std Dev",
                    None,
                    inputs,
                    [e],
                    dependencies=explains,
                ),
            ]

        contractors = await contractors_manager.get_contractors(tenant_id=tenant_id)
        if len(contractors) == 0:
            return [
                ExplainMethodOutput(
                    "Global Contractor Safety Score Average", None, [], []
                ),
                ExplainMethodOutput(
                    "Global Contractor Safety Score Std Dev",
                    None,
                    inputs,
                    [MissingDependencyError(Contractor)],
                    dependencies=explains,
                ),
            ]

        metrics = await metrics_manager.load_bulk(
            ContractorSafetyScoreModel,
            contractor_id=[x.id for x in contractors],
            calculated_before=avg.calculated_at,
        )

        for item in metrics:
            inputs.append(item)
            if verbose:
                explains.append(
                    await ContractorSafetyScore.explain(
                        metrics_manager,
                        contractor_id=item.contractor_id,
                        contractors_manager=contractors_manager,
                        calculated_before=avg.calculated_at,
                        verbose=verbose,
                    )
                )

        return [
            ExplainMethodOutput("Global Contractor Safety Score Average", avg, [], []),
            ExplainMethodOutput(
                "Global Contractor Safety Score Std Dev",
                stddev,
                inputs,
                errors,
                dependencies=explains,
            ),
        ]
