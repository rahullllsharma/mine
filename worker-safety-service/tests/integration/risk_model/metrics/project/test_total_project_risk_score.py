import asyncio
import datetime
import itertools
import random
import uuid
from typing import Awaitable, Callable

import pendulum
import pytest

from tests.db_data import DBData
from tests.integration.risk_model.explain_functions import (
    check_dependency,
    check_error,
    check_has_dependencies,
    check_input,
    check_inputs_errors_length,
    check_no_dependencies,
    check_successful_test,
)
from tests.integration.risk_model.utils.common_project_factories import (
    ProjectWithContext,
    project_not_active,
    project_with_multiple_locations_with_multiple_tasks,
    project_with_multiple_locations_with_multiple_tasks_with_empty_location,
    project_with_multiple_tasks,
    project_with_one_task,
)
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.locations import LocationsManager
from worker_safety_service.dal.risk_model import (
    MetricNotAvailableForDateError,
    MissingMetricError,
    RiskModelMetricsManager,
)
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    Location,
    TotalProjectLocationRiskScoreModel,
    TotalProjectRiskScoreModel,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.risk_model.metrics.project.total_project_risk_score import (
    TotalProjectRiskScore,
)


async def with_multiple_tasks_skips_project_location_without_tasks(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    _date: datetime.date,
) -> ProjectWithContext:
    context = (
        await project_with_multiple_locations_with_multiple_tasks_with_empty_location(
            db_session
        )
    )

    locations_with_tasks: list[Location] = context["locations_with_tasks"]  # type: ignore
    assert len(locations_with_tasks) == 2, "Precondition: 2 locations with tasks"

    # Store a value for the tasks that have tasks, probably replace
    location_values = [100.0, 200.0]
    for i, location in enumerate(locations_with_tasks):
        await TotalProjectLocationRiskScore.store(
            metrics_manager, location.id, _date, location_values[i]
        )

    return context


async def _test_total_project_risk_score(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    _date: datetime.date,
) -> ProjectWithContext:
    # Migrated from the old function.
    ctx = await project_with_multiple_locations_with_multiple_tasks(db_session)
    project = ctx["project"]
    locations = await DBData(db_session).project_locations(project.id)

    total_project_location_risk_scores: list[float] = [298.0, 140.3, 41.5]

    routines = []
    for location, score in zip(locations, total_project_location_risk_scores):
        routines.append(
            TotalProjectLocationRiskScore.store(
                metrics_manager,
                location.id,
                _date,
                score,
            )
        )

    await asyncio.gather(*routines)

    return ctx


@pytest.mark.parametrize(
    "context",
    [
        project_with_one_task,
        project_with_multiple_tasks,
        project_with_multiple_locations_with_multiple_tasks,
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_no_metrics_for_location(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    locations_manager: LocationsManager,
    context: Callable[[AsyncSession], Awaitable[ProjectWithContext]],
    db_data: DBData,
) -> None:
    ctx = await context(db_session)
    project = ctx["project"]
    locations = await db_data.project_locations(project.id)
    _date = pendulum.today().date()

    # Will make sure only one of the locations is missing the value
    if len(locations) > 1:
        location_without_value = random.choice(locations)
        for location in itertools.filterfalse(
            lambda e: e == location_without_value, locations
        ):
            await TotalProjectLocationRiskScore.store(
                metrics_manager, location.id, _date, 100
            )

    metric = TotalProjectRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        locations_manager,
        project.id,
        _date,
    )

    with pytest.raises(MissingMetricError) as error:
        await metric.run()

    assert "Could not fetch metric: TotalProjectLocationRiskScoreModel" in str(
        error.value
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_with_project_not_active(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    locations_manager: LocationsManager,
) -> None:
    ctx = await project_not_active(db_session)
    project = ctx["project"]
    _date = pendulum.today().date()

    metric = TotalProjectRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        locations_manager,
        project.id,
        _date,
    )

    with pytest.raises(MetricNotAvailableForDateError):
        await metric.run()


@pytest.mark.parametrize(
    "context, expected_value",
    [
        (with_multiple_tasks_skips_project_location_without_tasks, 150.0),
        (_test_total_project_risk_score, 188.4333),
    ],
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_value_is_calculated_correctly(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    context: Callable[
        [AsyncSession, RiskModelMetricsManager, datetime.date],
        Awaitable[ProjectWithContext],
    ],
    expected_value: float,
    locations_manager: LocationsManager,
) -> None:
    _date = datetime.date.today()
    ctx = await context(db_session, metrics_manager, _date)
    project = ctx["project"]

    metric = TotalProjectRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        locations_manager,
        project.id,
        _date,
    )

    await metric.run()

    # Load value that was calculated
    actual = await TotalProjectRiskScore.load(metrics_manager, project.id, _date)
    expected = TotalProjectRiskScoreModel(
        project_id=project.id, date=_date, value=expected_value
    )
    assert (
        actual.project_id == expected.project_id
        and actual.date == expected.date
        and round(actual.value, 4) == expected.value
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_total_project_risk_score_explain_method(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    work_package_manager: WorkPackageManager,
    contractors_manager: ContractorsManager,
    task_manager: TaskManager,
    db_data: DBData,
) -> None:
    ctx = await project_with_multiple_locations_with_multiple_tasks(db_session)
    project = ctx["project"]
    locations = await db_data.project_locations(project.id)

    total_project_location_risk_scores: list[list[float]] = [
        [103.5, 245.3, 298.0],
        [31.9, 231.8, 140.3],
        [256.1, 79.9, 41.5],
    ]
    flat_scores: list[float] = list(
        itertools.chain(*total_project_location_risk_scores)
    )
    location_ids: list[uuid.UUID] = [x.id for x in locations]
    _date = datetime.date.today()

    for i, location in enumerate(locations):
        for score in total_project_location_risk_scores[i]:
            await TotalProjectLocationRiskScore.store(
                metrics_manager,
                location.id,
                _date,
                score,
            )

    await TotalProjectRiskScore.store(
        metrics_manager,
        project.id,
        _date,
        1.234,
        dict(project_location_ids=list(set([str(x.id) for x in locations]))),
    )

    data = await TotalProjectRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        project.id,
        _date,
    )
    check_successful_test(data, ["Total Project Risk Score"], [1.234])
    check_inputs_errors_length(data, [3], [0])
    for inp in data[0].inputs:
        check_input(
            inp,
            TotalProjectLocationRiskScoreModel,
            {
                "date": _date,
                "value__in": flat_scores,
                "project_location_id__in": location_ids,
            },
        )
    check_has_dependencies(data[0], 3)
    if data[0].dependencies is not None:
        for dep in data[0].dependencies:
            check_dependency(dep, ["Total Project Location Risk Score"], flat_scores)

    data = await TotalProjectLocationRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        project.id,
        _date - datetime.timedelta(days=1),
    )

    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        TotalProjectLocationRiskScoreModel,
        {
            "calculated_before": None,
            "date": _date - datetime.timedelta(days=1),
        },
    )
    check_no_dependencies(data)

    data = await TotalProjectLocationRiskScore.explain(
        metrics_manager,
        work_package_manager,
        contractors_manager,
        task_manager,
        uuid.uuid4(),
        _date,
    )
    check_inputs_errors_length(data, [0], [1])
    check_error(
        data[0].errors[0],
        TotalProjectLocationRiskScoreModel,
        {
            "calculated_before": None,
            "date": _date,
        },
    )
    check_no_dependencies(data)
