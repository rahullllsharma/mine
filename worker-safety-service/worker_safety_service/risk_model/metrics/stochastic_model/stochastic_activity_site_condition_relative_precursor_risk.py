import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models.risk_model import (
    StochasticActivitySiteConditionRelativePrecursorRiskScoreModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.stochastic_model.library_site_condition_relative_precursor_risk import (
    LibrarySiteConditionRelativePrecursorRisk,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput, assert_date_type
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class StochasticActivitySiteConditionRelativePrecursorRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        activity_manager: ActivityManager,
        site_conditions_evaluator: SiteConditionsEvaluator,
        activity_id: UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._activity_manager = activity_manager
        self._site_conditions_evaluator = site_conditions_evaluator
        self.activity_id = activity_id
        assert_date_type(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, StochasticActivitySiteConditionRelativePrecursorRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.activity_id == o.activity_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.activity_id, self.date))

    async def run(self) -> None:
        # TODO: TEST
        activity = await self._activity_manager.get_activity(
            self.activity_id, load_work_package=True
        )
        if not activity:
            raise ValueError(f"Activity {self.activity_id} not found")

        logger.info(
            "Evaluating location from StochasticActivitySiteConditionRelativePrecursorRiskScore",
            location_id=activity.location.id,
            date=self.date,
        )
        site_condition_results = (
            await self._site_conditions_evaluator.evaluate_location(
                activity.location, self.date
            )
        )

        # calculate score
        value = 0.0
        for library_site_condition, site_condition in site_condition_results:
            if site_condition.condition_applies:
                if activity.location.project is None:
                    continue
                try:
                    precursor = await LibrarySiteConditionRelativePrecursorRisk.load(
                        self._metrics_manager,
                        activity.location.project.tenant_id,
                        library_site_condition.id,
                    )
                    value += precursor.value
                except MissingMetricError:
                    logger.warning(
                        f"Missing LibrarySiteConditionRelativePrecursorRisk for tenant:{activity.location.project.tenant_id} site condition:{library_site_condition.id}"
                    )

        await self.store(
            self._metrics_manager,
            self.activity_id,
            self.date,
            value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        activity_id: UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = StochasticActivitySiteConditionRelativePrecursorRiskScoreModel(
            activity_id=activity_id, date=date, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        activity_id: UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> StochasticActivitySiteConditionRelativePrecursorRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            StochasticActivitySiteConditionRelativePrecursorRiskScoreModel,
            activity_id=activity_id,
            date=date,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        activity_manager: ActivityManager,
        activity_id: UUID,
        date: datetime.date,
    ) -> list[ExplainMethodOutput]:
        # TODO: Implement in the future
        raise NotImplementedError()


TaskSpecificRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=None,
        metrics=[
            StochasticActivitySiteConditionRelativePrecursorRiskScore,
        ],
    ),
)
