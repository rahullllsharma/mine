from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests import have_gcs_credentials
from ws_customizable_workflow.managers.services.forms import FormsManager
from ws_customizable_workflow.managers.services.storage import (
    CachedStorageManager,
    StorageManager,
)


@pytest.fixture
def storage_manager() -> StorageManager:
    return StorageManager(bucket_name="test-bucket")


@pytest.mark.skipif(not have_gcs_credentials(), reason="no gcs credentials")
class TestStorageManager:
    @pytest.mark.parametrize(
        "url,expected",
        [
            (
                "https://storage.googleapis.com/test-bucket/path/to/file.jpg",
                "test-bucket",
            ),
            (
                "https://storage.googleapis.com/other-bucket/path/to/file.jpg",
                "other-bucket",
            ),
            ("https://storage.googleapis.com/test-bucket/", "test-bucket"),
            ("invalid-url", "test-bucket"),
        ],
    )
    def test_get_bucket_from_url(
        self, storage_manager: StorageManager, url: str, expected: str
    ) -> None:
        assert storage_manager.get_bucket_from_url(url) == expected

    @pytest.mark.parametrize(
        "url,expected",
        [
            (
                "https://storage.googleapis.com/test-bucket/path/to/file.jpg",
                "path/to/file.jpg",
            ),
            (
                "https://storage.googleapis.com/other-bucket/path/to/file.jpg",
                "path/to/file.jpg",
            ),
            ("https://storage.googleapis.com/test-bucket/", ""),
            ("invalid-url", None),
        ],
    )
    def test_get_blob_name_from_url(
        self, storage_manager: StorageManager, url: str, expected: Optional[str]
    ) -> None:
        assert storage_manager.get_blob_name_from_url(url) == expected

    @patch("google.cloud.storage.Blob")
    @patch("google.cloud.storage.Bucket")
    @patch("google.cloud.storage.Client")
    def test_generate_signed_url(
        self,
        mock_client: MagicMock,
        mock_bucket: MagicMock,
        mock_blob: MagicMock,
    ) -> None:
        # Setup
        storage_manager = StorageManager(bucket_name="test-bucket")
        mock_blob_instance = MagicMock()
        mock_bucket_instance = MagicMock()
        mock_bucket.return_value = mock_bucket_instance
        mock_bucket_instance.blob.return_value = mock_blob_instance
        mock_blob_instance.exists.return_value = True
        mock_blob_instance.generate_signed_url.return_value = "https://signed-url.com"
        mock_client.return_value.bucket.return_value = mock_bucket_instance

        # Test
        url = storage_manager.generate_signed_url("path/to/file.jpg")

        # Assert
        assert url == "https://signed-url.com"
        mock_blob_instance.exists.assert_called_once()
        mock_blob_instance.generate_signed_url.assert_called_once()

    @patch("google.cloud.storage.Blob")
    @patch("google.cloud.storage.Bucket")
    @patch("google.cloud.storage.Client")
    def test_generate_signed_url_nonexistent_blob(
        self,
        mock_client: MagicMock,
        mock_bucket: MagicMock,
        mock_blob: MagicMock,
    ) -> None:
        # Setup
        storage_manager = StorageManager(bucket_name="test-bucket")
        mock_blob_instance = MagicMock()
        mock_bucket_instance = MagicMock()
        mock_bucket.return_value = mock_bucket_instance
        mock_bucket_instance.blob.return_value = mock_blob_instance
        mock_blob_instance.exists.return_value = False
        mock_client.return_value.bucket.return_value = mock_bucket_instance

        # Test and Assert
        with pytest.raises(Exception) as exc_info:
            storage_manager.generate_signed_url(
                "path/to/file.jpg",
                "https://storage.googleapis.com/test-bucket/path/to/file.jpg",
            )
        assert "Blob does not exist" in str(exc_info.value)

    @patch(
        "ws_customizable_workflow.managers.services.cache.Cache", new_callable=AsyncMock
    )
    @patch("ws_customizable_workflow.managers.services.storage.StorageManager")
    async def test_process_form_data_for_signed_urls(
        self,
        mock_storage_manager: MagicMock,
        mock_cache: MagicMock,
    ) -> None:
        # Setup
        mock_cache.get.return_value = None
        mock_storage_manager.check_blob_exists = False
        mock_storage_manager.generate_signed_url.return_value = "https://signed-url.com"
        cached_storage_manager: CachedStorageManager = CachedStorageManager(
            cache=mock_cache, storage_manager=mock_storage_manager
        )

        test_data: Dict[str, Any] = {
            "signed_url": "https://storage.googleapis.com/test-bucket/path/to/file.jpg",
            "nested": {
                "signed_url": "https://storage.googleapis.com/test-bucket/path/to/other.jpg",
            },
            "list_of_files": [
                {
                    "signed_url": "https://storage.googleapis.com/test-bucket/path/to/file3.jpg",
                },
                {
                    "signedUrl": "https://storage.googleapis.com/test-bucket/path/to/file3.jpg",
                },
                {
                    "some_key": "https://storage.googleapis.com/test-bucket/path/to/file3.jpg",
                },
            ],
            "regular_field": "not a url",
        }

        # Test
        result = await FormsManager._refresh_signed_urls(
            cached_storage_manager, test_data
        )

        # Assert
        assert result["signed_url"] == "https://signed-url.com"
        assert result["nested"]["signed_url"] == "https://signed-url.com"
        assert result["list_of_files"][0]["signed_url"] == "https://signed-url.com"
        assert result["list_of_files"][1]["signedUrl"] == "https://signed-url.com"
        assert (
            result["list_of_files"][2]["some_key"]
            == "https://storage.googleapis.com/test-bucket/path/to/file3.jpg"
        )
        assert result["regular_field"] == "not a url"
        assert mock_storage_manager.generate_signed_url.call_count == 4

    @patch(
        "ws_customizable_workflow.managers.services.cache.Cache", new_callable=AsyncMock
    )
    async def test_process_form_data_for_signed_urls_invalid_input(
        self, mock_cache: MagicMock
    ) -> None:
        # Setup
        storage_manager = StorageManager(bucket_name="test-bucket")
        cached_storage_manager = CachedStorageManager(mock_cache, storage_manager)

        # Test with non-dict input
        result = await FormsManager._refresh_signed_urls(
            cached_storage_manager, {"not_a_dict": "value"}
        )
        assert result == {"not_a_dict": "value"}

        # Test with empty dict input
        result = await FormsManager._refresh_signed_urls(cached_storage_manager, {})
        assert result == {}
