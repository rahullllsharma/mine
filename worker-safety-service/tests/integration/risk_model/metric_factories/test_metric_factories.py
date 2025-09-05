from collections import Counter
from typing import Any
from unittest import TestCase
from unittest.mock import Mock

import pendulum
import pytest

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TaskFactory,
    WorkPackageFactory,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.risk_model.riskmodelreactor import (
    ForEachProjectLocationInTheSystem,
    ForEachTaskInTheSystem,
    MetricCalculation,
    OnTheDateWindow,
)


@pytest.mark.asyncio
async def test_for_each_task_in_the_system(
    db_session: AsyncSession,
) -> None:
    test = TestCase()

    today = pendulum.today().date()

    # Test_1 Date is not provided
    metric_calculation = Mock(spec=MetricCalculation)
    factory: Any = ForEachTaskInTheSystem(metric_calculation)
    with test.assertRaises(Exception):
        await factory.unwrap(None)

    half_point = pendulum.today().add(days=5).date()
    end_date = pendulum.today().add(days=15).date()
    activities = [
        await ActivityFactory.persist(db_session, start_date=today, end_date=end_date),
        await ActivityFactory.persist(
            db_session, start_date=today, end_date=half_point
        ),
        await ActivityFactory.persist(
            db_session, start_date=half_point, end_date=end_date
        ),
    ]
    tasks = [
        await TaskFactory.persist(
            db_session, start_date=today, end_date=end_date, activity=activities[0]
        ),
        await TaskFactory.persist(
            db_session, start_date=today, end_date=half_point, activity=activities[1]
        ),
        await TaskFactory.persist(
            db_session, start_date=half_point, end_date=end_date, activity=activities[2]
        ),
    ]

    # Test_2 Date is provided in parent metric
    metric_calculation = Mock(spec=MetricCalculation)
    metric_calculation.date = today
    factory = ForEachTaskInTheSystem(metric_calculation)
    ret = await factory.unwrap(metric_calculation)
    counter = Counter([f.keywords.get("project_task_id") for f in ret])
    test.assertEqual(counter[tasks[0].id], 1)
    test.assertEqual(counter[tasks[1].id], 1)

    # Test_3 With normal usage
    metric_calculation = Mock(spec=MetricCalculation)
    factory = OnTheDateWindow(ForEachTaskInTheSystem(metric_calculation))
    ret = await factory.unwrap(None)
    counter = Counter([f.keywords.get("project_task_id") for f in ret])
    test.assertEqual(counter[tasks[0].id], 15)
    test.assertEqual(counter[tasks[1].id], 6)
    test.assertEqual(counter[tasks[2].id], 10)
    # TODO: Could check by date


@pytest.mark.asyncio
async def test_for_each_project_location_in_the_system(
    db_session: AsyncSession,
) -> None:
    test = TestCase()

    today = pendulum.today().date()

    # Test_1 Date is not provided
    metric_calculation = Mock(spec=MetricCalculation)
    factory: Any = ForEachProjectLocationInTheSystem(metric_calculation)
    with test.assertRaises(Exception):
        await factory.unwrap(None)

    half_point = pendulum.today().add(days=5).date()
    end_date = pendulum.today().add(days=15).date()
    projects = [
        await WorkPackageFactory.persist(
            db_session, start_date=today, end_date=end_date
        ),
        await WorkPackageFactory.persist(
            db_session, start_date=today, end_date=half_point
        ),
        await WorkPackageFactory.persist(
            db_session, start_date=half_point, end_date=end_date
        ),
    ]

    project_locations = []
    for project in projects:
        project_locations.extend(
            await LocationFactory.persist_many(
                db_session, project_id=project.id, size=3
            )
        )

    # Test_2 Date is provided in parent metric
    metric_calculation = Mock(spec=MetricCalculation)
    metric_calculation.date = today
    factory = ForEachProjectLocationInTheSystem(metric_calculation)
    ret = await factory.unwrap(metric_calculation)
    counter = Counter([f.keywords.get("project_location_id") for f in ret])
    for location in project_locations:
        # Expect locations from the 3rd project not to be present
        expected = 0 if location.project_id == projects[2].id else 1
        test.assertEqual(counter[location.id], expected)

    # Test_3 With normal usage
    metric_calculation = Mock(spec=MetricCalculation)
    factory = OnTheDateWindow(ForEachProjectLocationInTheSystem(metric_calculation))
    ret = await factory.unwrap(None)
    counter = Counter([f.keywords.get("project_location_id") for f in ret])
    expect = {
        projects[0].id: 15,
        projects[1].id: 6,
        projects[2].id: 10,
    }
    for location in project_locations:
        # Expect locations from the 3rd project not to be present
        assert location.project_id
        test.assertEqual(counter[location.id], expect[location.project_id])
    # TODO: Could check by date
