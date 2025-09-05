import uuid
from functools import cache

from tests.factories import TenantFactory
from worker_safety_service.configs.base_configuration_model import store_partial
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    ActivityTotalTaskRiskScoreMetricConfig,
    LocationTotalTaskRiskScoreMetricConfig,
    MetricConfig,
    ProjectTotalTaskRiskScoreMetricConfig,
    SupervisorRiskScoreMetricConfig,
    TaskSpecificRiskScoreMetricConfig,
    TotalActivityRiskScoreMetricConfig,
    TotalLocationRiskScoreMetricConfig,
    TotalProjectRiskScoreMetricConfig,
)


async def random_tenant(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> uuid.UUID:
    return uuid.uuid4()


@cache
async def natgrid_tenant_mock(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> uuid.UUID:
    tenant = await TenantFactory.persist(db_session)

    metrics_to_set: list[type[MetricConfig]] = [
        TaskSpecificRiskScoreMetricConfig,
        SupervisorRiskScoreMetricConfig,
    ]
    for conf_type in metrics_to_set:
        await store_partial(
            configurations_manager,
            conf_type,
            tenant.id,
            type="RULE_BASED_ENGINE",
        )

    return tenant.id


@cache
async def h1_tenant_mock(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> uuid.UUID:
    tenant = await TenantFactory.persist(db_session)

    metrics_to_set: list[type[MetricConfig]] = [
        TaskSpecificRiskScoreMetricConfig,
        ProjectTotalTaskRiskScoreMetricConfig,
        TotalLocationRiskScoreMetricConfig,
        TotalProjectRiskScoreMetricConfig,
        ActivityTotalTaskRiskScoreMetricConfig,
        TotalActivityRiskScoreMetricConfig,
        LocationTotalTaskRiskScoreMetricConfig,
        TotalLocationRiskScoreMetricConfig,
        SupervisorRiskScoreMetricConfig,
    ]
    for metric in metrics_to_set:
        await store_partial(
            configurations_manager, metric, tenant.id, type="STOCHASTIC_MODEL"
        )

    return tenant.id
