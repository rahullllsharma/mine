import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import TaskSpecificSiteConditionsMultiplierModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.site_conditions import (
    SiteConditionResult,
    SiteConditionsEvaluator,
)
from worker_safety_service.utils import assert_date


class TaskSpecificSiteConditionsMultiplier:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        task_manager: TaskManager,
        work_package_manager: WorkPackageManager,
        site_conditions_evaluator: SiteConditionsEvaluator,
        project_task_id: UUID,  # project location task
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._task_manager = task_manager
        self._work_package_manager: WorkPackageManager = work_package_manager
        self._site_conditions_evaluator = site_conditions_evaluator

        self.project_task_id = project_task_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TaskSpecificSiteConditionsMultiplier):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.project_task_id == o.project_task_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.project_task_id, self.date))

    def calc(self, site_conditions: list[SiteConditionResult]) -> float:
        # For each site condition for a given day. Location & Date
        # https://github.com/urbint/worker-safety-poc/blob/main/worker_safety/risk/services/site_conditions.py

        # 3. Sum up all the multipliers that are relevant for the task and were triggered to get the task specific site conditions multiplier score
        tmp = 0.0
        applicable_site_conditions = []
        for site_condition in site_conditions:
            if site_condition.condition_applies:
                tmp += site_condition.multiplier
                applicable_site_conditions.append(site_condition)

        return tmp

    async def run(self) -> None:
        # 2. Determine whether the task site condition is applicable for the task
        site_conditions_results = (
            await self._site_conditions_evaluator.evaluate_project_location_task(
                task_id=self.project_task_id,
                date=self.date,
            )
        )

        value = self.calc(site_conditions_results)

        await self.store(
            self._metrics_manager,
            self.project_task_id,
            self.date,
            value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = TaskSpecificSiteConditionsMultiplierModel(
            project_task_id=project_task_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> TaskSpecificSiteConditionsMultiplierModel:
        return await metrics_manager.load_unwrapped(
            TaskSpecificSiteConditionsMultiplierModel,
            project_task_id=project_task_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        project_task_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        try:
            metric = await TaskSpecificSiteConditionsMultiplier.load(
                metrics_manager,
                project_task_id=project_task_id,
                date=date,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput(
                    "Task Specific Site Conditions Multiplier", None, [], [e]
                )
            ]

        return [
            ExplainMethodOutput(
                "Task Specific Site Conditions Multiplier", metric, [], []
            )
        ]


TaskSpecificRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=None,
        metrics=[TaskSpecificSiteConditionsMultiplier],
    ),
)
