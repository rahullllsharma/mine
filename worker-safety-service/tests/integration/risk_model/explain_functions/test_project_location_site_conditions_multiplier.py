import uuid

import pendulum
import pytest

from tests.db_data import DBData
from tests.factories import SiteConditionFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_error,
    check_inputs_errors_length,
    check_successful_test,
)
from tests.integration.risk_model.utils.common_project_factories import (
    project_with_location_but_no_active_tasks,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    ProjectLocationSiteConditionsMultiplierModel,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_site_conditions_multiplier_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    db_data: DBData,
) -> None:
    now = pendulum.now().date()
    yesterday = pendulum.yesterday().date()
    location_id = uuid.uuid4()
    data = await ProjectLocationSiteConditionsMultiplier.explain(
        metrics_manager, location_id, now
    )
    check_data(data, ["Project Site Conditions Multiplier"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ProjectLocationSiteConditionsMultiplierModel,
        {
            "project_location_id": location_id,
            "date": now,
            "calculated_before": None,
        },
    )

    ctx = await project_with_location_but_no_active_tasks(db_session)
    project = ctx["project"]
    location = (await db_data.project_locations(project.id))[0]

    await SiteConditionFactory.persist_many(
        db_session,
        size=4,
        location_id=location.id,
    )

    await ProjectLocationSiteConditionsMultiplier.store(
        metrics_manager,
        project_location_id=location.id,
        date=now,
        value=123,
    )

    data = await ProjectLocationSiteConditionsMultiplier.explain(
        metrics_manager, location.id, yesterday
    )
    check_data(data, ["Project Site Conditions Multiplier"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ProjectLocationSiteConditionsMultiplierModel,
        {
            "project_location_id": location.id,
            "date": yesterday,
            "calculated_before": None,
        },
    )

    data = await ProjectLocationSiteConditionsMultiplier.explain(
        metrics_manager, location.id, now
    )

    check_successful_test(data, ["Project Site Conditions Multiplier"], [123])
    check_inputs_errors_length(data, [0], [0])
