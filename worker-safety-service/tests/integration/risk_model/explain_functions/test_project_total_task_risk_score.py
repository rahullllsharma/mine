import datetime

import pytest
from faker import Faker

from tests.db_data import DBData
from tests.factories import TaskFactory
from tests.integration.risk_model.explain_functions import (
    check_data,
    check_dependency,
    check_error,
    check_has_dependencies,
    check_input,
    check_inputs_errors_length,
    check_no_dependencies,
    check_successful_test,
)
from tests.integration.risk_model.utils.common_project_factories import (
    project_with_location_but_no_tasks,
)
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.models import (
    AsyncSession,
    ProjectTotalTaskRiskScoreModel,
    TaskSpecificRiskScoreModel,
)
from worker_safety_service.risk_model.metrics.tasks.project_total_task_riskscore import (
    ProjectTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)

fake = Faker()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_total_task_risk_score_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    task_manager: TaskManager,
    db_data: DBData,
) -> None:
    ctx = await project_with_location_but_no_tasks(db_session)
    project = ctx["project"]
    location = (await db_data.project_locations(project.id))[0]

    _date = datetime.date.today()
    data = await ProjectTotalTaskRiskScore.explain(
        metrics_manager, task_manager, project.id, _date
    )
    check_data(data, ["Project Total Task Risk Score"])
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        ProjectTotalTaskRiskScoreModel,
        {"calculated_before": None, "project_id": project.id, "date": _date},
    )
    check_no_dependencies(data)

    await ProjectTotalTaskRiskScore.store(metrics_manager, project.id, _date, 123)
    data = await ProjectTotalTaskRiskScore.explain(
        metrics_manager, task_manager, project.id, _date
    )
    check_inputs_errors_length(data, [0], [0])
    check_no_dependencies(data)

    await ProjectTotalTaskRiskScore.store(
        metrics_manager, project.id, _date, 123, inputs=dict(task_ids=[])
    )
    data = await ProjectTotalTaskRiskScore.explain(
        metrics_manager, task_manager, project.id, _date
    )

    check_inputs_errors_length(data, [0], [0])
    check_no_dependencies(data)

    task = await TaskFactory.persist(db_session, location_id=location.id)

    await TaskSpecificRiskScore.store(metrics_manager, task.id, _date, 456)

    await ProjectTotalTaskRiskScore.store(
        metrics_manager,
        project.id,
        _date,
        123,
        inputs=dict(task_ids=[str(task.id)]),
    )

    data = await ProjectTotalTaskRiskScore.explain(
        metrics_manager, task_manager, project.id, _date
    )

    check_successful_test(data, ["Project Total Task Risk Score"], [123])
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        TaskSpecificRiskScoreModel,
        {"project_task_id": task.id, "date": _date, "value": 456},
    )
    check_has_dependencies(data[0], 1)
    if data[0].dependencies is not None:
        check_dependency(data[0].dependencies[0], ["Task Specific Risk Score"], [456])

    data = await ProjectTotalTaskRiskScore.explain(
        metrics_manager, task_manager, project.id, _date, verbose=False
    )
    check_no_dependencies(data)
