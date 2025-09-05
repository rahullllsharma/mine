import datetime
import uuid
from collections import Counter
from typing import Optional, Sequence
from uuid import UUID

from pydantic import BaseModel, Field
from sqlalchemy.exc import DBAPIError
from sqlmodel import col, select

from worker_safety_service.dal.contractors import ContractorsManager
from worker_safety_service.dal.supervisors import SupervisorsManager
from worker_safety_service.dal.work_types import WorkTypeManager
from worker_safety_service.exceptions import (
    DuplicateExternalKeyException,
    ResourceReferenceException,
)
from worker_safety_service.models import (
    AsyncSession,
    Incident,
    IncidentTask,
    LibraryTask,
    set_order_by,
)
from worker_safety_service.types import OrderBy


def count_incident_type_occurences(incidents: list[Incident]) -> Counter:
    occurrence_count: Counter[str] = Counter()
    for incident in incidents:
        if incident.severity is None:
            continue
        severity = incident.severity.to_ml_code()
        occurrence_count[severity] += 1

    return occurrence_count


class IncidentData(BaseModel):
    near_miss: Optional[int] = Field(default=0)
    first_aid: Optional[int] = Field(default=0)
    recordable: Optional[int] = Field(default=0)
    restricted: Optional[int] = Field(default=0)
    lost_time: Optional[int] = Field(default=0)
    p_sif: Optional[int] = Field(default=0)
    sif: Optional[int] = Field(default=0)


class IncidentsManager:
    def __init__(
        self,
        session: AsyncSession,
        contractor_manager: ContractorsManager,
        supervisors_manager: SupervisorsManager,
        work_type_manager: WorkTypeManager,
    ):
        self.session = session
        self.contractor_manager = contractor_manager
        self.supervisors_manager = supervisors_manager
        self.work_type_manager = work_type_manager

    async def get_incidents(
        self,
        ids: list[uuid.UUID] | None = None,
        tenant_id: uuid.UUID | None = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        external_keys: list[str] | None = None,
        allow_archived: bool = False,
    ) -> list[Incident]:
        """
        Retrieve incidents
        """
        if ids is not None and not ids:
            return []
        elif external_keys is not None and not external_keys:
            return []

        statement = select(Incident).order_by(Incident.id)
        if ids:
            statement = statement.where(col(Incident.id).in_(ids))
        if external_keys:
            statement = statement.where(col(Incident.external_key).in_(external_keys))
        if tenant_id:
            statement = statement.where(Incident.tenant_id == tenant_id)

        if not allow_archived:
            statement = statement.where(col(Incident.archived_at).is_(None))

        if limit is not None:
            statement = statement.limit(limit)

        if after is not None:
            statement = statement.where(Incident.id > after)
        return (await self.session.exec(statement)).all()

    async def get_incident_task_links(
        self,
        incident_ids: Sequence[uuid.UUID] | None = None,
        library_task_ids: Sequence[uuid.UUID] | None = None,
    ) -> Sequence[IncidentTask]:
        if incident_ids is not None and not incident_ids:
            return []
        if library_task_ids is not None and not library_task_ids:
            return []

        statement = select(IncidentTask)
        if incident_ids:
            statement = statement.where(col(IncidentTask.incident_id).in_(incident_ids))
        if library_task_ids:
            statement = statement.where(
                col(IncidentTask.library_task_id).in_(library_task_ids)
            )
        return (await self.session.exec(statement)).all()

    async def get_incidents_by_id(
        self, ids: list[uuid.UUID], allow_archived: bool = False
    ) -> dict[uuid.UUID, Incident]:
        return {
            i.id: i
            for i in await self.get_incidents(ids=ids, allow_archived=allow_archived)
        }

    async def get_incident_by_id(
        self, incident_id: UUID, tenant_id: UUID | None = None
    ) -> Incident | None:
        get_incident_statement = select(Incident).where(Incident.id == incident_id)
        if tenant_id:
            get_incident_statement = get_incident_statement.where(
                Incident.tenant_id == tenant_id
            )
        return (await self.session.exec(get_incident_statement)).first()

    async def get_incident_by_external_key(
        self, key: str, tenant_id: UUID | None = None
    ) -> Incident | None:
        get = select(Incident).where(Incident.external_key == key)
        if tenant_id:
            get = get.where(Incident.tenant_id == tenant_id)
        return (await self.session.exec(get)).first()

    async def get_incidents_for_library_task_id(
        self,
        library_task_id: UUID,
        tenant_id: UUID | None = None,
        limit: int | None = None,
        order_by: Optional[list[OrderBy]] = None,
        allow_archived: bool = False,
    ) -> list[Incident]:
        statement = (
            select(Incident)
            .join(IncidentTask, IncidentTask.incident_id == Incident.id)
            .join(LibraryTask, LibraryTask.id == IncidentTask.library_task_id)
            .where(IncidentTask.library_task_id == library_task_id)
        )
        if tenant_id:
            statement = statement.where(Incident.tenant_id == tenant_id)
        if not allow_archived:
            statement = statement.where(col(Incident.archived_at).is_(None))
        if limit:
            statement = statement.limit(limit)
        if order_by:
            statement = set_order_by(Incident, statement, order_by)

        return (await self.session.exec(statement)).all()

    async def validate_incidents(self, incidents: Sequence[Incident]) -> None:
        if not incidents:
            return
        tenant_id = incidents[0].tenant_id
        assert all(tenant_id == i.tenant_id for i in incidents)

        contractor_ids = {i.contractor_id for i in incidents if i.contractor_id}
        supervisor_ids = {i.supervisor_id for i in incidents if i.supervisor_id}
        work_type_ids = {i.work_type for i in incidents if i.work_type}

        contractors = await self.contractor_manager.get_contractors(
            ids=contractor_ids, tenant_id=tenant_id
        )
        supervisors = await self.supervisors_manager.get_supervisors(
            ids=supervisor_ids, tenant_id=tenant_id
        )
        work_types = await self.work_type_manager.get_work_types(
            ids=work_type_ids, tenant_ids=[tenant_id]
        )

        db_contractor_ids = [c.id for c in contractors]
        db_supervisor_ids = [s.id for s in supervisors]
        db_work_type_ids = [wt.id for wt in work_types]

        missing_contractors = [
            str(c) for c in contractor_ids if c not in db_contractor_ids
        ]
        missing_supervisors = [
            str(s) for s in supervisor_ids if s not in db_supervisor_ids
        ]
        missing_work_types = [
            str(wt) for wt in work_type_ids if wt not in db_work_type_ids
        ]

        if any([missing_contractors, missing_supervisors, missing_work_types]):
            c_message = (
                f"contractors not found: {', '.join(missing_contractors)}"
                if missing_contractors
                else ""
            )
            s_message = (
                f"supervisors not found: {', '.join(missing_supervisors)}"
                if missing_supervisors
                else ""
            )
            wt_message = (
                f"work types not found: {', '.join(missing_work_types)}"
                if missing_work_types
                else ""
            )
            raise ValueError(f"{c_message} {s_message} {wt_message}".strip())

    async def create_incidents(
        self, incidents: Sequence[Incident]
    ) -> Sequence[Incident]:
        await self.validate_incidents(incidents)
        self.session.add_all(incidents)
        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            if (
                db_err.orig.args
                and "ExternalKey must be unique within a Tenant" in db_err.orig.args[0]
            ):
                raise DuplicateExternalKeyException()
            else:
                raise db_err
        return incidents

    async def create_incident(self, incident: Incident) -> Incident:
        return (await self.create_incidents([incident]))[0]

    # TODO: This might be problematic in the future.
    async def link_library_task_by_unique_id(
        self, incident_id: uuid.UUID, unique_task_id: str
    ) -> None:
        statement = select(LibraryTask).where(
            LibraryTask.unique_task_id == unique_task_id
        )
        library_task = (await self.session.exec(statement)).one()

        incident_task = IncidentTask(
            incident_id=incident_id, library_task_id=library_task.id
        )
        self.session.add(incident_task)
        await self.session.commit()

    async def link_incident_to_library_task(
        self, incident_id: uuid.UUID, library_task_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> Incident:
        incident = await self.get_incident_by_id(incident_id, tenant_id)
        if not incident:
            raise ResourceReferenceException("incident not found")

        incident_task = IncidentTask(
            incident_id=incident_id, library_task_id=library_task_id
        )
        self.session.add(incident_task)
        await self.session.commit()
        return incident

    async def get_tasks_incident_data(
        self, library_task_id: UUID, tenant_id: UUID, history_limit_years: float = 5
    ) -> IncidentData:
        since_date = datetime.date.today() - datetime.timedelta(
            days=history_limit_years * 365
        )
        statement = (
            select(Incident)
            .where(Incident.id == IncidentTask.incident_id)
            .where(IncidentTask.library_task_id == library_task_id)
            .where(Incident.tenant_id == tenant_id)
            .where(Incident.incident_date >= since_date)
            .where(col(Incident.archived_at).is_(None))
        )
        incidents = (await self.session.exec(statement)).all()
        occurrence_count = count_incident_type_occurences(incidents)
        return IncidentData(**occurrence_count)

    async def update_incidents(
        self, incidents: Sequence[Incident], tenant_id: UUID | None = None
    ) -> Sequence[Incident]:
        db_incidents = await self.get_incidents(
            [i.id for i in incidents], tenant_id=tenant_id
        )
        if len(db_incidents) != len(incidents):
            raise ValueError("not enough incidents found for update")
        await self.validate_incidents(incidents)

        for db_incident, incident_update in zip(
            sorted(db_incidents, key=lambda i: i.id),
            sorted(incidents, key=lambda i: i.id),
        ):
            db_incident.external_key = incident_update.external_key
            db_incident.incident_date = incident_update.incident_date
            db_incident.incident_type = incident_update.incident_type
            db_incident.task_type = incident_update.task_type
            db_incident.work_type = incident_update.work_type
            db_incident.severity = incident_update.severity
            db_incident.description = incident_update.description
            db_incident.meta_attributes = incident_update.meta_attributes
            db_incident.supervisor_id = incident_update.supervisor_id
            db_incident.contractor_id = incident_update.contractor_id
            self.session.add(db_incident)

        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            if (
                db_err.orig.args
                and "ExternalKey must be unique within a Tenant" in db_err.orig.args[0]
            ):
                raise DuplicateExternalKeyException()

        return incidents

    async def archive_incident(self, id: UUID) -> bool:
        incident_to_be_archived = await self.get_incident_by_id(id)
        if not incident_to_be_archived:
            raise ResourceReferenceException(f"No incident found with id - {id}")

        incident_to_be_archived.archived_at = datetime.datetime.now(
            datetime.timezone.utc
        )
        self.session.add(incident_to_be_archived)
        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            raise db_err

        return True

    async def get_incidents_for_library_tasks(
        self,
        library_task_ids: list[UUID],
        tenant_id: UUID | None = None,
        limit: int | None = None,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = False,
    ) -> list[Incident]:
        statement = (
            select(Incident)
            .join(IncidentTask, IncidentTask.incident_id == Incident.id)
            .join(LibraryTask, LibraryTask.id == IncidentTask.library_task_id)
            .where(col(IncidentTask.library_task_id).in_(library_task_ids))
        )
        if tenant_id:
            statement = statement.where(Incident.tenant_id == tenant_id)
        if not allow_archived:
            statement = statement.where(col(Incident.archived_at).is_(None))
        if limit:
            statement = statement.limit(limit)
        if order_by:
            statement = set_order_by(Incident, statement, order_by)

        return (await self.session.exec(statement)).all()
