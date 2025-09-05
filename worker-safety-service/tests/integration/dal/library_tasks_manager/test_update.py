import pytest

from tests.factories import LibraryTaskFactory
from tests.integration.dal.library_tasks_manager.test_add import (
    test_add_new_library_task,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import AsyncSession, LibraryTask


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_library_task(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    added_task = await test_add_new_library_task(
        db_session, library_tasks_manager, new_library_task
    )
    updated_task = LibraryTaskFactory.build(
        id=added_task.id,
        unique_task_id=added_task.unique_task_id,
    )

    await library_tasks_manager.update(updated_task)
    actual = await library_tasks_manager.get_by_id(added_task.id)
    assert actual == updated_task, "The task the task field must have been updated"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_library_task_work_type(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    added_task = await test_add_new_library_task(
        db_session, library_tasks_manager, new_library_task
    )
    updated_task = await LibraryTaskFactory.build_with_dependencies(
        db_session, id=added_task.id, unique_task_id=added_task.unique_task_id
    )

    await library_tasks_manager.update(updated_task)
    actual = await library_tasks_manager.get_by_id(added_task.id)
    assert actual == updated_task, "The task the Work Type field must have been updated"


async def test_update_library_task_not_existing_task(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    with pytest.raises(Exception):
        # TODO: Check if we should give a better exception!!
        await library_tasks_manager.update(new_library_task)


async def test_update_library_task_fails_on_archived(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    archived_library_task: LibraryTask,
) -> None:
    updated_task = await LibraryTaskFactory.build_with_dependencies(
        db_session,
        id=archived_library_task.id,
        unique_task_id=archived_library_task.unique_task_id,
    )

    with pytest.raises(Exception):
        # TODO: Check if we should give a better exception!!
        await library_tasks_manager.update(updated_task)
