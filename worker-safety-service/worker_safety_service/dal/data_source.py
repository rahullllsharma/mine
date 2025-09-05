import uuid

from sqlmodel import desc, select

from worker_safety_service.models import (
    AsyncSession,
    DataSource,
    DataSourceCreate,
    User,
)
from worker_safety_service.models.utils import db_default_utcnow
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class DataSourceManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, data_source: DataSourceCreate, user: User
    ) -> DataSource | None:
        """
        Create or overwrite a data source. If a data source with the same name exists,
        it will be updated with the new data instead of creating a new one.
        """
        try:
            # Check if a data source with the same name already exists
            existing_data_source = await self.get_data_source_by_name(
                data_source.name, user.tenant_id
            )

            if existing_data_source:
                # Update the existing data source with new data
                existing_data_source.raw_json = data_source.raw_json
                existing_data_source.file_name = data_source.file_name
                existing_data_source.original_file_content = (
                    data_source.original_file_content
                )
                existing_data_source.file_type = data_source.file_type
                # Set updated_at for updates
                existing_data_source.updated_at = db_default_utcnow()

                self.session.add(existing_data_source)
                await self.session.commit()
                logger.info(
                    "Data source updated (overwritten)",
                    data_source_id=str(existing_data_source.id),
                    data_source_name=existing_data_source.name,
                )
                return existing_data_source
            else:
                # Create a new data source
                db_data_source = DataSource.from_orm(data_source)
                # Set creator and tenant on creation
                db_data_source.created_by_id = user.id
                db_data_source.tenant_id = user.tenant_id
                # Set updated_at on creation to match created_at
                db_data_source.updated_at = db_data_source.created_at
                self.session.add(db_data_source)
                await self.session.commit()
                logger.info(
                    "Data source created",
                    data_source_id=str(db_data_source.id),
                    data_source_name=db_data_source.name,
                )
                return db_data_source

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to create or update data source",
                error=str(e),
                data_source_name=data_source.name,
            )
            return None

    async def get_all(self, tenant_id: uuid.UUID) -> list[tuple[DataSource, User]]:
        statement = (
            select(DataSource, User)
            .join(User, DataSource.created_by_id == User.id)
            .where(DataSource.tenant_id == tenant_id)
            .order_by(desc(DataSource.updated_at))
        )
        return (await self.session.exec(statement)).all()

    async def get_data_source_by_id(
        self, data_source_id: str, tenant_id: uuid.UUID | None = None
    ) -> DataSource | None:
        statement = select(DataSource).where(DataSource.id == data_source_id)
        if tenant_id:
            statement = statement.where(DataSource.tenant_id == tenant_id)
        return (await self.session.exec(statement)).first()

    async def get_data_source_by_name(
        self, name: str, tenant_id: uuid.UUID | None = None
    ) -> DataSource | None:
        statement = select(DataSource).where(DataSource.name == name)
        if tenant_id:
            statement = statement.where(DataSource.tenant_id == tenant_id)
        return (await self.session.exec(statement)).first()

    async def get_column_data(
        self, data_source_id: str, column_name: str, tenant_id: uuid.UUID | None = None
    ) -> list[str] | None:
        """Get all values for a specific column in a data source."""
        data_source = await self.get_data_source_by_id(data_source_id, tenant_id)
        if not data_source or not data_source.raw_json:
            return None

        column_data = data_source.raw_json.get(column_name, [])
        return column_data if isinstance(column_data, list) else []
