import uuid
from datetime import datetime
from typing import Any, Awaitable, Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mongomock_motor import AsyncMongoMockClient

from tests.factories.form_factory import FormFactory
from ws_customizable_workflow.managers.services.audit_log_service import (
    AuditLogRequest,
    EventType,
    ObjectType,
    _generate_request,
    _post_audit_log,
    audit_archive,
    audit_create,
    audit_reopen,
    audit_update,
    call_audit,
)
from ws_customizable_workflow.models.base import FormStatus
from ws_customizable_workflow.models.form_models import FormProperties


@pytest.fixture
async def mock_form(db_client: AsyncMongoMockClient) -> Any:
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
async def mock_form_completed(db_client: AsyncMongoMockClient) -> Any:
    """Create a mock completed form for testing using FormFactory"""
    form = FormFactory.build()
    # Override datetime fields for consistent testing
    form.created_at = datetime(2023, 1, 1, 12, 0, 0)
    form.updated_at = datetime(2023, 1, 2, 12, 0, 0)
    form.completed_at = datetime(2023, 1, 3, 12, 0, 0)
    form.properties.status = FormStatus.COMPLETE
    return form


@pytest.fixture
def mock_async_func() -> Callable[..., Awaitable["MockForm"]]:
    """Create a mock async function for testing"""

    async def mock_func(cls: Any, *args: Any, **kwargs: Any) -> MockForm:
        return MockForm(
            id=uuid.uuid4(),
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            updated_at=datetime(2023, 1, 2, 12, 0, 0),
            properties=FormProperties(title="Test Form", status=FormStatus.INPROGRESS),
        )

    return mock_func


class MockForm:
    """Simple mock form class for testing audit log service"""

    def __init__(self, **kwargs: Any) -> None:
        self.id = kwargs.get("id", uuid.uuid4())
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())
        self.completed_at = kwargs.get("completed_at")
        self.archived_at = kwargs.get("archived_at")
        self.properties = kwargs.get("properties", FormProperties(title="Test Form"))


class TestAuditLogRequest:
    """Test cases for AuditLogRequest model"""

    def test_audit_log_request_creation(self) -> None:
        """Test creating an AuditLogRequest with required fields"""
        request = AuditLogRequest(
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            object_id=uuid.uuid4(),
            event_type=EventType.CREATE,
            location=None,
        )

        assert request.created_at == datetime(2023, 1, 1, 12, 0, 0)
        assert request.object_type == ObjectType.CWF
        assert request.source_app == "ws-customizable-workflow"
        assert request.location is None
        assert request.new_value is None
        assert request.old_value is None

    def test_audit_log_request_with_optional_fields(self) -> None:
        """Test creating an AuditLogRequest with optional fields"""
        object_id = uuid.uuid4()
        request = AuditLogRequest(
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            object_id=object_id,
            location="Test Location",
            event_type=EventType.UPDATE,
            new_value={"status": "completed"},
            old_value={"status": "in_progress"},
        )

        assert request.object_id == object_id
        assert request.location == "Test Location"
        assert request.event_type == EventType.UPDATE
        assert request.new_value == {"status": "completed"}
        assert request.old_value == {"status": "in_progress"}


class TestGenerateRequest:
    """Test cases for _generate_request function"""

    def test_generate_request_create(self, mock_form: Any) -> None:
        """Test generating request for CREATE event"""
        request = _generate_request(EventType.CREATE, mock_form)

        assert request.created_at == mock_form.created_at
        assert request.object_id == mock_form.id
        assert request.event_type == EventType.CREATE
        assert request.object_type == ObjectType.CWF

    def test_generate_request_update(self, mock_form: Any) -> None:
        """Test generating request for UPDATE event"""
        request = _generate_request(EventType.UPDATE, mock_form)

        assert request.created_at == mock_form.updated_at
        assert request.object_id == mock_form.id
        assert request.event_type == EventType.UPDATE

    def test_generate_request_complete(self, mock_form: Any) -> None:
        """Test generating request for COMPLETE event"""
        request = _generate_request(EventType.COMPLETE, mock_form)

        assert request.created_at == mock_form.completed_at
        assert request.object_id == mock_form.id
        assert request.event_type == EventType.COMPLETE

    def test_generate_request_reopen(self, mock_form: Any) -> None:
        """Test generating request for REOPEN event"""
        request = _generate_request(EventType.REOPEN, mock_form)

        assert request.created_at == mock_form.updated_at
        assert request.object_id == mock_form.id
        assert request.event_type == EventType.REOPEN

    def test_generate_request_archive(self, mock_form: Any) -> None:
        """Test generating request for ARCHIVE event"""
        request = _generate_request(EventType.ARCHIVE, mock_form)

        assert request.created_at == mock_form.archived_at
        assert request.object_id == mock_form.id
        assert request.event_type == EventType.ARCHIVE


class TestPostAuditLog:
    """Test cases for _post_audit_log function"""

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_post_audit_log_success(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test successful audit log posting"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "audit_log_id"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        request = AuditLogRequest(
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            object_id=mock_form.id,
            event_type=EventType.CREATE,
            location=None,
        )

        result = await _post_audit_log(request, "test_token")

        assert result == {"id": "audit_log_id"}
        mock_client_instance.post.assert_called_once()

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.AsyncClient")
    async def test_post_audit_log_failure(
        self, mock_async_client: MagicMock, mock_form: Any
    ) -> None:
        """Test audit log posting failure"""
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "Internal server error"}

        # Mock the client context manager
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_async_client.return_value.__aenter__.return_value = mock_client_instance

        request = AuditLogRequest(
            created_at=datetime(2023, 1, 1, 12, 0, 0),
            object_id=mock_form.id,
            event_type=EventType.CREATE,
            location=None,
        )

        result = await _post_audit_log(request, "test_token")

        assert result == {"error": "Internal server error"}


class TestCallAudit:
    """Test cases for call_audit function"""

    @pytest.mark.asyncio
    @patch(
        "ws_customizable_workflow.managers.services.audit_log_service._post_audit_log"
    )
    async def test_call_audit_success(
        self,
        mock_post_audit: AsyncMock,
        mock_async_func: Callable[..., Awaitable[Any]],
        mock_form: Any,
    ) -> None:
        """Test successful audit call"""
        mock_post_audit.return_value = {"id": "audit_log_id"}

        result = await call_audit(  # type: ignore[func-returns-value]
            cls=MagicMock(),
            func=mock_async_func,
            event_type=EventType.CREATE,
            token="test_token",
        )

        assert result is not None
        mock_post_audit.assert_called_once()

    @pytest.mark.asyncio
    @patch(
        "ws_customizable_workflow.managers.services.audit_log_service._post_audit_log"
    )
    async def test_call_audit_no_token(
        self, mock_post_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit call without token"""
        result = await call_audit(  # type: ignore[func-returns-value]
            cls=MagicMock(),
            func=mock_async_func,
            event_type=EventType.CREATE,
            token=None,
        )

        assert result is not None
        mock_post_audit.assert_not_called()

    @pytest.mark.asyncio
    @patch(
        "ws_customizable_workflow.managers.services.audit_log_service._post_audit_log"
    )
    async def test_call_audit_completed_form(
        self,
        mock_post_audit: AsyncMock,
        mock_async_func: Callable[..., Awaitable[Any]],
        mock_form_completed: Any,
    ) -> None:
        """Test audit call for completed form"""
        mock_post_audit.return_value = {"id": "audit_log_id"}

        # Mock the function to return a completed form
        async def mock_completed_func(cls: Any, *args: Any, **kwargs: Any) -> Any:
            return mock_form_completed

        result = await call_audit(  # type: ignore[func-returns-value]
            cls=MagicMock(),
            func=mock_completed_func,
            event_type=EventType.UPDATE,
            token="test_token",
        )

        assert result is not None
        # Should call with COMPLETE event type for completed forms
        call_args = mock_post_audit.call_args[0]
        assert call_args[0].event_type == EventType.COMPLETE

    @pytest.mark.asyncio
    @patch(
        "ws_customizable_workflow.managers.services.audit_log_service._post_audit_log"
    )
    async def test_call_audit_exception_handling(
        self, mock_post_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit call with exception handling"""
        mock_post_audit.side_effect = Exception("Network error")

        result = await call_audit(  # type: ignore[func-returns-value]
            cls=MagicMock(),
            func=mock_async_func,
            event_type=EventType.CREATE,
            token="test_token",
        )

        assert result is not None  # Function should still return the result


class TestAuditDecorators:
    """Test cases for audit decorators"""

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_audit_create_decorator(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit_create decorator"""
        mock_call_audit.return_value = MockForm(
            properties=FormProperties(title="Test Form")
        )

        decorated_func = audit_create(mock_async_func)
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        assert result is not None
        mock_call_audit.assert_called_once()
        # Check that EventType.CREATE was passed
        call_args = mock_call_audit.call_args[0]
        assert call_args[2] == EventType.CREATE

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_audit_reopen_decorator(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit_reopen decorator"""
        mock_call_audit.return_value = MockForm(
            properties=FormProperties(title="Test Form")
        )

        decorated_func = audit_reopen(mock_async_func)
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        assert result is not None
        mock_call_audit.assert_called_once()
        # Check that EventType.REOPEN was passed
        call_args = mock_call_audit.call_args[0]
        assert call_args[2] == EventType.REOPEN

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_audit_update_decorator(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit_update decorator"""
        mock_call_audit.return_value = MockForm(
            properties=FormProperties(title="Test Form")
        )

        decorated_func = audit_update(mock_async_func)
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        assert result is not None
        mock_call_audit.assert_called_once()
        # Check that EventType.UPDATE was passed
        call_args = mock_call_audit.call_args[0]
        assert call_args[2] == EventType.UPDATE

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_audit_archive_decorator(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test audit_archive decorator"""
        mock_call_audit.return_value = MockForm(
            properties=FormProperties(title="Test Form")
        )

        decorated_func = audit_archive(mock_async_func)
        result = await decorated_func(MagicMock(), token="test_token")  # type: ignore[func-returns-value]

        assert result is not None
        mock_call_audit.assert_called_once()
        # Check that EventType.ARCHIVE was passed
        call_args = mock_call_audit.call_args[0]
        assert call_args[2] == EventType.ARCHIVE

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_decorator_preserves_function_metadata(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test that decorators preserve function metadata"""
        decorated_func = audit_create(mock_async_func)

        assert decorated_func.__name__ == mock_async_func.__name__
        assert decorated_func.__doc__ == mock_async_func.__doc__

    @pytest.mark.asyncio
    @patch("ws_customizable_workflow.managers.services.audit_log_service.call_audit")
    async def test_decorator_passes_arguments_correctly(
        self, mock_call_audit: AsyncMock, mock_async_func: Callable[..., Awaitable[Any]]
    ) -> None:
        """Test that decorators pass arguments correctly"""
        mock_call_audit.return_value = MockForm(
            properties=FormProperties(title="Test Form")
        )

        decorated_func = audit_create(mock_async_func)
        await decorated_func(
            MagicMock(),
            arg1="value1",
            arg2="value2",
            token="test_token",
            extra_kwarg="extra_value",
        )

        # Check that call_audit was called with the correct arguments
        mock_call_audit.assert_called_once()
        call_args = mock_call_audit.call_args
        assert call_args[0][0] is not None  # cls
        assert call_args[0][1] == mock_async_func  # func
        assert call_args[0][2] == EventType.CREATE  # event_type
        assert call_args[1]["arg1"] == "value1"
        assert call_args[1]["arg2"] == "value2"
        assert call_args[1]["extra_kwarg"] == "extra_value"
        assert call_args[1]["token"] == "test_token"  # token should be passed through
