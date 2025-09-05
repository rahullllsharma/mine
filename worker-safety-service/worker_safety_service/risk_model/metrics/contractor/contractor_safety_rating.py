import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import ContractorSafetyRatingModel
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class ContractorSafetyRating:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        contractor_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._contractors_manager = contractors_manager
        self.contractor_id = contractor_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ContractorSafetyRating):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.contractor_id == o.contractor_id

    def __hash__(self) -> int:
        return hash(self.contractor_id)

    def calc(self) -> float:
        return 0.0

    async def run(self) -> None:
        prev_value = await self._metrics_manager.load(
            ContractorSafetyRatingModel, contractor_id=self.contractor_id
        )
        # Will only calculate if the value was not previously saved
        # TODO: Change in the future
        if prev_value is None:
            new_value = self.calc()
            await self.store(self._metrics_manager, self.contractor_id, new_value)

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager, contractor_id: UUID, value: float
    ) -> None:
        to_store = ContractorSafetyRatingModel(contractor_id=contractor_id, value=value)
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ContractorSafetyRatingModel:
        return await metrics_manager.load_unwrapped(
            ContractorSafetyRatingModel,
            contractor_id=contractor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[ContractorSafetyRating] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            metric = await ContractorSafetyRating.load(
                metrics_manager, contractor_id, calculated_before=calculated_before
            )

        except MissingMetricError as e:
            errors.append(e)
            metric = None

        return [ExplainMethodOutput("Contractor Safety Rating", metric, inputs, errors)]
