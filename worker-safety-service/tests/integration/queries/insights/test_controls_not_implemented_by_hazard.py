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
    to_project_input,
)

################################################################################
# Test Query and helper

project_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryControlId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    notImplementedControlsByHazard(libraryControlId: $libraryControlId) {
      percent libraryHazard { id name }
    }
  }
}
"""

portfolio_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryControlId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    notImplementedControlsByHazard(libraryControlId: $libraryControlId) {
      percent libraryHazard { id name }
    }
  }
}
"""


async def execute_not_implemented_controls_by_hazard(
    execute_gql: ExecuteGQL,
    query: str,
    library_control_id: uuid.UUID,
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
        variables={"filter": filt, "libraryControlId": library_control_id},
    )
    return data[query_name]["notImplementedControlsByHazard"]


async def assert_not_implemented_controls(
    execute_gql: ExecuteGQL,
    query: str,
    filters: Any,
    expected_data: dict[uuid.UUID, ControlsResult] | None = None,
    expected_percentages: list[float] | None = None,
) -> None:
    controls_data = await execute_not_implemented_controls_by_hazard(
        execute_gql, query, **filters
    )

    if isinstance(expected_percentages, list):
        assert_controls_percentages(expected_percentages, controls_data)

    if expected_data:
        assert_controls_data(expected_data, controls_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates impled/not-impled controls on daily-reports across 3 hazards.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for not-impled-controls-by-hazard for each library_control.
    Tests for both project and portfolio learnings.
    """
    project = await factories.WorkPackageFactory.persist(db_session)
    (
        lib_hazard1,
        lib_hazard2,
        lib_hazard3,
        lib_hazard4,
    ) = await factories.LibraryHazardFactory.persist_many(db_session, size=4)
    items = await factories.TaskControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard1.id},
            },
            {
                "project": project,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard2.id},
            },
        ],
    )
    hazard1 = items[0][4]
    hazard2 = items[1][4]
    (
        (
            *_,
            site_condition,
            hazard3,
        ),
        (
            *_,
            site_condition2,
            hazard4,
        ),
    ) = await factories.SiteConditionControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard3.id},
            },
            {
                "project": project,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard4.id},
            },
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
                    implemented=True, library_control=control1, hazard=hazard1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    site_condition=site_condition,
                    hazard=hazard3,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, hazard=hazard2
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    hazard=hazard3,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
        },
    )

    # portfolio queries

    # assert by location for each control
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "library_control_id": control1.id},
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "library_control_id": control2.id},
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )

    # control2, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "library_control_id": control2.id, "start_date": day2},
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )

    # project queries

    # assert by location for each control
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )

    # control2, only day 2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_hazard_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates impled/not-impled controls on daily-reports across 3 hazards.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for not-impled-controls-by-hazard for each library_control.
    Tests for both project and portfolio learnings.
    """
    project = await factories.WorkPackageFactory.persist(db_session)
    location1, location2 = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=2
    )
    (
        lib_hazard1,
        lib_hazard2,
        lib_hazard3,
        lib_hazard4,
    ) = await factories.LibraryHazardFactory.persist_many(db_session, size=4)
    items = await factories.TaskControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project,
                "location": location1,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard1.id},
            },
            {
                "project": project,
                "location": location2,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard2.id},
            },
        ],
    )
    hazard1 = items[0][4]
    hazard2 = items[1][4]
    (
        (
            *_,
            site_condition,
            hazard3,
        ),
        (
            *_,
            site_condition2,
            hazard4,
        ),
    ) = await factories.SiteConditionControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project,
                "location": location1,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard3.id},
            },
            {
                "project": project,
                "location": location2,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard4.id},
            },
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
                    implemented=True, library_control=control1, hazard=hazard1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    site_condition=site_condition,
                    hazard=hazard3,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, hazard=hazard2
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    hazard=hazard3,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
        },
    )

    # for both locations
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )

    # for location1
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
        },
    )

    # for location2
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_id": project.id,
            "location_ids": [location2.id],
        },
        expected_data={
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_id": project.id,
            "location_ids": [location2.id],
        },
        expected_data={
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_not_implemented_controls_by_hazard_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates impled/not-impled controls on daily-reports across 3 hazards.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for not-impled-controls-by-hazard for each library_control.
    Tests for both project and portfolio learnings.
    """
    project1, project2 = await factories.WorkPackageFactory.persist_many(
        db_session, size=2
    )
    (
        lib_hazard1,
        lib_hazard2,
        lib_hazard3,
        lib_hazard4,
    ) = await factories.LibraryHazardFactory.persist_many(db_session, size=4)
    items = await factories.TaskControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project1,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard1.id},
            },
            {
                "project": project2,
                "task_hazard_kwargs": {"library_hazard_id": lib_hazard2.id},
            },
        ],
    )
    hazard1 = items[0][4]
    hazard2 = items[1][4]
    (
        (
            *_,
            site_condition,
            hazard3,
        ),
        (
            *_,
            site_condition2,
            hazard4,
        ),
    ) = await factories.SiteConditionControlFactory.batch_with_relations(
        db_session,
        [
            {
                "project": project1,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard3.id},
            },
            {
                "project": project2,
                "site_condition_hazard_kwargs": {"library_hazard_id": lib_hazard4.id},
            },
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
                    implemented=True, library_control=control1, hazard=hazard1
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard2,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    site_condition=site_condition,
                    hazard=hazard3,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    hazard=hazard1,
                ),
                SampleControl(
                    implemented=False, library_control=control1, hazard=hazard2
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    hazard=hazard3,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition2,
                    hazard=hazard4,
                ),
            ],
        },
    )

    # for both locations
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )

    # for location1
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_hazard1.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard1.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_hazard3.id: ControlsResult(
                percent=0.5, library_hazard_name=lib_hazard3.name
            ),
        },
    )

    # for location2
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_hazard2.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard2.name
            ),
        },
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={
            **filters,
            "library_control_id": control2.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_hazard4.id: ControlsResult(
                percent=1.0, library_hazard_name=lib_hazard4.name
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_hazard_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    """
    day1 = datetime.now(timezone.utc)

    # setting a task to speed up the created data a bit
    (
        task,
        project,
        _,
    ) = await factories.TaskFactory.with_project_and_location(
        db_session,
    )

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False, library_control=library_control, task=task
                )
                for _ in range(11)
            ]
        },
    )

    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0 for _ in range(10)],
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": library_control.id,
            "project_id": project.id,
        },
        expected_percentages=[1.0 for _ in range(10)],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_not_implemented_controls_by_hazard_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)

    # setting a task to speed up the created data a bit
    (
        task,
        project,
        _,
    ) = await factories.TaskFactory.with_project_and_location(
        db_session,
    )

    library_control = await factories.LibraryControlFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=False, library_control=library_control, task=task
                ),
                SampleControl(
                    implemented=True, library_control=library_control, task=task
                ),
            ]
        },
    )

    await assert_not_implemented_controls(
        execute_gql,
        query=portfolio_query,
        filters={**filters, "library_control_id": library_control.id},
        expected_percentages=[1.0],
    )
    await assert_not_implemented_controls(
        execute_gql,
        query=project_query,
        filters={
            **filters,
            "library_control_id": library_control.id,
            "project_id": project.id,
        },
        expected_percentages=[1.0],
    )
