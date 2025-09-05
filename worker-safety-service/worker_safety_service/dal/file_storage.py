import uuid
from datetime import timedelta
from typing import Any, Optional

from sqlmodel import select
from sqlmodel.sql.expression import col

from worker_safety_service.config import settings
from worker_safety_service.gcloud.storage import FileStorage
from worker_safety_service.models import AsyncSession, File, GoogleCloudStorageBlob


class FileStorageManager:
    def __init__(self, session: AsyncSession, file_storage: FileStorage):
        self.session = session
        self.file_storage = file_storage

    async def get_upload_policies(
        self,
        count: int,
        tenant_id: uuid.UUID,
        expiration: timedelta = settings.GS_UPLOAD_EXPIRATION,
    ) -> list[dict[str, Any]]:
        policies = await self.file_storage.policies_for_upload(
            count, tenant_id, expiration
        )
        models = await self.file_storage.to_orm(
            [policy["id"] for policy in policies], with_reload=False
        )

        self.session.add_all(models)
        await self.session.commit()
        return policies

    async def get_models(
        self, ids: Optional[list[str]] = None
    ) -> list[GoogleCloudStorageBlob]:
        statement = select(GoogleCloudStorageBlob)
        if ids:
            statement = statement.where(col(GoogleCloudStorageBlob.id).in_(ids))
        return (await self.session.exec(statement)).all()

    async def get_files(self, ids: Optional[list[str]] = None) -> list[File]:
        models = await self.get_models(ids)
        signed_urls = await self.file_storage.urls([i.id for i in models])
        return [
            File(
                url=self.file_storage.unsigned_url(model.id),
                id=model.id,
                bucket_name=model.bucket_name,
                name=model.file_name,
                display_name=model.file_name,
                mimetype=model.mimetype,
                md5=model.md5,
                crc32c=model.crc32c,
                signed_url=signed_urls[index],
            )
            for index, model in enumerate(models)
        ]

    async def urls(self, blob_ids: list[str]) -> list[str]:
        return await self.file_storage.urls(blob_ids)

    async def exists(self, blob_ids: list[str]) -> list[bool]:
        return await self.file_storage.exists(blob_ids)

    def blob_id_from_unsigned_url(self, url: str) -> str:
        return self.file_storage.blob_id_from_unsigned_url(url)
