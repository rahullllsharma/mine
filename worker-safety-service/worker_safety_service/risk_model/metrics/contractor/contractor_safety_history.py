import datetime
from dataclasses import asdict
from typing import Any, NamedTuple, Optional, Union
from uuid import UUID

from worker_safety_service.dal.contractors import ContractorsManager, CSHIncident
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import ContractorSafetyHistoryModel
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class ContractorSafetyHistoryParams(NamedTuple):
    near_miss: float
    first_aid: float
    recordable: float
    restricted: float
    lost_time: float
    p_sif: float
    sif: float


class ContractorSafetyHistory:
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
        if not isinstance(o, ContractorSafetyHistory):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.contractor_id == o.contractor_id

    def __hash__(self) -> int:
        return hash(self.contractor_id)

    def calc(
        self, input_data: CSHIncident, params: dict[str, Union[str, int, float, bool]]
    ) -> float:
        val = 0
        for k, v in params.items():
            input_attr = getattr(input_data, k)
            if v is not None and input_attr is not None:
                val += v * input_attr

        return val * (100 / input_data.sum_of_project_cost)

    async def run(self) -> None:
        # Fetch params
        params = await self._metrics_manager.load_riskmodel_params(
            ContractorSafetyHistoryParams, "contractor_safety_history"
        )

        # Fetch input data
        input_data = await self._contractors_manager.get_csh_incident_data(
            self.contractor_id
        )

        new_value = self.calc(input_data, params._asdict())

        await self.store(
            self._metrics_manager,
            self.contractor_id,
            new_value,
            inputs=asdict(input_data),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        value: float,
        inputs: Optional[dict[str, int | float]] = None,
    ) -> None:
        to_store = ContractorSafetyHistoryModel(
            contractor_id=contractor_id, value=value, inputs=inputs
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ContractorSafetyHistoryModel:
        return await metrics_manager.load_unwrapped(
            ContractorSafetyHistoryModel,
            contractor_id=contractor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[Any] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        params = await metrics_manager.load_riskmodel_params(
            ContractorSafetyHistoryParams, "contractor_safety_history"
        )

        try:
            metric = await ContractorSafetyHistory.load(
                metrics_manager, contractor_id, calculated_before=calculated_before
            )
        except MissingMetricError as e:
            errors.append(e)
            metric = None
            return [
                ExplainMethodOutput(
                    "Contractor Safety History", metric, inputs, errors, params
                )
            ]
        if metric is not None and metric.inputs is not None:
            inputs.append(CSHIncident(**metric.inputs))

        return [
            ExplainMethodOutput(
                "Contractor Safety History",
                metric,
                inputs,
                errors,
                params,
            )
        ]
