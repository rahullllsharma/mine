from collections import defaultdict
from typing import Any, Optional
from uuid import UUID

from sqlmodel import select

from worker_safety_service.models import AsyncSession, Observation

SEVERITY_OUTCOME_INCIDENT_TYPE_MAP = defaultdict(
    lambda: "not_applicable",
    {
        "Other non-occupational": "near_miss",
        "First Aid Only": "first_aid",
        "Report Purposes Only": "recordable",
        "Restriction or job transfer": "restricted",
        "Lost Time": "lost_time",
        "Near deaths": "p_sif",  # (not in data)
        "Deaths": "sif",  # (not in data)
    },
)


class ObservationsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_observation_by_id(
        self, observation_id: UUID, tenant_id: UUID | None = None
    ) -> Observation | None:
        get_observation_statement = select(Observation).where(
            Observation.observation_id == observation_id
        )
        if tenant_id:
            get_observation_statement = get_observation_statement.where(
                Observation.tenant_id == tenant_id
            )
        return (await self.session.exec(get_observation_statement)).first()

    async def create_observation(self, kwargs: dict[str, Optional[Any]]) -> Observation:
        observation = Observation(**kwargs)
        self.session.add(observation)
        await self.session.commit()
        return observation
