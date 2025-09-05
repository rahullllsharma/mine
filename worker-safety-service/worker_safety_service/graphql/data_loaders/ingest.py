import uuid
from typing import Any

from worker_safety_service.dal.ingest import (
    IngestedResponse,
    IngestManager,
    IngestOption,
    IngestType,
)


class TenantIngestLoader:
    def __init__(self, manager: IngestManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.__manager = manager

    def get_options(self) -> list[IngestOption]:
        return self.__manager.get_options()

    async def get_items(self, key: IngestType) -> list[dict[str, Any | None]]:
        return await self.__manager.get_items(key, self.tenant_id)

    async def ingest(
        self, key: IngestType, body: str, delimiter: str = ","
    ) -> IngestedResponse:
        return await self.__manager.ingest(
            key, body, self.tenant_id, delimiter=delimiter
        )
