import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder

# from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    ActivityFactory,
    LocationFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.rest import verify_pagination
from worker_safety_service.models import Activity, ActivityStatus, AsyncSession
from worker_safety_service.rest.routers.activities import (
    ActivityAttributes,
    ActivityBulkRequest,
    ActivityModelRequest,
    ActivityRelationships,
    ActivityRequest,
    LocationRelationship,
    LocationRelationshipData,
)

ACTIVITIES_ROUTE = "/rest/activities"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(ACTIVITIES_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0

    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    # ActivityFactory does not correctly propogate the tenant_id
    activities = await ActivityFactory.persist_many(
        db_session,
        tenant_id=tenant.id,
        location_id=location.id,
        size=5,
    )

    response = await client.get(ACTIVITIES_ROUTE)
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 5
    assert {str(i.id) for i in activities} == {d["id"] for d in data}

    # Test Pagination using the existing data
    activity_ids = sorted(str(i.id) for i in activities)
    page2_url = await verify_pagination(
        client.get(f"{ACTIVITIES_ROUTE}?page[limit]=2"), activity_ids[:2]
    )
    assert page2_url is not None
    page3_url = await verify_pagination(client.get(page2_url), activity_ids[2:4])
    assert page3_url is not None
    end_page = await verify_pagination(client.get(page3_url), activity_ids[4:])
    assert end_page is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_by_location(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    activities = await ActivityFactory.persist_many(
        db_session,
        tenant_id=tenant.id,
        location_id=location.id,
        size=5,
    )

    activity_ids = set([str(a.id) for a in activities])
    response = await client.get(f"{ACTIVITIES_ROUTE}?filter[location]={uuid.uuid4()}")
    assert response.json()["data"] == []

    loc_activities = await client.get(
        f"{ACTIVITIES_ROUTE}?filter[location]={location.id}"
    )
    loc_activities_data = loc_activities.json()["data"]
    assert len(loc_activities_data) == 5
    assert set([a["id"] for a in loc_activities_data]) == activity_ids

    location2 = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    activities2 = await ActivityFactory.persist_many(
        db_session,
        tenant_id=tenant.id,
        location_id=location.id,
        size=5,
    )

    for a in activities2:
        activity_ids.add(str(a.id))

    loc_activities2 = await client.get(
        f"{ACTIVITIES_ROUTE}?filter[location]={location.id}&filter[location]={location2.id}"
    )
    loc_activities_data2 = loc_activities2.json()["data"]
    assert len(loc_activities_data2) == 10
    assert set([a["id"] for a in loc_activities_data2]) == activity_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_bulk(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)

    def make_request_data(length: int = 5) -> ActivityBulkRequest:
        return ActivityBulkRequest(
            data=[
                ActivityModelRequest(
                    attributes=ActivityAttributes(
                        name=f"{uuid.uuid4()}",
                        start_date=work_package.start_date,
                        end_date=work_package.end_date,
                        status=ActivityStatus.COMPLETE.value,
                        external_key=f"{uuid.uuid4()}",
                        meta_attributes={"numberOfPeople": 3},
                    ),
                    relationships=ActivityRelationships(
                        location=LocationRelationship(
                            data=LocationRelationshipData(
                                id=location.id,
                            )
                        )
                    ),
                ).dict()
                for _ in range(length)
            ]
        )

    bulk_request = make_request_data()
    response = await rest_api_test_client.post(
        f"{ACTIVITIES_ROUTE}/bulk", json=jsonable_encoder(bulk_request.dict())
    )

    assert response.status_code == 201
    data = response.json()["data"]
    assert len(data) == 5

    db_activities: list[Activity] = (
        await db_session.exec(
            select(Activity).where(Activity.location_id == location.id)
        )
    ).all()

    assert len(db_activities) == 5
    assert {dba.name for dba in db_activities} == {
        d.attributes.name for d in bulk_request.data
    }

    too_much_data = make_request_data(201)
    too_much_response = await rest_api_test_client.post(
        f"{ACTIVITIES_ROUTE}/bulk", json=jsonable_encoder(too_much_data.dict())
    )

    assert too_much_response.status_code == 400
    assert too_much_response.json() == {
        "title": "Too many activities",
        "detail": "Limit create requests to 200 activities",
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_201_created(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)

    attributes = ActivityAttributes(
        name=f"{uuid.uuid4()}",
        start_date=work_package.start_date,
        end_date=work_package.end_date,
        status=ActivityStatus.COMPLETE.value,
    )
    relationship = ActivityRelationships(
        location=LocationRelationship(
            data=LocationRelationshipData(
                id=location.id,
            )
        )
    )

    activity_request = ActivityRequest(
        data=ActivityModelRequest(
            attributes=attributes,
            relationships=relationship,
        )
    )

    response = await rest_api_test_client.post(
        ACTIVITIES_ROUTE, json=jsonable_encoder(activity_request.dict())
    )

    assert response.status_code == 201
    data = response.json()["data"]
    r_attributes = data["attributes"]
    assert data["type"] == "activity"
    assert r_attributes["name"] == attributes.name
    assert r_attributes["start_date"] == str(attributes.start_date)
    assert r_attributes["end_date"] == str(attributes.end_date)
    assert r_attributes["status"] == attributes.status
    assert r_attributes["external_key"] == attributes.external_key
    assert r_attributes["meta_attributes"] == attributes.meta_attributes
    assert data["relationships"]["location"]["data"]["id"] == str(location.id)
    assert data["relationships"]["location"]["data"]["type"] == "location"

    db_activity: Activity = (
        await db_session.exec(select(Activity).where(Activity.id == data["id"]))
    ).one()
    assert str(db_activity.id) == data["id"]
    assert db_activity.name == attributes.name
    assert db_activity.start_date == attributes.start_date
    assert db_activity.end_date == work_package.end_date
    assert db_activity.status == ActivityStatus.COMPLETE


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activity_404(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    _404 = await rest_api_test_client.get(f"{ACTIVITIES_ROUTE}/{uuid.uuid4()}")
    assert _404.status_code == 404

    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    activity = await ActivityFactory.persist(
        db_session,
        location_id=location.id,
    )
    other_tenant_404 = await rest_api_test_client.get(
        f"{ACTIVITIES_ROUTE}/{activity.id}"
    )
    assert other_tenant_404.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activity(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    activity = await ActivityFactory.persist(db_session)

    response = await rest_api_test_client.get(f"{ACTIVITIES_ROUTE}/{activity.id}")
    assert response.status_code == 200
    data = response.json()["data"]

    assert data["id"] == str(activity.id)
    assert data["type"] == "activity"
    attributes = data["attributes"]
    assert attributes["name"] == activity.name
    assert attributes["start_date"] == str(activity.start_date)
    assert attributes["end_date"] == str(activity.end_date)
    assert attributes["external_key"] == activity.external_key
    assert attributes["meta_attributes"] == activity.meta_attributes
    assert data["relationships"]["location"]["data"]["id"] == str(activity.location_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_activity(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    external_key = str(uuid.uuid4())
    activity_request = ActivityRequest(
        data=ActivityModelRequest(
            attributes=ActivityAttributes(
                name=f"{uuid.uuid4()}",
                start_date=work_package.start_date,
                end_date=work_package.end_date,
                status=ActivityStatus.COMPLETE.value,
                external_key=external_key,
                meta_attributes={"numberOfPeople": 4},
            ),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(
                        id=activity.location_id,
                    )
                )
            ),
        )
    )
    response = await rest_api_test_client.put(
        f"{ACTIVITIES_ROUTE}/{activity.id}",
        json=jsonable_encoder(activity_request.dict()),
    )

    assert response.status_code == 200
    data = response.json()["data"]
    u_attributes = data["attributes"]
    attributes = activity_request.data.attributes
    assert data["type"] == "activity"
    assert u_attributes["name"] == attributes.name
    assert u_attributes["start_date"] == str(attributes.start_date)
    assert u_attributes["end_date"] == str(attributes.end_date)
    assert u_attributes["status"] == attributes.status
    assert u_attributes["external_key"] == attributes.external_key
    assert u_attributes["meta_attributes"] == attributes.meta_attributes
    assert data["relationships"]["location"]["data"]["id"] == str(location.id)
    assert data["relationships"]["location"]["data"]["type"] == "location"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_activity_404(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    external_key = str(uuid.uuid4())
    activity_request = ActivityRequest(
        data=ActivityModelRequest(
            attributes=ActivityAttributes(
                name=f"{uuid.uuid4()}",
                start_date=work_package.start_date,
                end_date=work_package.end_date,
                status=ActivityStatus.COMPLETE.value,
                external_key=external_key,
                meta_attributes={"numberOfPeople": 4},
            ),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(
                        id=activity.location_id,
                    )
                )
            ),
        )
    )
    default_tenant_client = rest_client()
    response = await default_tenant_client.put(
        f"{ACTIVITIES_ROUTE}/{uuid.uuid4()}",
        json=jsonable_encoder(activity_request.dict()),
    )

    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_activity_404_other_tenant(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, project_id=work_package.id, tenant_id=tenant.id
    )
    activity = await ActivityFactory.persist(db_session, location_id=location.id)

    external_key = str(uuid.uuid4())
    activity_request = ActivityRequest(
        data=ActivityModelRequest(
            attributes=ActivityAttributes(
                name=f"{uuid.uuid4()}",
                start_date=work_package.start_date,
                end_date=work_package.end_date,
                status=ActivityStatus.COMPLETE.value,
                external_key=external_key,
                meta_attributes={"numberOfPeople": 4},
            ),
            relationships=ActivityRelationships(
                location=LocationRelationship(
                    data=LocationRelationshipData(
                        id=activity.location_id,
                    )
                )
            ),
        )
    )
    default_tenant_client = rest_client()
    response = await default_tenant_client.put(
        f"{ACTIVITIES_ROUTE}/{activity.id}",
        json=jsonable_encoder(activity_request.dict()),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_activity(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    activities, tasks = await ActivityFactory.persist_many_with_task(db_session)
    activity = activities[0]
    task = tasks[0]

    assert activity.archived_at is None
    assert task.archived_at is None

    response = await rest_client().delete(f"{ACTIVITIES_ROUTE}/{activity.id}")
    assert response.status_code == 204

    await db_session.refresh(activity)
    await db_session.refresh(task)

    assert activity.archived_at is not None
    assert task.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_activity_404(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    response = await rest_client().delete(f"{ACTIVITIES_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404

    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, project_id=work_package.id, tenant_id=tenant.id
    )
    activity = await ActivityFactory.persist(db_session, location_id=location.id)

    response = await rest_client().delete(f"{ACTIVITIES_ROUTE}/{activity.id}")
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_by_external_keys(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    response = await rest_client().get(
        f"{ACTIVITIES_ROUTE}?filter[externalKey]={uuid.uuid4()}"
    )
    assert response.status_code == 200
    assert response.json()["data"] == []

    external_keys = [str(uuid.uuid4()) for _ in range(5)]
    activities = [
        await ActivityFactory.persist(db_session, external_key=external_key)
        for external_key in external_keys
    ]
    external_keys_qps = "&".join(f"filter[externalKey]={ek}" for ek in external_keys)
    response = await rest_client().get(f"{ACTIVITIES_ROUTE}?{external_keys_qps}")
    assert {d["id"] for d in response.json()["data"]} == {str(a.id) for a in activities}
