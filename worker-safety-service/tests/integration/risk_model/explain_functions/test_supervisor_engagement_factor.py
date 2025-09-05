import uuid

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
    Supervisor,
    SupervisorEngagementFactorModel,
)
from worker_safety_service.risk_model.metrics.supervisor_engagement_factor import (
    SupervisorEngagementFactor,
    SupervisorEngagementFactorParams,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisor_engagement_factor_explain_method(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    supervisor_id = uuid.uuid4()
    data = await SupervisorEngagementFactor.explain(
        metrics_manager, supervisor_id=supervisor_id
    )
    check_data(data, ["Supervisor Engagement Factor"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        SupervisorEngagementFactorModel,
        {"supervisor_id": supervisor_id, "calculated_before": None},
    )

    tenant = await TenantFactory.default_tenant(db_session)
    supervisor = Supervisor(external_key=uuid.uuid4().hex, tenant_id=tenant.id)
    db_session.add(supervisor)
    await db_session.commit()
    await db_session.refresh(supervisor)

    await SupervisorEngagementFactor.store(
        metrics_manager, supervisor_id=supervisor.id, value=123
    )

    data = await SupervisorEngagementFactor.explain(
        metrics_manager, supervisor_id=supervisor.id
    )

    check_successful_test(data, ["Supervisor Engagement Factor"], [123])

    check_input(
        data[0].calc_params,
        SupervisorEngagementFactorParams,
        dict(
            obs_number_threshold=4,
            esd_number_threshold=4,
            obs_number_value_below=1,
            obs_number_value_above=0,
            esd_number_value_below=1,
            esd_number_value_above=0,
            obs_timing_threshold_first=0.25,
            obs_timing_threshold_second=0.5,
            obs_timing_threshold_third=0.75,
            obs_timing_value_first=0.0,
            obs_timing_value_second=1.0,
            obs_timing_value_third=1.5,
            obs_timing_value_fourth=2.0,
            esd_timing_threshold_first=0.25,
            esd_timing_threshold_second=0.5,
            esd_timing_threshold_third=0.75,
            esd_timing_value_first=0.0,
            esd_timing_value_second=1.0,
            esd_timing_value_third=1.5,
            esd_timing_value_fourth=2.0,
            obs_month_fraction=0.75,
            esd_month_fraction=0.75,
        ),
    )
