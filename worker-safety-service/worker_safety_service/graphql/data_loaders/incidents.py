import uuid
from typing import Any, Sequence

from sqlmodel.sql.expression import col
from strawberry.dataloader import DataLoader

from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import OrderBy, OrderByDirection
from worker_safety_service.models.consumer_models import Incident
from worker_safety_service.risk_model.riskmodelreactor import RiskModelReactorInterface
from worker_safety_service.risk_model.triggers import IncidentChanged


def incidents_severity_order_by(
    statement: Any, column: Any, direction: OrderByDirection
) -> Any:
    sql_column: Any = col(column)
    if direction == OrderByDirection.DESC:
        sql_column = sql_column.desc()
    return statement.order_by(sql_column)


class IncidentsLoader:
    def __init__(
        self,
        manager: IncidentsManager,
        risk_model_reactor: RiskModelReactorInterface,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.__risk_model_reactor = risk_model_reactor
        self.incidents_for_library_task = DataLoader(
            load_fn=self.load_incidents_for_library_task
        )
        self.incidents_for_multiple_library_tasks = DataLoader(
            load_fn=self.load_incidents_for_multiple_library_tasks
        )

    async def load_incidents_for_library_task(
        self,
        library_task_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
        limit: int = 10,
        allow_archived: bool = False,
    ) -> list[list[Incident]]:
        incidents = []
        if not order_by:
            order_by = [OrderBy(field="severity", direction=OrderByDirection.DESC)]

        for position, ob in enumerate(order_by):
            if ob.field == "severity":
                ob.custom_order_by = incidents_severity_order_by

        for library_task_id in library_task_ids:
            lti_incidents = await self.__manager.get_incidents_for_library_task_id(
                library_task_id=library_task_id,
                tenant_id=self.tenant_id,
                limit=limit,
                order_by=order_by,
                allow_archived=allow_archived,
            )
            incidents.append(lti_incidents)

        return incidents

    async def get_incidents(
        self,
        ids: list[uuid.UUID] | None = None,
        limit: int | None = None,
        after: uuid.UUID | None = None,
        external_keys: list[str] | None = None,
        allow_archived: bool = False,
    ) -> list[Incident]:
        return await self.__manager.get_incidents(
            tenant_id=self.tenant_id,
            ids=ids,
            limit=limit,
            after=after,
            external_keys=external_keys,
            allow_archived=allow_archived,
        )

    async def get_incident(
        self, id: uuid.UUID, allow_archived: bool = False
    ) -> Incident:
        incidents = await self.get_incidents(ids=[id], allow_archived=allow_archived)
        if not incidents:
            raise ResourceReferenceException("incident not found")
        return incidents[0]

    async def trigger_incidents_changed(self, incidents: Sequence[Incident]) -> None:
        for incident in incidents:
            await self.__risk_model_reactor.add(
                IncidentChanged(incident_id=incident.id)
            )

    async def create_incidents(
        self, incidents: Sequence[Incident]
    ) -> Sequence[Incident]:
        created = await self.__manager.create_incidents(incidents)
        await self.trigger_incidents_changed(created)
        return created

    async def update_incidents(
        self, incidents: Sequence[Incident]
    ) -> Sequence[Incident]:
        updated = await self.__manager.update_incidents(incidents, self.tenant_id)
        await self.trigger_incidents_changed(updated)
        return updated

    async def link_incident_to_library_task(
        self, incident_id: uuid.UUID, library_task_id: uuid.UUID
    ) -> Sequence[Incident]:
        linked = await self.__manager.link_incident_to_library_task(
            incident_id, library_task_id, self.tenant_id
        )
        await self.trigger_incidents_changed([linked])
        return [linked]

    async def load_incidents_for_multiple_library_tasks(
        self,
        library_task_ids: list[uuid.UUID],
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
        allow_archived: bool = False,
    ) -> list[Incident]:
        """Load incidents for multiple library tasks."""
        if not library_task_ids:
            return []

        if not order_by:
            order_by = [OrderBy(field="severity", direction=OrderByDirection.DESC)]

        for ob in order_by:
            if ob.field == "severity":
                ob.custom_order_by = incidents_severity_order_by

        incidents = await self.__manager.get_incidents_for_library_tasks(
            library_task_ids=library_task_ids,
            tenant_id=self.tenant_id,
            limit=limit,
            order_by=order_by,
            allow_archived=allow_archived,
        )
        return incidents
