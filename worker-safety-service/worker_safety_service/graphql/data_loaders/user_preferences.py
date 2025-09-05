import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.user_preference import UserPreferenceManager
from worker_safety_service.models import UserPreference, UserPreferenceEntityType


class UserPreferenceLoader:
    def __init__(self, manager: UserPreferenceManager) -> None:
        self.__manager = manager
        self.by_user_id = DataLoader(load_fn=self.load_by_user_id)

    async def load_by_user_id(
        self, user_ids: list[uuid.UUID]
    ) -> list[list[UserPreference]]:
        return [(await self.__manager.get_all(user_id)) for user_id in user_ids]

    async def save(
        self, data: dict, entity_type: UserPreferenceEntityType, user_id: uuid.UUID
    ) -> UserPreference:
        result = await self.__manager.save(
            data=data, user_id=user_id, entity_type=entity_type
        )

        return result
