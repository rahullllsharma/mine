from typing import Optional
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    LibraryControl,
    LibrarySiteConditionRecommendations,
    LibraryTaskRecommendations,
)

logger = get_logger(__name__)


class LibraryControlManager(CRUAManager[LibraryControl]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=LibraryControl)

    async def get_library_controls(
        self,
        after: Optional[UUID] = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        ids: Optional[list[UUID]] = None,
        library_hazard_ids: Optional[list[UUID]] = None,
        library_site_condition_ids: Optional[list[UUID]] = None,
        library_task_ids: Optional[list[UUID]] = None,
        allow_archived: bool = False,
    ) -> list[LibraryControl]:
        statement = select(LibraryControl)

        if ids:
            statement = statement.where(col(LibraryControl.id).in_(ids))

        if library_hazard_ids is not None or library_task_ids is not None:
            statement = statement.join(LibraryTaskRecommendations, isouter=True)

        if library_hazard_ids is not None or library_site_condition_ids is not None:
            statement = statement.join(
                LibrarySiteConditionRecommendations, isouter=True
            )

        if library_task_ids is not None:
            statement = statement.where(
                col(LibraryTaskRecommendations.library_task_id).in_(library_task_ids)
            )

        if library_site_condition_ids is not None:
            statement = statement.where(
                col(LibrarySiteConditionRecommendations.library_site_condition_id).in_(
                    library_site_condition_ids
                )
            )

        if library_hazard_ids is not None:
            statement = statement.where(
                col(LibraryTaskRecommendations.library_hazard_id).in_(
                    library_hazard_ids
                )
            )

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(LibraryControl.id > after)
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(LibraryControl.id)

        if not allow_archived:
            statement = statement.where(col(LibraryControl.archived_at).is_(None))

        return (await self.session.exec(statement)).all()

    async def get_library_controls_by_id(
        self,
        ids: list[UUID],
        allow_archived: bool = False,
    ) -> dict[UUID, LibraryControl]:
        return {
            i.id: i
            for i in await self.get_library_controls(
                ids=ids, allow_archived=allow_archived
            )
        }
