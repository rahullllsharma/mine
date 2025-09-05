import uuid
from typing import Awaitable, Callable, Type

import pytest

from tests.factories import SupervisorFactory
from tests.integration.risk_model.configs.helpers_tenant_factories import (
    h1_tenant_mock,
    natgrid_tenant_mock,
    random_tenant,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.global_supervisor_relative_precursor_risk import (
    GlobalSupervisorRelativePrecursorRisk,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_activity_site_condition_relative_precursor_risk import (
    StochasticActivitySiteConditionRelativePrecursorRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
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
from worker_safety_service.risk_model.riskmodelreactor import (
    ForAGivenSupervisor,
    ForAGivenTenant,
    IfMetricIsEnabledForTenant,
    MetricCalculation,
    OnTheDateWindow,
)
from worker_safety_service.risk_model.triggers.supervisor_data_changed import (
    SupervisorDataChanged,
)
from worker_safety_service.risk_model.triggers.supervisor_data_changed_for_tenant import (
    SupervisorDataChangedForTenant,
)


@pytest.mark.parametrize(
    ["tenant_id_supplier", "metric_type", "expected"],
    [
        (random_tenant, SupervisorEngagementFactor, True),
        (random_tenant, SupervisorRelativePrecursorRisk, False),
        (random_tenant, GlobalSupervisorEngagementFactor, True),
        (random_tenant, GlobalSupervisorRelativePrecursorRisk, False),
        (random_tenant, TaskSpecificRiskScore, True),
        (random_tenant, StochasticTaskSpecificRiskScore, False),
        (random_tenant, ProjectLocationSiteConditionsMultiplier, True),
        (
            random_tenant,
            StochasticActivitySiteConditionRelativePrecursorRiskScore,
            False,
        ),
        (natgrid_tenant_mock, SupervisorEngagementFactor, True),
        (natgrid_tenant_mock, SupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, GlobalSupervisorEngagementFactor, True),
        (natgrid_tenant_mock, GlobalSupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, TaskSpecificRiskScore, True),
        (natgrid_tenant_mock, StochasticTaskSpecificRiskScore, False),
        (natgrid_tenant_mock, ProjectLocationSiteConditionsMultiplier, True),
        (
            natgrid_tenant_mock,
            StochasticActivitySiteConditionRelativePrecursorRiskScore,
            False,
        ),
        (h1_tenant_mock, SupervisorEngagementFactor, False),
        (h1_tenant_mock, SupervisorRelativePrecursorRisk, True),
        (h1_tenant_mock, GlobalSupervisorEngagementFactor, False),
        (h1_tenant_mock, GlobalSupervisorRelativePrecursorRisk, True),
        (h1_tenant_mock, TaskSpecificRiskScore, False),
        (h1_tenant_mock, StochasticTaskSpecificRiskScore, True),
        (h1_tenant_mock, ProjectLocationSiteConditionsMultiplier, False),
        (
            h1_tenant_mock,
            StochasticActivitySiteConditionRelativePrecursorRiskScore,
            True,
        ),
    ],
)
@pytest.mark.asyncio
async def test_if_metric_is_enabled_for_tenant_main_test(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id_supplier: Callable[
        [AsyncSession, ConfigurationsManager], Awaitable[uuid.UUID]
    ],
    metric_type: Type[MetricCalculation],
    expected: bool,
) -> None:
    # Configure Tenant
    tenant_id = await tenant_id_supplier(db_session, configurations_manager)

    factory = ForAGivenTenant(IfMetricIsEnabledForTenant(metric_type))
    ret = await factory.unwrap(SupervisorDataChangedForTenant(tenant_id))

    if expected:
        # Expect a partial!!
        assert len(ret) == 1
        assert ret[0].func == metric_type  # type: ignore
        assert ret[0].keywords == {"tenant_id": tenant_id}  # type: ignore
    else:
        # Expect the metric to be aborted
        assert len(ret) == 0


@pytest.mark.parametrize(
    ["tenant_id_supplier", "metric_type", "expected"],
    [
        (random_tenant, SupervisorEngagementFactor, True),
        (random_tenant, SupervisorRelativePrecursorRisk, False),
        (random_tenant, GlobalSupervisorEngagementFactor, True),
        (random_tenant, GlobalSupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, SupervisorEngagementFactor, True),
        (natgrid_tenant_mock, SupervisorRelativePrecursorRisk, False),
        (natgrid_tenant_mock, GlobalSupervisorEngagementFactor, True),
        (natgrid_tenant_mock, GlobalSupervisorRelativePrecursorRisk, False),
        (h1_tenant_mock, SupervisorEngagementFactor, False),
        (h1_tenant_mock, SupervisorRelativePrecursorRisk, True),
        (h1_tenant_mock, GlobalSupervisorEngagementFactor, False),
        (h1_tenant_mock, GlobalSupervisorRelativePrecursorRisk, True),
    ],
)
@pytest.mark.asyncio
async def test_if_metric_is_enabled_for_tenant_nested_metrics(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id_supplier: Callable[
        [AsyncSession, ConfigurationsManager], Awaitable[uuid.UUID]
    ],
    metric_type: Type[MetricCalculation],
    expected: bool,
) -> None:
    # Configure Tenant
    tenant_id = await tenant_id_supplier(db_session, configurations_manager)
    supervisor = await SupervisorFactory.persist(db_session, tenant_id=tenant_id)

    # Very hypothetical factory
    factory = OnTheDateWindow(
        ForAGivenTenant(ForAGivenSupervisor(IfMetricIsEnabledForTenant(metric_type))), 5
    )
    ret = await factory.unwrap(SupervisorDataChanged(supervisor.id))

    if expected:
        # Expect a partial!!
        assert len(ret) == 5
        assert ret[0].func == metric_type  # type: ignore
        assert "tenant_id" in ret[0].keywords  # type: ignore
        assert "supervisor_id" in ret[0].keywords  # type: ignore
        assert "date" in ret[0].keywords  # type: ignore
    else:
        # Expect the metric to be aborted
        assert len(ret) == 0
