from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tests.factories import DailyReportFactory, LocationFactory, SupervisorUserFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import (
    execute_get_report,
    execute_list_reports,
    execute_update_status_report,
)
from worker_safety_service.models import AsyncSession, FormStatus


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_reports_hides_archived(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()
    reports = await DailyReportFactory.persist_many(
        db_session,
        size=4,
        project_location_id=location.id,
        date_for=date,
        sections="{}",
    )
    to_archive = reports.pop(-1)

    response = await execute_list_reports(
        execute_gql=execute_gql, project_location_id=location.id, date=date
    )
    # Assert returns all reports
    assert len(response) == 4

    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    # Assert doesn't return archived
    response = await execute_list_reports(
        execute_gql=execute_gql, project_location_id=location.id, date=date
    )
    assert len(response) == 3
    expected_ids = [str(r.id) for r in reports]
    assert response[0]["id"] in expected_ids
    assert response[1]["id"] in expected_ids
    assert response[2]["id"] in expected_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_fetch_by_status(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(db_session)
    date = datetime.now(timezone.utc).date()
    shared_args = dict(project_location_id=location.id, date_for=date, sections="{}")
    in_progress_id = str(
        (
            await DailyReportFactory.persist(
                db_session, status=FormStatus.IN_PROGRESS, **shared_args
            )
        ).id
    )
    completed_id = str(
        (
            await DailyReportFactory.persist(
                db_session, status=FormStatus.COMPLETE, **shared_args
            )
        ).id
    )

    # Should work with status filter
    response = await execute_get_report(execute_gql, in_progress_id)
    assert response["id"] == in_progress_id
    response = await execute_get_report(
        execute_gql, in_progress_id, status=FormStatus.IN_PROGRESS
    )
    assert response["id"] == in_progress_id
    response = await execute_get_report(execute_gql, completed_id)
    assert response["id"] == completed_id
    response = await execute_get_report(
        execute_gql, completed_id, status=FormStatus.COMPLETE
    )
    assert response["id"] == completed_id

    # Should give NULL if not found
    response = await execute_get_report(execute_gql, uuid4())
    assert response is None
    response = await execute_get_report(
        execute_gql, in_progress_id, status=FormStatus.COMPLETE
    )
    assert response is None
    response = await execute_get_report(
        execute_gql, completed_id, status=FormStatus.IN_PROGRESS
    )
    assert response is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_completions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Arrange
    user = await SupervisorUserFactory.persist(db_session)
    other_user = await SupervisorUserFactory.persist(db_session)
    report = await DailyReportFactory.persist(db_session)
    await execute_update_status_report(
        execute_gql, report.id, FormStatus.COMPLETE, user=user
    )
    await db_session.refresh(report)
    completed_at = report.completed_at
    await execute_update_status_report(
        execute_gql, report.id, FormStatus.IN_PROGRESS, user=user
    )
    await execute_update_status_report(
        execute_gql, report.id, FormStatus.COMPLETE, user=user
    )
    await execute_update_status_report(
        execute_gql, report.id, FormStatus.IN_PROGRESS, user=user
    )
    await execute_update_status_report(
        execute_gql, report.id, FormStatus.COMPLETE, user=other_user
    )

    # Act
    response = await execute_get_report(execute_gql, report.id)

    # Assert
    assert completed_at
    completions = response["sections"]["completions"]
    assert len(completions) == 3

    assert completions[0]["completedBy"]["id"] == str(user.id)
    assert completions[0]["completedAt"] == completed_at.isoformat()

    assert completions[1]["completedBy"]["id"] == str(user.id)
    assert datetime.fromisoformat(completions[1]["completedAt"]) > completed_at

    assert completions[2]["completedBy"]["id"] == str(other_user.id)
    assert datetime.fromisoformat(
        completions[2]["completedAt"]
    ) > datetime.fromisoformat(completions[1]["completedAt"])
