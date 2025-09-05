import pytest

from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import AsyncSession, WorkType


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_work_type_empty(
    db_session: AsyncSession,
    work_type_manager: WorkTypeManager,
    an_empty_work_type: WorkType,
) -> None:
    await work_type_manager.archive_work_type(an_empty_work_type.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_work_type_unknown(
    db_session: AsyncSession,
    work_type_manager: WorkTypeManager,
    new_work_type: WorkType,
) -> None:
    with pytest.raises(ResourceReferenceException):
        await work_type_manager.archive_work_type(new_work_type.id)
