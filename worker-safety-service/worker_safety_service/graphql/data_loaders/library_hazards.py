import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service import get_logger
from worker_safety_service.dal.library_hazards import LibraryHazardManager
from worker_safety_service.models import LibraryHazard

logger = get_logger(__name__)


class LibraryHazardsLoader:
    """Loader for orchestrating library hazard actions"""

    def __init__(self, manager: LibraryHazardManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_hazards)

    async def get_by_id(self, library_hazard_id: uuid.UUID) -> LibraryHazard | None:
        """Get library hazard by id"""
        return await self.__manager.get_by_id(entity_id=library_hazard_id)

    async def load_hazards(
        self, library_hazard_ids: list[uuid.UUID]
    ) -> list[LibraryHazard | None]:
        items = await self.__manager.get_library_hazards_by_id(
            ids=library_hazard_ids, allow_archived=True
        )
        return [items.get(i) for i in library_hazard_ids]
