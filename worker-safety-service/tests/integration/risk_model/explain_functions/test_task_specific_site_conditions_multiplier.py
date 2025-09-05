import uuid

import pendulum
import pytest

from tests.db_data import DBData
from tests.factories import LibraryTaskFactory, TaskFactory
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
    TaskSpecificSiteConditionsMultiplierModel,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_task_specific_site_conditions_multiplier_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    db_data: DBData,
) -> None:
    now = pendulum.now().date()
    yesterday = pendulum.yesterday().date()
    task_id = uuid.uuid4()
    data = await TaskSpecificSiteConditionsMultiplier.explain(
        metrics_manager, task_id, now
    )

    check_data(data, ["Task Specific Site Conditions Multiplier"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        TaskSpecificSiteConditionsMultiplierModel,
        {"project_task_id": task_id, "date": now, "calculated_before": None},
    )

    ctx = await project_with_location_but_no_active_tasks(db_session)
    project = ctx["project"]
    location = (await db_data.project_locations(project.id))[0]
    library_task = await LibraryTaskFactory.persist(db_session, name=uuid.uuid4().hex)
    task = await TaskFactory.persist(
        db_session,
        location_id=location.id,
        library_task_id=library_task.id,
        date=now,
    )

    await TaskSpecificSiteConditionsMultiplier.store(
        metrics_manager,
        project_task_id=task.id,
        date=now,
        value=123,
    )

    data = await TaskSpecificSiteConditionsMultiplier.explain(
        metrics_manager, task.id, yesterday
    )

    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        TaskSpecificSiteConditionsMultiplierModel,
        {
            "project_task_id": task.id,
            "date": yesterday,
            "calculated_before": None,
        },
    )

    data = await TaskSpecificSiteConditionsMultiplier.explain(
        metrics_manager, task.id, now
    )
    check_successful_test(data, ["Task Specific Site Conditions Multiplier"], [123])
