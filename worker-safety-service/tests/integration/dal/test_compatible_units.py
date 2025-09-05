import pytest

from tests.factories import CompatibleUnitFactory, ElementLibraryTaskLinkFactory
from worker_safety_service.dal.ingestion.compatible_units import CompatibleUnitManager
from worker_safety_service.models.utils import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_compatible_units_returns_all_compatible_units(
    db_session: AsyncSession, compatible_unit_manager: CompatibleUnitManager
) -> None:
    cu = await CompatibleUnitFactory.persist(db_session)
    await CompatibleUnitFactory.persist(db_session)
    retrieved_cus = await compatible_unit_manager.get_compatible_units(cu.tenant_id)

    assert len(retrieved_cus) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_compatible_units_returns_filtered_compatible_units(
    db_session: AsyncSession, compatible_unit_manager: CompatibleUnitManager
) -> None:
    cu = await CompatibleUnitFactory.persist(db_session)
    await CompatibleUnitFactory.persist(db_session)
    retrieved_cus = await compatible_unit_manager.get_compatible_units(
        cu.tenant_id, [cu.compatible_unit_id]
    )

    assert len(retrieved_cus) == 1
    assert cu == retrieved_cus[0]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_compatible_units_by_id_returns_correct_mapping(
    db_session: AsyncSession, compatible_unit_manager: CompatibleUnitManager
) -> None:
    cu = await CompatibleUnitFactory.persist(db_session)
    cu_mapping = await compatible_unit_manager.get_compatible_units_by_id(
        tenant_id=cu.tenant_id, compatible_unit_ids=[cu.compatible_unit_id]
    )

    assert cu_mapping == {cu.compatible_unit_id: cu}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_compatible_units_by_id_returns_empty_dict_if_no_library_task_id(
    db_session: AsyncSession,
    compatible_unit_manager: CompatibleUnitManager,
) -> None:
    cu = await CompatibleUnitFactory.persist(db_session)
    cu_mapping = await compatible_unit_manager.get_compatible_units_by_id(
        tenant_id=cu.tenant_id, compatible_unit_ids=[]
    )

    assert cu_mapping == {}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_tasks_for_cu_returns_library_tasks_correctly(
    db_session: AsyncSession,
    compatible_unit_manager: CompatibleUnitManager,
) -> None:
    cu = await CompatibleUnitFactory.persist(db_session)
    element_library_task_link = await ElementLibraryTaskLinkFactory.persist(db_session)
    cu.element_id = element_library_task_link.element_id

    db_session.add(cu)
    await db_session.commit()

    library_task_ids = await compatible_unit_manager.get_library_tasks_for_cu(
        tenant_id=cu.tenant_id, compatible_unit_id=cu.compatible_unit_id
    )

    assert {element_library_task_link.library_task_id} == library_task_ids
