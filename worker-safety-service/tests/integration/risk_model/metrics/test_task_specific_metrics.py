import asyncio
import datetime
import random
import uuid
from typing import NamedTuple
from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker

from tests.factories import (
    ActivityFactory,
    LibraryTaskFactory,
    LocationFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from worker_safety_service.configs.base_configuration_model import store
from worker_safety_service.dal.activities import ActivityManager
from worker_safety_service.dal.configurations import ConfigurationsManager
from worker_safety_service.dal.incidents import IncidentData, IncidentsManager
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.dal.tasks import TaskManager
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    LibrarySiteCondition,
    LibraryTask,
    Location,
    ProjectLocationTotalTaskRiskScoreModel,
    ProjectTotalTaskRiskScoreModel,
    Task,
    TaskSpecificRiskScoreModel,
    TaskSpecificSafetyClimateMultiplierModel,
    TaskSpecificSiteConditionsMultiplierModel,
    WorkPackage,
)
from worker_safety_service.models.base import Activity
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.risk_model.configs.types import (
    RankingThresholds,
    RankingWeight,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_location_total_task_riskscore import (
    StochasticLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.stochastic_model.stochastic_task_specific_risk_score import (
    StochasticTaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.project_location_total_task_riskscore import (
    ProjectLocationTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.project_total_task_riskscore import (
    ProjectTotalTaskRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_riskscore import (
    TaskSpecificRiskScore,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_safety_climate_multiplier import (
    TaskSpecificSafetyClimateMultiplier,
)
from worker_safety_service.risk_model.metrics.tasks.task_specific_site_conditions_multiplier import (
    TaskSpecificSiteConditionsMultiplier,
)
from worker_safety_service.site_conditions import (
    SiteConditionResult,
    SiteConditionsEvaluator,
)

incident_data = IncidentData(
    near_miss=1,
    first_aid=3,
    recordable=5,
    restricted=7,
    lost_time=5,
    p_sif=3,
    sif=1,
)


class SampleProject(NamedTuple):
    library_task: LibraryTask
    project: WorkPackage
    location: Location
    task: Task
    activity: Activity
    locations: list[Location]
    tasks: list[Task]
    activities: list[Activity]


@pytest.mark.asyncio
async def test_task_specific_safety_climate_multiplier(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    library_tasks_manager: LibraryTasksManager,
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    # Get random task id
    tasks = await library_tasks_manager.get_library_tasks()
    library_task_id: uuid.UUID = random.choice(tasks).id

    metrics_manager = Mock(wraps=metrics_manager)

    incidents_manager: IncidentsManager = Mock(spec=IncidentsManager)
    incidents_manager.get_tasks_incident_data = AsyncMock(return_value=incident_data)  # type: ignore

    metric = TaskSpecificSafetyClimateMultiplier(
        metrics_manager, incidents_manager, library_task_id, tenant_id=tenant.id
    )
    await metric.run()

    metrics_manager.store.assert_called_once()
    actual = metrics_manager.store.call_args[0][0]
    expected_value = (
        (1 * 0.001)
        + (3 * 0.007)
        + (5 * 0.033)
        + (7 * 0.033)
        + (5 * 0.067)
        + (3 * 0.1)
        + (1 * 0.1)
    )
    expected = TaskSpecificSafetyClimateMultiplierModel(
        library_task_id=library_task_id, value=expected_value
    )
    assert (
        actual.value == expected.value
        and actual.library_task_id == expected.library_task_id
    )

    stored = await TaskSpecificSafetyClimateMultiplier.load(
        metrics_manager, library_task_id=library_task_id, tenant_id=tenant.id
    )
    assert stored.value == expected.value


@pytest.mark.asyncio
async def test_task_specific_site_conditions_multiplier(
    metrics_manager: RiskModelMetricsManager,
    task_manager: TaskManager,
    work_package_manager: WorkPackageManager,
    sample_project: SampleProject,
) -> None:
    task: Task = sample_project.task
    date = datetime.date.today()

    site_conditions_evaluations: list[SiteConditionResult] = [
        SiteConditionResult(
            condition_name="sd_1",
            condition_value="100",
            condition_applies=True,
            multiplier=7,
        ),
        SiteConditionResult(
            condition_name="sd_2",
            condition_value="25",
            condition_applies=False,
            multiplier=11,
        ),
        SiteConditionResult(
            condition_name="sd_3",
            condition_value="75",
            condition_applies=True,
            multiplier=5,
        ),
    ]

    site_conditions_evaluator: SiteConditionsEvaluator = Mock(
        spec=SiteConditionsEvaluator
    )
    site_conditions_evaluator.evaluate_project_location_task = AsyncMock(return_value=site_conditions_evaluations)  # type: ignore

    metric = TaskSpecificSiteConditionsMultiplier(
        metrics_manager,
        task_manager,
        work_package_manager,
        site_conditions_evaluator,
        task.id,
        date,
    )
    await metric.run()

    actual = await TaskSpecificSiteConditionsMultiplier.load(
        metrics_manager, task.id, date
    )
    expected = TaskSpecificSiteConditionsMultiplierModel(
        project_task_id=task.id, date=date, value=12
    )
    assert (
        actual.project_task_id == expected.project_task_id
        and actual.date == expected.date
        and actual.value == expected.value
    )


@pytest.mark.asyncio
async def test_task_specific_riskscore(
    db_session: AsyncSession,
    metrics_manager: RiskModelMetricsManager,
    task_manager: TaskManager,
    sample_project: SampleProject,
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    library_task = sample_project.library_task
    task = sample_project.task
    date = datetime.date.today()

    await asyncio.gather(
        TaskSpecificSafetyClimateMultiplier.store(
            metrics_manager, library_task.id, 0.17, tenant.id
        ),
        TaskSpecificSiteConditionsMultiplier.store(
            metrics_manager, task.id, date, 0.33
        ),
    )

    metric = TaskSpecificRiskScore(
        metrics_manager, task_manager, task.id, date, tenant.id
    )
    await metric.run()

    actual = await TaskSpecificRiskScore.load(metrics_manager, task.id, date)
    expected = TaskSpecificRiskScoreModel(
        project_task_id=task.id, date=date, value=150.0
    )
    assert (
        actual.project_task_id == expected.project_task_id
        and actual.date == expected.date
        and actual.value == expected.value
    )


@pytest.mark.asyncio
async def test_project_total_task_risk_score(
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    sample_project: SampleProject,
) -> None:
    project_id = sample_project.project.id
    date = datetime.date.today()

    # Contributes to the ProjectTotalTaskRiskScore (Other tasks are not in progress today)
    # ((201 * 1.5) + (361 * 2) + (41 * 1) + (10 * 1)) / 5.5 = 195.363636364
    task_scores = [201, 361, 349, 41, 10, 243]
    await asyncio.gather(
        *[
            TaskSpecificRiskScore.store(metrics_manager, task.id, date, task_scores[i])
            for i, task in enumerate(sample_project.tasks)
        ]
    )

    metric = ProjectTotalTaskRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        project_id,
        date,
    )
    await metric.run()

    actual = await ProjectTotalTaskRiskScore.load(metrics_manager, project_id, date)
    expected = ProjectTotalTaskRiskScoreModel(
        project_id=project_id, date=date, value=195.3636
    )
    assert (
        actual.project_id == expected.project_id
        and actual.date == expected.date
        and round(actual.value, 4) == expected.value
    )


@pytest.mark.asyncio
async def test_project_location_total_task_risk_score(
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    sample_project: SampleProject,
) -> None:
    # Grab the location with 4 tasks
    location_id = sample_project.locations[1].id
    date = datetime.date.today()

    # The score at 2: will be discarded because of the task end_date
    # The score at 0, 5: will be discarded because they are from a different task
    task_scores = [3.0, 0.33, 2.0, 0.77, 1.0, 0.0]
    await asyncio.gather(
        *[
            TaskSpecificRiskScore.store(metrics_manager, task.id, date, task_scores[i])
            for i, task in enumerate(sample_project.tasks)
        ]
    )

    metric = ProjectLocationTotalTaskRiskScore(
        metrics_manager,
        configurations_manager,
        work_package_manager,
        task_manager,
        location_id,
        date,
    )
    await metric.run()

    actual = await ProjectLocationTotalTaskRiskScore.load(
        metrics_manager, location_id, date
    )
    expected = ProjectLocationTotalTaskRiskScoreModel(
        project_location_id=location_id, date=date, value=0.7
    )
    assert (
        actual.project_location_id == expected.project_location_id
        and actual.date == expected.date
        and round(actual.value, 4) == expected.value
    )


@pytest.fixture
async def sample_project(db_session: AsyncSession) -> SampleProject:
    library_task = await LibraryTaskFactory.persist(db_session, hesp=100)
    site_conditions = [
        LibrarySiteCondition(
            name=f"sc_{i}", handle_code=f"hc_{random.randint(0, 1000)}"
        )
        for i in range(1, 4)
    ]
    db_session.add_all(site_conditions)
    await db_session.commit()

    project: WorkPackage = await WorkPackageFactory.persist(db_session)

    locations: list[Location] = [
        await LocationFactory.persist(db_session, project_id=project.id)
        for _ in range(0, 3)
    ]

    fake = Faker()
    n_tasks_per_location = [1, 4, 0]
    project_activities: list[Activity] = []
    project_tasks: list[Task] = []
    for i in range(0, 3):
        location = locations[i]
        for ii in range(0, n_tasks_per_location[i]):
            dates = {"start_date": fake.past_date()}

            if i == 1 and ii == 1:
                dates["end_date"] = fake.past_date(start_date=dates["start_date"])

            activity = await ActivityFactory.persist(
                db_session, location_id=location.id, **dates
            )
            task = await TaskFactory.persist(
                db_session,
                location_id=location.id,
                activity_id=activity.id,
                library_task_id=library_task.id,
                **dates,
            )
            project_activities.append(activity)
            project_tasks.append(task)

    return SampleProject(
        library_task,
        project,
        locations[0],
        project_tasks[0],
        project_activities[0],
        locations,
        project_tasks,
        project_activities,
    )


@pytest.mark.asyncio
async def test_stochastic_location_total_task_risk_score(
    metrics_manager: RiskModelMetricsManager,
    configurations_manager: ConfigurationsManager,
    work_package_manager: WorkPackageManager,
    task_manager: TaskManager,
    activity_manager: ActivityManager,
    db_session: AsyncSession,
) -> None:
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "start_date": datetime.date(2022, 10, 1),
            "end_date": datetime.date(2022, 11, 1),
        },
    )

    tasks = await TaskFactory.persist_many(db_session, size=6, activity_id=activity.id)

    tenant_id = project.tenant_id
    location_id = location.id
    test_date = datetime.date(2022, 10, 1)
    await store(
        configurations_manager,
        TaskSpecificRiskScoreMetricConfig(
            type="STOCHASTIC_MODEL",
            thresholds=RankingThresholds(low=50, medium=150),
            weights=RankingWeight(low=2.0, medium=4.0, high=6.0),
        ),
        tenant_id,
    )
    task_scores = [30.0, 75.0, 225.0, 300.0, 150.0, 100.0]
    expected_value = 171.7857

    await asyncio.gather(
        *[
            StochasticTaskSpecificRiskScore.store(
                metrics_manager, task.id, test_date, task_scores[i]
            )
            for i, task in enumerate(tasks)
        ]
    )

    metric = StochasticLocationTotalTaskRiskScore(
        metrics_manager=metrics_manager,
        configurations_manager=configurations_manager,
        work_package_manager=work_package_manager,
        activity_manager=activity_manager,
        task_manager=task_manager,
        project_location_id=location_id,
        date=test_date,
    )

    await metric.run()

    actual = await StochasticLocationTotalTaskRiskScore.load(
        metrics_manager=metrics_manager,
        project_location_id=location_id,
        date=test_date,
    )

    assert actual.value == expected_value
