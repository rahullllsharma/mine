from typing import Collection, Optional
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    LibrarySiteCondition,
    OrderBy,
    TenantLibrarySiteConditionSettings,
    WorkTypeLibrarySiteConditionLink,
    set_order_by,
)

logger = get_logger(__name__)


class LibrarySiteConditionManager(CRUAManager[LibrarySiteCondition]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session, entity_type=LibrarySiteCondition, immutable_fields=["id"]
        )

    async def get_library_site_condition(self, id: UUID) -> LibrarySiteCondition | None:
        statement = (
            select(LibrarySiteCondition)
            .where(LibrarySiteCondition.id == id)
            .where(col(LibrarySiteCondition.archived_at).is_(None))
        )

        return (await self.session.exec(statement)).first()

    async def get_library_site_conditions(
        self,
        after: Optional[UUID] = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        ids: Optional[list[UUID]] = None,
        allow_archived: bool = False,
        handle_codes: Collection[str] | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: UUID | None = None,
        filter_tenant_settings: bool | None = False,
    ) -> list[LibrarySiteCondition]:
        statement = select(LibrarySiteCondition)

        if not allow_archived:
            statement = statement.where(col(LibrarySiteCondition.archived_at).is_(None))

        if ids:
            statement = statement.where(col(LibrarySiteCondition.id).in_(ids))

        if handle_codes:
            statement = statement.where(
                col(LibrarySiteCondition.handle_code).in_(handle_codes)
            )

        if tenant_id and filter_tenant_settings:
            statement = statement.join(
                TenantLibrarySiteConditionSettings,
                onclause=TenantLibrarySiteConditionSettings.library_site_condition_id
                == LibrarySiteCondition.id,
            ).where(TenantLibrarySiteConditionSettings.tenant_id == tenant_id)

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibrarySiteCondition.id > after)
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(LibrarySiteCondition.id)

        statement = set_order_by(LibrarySiteCondition, statement, order_by=order_by)
        result = await self.session.exec(statement)
        return list(result.all())

    async def get_tenant_and_work_type_linked_library_site_conditions(
        self,
        tenant_id: UUID,
        tenant_work_type_ids: list[UUID],
        ids: list[UUID] | None = None,
        allow_archived: bool = False,
        after: UUID | None = None,
        limit: int | None = None,
        order_by: list[OrderBy] | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[LibrarySiteCondition]:
        """
        Retrieve library site_conditions related to a tenant
        and optionally linked to a specific project type.
        """
        if not tenant_work_type_ids:
            return []

        statement = (
            select(LibrarySiteCondition)
            .join(
                TenantLibrarySiteConditionSettings,
                onclause=TenantLibrarySiteConditionSettings.library_site_condition_id
                == LibrarySiteCondition.id,
            )
            .where(TenantLibrarySiteConditionSettings.tenant_id == tenant_id)
            .join(
                WorkTypeLibrarySiteConditionLink,
                onclause=WorkTypeLibrarySiteConditionLink.library_site_condition_id
                == LibrarySiteCondition.id,
            )
            .where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    tenant_work_type_ids
                )
            )
        )

        if not allow_archived:
            statement = statement.where(col(LibrarySiteCondition.archived_at).is_(None))

        if ids:
            statement = statement.where(col(LibrarySiteCondition.id).in_(ids))

        if order_by:
            statement = set_order_by(LibrarySiteCondition, statement, order_by=order_by)
        else:
            statement = statement.order_by(LibrarySiteCondition.id)

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibrarySiteCondition.id > after)
            if limit is not None:
                statement = statement.limit(limit)

        # To remove duplicate scs(if any)
        statement = statement.group_by(LibrarySiteCondition)

        result = await self.session.exec(statement)
        scs = list(result.all())
        logger.debug(f"total scs fetched --> {len(scs)}")
        return scs

    async def add_library_site_condition(
        self, library_site_condition: LibrarySiteCondition
    ) -> Optional[LibrarySiteCondition]:
        await self.create(library_site_condition)

        return await self.get_by_id(library_site_condition.id)

    async def edit_library_site_condition(
        self, id: UUID, library_site_condition: LibrarySiteCondition
    ) -> Optional[LibrarySiteCondition]:
        await super().update(library_site_condition)

        return await self.get_by_id(library_site_condition.id)

    async def archive_library_site_condition(self, id: UUID) -> None:
        await super().archive(id)

    async def unarchive_library_site_condition(self, id: UUID) -> None:
        await super().unarchive(id)
