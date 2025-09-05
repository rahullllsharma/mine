from typing import AsyncGenerator

import pytest
from sqlmodel import delete

from tests.factories import DataSourceFactory, SupervisorUserFactory, TenantFactory
from worker_safety_service.dal.data_source import DataSourceManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.data_source import DataSource, DataSourceCreate


@pytest.mark.asyncio
@pytest.mark.integration
class TestDataSourceManager:
    """Test cases for DataSourceManager DAL operations."""

    @pytest.fixture(autouse=True)
    async def cleanup_data_sources(
        self, db_session: AsyncSession
    ) -> AsyncGenerator[None, None]:
        """Clean up data sources after each test to ensure test isolation."""
        yield
        # Clean up after the test
        await db_session.execute(delete(DataSource))
        await db_session.commit()

    async def test_create_new_data_source(self, db_session: AsyncSession) -> None:
        """Test creating a new data source."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        data_source_create = DataSourceCreate(
            name="Test Data Source",
            raw_json={"col1": ["a", "b"], "col2": ["1", "2"]},
            file_name="test.csv",
            original_file_content=b"col1,col2\na,1\nb,2",
            file_type=".csv",
        )

        # Act
        result = await manager.create(data_source_create, user)

        # Assert
        assert result is not None
        assert result.name == "Test Data Source"
        assert result.created_by_id == user.id
        assert result.tenant_id == tenant.id
        assert result.file_name == "test.csv"
        assert result.file_type == ".csv"
        assert result.raw_json == {"col1": ["a", "b"], "col2": ["1", "2"]}
        assert result.updated_at == result.created_at

    async def test_create_overwrites_existing_data_source_same_name_same_tenant(
        self, db_session: AsyncSession
    ) -> None:
        """Test that creating a data source with existing name in same tenant overwrites it."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        user2 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        # Create initial data source
        existing_ds = await DataSourceFactory.persist(
            db_session,
            name="Shared Name",
            raw_json={"old": ["data"]},
            file_name="old.csv",
            tenant_id=tenant.id,
            created_by_user_id=user1.id,
        )
        original_id = existing_ds.id
        original_created_at = existing_ds.created_at

        # Create new data source with same name
        new_data_source = DataSourceCreate(
            name="Shared Name",
            raw_json={"new": ["data"]},
            file_name="new.csv",
            original_file_content=b"new,data",
            file_type=".csv",
        )

        # Act
        result = await manager.create(new_data_source, user2)

        # Assert
        assert result is not None
        assert result.id == original_id  # Same ID (updated, not created)
        assert result.name == "Shared Name"
        assert result.raw_json == {"new": ["data"]}  # Updated content
        assert result.file_name == "new.csv"  # Updated filename
        assert result.created_by_id == user1.id  # Original creator unchanged
        assert result.tenant_id == tenant.id
        assert result.created_at == original_created_at  # Created time unchanged
        assert (
            result.updated_at is not None and result.updated_at > original_created_at
        )  # Updated time changed

    async def test_create_allows_same_name_different_tenants(
        self, db_session: AsyncSession
    ) -> None:
        """Test that data sources with same name are allowed in different tenants."""
        # Arrange
        tenant1 = await TenantFactory.default_tenant(db_session)
        tenant2 = await TenantFactory.extra_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant1.id)
        user2 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant2.id)
        manager = DataSourceManager(db_session)

        # Create data source in tenant1
        data_source1 = DataSourceCreate(
            name="Shared Name",
            raw_json={"tenant1": ["data"]},
            file_name="tenant1.csv",
            original_file_content=b"tenant1,data",
            file_type=".csv",
        )

        # Create data source in tenant2 with same name
        data_source2 = DataSourceCreate(
            name="Shared Name",
            raw_json={"tenant2": ["data"]},
            file_name="tenant2.csv",
            original_file_content=b"tenant2,data",
            file_type=".csv",
        )

        # Act
        result1 = await manager.create(data_source1, user1)
        result2 = await manager.create(data_source2, user2)

        # Assert
        assert result1 is not None
        assert result2 is not None
        assert result1.id != result2.id  # Different IDs
        assert result1.name == result2.name == "Shared Name"
        assert result1.tenant_id == tenant1.id
        assert result2.tenant_id == tenant2.id
        assert result1.raw_json == {"tenant1": ["data"]}
        assert result2.raw_json == {"tenant2": ["data"]}

    async def test_get_all_filters_by_tenant(self, db_session: AsyncSession) -> None:
        """Test that get_all only returns data sources for the specified tenant."""
        # Arrange
        tenant1 = await TenantFactory.default_tenant(db_session)
        tenant2 = await TenantFactory.extra_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant1.id)
        user2 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant2.id)
        manager = DataSourceManager(db_session)

        # Create data sources in different tenants
        await DataSourceFactory.persist(
            db_session,
            name="Tenant1 DS",
            tenant_id=tenant1.id,
            created_by_user_id=user1.id,
        )
        await DataSourceFactory.persist(
            db_session,
            name="Tenant2 DS",
            tenant_id=tenant2.id,
            created_by_user_id=user2.id,
        )

        # Act
        tenant1_results = await manager.get_all(tenant1.id)
        tenant2_results = await manager.get_all(tenant2.id)

        # Assert
        assert len(tenant1_results) == 1
        assert len(tenant2_results) == 1
        assert tenant1_results[0][0].name == "Tenant1 DS"
        assert tenant2_results[0][0].name == "Tenant2 DS"
        assert tenant1_results[0][0].tenant_id == tenant1.id
        assert tenant2_results[0][0].tenant_id == tenant2.id

    async def test_get_all_orders_by_updated_at_desc(
        self, db_session: AsyncSession
    ) -> None:
        """Test that get_all returns data sources ordered by updated_at descending."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        # Create data sources with different update times
        await DataSourceFactory.persist(
            db_session, name="First", tenant_id=tenant.id, created_by_user_id=user.id
        )
        await DataSourceFactory.persist(
            db_session, name="Second", tenant_id=tenant.id, created_by_user_id=user.id
        )
        await DataSourceFactory.persist(
            db_session, name="Third", tenant_id=tenant.id, created_by_user_id=user.id
        )

        # Act
        results = await manager.get_all(tenant.id)

        # Assert
        assert len(results) == 3
        # Should be ordered by updated_at descending (newest first)
        assert results[0][0].name == "Third"  # Most recent
        assert results[1][0].name == "Second"
        assert results[2][0].name == "First"  # Oldest

    async def test_get_all_includes_user_information(
        self, db_session: AsyncSession
    ) -> None:
        """Test that get_all returns user information with data sources."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        await DataSourceFactory.persist(
            db_session, name="Test DS", tenant_id=tenant.id, created_by_user_id=user.id
        )

        # Act
        results = await manager.get_all(tenant.id)

        # Assert
        assert len(results) == 1
        data_source, created_by_user = results[0]
        assert data_source.name == "Test DS"
        assert created_by_user is not None
        assert created_by_user.id == user.id

    async def test_get_data_source_by_id_with_tenant_filter(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_data_source_by_id with tenant filtering."""
        # Arrange
        tenant1 = await TenantFactory.default_tenant(db_session)
        tenant2 = await TenantFactory.extra_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant1.id)
        manager = DataSourceManager(db_session)

        ds = await DataSourceFactory.persist(
            db_session, tenant_id=tenant1.id, created_by_user_id=user1.id
        )

        # Act & Assert
        # Should find data source when correct tenant is provided
        result1 = await manager.get_data_source_by_id(str(ds.id), tenant1.id)
        assert result1 is not None
        assert result1.id == ds.id

        # Should not find data source when wrong tenant is provided
        result2 = await manager.get_data_source_by_id(str(ds.id), tenant2.id)
        assert result2 is None

        # Should find data source when no tenant filter is provided
        result3 = await manager.get_data_source_by_id(str(ds.id))
        assert result3 is not None
        assert result3.id == ds.id

    async def test_get_data_source_by_name_with_tenant_filter(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_data_source_by_name with tenant filtering."""
        # Arrange
        tenant1 = await TenantFactory.default_tenant(db_session)
        tenant2 = await TenantFactory.extra_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant1.id)
        user2 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant2.id)
        manager = DataSourceManager(db_session)

        # Create data sources with same name in different tenants
        ds1 = await DataSourceFactory.persist(
            db_session,
            name="Same Name",
            tenant_id=tenant1.id,
            created_by_user_id=user1.id,
        )
        ds2 = await DataSourceFactory.persist(
            db_session,
            name="Same Name",
            tenant_id=tenant2.id,
            created_by_user_id=user2.id,
        )

        # Act & Assert
        # Should find correct data source for tenant1
        result1 = await manager.get_data_source_by_name("Same Name", tenant1.id)
        assert result1 is not None
        assert result1.id == ds1.id
        assert result1.tenant_id == tenant1.id

        # Should find correct data source for tenant2
        result2 = await manager.get_data_source_by_name("Same Name", tenant2.id)
        assert result2 is not None
        assert result2.id == ds2.id
        assert result2.tenant_id == tenant2.id

    async def test_get_column_data_with_tenant_filter(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_column_data with tenant filtering."""
        # Arrange
        tenant1 = await TenantFactory.default_tenant(db_session)
        tenant2 = await TenantFactory.extra_tenant(db_session)
        user1 = await SupervisorUserFactory.persist(db_session, tenant_id=tenant1.id)
        await SupervisorUserFactory.persist(db_session, tenant_id=tenant2.id)
        manager = DataSourceManager(db_session)

        ds = await DataSourceFactory.persist(
            db_session,
            raw_json={"column1": ["value1", "value2"], "column2": ["value3", "value4"]},
            tenant_id=tenant1.id,
            created_by_user_id=user1.id,
        )

        # Act & Assert
        # Should return column data when correct tenant is provided
        result1 = await manager.get_column_data(str(ds.id), "column1", tenant1.id)
        assert result1 == ["value1", "value2"]

        # Should return None when wrong tenant is provided
        result2 = await manager.get_column_data(str(ds.id), "column1", tenant2.id)
        assert result2 is None

        # Should return column data when no tenant filter is provided
        result3 = await manager.get_column_data(str(ds.id), "column1")
        assert result3 == ["value1", "value2"]

    async def test_get_column_data_nonexistent_column(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_column_data with non-existent column."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        ds = await DataSourceFactory.persist(
            db_session,
            raw_json={"column1": ["value1", "value2"]},
            tenant_id=tenant.id,
            created_by_user_id=user.id,
        )

        # Act
        result = await manager.get_column_data(
            str(ds.id), "nonexistent_column", tenant.id
        )

        # Assert
        assert result == []  # Should return empty list for non-existent column

    async def test_get_column_data_with_empty_values_in_data(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_column_data with data that has empty values."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        # Create data source with mixed data including empty values
        ds = await DataSourceFactory.persist(
            db_session,
            raw_json={
                "names": ["Alice", "Bob", "Charlie"],  # All non-empty
                "ages": [
                    "25",
                    "35",
                ],  # Missing some values (empty values were filtered out during parsing)
                "cities": [
                    "NYC",
                    "LA",
                ],  # Missing some values (empty values were filtered out during parsing)
            },
            tenant_id=tenant.id,
            created_by_user_id=user.id,
        )

        # Act
        names_result = await manager.get_column_data(str(ds.id), "names", tenant.id)
        ages_result = await manager.get_column_data(str(ds.id), "ages", tenant.id)
        cities_result = await manager.get_column_data(str(ds.id), "cities", tenant.id)

        # Assert
        assert names_result == ["Alice", "Bob", "Charlie"]
        assert ages_result == ["25", "35"]  # Only non-empty values
        assert cities_result == ["NYC", "LA"]  # Only non-empty values

    async def test_get_column_data_invalid_data_format(
        self, db_session: AsyncSession
    ) -> None:
        """Test get_column_data with invalid data format in raw_json."""
        # Arrange
        tenant = await TenantFactory.default_tenant(db_session)
        user = await SupervisorUserFactory.persist(db_session, tenant_id=tenant.id)
        manager = DataSourceManager(db_session)

        ds = await DataSourceFactory.persist(
            db_session,
            raw_json={"column1": "not_a_list"},  # Invalid format
            tenant_id=tenant.id,
            created_by_user_id=user.id,
        )

        # Act
        result = await manager.get_column_data(str(ds.id), "column1", tenant.id)

        # Assert
        assert result == []  # Should return empty list for invalid format
