import uuid
from typing import Any, Optional

import pytest
from sqlmodel import col, select

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibraryTaskFactory,
    LibraryTaskRecommendationsFactory,
    LibraryTaskStandardOperatingProcedureFactory,
    StandardOperatingProcedureFactory,
    TenantFactory,
    TenantLibraryTaskSettingsFactory,
    WorkTypeFactory,
    WorkTypeTaskLinkFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.queries.helpers import (
    asc_order,
    build_library_controls_for_order_by,
    build_library_hazards_for_order_by,
    build_library_tasks_for_order_by,
    desc_order,
    set_library_tasks_relations,
)
from worker_safety_service.models import (
    AsyncSession,
    TenantLibraryTaskSettings,
    WorkTypeTaskLink,
)

library_tasks_query = {
    "operation_name": "tasksLibrary",
    "query": """
query tasksLibrary ($ids: [UUID!], $withName: Boolean! = true, $withHazards: Boolean! = false, $withWorkType: Boolean = true, $withStandardOperatingProcedures: Boolean = false, $orderBy: [LibraryTaskOrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tasksLibrary(ids: $ids, orderBy: $orderBy) {
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
    standardOperatingProcedures @include(if: $withStandardOperatingProcedures){
      id
      name
      link
    }
  }
}
""",
}

tenant_and_work_type_linked_library_tasks_query = {
    "operation_name": "tasksLibrary",
    "query": """
query tasksLibrary ($tenantWorkTypeIds:[UUID!]!, $ids: [UUID!], $withName: Boolean! = true, $withHazards: Boolean! = false, $withWorkType: Boolean = true, $orderBy: [LibraryTaskOrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
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


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**library_tasks_query, variables=kwargs)
    tasks: list[dict] = data["tasksLibrary"]
    return tasks


async def call_linked_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(
        **tenant_and_work_type_linked_library_tasks_query, variables=kwargs
    )
    tasks: list[dict] = data["tenantAndWorkTypeLinkedLibraryTasks"]
    return tasks


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_query(execute_gql: ExecuteGQL) -> None:
    """Simple library tasks check"""

    # Check all tasks
    tasks = await call_query(execute_gql)
    assert tasks
    first_task = tasks[0]
    assert uuid.UUID(first_task["id"])
    assert first_task["name"]
    assert isinstance(first_task["name"], str)

    # Check if filter have valid data
    tasks_one = await call_query(execute_gql, ids=[first_task["id"]])
    assert len(tasks_one) == 1
    assert tasks_one[0] == first_task

    # Check if only id field is sent
    tasks_id = await call_query(execute_gql, withName=False, withWorkType=False)
    assert len(tasks_id) == len(tasks)
    assert all(uuid.UUID(i["id"]) for i in tasks_id)
    returned_fields: set[str] = set()
    for task in tasks_id:
        returned_fields.update(task.keys())
    assert returned_fields == {"id", "isCritical", "hespScore", "riskLevel"}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_resolvers_query(execute_gql: ExecuteGQL) -> None:
    """Check library tasks hazards, controls, and work type resolvers"""

    # Check if all resolvers are defined
    tasks = await call_query(execute_gql, withHazards=True)
    assert tasks
    assert all(isinstance(i["hazards"], list) for i in tasks)
    assert all(isinstance(h["controls"], list) for i in tasks for h in i["hazards"])
    assert all(isinstance(t["hespScore"], int) for t in tasks)
    assert all(isinstance(t["riskLevel"], str) for t in tasks)
    assert all(isinstance(t["isCritical"], bool) for t in tasks)

    task_1: Optional[dict] = None
    task_2: Optional[dict] = None
    for task in tasks:
        with_controls = False
        for hazard in task["hazards"]:
            assert uuid.UUID(hazard["id"])
            assert isinstance(hazard["name"], str)
            assert hazard["isApplicable"] is True
            if hazard["controls"]:
                with_controls = True
            for control in hazard["controls"]:
                assert uuid.UUID(control["id"])
                assert isinstance(control["name"], str)
                assert control["isApplicable"] is True

        if with_controls and task["hazards"]:
            if not task_1:
                task_1 = task
            elif not task_2:
                task_2 = task
        if task["workTypes"]:
            for work_types in task["workTypes"]:
                assert uuid.UUID(work_types["id"])
                assert isinstance(work_types["name"], str)
    assert task_1
    assert task_2

    # Check if filters match resolvers
    response = await call_query(execute_gql, ids=[task_1["id"]], withHazards=True)
    assert len(response) == 1
    response_task_1 = response[0]

    response = await call_query(execute_gql, ids=[task_2["id"]], withHazards=True)
    assert len(response) == 1
    response_task_2 = response[0]

    # resolvers are not ordered, order it to check data
    task_1["hazards"].sort(key=lambda i: i["id"])
    for hazard in task_1["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    response_task_1["hazards"].sort(key=lambda i: i["id"])
    for hazard in response_task_1["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    task_2["hazards"].sort(key=lambda i: i["id"])
    for hazard in task_2["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    response_task_2["hazards"].sort(key=lambda i: i["id"])
    for hazard in response_task_2["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])

    # Now check it
    assert response_task_1 == task_1
    assert response_task_2 == task_2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_duplicated_controls_query(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Make sure controls only return direct hazard relation
    If we have:
        task 1 -> hazard 1 -> control 1 + control 2
        task 2 -> hazard 1 -> control 1
        task 2 resolvers should only return "control 1"
    """

    # creating tenant and linking work type to the tenant
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id

    # creating library tasks with the work types
    task1_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    task2_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    await set_library_tasks_relations(
        db_session, [task1_id], [hazard1_id], [control1_id, control2_id]
    )
    await set_library_tasks_relations(
        db_session, [task2_id], [hazard1_id], [control1_id]
    )

    expected_task1_hazards = {hazard1_id}
    expected_task1_controls = {control1_id, control2_id}
    expected_task2_hazards = {hazard1_id}
    expected_task2_controls = {control1_id}

    # Check if all resolvers are defined
    tasks = await call_query(execute_gql, withHazards=True)
    assert tasks
    tasks_by_id = {i["id"]: i for i in tasks}

    testing_task1 = tasks_by_id[task1_id]
    assert expected_task1_hazards == {i["id"] for i in testing_task1["hazards"]}
    assert expected_task1_controls == {
        x["id"] for i in testing_task1["hazards"] for x in i["controls"]
    }
    testing_task2 = tasks_by_id[task2_id]
    assert expected_task2_hazards == {i["id"] for i in testing_task2["hazards"]}
    assert expected_task2_controls == {
        x["id"] for i in testing_task2["hazards"] for x in i["controls"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check library tasks order"""

    expected_order = list(await build_library_tasks_for_order_by(db_session))

    # No order
    tasks = await call_query(execute_gql, orderBy=None)
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert set(tasks_ids) == set(expected_order)

    tasks = await call_query(execute_gql, orderBy=[])
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert set(tasks_ids) == set(expected_order)

    for column, set_asc_order, set_desc_order in [
        ("NAME", asc_order, desc_order),
        ("CATEGORY", desc_order, asc_order),
    ]:
        # ASC
        tasks = await call_query(
            execute_gql, orderBy=[{"field": column, "direction": "ASC"}]
        )
        tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
        assert tasks_ids == set_asc_order(expected_order)

        # DESC
        tasks = await call_query(
            execute_gql, orderBy=[{"field": column, "direction": "DESC"}]
        )
        tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
        assert tasks_ids == set_desc_order(expected_order)

    # with multiple order by should match first
    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == expected_order

    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_order_by_with_2_columns(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check library tasks order with 2 columns"""

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id

    task_1 = str(
        (await LibraryTaskFactory.persist(db_session, name="1", category="4")).id
    )
    task_2 = str(
        (await LibraryTaskFactory.persist(db_session, name="1", category="3")).id
    )
    task_3 = str(
        (await LibraryTaskFactory.persist(db_session, name="2", category="2")).id
    )
    task_4 = str(
        (await LibraryTaskFactory.persist(db_session, name="2", category="1")).id
    )

    await WorkTypeTaskLinkFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"work_type_id": work_id, "task_id": task_1},
            {"work_type_id": work_id, "task_id": task_2},
            {"work_type_id": work_id, "task_id": task_3},
            {"work_type_id": work_id, "task_id": task_4},
        ],
    )

    # ASC
    expected_order = [task_2, task_1, task_4, task_3]
    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "CATEGORY", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == expected_order

    # DESC
    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "CATEGORY", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == desc_order(expected_order)

    # Mix
    expected_order = [task_1, task_2, task_3, task_4]
    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "CATEGORY", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == expected_order

    # Category first
    expected_order = [task_4, task_3, task_2, task_1]
    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "CATEGORY", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hazards_and_controls_order_on_tasks_library(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check hazards and controls order on library tasks query"""

    expected_order = list(await build_library_tasks_for_order_by(db_session))
    expected_hazards_order = list(await build_library_hazards_for_order_by(db_session))
    expected_controls_order = list(
        await build_library_controls_for_order_by(db_session)
    )
    await set_library_tasks_relations(
        db_session, expected_order, expected_hazards_order, expected_controls_order
    )

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    for direction, set_order in available_order:
        for hazard_direction, hazard_set_order in available_order:
            for control_direction, control_set_order in available_order:
                tasks = await call_query(
                    execute_gql,
                    withHazards=True,
                    orderBy=[{"field": "NAME", "direction": direction}],
                    hazardsOrderBy=[{"field": "NAME", "direction": hazard_direction}],
                    controlsOrderBy=[{"field": "NAME", "direction": control_direction}],
                )
                tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
                assert set_order(tasks_ids) == expected_order
                for task in tasks:
                    if task["id"] in expected_order:
                        hazards_ids = [
                            i["id"]
                            for i in task["hazards"]
                            if i["id"] in expected_hazards_order
                        ]
                        assert hazard_set_order(hazards_ids) == expected_hazards_order
                        for hazard in task["hazards"]:
                            controls_ids = [
                                i["id"]
                                for i in hazard["controls"]
                                if i["id"] in expected_controls_order
                            ]
                            assert (
                                control_set_order(controls_ids)
                                == expected_controls_order
                            )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    expected_order = sorted(
        await build_library_tasks_for_order_by(db_session, name="cenas")
    )

    tasks = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks if i["id"] in expected_order]
    assert tasks_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_query_only_includes_recommended_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available hazards for a given library task"""
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id
    task_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    hazard2_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding only hazard1 as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard1_id,
        library_control_id=control_id,
    )  # hazard2 already exists, but is not recommended and shouldn't be listed

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if only the recommended hazard is listed for now
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard1_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control_id)

    # also adding hazard2 as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard2_id,
        library_control_id=control_id,
    )  # hazard2 exists and is recommended, so it should also be listed

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if both recommended hazards are listed
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 2
    assert task["hazards"][0]["id"] in [str(hazard1_id), str(hazard2_id)]
    if task["hazards"][0]["id"] == str(hazard1_id):
        assert task["hazards"][1]["id"] == str(hazard2_id)
    elif task["hazards"][0]["id"] == str(hazard2_id):
        assert task["hazards"][1]["id"] == str(hazard1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe
    assert task["hazards"][0]["controls"][0]["id"] == str(control_id)
    assert task["hazards"][1]["controls"][0]["id"] == str(control_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_query_only_includes_recommended_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available controls for a given library task"""
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id

    task_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    hazard_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding control1 only as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard_id,
        library_control_id=control1_id,
    )  # control2 already exists, but is not recommended and shouldn't be listed

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if only the recommended control is listed for now
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control1_id)

    # also adding control2 as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard_id,
        library_control_id=control2_id,
    )  # control2 already exists and is recommended, so it should also be listed

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if both recommended controls are listed
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 2
    assert hazard["controls"][0]["id"] in [str(control1_id), str(control2_id)]
    if hazard["controls"][0]["id"] == str(control1_id):
        assert hazard["controls"][1]["id"] == str(control2_id)
    elif hazard["controls"][0]["id"] == str(control2_id):
        assert hazard["controls"][1]["id"] == str(control1_id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_recommended_hazards_list_updated_upon_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available hazards for a given library task"""

    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id
    task_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    hazard2_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding both hazards and controls as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard1_id,
        library_control_id=control_id,
    )
    temp_recommendation = await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard2_id,
        library_control_id=control_id,
    )

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if both recommended hazards are listed
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 2
    assert task["hazards"][0]["id"] in [str(hazard1_id), str(hazard2_id)]
    if task["hazards"][0]["id"] == str(hazard1_id):
        assert task["hazards"][1]["id"] == str(hazard2_id)
    elif task["hazards"][0]["id"] == str(hazard2_id):
        assert task["hazards"][1]["id"] == str(hazard1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe
    assert task["hazards"][0]["controls"][0]["id"] == str(control_id)
    assert task["hazards"][1]["controls"][0]["id"] == str(control_id)

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if only the recommended hazard is listed now
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard1_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_recommended_controls_list_updated_upon_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available controls for a given library task"""
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    work_id = (
        await WorkTypeFactory.tenant_work_type(session=db_session, tenant_id=tenant_id)
    ).id

    task_id = str(
        (await LibraryTaskFactory.with_work_type_link(db_session, work_id)).id
    )
    hazard_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding both controls as recommended for task
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard_id,
        library_control_id=control1_id,
    )
    temp_recommendation = await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=task_id,
        library_hazard_id=hazard_id,
        library_control_id=control2_id,
    )

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if both recommended controls are listed
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 2
    assert hazard["controls"][0]["id"] in [str(control1_id), str(control2_id)]
    if hazard["controls"][0]["id"] == str(control1_id):
        assert hazard["controls"][1]["id"] == str(control2_id)
    elif hazard["controls"][0]["id"] == str(control2_id):
        assert hazard["controls"][1]["id"] == str(control1_id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    tasks = await call_query(execute_gql, ids=[task_id], withHazards=True)

    # Check if only the recommended control is listed now
    assert tasks
    task = tasks[0]
    assert uuid.UUID(task["id"])
    assert task["id"] == str(task_id)
    assert task["hazards"]
    assert len(task["hazards"]) == 1
    hazard = task["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control1_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_tenant_wise_worktypes(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    """Simple library tasks check"""
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # create Library Task linked to 2 worktypes

    library_task = await LibraryTaskFactory.persist(db_session)
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[0].id, library_task.id
    )
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[1].id, library_task.id
    )
    expected_work_types = sorted([str(work_type.id) for work_type in work_types])

    # create another worktype not linked to any tenant and link it with the library task
    new_work_type = await WorkTypeFactory.persist(db_session)
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, new_work_type.id, library_task.id
    )
    # Check if only 2 work types are shown in result which are linked to tenant
    task = await call_query(execute_gql, ids=[library_task.id])
    assert len(task) == 1
    assert len(task[0]["workTypes"]) == 2
    result_work_type_ids = sorted(
        [work_type["id"] for work_type in task[0]["workTypes"]]
    )
    assert result_work_type_ids == expected_work_types


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_standard_operating_procedures(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # Arrange
    # create 2 Standard Operating Procedures linked to default tenant
    default_tenant_id = (await TenantFactory.default_tenant(db_session)).id
    extra_tenant_id = (await TenantFactory.extra_tenant(db_session)).id
    default_work_id = (
        await WorkTypeFactory.tenant_work_type(
            session=db_session,
            tenant_id=default_tenant_id,
        )
    ).id
    extra_work_id = (
        await WorkTypeFactory.tenant_work_type(
            session=db_session,
            tenant_id=extra_tenant_id,
        )
    ).id
    standard_operating_procedures = (
        await StandardOperatingProcedureFactory.persist_many(db_session, size=2)
    )
    # create Library Task linked to the Standard Operating Procedures and work type
    library_task = await LibraryTaskFactory.persist(db_session)
    await WorkTypeTaskLinkFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "work_type_id": default_work_id,
                "task_id": library_task.id,
            },
            {
                "work_type_id": extra_work_id,
                "task_id": library_task.id,
            },
        ],
    )
    await LibraryTaskStandardOperatingProcedureFactory.link(
        db_session, library_task.id, standard_operating_procedures[0].id
    )
    await LibraryTaskStandardOperatingProcedureFactory.link(
        db_session, library_task.id, standard_operating_procedures[1].id
    )
    # create another Standard Operating Procedure not linked to other tenant and link it with the Library Task
    other_standard_operating_procedure = (
        await StandardOperatingProcedureFactory.persist(
            db_session, default_tenant=False
        )
    )
    await LibraryTaskStandardOperatingProcedureFactory.link(
        db_session, library_task.id, other_standard_operating_procedure.id
    )

    # Act
    tasks = await call_query(
        execute_gql, ids=[library_task.id], withStandardOperatingProcedures=True
    )

    # Assert
    # Check if only 2 work types are shown in result which are linked to tenant
    assert len(tasks) == 1, tasks
    assert len(tasks[0]["workTypes"]) == 1, tasks
    assert len(tasks[0]["standardOperatingProcedures"]) == 2, tasks
    assert sorted(
        [
            (
                standard_operating_procedure["id"],
                standard_operating_procedure["name"],
                standard_operating_procedure["link"],
            )
            for standard_operating_procedure in tasks[0]["standardOperatingProcedures"]
        ]
    ) == sorted(
        [
            (
                str(standard_operating_procedure.id),
                standard_operating_procedure.name,
                standard_operating_procedure.link,
            )
            for standard_operating_procedure in standard_operating_procedures
        ]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_with_tenant_settings_with_correct_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # create Library Task linked to 2 work types
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[0].id, library_tasks[0].id
    )
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[1].id, library_tasks[1].id
    )

    await TenantLibraryTaskSettingsFactory.persist(
        db_session,
        library_task_id=library_tasks[0].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_task_name",
    )

    task = await call_linked_query(execute_gql, tenantWorkTypeIds=[work_types[0].id])
    assert len(task) == 1
    assert len(task[0]["workTypes"]) == 1
    assert task[0]["workTypes"][0]["id"] == str(work_types[0].id)

    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id).in_(
                    [library_tasks[0].id, library_tasks[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_with_tenant_settings_with_incorrect_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[1].id, library_tasks[1].id
    )

    await TenantLibraryTaskSettingsFactory.persist(
        db_session,
        library_task_id=library_tasks[0].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_task_name",
    )

    task = await call_linked_query(execute_gql, tenantWorkTypeIds=[work_types[0].id])
    assert len(task) == 0

    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id).in_(
                    [library_tasks[0].id, library_tasks[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_with_tenant_settings_with_incorrect_tenant_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # create Library Task linked to 2 work types
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=2)
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[0].id, library_tasks[0].id
    )
    await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
        db_session, work_types[1].id, library_tasks[1].id
    )

    await TenantLibraryTaskSettingsFactory.persist(
        db_session,
        library_task_id=library_tasks[1].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_task_name",
    )

    task = await call_linked_query(execute_gql, tenantWorkTypeIds=[work_types[0].id])
    assert len(task) == 0

    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeTaskLink).where(
                col(WorkTypeTaskLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibraryTaskSettings).where(
                col(TenantLibraryTaskSettings.library_task_id).in_(
                    [library_tasks[0].id, library_tasks[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeTaskLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibraryTaskSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_and_work_type_linked_library_tasks_with_ids_filter(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # Create tenant and work types
    tenant = await TenantFactory.default_tenant(db_session)
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # Create library tasks
    library_tasks = await LibraryTaskFactory.persist_many(db_session, size=3)

    # Create tenant settings for each task if they don't exist
    for task in library_tasks:
        existing_settings = (
            await db_session.exec(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.tenant_id == tenant.id,
                    TenantLibraryTaskSettings.library_task_id == task.id,
                )
            )
        ).first()
        if not existing_settings:
            await TenantLibraryTaskSettingsFactory.persist(
                db_session,
                library_task_id=task.id,
                tenant_id=tenant.id,
            )

    # Link all tasks to both work types
    for task in library_tasks:
        for work_type in work_types:
            await WorkTypeTaskLinkFactory.get_or_create_work_type_task_link(
                db_session, work_type.id, task.id
            )

    # Test without ids filter - should return all tasks
    tasks = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[work_types[0].id, work_types[1].id]
    )
    assert len(tasks) == 3

    # Test with ids filter - should return only specified tasks
    tasks = await call_linked_query(
        execute_gql,
        tenantWorkTypeIds=[work_types[0].id, work_types[1].id],
        ids=[str(library_tasks[0].id), str(library_tasks[1].id)],
    )
    assert len(tasks) == 2
    task_ids = {task["id"] for task in tasks}
    assert task_ids == {str(library_tasks[0].id), str(library_tasks[1].id)}

    # Test with non-existent id - should return empty result
    tasks = await call_linked_query(
        execute_gql,
        tenantWorkTypeIds=[work_types[0].id, work_types[1].id],
        ids=[str(uuid.uuid4())],
    )
    assert len(tasks) == 0

    # Clean up
    for task in library_tasks:
        settings = (
            await db_session.exec(
                select(TenantLibraryTaskSettings).where(
                    TenantLibraryTaskSettings.library_task_id == task.id
                )
            )
        ).all()
        if settings:
            await TenantLibraryTaskSettingsFactory.delete_many(db_session, settings)

    for work_type in work_types:
        links = (
            await db_session.exec(
                select(WorkTypeTaskLink).where(
                    WorkTypeTaskLink.work_type_id == work_type.id
                )
            )
        ).all()
        if links:
            await WorkTypeTaskLinkFactory.delete_many(db_session, links)

    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibraryTaskFactory.delete_many(db_session, library_tasks)
