import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service import get_logger
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.site_conditions import SiteConditionManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import ProjectLocationSiteConditionsMultiplierModel
from worker_safety_service.models.library import LibrarySiteCondition
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

logger = get_logger(__name__)


class ProjectLocationSiteConditionsMultiplier:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        work_package_manager: WorkPackageManager,
        site_conditions_manager: SiteConditionManager,
        site_conditions_evaluator: SiteConditionsEvaluator,
        project_location_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._work_package_manager = work_package_manager
        self._site_conditions_manager = site_conditions_manager
        self._site_conditions_evaluator = site_conditions_evaluator

        self.project_location_id = project_location_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, ProjectLocationSiteConditionsMultiplier):
            return NotImplemented
        elif self is o:
            return True
        else:
            return (
                self.project_location_id == o.project_location_id
                and self.date == o.date
            )

    def __hash__(self) -> int:
        return hash((self.project_location_id, self.date))

    @staticmethod
    def calc(
        site_conditions: list[tuple[LibrarySiteCondition, SiteConditionResult]],
    ) -> float:
        return sum(x.multiplier for _, x in site_conditions if x.condition_applies)

    async def run(self) -> None:
        location = await self._work_package_manager.get_location(
            self.project_location_id
        )
        if not location:
            raise ValueError(f"Location {self.project_location_id} not found")

        logger.info(
            "Evaluating location ProjectLocationSiteConditionsMultiplier",
            location_id=location.id,
            date=self.date,
        )
        site_condition_results = (
            await self._site_conditions_evaluator.evaluate_location(location, self.date)
        )
        value = self.calc(site_condition_results)

        await self.store(
            self._metrics_manager,
            location.id,
            self.date,
            value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = ProjectLocationSiteConditionsMultiplierModel(
            project_location_id=project_location_id,
            date=date,
            value=value,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> ProjectLocationSiteConditionsMultiplierModel:
        return await metrics_manager.load_unwrapped(
            ProjectLocationSiteConditionsMultiplierModel,
            project_location_id=project_location_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> list[ExplainMethodOutput]:
        try:
            metric = await ProjectLocationSiteConditionsMultiplier.load(
                metrics_manager,
                project_location_id=project_location_id,
                date=date,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput("Project Site Conditions Multiplier", None, [], [e])
            ]

        return [
            ExplainMethodOutput("Project Site Conditions Multiplier", metric, [], [])
        ]


TaskSpecificRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=None,
        metrics=[ProjectLocationSiteConditionsMultiplier],
    ),
)
