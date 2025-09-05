from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    SampleControl,
    assert_reasons_data,
    batch_upsert_control_report,
    to_portfolio_input,
    to_project_input,
)

################################################################################
# Test Query and helper

project_query = """
query TestQuery($filter: ProjectLearningsInput!) {
  projectLearnings(projectLearningsInput: $filter) {
    reasonsControlsNotImplemented {
      count
      reason
    }
  }
}
"""

portfolio_query = """
query TestQuery($filter: PortfolioLearningsInput!) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    reasonsControlsNotImplemented {
      count
      reason
    }
  }
}
"""


async def execute_reasons_not_implemented(
    execute_gql: ExecuteGQL,
    query: str,
    **filters: Any,
) -> Any:
    filt = None
    query_name = None
    if query == project_query:
        filt = to_project_input(**filters)
        query_name = "projectLearnings"
    elif query == portfolio_query:
        filt = to_portfolio_input(**filters)
        query_name = "portfolioLearnings"
    assert filt
    assert query_name

    data = await execute_gql(
        query=query,
        variables={"filter": filt},
    )
    return data[query_name]["reasonsControlsNotImplemented"]


async def assert_reasons_not_implemented(
    execute_gql: ExecuteGQL,
    query: str,
    filters: Any,
    expected_data: dict[str, int],
) -> None:
    reasons_data = await execute_reasons_not_implemented(execute_gql, query, **filters)

    assert_reasons_data(expected_data, reasons_data)


################################################################################
# Tests


# at the time of writing, these reasons are hard-coded on the frontend
# this implementation is not dependent on them, but we use these as test data anyway
REASONS = [
    "Planned but not implemented",
    "Other controls in place",
    "Control was not relevant",
    "Control was not available",
]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_basic(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, not_implemented_reason=REASONS[0], project=project
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
                SampleControl(
                    implemented=True, not_implemented_reason=REASONS[0], project=project
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    project=project,
                ),
            ],
        },
    )

    # portfolio queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters=filters,
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )

    # project queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id},
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    projects = await factories.WorkPackageFactory.persist_many(db_session, size=3)
    [project1, project2, project3] = projects

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True,
                    not_implemented_reason=REASONS[0],
                    project=project1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project2,
                ),
                SampleControl(
                    implemented=True,
                    not_implemented_reason=REASONS[0],
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    project=project1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    project=project2,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    project=project3,
                ),
            ],
        },
    )

    # no projects specified
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters=filters,
        expected_data={
            REASONS[0]: 1,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 1,
        },
    )

    # project1
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "project_ids": [project1.id]},
        expected_data={
            REASONS[1]: 1,
        },
    )

    # project2
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "project_ids": [project2.id]},
        expected_data={
            REASONS[0]: 1,
            REASONS[2]: 1,
        },
    )

    # projects 2 and 3
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "project_ids": [project2.id, project3.id]},
        expected_data={
            REASONS[0]: 1,
            REASONS[2]: 1,
            REASONS[3]: 1,
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    project = await factories.WorkPackageFactory.persist(db_session)
    locations = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )
    [location1, location2, location3] = locations

    filters = dict(start_date=day1, end_date=day2, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True,
                    not_implemented_reason=REASONS[0],
                    location=location1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    location=location2,
                ),
                SampleControl(
                    implemented=True,
                    not_implemented_reason=REASONS[0],
                    location=location3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    location=location1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    location=location2,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    location=location3,
                ),
            ],
        },
    )

    # no locations specified
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters=filters,
        expected_data={
            REASONS[0]: 1,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 1,
        },
    )

    # location1
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "location_ids": [location1.id]},
        expected_data={
            REASONS[1]: 1,
        },
    )

    # location2
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "location_ids": [location2.id]},
        expected_data={
            REASONS[0]: 1,
            REASONS[2]: 1,
        },
    )

    # locations 2 and 3
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "location_ids": [location2.id, location3.id]},
        expected_data={
            REASONS[0]: 1,
            REASONS[2]: 1,
            REASONS[3]: 1,
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, not_implemented_reason=REASONS[0], project=project
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
                SampleControl(
                    implemented=True, not_implemented_reason=REASONS[0], project=project
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[3],
                    project=project,
                ),
            ],
        },
    )

    # portfolio queries

    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters=filters,
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )
    # day1
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "end_date": day1},
        expected_data={
            REASONS[0]: 2,
        },
    )
    # day2
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "start_date": day2},
        expected_data={
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )

    # project queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id},
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )
    # day1
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id, "end_date": day1},
        expected_data={
            REASONS[0]: 2,
        },
    )
    # day2
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id, "start_date": day2},
        expected_data={
            REASONS[1]: 1,
            REASONS[2]: 1,
            REASONS[3]: 2,
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_empty_strings(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason="",  # empty string!
                    project=project,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    project=project,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason="",  # empty string!
                    project=project,
                ),
            ],
        },
    )

    # portfolio queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters=filters,
        expected_data={
            # make sure no empty strings are returned
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
        },
    )

    # project queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id},
        expected_data={
            # make sure no empty strings are returned
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 1,
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_reasons_controls_not_implemented_same_control_reported_multiple_times(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    items = await factories.TaskControlFactory.batch_with_relations(
        db_session,
        [
            {"project": project},
            {"project": project},
        ],
    )
    control1 = items[0][0]
    control2 = items[1][0]
    day1, day2, day3 = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    filters = dict(start_date=day1, end_date=day3)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    control=control1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[0],
                    control=control2,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[1],
                    control=control1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    control=control2,
                ),
            ],
            day3: [
                SampleControl(
                    implemented=True,
                    not_implemented_reason=REASONS[1],
                    control=control1,
                ),
                SampleControl(
                    implemented=False,
                    not_implemented_reason=REASONS[2],
                    control=control2,
                ),
            ],
        },
    )

    # portfolio queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=portfolio_query,
        filters=filters,
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 2,
        },
    )

    # project queries
    await assert_reasons_not_implemented(
        execute_gql,
        query=project_query,
        filters={**filters, "project_id": project.id},
        expected_data={
            REASONS[0]: 2,
            REASONS[1]: 1,
            REASONS[2]: 2,
        },
    )
