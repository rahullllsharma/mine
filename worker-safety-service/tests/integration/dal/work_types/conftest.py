import pytest

from tests.factories import LibraryTaskFactory, TenantFactory, WorkTypeFactory
from worker_safety_service.models import AsyncSession, WorkType


@pytest.fixture()
async def new_work_type(db_session: AsyncSession) -> WorkType:
    return await WorkTypeFactory.build_with_dependencies(db_session)


@pytest.fixture()
async def an_empty_work_type(db_session: AsyncSession) -> WorkType:
    return await WorkTypeFactory.persist(db_session)


@pytest.fixture()
async def general_work_type(db_session: AsyncSession) -> WorkType:
    return await WorkTypeFactory.get_or_create_general_work_type(db_session)


@pytest.fixture()
async def a_work_type_with_tasks(db_session: AsyncSession) -> WorkType:
    wt = await WorkTypeFactory.persist(db_session)
    await LibraryTaskFactory.with_work_type_link(db_session, work_type_id=wt.id)
    return wt


@pytest.fixture()
async def a_work_type_with_tenant(db_session: AsyncSession) -> WorkType:
    t = await TenantFactory.persist(db_session)
    wt = await WorkTypeFactory.tenant_work_type(t.id, db_session)
    return wt
