import uuid
from typing import Awaitable, Callable, Type

import pytest

from tests.integration.risk_model.configs.helpers_tenant_factories import (
    h1_tenant_mock,
    natgrid_tenant_mock,
    random_tenant,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import (
    AsyncSession,
    SupervisorEngagementFactorModel,
    SupervisorRelativePrecursorRiskModel,
)
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    SupervisorRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_rating import (
    ContractorSafetyRating,
)
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.global_supervisor_relative_precursor_risk import (
    GlobalSupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.supervisor_relative_precursor_risk import (
    SupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.riskmodelreactor import MetricCalculation


@pytest.mark.parametrize(
    ["tenant_id_supplier", "metric_type", "expected"],
    [
        (random_tenant, SupervisorEngagementFactor, True),
        (random_tenant, GlobalSupervisorEngagementFactor, True),
        (random_tenant, SupervisorRelativePrecursorRisk, False),
        (random_tenant, GlobalSupervisorRelativePrecursorRisk, False),
        (random_tenant, ContractorSafetyRating, True),  # Unrelated metric
        (random_tenant, TaskSpecificRiskScore, True),  # Unrelated metric
        (natgrid_tenant_mock, SupervisorEngagementFactor, True),
        (natgrid_tenant_mock, GlobalSupervisorEngagementFactor, True),
        (natgrid_tenant_mock, SupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, GlobalSupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, ContractorSafetyRating, True),  # Unrelated metric
        (natgrid_tenant_mock, TaskSpecificRiskScore, True),  # Unrelated metric
        (h1_tenant_mock, SupervisorEngagementFactor, False),
        (h1_tenant_mock, GlobalSupervisorEngagementFactor, False),
        (h1_tenant_mock, SupervisorRelativePrecursorRisk, True),
        (h1_tenant_mock, GlobalSupervisorRelativePrecursorRisk, True),
        (h1_tenant_mock, ContractorSafetyRating, True),  # Unrelated metric
        (h1_tenant_mock, TaskSpecificRiskScore, True),  # Unrelated metric
    ],
)
@pytest.mark.asyncio
async def test_is_metric_enabled_for_tenant(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id_supplier: Callable[
        [AsyncSession, ConfigurationsManager], Awaitable[uuid.UUID]
    ],
    metric_type: Type[MetricCalculation],
    expected: bool,
) -> None:
    metric_config = SupervisorRiskScoreMetricConfig
    # Configure Tenant
    tenant_id = await tenant_id_supplier(db_session, configurations_manager)
    is_disabled = await metric_config.is_metric_disabled_for_tenant(
        configurations_manager, metric_type, tenant_id
    )
    assert is_disabled != expected


@pytest.mark.asyncio
async def test_metric_model_for_tenants(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    metric_config = SupervisorRiskScoreMetricConfig
    random_tenant_id = await random_tenant(db_session, configurations_manager)
    ng_tenant_id = await natgrid_tenant_mock(db_session, configurations_manager)
    h1_tenant_id = await h1_tenant_mock(db_session, configurations_manager)

    tenant_ids = {random_tenant_id, ng_tenant_id, h1_tenant_id}
    metrics_for_tenants = await metric_config.metric_model_for_tenants(
        configurations_manager, tenant_ids
    )
    assert metrics_for_tenants == {
        random_tenant_id: SupervisorEngagementFactorModel,
        ng_tenant_id: SupervisorEngagementFactorModel,
        h1_tenant_id: SupervisorRelativePrecursorRiskModel,
    }
