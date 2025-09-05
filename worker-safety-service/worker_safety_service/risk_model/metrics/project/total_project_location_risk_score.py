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
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import TotalProjectLocationRiskScoreModel
from worker_safety_service.models.base import Location
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    TotalLocationRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.project.project_safety_climate_multiplier import (
    ProjectSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.rankings import project_location_risk_level_bulk
from worker_safety_service.risk_model.utils import ExplainMethodOutput
from worker_safety_service.utils import assert_date


@dataclass
class TotalProjectLocationRiskScoreInput:
    project_safety_climate_multiplier: Optional[float] = field(
        default=None, metadata={"full_name": "Project Safety Climate Multiplier"}
    )
    project_location_site_conditions_multiplier: Optional[float] = field(
        default=None,
        metadata={"full_name": "Project Location Site Conditions Multiplier"},
    )
    project_location_total_task_risk_score: Optional[float] = field(
        default=None, metadata={"full_name": "Project Location Total Task Risk Score"}
    )


class TotalProjectLocationRiskScore:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        work_package_manager: WorkPackageManager,
        project_location_id: uuid.UUID,
        date: datetime.date,
    ) -> None:
        self._metrics_manager = metrics_manager
        self._work_package_manager = work_package_manager
        self._locations_manager = work_package_manager.locations_manager
        self.project_location_id = project_location_id
        assert_date(date)
        self.date = date

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, TotalProjectLocationRiskScore):
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
        project_safety_climate_multiplier: float = 0.0,
        project_site_conditions_multiplier: float = 0.0,
        total_task_risk_score: float = 0.0,
    ) -> float:
        return total_task_risk_score * (
            1 + project_site_conditions_multiplier + project_safety_climate_multiplier
        )

    async def run(self) -> None:
        # Fetch input data
        project_safety_climate_multiplier = await ProjectSafetyClimateMultiplier.load(
            self._metrics_manager, self.project_location_id
        )

        project_site_conditions_multiplier = (
            await (
                ProjectLocationSiteConditionsMultiplier.load(
                    self._metrics_manager, self.project_location_id, self.date
                )
            )
        )

        total_task_risk_score = await ProjectLocationTotalTaskRiskScore.load(
            self._metrics_manager, self.project_location_id, self.date
        )

        new_value = self.calc(
            project_safety_climate_multiplier.value,
            project_site_conditions_multiplier.value,
            total_task_risk_score.value,
        )
        await self.store(
            self._metrics_manager, self.project_location_id, self.date, new_value
        )
        # await self.store_risk()

    async def store_risk(self) -> None:
        location: Location | None = await self._locations_manager.get_location(
            id=self.project_location_id
        )
        if location:
            risk_data = project_location_risk_level_bulk(
                self._metrics_manager,
                [self.project_location_id],
                location.tenant_id,
                self.date,
            )
            risk_data_list = await risk_data
            id_to_risk_map = dict(zip([self.project_location_id], risk_data_list))
            await self._locations_manager.update_location_risk(id_to_risk_map)

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: uuid.UUID,
        date: datetime.date,
        value: float,
    ) -> None:
        to_store = TotalProjectLocationRiskScoreModel(
            project_location_id=project_location_id,
            date=date,
            value=value,
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        project_location_id: uuid.UUID,
        date: datetime.date,
        calculated_before: Optional[datetime.datetime] = None,
    ) -> TotalProjectLocationRiskScoreModel:
        return await metrics_manager.load_unwrapped(
            TotalProjectLocationRiskScoreModel,
            calculated_before=calculated_before,
            project_location_id=project_location_id,
            date=date,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        work_package_manager: WorkPackageManager,
        contractors_manager: ContractorsManager,
        task_manager: TaskManager,
        project_location_id: uuid.UUID,
        date: datetime.date,
        verbose: bool = True,
    ) -> list[ExplainMethodOutput]:
        errors: list[MissingMetricError | MissingDependencyError] = []
        explains: list[list[ExplainMethodOutput]] = []
        try:
            metric = await TotalProjectLocationRiskScore.load(
                metrics_manager, project_location_id, date
            )
        except MissingMetricError as e:
            return [
                ExplainMethodOutput("Total Project Location Risk Score", None, [], [e])
            ]

        async def fetch_dependency(
            metric_type: Type[ProjectSafetyClimateMultiplier]
            | Type[ProjectLocationSiteConditionsMultiplier]
            | Type[ProjectLocationTotalTaskRiskScore],
            metric_calculated_before: datetime.datetime,
            input_value: TotalProjectLocationRiskScoreInput,
            input_val_lookup: Literal[
                "project_safety_climate_multiplier",
                "project_location_site_conditions_multiplier",
                "project_location_total_task_risk_score",
            ],
            location_id: uuid.UUID,
            explain_kwargs: Optional[dict[str, Any]] = None,
            **kwargs: Any
        ) -> None:
            """
            Note: The 'explain_kwargs' option is needed because there
            are certain managers that are required for the `explain`
            methods but will break the `load` methods
            """
            if explain_kwargs is None:
                explain_kwargs = {}
            try:
                value = await metric_type.load(
                    metrics_manager,
                    project_location_id=location_id,
                    calculated_before=metric_calculated_before,
                    **kwargs
                )
                if value is not None:
                    setattr(input_value, input_val_lookup, value.value)
                if verbose:
                    explains.append(
                        await metric_type.explain(
                            metrics_manager,
                            project_location_id=location_id,
                            calculated_before=metric_calculated_before,
                            **explain_kwargs,
                            **kwargs
                        )
                    )
            except MissingMetricError as err:
                errors.append(err)

        input_val = TotalProjectLocationRiskScoreInput()
        await fetch_dependency(
            ProjectSafetyClimateMultiplier,
            metric.calculated_at,
            input_val,
            "project_safety_climate_multiplier",
            project_location_id,
            explain_kwargs=dict(
                work_package_manager=work_package_manager,
                contractors_manager=contractors_manager,
            ),
        )
        await fetch_dependency(
            ProjectLocationSiteConditionsMultiplier,
            metric.calculated_at,
            input_val,
            "project_location_site_conditions_multiplier",
            project_location_id,
            date=date,
        )
        await fetch_dependency(
            ProjectLocationTotalTaskRiskScore,
            metric.calculated_at,
            input_val,
            "project_location_total_task_risk_score",
            project_location_id,
            explain_kwargs=dict(task_manager=task_manager),
            date=date,
        )

        return [
            ExplainMethodOutput(
                "Total Project Location Risk Score",
                metric,
                [input_val],
                errors,
                dependencies=explains,
            )
        ]


TotalLocationRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=TotalProjectLocationRiskScoreModel,
        metrics=[TotalProjectLocationRiskScore],
    ),
)
