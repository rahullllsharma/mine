import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service import get_logger
from worker_safety_service.dal.library_controls import LibraryControlManager
from worker_safety_service.models import LibraryControl

logger = get_logger(__name__)


class LibraryControlsLoader:
    """Loader for orchestrating library control actions"""

    def __init__(self, manager: LibraryControlManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.me = DataLoader(load_fn=self.load_controls)

    async def get_by_id(self, library_control_id: uuid.UUID) -> LibraryControl | None:
        """Get library control by id"""
        return await self.__manager.get_by_id(entity_id=library_control_id)

    async def load_controls(
        self, library_control_ids: list[uuid.UUID]
    ) -> list[LibraryControl | None]:
        items = await self.__manager.get_library_controls_by_id(
            ids=library_control_ids, allow_archived=True
        )
        return [items.get(i) for i in library_control_ids]
