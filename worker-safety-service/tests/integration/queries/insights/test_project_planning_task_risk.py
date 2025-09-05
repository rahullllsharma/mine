import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import pytest

import worker_safety_service.utils as utils
from tests.factories import ActivityFactory, TaskFactory, WorkPackageFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, RiskLevel, Task

from .helpers import batch_create_risk_score, to_project_input

################################################################################
# Test Query and helper

task_risk_by_date = """
query TestQuery($filter: ProjectPlanningInput!, $task_order_by: [TaskOrderBy!]) {
  projectPlanning(projectPlanningInput: $filter) {
    taskRiskLevelByDate(orderBy: $task_order_by) {
      taskName
      locationName
      projectName
      task {
        id name status startDate endDate
        libraryTask { name category }

        location { id name project { id name } }
      }
      riskLevelByDate {
        date riskLevel
      }
    }
  }
}
"""


async def execute_task_risk_by_date(
    execute_gql: ExecuteGQL,
    task_order_by: list[dict[str, Any]] | None = None,
    **filters: Any
) -> Any:
    vs = to_project_input(**filters)

    variables: dict[str, Any] = {"filter": vs}
    if task_order_by:
        variables["task_order_by"] = task_order_by

    data = await execute_gql(query=task_risk_by_date, variables=variables)
    location_risks = data["projectPlanning"]["taskRiskLevelByDate"]
    return location_risks


async def persist_test_data(
    session: AsyncSession, test_data: dict[datetime, list[Tuple[int, uuid.UUID]]]
) -> None:
    await batch_create_risk_score(
        session,
        [
            {"day": day, "score": score, "task_id": _id}
            for day, scores in test_data.items()
            for score, _id in scores
        ],
    )


async def assert_task_risk_by_date(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[uuid.UUID, Dict[datetime, str]],
    log: bool = False,
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_task_risk_over_time` where the PlanningInput
    filter is built.
    """

    task_risks = await execute_task_risk_by_date(execute_gql, **filters)

    expected_task_ids = {str(id) for id in expected_data.keys()}
    expected_data_str_keys = {
        str(id): {d.strftime("%Y-%m-%d"): level for d, level in level_by_date.items()}
        for id, level_by_date in expected_data.items()
    }

    by_id = lambda pr: pr["task"]["id"]  # noqa: E731
    task_risks_by_id = utils.groupby(task_risks, key=by_id)

    if log:
        print("\nreturned data", task_risks_by_id)
        print("\nexpected_data", expected_data_str_keys)

    # make sure only the expected dates are returned
    assert set(task_risks_by_id.keys()) == expected_task_ids

    for task_id, fetched_task_and_riskses in task_risks_by_id.items():
        assert len(fetched_task_and_riskses) == 1  # sanity check
        fetched_task_and_risks = fetched_task_and_riskses[0]
        expected_level_by_date = expected_data_str_keys[task_id]

        # if we expect no data, make sure there isn't any
        if not expected_level_by_date:
            assert not fetched_task_and_risks["riskLevelByDate"]

        task_data = fetched_task_and_risks["task"]

        assert task_data["name"] == fetched_task_and_risks["taskName"]

        # make sure location data was fetched
        location_data = fetched_task_and_risks["task"]["location"]
        assert location_data["name"]
        assert location_data["name"] == fetched_task_and_risks["locationName"]

        # make sure project data was fetched
        project_data = location_data["project"]
        assert project_data["name"]
        assert project_data["name"] == fetched_task_and_risks["projectName"]

        if expected_level_by_date:
            fetched_risk_levels = fetched_task_and_risks["riskLevelByDate"]
            assert fetched_risk_levels

            by_date = lambda pr: pr["date"]  # noqa: E731
            risk_levels_by_date = utils.groupby(fetched_risk_levels, key=by_date)

            # make sure only our expected dates are included
            assert set(expected_level_by_date.keys()) == set(risk_levels_by_date.keys())

            # finally, make sure each data and riskLevel are as expected
            for date, expected_level in expected_level_by_date.items():
                levels_for_date = risk_levels_by_date[date]
                assert len(levels_for_date) == 1  # sanity check
                level_for_date = levels_for_date[0]
                actual_risk_level = level_for_date["riskLevel"]
                assert expected_level == actual_risk_level


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_planning_task_risk_location_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A basic test for the location_risk query, that uses only one location
    and a few dates with one score each.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task_kwargs = {"start_date": day1, "end_date": day3}
    # task1 on location1, task2 and task3 on location2
    (
        task1,
        project,
        location1,
    ) = await TaskFactory.with_project_and_location(db_session, task_kwargs=task_kwargs)
    task2, _, location2 = await TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs=task_kwargs
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project, location=location2, task_kwargs=task_kwargs
    )

    filters = dict(project_id=project.id, **task_kwargs)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )
    expected_task1_risk = {
        task1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.HIGH.name,
            day3: RiskLevel.HIGH.name,
        },
    }
    expected_task2_risk = {
        task2.id: {
            day1: RiskLevel.MEDIUM.name,
            day2: RiskLevel.LOW.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }
    expected_task3_risk = {
        task3.id: {
            day1: RiskLevel.HIGH.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }

    # fetch for all locations on this project
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            **expected_task1_risk,
            **expected_task2_risk,
            **expected_task3_risk,
        },
    )

    # fetch for both locations
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            **expected_task1_risk,
            **expected_task2_risk,
            **expected_task3_risk,
        },
    )

    # fetch for location 1
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id],
        },
        expected_data=expected_task1_risk,
    )

    # fetch for location 2
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location2.id],
        },
        expected_data={**expected_task2_risk, **expected_task3_risk},
    )

    # archive location 1
    location1.archived_at = datetime.now(timezone.utc)
    await db_session.commit()
    await db_session.refresh(location1)

    # fetch for all project locations, assert the archived location is not present
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={**expected_task2_risk, **expected_task3_risk},
    )

    # explicitly fetch with all locations, including the archived location
    vs = {
        "projectId": project.id,
        "startDate": day1.date(),
        "endDate": day3.date(),
        "locationIds": [location1.id, location2.id],
    }
    data = await execute_gql(
        query=task_risk_by_date, variables={"filter": vs}, raw=True
    )
    # archived location id is no longer valid, reject the request
    assert data.json().get("errors"), "invalid location_id"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_planning_task_risk_date_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that date filtering via start_date and end_date limits the
    data returned.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task_kwargs = {"start_date": day1, "end_date": day3}
    task1, project, _ = await TaskFactory.with_project_and_location(
        db_session, task_kwargs=task_kwargs
    )
    task2, _, location2 = await TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs=task_kwargs
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project, location=location2, task_kwargs=task_kwargs
    )

    filters = dict(project_id=project.id, start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )
    expected_task1_risk = {
        task1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.HIGH.name,
            day3: RiskLevel.HIGH.name,
        },
    }
    expected_task2_risk = {
        task2.id: {
            day1: RiskLevel.MEDIUM.name,
            day2: RiskLevel.LOW.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }
    expected_task3_risk = {
        task3.id: {
            day1: RiskLevel.HIGH.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }

    # fetch for the full date-range
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            **expected_task1_risk,
            **expected_task2_risk,
            **expected_task3_risk,
        },
    )

    # fetch for the first day
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "end_date": day1},
        expected_data={
            task1.id: {
                day1: RiskLevel.LOW.name,
            },
            task2.id: {
                day1: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day1: RiskLevel.HIGH.name,
            },
        },
    )

    # fetch for the last day
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day3},
        expected_data={
            task1.id: {
                day3: RiskLevel.HIGH.name,
            },
            task2.id: {
                day3: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day3: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for the first two days
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "end_date": day2},
        expected_data={
            task1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            task2.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.LOW.name,
            },
            task3.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )
    # fetch for the last two days
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day2, "end_date": day3},
        expected_data={
            task1.id: {
                day2: RiskLevel.HIGH.name,
                day3: RiskLevel.HIGH.name,
            },
            task2.id: {
                day2: RiskLevel.LOW.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_planning_task_risk_date_filtering_task_ranges(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Ensures tasks overlapping with the passed start/end date are
    filtered/included properly.
    """

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    project = await WorkPackageFactory.persist(db_session)
    (
        (task1, _, _),
        (task2, _, _),
        (task3, _, _),
        (task4, _, _),
        (task5, _, _),
    ) = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project, "task_kwargs": {"start_date": day1, "end_date": day3}},
            {"project": project, "task_kwargs": {"start_date": day1, "end_date": day1}},
            {"project": project, "task_kwargs": {"start_date": day1, "end_date": day2}},
            {"project": project, "task_kwargs": {"start_date": day2, "end_date": day3}},
            {"project": project, "task_kwargs": {"start_date": day3, "end_date": day3}},
        ],
    )
    tasks = [task1, task2, task3, task4, task5]

    filters = dict(project_id=project.id)

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    def expected_risk(
        tasks: list[Task], days: list[datetime]
    ) -> dict[uuid.UUID, dict[datetime, str]]:
        return {task.id: {day: RiskLevel.MEDIUM.name for day in days} for task in tasks}

    # fetch for the full date-range
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day1, "end_date": day3},
        expected_data={
            task1.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task2.id: {
                day1: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
            },
            task4.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task5.id: {
                day3: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for the first day
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day1, "end_date": day1},
        expected_data=expected_risk([task1, task2, task3], [day1]),
    )

    # fetch for the second day
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day2, "end_date": day2},
        expected_data=expected_risk([task1, task3, task4], [day2]),
    )

    # fetch for the third day
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day3, "end_date": day3},
        expected_data=expected_risk([task1, task4, task5], [day3]),
    )

    # fetch for the first two
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day1, "end_date": day2},
        expected_data={
            task1.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
            },
            task2.id: {
                day1: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
            },
            task4.id: {
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for the last two
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day2, "end_date": day3},
        expected_data={
            task1.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day2: RiskLevel.MEDIUM.name,
            },
            task4.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task5.id: {
                day3: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_planning_task_risk_multiple_calcs_same_day(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates multiple scores on the same day for the same location.
    Only the latest calculated score, per day, per location should be counted.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task, project, _ = await TaskFactory.with_project_and_location(
        db_session, task_kwargs={"start_date": day1, "end_date": day3}
    )

    filters = dict(start_date=day1, end_date=day3, project_id=project.id)

    await persist_test_data(
        db_session,
        {
            day1: [(99, task.id), (4, task.id), (105, task.id)],
            day2: [(100, task.id), (290, task.id), (105, task.id)],
            day3: [(249, task.id), (250, task.id)],
        },
    )

    # fetch for all locations on this project
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            task.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            }
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_planning_task_risk_sorting(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests the sort order of taskRiskByDate, which should sort by location name,
    then task name.
    """

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days
    task_kwargs = {"start_date": day1, "end_date": day2}

    task1, project, _ = await TaskFactory.with_project_and_location(
        db_session, task_kwargs=task_kwargs, location_kwargs={"name": "Alexandria"}
    )
    task2, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
        project=project,
        location_kwargs={"name": "Boston"},
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
        project=project,
        location_kwargs={"name": "Zoo Zealand"},
    )
    tasks = [task1, task2, task3]

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    expected_order = tasks
    expected_id_order = [str(p.id) for p in expected_order]

    task_risks = await execute_task_risk_by_date(
        execute_gql,
        start_date=days[0],
        end_date=days[-1],
        project_id=project.id,
        task_order_by=[
            dict(field="PROJECT_LOCATION_NAME", direction="ASC"),
            dict(field="CATEGORY", direction="ASC"),
        ],
    )
    fetched_tasks = [task_risk["task"] for task_risk in task_risks]
    fetched_ids = [fetched["id"] for fetched in fetched_tasks]

    assert len(tasks) == len(fetched_tasks)
    assert fetched_ids == expected_id_order

    # test descending
    expected_order = [task3, task2, task1]
    expected_id_order = [str(p.id) for p in expected_order]

    task_risks = await execute_task_risk_by_date(
        execute_gql,
        start_date=days[0],
        end_date=days[-1],
        project_id=project.id,
        task_order_by=[
            dict(field="PROJECT_LOCATION_NAME", direction="DESC"),
            dict(field="CATEGORY", direction="DESC"),
        ],
    )
    fetched_tasks = [task_risk["task"] for task_risk in task_risks]
    fetched_ids = [fetched["id"] for fetched in fetched_tasks]

    assert len(tasks) == len(fetched_tasks)
    assert fetched_ids == expected_id_order


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_planning_task_risk_respects_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure task risk levels that are outside of task start/end date are not
    returned.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day1, "end_date": day3}
    )

    task1 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day1,
        end_date=day2,
        activity=activity,
        location=location,
    )
    task2 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day2,
        end_date=day3,
        activity=activity,
        location=location,
    )
    task3 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day1,
        end_date=day2,
        activity=activity,
        location=location,
    )

    filters = dict(project_id=project.id, start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )

    # fetch for all locations on this project
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            task1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            task2.id: {
                day2: RiskLevel.LOW.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_planning_task_risk_respects_activity_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure task risk levels that are outside of task start/end date are not
    returned.
    """
    [day1, day2, day3, day4, day5] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(5)
    ]

    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day2, "end_date": day4}
    )

    t1 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day2,
        end_date=day4,
        activity=activity,
        location=location,
    )
    t2 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day2,
        end_date=day4,
        activity=activity,
        location=location,
    )
    t3 = await TaskFactory.persist(
        db_session,
        project=project,
        start_date=day2,
        end_date=day4,
        activity=activity,
        location=location,
    )

    (
        other_act,
        other_proj,
        other_loc,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day4, "end_date": day5}
    )
    ot1 = await TaskFactory.persist(
        db_session,
        project=other_proj,
        start_date=day4,
        end_date=day5,
        activity=other_act,
        location=other_loc,
    )
    ot2 = await TaskFactory.persist(
        db_session,
        project=other_proj,
        start_date=day4,
        end_date=day5,
        activity=other_act,
        location=other_loc,
    )
    ot3 = await TaskFactory.persist(
        db_session,
        project=other_proj,
        start_date=day4,
        end_date=day5,
        activity=other_act,
        location=other_loc,
    )

    filters = dict(project_id=project.id, start_date=day2, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [
                (84, t1.id),
                (75, t2.id),
                (105, t3.id),
                (222, ot1.id),
                (333, ot2.id),
                (444, ot3.id),
            ],
            day2: [
                (75, t1.id),
                (80, t2.id),
                (200, t3.id),
                (222, ot1.id),
                (333, ot2.id),
                (444, ot3.id),
            ],
            day3: [
                (105, t1.id),
                (150, t2.id),
                (333, t3.id),
                (222, ot1.id),
                (333, ot2.id),
                (444, ot3.id),
            ],
            day4: [
                (127, t1.id),
                (88, t2.id),
                (76, t3.id),
                (222, ot1.id),
                (333, ot2.id),
                (444, ot3.id),
            ],
            day5: [
                (230, t1.id),
                (280, t2.id),
                (330, t3.id),
                (222, ot1.id),
                (333, ot2.id),
                (444, ot3.id),
            ],
        },
    )

    # fetch for all locations on this project with activities with schedules overlapping the filter
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            t1.id: {
                day2: RiskLevel.LOW.name,
                day3: RiskLevel.MEDIUM.name,
            },
            t2.id: {
                day2: RiskLevel.LOW.name,
                day3: RiskLevel.MEDIUM.name,
            },
            t3.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
        },
    )
