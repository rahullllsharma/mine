import datetime
import uuid
from typing import Callable

import pytest
from fastapi.encoders import jsonable_encoder

# from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    ActivityFactory,
    LibraryTaskFactory,
    LocationFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.rest import verify_pagination
from worker_safety_service.models import AsyncSession, Task
from worker_safety_service.rest import api_models
from worker_safety_service.rest.routers.tasks import (
    TaskBulkRequest,
    TaskModelRequest,
    TaskRelationships,
    TaskRequest,
)

ACTIVITIES_ROUTE = "/rest/activities"
TASKS_ROUTE = "/rest/tasks"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tasks(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    empty = await client.get(TASKS_ROUTE)
    assert empty.status_code == 200
    data = empty.json()["data"]
    assert len(data) == 0

    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    activity = await ActivityFactory.persist(
        db_session,
        tenant_id=tenant.id,
        location_id=location.id,
    )
    tasks = await TaskFactory.persist_many(
        db_session, activity_id=activity.id, location_id=location.id, size=5
    )
    response = await client.get(TASKS_ROUTE)
    data = response.json()["data"]
    assert response.status_code == 200
    assert len(data) == 5
    assert {str(i.id) for i in tasks} == {d["id"] for d in data}

    # Test Pagination using the existing data
    task_ids = sorted(str(i.id) for i in tasks)
    page2_url = await verify_pagination(
        client.get(f"{TASKS_ROUTE}?page[limit]=2"), task_ids[:2]
    )
    assert page2_url is not None
    page3_url = await verify_pagination(client.get(page2_url), task_ids[2:4])
    assert page3_url is not None
    end_page = await verify_pagination(client.get(page3_url), task_ids[4:])
    assert end_page is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tasks_by_activity(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, tenant_id=tenant.id, project_id=work_package.id
    )
    external_key = str(uuid.uuid4())
    activity = await ActivityFactory.persist(
        db_session,
        tenant_id=tenant.id,
        location_id=location.id,
        external_key=external_key,
    )
    tasks = await TaskFactory.persist_many(
        db_session, activity_id=activity.id, location_id=location.id, size=5
    )
    task_ids = {str(t.id) for t in tasks}

    no_tasks = await client.get(f"{TASKS_ROUTE}?filter[activity]={uuid.uuid4()}")
    assert no_tasks.status_code == 200
    assert no_tasks.json()["data"] == []

    by_activity_id = await client.get(f"{TASKS_ROUTE}?filter[activity]={activity.id}")
    assert by_activity_id.status_code == 200
    assert task_ids == {d["id"] for d in by_activity_id.json()["data"]}

    by_activity_ek = await client.get(
        f"{TASKS_ROUTE}?filter[activity][externalKey]={activity.external_key}"
    )
    assert by_activity_ek.status_code == 200
    assert task_ids == {d["id"] for d in by_activity_ek.json()["data"]}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_task(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    task = await TaskFactory.persist(
        db_session, activity_id=activity.id, location_id=location.id
    )
    response = await rest_client().get(f"{TASKS_ROUTE}/{task.id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == str(task.id)
    assert data["type"] == "task"
    assert data["attributes"] == {}
    relations = data["relationships"]
    assert relations["activity"]["data"]["id"] == str(activity.id)
    assert relations["activity"]["data"]["type"] == "activity"
    assert (
        relations["activity"]["links"]["related"] == f"/rest/activities/{activity.id}"
    )
    assert relations["libraryTask"]["data"]["id"] == str(task.library_task_id)
    assert relations["libraryTask"]["data"]["type"] == "libraryTask"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_task_404(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    response = await rest_client().get(f"{TASKS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404

    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    task = await TaskFactory.persist(
        db_session, activity_id=activity.id, location_id=location.id
    )
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    other_client_response = await client.get(f"{TASKS_ROUTE}/{task.id}")
    assert other_client_response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task_bulk(
    rest_api_test_client: AsyncClient, db_session: AsyncSession
) -> None:
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=5)
    task = await TaskFactory.persist(
        db_session,
        activity_id=activity.id,
        location_id=location.id,
        library_task_id=library_tasks[0].id,
        archived_at=datetime.datetime.now(),
    )
    assert task.archived_at is not None

    bulk_request = TaskBulkRequest(
        data=[
            TaskModelRequest(
                attributes={},
                relationships=TaskRelationships(
                    activity=api_models.OneToOneRelation(
                        data=api_models.RelationshipData(
                            id=activity.id,
                            type="activity",
                        ),
                    ),
                    libraryTask=api_models.OneToOneRelation(
                        data=api_models.RelationshipData(
                            id=library_task.id,
                            type="libraryTask",
                        ),
                    ),
                ),
            ).dict()
            for library_task in library_tasks
        ]
    )

    response = await rest_api_test_client.post(
        f"{TASKS_ROUTE}/bulk", json=jsonable_encoder(bulk_request.dict())
    )
    await db_session.refresh(task)

    assert response.status_code == 201
    data = response.json()["data"]
    assert len(data) == 5

    db_tasks: list[Task] = (
        await db_session.exec(select(Task).where(Task.location_id == location.id))
    ).all()

    assert len(db_tasks) == 5
    assert {db_task.library_task_id for db_task in db_tasks} == {
        lt.id for lt in library_tasks
    }
    assert all(db_task.archived_at is None for db_task in db_tasks)
    assert task.id in {db_task.id for db_task in db_tasks}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    library_task = await LibraryTaskFactory.persist(db_session)

    task_request = TaskRequest(
        data=TaskModelRequest(
            attributes={},
            relationships=TaskRelationships(
                activity=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        id=activity.id,
                        type="activity",
                    ),
                ),
                libraryTask=api_models.OneToOneRelation(
                    data=api_models.RelationshipData(
                        id=library_task.id,
                        type="libraryTask",
                    ),
                ),
            ),
        )
    )

    response = await rest_client().post(
        TASKS_ROUTE, json=jsonable_encoder(task_request.dict())
    )
    assert response.status_code == 201
    data = response.json()["data"]
    db_task: Task = (
        await db_session.exec(select(Task).where(Task.id == data["id"]))
    ).one()
    assert data["relationships"]["activity"]["data"]["id"] == str(activity.id)
    assert data["relationships"]["libraryTask"]["data"]["id"] == str(library_task.id)
    assert db_task.library_task_id == library_task.id
    assert db_task.activity_id == activity.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    activities, tasks = await ActivityFactory.persist_many_with_task(db_session)
    activity = activities[0]
    task = tasks[0]

    assert activity.archived_at is None
    assert task.archived_at is None

    response = await rest_client().delete(f"{TASKS_ROUTE}/{task.id}")
    assert response.status_code == 204

    await db_session.refresh(activity)
    await db_session.refresh(task)

    assert activity.archived_at is None
    assert task.archived_at is not None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task_404(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    response = await rest_client().delete(f"{TASKS_ROUTE}/{uuid.uuid4()}")
    assert response.status_code == 404

    tenant = await TenantFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(db_session, tenant_id=tenant.id)
    location = await LocationFactory.persist(
        db_session, project_id=work_package.id, tenant_id=tenant.id
    )
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    task = await TaskFactory.persist(
        db_session, activity_id=activity.id, location_id=location.id
    )

    response = await rest_client().delete(f"{TASKS_ROUTE}/{task.id}")
    assert response.status_code == 404
