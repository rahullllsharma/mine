from datetime import datetime, timezone

import pytest

from tests.factories import DailyReportFactory, LocationFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, Location

project_with_locations_and_daily_reports_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($projectId: UUID!) {
  project(projectId: $projectId) {
    id name locations { id dailyReports { id } }
  }
}
""",
}

all_locations_with_daily_reports_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($id: UUID!) {
  projectLocations(id: $id) {
    id dailyReports {id}
  }
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_query_with_project_location_and_daily_reports_hides_archived(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location: Location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()
    reports = await DailyReportFactory.persist_many(
        db_session,
        size=4,
        project_location_id=location.id,
        date_for=date,
        sections="{}",
    )
    to_archive = reports.pop(-1)

    response = await execute_gql(
        **project_with_locations_and_daily_reports_query,
        variables={"projectId": str(location.project_id)},
    )

    assert response["project"]["id"] == str(location.project_id)
    assert len(response["project"]["locations"]) == 1
    assert len(response["project"]["locations"][0]["dailyReports"]) == 4

    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await execute_gql(
        **project_with_locations_and_daily_reports_query,
        variables={"projectId": str(location.project_id)},
    )
    assert len(response["project"]["locations"][0]["dailyReports"]) == 3
    returned_report_ids = {
        r["id"] for r in response["project"]["locations"][0]["dailyReports"]
    }
    expected_ids = {str(r.id) for r in reports}
    assert returned_report_ids == expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_location_query_with_daily_reports_hides_archived(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location: Location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()
    reports = await DailyReportFactory.persist_many(
        db_session,
        size=4,
        project_location_id=location.id,
        date_for=date,
        sections="{}",
    )
    to_archive = reports.pop(-1)

    response = await execute_gql(
        **all_locations_with_daily_reports_query, variables={"id": str(location.id)}
    )

    assert len(response["projectLocations"]) == 1
    assert response["projectLocations"][0]["id"] == str(location.id)
    assert len(response["projectLocations"][0]["dailyReports"]) == 4

    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    response = await execute_gql(
        **all_locations_with_daily_reports_query, variables={"id": str(location.id)}
    )

    assert len(response["projectLocations"][0]["dailyReports"]) == 3
    returned_report_ids = {
        r["id"] for r in response["projectLocations"][0]["dailyReports"]
    }
    expected_ids = {str(r.id) for r in reports}
    assert returned_report_ids == expected_ids
