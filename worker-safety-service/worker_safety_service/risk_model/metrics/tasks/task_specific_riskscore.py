import datetime
from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Type
from uuid import UUID

from worker_safety_service.dal.risk_model import (
    MissingDependencyError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.models import LibraryTask, TaskSpecificRiskScoreModel

# WS-380
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


@dataclass
class TaskSpecificRiskScoreInput:
    task_hesp_score: Optional[float] = field(
        default=None, metadata={"full_name": "Task HESP Score"}
    )
    task_specific_site_conditions_multiplier: Optional[float] = field(
        default=None, metadata={"full_name": "Task Specific Site Conditions Multiplier"}
    )
    task_specific_safety_climate_multiplier: Optional[float] = field(
        default=None, metadata={"full_name": "Task Specific Safety ClimateMultiplier"}
    )


class TaskSpecificRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        project_task_id: UUID,  # project location task
        date: datetime.date,
        tenant_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._task_manager = task_manager
        self.project_task_id = project_task_id
        self.tenant_id = tenant_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TaskSpecificRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_task_id == o.project_task_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.project_task_id, self.date))

    def calc(
        self,
        task_hesp_score: int,
        task_site_conditions_multiplier: float,
        task_safety_climate: float,
    ) -> float:
        # Task Specific HESP Score (1 + Task Specific Site Conditions Multiplier + Task Specific Safety Climate Multiplier)
        return (
            1.0 + task_site_conditions_multiplier + task_safety_climate
        ) * task_hesp_score

    async def run(self) -> None:
        t = await self._task_manager.get_task(self.project_task_id)
        if not t:
            raise ValueError(f"Task {self.project_task_id} not found")
        library_task = t[0]

        task_hesp_score = library_task.hesp
        task_site_conditions_multiplier = (
            await TaskSpecificSiteConditionsMultiplier.load(
                self._metrics_manager, self.project_task_id, self.date
            )
        )
        task_safety_climate = await TaskSpecificSafetyClimateMultiplier.load(
            self._metrics_manager, library_task.id, self.tenant_id
        )

        new_value = self.calc(
            task_hesp_score,
            task_site_conditions_multiplier.value,
            task_safety_climate.value,
        )

        await self.store(
            self._metrics_manager,
            self.project_task_id,
            self.date,
            new_value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = TaskSpecificRiskScoreModel(
            project_task_id=project_task_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> TaskSpecificRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            TaskSpecificRiskScoreModel,
            project_task_id=project_task_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        task_manager: TaskManager,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        inputs: list[TaskSpecificRiskScoreInput] = []
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []
        try:
            metric = await TaskSpecificRiskScore.load(
                metrics_manager, project_task_id, date
            )
        except MissingMetricError as e:
            return [ExplainMethodOutput("Task Specific Risk Score", None, [], [e])]

        async def fetch_dependency(
            metric_type: Type[TaskSpecificSiteConditionsMultiplier]
            | Type[TaskSpecificSafetyClimateMultiplier],
            metric_calculated_before: datetime.datetime,
            input_value: TaskSpecificRiskScoreInput,
            input_value_lookup: Literal[
                "task_specific_site_conditions_multiplier",
                "task_specific_safety_climate_multiplier",
            ],
            **kwargs: Any,
        ) -> None:
            try:
                value = await metric_type.load(
                    metrics_manager,
                    calculated_before=metric_calculated_before,
                    **kwargs,
                )
                if value is not None:
                    setattr(input_value, input_value_lookup, value.value)
                if verbose:
                    explains.append(
                        await metric_type.explain(
                            metrics_manager,
                            calculated_before=metric_calculated_before,
                            **kwargs,
                        )
                    )
            except MissingMetricError as err:
                errors.append(err)

        t = await task_manager.get_task_with_location(project_task_id)
        if not t:
            return [
                ExplainMethodOutput(
                    "Task Specific Risk Score",
                    None,
                    [],
                    [MissingDependencyError(LibraryTask, task_id=project_task_id)],
                )
            ]
        library_task, _, location = t
        if not library_task:
            return [
                ExplainMethodOutput(
                    "Task Specific Risk Score",
                    None,
                    [],
                    [MissingDependencyError(LibraryTask, task_id=project_task_id)],
                )
            ]
        input_val = TaskSpecificRiskScoreInput(task_hesp_score=library_task.hesp)

        library_task_id = library_task.id
        await fetch_dependency(
            TaskSpecificSiteConditionsMultiplier,
            metric.calculated_at,
            input_val,
            "task_specific_site_conditions_multiplier",
            project_task_id=project_task_id,
            date=date,
        )
        await fetch_dependency(
            TaskSpecificSafetyClimateMultiplier,
            metric.calculated_at,
            input_val,
            "task_specific_safety_climate_multiplier",
            library_task_id=library_task_id,
            tenant_id=location.tenant_id,
        )
        inputs.append(input_val)

        return [
            ExplainMethodOutput(
                "Task Specific Risk Score",
                metric,
                inputs,
                errors,
                dependencies=explains,
            )
        ]


TaskSpecificRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=TaskSpecificRiskScoreModel,
        metrics=[TaskSpecificRiskScore],
    ),
)
