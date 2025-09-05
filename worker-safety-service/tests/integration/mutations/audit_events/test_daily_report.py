from datetime import datetime
from uuid import UUID

import jsonpatch
import pytest

from tests.db_data import DBData
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import (
    build_report_data,
    execute_delete_report,
    execute_report,
    execute_update_status_report,
)
from tests.integration.helpers import assert_recent_datetime
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
)
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.models import AsyncSession, AuditEventType, FormStatus, User


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report(
    test_user: User,
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    daily_report_manager: DailyReportManager,
    db_data: DBData,
) -> None:
    """Assert the daily report create, update, archive flow is audited"""

    report_request, *_ = await build_report_data(db_session)
    # create daily report audit
    response = await execute_report(execute_gql, report_request)

    sections = {
        "workSchedule": {
            "endDatetime": "2022-03-24T04:14:00.000",
            "startDatetime": "2022-03-24T02:12:00.000",
            "sectionIsValid": True,
        },
        "taskSelection": {"selectedTasks": [], "sectionIsValid": True},
        "jobHazardAnalysis": {
            "tasks": [],
            "siteConditions": [],
            "sectionIsValid": True,
        },
    }

    report_request.update(**sections, id=response["id"])
    # update_data audit
    response = await execute_report(execute_gql, report_request)

    # update_status audit
    response = await execute_update_status_report(
        execute_gql, response["id"], FormStatus.COMPLETE, user=test_user
    )
    # archive audit
    await execute_delete_report(execute_gql, response["id"])

    audits = sorted(
        await audit_events_for_object(db_session, response["id"]),
        key=lambda audit: audit.created_at,
    )
    for event in audits:
        await assert_created_at(db_session, event)
    create, update_data, update_status, archive = audits
    # check the audit logs are of the expected type
    assert create.event_type == AuditEventType.daily_report_created
    assert (
        update_data.event_type
        == update_status.event_type
        == AuditEventType.daily_report_updated
    )
    assert archive.event_type == AuditEventType.daily_report_archived

    # check we can get from an "empty" section to the latest section
    # ignore mypy checks on optional types for this test
    # the objects should all exist (or this test case should not pass)
    # the update_status needs to be patched due to completions field
    new_sections: dict = {}
    create_diffs = await db_data.audit_event_diffs(create.id)
    create_sections = create_diffs[0].new_values["sections"]  # type: ignore
    new_sections = jsonpatch.JsonPatch(create_sections).apply(new_sections)
    update_data_diffs = await db_data.audit_event_diffs(update_data.id)
    update_data_sections = update_data_diffs[0].new_values["sections"]  # type: ignore
    new_sections = jsonpatch.JsonPatch(update_data_sections).apply(new_sections)
    update_status_diffs = await db_data.audit_event_diffs(update_status.id)
    update_status_sections = update_status_diffs[0].new_values["sections"]  # type: ignore
    new_sections = jsonpatch.JsonPatch(update_status_sections).apply(new_sections)
    dr = await daily_report_manager.get_daily_report(UUID(response["id"]))
    assert dr.sections == new_sections  # type: ignore

    # verify archived_at set on archive diff
    archive_diffs = await db_data.audit_event_diffs(archive.id)
    assert "archived_at" in archive_diffs[0].new_values  # type: ignore
    archived_at = archive_diffs[0].new_values["archived_at"]  # type: ignore
    assert archived_at is not None
    assert_recent_datetime(datetime.fromisoformat(archived_at))
