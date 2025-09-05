import datetime
from typing import Any, NamedTuple, Optional
from uuid import UUID

from worker_safety_service.dal.incidents import IncidentData, IncidentsManager
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models import TaskSpecificSafetyClimateMultiplierModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class TaskSpecificClimateMultiplierParams(NamedTuple):
    near_miss: float
    first_aid: float
    recordable: float
    restricted: float
    lost_time: float
    p_sif: float
    sif: float


# WS-643
class TaskSpecificSafetyClimateMultiplier:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        incidents_manager: IncidentsManager,
        library_task_id: UUID,
        tenant_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._incidents_manager = incidents_manager
        self.library_task_id = library_task_id
        self.tenant_id = tenant_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TaskSpecificSafetyClimateMultiplier):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.library_task_id == o.library_task_id

    def __hash__(self) -> int:
        return hash(self.library_task_id)

    def calc(
        self, incidents_data: IncidentData, params: TaskSpecificClimateMultiplierParams
    ) -> float:
        val = 0
        for k, multiplier in params._asdict().items():
            count = getattr(incidents_data, k)
            val += count * multiplier
        return val

    async def run(self) -> None:
        # Fetch params
        params = await self._metrics_manager.load_riskmodel_params(
            TaskSpecificClimateMultiplierParams,
            "task_specific_safety_climate_multiplier",
        )

        incident_data = await self._incidents_manager.get_tasks_incident_data(
            self.library_task_id, self.tenant_id
        )

        new_value = self.calc(incident_data, params)
        inputs = incident_data.dict()
        params_as_dict = {k: v for k, v in params._asdict().items()}

        await self.store(
            self._metrics_manager,
            self.library_task_id,
            new_value,
            tenant_id=self.tenant_id,
            inputs=inputs,
            params=params_as_dict,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
        value: float,
        tenant_id: UUID,
        inputs: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        to_store = TaskSpecificSafetyClimateMultiplierModel(
            library_task_id=library_task_id,
            value=value,
            inputs=inputs,
            params=params,
            tenant_id=tenant_id,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
        tenant_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> TaskSpecificSafetyClimateMultiplierModel:
        return await metrics_manager.load_unwrapped(
            TaskSpecificSafetyClimateMultiplierModel,
            library_task_id=library_task_id,
            tenant_id=tenant_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        library_task_id: UUID,
        tenant_id: UUID,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        try:
            metric = await TaskSpecificSafetyClimateMultiplier.load(
                metrics_manager,
                library_task_id=library_task_id,
                tenant_id=tenant_id,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Task Specific Safety Climate Multiplier", None, [], [e]
                )
            ]

        params = await metrics_manager.load_riskmodel_params(
            TaskSpecificClimateMultiplierParams,
            "task_specific_safety_climate_multiplier",
        )

        return [
            ExplainMethodOutput(
                "Task Specific Safety Climate Multiplier", metric, [], [], params
            )
        ]


TaskSpecificRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=None,
        metrics=[TaskSpecificSafetyClimateMultiplier],
    ),
)
