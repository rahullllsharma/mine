from typing import Optional
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import AsyncSession, LibraryActivityGroup

logger = get_logger(__name__)


class LibraryActivityGroupManager(CRUAManager[LibraryActivityGroup]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=LibraryActivityGroup)

    async def get_library_activity_groups(
        self,
        ids: Optional[list[UUID]],
        after: UUID | None = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
    ) -> list[LibraryActivityGroup]:
        statement = select(LibraryActivityGroup)

        if ids:
            statement = statement.where(col(LibraryActivityGroup.id).in_(ids))

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibraryActivityGroup.id > after)
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(LibraryActivityGroup.id)

        return (await self.session.exec(statement)).all()
