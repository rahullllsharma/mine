from datetime import datetime, timedelta, timezone

import pytest

from tests.db_data import DBData
from tests.factories import DailyReportFactory, LocationFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, User


def dir_data(
    fm: str = "bob",
    c: str = "bob's builders",
    sid: str = "1",
    stype: str = "1",
    steps: str = "1, 2, 3",
    pha: bool = True,
) -> dict:
    return {
        "crew": {
            "foreman_name": fm,
            "contractor": c,
        },
        "safety_and_compliance": {
            "systemOperatingProcedures": {
                "sopId": sid,
                "sopType": stype,
                "sopStepsCalledIn": steps,
            },
            "plans": {
                "comprehensivePHAConducted": pha,
            },
        },
    }


recommendation_gql = {
    "operation_name": "DailyReportRecommendation",
    "query": """
        query DailyReportRecommendation($projectLocationId: UUID!) {
          recommendations {
            dailyReport(projectLocationId: $projectLocationId) {
              crew {
                constructionCompany
                foremanName
              }
              safetyAndCompliance {
                phaCompletion
                sopNumber
                sopType
                stepsCalledIn
              }
            }
          }
        }
    """,
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_recommended_daily_report_excludes_other_users(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()

    assert location.project_id
    project = await db_data.project(
        project_id=location.project_id, load_contractor=True
    )
    assert project.contractor
    shared_args = dict(project_location_id=location.id, date_for=date)
    _ = await DailyReportFactory.persist(db_session, sections=dir_data(), **shared_args)

    recommendation = await execute_gql(
        **recommendation_gql,
        variables={"projectLocationId": location.id},
    )

    assert "recommendations" in recommendation
    assert "dailyReport" in recommendation["recommendations"]
    # recommendation defaults to project contractor name only
    report = recommendation["recommendations"]["dailyReport"]
    assert report["safetyAndCompliance"] is None
    assert report["crew"]["foremanName"] is None
    assert report["crew"]["constructionCompany"] == project.contractor.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_recommended_daily_report_with_no_reports(
    execute_gql: ExecuteGQL, db_session: AsyncSession, db_data: DBData
) -> None:
    location = await LocationFactory.persist(db_session)
    assert location.project_id
    project = await db_data.project(
        project_id=location.project_id, load_contractor=True
    )
    assert project.contractor
    recommendation = await execute_gql(
        **recommendation_gql,
        variables={"projectLocationId": location.id},
    )

    assert "recommendations" in recommendation
    assert "dailyReport" in recommendation["recommendations"]
    # recommendation defaults to project contractor name only
    report = recommendation["recommendations"]["dailyReport"]
    assert report["safetyAndCompliance"] is None
    assert report["crew"]["foremanName"] is None
    assert report["crew"]["constructionCompany"] == project.contractor.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_recommended_daily_report_gets_data(
    execute_gql: ExecuteGQL, db_session: AsyncSession, test_user: User
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()

    shared_args = dict(
        project_location_id=location.id,
        date_for=date,
        created_by_id=test_user.id,
        status="complete",
    )
    completed_at = datetime.now()
    _ = await DailyReportFactory.persist(
        db_session, sections=dir_data(), **shared_args, completed_at=completed_at
    )
    _ = await DailyReportFactory.persist(
        db_session,
        sections=dir_data(fm="charlie"),
        **shared_args,
        completed_at=completed_at + timedelta(seconds=30),
    )

    recommendation = await execute_gql(
        **recommendation_gql,
        variables={"projectLocationId": location.id},
        user=test_user,
    )

    assert "recommendations" in recommendation
    assert "dailyReport" in recommendation["recommendations"]
    assert recommendation["recommendations"]["dailyReport"] is not None
    dr = recommendation["recommendations"]["dailyReport"]
    crew = dr["crew"]
    snc = dr["safetyAndCompliance"]
    assert crew["foremanName"] == "charlie"
    assert crew["constructionCompany"] == "bob's builders"
    assert snc["phaCompletion"] == "true"
    assert snc["sopNumber"] == "1"
    assert snc["sopType"] == "1"
    assert snc["stepsCalledIn"] == "1, 2, 3"
