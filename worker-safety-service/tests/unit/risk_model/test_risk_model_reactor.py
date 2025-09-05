import asyncio
import uuid

import pytest

from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorLocalImpl
from worker_safety_service.risk_model.triggers.contractor_data_changed_for_tenant import (
    ContractorDataChangedForTenant,
)


@pytest.mark.asyncio
async def test_add_duplicated_metrics() -> None:
    reactor = RiskModelReactorLocalImpl()

    tenant_id = uuid.uuid4()
    await asyncio.gather(
        reactor.add(ContractorDataChangedForTenant(tenant_id)),
        reactor.add(ContractorDataChangedForTenant(uuid.uuid4())),
        reactor.add(ContractorDataChangedForTenant(tenant_id)),
    )

    assert reactor.work_queue.qsize() == 2
