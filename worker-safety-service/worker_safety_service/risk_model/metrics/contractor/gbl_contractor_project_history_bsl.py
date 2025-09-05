import datetime
import math
import uuid
from dataclasses import dataclass, field
from typing import Optional

from worker_safety_service.dal.contractors import ContractorHistory, ContractorsManager
from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import (
    GblContractorProjectHistoryBaselineModel,
    GblContractorProjectHistoryBaselineModelStdDev,
    RiskModelBase,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


@dataclass
class GlobalContractorProjectHistoryBaselineInputs:
    n_safety_observations: int | None = field(
        default=None, metadata={"full_name": "Number of Safety Observations"}
    )
    n_action_items: int | None = field(
        default=None, metadata={"full_name": "Number of Action Items"}
    )


def contractor_project_history_baseline(contractor_history: ContractorHistory) -> float:
    if not contractor_history.n_safety_observations:
        return 0.0

    return contractor_history.n_action_items / contractor_history.n_safety_observations


class GlobalContractorProjectHistoryBaseline:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        tenant_id: uuid.UUID,
    ):
        # TODO: Move over to a base class
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self._contractors_manager = contractors_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalContractorProjectHistoryBaseline):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id

    def __hash__(self) -> int:
        return hash(self.tenant_id)

    def calc(
        self, contractors: list[ContractorHistory]
    ) -> tuple[float, ContractorHistory]:
        n_safety_observations = 0
        n_action_items = 0

        for contractor in contractors:
            n_safety_observations += contractor.n_safety_observations
            n_action_items += contractor.n_action_items

        total: ContractorHistory = ContractorHistory(
            n_safety_observations, n_action_items
        )
        return contractor_project_history_baseline(total), total

    async def run(self) -> None:
        input_data: list[
            ContractorHistory
        ] = await self._contractors_manager.get_contractors_history(self.tenant_id)

        value, total = self.calc(input_data)

        await self.store(
            self._metrics_manager,
            value=value,
            tenant_id=self.tenant_id,
            inputs=dict(
                n_safety_observations=total.n_safety_observations,
                n_action_items=total.n_action_items,
            ),
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        value: float,
        inputs: Optional[dict[str, int]] = None,
    ) -> None:
        to_store = GblContractorProjectHistoryBaselineModel(
            tenant_id=tenant_id, value=value, inputs=inputs
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> GblContractorProjectHistoryBaselineModel:
        return await metrics_manager.load_unwrapped(
            GblContractorProjectHistoryBaselineModel,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[GlobalContractorProjectHistoryBaselineInputs | RiskModelBase] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            metric = await GlobalContractorProjectHistoryBaseline.load(
                metrics_manager,
                tenant_id=tenant_id,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Global Contractor Project History Baseline", None, [], [e]
                )
            ]

        if metric is not None and metric.inputs is not None:
            inputs.append(GlobalContractorProjectHistoryBaselineInputs(**metric.inputs))

        return [
            ExplainMethodOutput(
                "Global Contractor Project History Baseline", metric, inputs, errors
            )
        ]


@dataclass
class GlobalContractorProjectHistoryBaselineStdDevInput:
    gbl_contractor_project_history_baseline: float | None = field(
        default=None,
        metadata={"full_name": "Global Contractor Project History Baseline"},
    )
    acc: float | None = field(
        default=None,
        metadata={
            "full_name": "Accumulation of squared differences between the contractor histories and the baseline"
        },
    )
    n_contractors: int | None = field(
        default=None, metadata={"full_name": "Number of contractors"}
    )


# This should be on a different file probably
class GlobalContractorProjectHistoryBaselineStdDev:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        contractors_manager: ContractorsManager,
        tenant_id: uuid.UUID,
    ):
        # TODO: Move over to a base class
        self._metrics_manager: RiskModelMetricsManager = metrics_manager
        self._contractors_manager = contractors_manager
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, GlobalContractorProjectHistoryBaselineStdDev):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.tenant_id == o.tenant_id

    def __hash__(self) -> int:
        return hash(self.tenant_id)

    def calc(
        self,
        contractors: list[ContractorHistory],
        gbl_contractor_project_history_bsl: float,
    ) -> tuple[float, Optional[tuple[float, int]]]:
        n_contractors = 0
        acc = 0.0
        for contractor in contractors:
            contractor_project_history = contractor_project_history_baseline(contractor)

            # Accumulate the square of the difference
            acc += (
                contractor_project_history - gbl_contractor_project_history_bsl
            ) ** 2

            n_contractors += 1

        if not n_contractors:
            return 0.0, None

        return math.sqrt(acc / n_contractors), (acc, n_contractors)

    async def run(self) -> None:
        input_data: list[
            ContractorHistory
        ] = await self._contractors_manager.get_contractors_history(self.tenant_id)

        baseline_recording: GblContractorProjectHistoryBaselineModel = (
            await (
                GlobalContractorProjectHistoryBaseline.load(
                    self._metrics_manager, tenant_id=self.tenant_id
                )
            )
        )

        value, data = self.calc(input_data, baseline_recording.value)
        if data is None:
            inputs = None
        else:
            inputs = dict(acc=data[0], n_contractors=data[1])

        await self.store(
            self._metrics_manager, value=value, tenant_id=self.tenant_id, inputs=inputs
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        value: float,
        inputs: Optional[dict[str, float | int]] = None,
    ) -> None:
        to_store = GblContractorProjectHistoryBaselineModelStdDev(
            tenant_id=tenant_id, value=value, inputs=inputs
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> GblContractorProjectHistoryBaselineModelStdDev:
        return await metrics_manager.load_unwrapped(
            GblContractorProjectHistoryBaselineModelStdDev,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        tenant_id: uuid.UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        inputs: list[
            GlobalContractorProjectHistoryBaselineStdDevInput | RiskModelBase
        ] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        try:
            metric = await GlobalContractorProjectHistoryBaselineStdDev.load(
                metrics_manager, tenant_id, calculated_before=calculated_before
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Global Contractor Project History Baseline Standard Deviation",
                    None,
                    [],
                    [e],
                )
            ]
        try:
            metric_calculated_at = None
            if metric is not None:
                metric_calculated_at = metric.calculated_at
            baseline = await GlobalContractorProjectHistoryBaseline.load(
                metrics_manager,
                tenant_id=tenant_id,
                calculated_before=metric_calculated_at,
            )
            baseline_value = None
            if baseline is not None:
                baseline_value = baseline.value
        except MissingMetricError as e:
            errors.append(e)
            return [
                ExplainMethodOutput(
                    "Global Contractor Project History Baseline Standard Deviation",
                    metric,
                    inputs,
                    errors,
                )
            ]
        input_val = GlobalContractorProjectHistoryBaselineStdDevInput(
            gbl_contractor_project_history_baseline=baseline_value
        )
        if metric is not None and metric.inputs is not None:
            input_val.acc = metric.inputs.get("acc")
            input_val.n_contractors = metric.inputs.get("n_contractors")

        inputs.append(input_val)

        return [
            ExplainMethodOutput(
                "Global Contractor Project History Baseline Standard Deviation",
                metric,
                inputs,
                errors,
            )
        ]
