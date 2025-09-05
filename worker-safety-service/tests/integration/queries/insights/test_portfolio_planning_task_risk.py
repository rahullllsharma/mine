import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import pytest

import worker_safety_service.utils as utils
from tests.factories import (
    ContractorFactory,
    LibraryDivisionFactory,
    LibraryRegionFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import (
    AsyncSession,
    Contractor,
    LibraryDivision,
    LibraryRegion,
    ProjectStatus,
    RiskLevel,
    Task,
    WorkPackage,
)

from .helpers import batch_create_risk_score, to_portfolio_input

################################################################################
# Test Query and helper

task_risk_by_date = """
query TestQuery($filter: PortfolioPlanningInput!, $orderBy: [TaskOrderBy!]) {
  portfolioPlanning(portfolioPlanningInput: $filter) {
    taskRiskLevelByDate (orderBy: $orderBy) {
      task {
        id name status startDate endDate
        libraryTask { category }

        location {
          id name
          project { id name }
        }
      }
      taskName
      locationName
      projectName
      riskLevelByDate {
        date riskLevel
      }
    }
  }
}
"""


async def execute_task_risk_by_date(
    execute_gql: ExecuteGQL,
    order_by: list[dict[str, Any]] | None = None,
    user: Any = None,
    **filters: Any,
) -> Any:
    variables: dict[str, Any] = {"filter": to_portfolio_input(**filters)}
    if order_by:
        variables["orderBy"] = order_by

    data = await execute_gql(
        query=task_risk_by_date,
        variables=variables,
        user=user,
    )
    return data["portfolioPlanning"]["taskRiskLevelByDate"]


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
    order_by: list[dict[str, Any]] | None = None,
    user: Any = None,
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_task_risk_over_time` where the PlanningInput
    filter is built.
    """

    task_risks = await execute_task_risk_by_date(
        execute_gql, order_by=order_by, user=user, **filters
    )

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
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_project_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A basic test for the task_risk query.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    filters = dict(start_date=day1, end_date=day3)

    # task1 on project1, task2 and task3 on project2
    task1, project1, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=filters,
    )
    task2, project2, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=filters,
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        project=project2,
        task_kwargs=filters,
    )

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

    # fetch for all projects
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            **expected_task1_risk,
            **expected_task2_risk,
            **expected_task3_risk,
        },
    )

    # fetch for project 1
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "project_ids": [project1.id],
        },
        expected_data=expected_task1_risk,
    )

    # fetch for project 2
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "project_ids": [project2.id],
        },
        expected_data={**expected_task2_risk, **expected_task3_risk},
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_task_risk_ignore_other_tenants(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    other_tenant = await TenantFactory.persist(db_session)
    other_tenant_project = await WorkPackageFactory.persist(
        db_session, tenant_id=other_tenant.id
    )

    task_kwargs = {"start_date": day1, "end_date": day3}
    task1, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
        project_kwargs={"tenant_id": tenant.id},
    )
    (
        other_tenant_task,
        _,
        _,
    ) = await TaskFactory.with_project_and_location(
        db_session, project=other_tenant_project, task_kwargs=task_kwargs
    )

    filters = dict(start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (300, other_tenant_task.id)],
            day2: [(350, task1.id), (200, other_tenant_task.id)],
            day3: [(300, task1.id), (100, other_tenant_task.id)],
        },
    )
    expected_task1_risk = {
        task1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.HIGH.name,
            day3: RiskLevel.HIGH.name,
        },
    }

    # don't specify projects, should only show task1 risk
    await assert_task_risk_by_date(
        execute_gql,
        user=admin,
        filters=filters,
        expected_data=expected_task1_risk,
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_ignore_archived_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task_kwargs = {"start_date": day1, "end_date": day3}
    task1, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
    )
    task2, project2, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
    )
    filters = dict(start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (300, task2.id)],
            day2: [(350, task1.id), (200, task2.id)],
            day3: [(300, task1.id), (100, task2.id)],
        },
    )

    project2.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    expected_task1_risk = {
        task1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.HIGH.name,
            day3: RiskLevel.HIGH.name,
        },
    }

    # don't specify projects, should only show task1 risk
    await assert_task_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data=expected_task1_risk,
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_date_filtering(
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
    task1, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
    )
    task2, project2, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs=task_kwargs,
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        project=project2,
        task_kwargs=task_kwargs,
    )

    filters = dict(start_date=day1, end_date=day3)

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
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_date_filtering_task_ranges(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Ensures tasks overlapping with the passed start/end date are
    filtered/included properly.
    """
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    # days 1 - 3
    new_tasks = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"task_kwargs": {"start_date": day1, "end_date": day3}},
            {"task_kwargs": {"start_date": day1, "end_date": day1}},
            {"task_kwargs": {"start_date": day1, "end_date": day2}},
            {"task_kwargs": {"start_date": day2, "end_date": day3}},
            {"task_kwargs": {"start_date": day3, "end_date": day3}},
        ],
    )
    task1, task2, task3, task4, task5 = [i[0] for i in new_tasks]

    tasks = [task1, task2, task3, task4, task5]

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
        filters={"start_date": day1, "end_date": day3},
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
        filters={"start_date": day1, "end_date": day1},
        expected_data=expected_risk([task1, task2, task3], [day1]),
    )

    # fetch for the second day
    await assert_task_risk_by_date(
        execute_gql,
        filters={"start_date": day2, "end_date": day2},
        expected_data=expected_risk([task1, task3, task4], [day2]),
    )

    # fetch for the third day
    await assert_task_risk_by_date(
        execute_gql,
        filters={"start_date": day3, "end_date": day3},
        expected_data=expected_risk([task1, task4, task5], [day3]),
    )

    # fetch for the first two
    await assert_task_risk_by_date(
        execute_gql,
        filters={"start_date": day1, "end_date": day2},
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
        filters={"start_date": day2, "end_date": day3},
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
async def test_portfolio_planning_task_risk_multiple_calcs_same_day(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates multiple scores on the same day for the same location.
    Only the latest calculated score, per day, per location should be counted.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        task_kwargs={"start_date": day1, "end_date": day3},
    )

    filters = dict(start_date=day1, end_date=day3)

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
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_project_status_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    project_active: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        status=ProjectStatus.ACTIVE,
    )
    project_completed: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        status=ProjectStatus.COMPLETED,
    )

    task_kwargs = {"start_date": day1, "end_date": day2}
    task_active, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        project=project_active,
        task_kwargs=task_kwargs,
    )
    task_completed, _, _ = await TaskFactory.with_project_and_location(
        db_session,
        project=project_completed,
        task_kwargs=task_kwargs,
    )
    tasks = [task_active, task_completed]

    filters = dict(start_date=day1, end_date=day2)

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    def expected_risk(
        tasks: list[Task], days: list[datetime]
    ) -> dict[uuid.UUID, dict[datetime, str]]:
        return {task.id: {day: RiskLevel.MEDIUM.name for day in days} for task in tasks}

    # fetch for active and completed statuses
    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "statuses": [ProjectStatus.ACTIVE.name, ProjectStatus.COMPLETED.name],
        },
        expected_data=expected_risk(tasks, days),
    )

    # fetch for active only statuses
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "statuses": [ProjectStatus.ACTIVE.name]},
        expected_data=expected_risk([task_active], days),
    )

    # fetch for completed only statuses
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "statuses": [ProjectStatus.COMPLETED.name]},
        expected_data=expected_risk([task_completed], days),
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_task_risk_region_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    region1: LibraryRegion = await LibraryRegionFactory.persist(db_session)
    project_region1: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        region_id=region1.id,
    )
    region2: LibraryRegion = await LibraryRegionFactory.persist(db_session)
    project_region2: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        region_id=region2.id,
    )

    task_kwargs = {"start_date": day1, "end_date": day2}
    task_region1, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_region1, task_kwargs=task_kwargs
    )
    task_region2, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_region2, task_kwargs=task_kwargs
    )
    tasks = [task_region1, task_region2]

    filters = dict(start_date=day1, end_date=day2)

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    def expected_risk(
        tasks: list[Task], days: list[datetime]
    ) -> dict[uuid.UUID, dict[datetime, str]]:
        return {task.id: {day: RiskLevel.MEDIUM.name for day in days} for task in tasks}

    # fetch for both regions
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "region_ids": [region1.id, region2.id]},
        expected_data=expected_risk(tasks, days),
    )

    # fetch for region1
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "region_ids": [region1.id]},
        expected_data=expected_risk([task_region1], days),
    )

    # fetch for region2
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "region_ids": [region2.id]},
        expected_data=expected_risk([task_region2], days),
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_division_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    division1: LibraryDivision = await LibraryDivisionFactory.persist(db_session)
    project_division1: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        division_id=division1.id,
    )
    division2: LibraryDivision = await LibraryDivisionFactory.persist(db_session)
    project_division2: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        division_id=division2.id,
    )

    task_kwargs = {"start_date": day1, "end_date": day2}
    task_division1, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_division1, task_kwargs=task_kwargs
    )
    task_division2, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_division2, task_kwargs=task_kwargs
    )
    tasks = [task_division1, task_division2]

    filters = dict(start_date=day1, end_date=day2)

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    def expected_risk(
        tasks: list[Task], days: list[datetime]
    ) -> dict[uuid.UUID, dict[datetime, str]]:
        return {task.id: {day: RiskLevel.MEDIUM.name for day in days} for task in tasks}

    # fetch for both divisions
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "division_ids": [division1.id, division2.id]},
        expected_data=expected_risk(tasks, days),
    )

    # fetch for division1
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "division_ids": [division1.id]},
        expected_data=expected_risk([task_division1], days),
    )

    # fetch for division2
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "division_ids": [division2.id]},
        expected_data=expected_risk([task_division2], days),
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_task_risk_contractor_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    contractor1: Contractor = await ContractorFactory.persist(db_session)
    project_contractor1: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        contractor_id=contractor1.id,
    )
    contractor2: Contractor = await ContractorFactory.persist(db_session)
    project_contractor2: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        contractor_id=contractor2.id,
    )

    task_kwargs = {"start_date": day1, "end_date": day2}
    task_contractor1, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_contractor1, task_kwargs=task_kwargs
    )
    task_contractor2, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project_contractor2, task_kwargs=task_kwargs
    )
    tasks = [task_contractor1, task_contractor2]

    filters = dict(start_date=day1, end_date=day2)

    await persist_test_data(
        db_session,
        {day: [(100, task.id) for task in tasks] for day in days},
    )

    def expected_risk(
        tasks: list[Task], days: list[datetime]
    ) -> dict[uuid.UUID, dict[datetime, str]]:
        return {task.id: {day: RiskLevel.MEDIUM.name for day in days} for task in tasks}

    # fetch for both contractors
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "contractor_ids": [contractor1.id, contractor2.id]},
        expected_data=expected_risk(tasks, days),
    )

    # fetch for contractor1
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "contractor_ids": [contractor1.id]},
        expected_data=expected_risk([task_contractor1], days),
    )

    # fetch for contractor2
    await assert_task_risk_by_date(
        execute_gql,
        filters={**filters, "contractor_ids": [contractor2.id]},
        expected_data=expected_risk([task_contractor2], days),
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_sorting_by_project_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests the sort order of locationRiskByDate's return - it should by location name.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task_kwargs = {"start_date": day1, "end_date": day3}
    (
        (task1, *_),
        (task2, *_),
        (task3, *_),
    ) = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"project_kwargs": {"name": "á 1"}, "task_kwargs": task_kwargs},
            {"project_kwargs": {"name": "A 2"}, "task_kwargs": task_kwargs},
            {"project_kwargs": {"name": "a 3"}, "task_kwargs": task_kwargs},
        ],
    )
    filters = dict(
        start_date=day1,
        end_date=day3,
    )

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )
    expected_order = [str(task1.id), str(task2.id), str(task3.id)]

    # Check project name ASC order
    tasks = await execute_task_risk_by_date(
        execute_gql,
        order_by=[{"field": "PROJECT_NAME", "direction": "ASC"}],
        **filters,
    )
    assert expected_order == [i["task"]["id"] for i in tasks]

    # Check project name DESC order
    tasks = await execute_task_risk_by_date(
        execute_gql,
        order_by=[{"field": "PROJECT_NAME", "direction": "DESC"}],
        **filters,
    )
    assert list(reversed(expected_order)) == [i["task"]["id"] for i in tasks]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_sorting_by_project_location_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests the sort order of locationRiskByDate's return - it should by location name.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    filters = dict(start_date=day1, end_date=day3)

    (
        (task1, *_),
        (task2, *_),
        (task3, *_),
    ) = await TaskFactory.batch_with_project_and_location(
        db_session,
        [
            {"location_kwargs": {"name": "á 1"}, "task_kwargs": filters},
            {"location_kwargs": {"name": "A 2"}, "task_kwargs": filters},
            {"location_kwargs": {"name": "a 3"}, "task_kwargs": filters},
        ],
    )

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )
    expected_order = [str(task1.id), str(task2.id), str(task3.id)]

    # Check project name ASC order
    tasks = await execute_task_risk_by_date(
        execute_gql,
        order_by=[{"field": "PROJECT_LOCATION_NAME", "direction": "ASC"}],
        **filters,
    )
    assert expected_order == [i["task"]["id"] for i in tasks]

    # Check project name DESC order
    tasks = await execute_task_risk_by_date(
        execute_gql,
        order_by=[{"field": "PROJECT_LOCATION_NAME", "direction": "DESC"}],
        **filters,
    )
    assert list(reversed(expected_order)) == [i["task"]["id"] for i in tasks]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_task_risk_respects_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure task risk levels that are outside of task start/end date are not
    returned.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    task1, _, _ = await TaskFactory.with_project_and_location(
        db_session, task_kwargs={"start_date": day1, "end_date": day2}
    )
    task2, project2, _ = await TaskFactory.with_project_and_location(
        db_session, task_kwargs={"start_date": day2, "end_date": day3}
    )
    task3, _, _ = await TaskFactory.with_project_and_location(
        db_session, project=project2, task_kwargs={"start_date": day1, "end_date": day2}
    )

    filters = dict(start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(84, task1.id), (105, task2.id), (300, task3.id)],
            day2: [(350, task1.id), (80, task2.id), (200, task3.id)],
            day3: [(300, task1.id), (150, task2.id), (100, task3.id)],
        },
    )

    await assert_task_risk_by_date(
        execute_gql,
        filters={
            **filters,
        },
        expected_data={
            task1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
                # no day3
            },
            task2.id: {
                # no day1
                day2: RiskLevel.LOW.name,
                day3: RiskLevel.MEDIUM.name,
            },
            task3.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
                # no day 3
            },
        },
    )
