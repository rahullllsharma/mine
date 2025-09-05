import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
import worker_safety_service.models as models
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    HazardsResult,
    SampleControl,
    assert_daily_report_section_counts,
    assert_hazards_count,
    assert_hazards_data,
    batch_upsert_control_report,
    fetch_daily_report,
    to_portfolio_input,
)

################################################################################
# Test Query and helper

portfolio_applicable_hazards = """
query TestQuery($filter: PortfolioLearningsInput!) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    applicableHazards {
      count
      libraryHazard {
        id name
      }
    }
  }
}
"""


async def execute_portfolio_applicable_hazards(
    execute_gql: ExecuteGQL,
    **filters: Any,
) -> Any:
    data = await execute_gql(
        query=portfolio_applicable_hazards,
        variables={"filter": to_portfolio_input(**filters)},
    )
    return data["portfolioLearnings"]["applicableHazards"]


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

    hazards_data = await execute_portfolio_applicable_hazards(execute_gql, **filters)

    if isinstance(expected_count, list):
        assert_hazards_count(expected_count, hazards_data)

    if expected_data:
        assert_hazards_data(expected_data, hazards_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_basic(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [location1, location2] = await factories.LocationFactory.persist_many(
        db_session, size=2
    )
    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=2)
    [hazard1, hazard2] = library_hazards

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location2,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    location=location2,
                ),
            ],
        },
    )

    expected_hazards_data = {
        hazard1.id: HazardsResult(count=3, library_name=hazard1.name),
        hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
    }

    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data=expected_hazards_data,
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=2)
    [hazard1, hazard2] = library_hazards

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard1, project=project1
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, project=project2
                ),
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard2, project=project3
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, project=project1
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

    # no projects filtered
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data={
            hazard1.id: HazardsResult(count=3, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )

    # project1
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "project_ids": [project1.id]},
        expected_data={
            hazard1.id: HazardsResult(count=1, library_name=hazard1.name),
        },
    )

    # project2
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "project_ids": [project2.id]},
        expected_data={
            hazard1.id: HazardsResult(count=2, library_name=hazard1.name),
        },
    )

    # project1 and project3
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "project_ids": [project1.id, project3.id]},
        expected_data={
            hazard1.id: HazardsResult(count=1, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_same_location_or_task(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Asserts that hazards in various groupings on the daily reports are properly aggregated.
    Until now, the tests create a new report, task, hazard, and control per data point,
    so this ensures hazard_analysis is being properly aggregated from reports with
    multiple data points buried in lists of tasks and site-conditions.

    Assertions are included to be sure the created dailyReports have the expected counts,
    and then the api is hit again to be sure the count of applicable is the same.
    """
    (
        _,  # control
        project,
        location,
        task,
        _,  # hazard
    ) = await factories.TaskControlFactory.with_relations(
        db_session,
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=2)
    [hazard1, hazard2] = library_hazards

    filters = dict(start_date=day1, end_date=day3)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    location=location,
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, location=location
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, task=task
                ),
                SampleControl(
                    hazard_is_applicable=True, library_hazard=hazard1, task=task
                ),
                SampleControl(
                    hazard_is_applicable=False, library_hazard=hazard2, task=task
                ),
            ],
            day3: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    task=task,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    task=task,
                ),
            ],
        },
    )

    daily_report1 = await fetch_daily_report(db_session, location, day1)
    assert daily_report1
    assert_daily_report_section_counts(
        daily_report=daily_report1,
        task_count=3,
    )

    daily_report2 = await fetch_daily_report(db_session, location, day2)
    assert daily_report2
    assert_daily_report_section_counts(
        daily_report=daily_report2,
        task_count=1,
        task=task,
        hazard_count=3,
    )

    daily_report3 = await fetch_daily_report(db_session, location, day3)
    assert daily_report3
    assert_daily_report_section_counts(
        daily_report=daily_report3,
        task_count=1,
        task=task,
        hazard_count=3,
        control_count=3,
    )

    # no projects filtered
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data={
            hazard1.id: HazardsResult(count=5, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )

    # filter project
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "project_ids": [project.id]},
        expected_data={
            hazard1.id: HazardsResult(count=5, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_same_location_or_site_condition(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Asserts that hazards from the daily_report's site_condition analysis are included.
    """
    (
        _,  # control
        project,
        location,
        site_condition,
        _,  # hazard
    ) = await factories.SiteConditionControlFactory.with_relations(
        db_session,
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=2)
    [hazard1, hazard2] = library_hazards

    filters = dict(start_date=day1, end_date=day3)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    site_condition=site_condition,
                ),
            ],
            day3: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    site_condition=site_condition,
                ),
            ],
        },
    )

    daily_report2 = await fetch_daily_report(db_session, location, day2)
    assert daily_report2
    assert_daily_report_section_counts(
        daily_report=daily_report2,
        site_condition_count=1,
        site_condition=site_condition,
        hazard_count=3,
    )

    daily_report3 = await fetch_daily_report(db_session, location, day3)
    assert daily_report3
    assert_daily_report_section_counts(
        daily_report=daily_report3,
        site_condition_count=1,
        site_condition=site_condition,
        hazard_count=3,
        control_count=3,
    )

    # no projects filtered
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data={
            hazard1.id: HazardsResult(count=4, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )

    # filter project
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "project_ids": [project.id]},
        expected_data={
            hazard1.id: HazardsResult(count=4, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    [location1, location2] = await factories.LocationFactory.persist_many(
        db_session, size=2
    )
    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=2)
    [hazard1, hazard2] = library_hazards

    filters = dict(start_date=day1, end_date=day3)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location2,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location2,
                ),
            ],
            day3: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    location=location2,
                ),
            ],
        },
    )

    # assert full date range
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data={
            hazard1.id: HazardsResult(count=5, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )

    # assert day 1
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "end_date": day1},
        expected_data={
            hazard1.id: HazardsResult(count=1, library_name=hazard1.name),
        },
    )

    # assert day 3
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "start_date": day3},
        expected_data={
            hazard1.id: HazardsResult(count=2, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )

    # assert day 2 and 3
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "start_date": day2},
        expected_data={
            hazard1.id: HazardsResult(count=4, library_name=hazard1.name),
            hazard2.id: HazardsResult(count=1, library_name=hazard2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    It should also be ordered-descencing.
    """
    day1 = datetime.now(timezone.utc)

    # setting a task to speed up the created data a bit
    task, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
    )

    library_hazards: list[
        models.LibraryHazard
    ] = await factories.LibraryHazardFactory.persist_many(db_session, size=11)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(hazard_is_applicable=True, library_hazard=c, task=task)
                for c in library_hazards
            ],
        },
    )

    # assert full date range
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_count=[1] * 10,
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    It should also be ordered-descencing.
    """
    day1 = datetime.now(timezone.utc)

    # setting a task to speed up the created data a bit
    task, _, _ = await factories.TaskFactory.with_project_and_location(
        db_session,
    )

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(hazard_is_applicable=False, task=task),
                SampleControl(hazard_is_applicable=True, task=task),
            ],
        },
    )

    # assert full date range
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_count=[1],
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_portfolio_learnings_applicable_hazards_multiple_reports_same_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    day1, day2, day3 = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    lib_hazard1, lib_hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    items = await factories.TaskControlFactory.batch_with_relations(
        db_session,
        [
            {"task_hazard_kwargs": {"library_hazard_id": lib_hazard1.id}},
            {"task_hazard_kwargs": {"library_hazard_id": lib_hazard2.id}},
        ],
    )
    hazard1 = items[0][4]
    hazard2 = items[1][4]
    filters = dict(start_date=day1, end_date=day3)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(hazard_is_applicable=False, hazard=hazard1),
                SampleControl(hazard_is_applicable=False, hazard=hazard2),
            ],
            day2: [
                SampleControl(hazard_is_applicable=True, hazard=hazard1),
                SampleControl(hazard_is_applicable=False, hazard=hazard2),
            ],
            day3: [
                SampleControl(hazard_is_applicable=True, hazard=hazard1),
                SampleControl(hazard_is_applicable=True, hazard=hazard2),
            ],
        },
    )

    # expectations
    expected_hazards_data = {
        lib_hazard1.id: HazardsResult(count=2, library_name=lib_hazard1.name),
        lib_hazard2.id: HazardsResult(count=1, library_name=lib_hazard2.name),
    }

    # assert
    await assert_applicable_hazards(
        execute_gql,
        filters=filters,
        expected_data=expected_hazards_data,
    )
