import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from worker_safety_service.dal.data_source import DataSourceManager
from worker_safety_service.models import User
from worker_safety_service.models.data_source import DataSource, DataSourceCreate
from worker_safety_service.rest.routers.uploads import (
    create_data_source,
    download_data_source,
    get_column_data,
    get_data_sources,
)


@pytest.mark.asyncio
@pytest.mark.unit
class TestDataSourceRouter:
    """Unit tests for data source router functions."""

    @pytest.fixture
    def mock_user(self) -> MagicMock:
        """Create a mock user."""
        user = MagicMock(spec=User)
        user.id = uuid.uuid4()
        user.tenant_id = uuid.uuid4()
        user.get_name.return_value = "Test User"
        return user

    @pytest.fixture
    def mock_data_source_manager(self) -> MagicMock:
        """Create a mock data source manager."""
        return MagicMock(spec=DataSourceManager)

    @pytest.fixture
    def mock_data_source(self) -> MagicMock:
        """Create a mock data source."""
        ds = MagicMock(spec=DataSource)
        ds.id = uuid.uuid4()
        ds.name = "Test DS"
        ds.raw_json = {"col1": ["val1", "val2"], "col2": ["val3", "val4"]}
        ds.file_name = "test.csv"
        ds.file_type = ".csv"
        ds.original_file_content = b"col1,col2\nval1,val3\nval2,val4"
        return ds

    async def test_get_data_sources_success(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test successful retrieval of data sources."""
        # Arrange
        mock_created_by_user = MagicMock()
        mock_created_by_user.get_name.return_value = "Creator User"

        mock_ds = MagicMock()
        mock_ds.id = uuid.uuid4()
        mock_ds.name = "Test DS"
        mock_ds.created_by_id = uuid.uuid4()
        mock_ds.tenant_id = mock_user.tenant_id
        mock_ds.archived_at = None
        mock_ds.raw_json = {"col1": ["val1"], "col2": ["val2"]}
        mock_ds.file_name = "test.csv"
        mock_ds.file_type = ".csv"
        mock_ds.created_at = "2023-01-01T00:00:00"
        mock_ds.updated_at = "2023-01-01T00:00:00"

        mock_data_source_manager.get_all.return_value = [
            (mock_ds, mock_created_by_user)
        ]

        # Act
        result = await get_data_sources(mock_user, mock_data_source_manager)

        # Assert
        mock_data_source_manager.get_all.assert_called_once_with(mock_user.tenant_id)
        assert len(result) == 1
        assert result[0].name == "Test DS"
        assert result[0].created_by_username == "Creator User"
        assert result[0].columns == ["col1", "col2"]

    async def test_get_data_sources_empty_list(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test get_data_sources returns empty list when no data sources exist."""
        # Arrange
        mock_data_source_manager.get_all.return_value = []

        # Act
        result = await get_data_sources(mock_user, mock_data_source_manager)

        # Assert
        assert result == []

    async def test_get_column_data_success(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test successful column data retrieval."""
        # Arrange
        data_source_id = str(uuid.uuid4())
        column_name = "test_column"
        expected_data = ["value1", "value2", "value3"]

        mock_data_source_manager.get_column_data.return_value = expected_data

        # Act
        result = await get_column_data(
            data_source_id, column_name, mock_user, mock_data_source_manager
        )

        # Assert
        mock_data_source_manager.get_column_data.assert_called_once_with(
            data_source_id, column_name, mock_user.tenant_id
        )
        assert isinstance(result, JSONResponse)
        assert result.status_code == 200

    async def test_get_column_data_not_found(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test get_column_data raises HTTPException when data source or column not found."""
        # Arrange
        data_source_id = str(uuid.uuid4())
        column_name = "nonexistent_column"

        mock_data_source_manager.get_column_data.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_column_data(
                data_source_id, column_name, mock_user, mock_data_source_manager
            )

        assert exc_info.value.status_code == 404
        assert "Data source or column not found" in str(exc_info.value.detail)

    async def test_download_data_source_success(
        self,
        mock_user: MagicMock,
        mock_data_source_manager: MagicMock,
        mock_data_source: MagicMock,
    ) -> None:
        """Test successful data source download."""
        # Arrange
        data_source_id = str(mock_data_source.id)
        mock_data_source_manager.get_data_source_by_id.return_value = mock_data_source

        # Act
        result = await download_data_source(
            data_source_id, mock_user, mock_data_source_manager
        )

        # Assert
        mock_data_source_manager.get_data_source_by_id.assert_called_once_with(
            data_source_id, mock_user.tenant_id
        )
        assert isinstance(result, StreamingResponse)
        assert result.media_type == "text/csv"
        assert "attachment; filename=test.csv" in result.headers["Content-Disposition"]

    async def test_download_data_source_not_found(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test download raises HTTPException when data source not found."""
        # Arrange
        data_source_id = str(uuid.uuid4())
        mock_data_source_manager.get_data_source_by_id.return_value = None

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await download_data_source(
                data_source_id, mock_user, mock_data_source_manager
            )

        assert exc_info.value.status_code == 404
        assert "Data source not found" in str(exc_info.value.detail)

    async def test_download_data_source_no_content(
        self,
        mock_user: MagicMock,
        mock_data_source_manager: MagicMock,
        mock_data_source: MagicMock,
    ) -> None:
        """Test download raises HTTPException when original file content is missing."""
        # Arrange
        data_source_id = str(mock_data_source.id)
        mock_data_source.original_file_content = None
        mock_data_source_manager.get_data_source_by_id.return_value = mock_data_source

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await download_data_source(
                data_source_id, mock_user, mock_data_source_manager
            )

        assert exc_info.value.status_code == 404
        assert "Original file content not available" in str(exc_info.value.detail)

    async def test_create_data_source_success_csv(
        self,
        mock_user: MagicMock,
        mock_data_source_manager: MagicMock,
        mock_data_source: MagicMock,
    ) -> None:
        """Test successful CSV data source creation."""
        # Arrange
        csv_content = "name,age\nJohn,25\nJane,30"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.read = AsyncMock(return_value=csv_content.encode())

        mock_data_source_manager.create.return_value = mock_data_source

        # Mock the parse_file function
        with patch(
            "worker_safety_service.rest.routers.uploads.parse_file"
        ) as mock_parse:
            mock_parse.return_value = {"name": ["John", "Jane"], "age": ["25", "30"]}

            # Act
            result = await create_data_source(
                mock_file, "Test Dataset", mock_user, mock_data_source_manager
            )

        # Assert
        assert isinstance(result, JSONResponse)
        assert result.status_code == 200
        mock_data_source_manager.create.assert_called_once()

        # Verify the DataSourceCreate object passed to create method
        create_call_args = mock_data_source_manager.create.call_args[0]
        assert isinstance(create_call_args[0], DataSourceCreate)
        assert create_call_args[0].name == "Test Dataset"
        assert create_call_args[0].file_type == ".csv"
        assert create_call_args[1] == mock_user

    async def test_create_data_source_missing_filename(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test create_data_source returns error when filename is missing."""
        # Arrange
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = None

        # Act
        result = await create_data_source(
            mock_file, None, mock_user, mock_data_source_manager
        )

        # Assert
        assert isinstance(result, JSONResponse)
        assert result.status_code == 400
        # You would need to parse the response content to check the exact message

    async def test_create_data_source_unsupported_file_type(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test create_data_source returns error for unsupported file types."""
        # Arrange
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"

        # Act
        result = await create_data_source(
            mock_file, None, mock_user, mock_data_source_manager
        )

        # Assert
        assert isinstance(result, JSONResponse)
        assert result.status_code == 400

    async def test_create_data_source_uses_filename_when_name_not_provided(
        self,
        mock_user: MagicMock,
        mock_data_source_manager: MagicMock,
        mock_data_source: MagicMock,
    ) -> None:
        """Test that data source name defaults to filename when not provided."""
        # Arrange
        csv_content = "col1,col2\nval1,val2"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "my-dataset.csv"
        mock_file.read = AsyncMock(return_value=csv_content.encode())

        mock_data_source_manager.create.return_value = mock_data_source

        # Mock the parse_file function
        with patch(
            "worker_safety_service.rest.routers.uploads.parse_file"
        ) as mock_parse:
            mock_parse.return_value = {"col1": ["val1"], "col2": ["val2"]}

            # Act
            await create_data_source(
                mock_file, None, mock_user, mock_data_source_manager
            )

        # Assert
        create_call_args = mock_data_source_manager.create.call_args[0]
        assert create_call_args[0].name == "my-dataset"  # Without extension

    async def test_create_data_source_creation_failure(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test create_data_source handles creation failure."""
        # Arrange
        csv_content = "col1,col2\nval1,val2"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.read = AsyncMock(return_value=csv_content.encode())

        mock_data_source_manager.create.return_value = None  # Simulate failure

        # Mock the parse_file function
        with patch(
            "worker_safety_service.rest.routers.uploads.parse_file"
        ) as mock_parse:
            mock_parse.return_value = {"col1": ["val1"], "col2": ["val2"]}

            # Act
            result = await create_data_source(
                mock_file, "Test", mock_user, mock_data_source_manager
            )

        # Assert
        assert isinstance(result, JSONResponse)
        assert result.status_code == 500

    async def test_create_data_source_parse_error(
        self, mock_user: MagicMock, mock_data_source_manager: MagicMock
    ) -> None:
        """Test create_data_source handles file parsing errors."""
        # Arrange
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.csv"
        mock_file.read = AsyncMock(return_value=b"invalid csv content")

        # Mock the parse_file function to raise ValueError
        with patch(
            "worker_safety_service.rest.routers.uploads.parse_file"
        ) as mock_parse:
            mock_parse.side_effect = ValueError("Invalid CSV format")

            # Act
            result = await create_data_source(
                mock_file, "Test", mock_user, mock_data_source_manager
            )

        # Assert
        assert isinstance(result, JSONResponse)
        assert result.status_code == 400

    @pytest.mark.parametrize(
        "file_type,expected_content_type",
        [
            (".csv", "text/csv"),
            (
                ".xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
            (".xls", "application/vnd.ms-excel"),
            (".xlsm", "application/vnd.ms-excel.sheet.macroEnabled.12"),
            (".unknown", "application/octet-stream"),
        ],
    )
    async def test_download_content_types(
        self,
        mock_user: MagicMock,
        mock_data_source_manager: MagicMock,
        mock_data_source: MagicMock,
        file_type: str,
        expected_content_type: str,
    ) -> None:
        """Test that download returns correct content type for different file types."""
        # Arrange
        mock_data_source.file_type = file_type
        data_source_id = str(mock_data_source.id)
        mock_data_source_manager.get_data_source_by_id.return_value = mock_data_source

        # Act
        download_result = await download_data_source(
            data_source_id, mock_user, mock_data_source_manager
        )

        # Assert
        assert isinstance(download_result, StreamingResponse)
        assert download_result.media_type == expected_content_type
