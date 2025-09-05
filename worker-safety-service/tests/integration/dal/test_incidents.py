import pytest

from tests.factories import IncidentFactory, IncidentTaskFactory, TenantFactory
from worker_safety_service.dal.incidents import IncidentsManager
from worker_safety_service.models.utils import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incident_by_id(
    db_session: AsyncSession, incidents_manager: IncidentsManager
) -> None:
    incident = await IncidentFactory.persist(db_session)
    retrieved_incident = await incidents_manager.get_incident_by_id(
        incident_id=incident.id
    )

    assert incident == retrieved_incident


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incidents_by_id(
    db_session: AsyncSession, incidents_manager: IncidentsManager
) -> None:
    incidents = await IncidentFactory.persist_many(db_session, 2)
    retrieved_incidents_mapping = await incidents_manager.get_incidents_by_id(
        [i.id for i in incidents]
    )

    for incident in incidents:
        assert retrieved_incidents_mapping[incident.id] == incident


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incidents_for_library_task_id(
    db_session: AsyncSession, incidents_manager: IncidentsManager
) -> None:
    incident_task_link = await IncidentTaskFactory.persist(db_session)
    retrieved_incidents = await incidents_manager.get_incidents_for_library_task_id(
        incident_task_link.library_task_id
    )

    for incident in retrieved_incidents:
        assert incident.id == incident_task_link.incident_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tasks_incidents_data(
    db_session: AsyncSession, incidents_manager: IncidentsManager
) -> None:
    # This test case ensures that archived incidents are not
    # being considered for safety climate multiplier calculations

    # create incident and library task with link

    tenant = await TenantFactory.default_tenant(db_session)
    incident_task_link = await IncidentTaskFactory.persist(db_session)

    # get task risk counters
    incidents_data = await incidents_manager.get_tasks_incident_data(
        incident_task_link.library_task_id, tenant_id=tenant.id
    )

    assert incidents_data

    # archive incident
    await incidents_manager.archive_incident(incident_task_link.incident_id)

    # fetch task risk counter again now

    new_incidents_data = await incidents_manager.get_tasks_incident_data(
        incident_task_link.library_task_id, tenant_id=tenant.id
    )
    assert new_incidents_data

    new_incidents_data_dict = new_incidents_data.__dict__
    incidents_data_dict = incidents_data.__dict__

    # check if at least one risk counter type has
    # decreased in value after archiving the incident

    has_decreased = False
    for attr in incidents_data_dict:
        if new_incidents_data_dict[attr] < incidents_data_dict[attr]:
            has_decreased = True
    assert has_decreased
