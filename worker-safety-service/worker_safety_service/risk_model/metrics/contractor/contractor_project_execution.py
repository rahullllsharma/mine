import datetime
from dataclasses import asdict, dataclass, field
from typing import NamedTuple, Optional, Type
from uuid import UUID

from worker_safety_service.dal.contractors import ContractorHistory, ContractorsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import (
    Contractor,
    ContractorProjectExecutionModel,
    GblContractorProjectHistoryBaselineModel,
    GblContractorProjectHistoryBaselineModelStdDev,
    RiskModelBase,
)
from worker_safety_service.risk_model.metrics.contractor.gbl_contractor_project_history_bsl import (
    contractor_project_history_baseline,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class ContractorProjectExecutionParams(NamedTuple):
    cph_weight_low: float
    cph_weight_high: float
    exp_factor_1: float
    exp_factor_2: float
    exp_factor_n: float


@dataclass
class ContractorProjectExecutionInput:
    n_safety_observations: int = field(
        metadata={"full_name": "Contractor History number of safety observations"}
    )
    n_action_items: int = field(
        metadata={"full_name": "Contractor History number of action items"}
    )
    contractor_experience_years: float = field(
        metadata={"full_name": "Contractor experience years"}
    )


class ContractorProjectExecution:
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
        if not isinstance(o, ContractorProjectExecution):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.contractor_id == o.contractor_id

    def __hash__(self) -> int:
        return hash(self.contractor_id)

    def calc(
        self,
        cpe_inputs: ContractorProjectExecutionInput,
        gbl_contractor_project_hist: float,
        gbl_contractor_project_hist_stddev: float,
        params: ContractorProjectExecutionParams,
    ) -> float:
        contractor_history = contractor_project_history_baseline(
            ContractorHistory(
                n_safety_observations=cpe_inputs.n_safety_observations,
                n_action_items=cpe_inputs.n_action_items,
            )
        )

        contractor_project_history_score = 0.0
        if contractor_history <= gbl_contractor_project_hist:
            contractor_project_history_score = params.cph_weight_low
        elif (
            contractor_history
            > gbl_contractor_project_hist + gbl_contractor_project_hist_stddev
        ):
            contractor_project_history_score = params.cph_weight_high
        else:
            # what about here??
            pass

        # Could be refactored into a more dynamic code
        if cpe_inputs.contractor_experience_years < 1.0:
            contractor_exp_factor = params.exp_factor_1
        elif cpe_inputs.contractor_experience_years < 2.0:
            contractor_exp_factor = params.exp_factor_2
        else:
            contractor_exp_factor = params.exp_factor_n

        return contractor_project_history_score + contractor_exp_factor

    async def run(self) -> None:
        # Fetch params
        params = await self._metrics_manager.load_riskmodel_params(
            ContractorProjectExecutionParams, "contractor_project_execution"
        )

        contractor = await self._contractors_manager.get_contractor(self.contractor_id)
        if not contractor:
            raise ValueError(f"Contractor {self.contractor_id} not found")
        tenant_id = contractor.tenant_id

        # Fetch dependent metrics
        gbl_contractor_project_hist = await self._metrics_manager.load_unwrapped(
            GblContractorProjectHistoryBaselineModel, tenant_id=tenant_id
        )
        gbl_contractor_project_hist_stddev = await self._metrics_manager.load_unwrapped(
            GblContractorProjectHistoryBaselineModelStdDev, tenant_id=tenant_id
        )

        # Fetch input data
        contractor_history = await self._contractors_manager.get_contractor_history(
            self.contractor_id
        )
        contractor_experience_years = (
            await self._contractors_manager.get_contractor_experience_years(
                self.contractor_id
            )
        )

        contractor_project_execution_inputs = ContractorProjectExecutionInput(
            n_safety_observations=contractor_history.n_safety_observations,
            n_action_items=contractor_history.n_action_items,
            contractor_experience_years=contractor_experience_years,
        )

        new_value = self.calc(
            contractor_project_execution_inputs,
            gbl_contractor_project_hist.value,
            gbl_contractor_project_hist_stddev.value,
            params,
        )

        await self.store(
            self._metrics_manager,
            self.contractor_id,
            new_value,
            inputs=asdict(contractor_project_execution_inputs),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        value: float,
        inputs: dict[str, float | int],
    ) -> None:
        to_store = ContractorProjectExecutionModel(
            contractor_id=contractor_id, value=value, inputs=inputs
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ContractorProjectExecutionModel:
        return await metrics_manager.load_unwrapped(
            ContractorProjectExecutionModel,
            contractor_id=contractor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        contractor_id: UUID,
        contractors_manager: ContractorsManager,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[ContractorProjectExecutionInput | RiskModelBase] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        params = await metrics_manager.load_riskmodel_params(
            ContractorProjectExecutionParams, "contractor_project_execution"
        )

        async def fetch_dependency(
            metric_type: Type[GblContractorProjectHistoryBaselineModel]
            | Type[GblContractorProjectHistoryBaselineModelStdDev],
            metric_calculated_before: datetime.datetime,
        ) -> None:
            try:
                value = await metrics_manager.load_unwrapped(
                    metric_type,
                    tenant_id=tenant_id,
                    calculated_before=metric_calculated_before,
                )
                inputs.append(value)
            except MissingMetricError as err:
                errors.append(err)

        contractor = await contractors_manager.get_contractor(contractor_id)
        if contractor is None:
            errors.append(
                MissingDependencyError(Contractor, contractor_id=contractor_id)
            )
            metric = None
            return [
                ExplainMethodOutput(
                    "Contractor Project Execution", metric, inputs, errors, params
                )
            ]

        try:
            metric = await ContractorProjectExecution.load(
                metrics_manager,
                contractor_id,
                calculated_before=calculated_before,
            )

            tenant_id = contractor.tenant_id
            await fetch_dependency(
                GblContractorProjectHistoryBaselineModel, metric.calculated_at
            )
            await fetch_dependency(
                GblContractorProjectHistoryBaselineModelStdDev, metric.calculated_at
            )

            if metric.inputs is not None:
                inputs.append(ContractorProjectExecutionInput(**metric.inputs))

        except MissingMetricError as e:
            errors.append(e)
            metric = None

        return [
            ExplainMethodOutput(
                "Contractor Project Execution", metric, inputs, errors, params
            )
        ]
