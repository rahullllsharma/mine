from typing import Optional
from uuid import UUID

from sqlmodel import col, delete, select

from worker_safety_service import get_logger
from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    LibrarySiteConditionRecommendations,
)

logger = get_logger(__name__)


class LibrarySiteConditionRecommendationManager(
    CRUAManager[LibrarySiteConditionRecommendations]
):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_library_site_conditions_recommendations(
        self,
        after: Optional[UUID] = None,
        limit: int | None = None,
        use_seek_pagination: bool | None = False,
        library_site_condition_ids: Optional[list[UUID]] = None,
        library_hazard_ids: Optional[list[UUID]] = None,
        library_control_ids: Optional[list[UUID]] = None,
    ) -> list[LibrarySiteConditionRecommendations]:
        statement = select(LibrarySiteConditionRecommendations)

        if library_site_condition_ids:
            statement = statement.where(
                col(LibrarySiteConditionRecommendations.library_site_condition_id).in_(
                    library_site_condition_ids
                )
            )

        if library_hazard_ids:
            statement = statement.where(
                col(LibrarySiteConditionRecommendations.library_hazard_id).in_(
                    library_hazard_ids
                )
            )

        if library_control_ids:
            statement = statement.where(
                col(LibrarySiteConditionRecommendations.library_control_id).in_(
                    library_control_ids
                )
            )
        if use_seek_pagination:
            if after is not None:
                statement = statement.where(
                    LibrarySiteConditionRecommendations.library_site_condition_id
                    > after
                )
            if limit is not None:
                statement = statement.limit(limit)
            statement = statement.order_by(
                LibrarySiteConditionRecommendations.library_site_condition_id
            )

        return (await self.session.exec(statement)).all()

    async def get_library_site_condition_recommendation(
        self,
        library_site_condition_id: UUID,
    ) -> LibrarySiteConditionRecommendations | None:
        recommendation = await self.session.get(
            LibrarySiteConditionRecommendations, library_site_condition_id
        )

        return recommendation

    async def add_library_site_condition_recommendation(
        self,
        library_site_condition_recommendation: LibrarySiteConditionRecommendations,
    ) -> None:
        self.session.add(library_site_condition_recommendation)
        await self.session.commit()

    async def delete_library_site_condition_recommendation(
        self,
        library_site_condition_recommendation: LibrarySiteConditionRecommendations,
    ) -> None:
        stm = (
            delete(LibrarySiteConditionRecommendations)
            .where(
                LibrarySiteConditionRecommendations.library_site_condition_id
                == library_site_condition_recommendation.library_site_condition_id
            )
            .where(
                LibrarySiteConditionRecommendations.library_hazard_id
                == library_site_condition_recommendation.library_hazard_id
            )
            .where(
                LibrarySiteConditionRecommendations.library_control_id
                == library_site_condition_recommendation.library_control_id
            )
        )

        async with self.session.begin_nested():
            await self.session.execute(stm)
