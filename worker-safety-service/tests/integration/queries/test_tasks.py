import uuid
from collections import defaultdict
from typing import Any

import pytest

from tests.factories import (
    LibraryTaskFactory,
    LibraryTaskRecommendationsFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import valid_project_request
from tests.integration.queries.helpers import (
    asc_order,
    build_library_controls_for_order_by,
    build_library_hazards_for_order_by,
    build_library_tasks_for_order_by,
    create_tasks_for_sort,
    desc_order,
    set_library_tasks_relations,
)
from worker_safety_service.models import AsyncSession

tasks_query = {
    "operation_name": "tasks",
    "query": """
query tasks ($locationId: UUID, $withHazards: Boolean! = false, $orderBy: [TaskOrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tasks(locationId: $locationId, orderBy: $orderBy) {
    id
    name
    libraryTask { id name }
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        controls (orderBy: $controlsOrderBy) {
            id
            name
        }
    }
  }
}
""",
}


async def call_query(
    execute_gql: ExecuteGQL, location_id: str | uuid.UUID, **kwargs: Any
) -> list[dict]:
    kwargs["locationId"] = location_id
    data = await execute_gql(**tasks_query, variables=kwargs)
    tasks: list[dict] = data["tasks"]
    return tasks


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_no_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks no order"""

    location_id, expected_order = await create_tasks_for_sort(db_session)
    tasks = await call_query(execute_gql, location_id, orderBy=None)
    tasks_ids = [i["id"] for i in tasks]
    assert set(tasks_ids) == set(expected_order)

    tasks = await call_query(execute_gql, location_id, orderBy=[])
    tasks_ids = [i["id"] for i in tasks]
    assert set(tasks_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_asc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks asc order"""

    location_id, expected_order = await create_tasks_for_sort(db_session)
    tasks = await call_query(
        execute_gql, location_id, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order

    # NAME have different order of other fields
    expected_order = list(reversed(expected_order))
    for field in ["CATEGORY", "START_DATE", "END_DATE", "STATUS"]:
        tasks = await call_query(
            execute_gql, location_id, orderBy=[{"field": field, "direction": "ASC"}]
        )
        tasks_ids = [i["id"] for i in tasks]
        assert tasks_ids == expected_order, f"for {field}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_desc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks desc order"""

    location_id, expected_order = await create_tasks_for_sort(db_session)
    tasks = await call_query(
        execute_gql, location_id, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == desc_order(expected_order)

    # NAME have different order of other fields
    expected_order = list(reversed(expected_order))
    for field in ["CATEGORY", "START_DATE", "END_DATE", "STATUS"]:
        tasks = await call_query(
            execute_gql, location_id, orderBy=[{"field": field, "direction": "DESC"}]
        )
        tasks_ids = [i["id"] for i in tasks]
        assert tasks_ids == desc_order(expected_order), f"for {field}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_order_by_location_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks order by project location"""

    task_1 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                location_kwargs={"name": "á 1"},
            )
        )[0].id
    )
    task_2 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                location_kwargs={"name": "A 2"},
            )
        )[0].id
    )
    task_3 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                location_kwargs={"name": "a 3"},
            )
        )[0].id
    )

    # ASC
    expected_order = [task_1, task_2, task_3]
    data = await execute_gql(
        **tasks_query,
        variables={"orderBy": [{"field": "PROJECT_LOCATION_NAME", "direction": "ASC"}]},
    )
    tasks_ids = [i["id"] for i in data["tasks"] if i["id"] in expected_order]
    assert tasks_ids == expected_order

    # DESC
    data = await execute_gql(
        **tasks_query,
        variables={
            "orderBy": [{"field": "PROJECT_LOCATION_NAME", "direction": "DESC"}]
        },
    )
    tasks_ids = [i["id"] for i in data["tasks"] if i["id"] in expected_order]
    assert tasks_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_order_by_project_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks order by project"""

    task_1 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                project_kwargs={"name": "á 1"},
            )
        )[0].id
    )
    task_2 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                project_kwargs={"name": "A 2"},
            )
        )[0].id
    )
    task_3 = str(
        (
            await TaskFactory.with_project_and_location(
                db_session,
                project_kwargs={"name": "a 3"},
            )
        )[0].id
    )

    # ASC
    expected_order = [task_1, task_2, task_3]
    data = await execute_gql(
        **tasks_query,
        variables={"orderBy": [{"field": "PROJECT_NAME", "direction": "ASC"}]},
    )
    tasks_ids = [i["id"] for i in data["tasks"] if i["id"] in expected_order]
    assert tasks_ids == expected_order

    # DESC
    data = await execute_gql(
        **tasks_query,
        variables={"orderBy": [{"field": "PROJECT_NAME", "direction": "DESC"}]},
    )
    tasks_ids = [i["id"] for i in data["tasks"] if i["id"] in expected_order]
    assert tasks_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_multiple_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check tasks multiple duplicated order"""

    location_id, expected_order = await create_tasks_for_sort(db_session)
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order

    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_library_order_by_with_2_columns(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check library tasks order with 2 columns"""

    project_data = await valid_project_request(db_session, persist=True)
    location_id = project_data["locations"][0]["id"]

    task_1 = str(
        (
            await TaskFactory.persist(
                db_session,
                location_id=location_id,
                library_task_id=(
                    await LibraryTaskFactory.persist(db_session, name="1", category="4")
                ).id,
            )
        ).id
    )
    task_2 = str(
        (
            await TaskFactory.persist(
                db_session,
                location_id=location_id,
                library_task_id=(
                    await LibraryTaskFactory.persist(db_session, name="1", category="3")
                ).id,
            )
        ).id
    )
    task_3 = str(
        (
            await TaskFactory.persist(
                db_session,
                location_id=location_id,
                library_task_id=(
                    await LibraryTaskFactory.persist(db_session, name="2", category="2")
                ).id,
            )
        ).id
    )
    task_4 = str(
        (
            await TaskFactory.persist(
                db_session,
                location_id=location_id,
                library_task_id=(
                    await LibraryTaskFactory.persist(db_session, name="2", category="1")
                ).id,
            )
        ).id
    )

    # ASC
    expected_order = [task_2, task_1, task_4, task_3]
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "CATEGORY", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order

    # DESC
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "CATEGORY", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == desc_order(expected_order)

    # Mix
    expected_order = [task_1, task_2, task_3, task_4]
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "CATEGORY", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order

    # Category first
    expected_order = [task_4, task_3, task_2, task_1]
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "CATEGORY", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hazards_and_controls_order_on_tasks(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check hazards and controls order on tasks query"""

    project_data = await valid_project_request(db_session, persist=True)
    location_id = project_data["locations"][0]["id"]
    library_task_ids = await build_library_tasks_for_order_by(db_session)
    size = len(library_task_ids)
    db_tasks = await TaskFactory.persist_many(
        db_session,
        location_id=location_id,
        per_item_kwargs=[{"library_task_id": i} for i in library_task_ids],
    )
    library_hazard_ids = await build_library_hazards_for_order_by(db_session, size=size)
    hazards = await TaskHazardFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "task_id": db_tasks[int(idx / size)].id,
                "library_hazard_id": library_hazard_id,
            }
            for idx, library_hazard_id in enumerate(library_hazard_ids)
        ],
    )
    library_control_ids = await build_library_controls_for_order_by(
        db_session, size=len(library_hazard_ids)
    )
    controls = await TaskControlFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "task_hazard_id": hazards[int(idx / size)].id,
                "library_control_id": library_control_id,
            }
            for idx, library_control_id in enumerate(library_control_ids)
        ],
    )

    expected_order = [str(i.id) for i in db_tasks]
    expected_hazards_order = defaultdict(list)
    for hazard in hazards:
        expected_hazards_order[str(hazard.task_id)].append(str(hazard.id))
    expected_controls_order = defaultdict(list)
    for control in controls:
        expected_controls_order[str(control.task_hazard_id)].append(str(control.id))

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    for direction, set_order in available_order:
        for hazard_direction, hazard_set_order in available_order:
            for control_direction, control_set_order in available_order:
                tasks = await call_query(
                    execute_gql,
                    location_id,
                    withHazards=True,
                    orderBy=[{"field": "NAME", "direction": direction}],
                    hazardsOrderBy=[{"field": "NAME", "direction": hazard_direction}],
                    controlsOrderBy=[{"field": "NAME", "direction": control_direction}],
                )
                tasks_ids = [i["id"] for i in tasks]
                assert set_order(tasks_ids) == expected_order
                for task_item in tasks:
                    hazards_ids = [i["id"] for i in task_item["hazards"]]
                    assert (
                        hazard_set_order(hazards_ids)
                        == expected_hazards_order[task_item["id"]]
                    )
                    for hazard_item in task_item["hazards"]:
                        controls_ids = [i["id"] for i in hazard_item["controls"]]
                        assert (
                            control_set_order(controls_ids)
                            == expected_controls_order[hazard_item["id"]]
                        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location_id, expected_order = await create_tasks_for_sort(db_session, name="cenas")
    tasks = await call_query(
        execute_gql,
        location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    tasks_ids = [i["id"] for i in tasks]
    assert tasks_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_includes_even_nonrecommended_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of hazards for a given library task regardless of availability"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, lh2, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lt1, _, _ = await build_library_tasks_for_order_by(
        db_session
    )  # IDs for library tasks
    await set_library_tasks_relations(
        db_session, [lt1], [lh1], [lc1, lc2]
    )  # library task 1 only has recommendations for a single hazard with 2 controls

    # set up Task and its hazards and controls
    task_1 = await TaskFactory.persist(
        db_session,
        library_task_id=lt1,
    )
    location_id = task_1.location_id
    hazard_1 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh1
    )
    hazard_2 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh2
    )  # task_1 will have a hazard of type lh2, even though it's not recommended
    control_11 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc1
    )
    control_12 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc2
    )
    control_21 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_2.id, library_control_id=lc1
    )

    queried_tasks = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if both hazards are listed
    assert queried_tasks
    queried_task = queried_tasks[0]
    assert uuid.UUID(queried_task["id"])
    assert queried_task["id"] == str(task_1.id)
    assert queried_task["hazards"]
    assert len(queried_task["hazards"]) == 2

    if queried_task["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_task["hazards"][0]
        second_hazard = queried_task["hazards"][1]
    elif queried_task["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_task["hazards"][1]
        second_hazard = queried_task["hazards"][0]
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 2
    assert first_hazard["controls"][0]["id"] in [str(control_11.id), str(control_12.id)]
    assert first_hazard["controls"][1]["id"] in [str(control_11.id), str(control_12.id)]
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_21.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_task_includes_even_nonrecommended_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of controls for a given library task regardless of availability"""

    # set up library and recommendations
    lc1, lc2, lc3 = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, _, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lt1, _, _ = await build_library_tasks_for_order_by(
        db_session
    )  # IDs for library tasks
    await set_library_tasks_relations(
        db_session, [lt1], [lh1], [lc1, lc2]
    )  # library task 1 has recommendations of hazard 1 with controls 1 and 2

    # set up Tasks and their hazards and controls
    task_1 = await TaskFactory.persist(
        db_session,
        task_condition_id=lt1,
    )
    location_id = task_1.location_id
    hazard_1 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh1
    )  # will have all recommended controls
    control11 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc1
    )
    control12 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc2
    )

    task_2 = await TaskFactory.persist(
        db_session,
        location_id=location_id,
        library_task_id=lt1,
    )
    hazard_2 = await TaskHazardFactory.persist(
        db_session, task_id=task_2.id, library_hazard_id=lh1
    )  # won't have all recommended controls, and also one that is not recommended
    control21 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_2.id, library_control_id=lc1
    )
    control23 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_2.id, library_control_id=lc3
    )  # not recommended for library hazard 1

    queried_tasks = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if both hazards list all their controls
    assert queried_tasks
    assert len(queried_tasks)
    if queried_tasks[0]["id"] == str(task_1.id):
        first_task = queried_tasks[0]
        second_task = queried_tasks[1]
    elif queried_tasks[0]["id"] == str(task_2.id):
        first_task = queried_tasks[1]
        second_task = queried_tasks[0]

    assert len(first_task["hazards"]) == 1
    first_hazard = first_task["hazards"][0]
    assert len(second_task["hazards"]) == 1
    second_hazard = second_task["hazards"][0]

    assert first_hazard["id"] == str(hazard_1.id)
    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 2
    assert first_hazard["controls"][0]["id"] in [str(control11.id), str(control12.id)]
    assert first_hazard["controls"][1]["id"] in [str(control11.id), str(control12.id)]
    assert len(second_hazard["controls"]) == 2
    assert second_hazard["controls"][0]["id"] in [str(control21.id), str(control23.id)]
    assert second_hazard["controls"][1]["id"] in [str(control21.id), str(control23.id)]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_still_includes_hazards_after_recommendation_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of hazards for a given library task regardless of recommendation availability"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, lh2, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lt1, _, _ = await build_library_tasks_for_order_by(
        db_session
    )  # IDs for library tasks
    # adding both hazards and controls as recommended for task 1
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=lt1,
        library_hazard_id=lh1,
        library_control_id=lc1,
    )
    temp_recommendation = await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=lt1,
        library_hazard_id=lh2,
        library_control_id=lc2,
    )

    # set up Task with its recommended hazards and controls
    task_1 = await TaskFactory.persist(
        db_session,
        library_task_id=lt1,
    )
    location_id = task_1.location_id
    hazard_1 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh1
    )
    control_1 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc1
    )
    hazard_2 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh2
    )
    control_2 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_2.id, library_control_id=lc2
    )

    queried_tasks = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if both hazards are listed
    assert queried_tasks
    queried_task = queried_tasks[0]
    assert uuid.UUID(queried_task["id"])
    assert queried_task["id"] == str(task_1.id)
    assert queried_task["hazards"]
    assert len(queried_task["hazards"]) == 2

    if queried_task["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_task["hazards"][0]
        second_hazard = queried_task["hazards"][1]
    elif queried_task["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_task["hazards"][1]
        second_hazard = queried_task["hazards"][0]
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 1
    assert first_hazard["controls"][0]["id"] == str(control_1.id)
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_2.id)

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    # Check if task1's hazards are both still listed
    assert queried_tasks
    queried_task = queried_tasks[0]
    assert uuid.UUID(queried_task["id"])
    assert queried_task["id"] == str(task_1.id)
    assert queried_task["hazards"]
    assert len(queried_task["hazards"]) == 2

    if queried_task["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_task["hazards"][0]
        second_hazard = queried_task["hazards"][1]
    elif queried_task["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_task["hazards"][1]
        second_hazard = queried_task["hazards"][0]
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 1
    assert first_hazard["controls"][0]["id"] == str(control_1.id)
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_2.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_still_includes_controls_after_recommendation_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of controls for a given library task regardless of recommendation availability"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, _, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lt1, _, _ = await build_library_tasks_for_order_by(
        db_session
    )  # IDs for library tasks
    # adding both hazards and controls as recommended for task 1
    await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=lt1,
        library_hazard_id=lh1,
        library_control_id=lc1,
    )
    temp_recommendation = await LibraryTaskRecommendationsFactory.persist(
        db_session,
        library_task_id=lt1,
        library_hazard_id=lh1,
        library_control_id=lc2,
    )

    # set up Task with its recommended hazards and controls
    task_1 = await TaskFactory.persist(
        db_session,
        library_task_id=lt1,
    )
    location_id = task_1.location_id
    hazard_1 = await TaskHazardFactory.persist(
        db_session, task_id=task_1.id, library_hazard_id=lh1
    )
    control_1 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc1
    )
    control_2 = await TaskControlFactory.persist(
        db_session, task_hazard_id=hazard_1.id, library_control_id=lc2
    )

    queried_tasks = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if the task's hazard lists both controls
    assert queried_tasks
    assert len(queried_tasks) == 1
    queried_task = queried_tasks[0]
    assert len(queried_task["hazards"]) == 1
    queried_hazard = queried_task["hazards"][0]
    assert len(queried_hazard["controls"]) == 2
    if queried_hazard["controls"][0]["id"] == str(control_1.id):
        assert queried_hazard["controls"][1]["id"] == str(control_2.id)
    elif queried_hazard["controls"][0]["id"] == str(control_2.id):
        assert queried_hazard["controls"][1]["id"] == str(control_1.id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    # Check if the task's hazard still lists both controls, even the one that is no longer recommended
    assert queried_tasks
    assert len(queried_tasks) == 1
    queried_task = queried_tasks[0]
    assert len(queried_task["hazards"]) == 1
    queried_hazard = queried_task["hazards"][0]
    assert len(queried_hazard["controls"]) == 2
    if queried_hazard["controls"][0]["id"] == str(control_1.id):
        assert queried_hazard["controls"][1]["id"] == str(control_2.id)
    elif queried_hazard["controls"][0]["id"] == str(control_2.id):
        assert queried_hazard["controls"][1]["id"] == str(control_1.id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case
