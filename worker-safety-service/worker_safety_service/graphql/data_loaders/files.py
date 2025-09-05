import datetime
import uuid
from typing import Any

from strawberry.dataloader import DataLoader

from worker_safety_service.config import settings
from worker_safety_service.dal.file_storage import FileStorageManager
from worker_safety_service.models import File


class TenantFileLoader:
    def __init__(self, manager: FileStorageManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_files)
        self.signed_urls = DataLoader(load_fn=self.load_signed_urls)
        self.exists = DataLoader(load_fn=self.load_exists)
        self.__manager = manager

    async def load_files(self, file_ids: list[str]) -> list[File]:
        return await self.__manager.get_files(file_ids)

    async def load_signed_urls(self, blob_ids: list[str]) -> list[str]:
        return await self.__manager.urls(blob_ids)

    async def load_exists(self, blob_ids: list[str]) -> list[bool]:
        return await self.__manager.exists(blob_ids)

    def blob_id_from_unsigned_url(self, url: str) -> str:
        return self.__manager.blob_id_from_unsigned_url(url)

    async def get_upload_policies(
        self, count: int, expiration: datetime.timedelta = settings.GS_UPLOAD_EXPIRATION
    ) -> list[dict[str, Any]]:
        return await self.__manager.get_upload_policies(
            count, self.tenant_id, expiration=expiration
        )
