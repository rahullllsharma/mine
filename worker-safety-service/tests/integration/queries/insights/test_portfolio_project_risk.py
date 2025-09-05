import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Tuple

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
    WorkPackage,
)

from .helpers import (
    CountsByRiskLevel,
    batch_create_risk_score,
    risk_level_counts,
    to_portfolio_input,
)

################################################################################
# Test Query and helper

planning_project_risk_over_time = """
query TestQuery($filter: PortfolioPlanningInput!) {
  portfolioPlanning(portfolioPlanningInput: $filter) {
    projectRiskLevelOverTime {
      date
      riskLevel
      count
    }
  }
}
"""

learnings_project_risk_over_time = """
query TestQuery($filter: PortfolioLearningsInput!) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    projectRiskLevelOverTime {
      date
      riskLevel
      count
    }
  }
}
"""

project_risk_by_date = """
query TestQuery($filter: PortfolioPlanningInput!) {
  portfolioPlanning(portfolioPlanningInput: $filter) {
    projectRiskLevelByDate {
      project {
        id name
      }
      projectName
      riskLevelByDate {
        date riskLevel
      }
    }
  }
}
"""


async def execute_planning_project_risk_over_time(
    execute_gql: ExecuteGQL, user: Any, **filters: Any
) -> Any:
    data = await execute_gql(
        user=user,
        query=planning_project_risk_over_time,
        variables={"filter": to_portfolio_input(**filters)},
    )
    proj_risks = data["portfolioPlanning"]["projectRiskLevelOverTime"]
    return proj_risks


async def execute_learnings_project_risk_over_time(
    execute_gql: ExecuteGQL, user: Any, **filters: Any
) -> Any:
    data = await execute_gql(
        user=user,
        query=learnings_project_risk_over_time,
        variables={"filter": to_portfolio_input(**filters)},
    )
    proj_risks = data["portfolioLearnings"]["projectRiskLevelOverTime"]
    return proj_risks


async def execute_project_risk_by_date(
    execute_gql: ExecuteGQL, user: Any = None, **filters: Any
) -> Any:
    data = await execute_gql(
        user=user,
        query=project_risk_by_date,
        variables={"filter": to_portfolio_input(**filters)},
    )
    proj_risks = data["portfolioPlanning"]["projectRiskLevelByDate"]
    return proj_risks


async def persist_test_data(
    session: AsyncSession, test_data: dict[datetime, list[Tuple[int, uuid.UUID]]]
) -> None:
    await batch_create_risk_score(
        session,
        [
            {"day": day, "score": score, "project_id": _id}
            for day, scores in test_data.items()
            for score, _id in scores
        ],
    )


def assert_project_risk_over_time_results(
    expected_data: dict[datetime, CountsByRiskLevel],
    risk_counts: list[dict],
) -> None:
    expected_dates = {d.strftime("%Y-%m-%d") for d in expected_data.keys()}
    expected_data_str_keys = {
        d.strftime("%Y-%m-%d"): risk_level_counts(v) for d, v in expected_data.items()
    }

    keyfunc = lambda pr: pr["date"]  # noqa: E731
    risk_by_date = utils.groupby(risk_counts, key=keyfunc)

    # make sure only the expected dates are returned
    assert set(risk_by_date.keys()) == expected_dates

    for date, fetched_risks in risk_by_date.items():
        for risk_count in fetched_risks:
            risk_level = risk_count["riskLevel"]
            expected_count = expected_data_str_keys[date][risk_level]
            assert risk_count["count"] == expected_count


async def assert_project_risk(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[datetime, CountsByRiskLevel],
    user: Any = None,
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_project_risk_over_time` where the PlanningInput
    filter is built.
    """

    # test for planning side
    risk_counts = await execute_planning_project_risk_over_time(
        execute_gql, user, **filters
    )
    assert_project_risk_over_time_results(expected_data, risk_counts)

    # test for learnings side
    risk_counts = await execute_learnings_project_risk_over_time(
        execute_gql, user, **filters
    )
    assert_project_risk_over_time_results(expected_data, risk_counts)


async def assert_project_risk_by_date(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[uuid.UUID, dict[datetime, str]],
    user: Any = None,
    log: bool = False,
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_project_risk_by_date` where the PlanningInput
    filter is built.
    """

    project_risks = await execute_project_risk_by_date(execute_gql, user, **filters)

    expected_project_ids = {str(id) for id in expected_data.keys()}
    expected_data_str_keys = {
        str(id): {d.strftime("%Y-%m-%d"): level for d, level in level_by_date.items()}
        for id, level_by_date in expected_data.items()
    }

    by_id = lambda pr: pr["project"]["id"]  # noqa: E731
    project_risks_by_id = utils.groupby(project_risks, key=by_id)

    if log:
        print("\nreturned data", project_risks_by_id)
        print("\nexpected_data", expected_data_str_keys)

    # make sure only the expected dates are returned
    assert set(project_risks_by_id.keys()) == expected_project_ids

    for project_id, fetched_project_and_riskses in project_risks_by_id.items():
        assert len(fetched_project_and_riskses) == 1  # sanity check
        fetched_project_and_risks = fetched_project_and_riskses[0]
        expected_level_by_date = expected_data_str_keys[project_id]

        # if we expect no data, make sure there isn't any
        if not expected_level_by_date:
            assert not fetched_project_and_risks["riskLevelByDate"]

        project_data = fetched_project_and_risks["project"]
        assert project_data["name"] == fetched_project_and_risks["projectName"]

        if expected_level_by_date:
            fetched_risk_levels = fetched_project_and_risks["riskLevelByDate"]
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
async def test_portfolio_planning_project_risk_basic(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A basic test for the projectRiskLevelOverTime query.
    Ensures filtering with project_ids works.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    filters = dict(start_date=day1, end_date=day3)

    projects: list[WorkPackage] = await WorkPackageFactory.persist_many(
        db_session, size=2, **filters  # type: ignore
    )
    [project1, project2] = projects

    for project in projects:
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(99, project1.id), (105, project2.id)],
            day2: [(100, project1.id), (105, project2.id)],
            day3: [(250, project1.id), (99, project2.id)],
        },
    )

    # fetch for all projects
    await assert_project_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.LOW.name: 1, RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
            project2.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )

    # fetch for project1
    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, project_ids=[project1.id]),
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(**filters, project_ids=[project1.id]),
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
        },
    )

    # fetch for project2
    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, project_ids=[project2.id]),
        expected_data={
            day1: {RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.LOW.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(**filters, project_ids=[project2.id]),
        expected_data={
            project2.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_multiple_calcs_same_day(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Make sure projectRiskLevelOverTime returns only one score per project per day.
    Creates several scores for the same project on the same day.
    Only the last score for each day should be considered.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    filters = dict(
        start_date=day1,
        end_date=day3,
    )
    project: WorkPackage = await WorkPackageFactory.persist(db_session, **filters)

    await TaskFactory.with_project_and_location(
        db_session, project=project, task_kwargs=filters
    )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(92, project.id), (96, project.id), (90, project.id)],
            day2: [
                (90, project.id),
                (100, project.id),
                (110, project.id),
                (111, project.id),
            ],
            day3: [
                (90, project.id),
                (243, project.id),
                (249, project.id),
                (249, project.id),
            ],
        },
    )

    expected_data = {
        day1: {RiskLevel.LOW.name: 1},
        day2: {RiskLevel.MEDIUM.name: 1},
        day3: {RiskLevel.MEDIUM.name: 1},
    }

    # fetch for all projects
    await assert_project_risk(
        execute_gql,
        filters=filters,
        expected_data=expected_data,
    )

    await assert_project_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            project.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            }
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_project_risk_ignore_other_tenant_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    filters = dict(
        start_date=day1,
        end_date=day3,
    )

    tenant, admin = await TenantFactory.new_with_admin(db_session)

    projects: list[WorkPackage] = await WorkPackageFactory.persist_many(
        db_session, size=2, tenant_id=tenant.id, **filters  # type: ignore
    )
    [project1, project2] = projects
    for project in projects:
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    other_tenant = await TenantFactory.persist(db_session)
    other_tenant_project = await WorkPackageFactory.persist(
        db_session, tenant_id=other_tenant.id, **filters
    )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [
                (99, project1.id),
                (105, project2.id),
                (350, other_tenant_project.id),
            ],
            day2: [
                (100, project1.id),
                (105, project2.id),
                (100, other_tenant_project.id),
            ],
            day3: [
                (250, project1.id),
                (99, project2.id),
                (100, other_tenant_project.id),
            ],
        },
    )

    expected_data = {
        day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
        day2: {RiskLevel.MEDIUM.name: 2},
        day3: {RiskLevel.LOW.name: 1, RiskLevel.HIGH.name: 1},
    }

    # don't specify projects, but expect only projects from our tenant
    await assert_project_risk(
        execute_gql,
        user=admin,
        filters=filters,
        expected_data=expected_data,
    )
    await assert_project_risk_by_date(
        execute_gql,
        user=admin,
        filters=filters,
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
            project2.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_ignore_archived_projects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    filters = dict(
        start_date=day1,
        end_date=day3,
    )

    projects: list[WorkPackage] = await WorkPackageFactory.persist_many(
        db_session, size=2, **filters  # type: ignore
    )
    [project1, project2] = projects

    for project in projects:
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(99, project1.id), (105, project2.id)],
            day2: [(100, project1.id), (105, project2.id)],
            day3: [(250, project1.id), (99, project2.id)],
        },
    )

    project2.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    expected_data = {
        day1: {RiskLevel.LOW.name: 1},
        day2: {RiskLevel.MEDIUM.name: 1},
        day3: {RiskLevel.HIGH.name: 1},
    }

    # don't specify projects, but expect only non-archived data to be returned
    await assert_project_risk(
        execute_gql,
        filters=filters,
        expected_data=expected_data,
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_sorting(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests the sort order of projectRiskByDate's return - it should by project name.
    """
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    filters = dict(
        start_date=days[0],
        end_date=days[-1],
    )

    project1 = await WorkPackageFactory.persist(
        db_session, name="Aaron Aarons", **filters
    )
    project2 = await WorkPackageFactory.persist(
        db_session, name="Bobby Bobberson", **filters
    )
    project3 = await WorkPackageFactory.persist(
        db_session, name="Calvin and Hobbes", **filters
    )
    projects = [project1, project2, project3]
    expected_project_order = projects
    expected_id_order = [str(p.id) for p in expected_project_order]

    for project in projects:
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    await persist_test_data(
        db_session, {day: [(100, project.id) for project in projects] for day in days}
    )

    project_risks = await execute_project_risk_by_date(execute_gql, **filters)
    fetched_projects = [proj_risk["project"] for proj_risk in project_risks]
    fetched_ids = [fetched["id"] for fetched in fetched_projects]

    assert len(projects) == len(fetched_projects)
    assert fetched_ids == expected_id_order


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_date_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Test filtering projectRiskLevelOverTime by start and end date.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    filters = dict(
        start_date=day1,
        end_date=day3,
    )

    projects: list[WorkPackage] = await WorkPackageFactory.persist_many(
        db_session, size=2, **filters  # type: ignore
    )
    [project1, project2] = projects

    for project in projects:
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(92, project1.id), (96, project2.id)],
            day2: [(100, project1.id), (110, project2.id)],
            day3: [(243, project1.id), (90, project2.id)],
        },
    )

    # fetch for all projects, all days
    await assert_project_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.LOW.name: 2},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            project2.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )

    # fetch for first day
    await assert_project_risk(
        execute_gql,
        filters=dict(
            start_date=day1,
            end_date=day1,
        ),
        expected_data={day1: {RiskLevel.LOW.name: 2}},
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            start_date=day1,
            end_date=day1,
        ),
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
            },
            project2.id: {
                day1: RiskLevel.LOW.name,
            },
        },
    )

    # fetch for first two days
    await assert_project_risk(
        execute_gql,
        filters=dict(
            start_date=day1,
            end_date=day2,
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 2},
            day2: {RiskLevel.MEDIUM.name: 2},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            start_date=day1,
            end_date=day2,
        ),
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
            project2.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for last two days
    await assert_project_risk(
        execute_gql,
        filters=dict(
            start_date=day2,
            end_date=day3,
        ),
        expected_data={
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            start_date=day2,
            end_date=day3,
        ),
        expected_data={
            project1.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            project2.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )

    # fetch for last two days, and only project2
    await assert_project_risk(
        execute_gql,
        filters=dict(
            start_date=day2,
            end_date=day3,
            project_ids=[project2.id],
        ),
        expected_data={day2: {RiskLevel.MEDIUM.name: 1}, day3: {RiskLevel.LOW.name: 1}},
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            start_date=day2,
            end_date=day3,
            project_ids=[project2.id],
        ),
        expected_data={
            project2.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            }
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_status_filtering(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Test filtering projectRiskLevelOverTime by project status
    """
    [day1, day2] = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    filters = dict(start_date=day1, end_date=day2)

    project_active: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        status=ProjectStatus.ACTIVE,
        **filters,
    )
    project_completed: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        status=ProjectStatus.COMPLETED,
        **filters,
    )
    project_pending: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        status=ProjectStatus.PENDING,
        **filters,
    )

    for project in (project_active, project_completed, project_pending):
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [
                (92, project_active.id),
                (96, project_completed.id),
                (250, project_pending.id),
            ],
            day2: [
                (250, project_active.id),
                (110, project_completed.id),
            ],
        },
    )

    # fetch for all projects, all statuses
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[
                ProjectStatus.ACTIVE.name,
                ProjectStatus.PENDING.name,
                ProjectStatus.COMPLETED.name,
            ],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 2, RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[
                ProjectStatus.ACTIVE.name,
                ProjectStatus.PENDING.name,
                ProjectStatus.COMPLETED.name,
            ],
        ),
        expected_data={
            project_active.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            project_completed.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
            project_pending.id: {
                day1: RiskLevel.HIGH.name,
            },
        },
    )

    # fetch for all projects, ACTIVE status
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[ProjectStatus.ACTIVE.name],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[ProjectStatus.ACTIVE.name],
        ),
        expected_data={
            project_active.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
        },
    )

    # fetch for all projects, ACTIVE and COMPLETED status
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[ProjectStatus.ACTIVE.name, ProjectStatus.COMPLETED.name],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 2},
            day2: {RiskLevel.MEDIUM.name: 1, RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            statuses=[ProjectStatus.ACTIVE.name, ProjectStatus.COMPLETED.name],
        ),
        expected_data={
            project_active.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            project_completed.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_project_risk_region_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Test filtering projectRiskLevelOverTime by project region
    """
    [day1, day2] = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]

    filters = dict(
        start_date=day1,
        end_date=day2,
    )

    region1: LibraryRegion = await LibraryRegionFactory.persist(db_session)
    project_region1: WorkPackage = await WorkPackageFactory.persist(
        db_session, region_id=region1.id, **filters
    )
    region2: LibraryRegion = await LibraryRegionFactory.persist(db_session)
    project_region2: WorkPackage = await WorkPackageFactory.persist(
        db_session, region_id=region2.id, **filters
    )
    await db_session.refresh(project_region1)
    await db_session.refresh(project_region2)
    await db_session.refresh(region1)
    await db_session.refresh(region2)

    for project in (project_region1, project_region2):
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(92, project_region1.id), (250, project_region2.id)],
            day2: [(250, project_region1.id), (110, project_region2.id)],
        },
    )

    # fetch for all projects, all regions
    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, region_ids=[region1.id, region2.id]),
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1, RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(**filters, region_ids=[region1.id, region2.id]),
        expected_data={
            project_region1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            project_region2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for all projects, region1
    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, region_ids=[region1.id]),
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(**filters, region_ids=[region1.id]),
        expected_data={
            project_region1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
        },
    )

    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, region_ids=[region2.id]),
        expected_data={
            day1: {RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(**filters, region_ids=[region2.id]),
        expected_data={
            project_region2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_division_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Test filtering projectRiskLevelOverTime by project division
    """
    [day1, day2] = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    filters = dict(start_date=day1, end_date=day2)

    division1: LibraryDivision = await LibraryDivisionFactory.persist(db_session)
    project_division1: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        division_id=division1.id,
        **filters,
    )
    division2: LibraryDivision = await LibraryDivisionFactory.persist(db_session)
    project_division2: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        division_id=division2.id,
        **filters,
    )
    await db_session.refresh(project_division1)
    await db_session.refresh(project_division2)
    await db_session.refresh(division1)
    await db_session.refresh(division2)

    for project in (project_division1, project_division2):
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(92, project_division1.id), (250, project_division2.id)],
            day2: [(250, project_division1.id), (110, project_division2.id)],
        },
    )

    # fetch for all projects, all divisions
    await assert_project_risk(
        execute_gql,
        filters=dict(**filters, division_ids=[division1.id, division2.id]),
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1, RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            division_ids=[division1.id, division2.id],
        ),
        expected_data={
            project_division1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            project_division2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for all projects, division1
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            division_ids=[division1.id],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            division_ids=[division1.id],
        ),
        expected_data={
            project_division1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
        },
    )

    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            division_ids=[division2.id],
        ),
        expected_data={
            day1: {RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            division_ids=[division2.id],
        ),
        expected_data={
            project_division2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_planning_project_risk_contractor_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Test filtering projectRiskLevelOverTime by project contractor
    """
    [day1, day2] = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    filters = dict(start_date=day1, end_date=day2)

    contractor1: Contractor = await ContractorFactory.persist(db_session)
    project_contractor1: WorkPackage = await WorkPackageFactory.persist(
        db_session, contractor_id=contractor1.id, **filters
    )
    contractor2: Contractor = await ContractorFactory.persist(db_session)
    project_contractor2: WorkPackage = await WorkPackageFactory.persist(
        db_session, contractor_id=contractor2.id, **filters
    )
    await db_session.refresh(project_contractor1)
    await db_session.refresh(project_contractor2)
    await db_session.refresh(contractor1)
    await db_session.refresh(contractor2)

    for project in (project_contractor1, project_contractor2):
        await TaskFactory.with_project_and_location(
            db_session, project=project, task_kwargs=filters
        )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(92, project_contractor1.id), (250, project_contractor2.id)],
            day2: [(250, project_contractor1.id), (110, project_contractor2.id)],
        },
    )

    # fetch for all projects, all contractors
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor1.id, contractor2.id],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1, RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor1.id, contractor2.id],
        ),
        expected_data={
            project_contractor1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
            project_contractor2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )

    # fetch for all projects, contractor1
    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor1.id],
        ),
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor1.id],
        ),
        expected_data={
            project_contractor1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.HIGH.name,
            },
        },
    )

    await assert_project_risk(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor2.id],
        ),
        expected_data={
            day1: {RiskLevel.HIGH.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=dict(
            **filters,
            contractor_ids=[contractor2.id],
        ),
        expected_data={
            project_contractor2.id: {
                day1: RiskLevel.HIGH.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_planning_project_risk_respects_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests that project risk levels are returned w/ respect to project start/end dates.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    filters = dict(start_date=day1, end_date=day3)

    project1 = await WorkPackageFactory.persist(
        db_session, start_date=day1, end_date=day2
    )
    project2 = await WorkPackageFactory.persist(
        db_session, start_date=day2, end_date=day3
    )

    await TaskFactory.with_project_and_location(
        db_session, project=project1, task_kwargs={"start_date": day1, "end_date": day2}
    )
    await TaskFactory.with_project_and_location(
        db_session, project=project2, task_kwargs={"start_date": day2, "end_date": day3}
    )

    # scores by risk by date
    await persist_test_data(
        db_session,
        {
            day1: [(99, project1.id), (105, project2.id)],
            day2: [(100, project1.id), (105, project2.id)],
            day3: [(250, project1.id), (99, project2.id)],
        },
    )

    await assert_project_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.LOW.name: 1},
        },
    )
    await assert_project_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            project1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
            project2.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.LOW.name,
            },
        },
    )
