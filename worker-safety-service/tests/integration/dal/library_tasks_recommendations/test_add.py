import uuid

import pytest

from tests.factories import LibraryTaskRecommendationsFactory
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.library_tasks_recomendations import (
    LibraryTaskHazardRecommendationsManager,
)
from worker_safety_service.models import (
    AsyncSession,
    LibraryControl,
    LibraryHazard,
    LibraryTask,
    LibraryTaskRecommendations,
)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_recommendation_success(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    new_rec = await LibraryTaskRecommendationsFactory.build_with_dependencies(
        db_session
    )
    await library_task_hazard_recommendations_manager.create(new_rec)
    await db_session.commit()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_recommendation_success_duplicated(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    # Store the first recommendation
    new_rec = await LibraryTaskRecommendationsFactory.build_with_dependencies(
        db_session
    )
    await library_task_hazard_recommendations_manager.create(new_rec)
    await db_session.commit()

    # Store the duplicate recommendation
    dup_rec = LibraryTaskRecommendations.parse_obj(new_rec.dict())
    await library_task_hazard_recommendations_manager.create(dup_rec)
    await db_session.commit()


async def assert_missing_dependency(
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
    recommendation: LibraryTaskRecommendations,
    missing_entity_id: uuid.UUID,
    missing_entity_type: type,
) -> None:
    with pytest.raises(EntityNotFoundException) as ex:
        await library_task_hazard_recommendations_manager.create(recommendation)

    assert ex.value.entity_id == missing_entity_id
    assert ex.value.entity_type == missing_entity_type


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_recommendation_fail_unknown_task_id(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    new_rec = await LibraryTaskRecommendationsFactory.build_with_dependencies(
        db_session
    )
    new_rec.library_task_id = uuid.uuid4()
    await assert_missing_dependency(
        library_task_hazard_recommendations_manager,
        new_rec,
        new_rec.library_task_id,
        LibraryTask,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_recommendation_fail_unknown_hazard_id(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    new_rec = await LibraryTaskRecommendationsFactory.build_with_dependencies(
        db_session
    )
    new_rec.library_hazard_id = uuid.uuid4()
    await assert_missing_dependency(
        library_task_hazard_recommendations_manager,
        new_rec,
        new_rec.library_hazard_id,
        LibraryHazard,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_recommendation_fail_unknown_control_id(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    new_rec = await LibraryTaskRecommendationsFactory.build_with_dependencies(
        db_session
    )
    new_rec.library_control_id = uuid.uuid4()
    await assert_missing_dependency(
        library_task_hazard_recommendations_manager,
        new_rec,
        new_rec.library_control_id,
        LibraryControl,
    )
