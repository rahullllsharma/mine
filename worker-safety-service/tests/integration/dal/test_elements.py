import pytest

from tests.factories import ElementFactory
from worker_safety_service.dal.ingestion.elements import ElementManager
from worker_safety_service.models.utils import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_element_by_name_returns_correct_element(
    db_session: AsyncSession, element_manager: ElementManager
) -> None:
    element = await ElementFactory.persist(db_session)
    await ElementFactory.persist(db_session)
    retrieved_element = await element_manager.get_element_by_name(
        element_name=element.name
    )

    assert retrieved_element == element


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_elements_returns_correct_element(
    db_session: AsyncSession, element_manager: ElementManager
) -> None:
    element = await ElementFactory.persist(db_session)
    await ElementFactory.persist(db_session)
    retrieved_element = await element_manager.get_elements([element.id])

    assert retrieved_element == [element]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_elements_returns_empty_list_if_no_ids(
    db_session: AsyncSession, element_manager: ElementManager
) -> None:
    await ElementFactory.persist(db_session)

    retrieved_element = await element_manager.get_elements([])

    assert retrieved_element == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_elements_by_id_returns_correct_mapping(
    db_session: AsyncSession, element_manager: ElementManager
) -> None:
    element = await ElementFactory.persist(db_session)
    element_mapping = await element_manager.get_elements_by_id(ids=[element.id])

    assert element_mapping == {element.id: element}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_elements_by_id_returns_empty_dict_if_no_library_task_id(
    element_manager: ElementManager,
) -> None:
    element_mapping = await element_manager.get_elements_by_id(ids=[])

    assert element_mapping == {}
