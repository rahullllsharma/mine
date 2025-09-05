from typing import Optional
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    LibraryHazard,
    LibrarySiteConditionRecommendations,
    LibraryTaskRecommendations,
)

logger = get_logger(__name__)


class LibraryHazardManager(CRUAManager[LibraryHazard]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=LibraryHazard, immutable_fields=["id"])

    async def get_library_hazard(self, id: UUID) -> LibraryHazard | None:
        statement = (
            select(LibraryHazard)
            .where(LibraryHazard.id == id)
            .where(col(LibraryHazard.archived_at).is_(None))
        )

        return (await self.session.exec(statement)).first()

    async def get_library_hazards_by_id(
        self,
        ids: list[UUID],
        allow_archived: bool = False,
    ) -> dict[UUID, LibraryHazard]:
        return {
            i.id: i
            for i in await self.get_library_hazards(
                ids=ids, allow_archived=allow_archived
            )
        }

    async def get_library_hazards(
        self,
        after: Optional[UUID] = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        ids: Optional[list[UUID]] = None,
        library_site_condition_ids: Optional[list[UUID]] = None,
        library_task_ids: Optional[list[UUID]] = None,
        allow_archived: bool = False,
    ) -> list[LibraryHazard]:
        statement = select(LibraryHazard)

        if not allow_archived:
            statement = statement.where(col(LibraryHazard.archived_at).is_(None))

        if ids:
            statement = statement.where(col(LibraryHazard.id).in_(ids))

        if library_site_condition_ids is not None:
            statement = statement.join(
                LibrarySiteConditionRecommendations, isouter=True
            ).where(
                col(LibrarySiteConditionRecommendations.library_site_condition_id).in_(
                    library_site_condition_ids
                )
            )

        if library_task_ids is not None:
            statement = statement.join(LibraryTaskRecommendations, isouter=True).where(
                col(LibraryTaskRecommendations.library_task_id).in_(library_task_ids)
            )

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibraryHazard.id > after)
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(LibraryHazard.id)

        return (await self.session.exec(statement)).all()

    async def add_library_hazard(
        self, library_hazard: LibraryHazard
    ) -> Optional[LibraryHazard]:
        if not library_hazard.image_url:
            library_hazard.image_url = "https://storage.googleapis.com/worker-safety-public-icons/DefaultHazardIcon.svg"
        if not library_hazard.image_url_png:
            library_hazard.image_url_png = "https://storage.googleapis.com/worker-safety-public-icons/png-icons/DefaultHazardIcon.png"
        await self.create(library_hazard)

        return await self.get_by_id(library_hazard.id)

    async def update_library_hazard(
        self, id: UUID, library_hazard: LibraryHazard
    ) -> Optional[LibraryHazard]:
        await self.update(library_hazard)

        return await self.get_by_id(library_hazard.id)

    async def archive_library_hazard(self, id: UUID) -> None:
        await self.archive(id)

    async def unarchive_library_hazard(self, id: UUID) -> None:
        await self.unarchive(id)
