from typing import Optional
from uuid import UUID

from strawberry.dataloader import DataLoader

from worker_safety_service import get_logger
from worker_safety_service.dal.library_site_conditions import (
    LibrarySiteConditionManager,
)
from worker_safety_service.models import LibrarySiteCondition, OrderBy

logger = get_logger(__name__)


class LibrarySiteConditionsLoader:
    """Loader for orchestrating library site condition actions"""

    def __init__(
        self,
        manager: LibrarySiteConditionManager,
        tenant_id: UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_library_site_conditions)
        self.load_library_site_conditions_tenant = DataLoader(
            load_fn=self.library_site_condition_by_tenant_settings
        )

    async def library_site_condition_by_tenant_settings(
        self, keys: list[tuple[UUID, bool]]
    ) -> list[LibrarySiteCondition | None]:
        """Load library site conditions by tenant settings."""
        library_site_condition_ids = []
        filter_tenant_settings = None

        for key in keys:
            id, filter_tenant_settings = key
            library_site_condition_ids.append(id)

        library_site_conditions = await self.__manager.get_library_site_conditions(
            ids=library_site_condition_ids,
            allow_archived=True,
            tenant_id=self.tenant_id,
            filter_tenant_settings=filter_tenant_settings,
        )

        # Create a mapping from ID to LibrarySiteCondition
        items = {item.id: item for item in library_site_conditions}

        # Return individual items for each key, maintaining order
        return [items.get(key[0]) for key in keys]

    async def load_library_site_conditions(
        self, ids: list[UUID], filter_tenant_settings: bool | None = False
    ) -> list[LibrarySiteCondition | None]:
        items = {
            i.id: i
            for i in await self.__manager.get_library_site_conditions(
                ids=ids,
                allow_archived=True,
                tenant_id=self.tenant_id,
                filter_tenant_settings=filter_tenant_settings,
            )
        }
        return [items.get(i) for i in ids]

    async def get_library_site_conditions(
        self,
        ids: Optional[list[UUID]] = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = True,
    ) -> list[LibrarySiteCondition]:
        return await self.__manager.get_library_site_conditions(
            ids=ids, order_by=order_by, allow_archived=allow_archived
        )

    async def get_tenant_and_work_type_linked_library_site_conditions(
        self,
        tenant_work_type_ids: list[UUID],
        ids: list[UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[LibrarySiteCondition]:
        return await self.__manager.get_tenant_and_work_type_linked_library_site_conditions(
            order_by=order_by,
            tenant_id=self.tenant_id,
            tenant_work_type_ids=tenant_work_type_ids,
            ids=ids,
        )
