import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import google.auth
from google.auth import impersonated_credentials
from google.auth.exceptions import DefaultCredentialsError, RefreshError
from google.auth.impersonated_credentials import Credentials
from google.cloud import storage

from ws_customizable_workflow.configs.config import Settings
from ws_customizable_workflow.managers.services.cache import Cache

settings = Settings.get_settings()


class StorageManager:
    _signing_credentials: Optional[Credentials] = None

    def __init__(
        self,
        bucket_name: str = settings.GS_BUCKET_NAME,
        check_blob_exists: bool = True,
    ):
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.check_blob_exists = check_blob_exists

    @property
    def signing_credentials(self) -> Optional[Credentials]:
        try:
            # workload identity requires impersonated credentials
            credentials, _ = google.auth.default()  # type: ignore
            auth_request = google.auth.transport.requests.Request()  # type: ignore
            credentials.refresh(auth_request)
            signing_credentials = impersonated_credentials.Credentials(
                source_credentials=credentials,
                target_principal=credentials.service_account_email,
                target_scopes="https://www.googleapis.com/auth/devstorage.read_write",
                lifetime=3600,  # 3600 is the default value - 1 hour
            )  # type: ignore
            self._signing_credentials = signing_credentials

        except (DefaultCredentialsError, RefreshError):
            # assume private key auth which does not need signing credentials
            pass
        return self._signing_credentials

    def _check_blob_exists(self, bucket_name: str, blob_name: str) -> bool:
        """
        Cached check for blob existence to avoid repeated network calls.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return blob.exists()  # type: ignore

    def get_bucket_from_url(self, url: str) -> str:
        """
        Extract the bucket name from a GCS URL.
        """
        # Remove any query parameters first
        url = url.split("?")[0]

        # Get the bucket name from the URL
        parts = url.split("/")
        if len(parts) < 4:
            return self.bucket_name

        return parts[3]  # The bucket name is the fourth part

    def generate_signed_url(
        self,
        blob_name: str,
        bucket_name: str = settings.GS_BUCKET_NAME,
        expiration_minutes: int = getattr(settings, "GS_URL_EXPIRATION_MINUTES", 15),
    ) -> str:
        """
        Generate a signed URL for a blob in Google Cloud Storage.
        """
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        if self.check_blob_exists and not self._check_blob_exists(
            bucket_name, blob_name
        ):
            raise Exception(
                f"Blob does not exist: {blob_name} in bucket: {bucket_name}"
            )

        # Generate a unique identifier for this URL
        unique_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)  # Use milliseconds for more precision

        url = blob.generate_signed_url(
            version="v4",
            expiration=datetime.now(timezone.utc)
            + timedelta(minutes=expiration_minutes),
            method="GET",
            query_parameters={"t": str(timestamp), "id": unique_id},
            credentials=self.signing_credentials,
        )
        return str(url)

    def get_blob_name_from_url(self, url: str) -> Optional[str]:
        """
        Extract the blob name from a GCS URL.

        Args:
            url: The GCS URL

        Returns:
            Optional[str]: The blob name if the URL is a valid GCS URL, None otherwise
        """
        url = url.replace("https://storage.googleapis.com/", "")

        # Remove any query parameters first
        url = url.split("?")[0]

        url = re.sub(r"//+", "/", url)

        if "/" not in url:
            return None
        return "/".join(url.split("/")[1:])


class CachedStorageManager:
    def __init__(self, cache: Cache, storage_manager: StorageManager):
        self._cache = cache
        self._storage_manager = storage_manager

    async def generate_cached_signed_url(
        self,
        blob_name: str,
        bucket_name: str = settings.GS_BUCKET_NAME,
        expiration_minutes: int = settings.GS_URL_EXPIRATION_MINUTES,
    ) -> str:
        """
        Generate and cache a signed URL for a blob in Google Cloud Storage.
        """
        _key = f"__CachedFileStorage__{blob_name}"
        _value = await self._cache.get(_key)
        if isinstance(_value, bytes):
            _value = _value.decode("UTF-8", "replace")
        if not _value:
            try:
                _value = self._storage_manager.generate_signed_url(
                    blob_name, bucket_name, expiration_minutes
                )
                # To be safe, the cached url expires 5 sec before the signed_url
                # This is to counter any lag in the call above and cache set op below
                await self._cache.set(_key, _value, expiration_minutes * 60 - 5)
            except Exception:
                await self._cache.delete(_key)
                raise
        return _value
