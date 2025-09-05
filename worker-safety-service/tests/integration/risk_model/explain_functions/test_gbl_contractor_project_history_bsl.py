import datetime

import pytest

from tests.factories import TenantFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_error,
    check_input,
    check_inputs_errors_length,
    check_successful_test,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    GblContractorProjectHistoryBaselineModel,
    GblContractorProjectHistoryBaselineModelStdDev,
)
from worker_safety_service.risk_model.metrics.contractor.gbl_contractor_project_history_bsl import (
    GlobalContractorProjectHistoryBaseline,
    GlobalContractorProjectHistoryBaselineInputs,
    GlobalContractorProjectHistoryBaselineStdDev,
    GlobalContractorProjectHistoryBaselineStdDevInput,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_global_contractor_project_history_baseline(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    tenant = await TenantFactory.persist(db_session)
    data = await GlobalContractorProjectHistoryBaseline.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_data(data, ["Global Contractor Project History Baseline"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        GblContractorProjectHistoryBaselineModel,
        {"tenant_id": tenant.id, "calculated_before": None},
    )

    await GlobalContractorProjectHistoryBaseline.store(
        metrics_manager, tenant_id=tenant.id, value=123
    )
    data = await GlobalContractorProjectHistoryBaseline.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [0])

    await GlobalContractorProjectHistoryBaseline.store(
        metrics_manager,
        tenant_id=tenant.id,
        value=123,
        inputs=dict(n_safety_observations=1),
    )
    data = await GlobalContractorProjectHistoryBaseline.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [1])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineInputs,
        dict(n_safety_observations=1, n_action_items=None),
    )

    await GlobalContractorProjectHistoryBaseline.store(
        metrics_manager,
        tenant_id=tenant.id,
        value=123,
        inputs=dict(n_safety_observations=1, n_action_items=2),
    )

    data = await GlobalContractorProjectHistoryBaseline.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_successful_test(data, ["Global Contractor Project History Baseline"], [123])
    check_inputs_errors_length(data, [1])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineInputs,
        dict(n_safety_observations=1, n_action_items=2),
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_global_contractor_project_history_baseline_std_dev(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    tenant = await TenantFactory.persist(db_session)
    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_data(data, ["Global Contractor Project History Baseline Standard Deviation"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        GblContractorProjectHistoryBaselineModelStdDev,
        {"tenant_id": tenant.id, "calculated_before": None},
    )

    db_session.add(
        GblContractorProjectHistoryBaselineModelStdDev(
            tenant_id=tenant.id, value=123, calculated_at=datetime.datetime(2022, 1, 1)
        )
    )
    await db_session.commit()
    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, errors_length=[1])
    assert data[0].metric is not None and data[0].metric.calculated_at is not None
    check_error(
        data[0].errors[0],
        GblContractorProjectHistoryBaselineModel,
        {"tenant_id": tenant.id, "calculated_before": data[0].metric.calculated_at},
    )

    db_session.add(
        GblContractorProjectHistoryBaselineModel(
            tenant_id=tenant.id, value=1, calculated_at=datetime.datetime(2022, 1, 31)
        )
    )
    await db_session.commit()

    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, errors_length=[1])
    assert data[0].metric is not None and data[0].metric.calculated_at is not None
    check_error(
        data[0].errors[0],
        GblContractorProjectHistoryBaselineModel,
        {"tenant_id": tenant.id, "calculated_before": data[0].metric.calculated_at},
    )

    await GlobalContractorProjectHistoryBaselineStdDev.store(
        metrics_manager, tenant_id=tenant.id, value=123
    )
    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineStdDevInput,
        dict(gbl_contractor_project_history_baseline=1, acc=None, n_contractors=None),
    )

    await GlobalContractorProjectHistoryBaselineStdDev.store(
        metrics_manager, tenant_id=tenant.id, value=123, inputs=dict(hello=1)
    )
    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineStdDevInput,
        dict(gbl_contractor_project_history_baseline=1, acc=None, n_contractors=None),
    )

    await GlobalContractorProjectHistoryBaselineStdDev.store(
        metrics_manager, tenant_id=tenant.id, value=123, inputs=dict(acc=2)
    )
    await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineStdDevInput,
        dict(gbl_contractor_project_history_baseline=1, acc=None, n_contractors=None),
    )

    await GlobalContractorProjectHistoryBaselineStdDev.store(
        metrics_manager,
        tenant_id=tenant.id,
        value=123,
        inputs=dict(acc=2, n_contractors=3),
    )

    data = await GlobalContractorProjectHistoryBaselineStdDev.explain(
        metrics_manager, tenant_id=tenant.id
    )
    check_successful_test(
        data, ["Global Contractor Project History Baseline Standard Deviation"], [123]
    )
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        GlobalContractorProjectHistoryBaselineStdDevInput,
        dict(gbl_contractor_project_history_baseline=1, acc=2, n_contractors=3),
    )
