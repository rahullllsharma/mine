import pytest

from tests.factories import ContractorFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_error,
    check_inputs_errors_length,
    check_successful_test,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession, ContractorSafetyRatingModel
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_rating import (
    ContractorSafetyRating,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractor_safety_rating_explain_method(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    contractor = await ContractorFactory.persist(db_session)
    data = await ContractorSafetyRating.explain(
        metrics_manager, contractor_id=contractor.id
    )
    check_data(data, ["Contractor Safety Rating"])
    check_inputs_errors_length(data, errors_length=[1])
    check_error(
        data[0].errors[0],
        ContractorSafetyRatingModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": None,
        },
    )

    await ContractorSafetyRating.store(
        metrics_manager, contractor_id=contractor.id, value=123
    )
    data = await ContractorSafetyRating.explain(
        metrics_manager, contractor_id=contractor.id
    )

    check_successful_test(data, ["Contractor Safety Rating"], [123])
    check_inputs_errors_length(data, [0], [0])
