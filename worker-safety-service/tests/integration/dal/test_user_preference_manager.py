import pytest
from faker import Faker

from tests.factories import UserFactory
from worker_safety_service.dal.user_preference import UserPreferenceManager
from worker_safety_service.models import AsyncSession, UserPreferenceEntityType
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)
fake = Faker()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_user_preferences(db_session: AsyncSession) -> None:
    user = await UserFactory.persist(db_session)
    user_preference_manager = UserPreferenceManager(db_session)
    user_preferences = await user_preference_manager.get_all(user.id)

    assert user_preferences == []

    await user_preference_manager.save(
        data={"a": 10, "hello": "world"},
        entity_type=UserPreferenceEntityType.MapFilters,
        user_id=user.id,
    )

    user_preferences = await user_preference_manager.get_all(user.id)

    assert len(user_preferences) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_user_preferences(db_session: AsyncSession) -> None:
    user = await UserFactory.persist(db_session)
    user_preference_manager = UserPreferenceManager(db_session)

    await user_preference_manager.save(
        data={
            "a": 10,
        },
        entity_type=UserPreferenceEntityType.MapFilters,
        user_id=user.id,
    )

    user_preferences = await user_preference_manager.get_all(user.id)

    assert len(user_preferences) == 1
    if user_preferences[0].contents is not None:
        assert user_preferences[0].contents.get("a") == 10
        assert user_preferences[0].contents.get("hello") is None

    await user_preference_manager.save(
        data={"a": 10, "hello": "world"},
        entity_type=UserPreferenceEntityType.MapFilters,
        user_id=user.id,
    )

    user_preferences = await user_preference_manager.get_all(user.id)

    assert len(user_preferences) == 1
    if user_preferences[0].contents is not None:
        assert user_preferences[0].contents.get("a") == 10
        assert user_preferences[0].contents.get("hello") == "world"
