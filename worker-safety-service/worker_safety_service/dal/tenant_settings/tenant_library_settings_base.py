import uuid
from typing import Generic, List, Optional, TypeVar

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import delete, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crud_manager import CRUDManager
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.models import (
    AsyncSession,
    CreateTenantLibraryBaseSettingInput,
    Tenant,
    UpdateTenantLibraryBaseSettingInput,
)
from worker_safety_service.models.tenant_library_settings import (
    TenantLibrarySettingsBase,
)

T = TypeVar("T", bound=TenantLibrarySettingsBase)

logger = get_logger(__name__)


# This class provides CRUD operations for managing settings related to a multi-tenant library system.
class TenantLibrarySettingsCRUDBase(CRUDManager[T], Generic[T]):
    def __init__(
        self, session: AsyncSession, entity_type: type[T], primary_key_field: str
    ):
        self.primary_key_field = primary_key_field
        super().__init__(
            session, entity_type, immutable_fields=["tenant_id", primary_key_field]
        )

    async def get(self, tenant_id: uuid.UUID, primary_key_value: uuid.UUID) -> T | None:
        """
        This async function retrieves a tenant setting based on the given `tenant_id` and `primary_key_value`
        using SQLAlchemy and logs the result.

        :tenant_id [uuid.UUID]: The `tenant_id` parameter that identifies a specific tenant in the system.
        It is used to filter the query results to retrieve data specific to that tenant

        :primary_key_value [uuid.UUID]: The `primary_key_value` parameter represents the
        value of the primary key field that you want to use to retrieve an entity from the database.
        This value is used in the query to filter the results and find the specific entity you are
        looking for based on its primary key value

        :return: `T` or `None`.
        """
        try:
            statement = select(self._entity_type).where(
                (getattr(self._entity_type, "tenant_id") == tenant_id)
                & (
                    getattr(self._entity_type, self.primary_key_field)
                    == primary_key_value
                )
            )
            result = (await self.session.exec(statement)).one_or_none()
            if result:
                logger.info(
                    f"Retrieved {self._entity_type.__name__} for tenant_id={tenant_id}, {self.primary_key_field}={primary_key_value}"
                )
            else:
                logger.warning(
                    f"No {self._entity_type.__name__} found for tenant_id={tenant_id}, {self.primary_key_field}={primary_key_value}"
                )
            return result
        except Exception as e:
            logger.error(f"Error retrieving {self._entity_type.__name__}: {str(e)}")
            raise

    async def get_settings(
        self, tenant_id: uuid.UUID, primary_key_values: list[uuid.UUID]
    ) -> dict[uuid.UUID, T]:
        """
        This async function retrieves an tenant settings based on the given `tenant_id` and `primary_key_value`
        using SQLAlchemy and logs the result.

        :tenant_id [uuid.UUID]: The `tenant_id` parameter that identifies a specific tenant in the system.
        It is used to filter the query results to retrieve data specific to that tenant

        :primary_key_values [list[uuid.UUID]]: The `primary_key_values` parameter represents the
        values of the primary key field that you want to use to retrieve an entities from the database.

        :return: `T` or `None`.
        """
        try:
            statement = select(self._entity_type).where(
                (getattr(self._entity_type, "tenant_id") == tenant_id)
                & (
                    getattr(self._entity_type, self.primary_key_field).in_(
                        primary_key_values
                    )
                )
            )
            results = (await self.session.exec(statement)).all()
            if results:
                logger.info(
                    f"Retrieved {len(results)} from {self._entity_type.__name__} for tenant_id={tenant_id}"
                )

            else:
                logger.warning(
                    f"No {self._entity_type.__name__} found for tenant_id={tenant_id} with primary_keys={primary_key_values}"
                )

            return {getattr(i, self.primary_key_field): i for i in results}
        except Exception as e:
            logger.error(
                f"Error retrieving entries from {self._entity_type.__name__}: {str(e)}"
            )
            raise

    async def create_setting(self, input: CreateTenantLibraryBaseSettingInput) -> T:
        """
        This function creates a new setting entity based on the input data, logs the creation, and
        handles exceptions such as entity already existing.

        :input [CreateTenantLibraryBaseSettingInput]: The `create_setting` method is an asynchronous function that creates a new setting
        based on the input provided. The input parameter contains the necessary data for creating the
        setting
        :return: The `create_setting` method returns the created entity if it is successfully created.
        If an `EntityAlreadyExistsException` is caught, it returns the existing entity with the same
        primary key value for the specified tenant. If any other exception occurs during the process, an
        error message is logged, and the exception is raised.
        """
        try:
            entity = self._entity_type(**input.dict())
            created_entity = await self.create(entity)
            logger.info(f"Created new {self._entity_type.__name__}: {created_entity}")
            return created_entity
        except EntityAlreadyExistsException:
            primary_key_value = input.dict()[self.primary_key_field]
            logger.warning(
                f"{self._entity_type.__name__} already exists for tenant_id={input.tenant_id}, {self.primary_key_field}={primary_key_value}"
            )
            tlts = await self.get(input.tenant_id, primary_key_value)
            assert tlts
            return tlts
        except Exception as e:
            logger.error(f"Error creating {self._entity_type.__name__}: {str(e)}")
            raise

    async def update_setting(
        self,
        tenant_id: uuid.UUID,
        primary_key_value: uuid.UUID,
        input: UpdateTenantLibraryBaseSettingInput,
    ) -> T:
        """
        This async function updates a setting for a specific tenant and entity based on the input
        provided.

        :tenant_id [uuid.UUID]: The `tenant_id` parameter is of type `uuid.UUID` and represents the unique
        identifier of a specific tenant in the system. It is used to identify the settings associated
        with a particular tenant

        :primary_key_value [uuid.UUID]: The `primary_key_value` parameter in the `update_setting` method is a
        UUID value that represents the primary key of the entity you want to update. It is used to
        uniquely identify the entity within the specified `tenant_id`
        :input [UpdateTenantLibraryBaseSettingInput]: The `input` parameter in the `update_setting` method
        contains the data that will be used to update the settings for a specific entity associated with a given
        `tenant_id` and `primary_key_value`

        :return: The `update_setting` method is returning the updated entity after updating the alias
        field with the value provided in the input.
        """
        entity = await self.get(tenant_id, primary_key_value)
        if not entity:
            logger.error(
                f"Settings not found for tenant_id={tenant_id}, {self.primary_key_field}={primary_key_value}"
            )
            raise RuntimeError("Settings not found for the specified tenant and entity")
        entity.alias = input.alias
        await self.update(entity)
        await self.session.refresh(entity)
        logger.info(f"Updated {self._entity_type.__name__}: {entity}")
        return entity

    async def delete_setting(
        self, tenant_id: uuid.UUID, primary_key_value: uuid.UUID
    ) -> None:
        """
        This function deletes a setting entity based on the specified `tenant_id` and
        `primary_key_value`.

        :tenant_id [uuid.UUID]: The `tenant_id` parameter is a UUID (Universally Unique Identifier) that
        identifies a specific tenant in the system. It is used to specify which tenant's settings should
        be deleted

        :primary_key_value [uuid.UUID]: The `primary_key_value` parameter in the `delete_setting` method
        represents the unique identifier of the entity you want to delete. In this case, it is a UUID
        value that uniquely identifies the entity within the specified
        `tenant_id`. This value is used to locate and
        """
        entity = await self.get(tenant_id, primary_key_value)
        if not entity:
            logger.error(
                f"Settings not found for tenant_id={tenant_id}, {self.primary_key_field}={primary_key_value}"
            )
            raise RuntimeError("Settings not found for the specified tenant and entity")

        statement = delete(self._entity_type).where(
            (getattr(self._entity_type, "tenant_id") == tenant_id)
            & (getattr(self._entity_type, self.primary_key_field) == primary_key_value)
        )
        await self.session.execute(statement)
        await self.session.commit()
        logger.info(
            f"Deleted {self._entity_type.__name__} with tenant_id={tenant_id}, {self.primary_key_field}={primary_key_value}"
        )

    async def delete_all_settings_by_id(
        self,
        tenant_id: uuid.UUID | None = None,
        primary_key_value: uuid.UUID | None = None,
    ) -> None:
        """
        This function deletes settings based on the provided tenant_id and primary_key_value.

        :tenant_id [uuid.UUID | None]: The `tenant_id` parameter is used to specify the UUID of the tenant for which
        settings should be deleted. If a `tenant_id` is provided, settings associated with that specific
        tenant will be deleted. If `tenant_id` is not provided (i.e., it is `None`), the all settings(across all tenants) with the provided
        `primary_key_value` will be deleted.

        :primary_key_value [uuid.UUID | None]: The `primary_key_value` parameter in the `delete_all_settings_by_id`
        method is used to specify the value of the primary key field for which settings should be
        deleted. If a `primary_key_value` is provided, the method will include a clause in the deletion
        query to delete settings that match the id.

        :return: `None`
        """
        additional_clauses = []
        if tenant_id:
            additional_clauses.append(
                getattr(self._entity_type, "tenant_id") == tenant_id
            )
        if primary_key_value:
            additional_clauses.append(
                getattr(self._entity_type, self.primary_key_field) == primary_key_value
            )

        if not additional_clauses:
            logger.warning("No criteria provided for deletion.")
            return

        try:
            statement = delete(self._entity_type).where(*additional_clauses)
            await self.session.execute(statement)
            await self.session.commit()
            logger.info(
                f"Deleted settings for tenant_id={tenant_id} and primary_key_value={primary_key_value}"
            )
        except Exception as e:
            logger.error(f"Error deleting settings: {str(e)}")
            raise

    async def add_library_entities_for_tenants(
        self,
        primary_key_values: List[uuid.UUID],
        tenant_ids: Optional[List[uuid.UUID]] = None,
    ) -> None:
        """
        Efficiently adds new library entities for each tenant(if no tenant_ids provide)
        in the database, handling multiple primary key values and optional tenant IDs

        :primary_key_values [List[uuid.UUID]]: A list of UUID values for primary keys

        :tenant_ids [Optional[List[str]]]: Optional list of tenant IDs. If not provided, all tenants will be used
        """
        if not tenant_ids:
            tenant_ids = (
                (await self.session.execute(select(Tenant.id).distinct()))
                .scalars()
                .all()
            )

        # Prepare all combinations of primary keys and tenant IDs
        entities_to_add = [
            {
                self.primary_key_field: pk,
                "tenant_id": tenant_id,
            }
            for pk in primary_key_values
            for tenant_id in tenant_ids
        ]

        # Using PostgreSQL's INSERT ... ON CONFLICT DO NOTHING for efficient bulk insert
        stmt = insert(self._entity_type).values(entities_to_add)
        stmt = stmt.on_conflict_do_nothing(
            index_elements=[self.primary_key_field, "tenant_id"],
        )

        try:
            await self.session.flush()
            result = await self.session.execute(stmt)
            await self.session.commit()

            success_count = result.rowcount  # type:ignore
            total_combinations = len(entities_to_add)
            already_exists_count = total_combinations - success_count

            logger.info(
                f"Library entity {self._entity_type.__name__} addition summary: "
                f"Successfully added {success_count} entities, "
                f"Already existed for {already_exists_count} combinations."
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error during bulk insert: {str(e)}")
            raise
