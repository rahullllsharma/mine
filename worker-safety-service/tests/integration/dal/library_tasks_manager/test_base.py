import pytest

from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import LibraryTask
from worker_safety_service.models.utils import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_tasks_archived_flag(
    db_session: AsyncSession,
    library_tasks_manager: LibraryTasksManager,
    archived_library_task: LibraryTask,
) -> None:
    only_current_tasks = await library_tasks_manager.get_library_tasks(
        allow_archived=False
    )
    all_tasks = await library_tasks_manager.get_library_tasks(allow_archived=True)

    assert archived_library_task.id not in map(
        lambda t: t.id, only_current_tasks
    ), "Archived task must not show if allow archived was not used."
    assert archived_library_task.id in map(
        lambda t: t.id, all_tasks
    ), "Archived task must show if allow archived was used."
