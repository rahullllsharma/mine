import uuid
from unittest import TestCase
from unittest.mock import AsyncMock, Mock

import pytest

from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import Supervisor
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
)

# TODO: Replace mocks with the actual implementation


@pytest.mark.asyncio
async def test_global_contractor_safety_score_no_contractors(
    metrics_manager: RiskModelMetricsManager,
) -> None:
    test = TestCase()

    supervisor_manager: SupervisorsManager = Mock(spec=SupervisorsManager)
    supervisor_manager.get_supervisors = AsyncMock(return_value=[])  # type: ignore

    tenant_id = uuid.uuid4()
    metric = GlobalSupervisorEngagementFactor(
        metrics_manager, supervisor_manager, tenant_id
    )

    await metric.run()

    supervisor_manager.get_supervisors.assert_called_with(tenant_id=tenant_id)
    with test.assertRaises(Exception):
        await GlobalSupervisorEngagementFactor.load(metrics_manager, tenant_id)


@pytest.mark.asyncio
async def test_global_contractor_safety_score_with_contractors(
    metrics_manager: RiskModelMetricsManager,
    tenant_id: uuid.UUID,
) -> None:
    supervisors = []
    engagement_factors = [0.5, 0.3, 0.15]
    for i in range(0, 3):
        supervisor = Supervisor(
            id=uuid.uuid4(), external_key=f"name_{i}", tenant_id=tenant_id
        )
        supervisors.append(supervisor)
        await SupervisorEngagementFactor.store(
            metrics_manager, supervisor.id, engagement_factors[i]
        )

    supervisor_manager: SupervisorsManager = Mock(spec=SupervisorsManager)
    supervisor_manager.get_supervisors = AsyncMock(return_value=supervisors)  # type: ignore

    metric = GlobalSupervisorEngagementFactor(
        metrics_manager, supervisor_manager, tenant_id
    )

    await metric.run()

    supervisor_manager.get_supervisors.assert_called_with(tenant_id=tenant_id)
    metric_avg, metric_stddev = await GlobalSupervisorEngagementFactor.load(
        metrics_manager, tenant_id
    )
    assert metric_avg.tenant_id == tenant_id
    assert metric_stddev.tenant_id == tenant_id
    assert round(metric_avg.value, 4) == 0.3167
    assert round(metric_stddev.value, 4) == 0.1434
