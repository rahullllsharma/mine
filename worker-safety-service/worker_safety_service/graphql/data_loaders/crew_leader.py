import uuid
from typing import Optional

from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.models.crew_leader import CrewLeader


class CrewLeaderLoader:
    def __init__(
        self,
        manager: CrewLeaderManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager

    async def load_crew_leaders(
        self,
        limit: Optional[int] = None,
        offset: int | None = None,
    ) -> list[CrewLeader]:
        return await self.__manager.get_all(
            tenant_id=self.tenant_id, limit=limit, offset=offset
        )

    async def match_if_crew_leader_exists(self, crew_leaders: list[str]) -> list[str]:
        existing_names = await self.__manager.check_crew_leader_exists_by_name(
            self.tenant_id, crew_leaders
        )
        return existing_names
