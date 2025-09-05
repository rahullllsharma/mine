from __future__ import annotations

import asyncio
import uuid
from datetime import date, timedelta
from typing import Any, Optional
from urllib.parse import urlparse

import google
import google.auth
from google.auth import impersonated_credentials
from google.cloud.storage.blob import Blob
from google.cloud.storage.bucket import Bucket
from google.cloud.storage.client import Client
from google.oauth2.service_account import Credentials
from starlette.concurrency import run_in_threadpool

from worker_safety_service.config import settings
from worker_safety_service.models import GoogleCloudStorageBlob
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.urbint_logging.fastapi_utils import Stats

logger = get_logger(__name__)

UNSIGNED_URL = f"https://storage.cloud.google.com/{settings.GS_BUCKET_NAME}/%s"


class FileStorage:
    _bucket: Optional[Bucket] = None
    _client: Optional[Client] = None
    _signing_credentials: Optional[Credentials] = None

    @property
    def client(self) -> Client:
        if self._client is None:
            self._client = Client()
        return self._client

    @property
    def bucket(self) -> Bucket:
        if self._bucket is None:
            self._bucket = self.client.bucket(settings.GS_BUCKET_NAME)
        return self._bucket

    @property
    def signing_credentials(self) -> Optional[Credentials]:
        try:
            # workload identity requires impersonated credentials
            credentials, _ = google.auth.default()
            auth_request = google.auth.transport.requests.Request()
            credentials.refresh(auth_request)
            signing_credentials = impersonated_credentials.Credentials(
                source_credentials=credentials,
                target_principal=credentials.service_account_email,
                target_scopes="https://www.googleapis.com/auth/devstorage.read_write",
                lifetime=3600,  # 3600 is the default value - 1 hour
            )
            self._signing_credentials = signing_credentials

        except (
            google.auth.exceptions.DefaultCredentialsError,
            google.auth.exceptions.RefreshError,
        ):
            # assume private key auth which does not need signing credentials
            pass
        return self._signing_credentials

    def blob(self, *args: Any, **kwargs: Any) -> Blob:
        return self.bucket.blob(*args, **kwargs)

    def _exists(self, blob_id: str) -> bool:
        with Stats("gcs-exists"):
            exists: bool = self.blob(blob_id).exists()
            return exists

    async def exists(self, blob_ids: list[str]) -> list[bool]:
        return await asyncio.gather(
            *(run_in_threadpool(self._exists, blob_id) for blob_id in blob_ids)
        )

    @staticmethod
    def blob_id_from_unsigned_url(url: str) -> str:
        """return the blob-id for an unsigned URL

        example URL: https://storage.googleapis.com/worker-safety-local-dev//[blob-id]
        method returns: [blob-id]
        """
        path = urlparse(url).path
        blob_id = path.split(settings.GS_BUCKET_NAME)[-1]
        return blob_id.lstrip("/")

    @classmethod
    def generate_name(cls, tenant_id: uuid.UUID, name: str = "") -> str:
        _name = f"-{name}" if name != "" else name
        return f"{tenant_id}/{date.today().strftime('%Y-%m-%d')}-{uuid.uuid4()}{_name}"

    def unsigned_url(self, name: str) -> str:
        return UNSIGNED_URL.format(name)

    def _url(
        self,
        blob_id: str,
        expiration: timedelta = settings.GS_URL_EXPIRATION,
    ) -> str:
        blob = self.blob(blob_id)

        try:
            url: str = blob.generate_signed_url(
                version="v4" if expiration <= timedelta(days=7) else "v2",
                expiration=expiration,
                credentials=self.signing_credentials,
            )
            return url
        except google.auth.exceptions.TransportError:
            logger.exception("Failed to generate GCS signed url", blob_name=blob.name)
            return self.unsigned_url(blob.name)

    async def urls(self, blob_ids: list[str]) -> list[str]:
        if not blob_ids:
            return []
        else:
            return await asyncio.gather(
                *(run_in_threadpool(self._url, blob_id) for blob_id in blob_ids)
            )

    def _reload_blob(self, blob: Blob) -> None:
        with Stats("gcs-exists-reload"):
            if blob.exists():
                blob.reload()

    async def to_blobs(
        self, blob_ids: list[str], with_reload: bool = True
    ) -> list[Blob]:
        blobs = [self.blob(i) for i in blob_ids]
        if with_reload:
            await asyncio.gather(
                *(run_in_threadpool(self._reload_blob, blob) for blob in blobs)
            )
        return blobs

    async def to_orm(
        self, blob_ids: list[str], with_reload: bool = True
    ) -> list[GoogleCloudStorageBlob]:
        blobs = await self.to_blobs(blob_ids, with_reload=with_reload)
        return [
            GoogleCloudStorageBlob(
                id=blob.name,
                bucket_name=self.bucket.name,
                md5=blob.md5_hash,
                crc32c=blob.crc32c,
            )
            for blob in blobs
        ]

    def _generate_policy(
        self,
        tenant_id: uuid.UUID,
        expiration: timedelta = settings.GS_UPLOAD_EXPIRATION,
    ) -> dict[str, Any]:
        name = self.generate_name(tenant_id)
        with Stats("gcs-generate"):
            if expiration > timedelta(days=7):
                _url = self._url(name, expiration)
                policy: dict[str, Any] = {
                    "url": f"https://storage.googleapis.com/{self.bucket.name}/",
                    "_signed_url": _url,
                    "fields": {},
                }
            else:
                policy = self.client.generate_signed_post_policy_v4(
                    self.bucket.name,
                    name,
                    expiration,
                    credentials=self.signing_credentials,
                )
                if expiration is not settings.GS_UPLOAD_EXPIRATION:
                    policy["_signed_url"] = self._url(name, expiration)
        policy["id"] = name
        return policy

    async def policies_for_upload(
        self,
        count: int,
        tenant_id: uuid.UUID,
        expiration: timedelta = settings.GS_UPLOAD_EXPIRATION,
    ) -> list[dict[str, Any]]:
        """Generates policy data to allow uploads to GCS
        https://cloud.google.com/storage/docs/xml-api/post-object-forms

        Policy Data Shape
        {
          id: str  # same as fields.key
          url: str
          fields: {
            key: str
            policy: str
            x-goog-algorithm: str
            x-goog-credential: str
            x-goog-date: str
            x-goog-signature: str
          }
        }

        """
        policies: list[dict[str, Any]] = await asyncio.gather(
            *(
                run_in_threadpool(
                    self._generate_policy,
                    tenant_id,
                    expiration=expiration,
                )
                for _ in range(count)
            )
        )
        return policies


file_storage = FileStorage()
