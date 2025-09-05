import uuid

import pytest

from tests.factories import LibraryTaskFactory, TenantFactory
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
    TaskSpecificSafetyClimateMultiplierModel,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificClimateMultiplierParams,
    TaskSpecificSafetyClimateMultiplier,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_task_specific_safety_climate_multiplier_explain_method(
    db_session: AsyncSession, metrics_manager: RiskModelMetricsManager
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    library_task_id = uuid.uuid4()
    data = await TaskSpecificSafetyClimateMultiplier.explain(
        metrics_manager, library_task_id=library_task_id, tenant_id=tenant.id
    )
    check_data(data, ["Task Specific Safety Climate Multiplier"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        TaskSpecificSafetyClimateMultiplierModel,
        {"library_task_id": library_task_id, "calculated_before": None},
    )

    task = await LibraryTaskFactory.persist(db_session)

    await TaskSpecificSafetyClimateMultiplier.store(
        metrics_manager, library_task_id=task.id, value=123, tenant_id=tenant.id
    )

    data = await TaskSpecificSafetyClimateMultiplier.explain(
        metrics_manager, library_task_id=task.id, tenant_id=tenant.id
    )
    check_inputs_errors_length(data, [0], [0])

    check_successful_test(data, ["Task Specific Safety Climate Multiplier"], [123])
    check_input(
        data[0].calc_params,
        TaskSpecificClimateMultiplierParams,
        dict(
            near_miss=0.001,
            first_aid=0.007,
            recordable=0.033,
            restricted=0.033,
            lost_time=0.067,
            p_sif=0.1,
            sif=0.1,
        ),
    )
