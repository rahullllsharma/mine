import pytest

from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_work_types_with_after_simple(
    db_session: AsyncSession,
    work_type_manager: WorkTypeManager,
) -> None:
    # Get all worktypes
    all_wts = await work_type_manager.get_work_types()
    # Find a worktype
    assert len(all_wts) > 2, "This test requires at least 3 WorkTypes"
    # Make the after query
    after_wts = await work_type_manager.get_work_types(after=all_wts[1].id)
    assert after_wts == all_wts[2:]
