from typing import TYPE_CHECKING, NamedTuple, Optional, Type, TypedDict, Union
from uuid import UUID

from worker_safety_service.configs.base_configuration_model import load
from worker_safety_service.dal.configurations import ConfigurationsManager

if TYPE_CHECKING:
    from worker_safety_service.risk_model.configs.tenant_metric_configs import (
        RankedMetricConfig,
    )


class RiskModelParameterType(TypedDict):
    name: str
    value: Optional[Union[float, int]]


class RiskModelParameterDisplayType(RiskModelParameterType):
    display: str


class SiteConditionStorageType(NamedTuple):
    name: str
    multiplier: float


async def calculate_weighted_average(
    configurations_manager: ConfigurationsManager,
    risk_classification_type: Type["RankedMetricConfig"],
    tenant_id: UUID,
    scores: list[float],
) -> float:
    if len(scores) == 0:
        return 0

    ranked_metric_config = await load(
        configurations_manager, risk_classification_type, tenant_id
    )

    total_score = 0.0
    total_weight = 0.0
    for score in scores:
        ranking = ranked_metric_config.thresholds.ranking_for(score)
        weight = ranked_metric_config.weights.weight_for_ranking(ranking)

        total_score += score * weight
        total_weight += weight

    return round(total_score / total_weight, 4)
