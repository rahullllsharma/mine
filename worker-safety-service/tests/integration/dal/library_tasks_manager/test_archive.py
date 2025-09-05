import datetime
import uuid

import pendulum
import pytest

from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import AsyncSession, LibraryTask


async def assert_library_task_is_archived(
    library_tasks_manager: LibraryTasksManager,
    library_task: LibraryTask,
    _from: datetime.datetime | None = None,
    _to: datetime.datetime | None = None,
) -> None:
    # Retrieve the task without archived flag
    query_result = await library_tasks_manager.get_by_id(library_task.id)
    assert query_result is None

    # Retrieve task with archived flag
    archived_library_task = await library_tasks_manager.get_by_id(
        library_task.id, allow_archived=True
    )
    assert archived_library_task, "Archived task must be retrieved"
    assert archived_library_task.dict(exclude={"archived_at"}) == library_task.dict(
        exclude={"archived_at"}
    ), "All the attributes must remain the same"
    archived_at = archived_library_task.archived_at
    assert archived_at is not None
    if _from:
        assert _from <= archived_at, "Archived at must be greater than"
    if _to:
        assert archived_at <= _to, "Archived at must be less or equal than"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_library_task_success(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    a_library_task: LibraryTask,
) -> None:
    # Archive the task, and get a boundary on the archived timestamp
    _from = pendulum.now("UTC")
    await library_tasks_manager.archive(a_library_task.id)
    _to = pendulum.now("UTC")

    await assert_library_task_is_archived(
        library_tasks_manager, a_library_task, _from, _to
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_library_task_already_archived(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    a_library_task: LibraryTask,
) -> None:
    # Archive the task
    _from = pendulum.now("UTC")
    await test_archive_library_task_success(
        db_session, library_tasks_manager, a_library_task
    )
    _to = pendulum.now("UTC")

    # Archive the task again
    await library_tasks_manager.archive(a_library_task.id)

    # Check if the archived at property remains the same
    await assert_library_task_is_archived(
        library_tasks_manager, a_library_task, _from, _to
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_unknown_library_task(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
) -> None:
    _id = uuid.uuid4()
    # TODO: Assert that this task does not exist first

    with pytest.raises(EntityNotFoundException):
        # TODO: Check if we should give a better exception!!
        await library_tasks_manager.archive(_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unarchive_library_task_success(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    archived_library_task: LibraryTask,
) -> None:
    # When the user tries to unarchive it
    await library_tasks_manager.unarchive(archived_library_task.id)
    # Then the task should be visible
    actual = await library_tasks_manager.get_by_id(archived_library_task.id)
    assert actual == archived_library_task, "The LibraryTask must be visible"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unarchive_library_task_already_unarchived(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    a_library_task: LibraryTask,
) -> None:
    await library_tasks_manager.unarchive(a_library_task.id)
    actual = await library_tasks_manager.get_by_id(a_library_task.id)
    assert actual == a_library_task, "The LibraryTask must be visible"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_unarchive_library_task_unkown(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    _id = uuid.uuid4()
    # TODO: Assert that this task does not exist first
    with pytest.raises(EntityNotFoundException):
        # TODO: Check if we should give a better exception!!
        await library_tasks_manager.archive(_id)
