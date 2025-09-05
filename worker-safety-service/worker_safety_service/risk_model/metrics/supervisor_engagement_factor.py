import math
from calendar import monthrange
from datetime import datetime
from typing import Literal, NamedTuple, Optional, Union
from uuid import UUID

from worker_safety_service.dal.risk_model import (
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import Observation, SupervisorEngagementFactorModel
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    Config,
    SupervisorRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.utils import ExplainMethodOutput


class SupervisorEngagementFactorParams(NamedTuple):
    obs_number_threshold: int
    esd_number_threshold: int
    obs_number_value_below: int
    obs_number_value_above: int
    esd_number_value_below: int
    esd_number_value_above: int
    obs_timing_threshold_first: float
    obs_timing_threshold_second: float
    obs_timing_threshold_third: float
    obs_timing_value_first: float
    obs_timing_value_second: float
    obs_timing_value_third: float
    obs_timing_value_fourth: float
    esd_timing_threshold_first: float
    esd_timing_threshold_second: float
    esd_timing_threshold_third: float
    esd_timing_value_first: float
    esd_timing_value_second: float
    esd_timing_value_third: float
    esd_timing_value_fourth: float
    obs_month_fraction: float
    esd_month_fraction: float


class SupervisorEngagementFactor:
    def __init__(
        self,
        metrics_manager: RiskModelMetricsManager,
        supervisors_manager: SupervisorsManager,
        supervisor_id: UUID,
    ):
        self._metrics_manager = metrics_manager
        self._supervisors_manager = supervisors_manager
        # Will always be today's date, might be removed in the future
        self.supervisor_id = supervisor_id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SupervisorEngagementFactor):
            return NotImplemented
        elif self is o:
            return True
        else:
            return self.supervisor_id == o.supervisor_id

    def __hash__(self) -> int:
        return hash(self.supervisor_id)

    @staticmethod
    def calc_timing(
        engagement_type: Literal["obs", "esd"],
        engagements: Union[list[Observation], list[Observation]],
        quarter_engagements: int,
        params: dict[str, Union[int, float]],
    ) -> float:
        if len(engagements) == 0:
            return params[f"{engagement_type}_timing_value_fourth"]

        else:
            count: float = quarter_engagements / len(engagements)
            if count <= params[f"{engagement_type}_timing_threshold_first"]:
                return params[f"{engagement_type}_timing_value_first"]
            if count <= params[f"{engagement_type}_timing_threshold_second"]:
                return params[f"{engagement_type}_timing_value_second"]
            if count <= params[f"{engagement_type}_timing_threshold_third"]:
                return params[f"{engagement_type}_timing_value_third"]
            return params[f"{engagement_type}_timing_value_fourth"]

    def calc(
        self,
        params: dict[str, Union[int, float]],
        observations: list[Observation],
        esds: list[Observation],
    ) -> float:
        obs_number = []
        esd_number = []
        obs_timing = []
        esd_timing = []

        for month in range(1, 13):
            obs: list[Observation] = list(
                filter(lambda x: x.observation_datetime.month == month, observations)  # type: ignore
            )
            esd: list[Observation] = list(filter(lambda x: x.observation_datetime.month == month, esds))  # type: ignore

            if len(obs) < params["obs_number_threshold"]:
                obs_number.append(params["obs_number_value_below"])
            else:
                obs_number.append(params["obs_number_value_above"])
            if len(esd) < params["esd_number_threshold"]:
                esd_number.append(params["esd_number_value_below"])
            else:
                esd_number.append(params["esd_number_value_above"])

            quarter_obs = 0
            quarter_esd = 0
            for obs_instance in obs:
                if obs_instance.observation_datetime.day >= math.ceil(  # type: ignore
                    monthrange(
                        obs_instance.observation_datetime.year,  # type: ignore
                        obs_instance.observation_datetime.month,  # type: ignore
                    )[1]
                    * params["obs_month_fraction"]
                ):
                    quarter_obs += 1
            for esd_instance in esd:
                if esd_instance.observation_datetime.day >= math.ceil(  # type: ignore
                    monthrange(
                        esd_instance.observation_datetime.year,  # type: ignore
                        esd_instance.observation_datetime.month,  # type: ignore
                    )[1]
                    * params["esd_month_fraction"]
                ):
                    quarter_esd += 1

            obs_timing.append(self.calc_timing("obs", obs, quarter_obs, params))
            esd_timing.append(self.calc_timing("esd", esd, quarter_esd, params))

        return (
            (float(sum(obs_number)) / len(obs_number))
            + (float(sum(esd_number)) / len(esd_number))
            + (float(sum(obs_timing)) / len(obs_timing))
            + (float(sum(esd_timing)) / len(esd_timing))
        )

    async def run(self, date: Optional[datetime] = None) -> None:
        # Fetch params
        params = await self._metrics_manager.load_riskmodel_params(
            SupervisorEngagementFactorParams, "sef"
        )

        # Fetch input data
        observations, esds = await self._supervisors_manager.get_sef_input_data(
            self.supervisor_id, date
        )

        value: float = self.calc(
            params._asdict(),
            observations,
            esds,
        )

        await self.store(
            self._metrics_manager,
            self.supervisor_id,
            value,
        )

    @staticmethod
    async def store(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        value: float,
    ) -> None:
        to_store = SupervisorEngagementFactorModel(
            supervisor_id=supervisor_id, value=value
        )
        await metrics_manager.store(to_store)

    @staticmethod
    async def load(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        calculated_before: Optional[datetime] = None,
    ) -> SupervisorEngagementFactorModel:
        return await metrics_manager.load_unwrapped(
            SupervisorEngagementFactorModel,
            supervisor_id=supervisor_id,
            calculated_before=calculated_before,
        )

    @staticmethod
    async def explain(
        metrics_manager: RiskModelMetricsManager,
        supervisor_id: UUID,
        calculated_before: Optional[datetime] = None,
    ) -> list[ExplainMethodOutput]:
        try:
            metric = await SupervisorEngagementFactor.load(
                metrics_manager,
                supervisor_id=supervisor_id,
                calculated_before=calculated_before,
            )
        except MissingMetricError as e:
            return [ExplainMethodOutput("Supervisor Engagement Factor", None, [], [e])]

        params = await metrics_manager.load_riskmodel_params(
            SupervisorEngagementFactorParams, "sef"
        )

        return [
            ExplainMethodOutput("Supervisor Engagement Factor", metric, [], [], params)
        ]


SupervisorRiskScoreMetricConfig.register(
    "RULE_BASED_ENGINE",
    Config(
        model=SupervisorEngagementFactorModel,
        metrics=[SupervisorEngagementFactor],
    ),
)
