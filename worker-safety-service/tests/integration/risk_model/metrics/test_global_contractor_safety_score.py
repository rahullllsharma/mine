import uuid
from unittest import TestCase
from unittest.mock import AsyncMock, Mock

import pytest

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import Contractor
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_score import (
    ContractorSafetyScore,
)
from worker_safety_service.risk_model.metrics.contractor.global_contractor_safety_score import (
    GlobalContractorSafetyScore,
)

# TODO: Replace mocks with the actual implementation


@pytest.mark.asyncio
async def test_global_contractor_safety_score_no_contractors(
    metrics_manager: RiskModelMetricsManager,
) -> None:
    test = TestCase()

    contractors_manager: ContractorsManager = Mock(spec=ContractorsManager)
    contractors_manager.get_contractors = AsyncMock(return_value=[])  # type: ignore

    tenant_id = uuid.uuid4()
    metric = GlobalContractorSafetyScore(
        metrics_manager, contractors_manager, tenant_id
    )

    await metric.run()

    contractors_manager.get_contractors.assert_called_with(tenant_id=tenant_id)
    with test.assertRaises(Exception):
        await GlobalContractorSafetyScore.load(metrics_manager, tenant_id)


@pytest.mark.asyncio
async def test_global_contractor_safety_score_with_contractors(
    metrics_manager: RiskModelMetricsManager,
    tenant_id: uuid.UUID,
) -> None:
    contractors = []
    contractor_safety_scores = [0.3, 0.05, 0.1]
    for i in range(0, 3):
        contractor = Contractor(id=uuid.uuid4(), name=f"name_{i}", tenant_id=tenant_id)
        contractors.append(contractor)
        await ContractorSafetyScore.store(
            metrics_manager, contractor.id, contractor_safety_scores[i]
        )

    contractors_manager: ContractorsManager = Mock(spec=ContractorsManager)
    contractors_manager.get_contractors = AsyncMock(return_value=contractors)  # type: ignore

    metric = GlobalContractorSafetyScore(
        metrics_manager, contractors_manager, tenant_id
    )

    await metric.run()

    contractors_manager.get_contractors.assert_called_with(tenant_id=tenant_id)
    metric_avg, metric_stddev = await GlobalContractorSafetyScore.load(
        metrics_manager, tenant_id
    )
    assert metric_avg.tenant_id == tenant_id
    assert metric_stddev.tenant_id == tenant_id
    assert metric_avg.value == 0.15
    assert round(metric_stddev.value, 4) == 0.1080
