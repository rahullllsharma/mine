from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    gql_control,
    gql_hazard,
    gql_task,
)
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
    diffs_by_object_type,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    AuditObjectType,
)

edit_task_mutation = {
    "operation_name": "EditTask",
    "query": """
mutation EditTask($task: EditTaskInput!) {
  task: editTask(taskData: $task) { id hazards {id controls { id} }}
}
""",
}

delete_task_mutation = {
    "operation_name": "DeleteTask",
    "query": """
mutation DeleteTask($id: UUID!) { task: deleteTask(id: $id) }
""",
}


################################################################################
# Edit Task
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_hazard_and_control_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Asserts that updating a task, hazard, and control result in the expected
    audit_event and audit_event_diffs.
    """

    control, _, _, task, hazard = await TaskControlFactory.with_relations(db_session)
    hazard.position = 0  # not relevant to our diff
    control.position = 0  # not relevant to our diff
    hazard.user_id = None  # clear user so we can toggle applicable
    control.user_id = None  # clear user so we can toggle applicable
    await db_session.commit()
    await db_session.refresh(hazard)
    await db_session.refresh(control)
    await db_session.refresh(task)

    new_hazard_is_applicable = not hazard.is_applicable
    new_control_is_applicable = not control.is_applicable

    old_hazard_is_applicable = hazard.is_applicable
    old_control_is_applicable = control.is_applicable

    updated_control = {
        **gql_control(control),
        "isApplicable": new_control_is_applicable,
    }
    updated_hazard = {
        **gql_hazard(hazard),
        "isApplicable": new_hazard_is_applicable,
        "controls": [updated_control],
    }
    updated_task = {
        **gql_task(task),
        "hazards": [updated_hazard],
    }
    user = await AdminUserFactory.persist(db_session)
    await execute_gql(user=user, **edit_task_mutation, variables={"task": updated_task})

    events = await audit_events_for_object(db_session, str(control.id))

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.task_updated

    assert len(await db_data.audit_event_diffs(event.id)) == 2
    diffs_by_type = await diffs_by_object_type(db_session, event)
    assert AuditObjectType.task not in diffs_by_type
    hazard_diff = diffs_by_type[AuditObjectType.task_hazard][0]
    control_diff = diffs_by_type[AuditObjectType.task_control][0]

    assert hazard_diff.old_values == {"is_applicable": old_hazard_is_applicable}
    assert hazard_diff.new_values == {"is_applicable": new_hazard_is_applicable}

    assert control_diff.old_values == {"is_applicable": old_control_is_applicable}
    assert control_diff.new_values == {"is_applicable": new_control_is_applicable}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_creating_new_hazard_and_control_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Tests that newly created hazards and controls are audited correctly.

    Creates an audit event with 4 diffs: update_task, update_hazard, create_hazard,
    and create_control.
    """

    user = await AdminUserFactory.persist(db_session)

    task = await TaskFactory.persist(db_session)
    new_hazard = await TaskHazardFactory.persist(
        db_session, is_applicable=True, user_id=None
    )
    new_control = await TaskControlFactory.persist(
        db_session, task_hazard_id=new_hazard.id, is_applicable=True
    )
    hazard = await TaskHazardFactory.persist(
        db_session, task_id=task.id, position=0, is_applicable=True
    )
    control = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=hazard.id,
        position=0,
        is_applicable=True,
    )

    await db_session.refresh(task)
    await db_session.refresh(hazard)
    await db_session.refresh(control)
    await db_session.refresh(new_hazard)
    await db_session.refresh(new_control)

    # exclude 'id' here to create new hazard, control
    new_hazard_and_control = {
        **gql_hazard(new_hazard.dict(exclude={"id"})),
        "controls": [{**gql_control(new_control.dict(exclude={"id"}))}],
    }
    updated_hazard = {
        **gql_hazard(hazard),
        "controls": [{**gql_control(control)}],
    }

    updated_task = {
        **gql_task(task),
        # order mattered here for reproducing the missing relations bug,
        # due to the .positions set above
        "hazards": [new_hazard_and_control, updated_hazard],
    }

    data = await execute_gql(
        user=user, **edit_task_mutation, variables={"task": updated_task}
    )

    task_data = data["task"]
    events = await audit_events_for_object(db_session, str(hazard.id))

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.task_updated

    assert len(await db_data.audit_event_diffs(event.id)) == 3
    diffs_by_type = await diffs_by_object_type(db_session, event)
    assert AuditObjectType.task not in diffs_by_type
    hazard_diffs = diffs_by_type[AuditObjectType.task_hazard]
    assert len(hazard_diffs) == 2  # one created, one updated
    control_diff = diffs_by_type[AuditObjectType.task_control][0]

    new_hazard_diff = list(
        filter(lambda x: x.diff_type == AuditDiffType.created, hazard_diffs)
    )[0]
    updated_hazard_diff = list(
        filter(lambda x: x.diff_type == AuditDiffType.updated, hazard_diffs)
    )[0]

    assert new_hazard_diff.old_values is None
    await db_session.refresh(new_hazard)
    expected_new_vals = jsonable_encoder(
        {
            **new_hazard.dict(exclude={"id"}),
            "task_id": task_data["id"],
            "user_id": user.id,
            "position": 0,  # was given first position b/c it was first in the list
        }
    )
    assert new_hazard_diff.new_values == expected_new_vals

    assert updated_hazard_diff.old_values == {"position": 0}
    assert updated_hazard_diff.new_values == {"position": 1}

    assert control_diff.old_values is None
    await db_session.refresh(new_control)
    expected_new_vals = jsonable_encoder(
        {
            **new_control.dict(exclude={"id"}),
            "task_hazard_id": task_data["hazards"][0]["id"],
            "user_id": user.id,
            "position": 0,
        }
    )
    assert control_diff.new_values == expected_new_vals


################################################################################
# Delete Task
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Asserts that deleting a task results in the expected audit_event and
    audit_event_diffs.
    """
    _, _, _, task, _ = await TaskControlFactory.with_relations(db_session)

    # A second task must be created because you
    # cannot delete the last task an activity has
    await TaskFactory.persist(db_session, activity_id=task.activity_id)

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **delete_task_mutation, variables={"id": task.id}
    )

    assert data["task"]  # bool is returned
    events = await audit_events_for_object(db_session, task.id)

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.task_archived

    assert len(await db_data.audit_event_diffs(event.id)) == 3
    diffs_by_type = await diffs_by_object_type(db_session, event)
    assert set(diffs_by_type.keys()) == {
        AuditObjectType.task,
        AuditObjectType.task_hazard,
        AuditObjectType.task_control,
    }

    # ensure the objs still exist in the db, and have archived_at set
    for d in await db_data.audit_event_diffs(event.id):
        assert d.diff_type == AuditDiffType.archived
        assert d.new_values
        assert d.old_values
        assert ["archived_at"] == list(d.new_values.keys())
        assert ["archived_at"] == list(d.old_values.keys())
        assert_recent_datetime(datetime.fromisoformat(d.new_values["archived_at"]))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task_audit_fail_when_only_task(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Asserts that deleting a task when it is the only task for an
    activity fails with an error message
    """
    _, _, _, task, _ = await TaskControlFactory.with_relations(db_session)
    user = await AdminUserFactory.persist(db_session)

    with pytest.raises(Exception) as e:
        await execute_gql(user=user, **delete_task_mutation, variables={"id": task.id})
    e.match("Cannot delete this activity's only task!")
