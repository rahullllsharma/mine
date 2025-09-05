import uuid
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, NamedTuple, Optional
from uuid import UUID

import pendulum
from sqlmodel import col, func, select
from sqlmodel.sql.expression import SelectOfScalar

from worker_safety_service.models import (
    AsyncSession,
    Contractor,
    ContractorAlias,
    Incident,
    Observation,
    set_order_by,
)
from worker_safety_service.types import OrderBy


def count_incident_type_occurences(incidents: list[Incident]) -> Counter:
    occurrence_count: Counter[str] = Counter()
    for incident in incidents:
        severity = incident.severity
        if severity is None:
            continue
        occurrence_count[severity] += 1

    return occurrence_count


class ContractorHistory(NamedTuple):
    n_safety_observations: int
    n_action_items: int


@dataclass
class CSHIncident:
    # person_impacted_severity_outcome
    near_miss: int = field(
        default=0, metadata={"full_name": "Near Miss"}
    )  # Other non-occupational
    first_aid: int = field(
        default=0, metadata={"full_name": "First-Aid"}
    )  # First-aid only
    recordable: int = field(
        default=0, metadata={"full_name": "Recordable"}
    )  # Report Purposes Only
    restricted: int = field(
        default=0, metadata={"full_name": "Restricted"}
    )  # Restriction or job transfer
    lost_time: int = field(default=0, metadata={"full_name": "Lost Time"})  # Lost Time
    p_sif: int = field(
        default=0, metadata={"full_name": "P-SIF"}
    )  # <unknown for the time being>
    sif: int = field(
        default=0, metadata={"full_name": "SIF"}
    )  # <unknown for the time being>
    sum_of_project_cost: float = field(
        default=100, metadata={"full_name": "Sum of Project Cost"}
    )  # default to 100 for the time being


def selectWithOptionalTenant(
    tenant_id: Optional[uuid.UUID] = None,
) -> SelectOfScalar[Contractor]:
    if tenant_id:
        return select(Contractor).where(Contractor.tenant_id == tenant_id)
    return select(Contractor)


class ContractorsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_contractor(
        self, contractor_id: UUID, tenant_id: Optional[uuid.UUID] = None
    ) -> Contractor | None:
        statement = selectWithOptionalTenant(tenant_id).where(
            Contractor.id == contractor_id
        )
        return (await self.session.exec(statement)).first()

    async def get_contractors(
        self,
        *,
        ids: Iterable[uuid.UUID] | None = None,
        tenant_id: UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[Contractor]:
        if ids is not None and not ids:
            return []

        statement = selectWithOptionalTenant(tenant_id)
        if ids:
            statement = statement.where(col(Contractor.id).in_(ids))

        statement = set_order_by(Contractor, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def get_contractors_by_id(
        self,
        *,
        ids: Iterable[uuid.UUID] | None = None,
        tenant_id: UUID | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> dict[uuid.UUID, Contractor]:
        return {
            i.id: i
            for i in await self.get_contractors(
                ids=ids, tenant_id=tenant_id, order_by=order_by
            )
        }

    async def get_contractor_history(
        self, contractor_id: UUID, history_limit_years: float = 5
    ) -> ContractorHistory:
        max_date = pendulum.today(tz="UTC")
        min_date = max_date.subtract(years=history_limit_years)  # type: ignore

        statement = (
            select(func.count())  # type: ignore
            .select_from(Observation)
            .where(Observation.contractor_involved_id == contractor_id)
            .where(max_date.replace(tzinfo=None) >= Observation.observation_datetime)  # type: ignore
            .where(Observation.observation_datetime >= min_date.replace(tzinfo=None))  # type: ignore
        )
        n_safety_observations = (await self.session.exec(statement)).one()

        # NOTE: the definition of n_action_items is VERY open, and action_id!=None might not be correct
        statement = statement.where(Observation.action_id != None)  # noqa: E711
        n_action_items = (await self.session.exec(statement)).one()

        return ContractorHistory(
            n_safety_observations=n_safety_observations, n_action_items=n_action_items
        )

    async def get_contractors_history(
        self, tenant_id: UUID, history_limit_years: float = 5
    ) -> list[ContractorHistory]:
        return [
            await self.get_contractor_history(contractor.id, history_limit_years)
            for contractor in await self.get_contractors(tenant_id=tenant_id)
        ]

    async def get_contractor_experience_years(self, contractor_id: UUID) -> float:
        statement = (
            select(Observation)
            .where(Observation.contractor_involved_id == contractor_id)
            .order_by(Observation.observation_datetime.asc())  # type: ignore
        )
        oldest = (await self.session.exec(statement)).first()
        if not oldest or not oldest.observation_datetime:
            raise ValueError(
                f"Missing oldest observation for contractor {contractor_id}"
            )

        first_date = pendulum.instance(oldest.observation_datetime)
        months: float = pendulum.today().diff(first_date).months
        return months / 12

    async def get_csh_incident_data(self, contractor_id: UUID) -> CSHIncident:
        today = pendulum.today()
        statement = select(Incident).where(
            Incident.contractor_id == contractor_id,
            Incident.timestamp_created >= today.subtract(years=5),  # type: ignore
        )
        incidents = (await self.session.exec(statement)).all()

        occurrence_count = count_incident_type_occurences(incidents=incidents)
        return CSHIncident(
            near_miss=occurrence_count["near_miss"],
            first_aid=occurrence_count["first_aid"],
            recordable=occurrence_count["recordable"],
            restricted=occurrence_count["restricted"],
            lost_time=occurrence_count["lost_time"],
            p_sif=occurrence_count["p_sif"],
            sif=occurrence_count["sif"],
        )

    async def get_contractors_aliases(
        self,
        tenant_id: UUID,
        ids: list[uuid.UUID] | None = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[ContractorAlias]:
        statement = select(ContractorAlias).where(
            ContractorAlias.tenant_id == tenant_id
        )
        if ids:
            statement = statement.where(col(ContractorAlias.contractor_id).in_(ids))

        statement = set_order_by(ContractorAlias, statement, order_by=order_by)
        return (await self.session.exec(statement)).all()

    async def register_contractor_alias(
        self, id: UUID, name: str, tenant_id: UUID
    ) -> ContractorAlias:
        alias = ContractorAlias(alias=name, contractor_id=id, tenant_id=tenant_id)
        self.session.add(alias)
        await self.session.commit()
        return alias

    async def create_new_contractor(self, name: str, tenant_id: UUID) -> Contractor:
        contractor = Contractor(name=name, tenant_id=tenant_id)
        self.session.add(contractor)
        await self.session.commit()
        return contractor
