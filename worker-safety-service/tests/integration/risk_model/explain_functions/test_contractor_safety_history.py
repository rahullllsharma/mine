import datetime

import pytest

from tests.factories import ContractorFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_error,
    check_input,
    check_inputs_errors_length,
    check_successful_test,
)
from worker_safety_service.dal.contractors import CSHIncident
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import AsyncSession, ContractorSafetyHistoryModel
from worker_safety_service.risk_model.metrics.contractor.contractor_safety_history import (
    ContractorSafetyHistory,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractor_safety_history_explain_method(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    contractor = await ContractorFactory.persist(db_session)
    data = await ContractorSafetyHistory.explain(
        metrics_manager, contractor_id=contractor.id
    )
    check_data(data, ["Contractor Safety History"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ContractorSafetyHistoryModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": None,
        },
    )

    await ContractorSafetyHistory.store(
        metrics_manager,
        contractor_id=contractor.id,
        value=123,
    )
    data = await ContractorSafetyHistory.explain(
        metrics_manager, contractor_id=contractor.id
    )
    check_inputs_errors_length(data, [0], [0])

    inputs: dict[str, int | float] = dict(
        near_miss=1,
        first_aid=2,
        recordable=3,
        restricted=4,
        lost_time=5,
        p_sif=6,
        sif=7,
        sum_of_project_cost=8,
    )
    await ContractorSafetyHistory.store(
        metrics_manager, contractor_id=contractor.id, value=123, inputs=inputs
    )

    data = await ContractorSafetyHistory.explain(
        metrics_manager,
        contractor_id=contractor.id,
        calculated_before=datetime.datetime(2020, 12, 31),
    )
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ContractorSafetyHistoryModel,
        {
            "contractor_id": contractor.id,
            "calculated_before": datetime.datetime(2020, 12, 31, 0, 0),
        },
    )

    data = await ContractorSafetyHistory.explain(
        metrics_manager, contractor_id=contractor.id
    )

    check_successful_test(data, ["Contractor Safety History"], [123])
    check_inputs_errors_length(data, [1], [0])
    check_input(data[0].inputs[0], CSHIncident, inputs)
