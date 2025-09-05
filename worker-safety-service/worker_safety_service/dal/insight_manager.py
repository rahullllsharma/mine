from datetime import datetime, timezone
from logging import getLogger
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm.attributes import set_attribute
from sqlmodel import desc, select

from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.models import (
    AsyncSession,
    CreateInsightInput,
    Insight,
    UpdateInsightInput,
)

logger = getLogger(__name__)


class InsightManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(
        self,
        tenant_id: UUID,
        limit: Optional[int] = None,
        after: Optional[UUID] = None,
        additional_where_clause: Optional[list[Any]] = None,
    ) -> list[Insight]:
        query = select(Insight).where(
            Insight.tenant_id == tenant_id, Insight.ordinal != -1
        )
        if additional_where_clause:
            for clause in additional_where_clause:
                query = query.where(clause)
        if after is not None:
            after_insight = await self.get(after)
            query = query.where(Insight.ordinal > after_insight.ordinal)
        if limit:
            query = query.limit(limit)

        insights = await self.session.exec(query.order_by(desc(Insight.ordinal)))

        return insights.all()

    async def get(self, id: UUID) -> Insight:
        insight = await self.session.get(Insight, id)

        if not insight:
            raise ResourceReferenceException(
                f"Could not find requested insight with id {id}"
            )

        return insight

    async def create(self, input: CreateInsightInput, tenant_id: UUID) -> Insight:
        # get all insights from db
        all_insights = await self.get_all(tenant_id)
        self.check_for_duplicate_name(all_insights, input.name)

        # create the new insight
        insight_instance = Insight(**input.dict(), tenant_id=tenant_id)

        # update priority
        insight_instance.ordinal = len(all_insights) + 1

        return await self.add_and_commit(insight_instance)

    async def update(
        self, id: UUID, input: UpdateInsightInput, tenant_id: UUID
    ) -> Insight:
        insight_instance = await self.get(id)
        if input.name:
            all_insights = await self.get_all(tenant_id)
            self.check_for_duplicate_name(all_insights, input.name)

        data_dict = input.dict(exclude_none=True, exclude_unset=True)
        for column_name, updated_value in data_dict.items():
            set_attribute(insight_instance, column_name, updated_value)

        return await self.add_and_commit(insight_instance)

    async def archive(self, id: UUID, tenant_id: UUID) -> bool:
        insight_to_be_archived = await self.get(id)

        insights_after_archived_insight = await self.get_all(
            tenant_id,
            additional_where_clause=[Insight.ordinal > insight_to_be_archived.ordinal],
        )

        for insight in insights_after_archived_insight:
            logger.info(f"{insight.name} -> curr ordinal{insight.ordinal}")
            insight.ordinal -= 1

        insight_to_be_archived.archived_at = datetime.now(timezone.utc)
        insight_to_be_archived.ordinal = -1
        self.session.add_all(insights_after_archived_insight + [insight_to_be_archived])
        await self.session.commit()

        return True

    async def reorder(
        self, ordered_ids: list[UUID], tenant_id: UUID, limit: Optional[int] = None
    ) -> list[Insight]:
        all_insights = await self.get_all(tenant_id)
        if len(ordered_ids) < len(all_insights):
            raise RuntimeError(
                "Few insights missing. Please send all the insight ids in order"
            )
        if len(ordered_ids) > len(all_insights):
            raise RuntimeError("Extra insights provided. Please resend")
        insights_dict = {insight.id: insight for insight in all_insights}

        reordered_insights = []
        for count, id in enumerate(ordered_ids[::-1], start=1):
            insight = insights_dict.get(id)
            assert insight
            insight.ordinal = count
            reordered_insights.append(insight)

        self.session.add_all(reordered_insights)
        await self.session.commit()

        return await self.get_all(tenant_id, limit=limit)

    # helper methods
    def check_for_duplicate_name(
        self, all_insights: list[Insight], new_name: str
    ) -> None:
        names = [i.name.lower() for i in all_insights]
        if new_name.lower() in names:
            raise DuplicateKeyException(
                "Insight with same name already exists. Please give a unique name"
            )

    async def add_and_commit(self, insight: Insight) -> Insight:
        try:
            self.session.add(insight)
            await self.session.commit()
            await self.session.refresh(insight)
            return insight
        except Exception as e:
            await self.session.rollback()
            logger.exception("Some error occurred while committing to insights")
            raise e
