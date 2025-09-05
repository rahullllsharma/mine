import asyncio
import datetime

import pytest

from tests.db_data import DBData
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
    project_with_multiple_locations_with_multiple_tasks,
)
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    ProjectLocationSiteConditionsMultiplierModel,
    ProjectLocationTotalTaskRiskScoreModel,
    ProjectSafetyClimateMultiplierModel,
    TotalProjectLocationRiskScoreModel,
)
from worker_safety_service.risk_model.metrics.project.project_safety_climate_multiplier import (
    ProjectSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.project.project_site_conditions_multiplier import (
    ProjectLocationSiteConditionsMultiplier,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
    TotalProjectLocationRiskScoreInput,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_risk_score_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    work_package_manager: WorkPackageManager,
    contractors_manager: ContractorsManager,
    task_manager: TaskManager,
    db_data: DBData,
) -> None:
    ctx = await project_with_multiple_locations_with_multiple_tasks(db_session)
    project = ctx["project"]
    location = (await db_data.project_locations(project.id))[0]

    _date = datetime.date.today()
    db_session.add(
        TotalProjectLocationRiskScoreModel(
            project_location_id=location.id,
            date=_date,
            calculated_at=datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
            value=12,
        )
    )
    await db_session.commit()

    await asyncio.gather(
        ProjectSafetyClimateMultiplier.store(metrics_manager, location.id, 1.2),
        ProjectLocationSiteConditionsMultiplier.store(
            metrics_manager, location.id, _date, 1.2
        ),
        ProjectLocationTotalTaskRiskScore.store(
            metrics_manager, location.id, _date, 1.2
        ),
    )
    await ProjectLocationTotalTaskRiskScore.store(
        metrics_manager, location.id, _date, 1.2
    )
    data = await TotalProjectLocationRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        location.id,
        _date,
    )
    check_data(data, ["Total Project Location Risk Score"])
    check_inputs_errors_length(data, [1], [3])
    check_input(
        data[0].inputs[0],
        TotalProjectLocationRiskScoreInput,
        dict(
            project_safety_climate_multiplier=None,
            project_location_site_conditions_multiplier=None,
            project_location_total_task_risk_score=None,
        ),
    )
    check_error(
        data[0].errors[0],
        ProjectSafetyClimateMultiplierModel,
        {
            "project_location_id": location.id,
            "calculated_before": datetime.datetime(
                2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[1],
        ProjectLocationSiteConditionsMultiplierModel,
        {
            "project_location_id": location.id,
            "date": _date,
            "calculated_before": datetime.datetime(
                2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_error(
        data[0].errors[2],
        ProjectLocationTotalTaskRiskScoreModel,
        {
            "project_location_id": location.id,
            "date": _date,
            "calculated_before": datetime.datetime(
                2000, 1, 1, 0, 0, tzinfo=datetime.timezone.utc
            ),
        },
    )
    check_no_dependencies(data)

    await TotalProjectLocationRiskScore.store(metrics_manager, location.id, _date, 123)

    data = await TotalProjectLocationRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        location.id,
        _date,
    )
    check_successful_test(data, ["Total Project Location Risk Score"], [123])
    check_inputs_errors_length(data, [1], [0])
    check_input(
        data[0].inputs[0],
        TotalProjectLocationRiskScoreInput,
        dict(
            project_safety_climate_multiplier=1.2,
            project_location_site_conditions_multiplier=1.2,
            project_location_total_task_risk_score=1.2,
        ),
    )
    check_has_dependencies(data[0], 3)
    if data[0].dependencies is not None:
        check_dependency(
            data[0].dependencies[0], ["Project Safety Climate Multiplier"], [1.2]
        )
        check_dependency(
            data[0].dependencies[1], ["Project Site Conditions Multiplier"], [1.2]
        )
        check_dependency(
            data[0].dependencies[2], ["Project Location Total Task Risk Score"], [1.2]
        )

    data = await TotalProjectLocationRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        location.id,
        _date,
        False,
    )
    check_no_dependencies(data)
