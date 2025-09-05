import pytest

from tests.integration.risk_model.configs.helpers_tenant_factories import random_tenant
from worker_safety_service.configs.base_configuration_model import load
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    LocationTotalTaskRiskScoreMetricConfig,
    RankedMetricConfig,
    TaskSpecificRiskScoreMetricConfig,
    TotalLocationRiskScoreMetricConfig,
    TotalProjectRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.configs.types import RankingThresholds

# TODO: Create other tests for tenant specific settings
# TODO: Test what happens if we supply a metric that does not have thresholds


@pytest.mark.parametrize(
    ["metric_config_type", "default_thresholds"],
    [
        (TaskSpecificRiskScoreMetricConfig, RankingThresholds(low=85.0, medium=210.0)),
        (
            LocationTotalTaskRiskScoreMetricConfig,
            RankingThresholds(low=85.0, medium=210.0),
        ),
        (
            TotalLocationRiskScoreMetricConfig,
            RankingThresholds(low=100.0, medium=250.0),
        ),
        (TotalProjectRiskScoreMetricConfig, RankingThresholds(low=100.0, medium=250.0)),
    ],
)
@pytest.mark.integration
@pytest.mark.asyncio
async def test_metric_thresholds_for_tenants_defaults(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    metric_config_type: type[RankedMetricConfig],
    default_thresholds: RankingThresholds,
) -> None:
    # TODO: Generify those tenant factories
    tenant_id = await random_tenant(db_session, None)  # type: ignore
    metric_cnf = await load(configurations_manager, metric_config_type, tenant_id)
    assert metric_cnf.thresholds == default_thresholds
