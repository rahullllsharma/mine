import datetime
import uuid
from typing import Optional

from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.risk_model import (
    MetricNotAvailableForDateError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.models.risk_model import TotalActivityRiskScoreModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TotalActivityRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.crew.crew_relative_precursor_risk import (
    CrewRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.division_relative_precursor_risk import (
    DivisionRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_site_condition_relative_precursor_risk import (
    StochasticActivitySiteConditionRelativePrecursorRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_total_task_riskscore import (
    StochasticActivityTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.supervisor_relative_precursor_risk import (
    SupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput, assert_date_type
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class TotalActivityRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        activity_manager: ActivityManager,
        activity_id: uuid.UUID,
        date: datetime.date,
    ):
        self._metrics_manager = metrics_manager
        self._activity_manager = activity_manager
        self.activity_id = activity_id
        assert_date_type(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TotalActivityRiskScore):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.activity_id == o.activity_id and self.date == o.date

    def __hash__(self) -> int:
        return hash((self.activity_id, self.date))

    async def run(self) -> None:
        activity = await self._activity_manager.get_activity(
            self.activity_id, load_work_package=True
        )
        if not activity:
            raise ValueError(f"Activity {self.activity_id} not found")
        elif activity.start_date > self.date or activity.end_date < self.date:
            raise MetricNotAvailableForDateError(self, activity)

        tasks_metric = await StochasticActivityTotalTaskRiskScore.load(
            self._metrics_manager,
            activity.id,
            self.date,
        )
        score = tasks_metric.value

        sc_model = await StochasticActivitySiteConditionRelativePrecursorRiskScore.load(
            self._metrics_manager,
            activity.id,
            self.date,
        )
        score += sc_model.value

        if False and activity.crew_id:  # TODO ignore for now
            try:
                crew_model = await CrewRelativePrecursorRisk.load(
                    self._metrics_manager, activity.crew_id
                )
                score += crew_model.value
            except MissingMetricError:
                logger.warning(
                    f"Missing CrewRelativePrecursorRisk for activity:{activity.id} crew:{activity.crew_id}"
                )

        supervisor_ids: list[uuid.UUID] = []  # TODO WSAPP-1204
        if supervisor_ids:
            for supervisor_id in supervisor_ids:
                try:
                    supervisor_model = await SupervisorRelativePrecursorRisk.load(
                        self._metrics_manager, supervisor_id
                    )
                    score += supervisor_model.value
                except MissingMetricError:
                    logger.warning(
                        f"Missing SupervisorRelativePrecursorRisk for activity:{activity.id} supervisor:{supervisor_id}"
                    )

        work_package = activity.location.project
        if work_package is None:
            raise ValueError(f"Work Package {work_package}has no project id")
        if work_package.division_id:
            try:
                division_model = await DivisionRelativePrecursorRisk.load(
                    self._metrics_manager,
                    work_package.tenant_id,
                    work_package.division_id,
                )
                score += division_model.value
            except MissingMetricError:
                logger.warning(
                    f"Missing DivisionRelativePrecursorRisk for activity:{activity.id} division:{work_package.division_id}"
                )

        await self.store(
            self._metrics_manager,
            activity.id,
            self.date,
            score,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        activity_id: uuid.UUID,
        date: datetime.date,
        value: float,
        inputs: Optional[dict[str, list[str]]] = None,
    ) -> None:
        to_store = TotalActivityRiskScoreModel(
            activity_id=activity_id,
            date=date,
            value=value,
            inputs=inputs,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        activity_id: uuid.UUID,
        date: datetime.date,
    ) -> TotalActivityRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            TotalActivityRiskScoreModel, activity_id=activity_id, date=date
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        activity_id: uuid.UUID,
        date: datetime.date,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        # TODO: Implement in the future
        raise NotImplementedError()


TotalActivityRiskScoreMetricConfig.register(
    "STOCHASTIC_MODEL",
    Config(
        model=TotalActivityRiskScoreModel,
        metrics=[TotalActivityRiskScore],
    ),
)
