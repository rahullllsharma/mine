from uuid import UUID

from sqlmodel import col, select

from worker_safety_service.models import AsyncSession, Crew


class CrewManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_crew(
        self,
        *,
        ids: list[UUID] | None = None,
        tenant_id: UUID | None = None,
    ) -> list[Crew]:
        if ids is not None and not ids:
            return []

        statement = select(Crew)
        if tenant_id:
            statement = statement.where(Crew.tenant_id == tenant_id)
        if ids:
            statement = statement.where(col(Crew.id).in_(ids))

        return (await self.session.exec(statement)).all()

    async def get_crew_by_id(
        self,
        *,
        ids: list[UUID] | None = None,
        tenant_id: UUID | None = None,
    ) -> dict[UUID, Crew]:
        return {i.id: i for i in await self.get_crew(ids=ids, tenant_id=tenant_id)}
