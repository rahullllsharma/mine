import uuid
from typing import Optional

from worker_safety_service.dal.insight_manager import InsightManager
from worker_safety_service.models.insight import (
    CreateInsightInput,
    Insight,
    UpdateInsightInput,
)


class InsightLoader:
    def __init__(
        self,
        manager: InsightManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager

    async def load_insights(
        self,
        limit: Optional[int] = None,
        after: Optional[uuid.UUID] = None,
    ) -> list[Insight]:
        return await self.__manager.get_all(
            tenant_id=self.tenant_id, limit=limit, after=after
        )

    async def load_insight_by_id(self, id: uuid.UUID) -> Insight:
        return await self.__manager.get(id)

    async def create_insight(self, create_input: CreateInsightInput) -> Insight:
        return await self.__manager.create(input=create_input, tenant_id=self.tenant_id)

    async def update_insight(
        self, id: uuid.UUID, update_input: UpdateInsightInput
    ) -> Insight:
        return await self.__manager.update(
            id=id, input=update_input, tenant_id=self.tenant_id
        )

    async def archive_insight(self, id: uuid.UUID) -> bool:
        return await self.__manager.archive(id=id, tenant_id=self.tenant_id)

    async def reorder_insights(
        self, ordered_ids: list[uuid.UUID], limit: Optional[int] = None
    ) -> list[Insight]:
        return await self.__manager.reorder(
            ordered_ids=ordered_ids, tenant_id=self.tenant_id, limit=limit
        )
