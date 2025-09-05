import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    ControlsResult,
    SampleControl,
    assert_controls_data,
    assert_controls_percentages,
    batch_upsert_control_report,
    to_portfolio_input,
)

################################################################################
# Test Query and helper

portfolio_controls_not_implemented_by_project = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryControlId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    notImplementedControlsByProject(libraryControlId: $libraryControlId) {
      percent project { id name }
    }
  }
}
"""


async def execute_not_implemented_controls(
    execute_gql: ExecuteGQL,
    library_control_id: uuid.UUID,
    **filters: Any,
) -> Any:
    portfolio_filter = to_portfolio_input(**filters)
    data = await execute_gql(
        query=portfolio_controls_not_implemented_by_project,
        variables={"filter": portfolio_filter, "libraryControlId": library_control_id},
    )
    return data["portfolioLearnings"]["notImplementedControlsByProject"]


async def assert_not_implemented_controls(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[uuid.UUID, ControlsResult] | None = None,
    expected_percentages: list[float] | None = None,
) -> None:
    """
    Executes a risk count request, and asserts on the results.

    Passes kwargs to `execute_task_risk_over_time` where the PlanningInput
    filter is built.
    """

    controls_data = await execute_not_implemented_controls(execute_gql, **filters)

    if isinstance(expected_percentages, list):
        assert_controls_percentages(expected_percentages, controls_data)

    if expected_data:
        assert_controls_data(expected_data, controls_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_not_implemented_controls_by_project(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates impled/not-impled controls on daily-reports across 3 projects.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for not-impled-controls-by-project for each library_control.
    """
    project1, project2, project3 = await factories.WorkPackageFactory.persist_many(
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
    control1, control2 = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, project=project1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project2,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, project=project2
                ),
                SampleControl(
                    implemented=False, library_control=control2, project=project3
                ),
            ],
        },
    )

    # assert by project for each control
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control1.id},
        expected_data={
            project1.id: ControlsResult(percent=0.5, project_name=project1.name),
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control2.id},
        expected_data={
            project3.id: ControlsResult(percent=0.5, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_not_implemented_controls_by_project_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, project=project1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, project=project2
                ),
                SampleControl(
                    implemented=False, library_control=control2, project=project3
                ),
            ],
        },
    )

    # day1 only
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control1.id, "end_date": day1},
        expected_data={
            # no project1 results (b/c zeros are dropped)
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control2.id, "end_date": day1},
        # should be no results for control2 on day1
        expected_percentages=[],
    )

    # day2 only
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control1.id, "start_date": day2},
        expected_data={
            project1.id: ControlsResult(percent=1.0, project_name=project1.name),
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": control2.id, "start_date": day2},
        expected_data={
            project3.id: ControlsResult(percent=1.0, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_portfolio_not_implemented_controls_by_project_project_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    [project1, project2, project3] = await factories.WorkPackageFactory.persist_many(
        db_session, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, project=project1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    project=project3,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    project=project1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, project=project2
                ),
                SampleControl(
                    implemented=False, library_control=control2, project=project3
                ),
            ],
        },
    )

    # control 1

    # all projects (control1)
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id, project2.id, project3.id],
        },
        expected_data={
            project1.id: ControlsResult(percent=0.5, project_name=project1.name),
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )
    # projects 1 and 2
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            project1.id: ControlsResult(percent=0.5, project_name=project1.name),
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )
    # projects 2 and 3
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project2.id, project3.id],
        },
        expected_data={
            project2.id: ControlsResult(percent=1.0, project_name=project2.name),
        },
    )

    # control 2

    # all projects (control1)
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project1.id, project2.id, project3.id],
        },
        expected_data={
            project3.id: ControlsResult(percent=0.5, project_name=project3.name),
        },
    )
    # projects 1 and 2
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_percentages=[],
        expected_data={},
    )
    # projects 2 and 3
    await assert_not_implemented_controls(
        execute_gql,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project2.id, project3.id],
        },
        expected_data={
            project3.id: ControlsResult(percent=0.5, project_name=project3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_project_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    """
    day1 = datetime.now(timezone.utc)

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=False, library_control=library_control)
                for _ in range(11)
            ]
        },
    )

    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0 for _ in range(10)],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_project_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=False, library_control=library_control),
                SampleControl(implemented=True, library_control=library_control),
            ]
        },
    )

    # assert full date range
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0],
    )
