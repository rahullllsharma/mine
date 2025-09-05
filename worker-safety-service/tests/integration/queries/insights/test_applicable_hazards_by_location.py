import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.db_data import DBData
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    HazardsResult,
    SampleControl,
    assert_hazards_count,
    assert_hazards_data,
    batch_upsert_control_report,
    to_project_input,
)

################################################################################
# Test Query and helper

project_applicable_hazards_by_location = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryHazardId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    applicableHazardsByLocation(libraryHazardId: $libraryHazardId) {
      count location { id name }
    }
  }
}
"""


async def execute_applicable_hazards(
    execute_gql: ExecuteGQL,
    library_hazard_id: uuid.UUID,
    **filters: Any,
) -> Any:
    project_filter = to_project_input(**filters)
    data = await execute_gql(
        query=project_applicable_hazards_by_location,
        variables={"filter": project_filter, "libraryHazardId": library_hazard_id},
    )
    return data["projectLearnings"]["applicableHazardsByLocation"]


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
async def test_project_applicable_hazards_by_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates applicable hazards on daily-reports across 3 locations.
    Puts some data points on site-conditions (the rest default to tasks).
    Queries for applicable-hazards-by-location for each library_hazard.
    """
    project = await factories.WorkPackageFactory.persist(db_session)
    location1, location2, location3 = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
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
            {"location": location1},
            {"location": location2},
        ],
    )
    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2, project_id=project.id)

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
                    location=location2,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    location=location2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    location=location3,
                ),
            ],
        },
    )

    # assert by location for each hazard
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard1.id},
        expected_data={
            location1.id: HazardsResult(count=1, location_name=location1.name),
            location2.id: HazardsResult(count=2, location_name=location2.name),
        },
    )
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard2.id},
        expected_data={
            location3.id: HazardsResult(count=1, location_name=location3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_applicable_hazards_by_location_date_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    [location1, location2, location3] = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2, project_id=project.id)

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
                    location=location2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location3,
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
                    location=location2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    location=location3,
                ),
            ],
        },
    )

    # day1 only
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard1.id, "end_date": day1},
        expected_data={
            # no location1 results (b/c zeros are dropped)
            location2.id: HazardsResult(count=1, location_name=location2.name),
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
            location1.id: HazardsResult(count=1, location_name=location1.name),
            location2.id: HazardsResult(count=1, location_name=location2.name),
        },
    )
    await assert_applicable_hazards(
        execute_gql,
        filters={**filters, "library_hazard_id": hazard2.id, "start_date": day2},
        expected_data={
            location3.id: HazardsResult(count=1, location_name=location3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_applicable_hazards_by_location_location_filters(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    project = await factories.WorkPackageFactory.persist(db_session)
    [location1, location2, location3] = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=3
    )
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    [day1, day2] = days

    [hazard1, hazard2] = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )

    filters = dict(start_date=day1, end_date=day2, project_id=project.id)

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
                    location=location2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    location=location3,
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
                    location=location2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    location=location3,
                ),
            ],
        },
    )

    # hazard 1

    # all locations (hazard1)
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "location_ids": [location1.id, location2.id, location3.id],
        },
        expected_data={
            location1.id: HazardsResult(count=1, location_name=location1.name),
            location2.id: HazardsResult(count=2, location_name=location2.name),
        },
    )
    # locations 1 and 2
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            location1.id: HazardsResult(count=1, location_name=location1.name),
            location2.id: HazardsResult(count=2, location_name=location2.name),
        },
    )
    # locations 2 and 3
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "location_ids": [location2.id, location3.id],
        },
        expected_data={
            location2.id: HazardsResult(count=2, location_name=location2.name),
        },
    )

    # hazard 2

    # all locations (hazard1)
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "location_ids": [location1.id, location2.id, location3.id],
        },
        expected_data={
            location3.id: HazardsResult(count=1, location_name=location3.name),
        },
    )
    # locations 1 and 2
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_count=[],
        expected_data={},
    )
    # locations 2 and 3
    await assert_applicable_hazards(
        execute_gql,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "location_ids": [location2.id, location3.id],
        },
        expected_data={
            location3.id: HazardsResult(count=1, location_name=location3.name),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_location_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest applicable count.
    """
    day1 = datetime.now(timezone.utc)

    project = await factories.WorkPackageFactory.persist(db_session)

    library_hazard = await factories.LibraryHazardFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=library_hazard,
                    project=project,
                )
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
async def test_applicable_hazards_by_location_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)

    location = await factories.LocationFactory.persist(db_session)
    assert location.project_id
    project = await db_data.project(location.project_id)
    library_hazard = await factories.LibraryHazardFactory.persist(db_session)

    filters = dict(start_date=day1, end_date=day1, project_id=project.id)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=library_hazard,
                    project=project,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=library_hazard,
                    project=project,
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
