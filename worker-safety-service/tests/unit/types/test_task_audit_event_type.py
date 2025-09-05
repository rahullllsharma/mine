import random
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
    Task,
    User,
    WorkPackage,
)
from worker_safety_service.models.audit_events import AuditEvent
from worker_safety_service.models.library import LibraryTask


def _setup_diff(
    project_id: UUID | None = None,
    location: Location | None = None,
    library_task: LibraryTask | None = None,
    task_id: UUID | None = None,
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
    if library_task is None:
        library_task = LibraryTask(
            id=uuid4(),
            name="test library task",
            unique_task_id="RANDOM_TASK_" + str(random.randint(0, 10_000)),
        )
    if task_id is None:
        task_id = uuid4()
    task = Task(id=task_id, library_task_id=library_task.id, library_task=library_task)
    if user is None:
        user = User(
            id=uuid4(),
            first_name="test",
            last_name="name",
            email="1",
        )
    if event is None:
        event = AuditEvent(
            id=uuid4(), user_id=user.id, user=user, created_at=created_at
        )

    diff = AuditEventDiff(
        event_id=event.id,
        event=event,
        object_type=AuditObjectType.task,
        object_id=task.id,
        diff_type=diff_type,
        old_values=old_values,
        new_values=new_values,
        created_at=created_at,
    )

    return ProjectDiff(
        project_id=project.id,
        user=user,
        diff=diff,
    )


def assert_diff(
    audit_type: AuditEventTypeInput,
    task_diff: ProjectDiff,
    field_name: str | None = None,
    old_value: str | None = None,
    new_value: str | None = None,
    action_type: AuditActionType = AuditActionType.UPDATED,
) -> None:
    assert audit_type.diff.diff == task_diff.diff
    assert audit_type.field_name == field_name
    if audit_type.diff_values is not None:
        assert audit_type.diff_values.old_value == old_value
        assert audit_type.diff_values.new_value == new_value


@pytest.mark.unit
def test_audit_event_type_parse_diff_handles_new_old_on_update() -> None:
    """
    test AuditEventType is created for each old_values and new_values key on updates
    """
    task_diff = _setup_diff()

    parsed = build_audit_trail([task_diff])
    assert len(parsed) == 2
    # TODO: remove this when ordering is implemented
    parsed = sorted(parsed, key=lambda x: x.field_name or x.diff.diff.event_id)

    assert_diff(
        parsed[0], task_diff, field_name="end_date", old_value="y", new_value="B"
    )
    assert_diff(
        parsed[1], task_diff, field_name="start_date", old_value="x", new_value="A"
    )


@pytest.mark.unit
def test_audit_event_type_from_task_diffs() -> None:
    diff_1 = _setup_diff()
    diff_2 = _setup_diff(
        project_id=diff_1.project_id,
        task_id=diff_1.diff.object_id,
    )

    task_diffs = [diff_1, diff_2]

    diffs = build_audit_trail(task_diffs)

    assert len(diffs) == 4
    assert diffs[0].diff.diff.event_id == diff_1.diff.event_id
    assert diffs[1].diff.diff.event_id == diff_1.diff.event_id
    assert diffs[2].diff.diff.event_id == diff_2.diff.event_id
    assert diffs[3].diff.diff.event_id == diff_2.diff.event_id


@pytest.mark.unit
def test_audit_event_type_from_task_diffs_one_on_created() -> None:
    """
    only one AuditEventType should be created on created taskDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.created)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.CREATED)


@pytest.mark.unit
def test_audit_event_type_from_task_diffs_one_on_deleted() -> None:
    """
    only one AuditEventType should be created on deleted taskDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.deleted)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.DELETED)


@pytest.mark.unit
def test_audit_event_type_from_task_diffs_one_on_archived() -> None:
    """
    only one AuditEventType should be created on archived taskDiff.diff
    """
    diff = _setup_diff(diff_type=AuditDiffType.archived)
    diffs = build_audit_trail([diff])
    assert len(diffs) == 1
    assert_diff(diffs[0], diff, action_type=AuditActionType.DELETED)


@pytest.mark.unit
def test_audit_event_type_from_task_diffs_unknown_field_name() -> None:
    """
    unkown field_names should be ignored
    """
    diff = _setup_diff(
        old_values={"unknown_v": "x"},
        new_values={"unknown_v": "A"},
    )
    diffs = build_audit_trail([diff])
    assert len(diffs) == 0
