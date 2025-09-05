import asyncio
import dataclasses
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest

from tests.factories import (
    ActivityFactory,
    DailyReportFactory,
    JobSafetyBriefingFactory,
    LocationFactory,
    SiteConditionFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.dal.risk_model import RiskModelMetricsManager
from worker_safety_service.models import (
    AsyncSession,
    Location,
    SiteCondition,
    WorkPackage,
)
from worker_safety_service.risk_model.metrics.project.total_project_location_risk_score import (
    TotalProjectLocationRiskScore,
)
from worker_safety_service.types import Point

filter_location_daily_reports_date_range_query = {
    "operation_name": "MyQuery",
    "query": """
query MyQuery($id: UUID!, $start_date: Date!, $end_date: Date!) {
  filterLocationDateRange(id: $id) {
    locationsCount
    filterLocationsDateRange {
      dailyReports(filterDateRange: {startDate: $start_date, endDate: $end_date}) {
        date
        dailyReports {
          id
          date
          createdAt
          completedAt
          status
          updatedAt
        }
      }
    }
}
}
""",
}

filter_location_jsb_date_range_query = {
    "operation_name": "MyQuery",
    "query": """
query MyQuery($id: UUID!, $start_date: Date!, $end_date: Date!) {
  filterLocationDateRange(id: $id) {
  locationsCount
  filterLocationsDateRange{
    jobSafetyBriefings(
      filterDateRange: {startDate: $start_date, endDate: $end_date}
    ) {
        date
        jobSafetyBriefings{
          id
          date
          createdAt
          completedAt
          status
          updatedAt
        }
      }
    }
}
}
""",
}


filter_location_site_conditions_date_range_query = {
    "operation_name": "MyQuery",
    "query": """
query MyQuery($id: UUID!, $start_date: Date!, $end_date: Date!) {
  filterLocationDateRange(id: $id) {
    locationsCount
    filterLocationsDateRange{
    datedSiteConditions(
      filterDateRange: {startDate: $start_date, endDate: $end_date}
    ) {
        date
        siteConditions {
            id
            isManuallyAdded
            name
        }
    }
  }
}
}
""",
}

filter_location_tasks_risks_query = {
    "operation_name": "MyQuery",
    "query": """
query MyQuery($id: UUID!, $start_date: Date!, $end_date: Date!) {
  filterLocationDateRange(id: $id) {
    locationsCount
    filterLocationsDateRange{
    riskLevels(
      filterDateRange: {startDate: $start_date, endDate: $end_date}
    ) {
        date
        riskLevel
    }
  }
}
}
""",
}


filter_location_date_range_map_extent = {
    "operation_name": "MyQuery",
    "query": """
    query MyQuery($x_max: Float!, $x_min: Float!, $y_max: Float!, $y_min: Float!) {
    filterLocationDateRange(mapExtent: {xMin: $x_min, xMax: $x_max, yMax: $y_max, yMin: $y_min}) {
        locationsCount
        filterLocationsDateRange {
          name
          latitude
          longitude
          id
    }
    }
}
""",
}


filter_location_date_range_without_map_extent = {
    "operation_name": "MyQuery",
    "query": """
    query MyQuery{
    filterLocationDateRange{
      locationsCount
      filterLocationsDateRange {
          id
      }
    }
}
""",
}


@dataclasses.dataclass
class LocationInit:
    project_location: Location


@pytest.fixture
async def create_single_locations_daily_report(
    db_session: AsyncSession,
) -> AsyncGenerator[LocationInit, None]:
    # create location
    project_location: Location = await LocationFactory.persist(db_session)

    yield LocationInit(project_location=project_location)

    # delete location

    await db_session.delete(project_location)


@pytest.fixture
async def create_single_locations_job_safety_briefing(
    db_session: AsyncSession,
) -> AsyncGenerator[LocationInit, None]:
    # create location
    project_location: Location = await LocationFactory.persist(db_session)

    yield LocationInit(project_location=project_location)

    # delete location

    await db_session.delete(project_location)


@pytest.fixture
async def create_single_locations_site_conditions(
    db_session: AsyncSession,
) -> AsyncGenerator[LocationInit, None]:
    # create location
    project_location: Location = await LocationFactory.persist(db_session)

    yield LocationInit(project_location=project_location)

    # delete location

    await db_session.delete(project_location)


@pytest.fixture
async def create_single_locations_risk_levels(
    db_session: AsyncSession,
) -> AsyncGenerator[LocationInit, None]:
    # create location
    project_location: Location = await LocationFactory.persist(db_session)

    yield LocationInit(project_location=project_location)

    # delete location

    await db_session.delete(project_location)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_location_date_range_daily_reports(
    execute_gql: ExecuteGQL,
    create_single_locations_daily_report: LocationInit,
    db_session: AsyncSession,
) -> None:
    location = create_single_locations_daily_report.project_location
    # Set configurable start_date and end_date as datetime objects
    start_date = datetime(2024, 1, 15, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 17, tzinfo=timezone.utc)

    start_date_reports = await DailyReportFactory.persist_many(
        db_session,
        size=4,
        project_location_id=location.id,
        date_for=start_date,
        sections="{}",
    )

    end_date_reports = await DailyReportFactory.persist_many(
        db_session,
        size=1,
        project_location_id=location.id,
        date_for=end_date,
        sections="{}",
    )
    new_date = end_date + timedelta(days=1)
    _ = await DailyReportFactory.persist_many(
        db_session,
        size=1,
        project_location_id=location.id,
        date_for=new_date,
        sections="{}",
    )
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    response = await execute_gql(
        **filter_location_daily_reports_date_range_query,
        variables={
            "id": str(location.id),
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
    )

    assert "filterLocationDateRange" in response
    filter_location_date_range = response["filterLocationDateRange"]
    assert len(filter_location_date_range) == 1  # It has only Daily Reports
    assert filter_location_date_range[0]["locationsCount"] == 1

    daily_reports = filter_location_date_range[0]["filterLocationsDateRange"][0][
        "dailyReports"
    ]

    for i, reports in enumerate(daily_reports):
        date_str = reports["date"]
        expected_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        daily_reports = reports["dailyReports"]
        if date_str == start_date_str:
            assert len(daily_reports) == len(start_date_reports)
        else:
            assert len(daily_reports) == len(end_date_reports)
        assert date_str == expected_date


@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_location_date_range_job_safety_briefings(
    execute_gql: ExecuteGQL,
    create_single_locations_job_safety_briefing: LocationInit,
    db_session: AsyncSession,
) -> None:
    location = create_single_locations_job_safety_briefing.project_location

    # Set configurable start_date and end_date as datetime objects
    start_date = datetime(2024, 1, 15, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 17, tzinfo=timezone.utc)

    start_date_reports = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=3,
        project_location_id=location.id,
        date_for=start_date,
    )

    end_date_reports = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=end_date,
    )

    new_date = end_date + timedelta(days=1)
    _ = await JobSafetyBriefingFactory.persist_many(
        db_session,
        size=2,
        project_location_id=location.id,
        date_for=new_date,
    )
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    response = await execute_gql(
        **filter_location_jsb_date_range_query,
        variables={
            "id": str(location.id),
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
    )

    assert "filterLocationDateRange" in response
    filter_location_date_range = response["filterLocationDateRange"]
    assert len(filter_location_date_range) == 1  # It has only JobSafetyBriefings
    assert filter_location_date_range[0]["locationsCount"] == 1

    job_safety_briefings = filter_location_date_range[0]["filterLocationsDateRange"][0][
        "jobSafetyBriefings"
    ]

    for i, briefings in enumerate(job_safety_briefings):
        date_str = briefings["date"]
        expected_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        job_safety_briefings = briefings["jobSafetyBriefings"]
        if date_str == start_date_str:
            assert len(job_safety_briefings) == len(start_date_reports)
        else:
            assert len(job_safety_briefings) == len(end_date_reports)
        assert date_str == expected_date


@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_location_date_range_site_conditions(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    create_single_locations_site_conditions: LocationInit,
) -> None:
    location = create_single_locations_site_conditions.project_location
    site_conditions: list[SiteCondition] = await SiteConditionFactory.persist_many(
        db_session, size=1, location_id=location.id
    )
    start_date = datetime(2024, 1, 10, tzinfo=timezone.utc)
    end_date = datetime(2024, 1, 17, tzinfo=timezone.utc)

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    response = await execute_gql(
        **filter_location_site_conditions_date_range_query,
        variables={
            "id": str(location.id),
            "start_date": start_date_str,
            "end_date": end_date_str,
        },
    )

    assert "filterLocationDateRange" in response
    filter_location_date_range = response["filterLocationDateRange"]
    assert len(filter_location_date_range) == 1

    dated_site_conditions = filter_location_date_range[0]["filterLocationsDateRange"][
        0
    ]["datedSiteConditions"]

    # Assert that there is one site condition for each date
    for i, dated_site_condition in enumerate(dated_site_conditions):
        date_str = dated_site_condition["date"]
        expected_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        site_conditions = dated_site_condition["siteConditions"]
        assert len(site_conditions) == 1
        assert date_str == expected_date


@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_location_date_range_risk_levels(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    create_single_locations_risk_levels: LocationInit,
    risk_model_metrics_manager: RiskModelMetricsManager,
) -> None:
    project_start_date = date(2024, 1, 1)
    project_end_date = date(2024, 1, 28)

    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, start_date=project_start_date, project_end_date=project_end_date
    )
    location = create_single_locations_risk_levels.project_location
    await ActivityFactory.persist_many_with_task(
        db_session,
        location_id=location.id,
        start_date=project.start_date,
        end_date=project.end_date,
        size=3,
    )

    dates: list[date] = [
        datetime(2024, 1, 10),
        datetime(2024, 1, 11),
        datetime(2024, 1, 12),
    ]
    await asyncio.gather(
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[0], 99
        ),
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[1], 100
        ),
        TotalProjectLocationRiskScore.store(
            risk_model_metrics_manager, location.id, dates[2], 250
        ),
    )

    # Execute
    async def execute_test(
        start_date: date, end_date: date, expected_risk_levels: list[str]
    ) -> None:
        post_data = {
            "operation_name": "MyQuery",
            "query": filter_location_tasks_risks_query["query"],
            "variables": {
                "id": str(location.id),
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
            },
        }
        data = await execute_gql(**post_data)

        # Extract risk levels from the received data
        risk_levels = data["filterLocationDateRange"][0]["filterLocationsDateRange"][0][
            "riskLevels"
        ]

        # Iterate through received risk levels and assert them

        for i, risk_level_data in enumerate(risk_levels):
            assert (
                risk_level_data["riskLevel"] == expected_risk_levels[i]
                or "RECALCULATING"
            )
            assert risk_level_data["date"] == (start_date + timedelta(days=i)).strftime(
                "%Y-%m-%d"
            )

    await execute_test(dates[0], dates[2], ["LOW", "MEDIUM", "HIGH"])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_location_date_range_map_extent(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create project

    name = f"New Package + {uuid.uuid4()}"
    await WorkPackageFactory.persist(db_session, name=name)

    # create 2 locations on the project

    await LocationFactory.persist(db_session, name="L1", geom=Point(5, 3))
    await LocationFactory.persist(db_session, name="L2")
    response_with_map_extent = await execute_gql(
        **filter_location_date_range_map_extent,
        variables={
            "x_min": 0,
            "x_max": 10,
            "y_max": 10,
            "y_min": 0,
        },
    )

    assert "filterLocationDateRange" in response_with_map_extent
    filter_location_date_range = response_with_map_extent["filterLocationDateRange"]
    assert len(filter_location_date_range) == 1  # It has only response
    assert filter_location_date_range[0]["locationsCount"] < 4
