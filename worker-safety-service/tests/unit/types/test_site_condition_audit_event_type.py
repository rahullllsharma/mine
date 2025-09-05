from datetime import date, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest

from worker_safety_service.audit_events.dataclasses import (
    AuditEventTypeInput,
    ProjectDiff,
)
from worker_safety_service.graphql.data_loaders.audits import build_audit_trail
from worker_safety_service.graphql.types import AuditActionType
from worker_safety_service.models import (
    AuditDiffType,
    AuditEventDiff,
    AuditObjectType,
    Location,
    SiteCondition,
    User,
    WorkPackage,
)
from worker_safety_service.models.audit_events import AuditEvent
from worker_safety_service.models.library import LibrarySiteCondition


def _setup_diff(
    project_id: UUID | None = None,
    location: Location | None = None,
    library_site_condition: LibrarySiteCondition | None = None,
    site_condition_id: UUID | None = None,
    user: User | None = None,
    event: AuditEvent | None = None,
    diff_type: AuditDiffType = AuditDiffType.updated,
    old_values: dict[str, Any] = {"start_date": "x", "end_date": "y"},
    new_values: dict[str, Any] = {"start_date": "A", "end_date": "B"},
    created_at: datetime = datetime.now(),
) -> ProjectDiff:
    if project_id is None:
        project_id = uuid4()
    today = date.today()
    project = WorkPackage(
        id=project_id, name="test project", start_date=today, end_date=today, number=1
    )
    if location is None:
        location = Location(
            id=uuid4(),
            name="test location",
            project_id=project.id,
            project=project,
            clustering=[],
        )
    if library_site_condition is None:
        library_site_condition = LibrarySiteCondition(
            id=uuid4(), name="test library site_condition", handle_code="test_1"
        )
    if site_condition_id is None:
        site_condition_id = uuid4()
    site_condition = SiteCondition(
        id=site_condition_id,
        library_site_condition_id=library_site_condition.id,
        library_site_condition=library_site_condition,
        is_manually_added=False,
    )
    if user is None:
        user = User(
            id=uuid4(),
            first_name="test",
            last_name="name",
            email="1",
        )
    if event is None:
        event = AuditEvent(
            id=uuid4(),
            event_type=AuditObjectType.site_condition,
            user_id=user.id,
            user=user,
            created_at=created_at,
        )

    diff = AuditEventDiff(
        event_id=event.id,
        event=event,
        object_type=AuditObjectType.site_condition,
        object_id=site_condition.id,
        diff_type=diff_type,
        old_values=old_values,
        new_values=new_values,
        created_at=created_at,
    )

    return ProjectDiff(
        project_id=project_id,
        user=user,
        diff=diff,
    )


def assert_diff(
    audit_type: AuditEventTypeInput,
    site_condition_diff: ProjectDiff,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    action_type: AuditActionType = AuditActionType.UPDATED,
) -> None:
    assert audit_type.diff.diff == site_condition_diff.diff
    assert audit_type.field_name == field_name
    if audit_type.diff_values is not None:
        assert audit_type.diff_values.old_value == old_value
        assert audit_type.diff_values.new_value == new_value


@pytest.mark.unit
def test_audit_event_type_from_site_condition_diffs() -> None:
    diff_1 = _setup_diff()
    diff_2 = _setup_diff(
        project_id=diff_1.project_id,
        site_condition_id=diff_1.diff.object_id,
    )

    site_condition_diffs = [diff_1, diff_2]

    diffs = build_audit_trail(site_condition_diffs)

    assert len(diffs) == 2
    assert diffs[0].diff.diff.event_id == diff_1.diff.event_id
    assert diffs[1].diff.diff.event_id == diff_2.diff.event_id


@pytest.mark.unit
def test_audit_event_type_from_site_condition_diffs_one_on_created() -> None:
    """
    only one AuditEventType should be created on created ProjectDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.created)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.CREATED)


@pytest.mark.unit
def test_audit_event_type_from_site_condition_diffs_one_on_deleted() -> None:
    """
    only one AuditEventType should be created on deleted ProjectDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.deleted)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.DELETED)


@pytest.mark.unit
def test_audit_event_type_from_site_condition_diffs_one_on_archived() -> None:
    """
    only one AuditEventType should be created on archived ProjectDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.archived)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.DELETED)
