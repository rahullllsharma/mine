import datetime
import uuid
from unittest import TestCase
from unittest.mock import AsyncMock

import pytest
from sqlmodel import select

from tests.factories import ContractorFactory, TenantFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_dependency,
    check_error,
    check_has_dependencies,
    check_inputs_errors_length,
    check_successful_test,
)
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    AverageContractorSafetyScoreModel,
    Contractor,
    ContractorSafetyScoreModel,
    StdDevContractorSafetyScoreModel,
)
from worker_safety_service.risk_model.metrics.contractor.global_contractor_safety_score import (
    GlobalContractorSafetyScore,
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_global_contractor_safety_score_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    contractors_manager: ContractorsManager,
    tenant_id: uuid.UUID,
) -> None:
    data = await GlobalContractorSafetyScore.explain(
        metrics_manager,
        tenant_id=tenant_id,
        contractors_manager=contractors_manager,
    )
    assert len(data) == 2
    check_data(
        data,
        [
            "Global Contractor Safety Score Average",
            "Global Contractor Safety Score Std Dev",
        ],
    )
    check_inputs_errors_length(data, [0, 0], [0, 1])
    check_error(
        data[1].errors[0],
        AverageContractorSafetyScoreModel,
        {"tenant_id": tenant_id, "calculated_before": None},
    )
    check_has_dependencies(data[1], 0)

    tenant = await TenantFactory.persist(db_session)
    await ContractorFactory.persist_many(db_session, size=6, tenant_id=tenant.id)

    db_session.add(
        AverageContractorSafetyScoreModel(
            tenant_id=tenant.id, value=1, calculated_at=datetime.datetime(2021, 12, 31)
        )
    )
    await db_session.commit()
    data = await GlobalContractorSafetyScore.explain(
        metrics_manager,
        tenant_id=tenant.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0, 0], [0, 1])
    check_error(
        data[1].errors[0],
        StdDevContractorSafetyScoreModel,
        {"tenant_id": tenant.id, "calculated_before": None},
    )
    check_has_dependencies(data[1], 0)

    db_session.add(
        StdDevContractorSafetyScoreModel(
            tenant_id=tenant.id, value=2, calculated_at=datetime.datetime(2021, 12, 31)
        )
    )

    contractors_statement = select(Contractor).where(Contractor.tenant_id == tenant.id)
    contractors = (await db_session.exec(contractors_statement)).all()
    contractors_manager.get_contractors = AsyncMock(return_value=contractors)  # type: ignore
    for i, contractor in enumerate(contractors):
        db_session.add(
            ContractorSafetyScoreModel(
                contractor_id=contractor.id,
                value=5 + i,
                calculated_at=datetime.datetime(2022, 1, i + 1),
            )
        )

    await db_session.commit()

    data = await GlobalContractorSafetyScore.explain(
        metrics_manager,
        tenant_id=tenant.id,
        contractors_manager=contractors_manager,
    )
    check_successful_test(
        data,
        [
            "Global Contractor Safety Score Average",
            "Global Contractor Safety Score Std Dev",
        ],
        [1, 2],
    )
    check_inputs_errors_length(data, [0, 0], [0, 0])

    contractor_safety_score_models = [
        ContractorSafetyScoreModel(
            contractor_id=contractor.id,
            value=5 + i,
            calculated_at=datetime.datetime(2020, 12, i + 1),
        )
        for i, contractor in enumerate(contractors)
    ]
    for item in contractor_safety_score_models:
        db_session.add(item)

    await db_session.commit()
    for item in contractor_safety_score_models:
        await db_session.refresh(item)

    data = await GlobalContractorSafetyScore.explain(
        metrics_manager,
        tenant_id=tenant.id,
        contractors_manager=contractors_manager,
    )

    check_inputs_errors_length(data, [0, 6], [0, 0])

    test = TestCase()
    test.assertCountEqual(data[1].inputs, contractor_safety_score_models)

    check_has_dependencies(data[1], 6)
    if data[1].dependencies is not None:
        for dep in data[1].dependencies:
            check_dependency(dep, ["Contractor Safety Score"], [5, 6, 7, 8, 9, 10])
