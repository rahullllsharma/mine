import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Tuple

import pytest

import worker_safety_service.utils as utils
from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TaskFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, RiskLevel, WorkPackage

from .helpers import (
    CountsByRiskLevel,
    batch_create_risk_score,
    risk_level_counts,
    to_project_input,
)

################################################################################
# Test Query and helper

planning_location_risk_over_time = """
query TestQuery($filter: ProjectPlanningInput!) {
  projectPlanning(projectPlanningInput: $filter) {
    locationRiskLevelOverTime {
      date
      riskLevel
      count
    }
  }
}
"""

learnings_location_risk_over_time = """
query TestQuery($filter: ProjectLearningsInput!) {
  projectLearnings(projectLearningsInput: $filter) {
    locationRiskLevelOverTime {
      date
      riskLevel
      count
    }
  }
}
"""

location_risk_by_date = """
query TestQuery($filter: ProjectPlanningInput!) {
  projectPlanning(projectPlanningInput: $filter) {
    locationRiskLevelByDate {
      projectName
      locationName
      location {
        id name project { id name }
      }
      riskLevelByDate {
        date riskLevel
      }
    }
  }
}
"""


async def execute_planning_location_risk_over_time(
    execute_gql: ExecuteGQL, **filters: Any
) -> Any:
    data = await execute_gql(
        query=planning_location_risk_over_time,
        variables={"filter": to_project_input(**filters)},
    )
    return data["projectPlanning"]["locationRiskLevelOverTime"]


async def execute_learnings_location_risk_over_time(
    execute_gql: ExecuteGQL, **filters: Any
) -> Any:
    data = await execute_gql(
        query=learnings_location_risk_over_time,
        variables={"filter": to_project_input(**filters)},
    )
    return data["projectLearnings"]["locationRiskLevelOverTime"]


async def execute_location_risk_by_date(execute_gql: ExecuteGQL, **filters: Any) -> Any:
    data = await execute_gql(
        query=location_risk_by_date, variables={"filter": to_project_input(**filters)}
    )
    return data["projectPlanning"]["locationRiskLevelByDate"]


async def persist_test_data(
    session: AsyncSession, test_data: dict[datetime, list[Tuple[int, uuid.UUID]]]
) -> None:
    await batch_create_risk_score(
        session,
        [
            {"day": day, "score": score, "location_id": _id}
            for day, scores in test_data.items()
            for score, _id in scores
        ],
    )


def assert_location_risk_over_time(
    expected_data: dict[datetime, CountsByRiskLevel], risk_counts: list[dict]
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


async def assert_location_risk(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[datetime, CountsByRiskLevel],
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_location_risk_over_time` where the PlanningInput
    filter is built.
    """

    risk_counts = await execute_planning_location_risk_over_time(execute_gql, **filters)
    assert_location_risk_over_time(expected_data, risk_counts)

    risk_counts = await execute_learnings_location_risk_over_time(
        execute_gql, **filters
    )
    assert_location_risk_over_time(expected_data, risk_counts)


async def assert_location_risk_by_date(
    execute_gql: ExecuteGQL,
    filters: Any,
    expected_data: dict[uuid.UUID, Dict[datetime, str]],
    log: bool = False,
) -> None:
    """
    Executes a risk count request, and asserts on the results.
    Asserts that the results match the expected dates and risk_level counts
    in test_data.

    Passes kwargs to `execute_location_risk_over_time` where the PlanningInput
    filter is built.
    """

    location_risks = await execute_location_risk_by_date(execute_gql, **filters)

    expected_location_ids = {str(id) for id in expected_data.keys()}
    expected_data_str_keys = {
        str(id): {d.strftime("%Y-%m-%d"): level for d, level in level_by_date.items()}
        for id, level_by_date in expected_data.items()
    }

    by_id = lambda pr: pr["location"]["id"]  # noqa: E731
    location_by_id = utils.groupby(location_risks, key=by_id)

    if log:
        print("\nreturned data", location_by_id)
        print("\nexpected_data", expected_data_str_keys)

    # make sure only the expected dates are returned
    assert set(location_by_id.keys()) == expected_location_ids

    for location_id, fetched_location_risks in location_by_id.items():
        assert len(fetched_location_risks) == 1  # sanity check
        fetched_location_risk = fetched_location_risks[0]
        expected_level_by_date = expected_data_str_keys[location_id]

        if not expected_level_by_date:
            # if we expect no data, make sure there isn't any
            assert not fetched_location_risk["riskLevelByDate"]

        location_data = fetched_location_risk["location"]
        assert location_data["name"] == fetched_location_risk["locationName"]

        project_data = fetched_location_risk["location"]["project"]
        assert project_data["name"] == fetched_location_risk["projectName"]

        if expected_level_by_date:
            fetched_risk_levels = fetched_location_risk["riskLevelByDate"]
            assert fetched_risk_levels

            by_date = lambda pr: pr["date"]  # noqa: E731
            risk_levels_by_date = utils.groupby(fetched_risk_levels, key=by_date)

            # make sure only our expected dates are included
            assert set(expected_level_by_date.keys()) == set(risk_levels_by_date.keys())

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
async def test_planning_location_risk_location_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    A basic test for the location_risk query, that uses only one location
    and a few dates with one score each.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]
    date_filters = dict(start_date=day1, end_date=day3)

    project: WorkPackage = await WorkPackageFactory.persist(db_session, **date_filters)
    (activity1, _, location1) = await ActivityFactory.with_project_and_location(
        db_session,
        project=project,
        activity_kwargs={"start_date": day1, "end_date": day3},
    )
    (activity2, _, location2) = await ActivityFactory.with_project_and_location(
        db_session,
        project=project,
        activity_kwargs={"start_date": day1, "end_date": day3},
    )

    await TaskFactory.persist(
        db_session,
        project_id=project.id,
        activity_id=activity1.id,
        location_id=location1.id,
        **date_filters,
    )
    await TaskFactory.persist(
        db_session,
        project_id=project.id,
        activity_id=activity2.id,
        location_id=location2.id,
        **date_filters,
    )

    filters = dict(project_id=project.id, **date_filters)

    await persist_test_data(
        db_session,
        {
            day1: [(99, location1.id), (105, location2.id)],
            day2: [(100, location1.id), (105, location2.id)],
            day3: [(249, location1.id), (250, location2.id)],
        },
    )
    expected_location1_risk = {
        location1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }
    expected_location2_risk = {
        location2.id: {
            day1: RiskLevel.MEDIUM.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.HIGH.name,
        },
    }

    # fetch for all locations on this project
    await assert_location_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={**expected_location1_risk, **expected_location2_risk},
    )

    # fetch for both locations
    await assert_location_risk(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={**expected_location1_risk, **expected_location2_risk},
    )

    # fetch for location 1
    await assert_location_risk(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id],
        },
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location1.id],
        },
        expected_data=expected_location1_risk,
    )

    # fetch for location 2
    await assert_location_risk(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location2.id],
        },
        expected_data={
            day1: {RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.HIGH.name: 1},
        },
    )

    await assert_location_risk_by_date(
        execute_gql,
        filters={
            **filters,
            "location_ids": [location2.id],
        },
        expected_data=expected_location2_risk,
    )

    # archive location 1
    location1.archived_at = datetime.now(timezone.utc)
    await db_session.commit()
    await db_session.refresh(location1)

    # fetch for all project locations, assert the archived location is not present
    await assert_location_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data=expected_location2_risk,
    )

    # explicitly fetch with all locations, including the archived location
    vs = {
        "projectId": project.id,
        "startDate": day1.date(),
        "endDate": day3.date(),
        "locationIds": [location1.id, location2.id],
    }
    data = await execute_gql(
        query=planning_location_risk_over_time, variables={"filter": vs}, raw=True
    )
    # archived location id is no longer valid, reject the request
    assert data.json().get("errors"), "invalid location_id"

    # explicitly fetch with all locations, including the archived location
    vs = {
        "projectId": project.id,
        "startDate": day1.date(),
        "endDate": day3.date(),
        "locationIds": [location1.id, location2.id],
    }
    data = await execute_gql(
        query=learnings_location_risk_over_time, variables={"filter": vs}, raw=True
    )
    # archived location id is no longer valid, reject the request
    assert data.json().get("errors"), "invalid location_id"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_planning_location_risk_date_filtering(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that date filtering via start_date and end_date limits the
    data returned.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    date_filters = dict(start_date=day1, end_date=day3)

    project: WorkPackage = await WorkPackageFactory.persist(db_session, **date_filters)
    (activity1, _, location1) = await ActivityFactory.with_project_and_location(
        db_session,
        project=project,
        activity_kwargs={"start_date": day1, "end_date": day3},
    )
    (activity2, _, location2) = await ActivityFactory.with_project_and_location(
        db_session,
        project=project,
        activity_kwargs={"start_date": day1, "end_date": day3},
    )

    await TaskFactory.persist(
        db_session,
        project_id=project.id,
        activity_id=activity1.id,
        location_id=location1.id,
        **date_filters,
    )
    await TaskFactory.persist(
        db_session,
        project_id=project.id,
        activity_id=activity2.id,
        location_id=location2.id,
        **date_filters,
    )

    filters = dict(project_id=project.id, **date_filters)

    await persist_test_data(
        db_session,
        {
            day1: [(99, location1.id), (105, location2.id)],
            day2: [(100, location1.id), (105, location2.id)],
            day3: [(249, location1.id), (250, location2.id)],
        },
    )
    expected_location1_risk = {
        location1.id: {
            day1: RiskLevel.LOW.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.MEDIUM.name,
        },
    }
    expected_location2_risk = {
        location2.id: {
            day1: RiskLevel.MEDIUM.name,
            day2: RiskLevel.MEDIUM.name,
            day3: RiskLevel.HIGH.name,
        },
    }

    # fetch for the full date-range
    await assert_location_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={**expected_location1_risk, **expected_location2_risk},
    )

    # fetch for the first day
    await assert_location_risk(
        execute_gql,
        filters={**filters, "end_date": day1},
        expected_data={day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1}},
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "end_date": day1},
        expected_data={
            location1.id: {day1: RiskLevel.LOW.name},
            location2.id: {day1: RiskLevel.MEDIUM.name},
        },
    )

    # fetch for the last day
    await assert_location_risk(
        execute_gql,
        filters={**filters, "start_date": day3},
        expected_data={
            day3: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day3},
        expected_data={
            location1.id: {day3: RiskLevel.MEDIUM.name},
            location2.id: {day3: RiskLevel.HIGH.name},
        },
    )

    # fetch for the first two days
    await assert_location_risk(
        execute_gql,
        filters={**filters, "end_date": day2},
        expected_data={
            day1: {RiskLevel.LOW.name: 1, RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 2},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "end_date": day2},
        expected_data={
            location1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
            },
            location2.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
            },
        },
    )
    # fetch for the last two days
    await assert_location_risk(
        execute_gql,
        filters={**filters, "start_date": day2, "end_date": day3},
        expected_data={
            day2: {RiskLevel.MEDIUM.name: 2},
            day3: {RiskLevel.HIGH.name: 1, RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "start_date": day2, "end_date": day3},
        expected_data={
            location1.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.MEDIUM.name,
            },
            location2.id: {
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_planning_location_risk_multiple_calcs_same_day(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates multiple scores on the same day for the same location.
    Only the latest calculated score, per day, per location should be counted.
    """

    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    date_filters = dict(start_date=day1, end_date=day3)

    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day1, "end_date": day3}
    )
    await TaskFactory.persist(
        db_session,
        project_id=project.id,
        activity_id=activity.id,
        location_id=location.id,
        **date_filters,
    )

    filters = dict(**date_filters, project_id=project.id)

    await persist_test_data(
        db_session,
        {
            day1: [(99, location.id), (4, location.id), (105, location.id)],
            day2: [(100, location.id), (290, location.id), (105, location.id)],
            day3: [(249, location.id), (250, location.id)],
        },
    )

    # fetch for all locations on this project
    await assert_location_risk(
        execute_gql,
        filters=filters,
        expected_data={
            day1: {RiskLevel.MEDIUM.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters=filters,
        expected_data={
            location.id: {
                day1: RiskLevel.MEDIUM.name,
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            }
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_planning_location_risk_sorting(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests the sort order of locationRiskByDate's return - it should by location name.
    """
    days = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)]
    date_filters = dict(start_date=days[0], end_date=days[-1])

    project: WorkPackage = await WorkPackageFactory.persist(db_session, **date_filters)
    location3 = await LocationFactory.persist(
        db_session, project_id=project.id, name="Calvin and Hobbes"
    )
    location2 = await LocationFactory.persist(
        db_session, project_id=project.id, name="Bobby Bobbington"
    )
    location1 = await LocationFactory.persist(
        db_session, project_id=project.id, name="Aaron Aarons"
    )
    locations = [location1, location2, location3]
    for location in locations:
        await TaskFactory.persist(db_session, location_id=location.id, **date_filters)
    expected_location_order = locations
    expected_id_order = [str(p.id) for p in expected_location_order]

    await persist_test_data(
        db_session,
        {day: [(100, location.id) for location in locations] for day in days},
    )

    filters = dict(project_id=project.id, **date_filters)

    location_risks = await execute_location_risk_by_date(execute_gql, **filters)
    fetched_locations = [loc_risk["location"] for loc_risk in location_risks]
    fetched_ids = [fetched["id"] for fetched in fetched_locations]

    assert len(locations) == len(fetched_locations)
    assert fetched_ids == expected_id_order

    # test again, specifying locations this time
    filters = dict(
        **filters,
        location_ids=[loc.id for loc in locations],
    )

    location_risks = await execute_location_risk_by_date(execute_gql, **filters)
    fetched_locations = [loc_risk["location"] for loc_risk in location_risks]
    fetched_ids = [fetched["id"] for fetched in fetched_locations]

    assert len(locations) == len(fetched_locations)
    assert fetched_ids == expected_id_order


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_planning_location_risk_respects_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Tests that location risk levels are returned w/ respect to project start/end dates.
    """
    [day1, day2, day3] = [
        datetime.now(timezone.utc) + timedelta(days=n) for n in range(3)
    ]

    (activity1, project1, location1) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day1, "end_date": day2}
    )
    (activity2, project2, location2) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"start_date": day2, "end_date": day3}
    )
    await TaskFactory.persist(
        db_session,
        project_id=project1.id,
        activity_id=activity1.id,
        location_id=location1.id,
        start_date=day1,
        end_date=day2,
    )
    await TaskFactory.persist(
        db_session,
        project_id=project2.id,
        activity_id=activity2.id,
        location_id=location2.id,
        start_date=day2,
        end_date=day3,
    )

    filters = dict(start_date=day1, end_date=day3)

    await persist_test_data(
        db_session,
        {
            day1: [(99, location1.id), (105, location2.id)],
            day2: [(100, location1.id), (105, location2.id)],
            day3: [(249, location1.id), (250, location2.id)],
        },
    )

    # fetch for project 1
    await assert_location_risk(
        execute_gql,
        filters={**filters, "project_id": project1.id},
        expected_data={
            day1: {RiskLevel.LOW.name: 1},
            day2: {RiskLevel.MEDIUM.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "project_id": project1.id},
        expected_data={
            location1.id: {
                day1: RiskLevel.LOW.name,
                day2: RiskLevel.MEDIUM.name,
                # no day 3
            },
        },
    )

    # fetch for project 2
    await assert_location_risk(
        execute_gql,
        filters={**filters, "project_id": project2.id},
        expected_data={
            day2: {RiskLevel.MEDIUM.name: 1},
            day3: {RiskLevel.HIGH.name: 1},
        },
    )
    await assert_location_risk_by_date(
        execute_gql,
        filters={**filters, "project_id": project2.id},
        expected_data={
            location2.id: {
                # no day 1
                day2: RiskLevel.MEDIUM.name,
                day3: RiskLevel.HIGH.name,
            },
        },
    )
