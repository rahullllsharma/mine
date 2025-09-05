import pytest

from tests.factories import LibraryTaskFactory, fake
from worker_safety_service.dal.library_tasks import LibraryTasksManager
from worker_safety_service.models import AsyncSession, LibraryTask


@pytest.fixture()
async def new_library_task(db_session: AsyncSession) -> LibraryTask:
    task = await LibraryTaskFactory.build_with_dependencies(db_session)
    return task


@pytest.fixture()
async def a_library_task(
    db_session: AsyncSession, library_tasks_manager: LibraryTasksManager
) -> LibraryTask:
    return await LibraryTaskFactory.persist(db_session)


@pytest.fixture()
async def archived_library_task(db_session: AsyncSession) -> LibraryTask:
    archived_task = await LibraryTaskFactory.persist(
        db_session, archived_at=fake.past_datetime()
    )
    return archived_task
