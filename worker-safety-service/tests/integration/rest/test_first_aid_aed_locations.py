import json
from typing import Callable
from uuid import uuid4

import pytest
from faker import Faker
from httpx import AsyncClient

from tests.factories import FirstAidAedLocationsFactory, TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.first_aid_aed_locations import (
    FirstAidAedLocationsAttribute,
    FirstAidAedLocationsRequest,
)

FIRST_AID_AED_LOCATIONS_ROUTE = "http://127.0.0.1:8000/rest/first-aid-aed-locations"
fake = Faker()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_first_aid_location_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    location_name = fake.street_address() + str(uuid4())
    location_type = "first_aid_location"
    first_aid_aed_location_request = FirstAidAedLocationsRequest.pack(
        attributes=FirstAidAedLocationsAttribute(
            location_name=location_name, location_type=location_type
        )
    )
    response = await client.post(
        FIRST_AID_AED_LOCATIONS_ROUTE,
        json=json.loads(first_aid_aed_location_request.json()),
    )
    assert response.status_code == 201
    location = response.json()["data"]["attributes"]

    assert location["location_name"] == location_name
    assert location["location_type"] == location_type


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_aed_location_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    location_name = fake.street_address() + str(uuid4())
    location_type = "aed_location"
    first_aid_aed_location_request = FirstAidAedLocationsRequest.pack(
        attributes=FirstAidAedLocationsAttribute(
            location_name=location_name, location_type=location_type
        )
    )
    response = await client.post(
        FIRST_AID_AED_LOCATIONS_ROUTE,
        json=json.loads(first_aid_aed_location_request.json()),
    )
    assert response.status_code == 201
    location = response.json()["data"]["attributes"]

    assert location["location_name"] == location_name
    assert location["location_type"] == location_type


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_first_aid_aed_locations_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_aed_location = await FirstAidAedLocationsFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    location_name = fake.street_address()
    location_type = "first_aid_location"
    location_request = FirstAidAedLocationsRequest.pack(
        attributes=FirstAidAedLocationsAttribute(
            location_name=location_name, location_type=location_type
        )
    )
    response = await client.put(
        f"{FIRST_AID_AED_LOCATIONS_ROUTE}/{str(db_aed_location[0].id)}",
        json=json.loads(location_request.json()),
    )
    assert response.status_code == 200
    location_response = response.json()["data"]["attributes"]

    assert location_response["location_name"] == location_name
    assert location_response["location_type"] == location_type

    await db_session.refresh(db_aed_location[0])
    assert db_aed_location[0].location_name == location_name
    assert db_aed_location[0].location_type == location_type


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_first_aid_aed_location_204_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_aed_location = await FirstAidAedLocationsFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    response = await client.delete(
        f"{FIRST_AID_AED_LOCATIONS_ROUTE}/{str(db_aed_location[0].id)}",
    )
    assert response.status_code == 204
    await db_session.refresh(db_aed_location[0])
    assert db_aed_location[0].archived_at


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_first_aid_aed_location_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_aed_location = await FirstAidAedLocationsFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )

    response = await client.get(
        f"{FIRST_AID_AED_LOCATIONS_ROUTE}/{str(db_aed_location[0].id)}",
    )
    assert response.status_code == 200
    location_response = response.json()["data"]["attributes"]

    assert location_response["location_name"] == db_aed_location[0].location_name
    assert location_response["location_type"] == db_aed_location[0].location_type


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_burn_kit_location_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    location_name = fake.street_address() + str(uuid4())
    location_type = "burn_kit_location"
    burn_kit_location_request = FirstAidAedLocationsRequest.pack(
        attributes=FirstAidAedLocationsAttribute(
            location_name=location_name, location_type=location_type
        )
    )
    response = await client.post(
        FIRST_AID_AED_LOCATIONS_ROUTE,
        json=json.loads(burn_kit_location_request.json()),
    )
    assert response.status_code == 201
    location = response.json()["data"]["attributes"]

    assert location["location_name"] == location_name
    assert location["location_type"] == location_type
