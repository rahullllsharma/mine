from uuid import UUID

from pydantic import BaseModel
from sqlmodel import col, select

from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    AsyncSession,
    IngestionSettings,
    ParsedFile,
    Tenant,
    TenantCreate,
    TenantEdit,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class RealmDetails(BaseModel):
    realm_name: str
    client_id: str


GRAPHQL_CLIENT_ID_TEMPLATE = "worker-safety-{}"


class TenantManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tenant_by_auth_realm(
        self, auth_realm_name: str, audience: str | None = None
    ) -> Tenant | None:
        """
        Retrieve a tenant by its name
        """

        statement = select(Tenant).where(Tenant.auth_realm_name == auth_realm_name)

        if audience is not None:
            statement = statement.where(Tenant.tenant_name == audience)

        return (await self.session.exec(statement)).first()

    async def get_tenant_by_name(self, tenant_name: str) -> Tenant | None:
        """
        Retrieve a tenant by its name
        """

        statement = select(Tenant).where(Tenant.tenant_name == tenant_name)
        return (await self.session.exec(statement)).first()

    async def get_realm_details_by_tenant_name(self, tenant_name: str) -> RealmDetails:
        """
        Retrieve the realm details for a tenant
        """
        tenant = await self.get_tenant_by_name(tenant_name)

        if tenant is None:
            raise ResourceReferenceException(
                f"Tenant with name {tenant_name} not found"
            )

        client_id = GRAPHQL_CLIENT_ID_TEMPLATE.format(tenant.tenant_name)

        realm_details = RealmDetails(
            realm_name=tenant.auth_realm_name, client_id=client_id
        )
        return realm_details

    async def find_tenants_by_partial_name(self, partial_name: str) -> list[Tenant]:
        """
        Retrieve any tenants containing the string parameter in their names
        """

        statement = select(Tenant).where(col(Tenant.tenant_name).contains(partial_name))
        return (await self.session.exec(statement)).all()

    async def get_tenants_by_name(self, tenant_names: list[str]) -> dict[str, Tenant]:
        if not tenant_names:
            return {}

        statement = select(Tenant).where(col(Tenant.tenant_name).in_(tenant_names))
        return {
            tenant.tenant_name: tenant
            for tenant in (await self.session.exec(statement)).all()
        }

    async def get_tenants_by_id(self, tenant_ids: list[UUID]) -> dict[UUID, Tenant]:
        if not tenant_ids:
            return {}

        statement = select(Tenant).where(col(Tenant.id).in_(tenant_ids))
        return {
            tenant.id: tenant for tenant in (await self.session.exec(statement)).all()
        }

    async def get_tenants(self) -> list[Tenant]:
        """
        Retrieve all the tenants in the system
        """

        statement = select(Tenant)
        return (await self.session.exec(statement)).all()

    async def create(self, tenant: TenantCreate) -> Tenant:
        exists = await self.get_tenant_by_name(tenant.tenant_name)
        if exists:
            return exists

        db_tenant = Tenant.from_orm(tenant)
        self.session.add(db_tenant)
        await self.session.commit()
        logger.info(
            "Tenant created",
            tenant_id=str(db_tenant.id),
            tenant_name=db_tenant.tenant_name,
        )
        return db_tenant

    async def edit(self, tenant_edit: TenantEdit) -> Tenant:
        exists = await self.get_tenant_by_name(tenant_edit.tenant_name)
        if not exists:
            raise ResourceReferenceException(
                f"tenant {tenant_edit.tenant_name} does not exist"
            )
        change_flag = False

        if exists.auth_realm_name != tenant_edit.auth_realm_name:
            exists.auth_realm_name = tenant_edit.auth_realm_name
            change_flag = True

        if change_flag:
            self.session.add(exists)
            await self.session.commit()
            logger.info(
                "tenant updated",
                tenant_id=str(exists.id),
                tenant_name=exists.tenant_name,
                tenant_auth_name=exists.auth_realm_name,
            )

        return exists

    async def set_ingestion_settings(
        self, tenant_id: UUID, bucket_name: str, folder_name: str
    ) -> None:
        settings_statement = select(IngestionSettings).where(
            IngestionSettings.tenant_id == str(tenant_id)
        )
        tenant_settings = (await self.session.exec(settings_statement)).first()

        if tenant_settings:
            tenant_settings.bucket_name = bucket_name
            tenant_settings.folder_name = folder_name
        else:
            tenant_settings = IngestionSettings(
                tenant_id=tenant_id, bucket_name=bucket_name, folder_name=folder_name
            )
            self.session.add(tenant_settings)
        await self.session.commit()

    async def get_ingestion_settings(self, tenant_id: UUID) -> IngestionSettings | None:
        settings_statement = select(IngestionSettings).where(
            IngestionSettings.tenant_id == tenant_id
        )
        return (await self.session.exec(settings_statement)).first()

    async def get_parsed_file_paths(self, tenant_id: UUID) -> list[str]:
        statement = (
            select(ParsedFile.file_path)
            .select_from(ParsedFile)
            .where(ParsedFile.tenant_id == tenant_id)
        )
        return (await self.session.exec(statement)).all()
