import uuid
from typing import Any, Union

import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    TaskControlFactory,
    TaskControlFactoryUrbRec,
    TaskFactory,
    TaskHazardFactory,
    TaskHazardFactoryUrbRec,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    gql_control,
    gql_hazard,
    gql_task,
)
from worker_safety_service.models import AsyncSession, Task, TaskControl, TaskHazard


async def fetch_task(session: AsyncSession, id: Union[str, uuid.UUID]) -> Task:
    statement = select(Task).where(Task.id == id)
    return (await session.exec(statement)).one()


async def fetch_hazard(session: AsyncSession, id: Union[str, uuid.UUID]) -> TaskHazard:
    statement = select(TaskHazard).where(TaskHazard.id == id)
    return (await session.exec(statement)).one()


async def fetch_hazards(
    session: AsyncSession, task_id: Union[str, uuid.UUID]
) -> list[TaskHazard]:
    statement = select(TaskHazard).where(TaskHazard.task_id == task_id)
    return (await session.exec(statement)).all()


async def fetch_control(
    session: AsyncSession, id: Union[str, uuid.UUID]
) -> TaskControl:
    statement = select(TaskControl).where(TaskControl.id == id)
    return (await session.exec(statement)).one()


async def fetch_controls(
    session: AsyncSession, hazard_id: Union[str, uuid.UUID]
) -> list[TaskControl]:
    statement = select(TaskControl).where(TaskControl.task_hazard_id == hazard_id)
    return (await session.exec(statement)).all()


edit_task_mutation = {
    "operation_name": "EditTask",
    "query": """
mutation EditTask($task: EditTaskInput!) {
  task: editTask(taskData: $task) { id hazards {id isApplicable controls {id isApplicable}}}
}
""",
}


################################################################################
# Edit Task Hazards
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_hazard(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard's is_applicable field can be toggled.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(
        db_session,
        task_id=task.id,
    )
    await db_session.refresh(task)
    new_is_applicable = not hazard.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "isApplicable": new_is_applicable,
    }
    data = await execute_gql(
        **edit_task_mutation,
        variables={"task": {**gql_task(task), "hazards": [updated_hazard]}},
    )

    assert data["task"]["id"] == str(task.id)
    assert data["task"]["hazards"][0]["id"] == str(hazard.id)
    assert data["task"]["hazards"][0]["isApplicable"] == new_is_applicable

    await db_session.refresh(hazard)
    assert hazard.is_applicable == new_is_applicable


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_hazard_user_owned(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard's is_applicable field is not toggled if it has a user_id.
    """
    task: Task = await TaskFactory.persist(db_session)
    # allow a user_id to exist on this hazard
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    await db_session.refresh(task)
    new_is_applicable = not hazard.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        # attempt to update this value
        "isApplicable": new_is_applicable,
    }
    data = await execute_gql(
        **edit_task_mutation,
        variables={"task": {**gql_task(task), "hazards": [updated_hazard]}},
    )

    assert data["task"]["id"] == str(task.id)
    assert data["task"]["hazards"][0]["id"] == str(hazard.id)
    # here we make sure isApplicable was _not_ updated, because this hazard has a user_id
    assert data["task"]["hazards"][0]["isApplicable"] == (not new_is_applicable)

    await db_session.refresh(hazard)
    # here we make sure isApplicable was _not_ updated, because this hazard has a user_id
    assert hazard.is_applicable == (not new_is_applicable)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_hazard_append(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a task gets a correctly set 'position'.
    This hazard is appended to the current hazard list.
    """
    task: Task = await TaskFactory.persist(db_session)
    existing_hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(
        db_session,
        task_id=task.id,
    )
    new_hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(db_session)
    await db_session.refresh(task)
    await db_session.refresh(existing_hazard)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {**gql_hazard(existing_hazard), "isApplicable": True},
                    new,
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 2
    hazards = await fetch_hazards(db_session, data["task"]["id"])
    assert len(hazards) == 2
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id == existing_hazard.id:
            assert haz.position == 0
        else:
            assert haz.position == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_hazard_prepend(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a task gets a correctly set 'position'.
    This hazard is prepended to the existing hazard list.
    """
    task: Task = await TaskFactory.persist(db_session)
    existing_hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(
        db_session,
        task_id=task.id,
    )
    new_hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(db_session)
    await db_session.refresh(task)
    await db_session.refresh(existing_hazard)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    new,
                    {**gql_hazard(existing_hazard), "isApplicable": True},
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 2
    hazards = await fetch_hazards(db_session, data["task"]["id"])
    assert len(hazards) == 2
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id == existing_hazard.id:
            assert haz.position == 1
        else:
            assert haz.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_hazard_insert(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a hazard added to a task gets a correctly set 'position'.
    This hazard is inserted in the middle of the existing hazard list.
    """
    task: Task = await TaskFactory.persist(db_session)
    existing_hazards: list[TaskHazard] = await TaskHazardFactoryUrbRec.persist_many(
        db_session, task_id=task.id, size=2
    )
    new_hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(db_session)
    await db_session.refresh(task)
    for haz in existing_hazards:
        await db_session.refresh(haz)
    await db_session.refresh(new_hazard)

    new = {**gql_hazard(new_hazard), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {**gql_hazard(existing_hazards[0]), "isApplicable": True},
                    new,
                    {**gql_hazard(existing_hazards[1]), "isApplicable": True},
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 3
    hazards = await fetch_hazards(db_session, data["task"]["id"])
    assert len(hazards) == 3
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if haz.id in {i.id for i in existing_hazards}:
            assert haz.position == 0 or haz.position == 2
        else:
            assert haz.position == 1


################################################################################
# Edit Task Controls
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control's is_applicable field can be toggled.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    control: TaskControl = await TaskControlFactoryUrbRec.persist(
        db_session,
        task_hazard_id=hazard.id,
    )
    await db_session.refresh(hazard)
    await db_session.refresh(task)
    new_is_applicable = not control.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "controls": [{**gql_control(control), "isApplicable": new_is_applicable}],
    }
    data = await execute_gql(
        **edit_task_mutation,
        variables={"task": {**gql_task(task), "hazards": [updated_hazard]}},
    )

    assert data["task"]["id"] == str(task.id)
    assert data["task"]["hazards"][0]["controls"][0]["id"] == str(control.id)
    assert (
        data["task"]["hazards"][0]["controls"][0]["isApplicable"] == new_is_applicable
    )

    await db_session.refresh(control)
    assert control.is_applicable == new_is_applicable


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_control_user_owned(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a controls's is_applicable field cannot be toggled if it has a user_id.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    # allow a user_id to exist on this control
    control: TaskControl = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=hazard.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    await db_session.refresh(hazard)
    await db_session.refresh(task)
    new_is_applicable = not control.is_applicable

    updated_hazard = {
        **gql_hazard(hazard),
        "controls": [{**gql_control(control), "isApplicable": new_is_applicable}],
    }
    data = await execute_gql(
        **edit_task_mutation,
        variables={"task": {**gql_task(task), "hazards": [updated_hazard]}},
    )

    # assert the control's is_applicable has NOT changed

    assert data["task"]["id"] == str(task.id)
    assert data["task"]["hazards"][0]["controls"][0]["id"] == str(control.id)
    assert data["task"]["hazards"][0]["controls"][0]["isApplicable"] == (
        not new_is_applicable
    )

    await db_session.refresh(control)
    assert control.is_applicable == (not new_is_applicable)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_control_append(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a task gets a correctly set 'position'.
    This control is appended to the current control list.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    existing_control = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=hazard.id,
    )
    new_control = await TaskControlFactory.persist(db_session)
    await db_session.refresh(task)
    await db_session.refresh(hazard)
    await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            {**gql_control(existing_control), "isApplicable": True},
                            new,
                        ],
                    },
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 1
    assert len(data["task"]["hazards"][0]["controls"]) == 2
    controls = await fetch_controls(db_session, data["task"]["hazards"][0]["id"])
    assert len(controls) == 2
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id == existing_control.id:
            assert control.position == 0
        else:
            assert control.position == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_control_prepend(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a task gets a correctly set 'position'.
    This control is appended to the current control list.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    existing_control = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=hazard.id,
    )
    new_control = await TaskControlFactory.persist(db_session)
    await db_session.refresh(task)
    await db_session.refresh(hazard)
    await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            new,
                            {**gql_control(existing_control), "isApplicable": True},
                        ],
                    },
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 1
    assert len(data["task"]["hazards"][0]["controls"]) == 2
    controls = await fetch_controls(db_session, data["task"]["hazards"][0]["id"])
    assert len(controls) == 2
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id == existing_control.id:
            assert control.position == 1
        else:
            assert control.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_task_add_control_insert(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that a control added to a task gets a correctly set 'position'.
    This control is inserted to the middle of current control list.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    existing_controls: list[TaskControl] = await TaskControlFactory.persist_many(
        db_session, task_hazard_id=hazard.id, size=2
    )
    new_control = await TaskControlFactory.persist(db_session)
    await db_session.refresh(task)
    await db_session.refresh(hazard)
    for existing_control in existing_controls:
        await db_session.refresh(existing_control)
    await db_session.refresh(new_control)

    new = {**gql_control(new_control), "isApplicable": True}
    del new["id"]

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "isApplicable": True,
                        "controls": [
                            {**gql_control(existing_controls[0]), "isApplicable": True},
                            new,
                            {**gql_control(existing_controls[1]), "isApplicable": True},
                        ],
                    },
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 1
    assert len(data["task"]["hazards"][0]["controls"]) == 3
    controls = await fetch_controls(db_session, data["task"]["hazards"][0]["id"])
    assert len(controls) == 3
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if control.id in {i.id for i in existing_controls}:
            assert control.position == 0 or control.position == 2
        else:
            assert control.position == 1


################################################################################
# Archive an existing task
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task(execute_gql: ExecuteGQL, db_session: AsyncSession) -> None:
    task: Task = await TaskFactory.persist(db_session)

    delete_task_mutation = {
        "operation_name": "DeleteTask",
        "query": "mutation DeleteTask($id: UUID!) { task: deleteTask(id: $id) }",
    }

    data = await execute_gql(**delete_task_mutation, variables={"id": task.id})

    assert data["task"]  # our current response is a boolean

    # ensure the task still exists in the db, and is archived
    await db_session.refresh(task)
    assert_recent_datetime(task.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_task(db_session, task.id)
    assert_recent_datetime(archived.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_archives_nested_objs(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a task also archives it's hazards and controls.
    """
    task: Task = await TaskFactory.persist(db_session)
    rec_hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
        user_id=None,
    )
    rec_control: TaskControl = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=rec_hazard.id,
        user_id=None,
    )
    user_id = uuid.uuid4()
    user_hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
        user_id=user_id,
    )
    user_control: TaskControl = await TaskControlFactory.persist(
        db_session,
        task_hazard_id=user_hazard.id,
        user_id=user_id,
    )
    await db_session.refresh(task)

    delete_task_mutation = {
        "operation_name": "DeleteTask",
        "query": "mutation DeleteTask($id: UUID!) { task: deleteTask(id: $id) }",
    }

    data = await execute_gql(**delete_task_mutation, variables={"id": task.id})
    assert data["task"]  # our current response is a boolean

    # ensure the objs still exist in the db, and have archived_at set
    for d in [task, rec_hazard, rec_control, user_hazard, user_control]:
        await db_session.refresh(d)
        assert_recent_datetime(d.archived_at)  # type: ignore


################################################################################
# Archive task hazards
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_hazard(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a task and hazard, then sends an editTask mutation without that hazard,
    triggering an archive. Also asserts that recommended and user-owned controls
    are archived.
    """

    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    rec_control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id, user_id=None
    )
    user_control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id, user_id=None
    )
    await db_session.refresh(task)

    data = await execute_gql(
        **edit_task_mutation, variables={"task": {**gql_task(task), "hazards": []}}
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 0

    await db_session.refresh(hazard)
    assert_recent_datetime(hazard.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_hazard(db_session, hazard.id)
    assert_recent_datetime(archived.archived_at)

    for d in [rec_control, user_control]:
        await db_session.refresh(d)
        assert_recent_datetime(d.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_hazard_user_owned(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Prevents archiving a hazard that is not user_owned.
    """

    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactoryUrbRec.persist(
        db_session,
        task_id=task.id,
    )
    await db_session.refresh(task)

    post_data = {
        "operationName": edit_task_mutation["operation_name"],
        "query": edit_task_mutation["query"],
        "variables": jsonable_encoder({"task": {**gql_task(task), "hazards": []}}),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data

    message = data["errors"][0]["message"]
    assert "Not allowed to remove" in message

    await db_session.refresh(hazard)
    assert hazard.archived_at is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_hazard_updates_positions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a hazard on a task updates 'position' on the remaining hazards.
    """
    task: Task = await TaskFactory.persist(db_session)
    existing_hazards = await TaskHazardFactory.persist_many(
        db_session,
        task_id=task.id,
        size=3,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    to_archive = existing_hazards[1]
    await db_session.refresh(task)
    for haz in existing_hazards:
        await db_session.refresh(haz)

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {**gql_hazard(existing_hazards[0]), "isApplicable": True},
                    # dropping existing_hazards[1]
                    {**gql_hazard(existing_hazards[2]), "isApplicable": True},
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 2
    # note this fetch includes archived hazards
    hazards = await fetch_hazards(db_session, data["task"]["id"])
    assert len(hazards) == 3
    for haz in hazards:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(haz)
        assert haz.position is not None
        if not haz.archived_at:
            assert haz.position == 0 or haz.position == 1
        elif not haz.id == to_archive.id:
            # sanity check
            assert False, "Missing expected hazard in test!"


################################################################################
# Archive task controls
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a task, hazard, and control, then sends an editTask mutation without
    the control, triggering an archive.
    """

    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id, user_id=uuid.uuid4()
    )
    await db_session.refresh(task)
    await db_session.refresh(hazard)

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [{**gql_hazard(hazard), "controls": []}],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"][0]["controls"]) == 0

    await db_session.refresh(control)
    assert_recent_datetime(control.archived_at)

    # fetch a new version of the same obj.
    archived = await fetch_control(db_session, control.id)
    assert_recent_datetime(archived.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_control_user_owned(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Prevents archiving a hazard that is not user_owned.
    """

    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    control: TaskControl = await TaskControlFactoryUrbRec.persist(
        db_session, task_hazard_id=hazard.id
    )
    await db_session.refresh(task)
    await db_session.refresh(hazard)

    post_data = {
        "operationName": edit_task_mutation["operation_name"],
        "query": edit_task_mutation["query"],
        "variables": jsonable_encoder(
            {
                "task": {
                    **gql_task(task),
                    "hazards": [{**gql_hazard(hazard), "controls": []}],
                }
            }
        ),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data

    message = data["errors"][0]["message"]
    assert "Not allowed to remove" in message

    await db_session.refresh(control)
    assert control.archived_at is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_control_updates_positions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Asserts that archiving a control on a task updates 'position' on the remaining controls.
    """
    task: Task = await TaskFactory.persist(db_session)
    hazard = await TaskHazardFactory.persist(db_session, task_id=task.id)
    existing_controls = await TaskControlFactory.persist_many(
        db_session,
        task_hazard_id=hazard.id,
        size=3,
        user_id=uuid.uuid4(),  # make sure user_id is set!
    )
    to_archive = existing_controls[1]
    await db_session.refresh(task)
    await db_session.refresh(hazard)
    for ctrl in existing_controls:
        await db_session.refresh(ctrl)

    data = await execute_gql(
        **edit_task_mutation,
        variables={
            "task": {
                **gql_task(task),
                "hazards": [
                    {
                        **gql_hazard(hazard),
                        "controls": [
                            {**gql_control(existing_controls[0]), "isApplicable": True},
                            # dropping existing_hazards[1]
                            {**gql_control(existing_controls[2]), "isApplicable": True},
                        ],
                    }
                ],
            }
        },
    )

    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 1
    assert len(data["task"]["hazards"][0]["controls"]) == 2
    # note this fetch includes archived controls
    controls = await fetch_controls(db_session, data["task"]["hazards"][0]["id"])
    assert len(controls) == 3
    for control in controls:
        # refresh, b/c apparently fetch still uses cached data
        await db_session.refresh(control)
        assert control.position is not None
        if not control.archived_at:
            assert control.position == 0 or control.position == 1
        elif not control.id == to_archive.id:
            # sanity check
            assert False, "Missing expected control in test!"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_task_hazards_and_controls_only_once(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a task, hazard, and control, then sends an editTask mutation without
    the hazard or control, triggering an archive of both. Sends the query a second
    time and ensures the archived_at hasn't fired twice. Prevents re-archiving
    of hazards and controls
    """

    task: Task = await TaskFactory.persist(db_session)
    hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
        user_id=uuid.uuid4(),
    )
    control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard.id, user_id=uuid.uuid4()
    )
    await db_session.refresh(task)
    await db_session.refresh(hazard)

    variables: dict[str, Any] = {"task": {**gql_task(task), "hazards": []}}

    data = await execute_gql(**edit_task_mutation, variables=variables)
    assert data["task"]["id"] == str(task.id)
    assert len(data["task"]["hazards"]) == 0

    await db_session.refresh(hazard)
    await db_session.refresh(control)
    assert_recent_datetime(hazard.archived_at)
    assert_recent_datetime(control.archived_at)

    og_hazard_archived_at = hazard.archived_at
    og_control_archived_at = control.archived_at

    # archive again
    data = await execute_gql(**edit_task_mutation, variables=variables)
    assert data["task"]["id"] == str(task.id)

    await db_session.refresh(hazard)
    await db_session.refresh(control)

    assert og_hazard_archived_at == hazard.archived_at
    assert og_control_archived_at == control.archived_at
