from typing import Any, Callable

import pytest
from httpx import AsyncClient

from tests.factories import IncidentTaskFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

INCIDENTS_ROUTE = "/rest/incidents"

historic_incidents_query = {
    "operation_name": "historicalIncidents",
    "query": """
        query historicalIncidents($libraryTaskId: UUID!, $allow_archived: Boolean! = false) {
            historicalIncidents(libraryTaskId: $libraryTaskId, allowArchived: $allow_archived ) {
                id
                severity
                incidentDate
                taskTypeId
                taskType
                severityCode
                incidentType
                incidentId
                description
                archivedAt
            }
        }
""",
}


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**historic_incidents_query, variables=kwargs)
    tasks: list[dict] = data["historicalIncidents"]
    return tasks


@pytest.mark.asyncio
@pytest.mark.integration
async def test_incidents_gql(
    db_session: AsyncSession,
    execute_gql: ExecuteGQL,
    rest_client: Callable[..., AsyncClient],
) -> None:
    incident_task_link = await IncidentTaskFactory.persist(db_session)

    incidents = await call_query(
        execute_gql, libraryTaskId=str(incident_task_link.library_task_id)
    )
    assert incidents
    assert incidents[0]["id"] == str(incident_task_link.incident_id)

    # archive incident
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    response = await client.delete(
        INCIDENTS_ROUTE + "/" + str(incident_task_link.incident_id)
    )
    assert response.status_code == 200

    # check if archived incident doesn't appear in gql results

    incidents = await call_query(
        execute_gql, libraryTaskId=str(incident_task_link.library_task_id)
    )
    assert len(incidents) == 0

    # pass allow_archived flag as true and check if archived incidents appear in gql results

    incidents = await call_query(
        execute_gql,
        libraryTaskId=str(incident_task_link.library_task_id),
        allow_archived=True,
    )
    assert incidents
    assert incidents[0]["id"] == str(incident_task_link.incident_id)
