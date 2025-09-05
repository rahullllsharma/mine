import pytest

from tests.factories import LibraryTaskFactory
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import AsyncSession, LibraryTask


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_new_library_task(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> LibraryTask:
    await library_tasks_manager.create(new_library_task)
    actual = await library_tasks_manager.get_by_id(new_library_task.id)
    assert new_library_task == actual, "The new created task must be retrievable by id"
    return actual


async def add_duplicated_task(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    original_task: LibraryTask,
    duplicated_task: LibraryTask,
) -> EntityAlreadyExistsException:
    await test_add_new_library_task(db_session, library_tasks_manager, original_task)
    # Assert that an EntityAlreadyExists must be thrown
    with pytest.raises(EntityAlreadyExistsException) as ex:
        await library_tasks_manager.create(duplicated_task)

    return ex.value


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_new_library_task_duplicated_id(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    duplicated_task = LibraryTaskFactory.build(
        id=new_library_task.id,
    )
    ex = await add_duplicated_task(
        db_session, library_tasks_manager, new_library_task, duplicated_task
    )
    assert ex.unique_field == "id", "Add must fail because of a duplicated id."


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_new_library_task_duplicated_unique_task_id(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    new_library_task: LibraryTask,
) -> None:
    duplicated_task = LibraryTaskFactory.build(
        unique_task_id=new_library_task.unique_task_id,
    )
    ex = await add_duplicated_task(
        db_session, library_tasks_manager, new_library_task, duplicated_task
    )
    assert (
        ex.unique_field == "unique_task_id"
    ), "Add must fail because of a unique task id."
