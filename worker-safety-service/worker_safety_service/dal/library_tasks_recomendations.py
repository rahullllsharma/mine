import re
from typing import Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import col, select

from worker_safety_service import get_logger
from worker_safety_service.dal.base_relationship_manager import BaseRelationshipManager
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.models.library import (
    LibraryControl,
    LibraryHazard,
    LibraryTask,
    LibraryTaskRecommendations,
)

logger = get_logger(__name__)

MISSING_ENTITY_ERROR_MSG_PATTERN = r"violates foreign key constraint \"(\S+)\""


class LibraryTaskHazardRecommendationsManager(
    BaseRelationshipManager[LibraryTaskRecommendations]
):
    # what a hell of a name

    async def create(self, entity: LibraryTaskRecommendations) -> None:
        """
        Adds a new LibraryTask Recommendation. Adding a recommendation that already exists should not yield an error.
        """
        # TODO: Reconcile with the CRUD Manager Impl
        try:
            await super().create(entity)
        except IntegrityError as ex:
            match = re.search(MISSING_ENTITY_ERROR_MSG_PATTERN, str(ex))
            if match:
                constraint_name = match.group(1)
                if (
                    constraint_name
                    == "library_task_recommendations_library_task_id_fkey"
                ):
                    raise EntityNotFoundException(entity.library_task_id, LibraryTask)
                elif (
                    constraint_name
                    == "library_task_recommendations_library_hazard_id_fkey"
                ):
                    raise EntityNotFoundException(
                        entity.library_hazard_id, LibraryHazard
                    )
                else:
                    raise EntityNotFoundException(
                        entity.library_control_id, LibraryControl
                    )
            else:
                raise ex

    async def delete(self, entity: LibraryTaskRecommendations) -> None:
        stm = (
            delete(LibraryTaskRecommendations)
            .where(LibraryTaskRecommendations.library_task_id == entity.library_task_id)
            .where(
                LibraryTaskRecommendations.library_hazard_id == entity.library_hazard_id
            )
            .where(
                LibraryTaskRecommendations.library_control_id
                == entity.library_control_id
            )
        )

        async with self.session.begin_nested():
            await self.session.execute(stm)

    async def get_library_task_recommendations(
        self,
        library_task_ids: Optional[list[UUID]] = None,
        library_hazard_ids: Optional[list[UUID]] = None,
        library_control_ids: Optional[list[UUID]] = None,
        use_seek_pagination: bool = False,
        after: Optional[UUID] = None,
        limit: Optional[int] = None,
    ) -> list[LibraryTaskRecommendations]:
        statement = select(LibraryTaskRecommendations)

        if library_task_ids:
            statement = statement.where(
                col(LibraryTaskRecommendations.library_task_id).in_(library_task_ids)
            )

        if library_hazard_ids:
            statement = statement.where(
                col(LibraryTaskRecommendations.library_hazard_id).in_(
                    library_hazard_ids
                )
            )

        if library_control_ids:
            statement = statement.where(
                col(LibraryTaskRecommendations.library_control_id).in_(
                    library_control_ids
                )
            )

        if use_seek_pagination:
            if after is not None:
                statement = statement.where(
                    LibraryTaskRecommendations.library_task_id > after
                )
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(LibraryTaskRecommendations.library_task_id)

        return (await self.session.exec(statement)).all()
