import datetime
import uuid
from unittest.mock import AsyncMock

import pytest

from tests.factories import ContractorFactory, TenantFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_error,
    check_input,
    check_inputs_errors_length,
    check_successful_test,
)
from worker_safety_service.dal.contractors import ContractorHistory, ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    Contractor,
    ContractorProjectExecutionModel,
    GblContractorProjectHistoryBaselineModel,
    GblContractorProjectHistoryBaselineModelStdDev,
)
from worker_safety_service.risk_model.metrics.contractor.contractor_project_execution import (
    ContractorProjectExecution,
    ContractorProjectExecutionInput,
    ContractorProjectExecutionParams,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractor_project_execution(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    contractors_manager: ContractorsManager,
) -> None:
    temp_contractor_id = uuid.uuid4()
    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=temp_contractor_id,
        contractors_manager=contractors_manager,
    )
    check_data(data, ["Contractor Project Execution"])
    check_inputs_errors_length(data, [0], [1])
    check_error(data[0].errors[0], Contractor, {"contractor_id": temp_contractor_id})

    tenant = await TenantFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session, tenant_id=tenant.id)
    contractors_manager.get_contractor_experience_years = AsyncMock(return_value=1)  # type: ignore
    contractors_manager.get_contractor_history = AsyncMock(  # type: ignore
        return_value=ContractorHistory(n_safety_observations=2, n_action_items=3)
    )
    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ContractorProjectExecutionModel,
        {"contractor_id": contractor.id, "calculated_before": None},
    )

    inputs: dict[str, float | int] = dict(
        n_safety_observations=1, n_action_items=2, contractor_experience_years=3
    )
    await ContractorProjectExecution.store(
        metrics_manager,
        contractor.id,
        value=111,
        inputs=inputs,
    )
    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [2])

    check_input(data[0].inputs[0], ContractorProjectExecutionInput, inputs)
    assert data[0] is not None and data[0].metric is not None
    for err in data[0].errors:
        check_error(
            err,
            [
                GblContractorProjectHistoryBaselineModel,
                GblContractorProjectHistoryBaselineModelStdDev,
            ],
            {
                "tenant_id": tenant.id,
                "calculated_before": data[0].metric.calculated_at,
            },
        )

    await metrics_manager.store(
        GblContractorProjectHistoryBaselineModel(tenant_id=tenant.id, value=222)
    )
    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, [1], [2])
    check_input(data[0].inputs[0], ContractorProjectExecutionInput, inputs)
    assert data[0] is not None and data[0].metric is not None
    for err in data[0].errors:
        check_error(
            err,
            [
                GblContractorProjectHistoryBaselineModel,
                GblContractorProjectHistoryBaselineModelStdDev,
            ],
            {"tenant_id": tenant.id, "calculated_before": data[0].metric.calculated_at},
        )

    await metrics_manager.store(
        GblContractorProjectHistoryBaselineModelStdDev(tenant_id=tenant.id, value=333)
    )

    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )
    check_inputs_errors_length(data, errors_length=[2])
    assert data[0] is not None and data[0].metric is not None
    for err in data[0].errors:
        check_error(
            err,
            [
                GblContractorProjectHistoryBaselineModel,
                GblContractorProjectHistoryBaselineModelStdDev,
            ],
            {"tenant_id": tenant.id, "calculated_before": data[0].metric.calculated_at},
        )

    db_session.add(
        GblContractorProjectHistoryBaselineModel(
            tenant_id=tenant.id, value=222, calculated_at=datetime.datetime(2020, 1, 1)
        )
    )
    db_session.add(
        GblContractorProjectHistoryBaselineModelStdDev(
            tenant_id=tenant.id, value=333, calculated_at=datetime.datetime(2020, 1, 1)
        )
    )
    await db_session.commit()

    data = await ContractorProjectExecution.explain(
        metrics_manager,
        contractor_id=contractor.id,
        contractors_manager=contractors_manager,
    )

    check_successful_test(data, ["Contractor Project Execution"], [111])
    check_inputs_errors_length(data, [3], [0])

    check_input(
        data[0].inputs[0], GblContractorProjectHistoryBaselineModel, dict(value=222)
    )
    check_input(
        data[0].inputs[1],
        GblContractorProjectHistoryBaselineModelStdDev,
        dict(value=333),
    )
    check_input(
        data[0].inputs[2],
        ContractorProjectExecutionInput,
        dict(n_safety_observations=1, n_action_items=2, contractor_experience_years=3),
    )

    check_input(
        data[0].calc_params,
        ContractorProjectExecutionParams,
        dict(
            cph_weight_low=0,
            cph_weight_high=1,
            exp_factor_1=1,
            exp_factor_2=0.5,
            exp_factor_n=0,
        ),
    )
