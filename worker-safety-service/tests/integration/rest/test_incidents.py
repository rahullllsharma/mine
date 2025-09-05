import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient

from tests.factories import (
    ContractorFactory,
    IncidentFactory,
    SupervisorFactory,
    TenantFactory,
)
from tests.integration.rest import verify_pagination
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.incidents import (
    IncidentModelRequest,
    IncidentRequestAttributes,
    IncidentsBulkRequest,
    IncidentsRequest,
)

INCIDENTS_ROUTE = "/rest/incidents"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incident_201_created(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    supervisor = await SupervisorFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)
    incident_request = IncidentsRequest(
        data=IncidentModelRequest(
            attributes=IncidentRequestAttributes(
                incident_date="2022-08-03",
                incident_type="accident",
                severity="First Aid Only",
                description="Oh no",
                external_key=str(uuid.uuid4()),
                meta_attributes={"numberOfPeople": 3},
                supervisor_id=supervisor.id,
                contractor_id=contractor.id,
            )
        )
    )

    response = await rest_api_test_client.post(
        INCIDENTS_ROUTE, json=jsonable_encoder(incident_request.dict())
    )

    assert response.status_code == 201
    incident_id = response.json()["data"]["id"]
    retrieved_incident_response = await rest_api_test_client.get(
        f"{INCIDENTS_ROUTE}/{incident_id}"
    )
    data = retrieved_incident_response.json()["data"]

    assert data["id"] == str(incident_id)
    assert data["type"] == "incident"
    attributes = data["attributes"]
    ir_attributes = incident_request.data.attributes
    assert attributes["incident_date"] == str(ir_attributes.incident_date)
    assert attributes["incident_type"] == ir_attributes.incident_type
    assert attributes["severity"] == ir_attributes.severity
    assert attributes["description"] == ir_attributes.description
    assert attributes["external_key"] == ir_attributes.external_key
    assert attributes["meta_attributes"] == ir_attributes.meta_attributes


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incidents(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    supervisor = await SupervisorFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)
    incidents_request = IncidentsBulkRequest(
        data=[
            IncidentModelRequest(
                attributes=IncidentRequestAttributes(
                    incident_date=f"2022-08-0{i + 1}",
                    incident_type="accident",
                    severity="First Aid Only",
                    description="Oh no",
                    external_key=str(uuid.uuid4()),
                    meta_attributes={"numberOfPeople": 3},
                    supervisor_id=supervisor.id,
                    contractor_id=contractor.id,
                )
            ).dict()
            for i in range(5)
        ]
    )
    response = await rest_api_test_client.post(
        f"{INCIDENTS_ROUTE}/bulk", json=jsonable_encoder(incidents_request.dict())
    )

    rd = response.json()["data"]
    assert [d["attributes"]["incident_date"] for d in rd] == [
        f"2022-08-0{i + 1}" for i in range(5)
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incident_400_bad_request(
    rest_api_test_client: AsyncClient,
) -> None:
    response = await rest_api_test_client.post(
        INCIDENTS_ROUTE,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incident_400_duplicate_key(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    incident_request = IncidentsRequest(
        data=IncidentModelRequest(
            attributes=IncidentRequestAttributes(
                incident_date="2022-08-03",
                incident_type="accident",
                severity="First Aid Only",
                description="Oh no",
                external_key=str(uuid.uuid4()),
                meta_attributes={"numberOfPeople": 3},
            )
        )
    )

    response = await rest_api_test_client.post(
        INCIDENTS_ROUTE, json=jsonable_encoder(incident_request.dict())
    )

    assert response.status_code == 201

    response = await rest_api_test_client.post(
        INCIDENTS_ROUTE, json=jsonable_encoder(incident_request.dict())
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == "External Key already in use"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incident(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    incident = await IncidentFactory.persist(db_session)

    response = await rest_api_test_client.get(f"{INCIDENTS_ROUTE}/{incident.id}")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["id"] == str(incident.id)
    assert data["type"] == "incident"
    attributes = data["attributes"]
    assert attributes["incident_date"] == str(incident.incident_date)
    assert attributes["incident_type"] == incident.incident_type
    assert attributes["severity"] == incident.severity
    assert attributes["description"] == incident.description
    assert attributes["external_key"] == incident.external_key


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incident_404(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    _404 = await rest_api_test_client.get(f"{INCIDENTS_ROUTE}/{uuid.uuid4()}")
    assert _404.status_code == 404

    tenant = await TenantFactory.persist(db_session)
    incident_from_another_tenant = await IncidentFactory.persist(
        db_session, tenant_id=tenant.id
    )
    other_tenant_404 = await rest_api_test_client.get(
        f"{INCIDENTS_ROUTE}/{incident_from_another_tenant.id}"
    )
    assert other_tenant_404.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_incidents(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(INCIDENTS_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0

    incidents = await IncidentFactory.persist_many(
        db_session,
        tenant_id=tenant.id,
        size=5,
    )
    response = await client.get(INCIDENTS_ROUTE)
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 5
    assert {str(i.id) for i in incidents} == {d["id"] for d in data}

    # Test Pagination using the existing data
    incident_ids = sorted(str(i.id) for i in incidents)
    page2_url = await verify_pagination(
        client.get(f"{INCIDENTS_ROUTE}?page[limit]=2"), incident_ids[:2]
    )
    assert page2_url is not None
    page3_url = await verify_pagination(client.get(page2_url), incident_ids[2:4])
    assert page3_url is not None
    end_page = await verify_pagination(client.get(page3_url), incident_ids[4:])
    assert end_page is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_incident(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    incident = await IncidentFactory.persist(db_session)
    supervisor = await SupervisorFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)
    external_key = str(uuid.uuid4())
    incident_request = IncidentsRequest(
        data=IncidentModelRequest(
            attributes=IncidentRequestAttributes(
                incident_date="2022-08-03",
                incident_type="accident",
                severity="First Aid Only",
                description="Oh no",
                external_key=external_key,
                meta_attributes={"numberOfPeople": 3},
                supervisor_id=supervisor.id,
                contractor_id=contractor.id,
            )
        )
    )
    response = await rest_api_test_client.put(
        f"{INCIDENTS_ROUTE}/{incident.id}",
        json=jsonable_encoder(incident_request.dict()),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    attributes = data["attributes"]
    assert data["type"] == "incident"
    assert data["id"] == str(incident.id)
    assert attributes["incident_date"] == "2022-08-03"
    assert attributes["incident_type"] == "accident"
    assert attributes["description"] == "Oh no"
    assert attributes["external_key"] == external_key


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_incident_404(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    external_key = str(uuid.uuid4())
    incident_request = IncidentsRequest(
        data=IncidentModelRequest(
            attributes=IncidentRequestAttributes(
                incident_date="2022-08-03",
                incident_type="accident",
                severity="First Aid Only",
                description="Oh no",
                external_key=external_key,
                meta_attributes={"numberOfPeople": 3},
            )
        )
    )
    default_tenant_client = rest_client()
    response = await default_tenant_client.put(
        f"{INCIDENTS_ROUTE}/{uuid.uuid4()}",
        json=jsonable_encoder(incident_request.dict()),
    )

    assert response.status_code == 404

    # ensure we can't update another tenant's incidents
    tenant = await TenantFactory.persist(db_session)
    other_tenant_client = rest_client(custom_tenant=tenant)
    incident = await IncidentFactory.persist(db_session)

    response = await other_tenant_client.put(
        f"{INCIDENTS_ROUTE}/{incident.id}",
        json=jsonable_encoder(incident_request.dict()),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_by_external_keys(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    response = await rest_client().get(
        f"{INCIDENTS_ROUTE}?filter[externalKey]={uuid.uuid4()}"
    )
    assert response.status_code == 200
    assert response.json()["data"] == []

    external_keys = [str(uuid.uuid4()) for _ in range(5)]
    incidents = [
        await IncidentFactory.persist(db_session, external_key=external_key)
        for external_key in external_keys
    ]
    external_keys_qps = "&".join(f"filter[externalKey]={ek}" for ek in external_keys)
    response = await rest_client().get(f"{INCIDENTS_ROUTE}?{external_keys_qps}")
    assert {d["id"] for d in response.json()["data"]} == {str(i.id) for i in incidents}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_incidents(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(INCIDENTS_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0

    incidents = await IncidentFactory.persist_many(
        db_session,
        tenant_id=tenant.id,
        size=5,
    )

    # archive first 2 incidents
    response = await client.delete(INCIDENTS_ROUTE + "/" + str(incidents[0].id))
    assert response.status_code == 200

    response = await client.delete(INCIDENTS_ROUTE + "/" + str(incidents[1].id))
    assert response.status_code == 200

    # check if archived incidents are not appearing in get incidents results

    response = await client.get(INCIDENTS_ROUTE)
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 3
    assert {str(i.id) for i in incidents[2:]} == {d["id"] for d in data}

    # check if include_archived flag shows archived incidents as well

    response = await client.get(INCIDENTS_ROUTE + "?filter[include_archived]=true")
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 5
    assert {str(i.id) for i in incidents} == {d["id"] for d in data}
