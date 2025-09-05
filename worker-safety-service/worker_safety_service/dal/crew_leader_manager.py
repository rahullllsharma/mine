from datetime import datetime, timezone
from logging import getLogger
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm.attributes import set_attribute
from sqlmodel import col, select

from worker_safety_service.exceptions import (
    DuplicateKeyException,
    ResourceReferenceException,
)
from worker_safety_service.models import (
    AsyncSession,
    CreateCrewLeaderInput,
    CrewLeader,
    UpdateCrewLeaderInput,
)

logger = getLogger(__name__)


class CrewLeaderManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_all(
        self,
        tenant_id: UUID,
        limit: Optional[int] = None,
        offset: int | None = None,
        additional_where_clause: Optional[list[Any]] = None,
    ) -> list[CrewLeader]:
        query = select(CrewLeader).where(
            CrewLeader.tenant_id == tenant_id, col(CrewLeader.archived_at).is_(None)
        )
        if additional_where_clause:
            for clause in additional_where_clause:
                query = query.where(clause)

        if limit:
            query = query.limit(max(1, limit)).offset(max(0, offset or 0))

        crew_leaders = await self.session.exec(query.order_by(CrewLeader.name))

        return crew_leaders.all()

    async def get(self, id: UUID) -> Optional[CrewLeader]:
        query = select(CrewLeader).where(
            CrewLeader.id == id, col(CrewLeader.archived_at).is_(None)
        )
        crew_leader = (await self.session.exec(query)).first()

        if not crew_leader:
            raise ResourceReferenceException(
                f"Could not find requested crew leader with id {id}"
            )

        return crew_leader

    async def create(self, input: CreateCrewLeaderInput, tenant_id: UUID) -> CrewLeader:
        all_crew_leaders = await self.get_all(tenant_id)

        self.check_for_duplicate(input.name, all_crew_leaders)

        instance = CrewLeader(**input.dict(), tenant_id=tenant_id)

        return await self.add_and_commit(instance)

    async def update(
        self, id: UUID, input: UpdateCrewLeaderInput, tenant_id: UUID
    ) -> CrewLeader:
        instance = await self.get(id)
        self.check_crew_leader_exists(instance)
        assert instance

        if input.name:
            all_crew_leaders = await self.get_all(tenant_id)
            self.check_for_duplicate(input.name, all_crew_leaders)

        data_dict = input.dict(exclude_none=True, exclude_unset=True)
        for column_name, updated_value in data_dict.items():
            set_attribute(instance, column_name, updated_value)

        return await self.add_and_commit(instance)

    async def archive(self, id: UUID, tenant_id: UUID) -> bool:
        crew_leader_to_be_archived = await self.get(id)
        if (
            not crew_leader_to_be_archived
            or crew_leader_to_be_archived.tenant_id != tenant_id
        ):
            raise ResourceReferenceException(
                f"Could not find requested crew leader with id {id} for tenant {tenant_id}"
            )
        self.check_crew_leader_exists(crew_leader_to_be_archived)
        assert crew_leader_to_be_archived

        crew_leader_to_be_archived.archived_at = datetime.now(timezone.utc)
        _ = await self.add_and_commit(crew_leader_to_be_archived)

        return True

    # helper methods
    async def add_and_commit(self, crew_leader: CrewLeader) -> CrewLeader:
        self.session.add(crew_leader)
        await self.session.commit()
        await self.session.refresh(crew_leader)
        return crew_leader

    def check_for_duplicate(
        self, name: str, all_crew_leaders: list[CrewLeader]
    ) -> None:
        all_names = [crew_leader.name for crew_leader in all_crew_leaders]
        if name in all_names:
            raise DuplicateKeyException(
                f"Crew Leader with name '{name}' already exists. Please select a unique name"
            )

    def check_crew_leader_exists(self, crew_leader: Optional[CrewLeader]) -> None:
        if not crew_leader:
            raise ResourceReferenceException("Could not find requested crew leader.")
        else:
            return

    async def check_crew_leader_exists_by_name(
        self, tenant_id: UUID, names: list[str]
    ) -> list[str]:
        existing_names = await self.session.exec(
            select(CrewLeader.name)
            .where(CrewLeader.tenant_id == tenant_id)
            .where(col(CrewLeader.name).in_(names))
        )
        return existing_names.all()
