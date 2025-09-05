import uuid
from typing import Callable

import pytest
from faker import Faker
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.factories import (
    ActivityFactory,
    LibraryTaskFactory,
    LocationFactory,
    TenantFactory,
    TenantLibraryTaskSettingsFactory,
    WorkTypeFactory,
)
from worker_safety_service.models import (
    Activity,
    AsyncSession,
    TenantLibraryTaskSettings,
)
from worker_safety_service.rest import api_models
from worker_safety_service.rest.routers.library_tasks import (
    LibraryTaskAttributes,
    LibraryTaskInput,
    LibraryTaskInputRequest,
    LibraryTaskRequest,
)
from worker_safety_service.rest.routers.tasks import (
    TaskModelRequest,
    TaskRelationships,
    TaskRequest,
)

ACTIVITIES_ROUTE = "/rest/activities"
TASKS_ROUTE = "/rest/tasks"

LIBRARY_TASKS_ROUTE = "http://127.0.0.1:8000/rest/library-tasks"
WORK_TYPES_ROUTE = "http://127.0.0.1:8000/rest/work-types"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_tasks(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_TASKS_ROUTE}?page[limit]=5")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 5


@pytest.mark.skip(reason="work type id filter parm deprecated.")
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_library_tasks_filtered(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)

    work_type = await WorkTypeFactory.persist(db_session)

    library_task = await LibraryTaskFactory.with_work_type_link(
        db_session,
        work_type_id=work_type.id,
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(
        f"{LIBRARY_TASKS_ROUTE}?filter[work-type]={work_type.id}"
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["id"] == str(library_task.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_get(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_TASKS_ROUTE}/{library_task.id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["attributes"]["name"] == "test_task"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_library_task_get_critical_details(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", is_critical=True, archived_at=None
    )
    client = rest_client(custom_tenant=tenant)

    response = await client.get(f"{LIBRARY_TASKS_ROUTE}/{library_task.id}")
    assert response.status_code == 200

    data = response.json()["data"]
    assert data["attributes"]["is_critical"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_library_task(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    tenant_1, tenant_2 = await TenantFactory.persist_many(db_session, size=2)
    library_task = await LibraryTaskFactory.persist(db_session)

    await TenantLibraryTaskSettingsFactory.persist(
        db_session, tenant_id=tenant_1.id, library_task_id=library_task.id
    )
    await TenantLibraryTaskSettingsFactory.persist(
        db_session, tenant_id=tenant_2.id, library_task_id=library_task.id
    )

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    col(TenantLibraryTaskSettings.tenant_id).in_(
                        [tenant_1.id, tenant_2.id, tenant.id]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) > 1

    client = rest_client(custom_tenant=tenant)
    test_library_task_id = uuid.uuid4()
    work_type = await WorkTypeFactory.persist(db_session)
    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="New Task 1",
            hesp_score=6017,
            category="test_category",
            unique_task_id=Faker().name() + str(uuid.uuid4()),
            work_type_id=work_type.id,
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(test_library_task_id)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201
    new_links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    col(TenantLibraryTaskSettings.tenant_id).in_(
                        [tenant_1.id, tenant_2.id, tenant.id]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert new_links
    assert len(new_links) == len(links) + 3
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, new_links)
    await TenantFactory.delete_many(db_session, [tenant, tenant_1, tenant_2])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_library_task(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    tenant_1, tenant_2 = await TenantFactory.persist_many(db_session, size=2)
    library_task = await LibraryTaskFactory.persist(db_session)

    await TenantLibraryTaskSettingsFactory.persist(
        db_session, tenant_id=tenant_1.id, library_task_id=library_task.id
    )
    await TenantLibraryTaskSettingsFactory.persist(
        db_session, tenant_id=tenant_2.id, library_task_id=library_task.id
    )

    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert links
    assert len(links) > 1

    client = rest_client(custom_tenant=tenant)

    response = await client.delete(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(library_task.id)}",
    )
    assert response.status_code == 200
    links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.library_task_id == library_task.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert not links

    await TenantFactory.delete_many(db_session, [tenant, tenant_1, tenant_2])
    await LibraryTaskFactory.delete_many(db_session, [library_task])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_critical_task_field(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.persist(db_session)
    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", is_critical=False
    )
    client = rest_client(custom_tenant=tenant)
    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name=library_task.name,
            is_critical=True,
            hesp_score=library_task.hesp,
            category=library_task.category,
            unique_task_id=library_task.unique_task_id,
        )
    )
    response = await client.put(
        url=f"{LIBRARY_TASKS_ROUTE}/{library_task.id}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["attributes"]["is_critical"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_multiple_tenant_work_types_library_tasks(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)

    # create 2 worktypes to link to library task
    work_types = await WorkTypeFactory.persist_many_tenant_wt(
        db_session, size=2, tenant=tenant.id
    )

    # create library task
    library_task = await LibraryTaskFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # link work types to library task
    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[0].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[1].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    # get work types for this library task using rest API
    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(library_task.id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]

    # check if both worktype were linked to library tasks
    assert len(data) == 2
    result_ids = sorted([item["id"] for item in data])
    expected_ids = sorted([str(worktype.id) for worktype in work_types])

    assert result_ids == expected_ids

    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id) == library_task.id
            ),
        )
    ).all()
    assert tt_links
    assert len(tt_links) == 1

    # unlink a work_type for the library task

    response = await client.delete(
        f"{WORK_TYPES_ROUTE}/{str(work_types[1].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 204

    # check if the work_type is unlinked now
    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(library_task.id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    result_ids = [item["id"] for item in data]
    assert str(work_types[1].id) not in result_ids

    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id) == library_task.id
            ),
        )
    ).all()
    assert tt_links
    assert len(tt_links) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_multiple_tenant_work_types_library_tasks_with_multiple_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    tenant_1, _ = await TenantFactory.new_with_admin(db_session)

    # create 2 worktypes to link to library task
    work_types_with_tenant = await WorkTypeFactory.persist_many_tenant_wt(
        db_session, size=1, tenant_id=tenant.id
    )
    work_types_with_tenant_1 = await WorkTypeFactory.persist_many_tenant_wt(
        db_session, size=1, tenant_id=tenant_1.id
    )

    # create library task
    library_task = await LibraryTaskFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # link work types to library task
    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types_with_tenant[0].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types_with_tenant_1[0].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    # get work types for this library task using rest API
    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(library_task.id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]

    # check if both worktype were linked to library tasks
    assert len(data) == 2
    result_ids = sorted([item["id"] for item in data])
    expected_ids = sorted(
        [str(work_types_with_tenant[0].id), str(work_types_with_tenant_1[0].id)]
    )

    assert result_ids == expected_ids

    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id) == library_task.id
            ),
        )
    ).all()
    assert tt_links
    assert len(tt_links) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_multiple_core_work_types_library_tasks(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant, _ = await TenantFactory.new_with_admin(db_session)

    # create 2 core worktypes to link to library task
    work_types = await WorkTypeFactory.persist_many(db_session, size=2)
    twt_1 = await WorkTypeFactory.persist(
        db_session, core_work_type_ids=[work_types[0].id], tenant_id=tenant.id
    )
    twt_2 = await WorkTypeFactory.persist(
        db_session, core_work_type_ids=[work_types[1].id], tenant_id=tenant.id
    )

    # create library task
    library_task = await LibraryTaskFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # link work types to library task
    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[0].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[1].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    # get work types for this library task using rest API
    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(library_task.id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]

    # check if both worktype were linked to library tasks
    assert len(data) == 4
    result_ids = sorted([item["id"] for item in data])
    expected_ids = sorted(
        [str(worktype.id) for worktype in work_types] + [str(twt_1.id), str(twt_2.id)]
    )

    assert result_ids == expected_ids

    # it should only have one link because all work types belong to a single tenant.
    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id) == library_task.id
            ),
        )
    ).all()
    assert tt_links
    assert len(tt_links) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_linking_multiple_core_work_types_library_tasks_with_multiple_tenants(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    tenant, _ = await TenantFactory.new_with_admin(db_session)
    tenant2, _ = await TenantFactory.new_with_admin(db_session)

    # create 2 core worktypes to link to library task
    work_types = await WorkTypeFactory.persist_many(db_session, size=2)
    twt_1 = await WorkTypeFactory.persist(
        db_session, core_work_type_ids=[work_types[0].id], tenant_id=tenant.id
    )
    twt_2 = await WorkTypeFactory.persist(
        db_session, core_work_type_ids=[work_types[1].id], tenant_id=tenant.id
    )
    twt_3 = await WorkTypeFactory.persist(
        db_session,
        core_work_type_ids=[work_types[0].id, work_types[1].id],
        tenant_id=tenant2.id,
    )

    # create library task
    library_task = await LibraryTaskFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)

    # link work types to library task
    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[0].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    response = await client.put(
        f"{WORK_TYPES_ROUTE}/{str(work_types[1].id)}/relationships/library-tasks/{str(library_task.id)}"
    )
    assert response.status_code == 200

    # get work types for this library task using rest API
    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(library_task.id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]

    # check if both worktype were linked to library tasks
    assert len(data) == 5
    result_ids = sorted([item["id"] for item in data])
    expected_ids = sorted(
        [str(worktype.id) for worktype in work_types]
        + [str(twt_1.id), str(twt_2.id), str(twt_3.id)]
    )

    assert result_ids == expected_ids

    # it should only have 2 link because work types belong to a 2 tenants.
    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id) == library_task.id
            ),
        )
    ).all()
    assert tt_links
    assert len(tt_links) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_library_task_with_multiple_worktypes(
    rest_client: Callable[..., AsyncClient], db_session: AsyncSession
) -> None:
    test_library_task_id = uuid.uuid4()
    tenant = await TenantFactory.default_tenant(db_session)

    # create 3 worktypes to link to library task
    work_types = await WorkTypeFactory.persist_many_tenant_wt(
        db_session, size=3, tenant=tenant.id
    )
    work_type_ids = [str(item.id) for item in work_types]
    client = rest_client(custom_tenant=tenant)
    library_task_body = LibraryTaskInputRequest.pack(
        attributes=LibraryTaskInput(
            id=test_library_task_id,
            name="New Task 2",
            hesp_score=2000,
            category="6ee68e9a132f44138208cd1223f60ed4",
            unique_task_id=Faker().name() + str(uuid.uuid4()),
            work_types=work_type_ids,
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(test_library_task_id)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    response = await client.get(
        f"{WORK_TYPES_ROUTE}?filter[library-task]={str(test_library_task_id)}"
    )

    assert response.status_code == 200
    data = response.json()["data"]

    # check if all worktypes were linked to the library task
    assert len(data) == 3
    result_ids = sorted([item["id"] for item in data])
    expected_ids = sorted([str(worktype.id) for worktype in work_types])

    assert result_ids == expected_ids


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_library_task_and_create_activity(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)

    library_task = await LibraryTaskFactory.persist(
        db_session, name="test_task", is_critical=False
    )

    updated_library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name=library_task.name,
            is_critical=True,
            hesp_score=library_task.hesp,
            category=library_task.category,
            unique_task_id=library_task.unique_task_id,
        )
    )
    update_response = await rest_client(custom_tenant=tenant).put(
        url=f"{LIBRARY_TASKS_ROUTE}/{library_task.id}",
        json=jsonable_encoder(updated_library_task_body.dict()),
    )
    assert update_response.status_code == 200
    updated_data = update_response.json()["data"]
    assert updated_data["attributes"]["is_critical"]

    activity = await ActivityFactory.persist(
        db_session, library_task_id=library_task.id
    )
    location = await LocationFactory.persist(db_session)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)

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
    activity = await ActivityFactory.persist(db_session)

    result = await db_session.execute(
        select(Activity).where(
            Activity.id == data["relationships"]["activity"]["data"]["id"]
        )
    )
    updated_activity: Activity = result.scalars().one()

    assert updated_activity.is_critical
