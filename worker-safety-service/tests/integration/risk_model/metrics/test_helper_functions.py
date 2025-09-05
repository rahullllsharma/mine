from typing import TypeVar

import pytest

from tests.factories import TenantFactory
from worker_safety_service.configs.base_configuration_model import store
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    ProjectTotalTaskRiskScoreMetricConfig,
    RankedMetricConfig,
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.configs.types import (
    RankingThresholds,
    RankingWeight,
)
from worker_safety_service.risk_model.metrics import calculate_weighted_average

U = TypeVar("U")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "risk_classification, expected_result",
    [
        (
            TotalProjectRiskScoreMetricConfig(
                type="RULE_BASED_ENGINE",
                thresholds=RankingThresholds(low=100, medium=200),
                weights=RankingWeight(low=1.0, medium=1.5, high=2.0),
            ),
            170.0,
        ),
        (
            ProjectTotalTaskRiskScoreMetricConfig(
                type="STOCHASTIC_MODEL",
                thresholds=RankingThresholds(low=50, medium=150),
                weights=RankingWeight(low=2.0, medium=4.0, high=6.0),
            ),
            171.7857,
        ),
        (
            ProjectTotalTaskRiskScoreMetricConfig(
                type="RULE_BASED_ENGINE",
                thresholds=RankingThresholds(low=100, medium=250),
                weights=RankingWeight(low=0.5, medium=1.5, high=3),
            ),
            195.8824,
        ),
    ],
)
async def test_calculate_weighted_average(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    risk_classification: RankedMetricConfig,
    expected_result: float,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    scores = [30.0, 75.0, 225.0, 300.0, 150.0, 100.0]

    await store(configurations_manager, risk_classification, tenant.id)
    result = await calculate_weighted_average(
        configurations_manager, type(risk_classification), tenant.id, scores
    )
    assert result == expected_result
