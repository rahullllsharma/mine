import json
from typing import Callable
from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.rest import verify_pagination
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.api_models import RelationshipData
from worker_safety_service.rest.routers.locations import (
    Location,
    LocationAttributes,
    LocationModelRequest,
    LocationRelationships,
    LocationRequest,
    LocationsRequest,
    OneToOneRelation,
)

LOCATIONS_ROUTE = "/rest/locations"
ACTIVITIES_ROUTE = "/rest/activities"
WORK_PACKAGES_ROUTE = "/rest/work-packages"


def make_attributes() -> LocationAttributes:
    return LocationAttributes(
        name="Overlook Hotel",
        address="333 E Wonderview Ave, Estes Park, CO 80517",
        latitude="40.3829423",
        longitude="-105.5211992",
        external_key=str(uuid4()),
        meta_attributes={"numberOfPeople": 3},
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_location_201_created(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location_request = LocationRequest(
        data=LocationModelRequest(
            attributes=make_attributes(),
            relationships=LocationRelationships(
                activities=None,
                work_packages=OneToOneRelation(
                    data=RelationshipData(type="work-package", id=work_package.id),
                ),
            ),
        )
    )

    response = await rest_api_test_client.post(
        LOCATIONS_ROUTE, json=json.loads(location_request.json())
    )

    assert response.status_code == 201
    location_id = response.json()["data"]["id"]

    retrieved_location_response = await rest_api_test_client.get(
        f"rest/locations/{location_id}"
    )
    links = retrieved_location_response.json()["links"]
    assert links["self"] == LOCATIONS_ROUTE + "/" + location_id

    data = retrieved_location_response.json()["data"]
    assert data["id"] == location_id
    assert data["type"] == "location"

    attributes = data["attributes"]
    lr_attributes = location_request.data.attributes
    assert attributes["name"] == lr_attributes.name
    assert attributes["address"] == lr_attributes.address
    assert attributes["latitude"] == str(lr_attributes.latitude)
    assert attributes["longitude"] == str(lr_attributes.longitude)

    relationships = retrieved_location_response.json()["data"]["relationships"]
    work_package_relation = relationships["work_packages"]

    work_package_data = work_package_relation["data"]

    assert work_package_data["id"] == str(
        location_request.data.relationships.work_packages.data.id
    )
    assert (
        work_package_relation["links"]["related"]
        == f"{WORK_PACKAGES_ROUTE}/{location_request.data.relationships.work_packages.data.id}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_location_400_bad_request(
    rest_api_test_client: AsyncClient,
) -> None:
    response = await rest_api_test_client.post(
        LOCATIONS_ROUTE,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_location_400_wrong_tenant(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(
        session=db_session, tenant_id=tenant.id
    )
    location_request = LocationRequest(
        data=LocationModelRequest(
            attributes=make_attributes(),
            relationships=LocationRelationships(
                activities=None,
                work_packages=OneToOneRelation(
                    data=RelationshipData(type="work-package", id=work_package.id),
                ),
            ),
        )
    )
    response = await rest_api_test_client.post(
        LOCATIONS_ROUTE, json=json.loads(location_request.json())
    )
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_location_400_duplicate_key(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location_request = LocationRequest(
        data=LocationModelRequest(
            attributes=make_attributes(),
            relationships=LocationRelationships(
                activities=None,
                work_packages=OneToOneRelation(
                    data=RelationshipData(type="work-package", id=work_package.id),
                ),
            ),
        )
    )
    response = await rest_api_test_client.post(
        LOCATIONS_ROUTE, json=json.loads(location_request.json())
    )
    assert response.status_code == 201

    response = await rest_api_test_client.post(
        LOCATIONS_ROUTE, json=json.loads(location_request.json())
    )
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == "External Key already in use"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_location_404_not_found(rest_api_test_client: AsyncClient) -> None:
    response = await rest_api_test_client.put(f"LOCATIONS_ROUTE/{uuid4()}")

    assert response.status_code == 404

    response_data = response.json()
    assert response_data["detail"] == "Not Found"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_location_200_returned(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(
        db_session,
        name="Location 1",
        external_key="1929|7090",
        address="111 Fairmount Ave, Cleveland Heights, OH 44112",
    )
    latitude = location.geom.decimal_latitude
    longitude = location.geom.decimal_longitude

    new_external_key = str(uuid4())
    location_body = LocationsRequest.pack(
        attributes=Location(
            id=location.id,
            name="Updated Location",
            address="123 Jefferson Boulevard, Washington, DC 10101",
            latitude=latitude,
            longitude=longitude,
            project_id=location.project_id,
            external_key=new_external_key,
        )
    )

    response = await rest_api_test_client.put(
        f"{LOCATIONS_ROUTE}/{location.id}", json=json.loads(location_body.json())
    )
    assert response.status_code == 200

    updated_location = response.json()["data"]["attributes"]
    assert updated_location["name"] == "Updated Location"
    assert updated_location["external_key"] == new_external_key
    assert (
        updated_location["address"] == "123 Jefferson Boulevard, Washington, DC 10101"
    )
    assert updated_location["latitude"] == str(latitude)
    assert updated_location["longitude"] == str(longitude)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_location_200_returned(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(
        db_session, address="333 E Wonderview Ave, Estes Park, CO 80517"
    )

    response = await rest_api_test_client.get(f"{LOCATIONS_ROUTE}/{location.id}")

    assert response.status_code == 200

    links = response.json()["links"]
    assert links["self"] == LOCATIONS_ROUTE + "/" + str(location.id)

    data = response.json()["data"]
    assert data["id"] == str(location.id)
    assert data["type"] == "location"

    attributes = data["attributes"]

    assert attributes["name"] == location.name
    assert attributes["address"] == location.address
    assert attributes["latitude"] == str(location.geom.latitude)
    assert attributes["longitude"] == str(location.geom.longitude)

    relationships = response.json()["data"]["relationships"]
    work_package = relationships["work_packages"]

    work_package_data = work_package["data"]
    assert work_package_data["type"] == "work-package"

    assert work_package_data["id"] == str(location.project_id)
    assert (
        work_package["links"]["related"]
        == f"{WORK_PACKAGES_ROUTE}/{location.project_id}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_location_with_activities_200_returned(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(
        db_session, address="333 E Wonderview Ave, Estes Park, CO 80517"
    )
    _ = await ActivityFactory.persist_many(db_session, 3, location_id=location.id)

    response = await rest_api_test_client.get(f"{LOCATIONS_ROUTE}/{location.id}")

    assert response.status_code == 200
    links = response.json()["links"]
    assert links["self"] == LOCATIONS_ROUTE + "/" + str(location.id)

    data = response.json()["data"]
    assert data["id"] == str(location.id)
    assert data["type"] == "location"

    attributes = data["attributes"]

    assert attributes["name"] == location.name
    assert attributes["address"] == location.address
    assert attributes["latitude"] == str(location.geom.latitude)
    assert attributes["longitude"] == str(location.geom.longitude)

    relationships = response.json()["data"]["relationships"]
    work_package = relationships["work_packages"]
    activities = relationships["activities"]
    assert (
        activities["links"]["related"]
        == f"{ACTIVITIES_ROUTE}?filter[location_id]={location.id}"
    )

    work_package_data = work_package["data"]
    assert work_package_data["type"] == "work-package"
    assert work_package_data["id"] == str(location.project_id)
    assert (
        work_package["links"]["related"]
        == f"{WORK_PACKAGES_ROUTE}/{location.project_id}"
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_location_404_not_found(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    response = await rest_api_test_client.get(f"{LOCATIONS_ROUTE}/{str(uuid4())}")

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_200(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)

    client = rest_client(custom_tenant=tenant)
    client_locations = await LocationFactory.persist_many(
        db_session, tenant_id=tenant.id, size=5, project_id=work_package.id
    )
    response = await client.get(LOCATIONS_ROUTE)
    assert response.status_code == 200

    locations = response.json()["data"]
    assert len(locations) == 5

    assert {str(cl.id) for cl in client_locations} == {
        location["id"] for location in locations
    }

    location_ids = sorted(str(cl.id) for cl in client_locations)
    page2_url = await verify_pagination(
        client.get(f"{LOCATIONS_ROUTE}?page[limit]=2"), location_ids[:2]
    )
    assert page2_url is not None
    page3_url = await verify_pagination(client.get(page2_url), location_ids[2:4])
    assert page3_url is not None
    end_page = await verify_pagination(client.get(page3_url), location_ids[4:])
    assert end_page is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_200_empty_set(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(LOCATIONS_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_activity_ids_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    client = rest_client(custom_tenant=tenant)

    loc1 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    loc2 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    loc3 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )

    activity1 = await ActivityFactory.persist(
        db_session,
        tenant_id=tenant.id,
        location_id=loc1.id,
    )

    activity2 = await ActivityFactory.persist(
        db_session,
        tenant_id=tenant.id,
        location_id=loc2.id,
    )

    activities = [activity1, activity2]

    activity_ids_qps = "&".join(
        f"filter[activity]={activity.id}" for activity in activities
    )
    response = await client.get(f"{LOCATIONS_ROUTE}?{activity_ids_qps}")

    locations = response.json()["data"]
    location_ids = {location["id"] for location in locations}

    assert str(loc1.id) in location_ids
    assert str(loc2.id) in location_ids
    assert str(loc3.id) not in location_ids

    assert len(locations) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_activity_ids_200_empty_set(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(f"{LOCATIONS_ROUTE}?filter[activity]={uuid4()}")

    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_work_package_ids_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    wp1, wp2, wp3 = await WorkPackageFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    client = rest_client(custom_tenant=tenant)

    loc1 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wp1.id
    )

    loc2 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wp2.id
    )

    loc3 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wp3.id
    )

    wps = [wp1, wp2]
    wp_ids_qps = "&".join(f"filter[work-package]={wp.id}" for wp in wps)
    response = await client.get(f"{LOCATIONS_ROUTE}?{wp_ids_qps}")
    locations = response.json()["data"]

    location_ids = {location["id"] for location in locations}

    assert str(loc1.id) in location_ids
    assert str(loc2.id) in location_ids
    assert str(loc3.id) not in location_ids

    assert len(locations) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_work_package_ids_200_empty_set(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(f"{LOCATIONS_ROUTE}?filter[work-package]={uuid4()}")
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_external_key_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    wps = await WorkPackageFactory.persist_many(db_session, tenant_id=tenant.id, size=2)
    wp = await WorkPackageFactory.persist(db_session, tenant=tenant.id)

    client = rest_client(custom_tenant=tenant)

    loc1 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wps[0].id, external_key="123"
    )

    loc2 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wps[1].id, external_key="xyz"
    )

    loc3 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=wp.id, external_key="abc"
    )

    loc4 = await LocationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        project_id=wp.id,
    )

    locs = [loc1, loc2, loc4]

    ek_qps = "&".join(f"filter[external-key]={loc.external_key}" for loc in locs)
    response = await client.get(f"{LOCATIONS_ROUTE}?{ek_qps}")

    locations = response.json()["data"]

    location_ids = {location["id"] for location in locations}

    assert str(loc1.id) in location_ids
    assert str(loc2.id) in location_ids
    assert str(loc3.id) not in location_ids
    assert str(loc4.id) not in location_ids

    assert len(locations) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_external_keys_200_empty_set(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(f"{LOCATIONS_ROUTE}?filter[external-keys]={uuid4()}")
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_id_200(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    wps = await WorkPackageFactory.persist_many(db_session, tenant_id=tenant.id, size=3)
    client = rest_client(custom_tenant=tenant)

    loc1 = await LocationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        project_id=wps[0].id,
    )

    loc2 = await LocationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        project_id=wps[0].id,
    )

    loc3 = await LocationFactory.persist(
        db_session,
        tenant_id=tenant.id,
        project_id=wps[0].id,
    )

    locs = [loc1, loc2]

    id_qps = "&".join(f"filter[location]={loc.id}" for loc in locs)
    response = await client.get(f"{LOCATIONS_ROUTE}?{id_qps}")

    locations = response.json()["data"]

    location_ids = {location["id"] for location in locations}

    assert str(loc1.id) in location_ids
    assert str(loc2.id) in location_ids
    assert str(loc3.id) not in location_ids

    assert len(locations) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_locations_by_ids_200_empty_set(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(f"{LOCATIONS_ROUTE}?filter[location]={uuid4()}")
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_location_204(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    locs = await LocationFactory.persist_many(
        session=db_session, tenant_id=tenant.id, project_id=work_package.id, size=3
    )
    assert [loc.archived_at is None for loc in locs]

    id_qps = "&".join(f"filter[location]={loc.id}" for loc in locs)
    response = await client.delete(f"{LOCATIONS_ROUTE}?{id_qps}")

    assert response.status_code == 204
    empty = await client.get(f"{LOCATIONS_ROUTE}?{id_qps}")

    assert empty.status_code == 200
    assert len(empty.json()["data"]) == 0
