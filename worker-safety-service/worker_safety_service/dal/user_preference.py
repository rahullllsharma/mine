import datetime
import uuid

from sqlmodel import select

from worker_safety_service.models import (
    AsyncSession,
    UserPreference,
    UserPreferenceEntityType,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class UserPreferenceManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(self, user_id: uuid.UUID) -> list[UserPreference]:
        statement = select(UserPreference).where(UserPreference.user_id == user_id)

        result = await self.session.exec(statement)
        return result.all()

    async def save(
        self, data: dict, entity_type: UserPreferenceEntityType, user_id: uuid.UUID
    ) -> UserPreference:
        statment = (
            select(UserPreference)
            .where(UserPreference.user_id == user_id)
            .where(UserPreference.entity_type == entity_type)
        )

        result = (await self.session.exec(statment)).first()

        if result is None:
            result = UserPreference(
                user_id=user_id,
                entity_type=entity_type,
            )

        result.contents = data
        result.updated_at = datetime.datetime.now(datetime.timezone.utc)
        self.session.add(result)
        await self.session.commit()
        return result
