import datetime
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
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.models import (
    AsyncSession,
    AverageSupervisorEngagementFactorModel,
    StdDevSupervisorEngagementFactorModel,
    Supervisor,
    SupervisorEngagementFactorModel,
)
from worker_safety_service.risk_model.metrics.global_supervisor_enganement_factor import (
    GlobalSupervisorEngagementFactor,
)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_global_supervisor_engagement_factor_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    supervisors_manager: SupervisorsManager,
    tenant_id: uuid.UUID,
) -> None:
    data = await GlobalSupervisorEngagementFactor.explain(
        metrics_manager,
        tenant_id=tenant_id,
        supervisors_manager=supervisors_manager,
    )
    check_data(
        data,
        [
            "Global Supervisor Engagement Factor Average",
            "Global Supervisor Engagement Factor Std Dev",
        ],
    )
    check_inputs_errors_length(data, [0, 0], [0, 1])
    check_error(
        data[1].errors[0],
        AverageSupervisorEngagementFactorModel,
        {"calculated_before": None, "tenant_id": tenant_id},
    )

    tenant = await TenantFactory.persist(db_session)

    db_session.add(
        AverageSupervisorEngagementFactorModel(
            tenant_id=tenant.id, value=1, calculated_at=datetime.datetime(2021, 12, 31)
        )
    )
    await db_session.commit()
    data = await GlobalSupervisorEngagementFactor.explain(
        metrics_manager,
        tenant_id=tenant.id,
        supervisors_manager=supervisors_manager,
    )
    check_inputs_errors_length(data, [0, 0], [0, 1])
    check_error(
        data[1].errors[0],
        StdDevSupervisorEngagementFactorModel,
        {"calculated_before": None, "tenant_id": tenant.id},
    )

    db_session.add(
        StdDevSupervisorEngagementFactorModel(
            tenant_id=tenant.id, value=2, calculated_at=datetime.datetime(2021, 12, 31)
        )
    )

    await db_session.commit()

    data = await GlobalSupervisorEngagementFactor.explain(
        metrics_manager, tenant_id=tenant.id, supervisors_manager=supervisors_manager
    )
    check_successful_test(
        data,
        [
            "Global Supervisor Engagement Factor Average",
            "Global Supervisor Engagement Factor Std Dev",
        ],
        [1, 2],
    )
    check_inputs_errors_length(data, [0, 0], [0, 0])

    supervisors = [
        Supervisor(external_key=uuid.uuid4().hex, tenant_id=tenant.id) for _ in range(5)
    ]
    for supervisor in supervisors:
        db_session.add(supervisor)
    await db_session.commit()
    for supervisor in supervisors:
        await db_session.refresh(supervisor)

    supervisor_engagement_factors = [
        SupervisorEngagementFactorModel(
            supervisor_id=x.id, calculated_at=datetime.datetime(2022, 1, 1), value=i
        )
        for i, x in enumerate(supervisors)
    ]
    for sef in supervisor_engagement_factors:
        db_session.add(sef)
    await db_session.commit()
    for sef in supervisor_engagement_factors:
        await db_session.refresh(sef)
    data = await GlobalSupervisorEngagementFactor.explain(
        metrics_manager, tenant_id=tenant.id, supervisors_manager=supervisors_manager
    )
    check_inputs_errors_length(data, [0, 0], [0, 0])

    db_session.add(
        AverageSupervisorEngagementFactorModel(
            tenant_id=tenant.id, value=1, calculated_at=datetime.datetime(2022, 2, 1)
        )
    )
    db_session.add(
        StdDevSupervisorEngagementFactorModel(
            tenant_id=tenant.id, value=2, calculated_at=datetime.datetime(2022, 2, 1)
        )
    )
    await db_session.commit()
    data = await GlobalSupervisorEngagementFactor.explain(
        metrics_manager, tenant_id=tenant.id, supervisors_manager=supervisors_manager
    )
    check_inputs_errors_length(data, [0, 5], [0, 0])
    for inp in data[1].inputs:
        check_input(
            inp,
            SupervisorEngagementFactorModel,
            {
                "supervisor_id__in": [x.id for x in supervisors],
                "value__in": list(range(len(supervisor_engagement_factors) + 1)),
            },
        )
