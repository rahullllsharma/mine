import datetime
import uuid
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Type

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import ContractorSafetyScoreModel
from worker_safety_service.risk_model.metrics.contractor.contractor_project_execution import (
    ContractorProjectExecution,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_history import (
    ContractorSafetyHistory,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_rating import (
    ContractorSafetyRating,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


@dataclass
class ContractorSafetyScoreInput:
    contractor_safety_history: Optional[float] = field(
        default=None, metadata={"full_name": "Contractor Safety History"}
    )
    contractor_project_execution: Optional[float] = field(
        default=None, metadata={"full_name": "Contractor Project Execution"}
    )
    contractor_safety_rating: Optional[float] = field(
        default=None, metadata={"full_name": "Contractor Safety Rating"}
    )


class ContractorSafetyScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        contractor_id: uuid.UUID,
    ):
        self._metrics_manager = metrics_manager
        self._contractors_manager = contractors_manager
        self.contractor_id = contractor_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ContractorSafetyScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.contractor_id == o.contractor_id

    def __hash__(self) -> int:
        return hash(self.contractor_id)

    async def calc(self) -> float:
        contractor_safety_history = (
            await ContractorSafetyHistory.load(
                self._metrics_manager, contractor_id=self.contractor_id
            )
        ).value
        contractor_project_execution = (
            await ContractorProjectExecution.load(
                self._metrics_manager, contractor_id=self.contractor_id
            )
        ).value
        contractor_safety_rating = (
            await ContractorSafetyRating.load(
                self._metrics_manager, contractor_id=self.contractor_id
            )
        ).value

        return (
            contractor_project_execution
            + contractor_safety_rating
            + contractor_safety_history
        )

    async def run(self) -> None:
        new_value = await self.calc()
        await self.store(self._metrics_manager, self.contractor_id, new_value)

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: uuid.UUID,
        value: float,
    ) -> None:
        to_store = ContractorSafetyScoreModel(contractor_id=contractor_id, value=value)
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ContractorSafetyScoreModel:
        return await metrics_manager.load_unwrapped(
            ContractorSafetyScoreModel,
            contractor_id=contractor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        contractor_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        inputs: list[ContractorSafetyScoreInput] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []

        async def fetch_dependency(
            metric_type: Type[ContractorSafetyHistory]
            | Type[ContractorProjectExecution]
            | Type[ContractorSafetyRating],
            metric_calculated_before: datetime.datetime,
            input_value: ContractorSafetyScoreInput,
            input_val_lookup: Literal[
                "contractor_safety_history",
                "contractor_project_execution",
                "contractor_safety_rating",
            ],
            **kwargs: Any
        ) -> None:
            try:
                value = await metric_type.load(
                    metrics_manager,
                    contractor_id=contractor_id,
                    calculated_before=metric_calculated_before,
                )
                if value is not None:
                    setattr(input_value, input_val_lookup, value.value)
                if verbose:
                    explains.append(
                        await metric_type.explain(
                            metrics_manager,
                            contractor_id=contractor_id,
                            calculated_before=metric_calculated_before,
                            **kwargs
                        )
                    )
            except MissingMetricError as err:
                errors.append(err)

        try:
            metric = await ContractorSafetyScore.load(
                metrics_manager, contractor_id, calculated_before=calculated_before
            )

            input_val = ContractorSafetyScoreInput()
            await fetch_dependency(
                ContractorSafetyHistory,
                metric.calculated_at,
                input_val,
                input_val_lookup="contractor_safety_history",
            )
            await fetch_dependency(
                ContractorProjectExecution,
                metric.calculated_at,
                input_val,
                input_val_lookup="contractor_project_execution",
                contractors_manager=contractors_manager,
            )
            await fetch_dependency(
                ContractorSafetyRating,
                metric.calculated_at,
                input_val,
                input_val_lookup="contractor_safety_rating",
            )
            inputs.append(input_val)

        except MissingMetricError as e:
            errors.append(e)
            metric = None

        return [
            ExplainMethodOutput(
                "Contractor Safety Score", metric, inputs, errors, dependencies=explains
            )
        ]
