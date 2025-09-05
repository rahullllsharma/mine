import json
import uuid
from logging import getLogger
from typing import Any, Callable

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import col, select

from tests.db_data import DBData
from tests.factories import (
    ContractorFactory,
    LibraryAssetTypeFactory,
    LibraryDivisionFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    LibrarySiteConditionFactory,
    LibraryTaskFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    TenantFactory,
    TenantLibrarySiteConditionSettingsFactory,
    TenantLibraryTaskSettingsFactory,
    UserFactory,
    WorkPackageFactory,
    WorkTypeFactory,
    WorkTypeLibrarySiteConditionLinkFactory,
    WorkTypeTaskLinkFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    create_project_gql,
    gql_project,
    update_configuration,
    valid_project_location_request,
)
from worker_safety_service.dal.configurations import (
    WORK_PACKAGE_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.models import (
    AsyncSession,
    Tenant,
    TenantLibrarySiteConditionSettings,
    TenantLibraryTaskSettings,
    WorkTypeLibrarySiteConditionLink,
    WorkTypeTaskLink,
)
from worker_safety_service.rest.routers.library_site_conditions import (
    LibrarySiteConditionAttributes,
    LibrarySiteConditionRequest,
)
from worker_safety_service.rest.routers.library_tasks import (
    LibraryTaskAttributes,
    LibraryTaskRequest,
)
from worker_safety_service.rest.routers.work_types import (
    WorkTypeAttributes,
    WorkTypeRequest,
)

logger = getLogger(__name__)

WORK_TYPE_ROUTE = "http://127.0.0.1:8000/rest/work-types"
LIBRARY_TASKS_ROUTE = "http://127.0.0.1:8000/rest/library-tasks"
TENANT_LIBRARY_TASK_SETTINGS_ROUTE = (
    "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-tasks/{library_task_id}"
)
LIBRARY_SC_ROUTE = "http://127.0.0.1:8000/rest/library-site-conditions"
TENANT_LIBRARY_SC_SETTINGS_ROUTE = "http://127.0.0.1:8000/rest/settings/{tenant_id}/library-site-conditions/{library_site_condition_id}"

tenant_and_work_type_linked_library_tasks_query = {
    "operation_name": "tenantAndWorkTypeLinkedLibraryTasks",
    "query": """
query tenantAndWorkTypeLinkedLibraryTasks ($tenantWorkTypeIds:[UUID!]!, $ids: [UUID!], $withName: Boolean! = true, $withHazards: Boolean! = false, $withWorkType: Boolean = true, $orderBy: [LibraryTaskOrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tenantAndWorkTypeLinkedLibraryTasks(orderBy: $orderBy, tenantWorkTypeIds: $tenantWorkTypeIds, ids: $ids) {
    id
    name @include(if: $withName)
    isCritical
    hespScore
    riskLevel
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        isApplicable
        controls (orderBy: $controlsOrderBy) {
            id
            name
            isApplicable
        }
    }
    workTypes @include(if: $withWorkType){
      name
      id
    }
  }
}
""",
}

tenant_work_type_query = {
    "operation_name": "twts",
    "query": """
            query twts{
                tenantWorkTypes{
                    name
                    id
                    coreWorkTypeIds
                }
            }
        """,
}

tenant_and_work_type_linked_site_conditions_query = {
    "operation_name": "siteConditionsLibrary",
    "query": """
query siteConditionsLibrary ($tenantWorkTypeIds:[UUID!]!, $id: UUID, $withName: Boolean! = true, $withHazards: Boolean! = false, $orderBy: [OrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tenantAndWorkTypeLinkedLibrarySiteConditions(orderBy: $orderBy, tenantWorkTypeIds: $tenantWorkTypeIds, id: $id) {
    id
    name @include(if: $withName)
    workTypes{
      name
      id
    }
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        isApplicable
        controls (orderBy: $controlsOrderBy) {
            id
            name
            isApplicable
        }
    }
  }
}
""",
}


async def call_task_linked_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(
        **tenant_and_work_type_linked_library_tasks_query,
        variables=kwargs,
        user=kwargs.pop("user", None),
    )
    tasks: list[dict] = data["tenantAndWorkTypeLinkedLibraryTasks"]
    return tasks


async def call_sc_linked_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(
        **tenant_and_work_type_linked_site_conditions_query,
        variables=kwargs,
        user=kwargs.pop("user", None),
    )
    tasks: list[dict] = data["tenantAndWorkTypeLinkedLibrarySiteConditions"]
    return tasks


@pytest.mark.asyncio
@pytest.mark.integration
async def test_if_tasks_are_filtered_wrt_work_package_work_type_scenario1(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    execute_gql: ExecuteGQL,
    configurations_manager: ConfigurationsManager,
    db_data: DBData,
) -> None:
    admin_tenant, user = await TenantFactory.new_with_admin(db_session)
    client = rest_client(custom_tenant=admin_tenant)
    tenants = (await db_session.execute(select(Tenant))).scalars().all()
    tenant_task_links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    col(TenantLibraryTaskSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert tenant_task_links

    cwt_id_1 = uuid.uuid4()
    cwt_id_2 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.1_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_1}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.2_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_2}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    lt_id_1 = uuid.uuid4()
    lt_id_2 = uuid.uuid4()
    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.1",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_1)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.2",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_2)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    # after any library entity creation, that entity should be automatically be
    # enabled for every tenant in the system.
    curr_tenant_task_links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    col(TenantLibraryTaskSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert curr_tenant_task_links
    assert len(curr_tenant_task_links) == len(tenant_task_links) + (len(tenants) * 2)

    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-tasks/{str(lt_id_1)}"
    )
    assert response.status_code == 200

    # CREATING TENANT WORK TYPE
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_1", core_work_type_ids=[cwt_id_1, cwt_id_2]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={admin_tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # check if the tenant work type has appropriate task links.
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt_id_1, cwt_id_2, twt_id]),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 5

    # re verify the tenant task settings to make sure no extra link is created post linking tasks with work types because
    # we try adding links to tenant settings post linking a library entity to a work type
    re_tenant_task_links = (
        (
            await db_session.execute(
                select(TenantLibraryTaskSettings).where(
                    col(TenantLibraryTaskSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert re_tenant_task_links
    assert len(re_tenant_task_links) == len(curr_tenant_task_links)

    # WORK PACKAGE CREATION
    data = await execute_gql(**tenant_work_type_query, user=user)
    tenant_work_types: list[dict] = data["tenantWorkTypes"]
    assert len(tenant_work_types) == 1
    assert tenant_work_types[0]["id"] == str(twt_id)

    # CREATING WORK PACKAGE WITH THE CREATED TENANT WORK TYPE
    project = WorkPackageFactory.build(
        manager_id=(await ManagerUserFactory.persist(db_session)).id,
        primary_assigned_user_id=(await SupervisorUserFactory.persist(db_session)).id,
        additional_assigned_users_ids=[
            (await SupervisorUserFactory.persist(db_session)).id
        ],
        contractor_id=(await ContractorFactory.persist(db_session)).id,
        region_id=(await LibraryRegionFactory.persist(db_session)).id,
        division_id=(await LibraryDivisionFactory.persist(db_session)).id,
        work_type_id=(await LibraryProjectTypeFactory.persist(db_session)).id,
        work_type_ids=[tenant_work_types[0]["id"]],
        asset_type_id=(await LibraryAssetTypeFactory.persist(db_session)).id,
        tenant_id=admin_tenant.id,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        admin_tenant.id,
        WORK_PACKAGE_CONFIG,
        required_fields=None,
    )

    project_data = gql_project(project)
    project_data["locations"] = [await valid_project_location_request(db_session)]
    data = await create_project_gql(execute_gql, project_data)
    assert data["name"] == project_data["name"]

    tasks = await call_task_linked_query(
        execute_gql, tenantWorkTypeIds=project_data["workTypeIds"], user=user
    )
    assert len(tasks) == 2
    assert {task["id"] for task in tasks} == {str(lt_id_1), str(lt_id_2)}

    # DELETION
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_([cwt_id_1, cwt_id_2, twt_id]),
            )
        )
    ).all()
    assert wt_t_link

    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id).in_([lt_id_1, lt_id_2]),
            )
        )
    ).all()
    assert tt_links

    work_types = await db_data.work_types_by_id([cwt_id_1, cwt_id_2, twt_id])
    library_tasks = await db_data.library_tasks(library_task_ids=[lt_id_1, lt_id_2])
    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, tt_links)
    await UserFactory.delete_many(db_session, [user])
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_if_tasks_are_filtered_wrt_work_package_work_type_scenario2(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    execute_gql: ExecuteGQL,
    db_data: DBData,
) -> None:
    tenant, user = await TenantFactory.new_with_admin(db_session)
    client = rest_client(custom_tenant=tenant)
    # INITIAL SETUP
    # create 2 core wt's
    cwt_id_1 = uuid.uuid4()
    cwt_id_2 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_1}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.4_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_2}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # create some library tasks
    lt_id_1 = uuid.uuid4()
    lt_id_2 = uuid.uuid4()
    lt_id_3 = uuid.uuid4()
    lt_id_4 = uuid.uuid4()
    lt_id_5 = uuid.uuid4()
    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.3",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_1)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.4",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_2)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.5",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_3)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.6",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_4)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    library_task_body = LibraryTaskRequest.pack(
        attributes=LibraryTaskAttributes(
            name="TestTask1.7",
            hesp_score=6017,
            category="test_category",
            unique_task_id=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_TASKS_ROUTE}/{str(lt_id_5)}",
        json=jsonable_encoder(library_task_body.dict()),
    )
    assert response.status_code == 201

    # link the tasks to core wt's
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_3)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-tasks/{str(lt_id_4)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-tasks/{str(lt_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-tasks/{str(lt_id_5)}"
    )
    assert response.status_code == 200

    # CREATING TENANT WORK TYPE
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_2", core_work_type_ids=[cwt_id_1, cwt_id_2]
        )
    )
    twt_id_1 = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id_1}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # assert proper filtering of tasks
    tasks = await call_task_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1], user=user
    )
    assert len(tasks) == 5
    assert {task["id"] for task in tasks} == {
        str(lt_id_1),
        str(lt_id_2),
        str(lt_id_3),
        str(lt_id_4),
        str(lt_id_5),
    }

    # now we will split the cwt 1 into 2 new cwt's by deleting the cwt with id cwt_id_1 and creating
    # 2 new cwt's and distributing the linked library tasks to the new cwt's
    response = await client.delete(f"{WORK_TYPE_ROUTE}/{cwt_id_1}")
    assert response.status_code == 200

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id) == cwt_id_1,
            )
        )
    ).all()
    assert not wt_t_link

    cwt_id_3 = uuid.uuid4()
    cwt_id_4 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3.1_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_3}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3.2_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_4}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_3)}/relationships/library-tasks/{str(lt_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_3)}/relationships/library-tasks/{str(lt_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_4)}/relationships/library-tasks/{str(lt_id_3)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_4)}/relationships/library-tasks/{str(lt_id_4)}"
    )
    assert response.status_code == 200

    # now we update the tenant work type with one new core wt and one old core wt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(core_work_type_ids=[cwt_id_3, cwt_id_2])
    )
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(twt_id_1)}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 200

    # now if we have some project with the update tenant wt then the tasks should be filtered as per new links, so in the
    # below case as the twt is linked to cwt 3 and 2 then only the tasks linked to these 2 cwts should show up in the project,
    # whereas previously the twt was linked to twt 1 and 2
    tasks = await call_task_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1], user=user
    )
    assert len(tasks) == 3
    assert {task["id"] for task in tasks} == {
        str(lt_id_1),
        str(lt_id_2),
        str(lt_id_5),
    }

    # we now create an new twt with cwt 4
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_3", core_work_type_ids=[cwt_id_4]
        )
    )
    twt_id_2 = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id_2}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # now if we have a project that has both the work types i.e the updated twt and the new twt
    # then the only tasks that appear in the project should be mapped to these 2 twt's
    tasks = await call_task_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1, twt_id_2], user=user
    )
    assert len(tasks) == 5
    assert {task["id"] for task in tasks} == {
        str(lt_id_1),
        str(lt_id_2),
        str(lt_id_3),
        str(lt_id_4),
        str(lt_id_5),
    }

    # DELETION
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_(
                    [cwt_id_3, cwt_id_4, cwt_id_2, twt_id_1, twt_id_2]
                ),
            )
        )
    ).all()
    assert wt_t_link

    tt_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id).in_(
                    [lt_id_1, lt_id_2, lt_id_3, lt_id_4, lt_id_5]
                ),
            )
        )
    ).all()
    assert tt_links

    work_types = await db_data.work_types_by_id(
        [cwt_id_3, cwt_id_2, cwt_id_4, twt_id_1, twt_id_2]
    )
    library_tasks = await db_data.library_tasks(
        library_task_ids=[lt_id_1, lt_id_2, lt_id_3, lt_id_4, lt_id_5]
    )
    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_t_link)
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, tt_links)
    await UserFactory.delete_many(db_session, [user])
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_if_site_conditions_are_filtered_wrt_work_package_work_type_scenario1(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    execute_gql: ExecuteGQL,
    configurations_manager: ConfigurationsManager,
    db_data: DBData,
) -> None:
    admin_tenant, user = await TenantFactory.new_with_admin(db_session)
    client = rest_client(custom_tenant=admin_tenant)
    tenants = (await db_session.execute(select(Tenant))).scalars().all()
    tenant_site_condition_links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    col(TenantLibrarySiteConditionSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert tenant_site_condition_links

    cwt_id_1 = uuid.uuid4()
    cwt_id_2 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.1_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_1}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.2_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_2}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    lsc_id_1 = uuid.uuid4()
    lsc_id_2 = uuid.uuid4()
    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.1",
            id=str(lsc_id_1),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_1)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.2",
            id=str(lsc_id_2),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_2)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    # after any library entity creation, that entity should be automatically be
    # enabled for every tenant in the system.
    curr_tenant_site_condition_links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    col(TenantLibrarySiteConditionSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert curr_tenant_site_condition_links
    assert len(curr_tenant_site_condition_links) == len(tenant_site_condition_links) + (
        len(tenants) * 2
    )

    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-site-conditions/{str(lsc_id_1)}"
    )
    assert response.status_code == 200

    # CREATING TENANT WORK TYPE
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_1", core_work_type_ids=[cwt_id_1, cwt_id_2]
        )
    )
    twt_id = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id}?tenant_id={admin_tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # check if the tenant work type has appropriate site_condition links.
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt_id_1, cwt_id_2, twt_id]
                ),
            )
        )
    ).all()
    assert wt_t_link
    assert len(wt_t_link) == 5

    # re verify the tenant site_condition settings to make sure no extra link is created post linking site_conditions with work types because
    # we try adding links to tenant settings post linking a library entity to a work type
    re_tenant_site_condition_links = (
        (
            await db_session.execute(
                select(TenantLibrarySiteConditionSettings).where(
                    col(TenantLibrarySiteConditionSettings.tenant_id).in_(
                        [tenant.id for tenant in tenants]
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    assert re_tenant_site_condition_links
    assert len(re_tenant_site_condition_links) == len(curr_tenant_site_condition_links)

    # WORK PACKAGE CREATION
    data = await execute_gql(**tenant_work_type_query, user=user)
    tenant_work_types: list[dict] = data["tenantWorkTypes"]
    assert len(tenant_work_types) == 1
    assert tenant_work_types[0]["id"] == str(twt_id)

    # CREATING WORK PACKAGE WITH THE CREATED TENANT WORK TYPE
    project = WorkPackageFactory.build(
        manager_id=(await ManagerUserFactory.persist(db_session)).id,
        primary_assigned_user_id=(await SupervisorUserFactory.persist(db_session)).id,
        additional_assigned_users_ids=[
            (await SupervisorUserFactory.persist(db_session)).id
        ],
        contractor_id=(await ContractorFactory.persist(db_session)).id,
        region_id=(await LibraryRegionFactory.persist(db_session)).id,
        division_id=(await LibraryDivisionFactory.persist(db_session)).id,
        work_type_id=(await LibraryProjectTypeFactory.persist(db_session)).id,
        work_type_ids=[tenant_work_types[0]["id"]],
        asset_type_id=(await LibraryAssetTypeFactory.persist(db_session)).id,
        tenant_id=admin_tenant.id,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        admin_tenant.id,
        WORK_PACKAGE_CONFIG,
        required_fields=None,
    )

    project_data = gql_project(project)
    project_data["locations"] = [await valid_project_location_request(db_session)]
    data = await create_project_gql(execute_gql, project_data)
    assert data["name"] == project_data["name"]

    site_conditions = await call_sc_linked_query(
        execute_gql, tenantWorkTypeIds=project_data["workTypeIds"], user=user
    )
    assert len(site_conditions) == 2
    assert {site_condition["id"] for site_condition in site_conditions} == {
        str(lsc_id_1),
        str(lsc_id_2),
    }

    # DELETION
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt_id_1, cwt_id_2, twt_id]
                ),
            )
        )
    ).all()
    assert wt_t_link

    tt_links = (
        await db_session.exec(
            select(TenantLibrarySiteConditionSettings).where(
                col(TenantLibrarySiteConditionSettings.library_site_condition_id).in_(
                    [lsc_id_1, lsc_id_2]
                ),
            )
        )
    ).all()
    assert tt_links

    work_types = await db_data.work_types_by_id([cwt_id_1, cwt_id_2, twt_id])
    library_site_conditions = await db_data.library_site_conditions(
        library_site_condition_ids=[lsc_id_1, lsc_id_2]
    )
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_t_link)
    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, tt_links)
    await UserFactory.delete_many(db_session, [user])
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_if_site_conditions_are_filtered_wrt_work_package_work_type_scenario2(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
    execute_gql: ExecuteGQL,
    db_data: DBData,
) -> None:
    tenant, user = await TenantFactory.new_with_admin(db_session)
    client = rest_client(custom_tenant=tenant)
    # INITIAL SETUP
    # create 2 core wt's
    cwt_id_1 = uuid.uuid4()
    cwt_id_2 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_1}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.4_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_2}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # create some library site_conditions
    lsc_id_1 = uuid.uuid4()
    lsc_id_2 = uuid.uuid4()
    lsc_id_3 = uuid.uuid4()
    lsc_id_4 = uuid.uuid4()
    lsc_id_5 = uuid.uuid4()
    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.3",
            id=str(lsc_id_1),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_1)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.4",
            id=str(lsc_id_2),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_2)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.5",
            id=str(lsc_id_3),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_3)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.6",
            id=str(lsc_id_4),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_4)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    library_site_condition_body = LibrarySiteConditionRequest.pack(
        attributes=LibrarySiteConditionAttributes(
            name="TestSiteCondition1.7",
            id=str(lsc_id_5),
            handle_code=str(uuid.uuid4()),
        )
    )
    response = await client.post(
        url=f"{LIBRARY_SC_ROUTE}/{str(lsc_id_5)}",
        json=jsonable_encoder(library_site_condition_body.dict()),
    )
    assert response.status_code == 201

    # link the site_conditions to core wt's
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_3)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_1)}/relationships/library-site-conditions/{str(lsc_id_4)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-site-conditions/{str(lsc_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_2)}/relationships/library-site-conditions/{str(lsc_id_5)}"
    )
    assert response.status_code == 200

    # CREATING TENANT WORK TYPE
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_2", core_work_type_ids=[cwt_id_1, cwt_id_2]
        )
    )
    twt_id_1 = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id_1}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # assert proper filtering of site_conditions
    site_conditions = await call_sc_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1], user=user
    )
    assert len(site_conditions) == 5
    assert {site_condition["id"] for site_condition in site_conditions} == {
        str(lsc_id_1),
        str(lsc_id_2),
        str(lsc_id_3),
        str(lsc_id_4),
        str(lsc_id_5),
    }

    # now we will split the cwt 1 into 2 new cwt's by deleting the cwt with id cwt_id_1 and creating
    # 2 new cwt's and distributing the linked library site_conditions to the new cwt's
    response = await client.delete(f"{WORK_TYPE_ROUTE}/{cwt_id_1}")
    assert response.status_code == 200

    wt_t_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id) == cwt_id_1,
            )
        )
    ).all()
    assert not wt_t_link

    cwt_id_3 = uuid.uuid4()
    cwt_id_4 = uuid.uuid4()
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3.1_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_3}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(name=f"test_cwt_1.3.2_{uuid.uuid4()}")
    )
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{cwt_id_4}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_3)}/relationships/library-site-conditions/{str(lsc_id_1)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_3)}/relationships/library-site-conditions/{str(lsc_id_2)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_4)}/relationships/library-site-conditions/{str(lsc_id_3)}"
    )
    assert response.status_code == 200
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(cwt_id_4)}/relationships/library-site-conditions/{str(lsc_id_4)}"
    )
    assert response.status_code == 200

    # now we update the tenant work type with one new core wt and one old core wt.
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(core_work_type_ids=[cwt_id_3, cwt_id_2])
    )
    response = await client.put(
        f"{WORK_TYPE_ROUTE}/{str(twt_id_1)}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 200

    # now if we have some project with the update tenant wt then the site_conditions should be filtered as per new links, so in the
    # below case as the twt is linked to cwt 3 and 2 then only the site_conditions linked to these 2 cwts should show up in the project,
    # whereas previously the twt was linked to twt 1 and 2
    site_conditions = await call_sc_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1], user=user
    )
    assert len(site_conditions) == 3
    assert {site_condition["id"] for site_condition in site_conditions} == {
        str(lsc_id_1),
        str(lsc_id_2),
        str(lsc_id_5),
    }

    # we now create an new twt with cwt 4
    work_type_request = WorkTypeRequest.pack(
        attributes=WorkTypeAttributes(
            name="test_tenant_wt_3", core_work_type_ids=[cwt_id_4]
        )
    )
    twt_id_2 = uuid.uuid4()
    response = await client.post(
        f"{WORK_TYPE_ROUTE}/{twt_id_2}?tenant_id={tenant.id}",
        json=json.loads(work_type_request.json()),
    )
    assert response.status_code == 201

    # now if we have a project that has both the work types i.e the updated twt and the new twt
    # then the only site_conditions that appear in the project should be mapped to these 2 twt's
    site_conditions = await call_sc_linked_query(
        execute_gql, tenantWorkTypeIds=[twt_id_1, twt_id_2], user=user
    )
    assert len(site_conditions) == 5
    assert {site_condition["id"] for site_condition in site_conditions} == {
        str(lsc_id_1),
        str(lsc_id_2),
        str(lsc_id_3),
        str(lsc_id_4),
        str(lsc_id_5),
    }

    # DELETION
    wt_t_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [cwt_id_3, cwt_id_4, cwt_id_2, twt_id_1, twt_id_2]
                ),
            )
        )
    ).all()
    assert wt_t_link

    tt_links = (
        await db_session.exec(
            select(TenantLibrarySiteConditionSettings).where(
                col(TenantLibrarySiteConditionSettings.library_site_condition_id).in_(
                    [lsc_id_1, lsc_id_2, lsc_id_3, lsc_id_4, lsc_id_5]
                ),
            )
        )
    ).all()
    assert tt_links

    work_types = await db_data.work_types_by_id(
        [cwt_id_3, cwt_id_2, cwt_id_4, twt_id_1, twt_id_2]
    )
    library_site_conditions = await db_data.library_site_conditions(
        library_site_condition_ids=[lsc_id_1, lsc_id_2, lsc_id_3, lsc_id_4, lsc_id_5]
    )
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_t_link)
    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, tt_links)
    await UserFactory.delete_many(db_session, [user])
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)
