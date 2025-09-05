import json
from logging import getLogger
from typing import Callable
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient

from tests.factories import CrewLeaderFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.crew_leaders import (
    CrewLeaderAttributes,
    CrewLeaderRequest,
)

logger = getLogger(__name__)
CREW_LEADERS_ROUTE = "http://127.0.0.1:8000/rest/crew-leaders"
fake = Faker()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    name = fake.name() + str(uuid4())
    company_name = fake.company()
    lanid = fake.numerify(text="####")
    crew_leader_request = CrewLeaderRequest.pack(
        attributes=CrewLeaderAttributes(
            name=name, lanid=lanid, company_name=company_name
        )
    )
    response = await client.post(
        CREW_LEADERS_ROUTE,
        json=json.loads(crew_leader_request.json()),
    )
    assert response.status_code == 201
    crew_leader = response.json()["data"]["attributes"]

    assert crew_leader["name"] == name
    assert crew_leader["lanid"] == lanid
    assert crew_leader["company_name"] == company_name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader_400_validation_error(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    crew_leader_request = CrewLeaderRequest.pack(attributes=CrewLeaderAttributes())
    response = await client.post(
        CREW_LEADERS_ROUTE,
        json=json.loads(crew_leader_request.json()),
    )
    assert response.status_code == 400
    assert response.json()["title"] == "Bad Input"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader_400_duplicate_key_error(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    valid_crew_leader_request = CrewLeaderRequest.pack(
        attributes=CrewLeaderAttributes(
            name="test_343",
            company_name=fake.company(),
            lanid=fake.numerify(text="####"),
        )
    )
    await client.post(
        CREW_LEADERS_ROUTE,
        json=json.loads(valid_crew_leader_request.json()),
    )
    duplicate_key_crew_leader_request = CrewLeaderRequest.pack(
        attributes=CrewLeaderAttributes(name="test_343")
    )
    response = await client.post(
        CREW_LEADERS_ROUTE,
        json=json.loads(duplicate_key_crew_leader_request.json()),
    )
    assert response.status_code == 400
    assert response.json()["title"] == "External Key already in use"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_crew_leaders_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    await CrewLeaderFactory.persist_many(db_session, tenant_id=tenant.id, size=10)

    # Get first set
    first_response = await client.get(
        f"{CREW_LEADERS_ROUTE}", params={"page[limit]": 5}
    )
    assert first_response.status_code == 200

    first_crew_leaders = first_response.json()["data"]
    assert len(first_crew_leaders) == 5

    # Get second set using offset
    second_response = await client.get(
        f"{CREW_LEADERS_ROUTE}", params={"page[limit]": 5, "page[offset]": 5}
    )
    assert second_response.status_code == 200

    second_crew_leaders = second_response.json()["data"]
    assert len(second_crew_leaders) == 5

    # Test offset returns the next set
    for crew_leader in first_crew_leaders:
        assert crew_leader not in second_crew_leaders


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_crew_leaders_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_crew_leaders = await CrewLeaderFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    new_name = fake.name()
    new_company_name = fake.company()
    new_lanid = fake.numerify(text="####")
    crew_leader_request = CrewLeaderRequest.pack(
        attributes=CrewLeaderAttributes(
            name=new_name, company_name=new_company_name, lanid=new_lanid
        )
    )
    response = await client.put(
        f"{CREW_LEADERS_ROUTE}/{str(db_crew_leaders[0].id)}",
        json=json.loads(crew_leader_request.json()),
    )
    assert response.status_code == 200
    crew_leader = response.json()["data"]["attributes"]

    assert crew_leader["name"] == new_name
    assert crew_leader["lanid"] == new_lanid
    assert crew_leader["company_name"] == new_company_name

    await db_session.refresh(db_crew_leaders[0])
    assert db_crew_leaders[0].name == new_name
    assert db_crew_leaders[0].lanid == new_lanid
    assert db_crew_leaders[0].company_name == new_company_name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_crew_leaders_400_duplicate_key(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_crew_leaders = await CrewLeaderFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    crew_leader_request = CrewLeaderRequest.pack(
        attributes=CrewLeaderAttributes(name=db_crew_leaders[0].name)
    )
    response = await client.put(
        f"{CREW_LEADERS_ROUTE}/{str(db_crew_leaders[0].id)}",
        json=json.loads(crew_leader_request.json()),
    )
    assert response.status_code == 400
    assert response.json()["title"] == "External Key already in use"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_crew_leaders_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_crew_leaders = await CrewLeaderFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    response = await client.delete(
        f"{CREW_LEADERS_ROUTE}/{str(db_crew_leaders[0].id)}",
    )
    assert response.status_code == 204
    await db_session.refresh(db_crew_leaders[0])
    assert db_crew_leaders[0].archived_at
