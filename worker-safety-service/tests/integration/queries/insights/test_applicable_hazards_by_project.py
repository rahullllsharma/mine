import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    HazardsResult,
    SampleControl,
    assert_hazards_count,
    assert_hazards_data,
    batch_upsert_control_report,
    to_portfolio_input,
)

################################################################################
# Test Query and helper

portfolio_applicable_hazards_by_project = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryHazardId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    applicableHazardsByProject(libraryHazardId: $libraryHazardId) {
      count project { id name }
    }
  }
}
"""


async def execute_applicable_hazards(
    execute_gql: ExecuteGQL,
    library_hazard_id: uuid.UUID,
    **filters: Any,
) -> Any:
    portfolio_filter = to_portfolio_input(**filters)
    data = await execute_gql(
        query=portfolio_applicable_hazards_by_project,
        variables={"filter": portfolio_filter, "libraryHazardId": library_hazard_id},
    )
    return data["portfolioLearnings"]["applicableHazardsByProject"]


async def assert_applicable_hazards(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[uuid.UUID, HazardsResult] | None = None,
    expected_count: list[int] | None = None,
) -> None:
    """
    Executes a risk count request, and asserts on the results.

    Passes kwargs to `execute_task_risk_over_time` where the PlanningInput
    filter is built.
    """

    hazards_data = await execute_applicable_hazards(execute_gql, **filters)

    if isinstance(expected_count, list):
        assert_hazards_count(expected_count, hazards_data)

    if expected_data:
        assert_hazards_data(expected_data, hazards_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_applicable_hazards_by_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates applicable hazards on daily-reports across 3 projects.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for applicable-hazards-by-project for each library_hazard.
    """
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )
    (
        (
            site_condition1,
            *_,
        ),
        (
            site_condition2,
            *_,
        ),
    ) = await factories.SiteConditionFactory.batch_with_project_and_location(
        db_session,
        [
            {"project": project1},
            {"project": project2},
        ],
    )
    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, project=project1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project2,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, project=project2
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard2, project=project3
                ),
            ],
        },
    )

    # assert by project for each hazard
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard1.id},
        expected_data={
            project1.id: HazardsResult(count=1, project_name=project1.name),
            project2.id: HazardsResult(count=2, project_name=project2.name),
        },
    )
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard2.id},
        expected_data={
            project3.id: HazardsResult(count=1, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_applicable_hazards_by_project_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, project=project1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, project=project2
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard2, project=project3
                ),
            ],
        },
    )

    # day1 only
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard1.id, "end_date": day1},
        expected_data={
            # no project1 results (b/c zeros are dropped)
            project2.id: HazardsResult(count=1, project_name=project2.name),
        },
    )
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard2.id, "end_date": day1},
        # should be no results for hazard2 on day1
        expected_count=[],
    )

    # day2 only
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard1.id, "start_date": day2},
        expected_data={
            project1.id: HazardsResult(count=1, project_name=project1.name),
            project2.id: HazardsResult(count=1, project_name=project2.name),
        },
    )
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard2.id, "start_date": day2},
        expected_data={
            project3.id: HazardsResult(count=1, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_applicable_hazards_by_project_project_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, project=project1
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    project=project1,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, project=project2
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard2, project=project3
                ),
            ],
        },
    )

    # hazard 1

    # all projects (hazard1)
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id, project2.id, project3.id],
        },
        expected_data={
            project1.id: HazardsResult(count=1, project_name=project1.name),
            project2.id: HazardsResult(count=2, project_name=project2.name),
        },
    )
    # projects 1 and 2
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            project1.id: HazardsResult(count=1, project_name=project1.name),
            project2.id: HazardsResult(count=2, project_name=project2.name),
        },
    )
    # projects 2 and 3
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project2.id, project3.id],
        },
        expected_data={
            project2.id: HazardsResult(count=2, project_name=project2.name),
        },
    )

    # hazard 2

    # all projects (hazard1)
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_ids": [project1.id, project2.id, project3.id],
        },
        expected_data={
            project3.id: HazardsResult(count=1, project_name=project3.name),
        },
    )
    # projects 1 and 2
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_count=[],
        expected_data={},
    )
    # projects 2 and 3
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_ids": [project2.id, project3.id],
        },
        expected_data={
            project3.id: HazardsResult(count=1, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_project_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest applicable count.
    """
    day1 = datetime.now(timezone.utc)

    library_hazard = await factories.LibraryHazardFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(hazard_is_applicable=True, library_hazard=library_hazard)
                for _ in range(11)
            ]
        },
    )

    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1] * 10,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_project_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day = datetime.now(timezone.utc)

    library_hazard = await factories.LibraryHazardFactory.persist(db_session)

    filters = dict(start_date=day, end_date=day)

    await batch_upsert_control_report(
        db_session,
        {
            day: [
                SampleControl(hazard_is_applicable=True, library_hazard=library_hazard),
                SampleControl(
                    hazard_is_applicable=False, library_hazard=library_hazard
                ),
            ]
        },
    )

    # assert full date range
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1],
    )
