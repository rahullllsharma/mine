import uuid
from calendar import monthrange
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID

from sqlmodel import col, select

from worker_safety_service.models import (
    ActivitySupervisorLink,
    AsyncSession,
    Observation,
    Supervisor,
    User,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

ESD_type = "Effective Safety Discussion"


class SupervisorsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def get_dates(date_val: datetime | None = None) -> tuple[datetime, datetime]:
        # Get the start of the month passed in by the user
        # and go back to the end of the prior month
        start_of_month = (date_val or datetime.now(timezone.utc)).replace(day=1)
        end_of_prior_month = (start_of_month - timedelta(days=1)).replace(
            hour=23, minute=59, second=59
        )

        one_year_ago = end_of_prior_month.replace(
            year=end_of_prior_month.year - 1,
            day=monthrange(end_of_prior_month.year - 1, end_of_prior_month.month)[1],
        )

        # Move up 2 seconds to start the next month
        start_period = one_year_ago + timedelta(seconds=2)
        start_period = start_period.replace(tzinfo=None)
        end_of_prior_month = end_of_prior_month.replace(tzinfo=None)
        return start_period, end_of_prior_month

    async def get_supervisor(self, supervisor_id: UUID) -> Supervisor:
        statement = select(Supervisor).where(Supervisor.id == supervisor_id)
        return (await self.session.exec(statement)).one()

    async def get_supervisors(
        self, ids: Iterable[UUID] | None = None, tenant_id: UUID | None = None
    ) -> list[Supervisor]:
        if ids is not None and not ids:
            return []
        statement = select(Supervisor)
        if ids:
            statement = statement.where(col(Supervisor.id).in_(ids))
        if tenant_id:
            statement = statement.where(Supervisor.tenant_id == tenant_id)
        return (await self.session.exec(statement)).all()

    async def get_sef_input_data(
        self, supervisor_id: UUID, date_val: datetime | None = None
    ) -> tuple[list[Observation], list[Observation]]:
        if not date_val:
            date_val = datetime.now(timezone.utc)
        return (
            await self.get_supervisor_observations(supervisor_id, date_val),
            await self.get_supervisor_esds(supervisor_id, date_val),
        )

    async def get_supervisor_observations(
        self, supervisor_id: UUID, date_val: datetime
    ) -> list[Observation]:
        start_date, end_date = self.get_dates(date_val)
        statement = (
            select(Observation)
            .where(Observation.supervisor_id == supervisor_id)
            .where(Observation.observation_type != ESD_type)
            .where(end_date >= Observation.observation_datetime)  # type: ignore
            .where(Observation.observation_datetime >= start_date)  # type: ignore
        )
        return (await self.session.exec(statement)).all()

    async def get_supervisor_esds(
        self, supervisor_id: UUID, date_val: datetime
    ) -> list[Observation]:
        start_date, end_date = self.get_dates(date_val)
        statement = (
            select(Observation)
            .where(Observation.supervisor_id == supervisor_id)
            .where(Observation.observation_type == ESD_type)
            .where(end_date >= Observation.observation_datetime)  # type: ignore
            .where(Observation.observation_datetime >= start_date)  # type: ignore
        )
        return (await self.session.exec(statement)).all()

    async def get_supervisors_by_external_keys(
        self, external_keys: Iterable[str], tenant_id: UUID | None = None
    ) -> list[Supervisor]:
        statement = select(Supervisor).where(
            col(Supervisor.external_key).in_(external_keys)
        )
        if tenant_id:
            statement = statement.where(Supervisor.tenant_id == tenant_id)
        return (await self.session.exec(statement)).all()

    async def get_supervisors_by_external_key(
        self, external_key: str, tenant_id: UUID | None = None
    ) -> Supervisor | None:
        statement = select(Supervisor).where(Supervisor.external_key == external_key)
        if tenant_id:
            statement = statement.where(Supervisor.tenant_id == tenant_id)
        return (await self.session.exec(statement)).first()

    async def get_supervisors_by_activity(
        self, tenant_id: UUID, activity_ids: list[UUID]
    ) -> dict[uuid.UUID, list[Supervisor]]:
        supervisors_map: defaultdict[uuid.UUID, list[Supervisor]] = defaultdict(list)
        statement = (
            select(Supervisor, ActivitySupervisorLink)
            .join(
                ActivitySupervisorLink,
                onclause=Supervisor.id == ActivitySupervisorLink.supervisor_id,
            )
            .where(Supervisor.tenant_id == tenant_id)
            .where(col(ActivitySupervisorLink.activity_id).in_(activity_ids))
        )
        supervisor_data: list[tuple[Supervisor, ActivitySupervisorLink]] = (
            await self.session.exec(statement)
        ).all()
        for supervisor, link in supervisor_data:
            supervisors_map[link.activity_id].append(supervisor)
        return supervisors_map

    async def link_supervisor_to_activity(
        self, activity_id: UUID, supervisor_id: UUID
    ) -> bool:
        activity_supervisor_link = ActivitySupervisorLink(
            activity_id=activity_id, supervisor_id=supervisor_id
        )
        self.session.add(activity_supervisor_link)

        try:
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.exception(
                "Error adding supervisor to activity",
                error=e,
                activity_id=activity_id,
                supervisor_id=supervisor_id,
            )
            raise Exception("Failed to add supervisor")

    async def unlink_supervisor_to_activity(
        self, activity_id: UUID, supervisor_id: UUID
    ) -> bool:
        statement = (
            select(ActivitySupervisorLink)
            .where(ActivitySupervisorLink.activity_id == activity_id)
            .where(ActivitySupervisorLink.supervisor_id == supervisor_id)
        )
        activity_supervisor_link: ActivitySupervisorLink | None = (
            await self.session.exec(statement)
        ).first()
        if activity_supervisor_link is None:
            raise Exception("This supervisor is not linked to this activity")

        try:
            await self.session.delete(activity_supervisor_link)
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.exception(
                "Error removing supervisor from activity",
                error=e,
                activity_id=activity_id,
                supervisor_id=supervisor_id,
            )
            raise Exception("Failed to remove supervisor")

    async def create_supervisor(self, external_key: str, tenant_id: UUID) -> Supervisor:
        supervisor = Supervisor(external_key=external_key, tenant_id=tenant_id)
        self.session.add(supervisor)
        await self.session.commit()
        logger.info(
            "Supervisor added",
            supervisor_id=str(supervisor.id),
            external_key=supervisor.external_key,
        )
        return supervisor

    async def set_supervisor_user(
        self, supervisor: Supervisor, user: User
    ) -> Supervisor:
        supervisor.user_id = user.id
        self.session.add(supervisor)
        await self.session.commit()
        logger.info(
            "User added to supervisor",
            supervisor_id=str(supervisor.id),
            user_id=str(supervisor.user_id),
        )
        return supervisor
