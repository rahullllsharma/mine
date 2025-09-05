import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
import worker_safety_service.models as models
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    ControlsResult,
    SampleControl,
    assert_controls_data,
    assert_controls_percentages,
    assert_daily_report_section_counts,
    batch_upsert_control_report,
    fetch_daily_report,
    to_project_input,
)

################################################################################
# Test Query and helper

project_controls_not_implemented = """
query TestQuery($filter: ProjectLearningsInput!) {
  projectLearnings(projectLearningsInput: $filter) {
    notImplementedControls {
      percent
      libraryControl {
        id name
      }
    }
  }
}
"""


async def execute_project_not_implemented_controls(
    execute_gql: ExecuteGQL,
    **filters: Any,
) -> Any:
    data = await execute_gql(
        query=project_controls_not_implemented,
        variables={"filter": to_project_input(**filters)},
    )
    return data["projectLearnings"]["notImplementedControls"]


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

    controls_data = await execute_project_not_implemented_controls(
        execute_gql, **filters
    )

    if isinstance(expected_percentages, list):
        assert_controls_percentages(expected_percentages, controls_data)

    if expected_data:
        assert_controls_data(expected_data, controls_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_basic(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=2)

    [control1, control2] = library_controls

    location = await factories.LocationFactory.persist(db_session)
    filters = dict(start_date=day1, end_date=day2, project_id=location.project_id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control2, location=location
                ),
            ],
        },
    )

    expected_controls_data = {
        control1.id: ControlsResult(percent=0.75, library_name=control1.name),
        control2.id: ControlsResult(percent=0.5, library_name=control2.name),
    }

    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_data=expected_controls_data,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    [location1, location2, location3] = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=2)

    [control1, control2] = library_controls

    filters = dict(start_date=day1, end_date=day3, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, location=location1
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location2
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location3
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False, library_control=control1, location=location1
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location2
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location3
                ),
            ],
            day3: [
                SampleControl(
                    implemented=False, library_control=control1, location=location1
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location2
                ),
                SampleControl(
                    implemented=False, library_control=control2, location=location3
                ),
            ],
        },
    )

    # no projects filtered
    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_data={
            control1.id: ControlsResult(percent=0.83, library_name=control1.name),
            control2.id: ControlsResult(percent=0.33, library_name=control2.name),
        },
    )

    # project1
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "location_ids": [location1.id]},
        expected_data={
            control1.id: ControlsResult(percent=0.67, library_name=control1.name),
        },
    )

    # location2
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "location_ids": [location2.id]},
        expected_data={
            control1.id: ControlsResult(percent=1.0, library_name=control1.name),
        },
    )

    # location1 and location3
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "location_ids": [location1.id, location3.id]},
        expected_data={
            control1.id: ControlsResult(percent=0.67, library_name=control1.name),
            control2.id: ControlsResult(percent=0.33, library_name=control2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_same_location_task_or_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Asserts that controls in various groupings on the daily reports are properly aggregated.
    Until now, the tests create a new report, task, hazard, and control per data point,
    so this ensures control_analysis is being properly aggregated from reports with
    multiple data points buried in lists of tasks, site-conditions, and hazards.

    Assertions are included to be sure the created dailyReports have the expected counts,
    and then the api is hit again to be sure the % not impled is the same.
    """
    (
        _,  # control
        project,
        location,
        task,
        hazard,  # a hazard on this task/location/project
    ) = await factories.TaskControlFactory.with_relations(db_session)

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=2)

    [control1, control2] = library_controls

    filters = dict(start_date=day1, end_date=day3, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location
                ),
            ],
            day2: [
                SampleControl(implemented=False, library_control=control1, task=task),
                SampleControl(implemented=False, library_control=control1, task=task),
                SampleControl(implemented=True, library_control=control2, task=task),
            ],
            day3: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task,
                    hazard=hazard,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task,
                    hazard=hazard,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    task=task,
                    hazard=hazard,
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
        hazard_count=1,
        hazard=hazard,
        control_count=3,
    )

    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_data={
            control1.id: ControlsResult(percent=0.83, library_name=control1.name),
            control2.id: ControlsResult(percent=0.33, library_name=control2.name),
        },
    )

    # filter the location, should be the same
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "location_ids": [location.id]},
        expected_data={
            control1.id: ControlsResult(percent=0.83, library_name=control1.name),
            control2.id: ControlsResult(percent=0.33, library_name=control2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_same_location_site_condition_or_hazard(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Asserts that controls from the daily_report's site_condition analysis are included.
    """
    (
        _,  # control
        project,
        location,
        site_condition,
        hazard,  # a hazard on this sc/location/project
    ) = await factories.SiteConditionControlFactory.with_relations(
        db_session,
    )

    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=2)

    [control1, control2] = library_controls

    filters = dict(start_date=day1, end_date=day3, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [],
            day2: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=True,
                    library_control=control2,
                    site_condition=site_condition,
                ),
            ],
            day3: [
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    site_condition=site_condition,
                    hazard=hazard,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    site_condition=site_condition,
                    hazard=hazard,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition,
                    hazard=hazard,
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
        hazard_count=1,
        hazard=hazard,
        control_count=3,
    )

    # no projects filtered
    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_data={
            control1.id: ControlsResult(percent=1.0, library_name=control1.name),
            control2.id: ControlsResult(percent=0.5, library_name=control2.name),
        },
    )

    # filter location
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "location_ids": [location.id]},
        expected_data={
            control1.id: ControlsResult(percent=1.0, library_name=control1.name),
            control2.id: ControlsResult(percent=0.5, library_name=control2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_deduplicating_library_controls(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Tests that the same library control used in a task AND site_condition is
    deduplicated by this aggregate.
    """
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [control1, control2] = await factories.LibraryControlFactory.persist_many(
        db_session, size=2
    )

    (
        _,  # control
        project,
        _,
        task,
        _,
    ) = await factories.TaskControlFactory.with_relations(db_session)
    (
        _,  # control
        _,
        _,
        site_condition,
        _,
    ) = await factories.SiteConditionControlFactory.with_relations(
        db_session, project=project
    )

    filters = dict(start_date=day1, end_date=day2, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True,
                    library_control=control1,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control1,
                    task=task,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    site_condition=site_condition,
                ),
                SampleControl(
                    implemented=False,
                    library_control=control2,
                    task=task,
                ),
            ],
        },
    )

    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_percentages=[1.0, 0.5],
        expected_data={
            control1.id: ControlsResult(percent=0.5, library_name=control1.name),
            control2.id: ControlsResult(percent=1.0, library_name=control2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    [day1, day2, day3] = days

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=2)

    [control1, control2] = library_controls

    location = await factories.LocationFactory.persist(db_session)
    filters = dict(start_date=day1, end_date=day3, project_id=location.project_id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    implemented=True, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location
                ),
            ],
            day2: [
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=True, library_control=control2, location=location
                ),
            ],
            day3: [
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control1, location=location
                ),
                SampleControl(
                    implemented=False, library_control=control2, location=location
                ),
            ],
        },
    )

    # assert full date range
    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_data={
            control1.id: ControlsResult(percent=0.83, library_name=control1.name),
            control2.id: ControlsResult(percent=0.33, library_name=control2.name),
        },
    )

    # assert day 1
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "end_date": day1},
        expected_data={
            control1.id: ControlsResult(percent=0.5, library_name=control1.name),
        },
    )

    # assert day 3
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "start_date": day3},
        expected_data={
            control1.id: ControlsResult(percent=1.0, library_name=control1.name),
            control2.id: ControlsResult(percent=1.0, library_name=control2.name),
        },
    )

    # assert day 2 and 3
    await assert_not_implemented_controls(
        execute_gql,
        filters={**filters, "start_date": day2},
        expected_data={
            control1.id: ControlsResult(percent=1.0, library_name=control1.name),
            control2.id: ControlsResult(percent=0.5, library_name=control2.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    It should also be ordered-descencing.
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

    library_controls: list[
        models.LibraryControl
    ] = await factories.LibraryControlFactory.persist_many(db_session, size=11)

    filters = dict(start_date=day1, end_date=day1, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=False, library_control=c, task=task)
                for c in library_controls
            ]
        },
    )

    # assert full date range
    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_percentages=[1.0] * 10,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_learnings_not_implemented_controls_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest not-impled percentages.
    It should also be ordered-descencing.
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

    filters = dict(start_date=day1, end_date=day1, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(implemented=True, task=task),
                SampleControl(implemented=False, task=task),
            ],
        },
    )

    # assert full date range
    await assert_not_implemented_controls(
        execute_gql,
        filters=filters,
        expected_percentages=[1.0],
    )
