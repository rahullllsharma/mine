from datetime import datetime, timezone
from uuid import UUID

import pytest

from tests.factories import LocationFactory, TaskFactory, TaskHazardFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, Location, Task, TaskHazard

project_with_locations_and_tasks_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($projectId: UUID!) {
  project(projectId: $projectId) {
    id name locations { id tasks { id hazards { id controls { id } } } }
  }
}
""",
}

all_locations_with_tasks_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery {
  projectLocations {
    id tasks { id hazards { id controls { id } } }
  }
}
""",
}

all_tasks_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery {tasks { id hazards { id controls { id } }}}
""",
}

task_hazards_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($id: UUID!) {
  taskHazards(id: $id) { id controls { id } }}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tasks_query_with_archiving(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a few tasks, archives one, and ensures the archived never leaves.

    Tests fetching a few different ways:
    - `project(projectId)` - fetch a single project
    - `projectLocation` - fetch a single project
    - `tasks` - fetch all tasks
    - `task(id)` - fetch a task by id
    """

    location: Location = await LocationFactory.persist(db_session)
    tasks: list[Task] = await TaskFactory.persist_many(
        db_session, size=3, location_id=location.id
    )
    to_archive = tasks[1]
    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()
    expected_task_ids = set(
        map(lambda x: str(x.id), filter(lambda x: not x.id == to_archive.id, tasks))
    )

    ###########################################################
    # project_with_locations_and_tasks_query

    data = await execute_gql(
        **project_with_locations_and_tasks_query,
        variables={"projectId": str(location.project_id)},
    )
    assert data["project"]["id"] == str(location.project_id)  # sanity check
    fetched_tasks = data["project"]["locations"][0]["tasks"]
    fetched_task_ids: set[UUID] = {i["id"] for i in fetched_tasks}

    assert len(fetched_tasks) == 2
    assert expected_task_ids == fetched_task_ids

    ###########################################################
    # all_locations_with_tasks_query

    data = await execute_gql(**all_locations_with_tasks_query)
    fetched_locs = data["projectLocations"]
    loc = list(filter(lambda x: x["id"] == str(location.id), fetched_locs))[0]
    fetched_tasks = loc["tasks"]
    fetched_task_ids = {i["id"] for i in fetched_tasks}

    assert len(fetched_tasks) == 2
    assert expected_task_ids == fetched_task_ids

    ###########################################################
    # all_tasks_query

    data = await execute_gql(**all_tasks_query)
    fetched_tasks = data["tasks"]
    fetched_task_ids = {i["id"] for i in fetched_tasks}

    assert str(to_archive.id) not in fetched_task_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_task_hazards_query_with_archiving(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a few hazards on a task, archives one, and ensures the archived never leaves.

    Tests fetching a few different ways:
    - `project(projectId)` - fetch a single project
    - `projectLocation` - fetch a single project
    - `tasks` - fetch all tasks
    - `task(id)` - fetch a task by id
    - `taskHazards(id)` - fetch a task's hazards by id
    """

    location: Location = await LocationFactory.persist(db_session)
    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    hazards: list[TaskHazard] = await TaskHazardFactory.persist_many(
        db_session, task_id=task.id, size=3
    )
    to_archive = hazards[1]
    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()
    expected_hazard_ids = set(
        map(lambda x: str(x.id), filter(lambda x: not x.id == to_archive.id, hazards))
    )

    ###########################################################
    # project_with_locations_and_tasks_query

    data = await execute_gql(
        **project_with_locations_and_tasks_query,
        variables={"projectId": str(location.project_id)},
    )
    assert data["project"]["id"] == str(location.project_id)  # sanity check
    fetched = data["project"]["locations"][0]["tasks"][0]["hazards"]
    fetched_ids: set[UUID] = {i["id"] for i in fetched}

    assert len(fetched) == 2
    assert expected_hazard_ids == fetched_ids

    ###########################################################
    # all_locations_with_tasks_query

    data = await execute_gql(**all_locations_with_tasks_query)
    fetched_locs = data["projectLocations"]
    loc = list(filter(lambda x: x["id"] == str(location.id), fetched_locs))[0]
    fetched = loc["tasks"][0]["hazards"]
    fetched_ids = {i["id"] for i in fetched}

    assert len(fetched) == 2
    assert expected_hazard_ids == fetched_ids

    ###########################################################
    # all_tasks_query

    data = await execute_gql(**all_tasks_query)
    fetched_tasks = data["tasks"]
    our_task = list(filter(lambda x: x["id"] == str(task.id), fetched_tasks))[0]
    fetched_ids = {i["id"] for i in our_task["hazards"]}

    assert len(fetched_ids) == 2
    assert expected_hazard_ids == fetched_ids
