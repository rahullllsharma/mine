import uuid

import pytest

from tests.factories import LibraryTaskRecommendationsFactory
from worker_safety_service.dal.library_tasks_recomendations import (
    LibraryTaskHazardRecommendationsManager,
)
from worker_safety_service.models import AsyncSession, LibraryTaskRecommendations


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_recommendation_success(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    lr = await LibraryTaskRecommendationsFactory.persist(db_session)
    await library_task_hazard_recommendations_manager.delete(lr)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_recommendation_success_unknown_recommendation(
    db_session: AsyncSession,
    library_task_hazard_recommendations_manager: LibraryTaskHazardRecommendationsManager,
) -> None:
    lr = LibraryTaskRecommendations(
        library_task_id=uuid.uuid4(),
        library_hazard_id=uuid.uuid4(),
        library_control_id=uuid.uuid4(),
    )
    await library_task_hazard_recommendations_manager.delete(lr)
