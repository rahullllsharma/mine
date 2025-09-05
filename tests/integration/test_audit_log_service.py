from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from motor.core import AgnosticClient

from tests.factories.form_factory import FormFactory
from ws_customizable_workflow.managers.services.audit_log_service import (
    audit_archive,
    audit_create,
    audit_reopen,
    audit_update,
)
from ws_customizable_workflow.models.base import FormStatus


@pytest.fixture
async def mock_form(db_client: AgnosticClient) -> Any:
    """Create a mock form for testing using FormFactory"""
    form = FormFactory.build()
    # Override datetime fields for consistent testing
    form.created_at = datetime(2023, 1, 1, 12, 0, 0)
    form.updated_at = datetime(2023, 1, 2, 12, 0, 0)
    form.completed_at = datetime(2023, 1, 3, 12, 0, 0)
    form.archived_at = datetime(2023, 1, 4, 12, 0, 0)
    form.properties.status = FormStatus.INPROGRESS
    return form


@pytest.fixture
async def mock_form_completed(db_client: AgnosticClient) -> Any:
    """Create a mock completed form for testing using FormFactory"""
    form = FormFactory.build()
    # Override datetime fields for consistent testing
    form.created_at = datetime(2023, 1, 1, 12, 0, 0)
    form.updated_at = datetime(2023, 1, 2, 12, 0, 0)
    form.completed_at = datetime(2023, 1, 3, 12, 0, 0)
    form.properties.status = FormStatus.COMPLETE
    return form


class TestAuditLogServiceIntegration:
    """Integration tests for audit log service"""

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_full_audit_flow(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test the complete audit flow from decorator to API call"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "audit_log_id"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function
        async def test_create_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form

        # Apply the decorator
        decorated_func = audit_create(test_create_function)

        # Call the decorated function
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        # Verify the result
        assert result == mock_form

        # Verify the API call was made
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args

        # Verify the request URL and headers
        assert "logs/" in call_args[1]["url"]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_token"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"

        # Verify the request body
        request_body = call_args[1]["json"]
        assert request_body["event_type"] == "create"
        assert request_body["object_type"] == "cwf"
        assert request_body["source_app"] == "ws-customizable-workflow"
        assert str(mock_form.id) in request_body["object_id"]

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_audit_flow_with_completed_form(
        self, mock_async_client: MagicMock, mock_form_completed: Any
    ) -> None:
        """Test audit flow when form is completed"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "audit_log_id"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function that returns a completed form
        async def test_update_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form_completed

        # Apply the decorator
        decorated_func = audit_update(test_update_function)

        # Call the decorated function
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        # Verify the result
        assert result == mock_form_completed

        # Verify the API call was made with COMPLETE event type
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        request_body = call_args[1]["json"]
        assert (
            request_body["event_type"] == "complete"
        )  # Should be complete, not update

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_audit_flow_with_reopen_decorator(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test audit flow with reopen decorator"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "audit_log_id"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function
        async def test_reopen_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form

        # Apply the decorator
        decorated_func = audit_reopen(test_reopen_function)

        # Call the decorated function
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        # Verify the result
        assert result == mock_form

        # Verify the API call was made with REOPEN event type
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["event_type"] == "reopen"

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_audit_flow_with_archive_decorator(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test audit flow with archive decorator"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "audit_log_id"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function
        async def test_archive_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form

        # Apply the decorator
        decorated_func = audit_archive(test_archive_function)

        # Call the decorated function
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        # Verify the result
        assert result == mock_form

        # Verify the API call was made with ARCHIVE event type
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        request_body = call_args[1]["json"]
        assert request_body["event_type"] == "archive"

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_audit_flow_without_token(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test audit flow without token (should not make API call)"""
        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function
        async def test_create_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form

        # Apply the decorator
        decorated_func = audit_create(test_create_function)

        # Call the decorated function without token
        result = await decorated_func(MagicMock(), token=None)  # type: ignore[func-returns-value]

        # Verify the result
        assert result == mock_form

        # Verify no API call was made
        mock_client_instance.post.assert_not_called()

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_audit_flow_api_failure(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test audit flow when API call fails"""
        # Mock the response with failure
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        # Create a test function
        async def test_create_function(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form

        # Apply the decorator
        decorated_func = audit_create(test_create_function)

        # Call the decorated function
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        # Verify the result (function should still return even if audit fails)
        assert result == mock_form

        # Verify the API call was made
        mock_client_instance.post.assert_called_once()
