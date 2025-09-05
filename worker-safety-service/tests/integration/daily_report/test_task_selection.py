import copy
import datetime
import uuid

import pytest

from tests.db_data import DBData
from tests.factories import LocationFactory, TaskFactory, WorkPackageFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.daily_report.helpers import build_report_data, execute_report
from worker_safety_service.models import AsyncSession, Task


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_task_selection(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    report_request, _, location = await build_report_data(db_session)

    # Add as empty is allowed
    report_request["taskSelection"] = {"selectedTasks": []}
    response = await execute_report(execute_gql, report_request)
    report_1 = uuid.UUID(response["id"])
    assert response["sections"]["taskSelection"]["selectedTasks"] == []

    # Create
    task1: Task = await TaskFactory.persist(db_session, location_id=location.id)
    task_1_data = {"name": "Task 1", "riskLevel": "HIGH", "id": str(task1.id)}
    report_request["taskSelection"]["selectedTasks"] = [task_1_data]
    response = await execute_report(execute_gql, report_request)
    report_2 = uuid.UUID(response["id"])
    assert report_2 != report_1
    assert response["sections"]["taskSelection"]["selectedTasks"] == [task_1_data]
    sections = (await db_data.daily_report(report_2)).sections_to_pydantic()
    assert sections
    assert sections.task_selection
    assert len(sections.task_selection.selected_tasks) == 1
    db_report_2_task = sections.task_selection.selected_tasks[0]
    assert str(db_report_2_task.id) == task_1_data["id"]
    assert db_report_2_task.name == task_1_data["name"]
    assert db_report_2_task.risk_level.name == task_1_data["riskLevel"]

    # Update
    task2: Task = await TaskFactory.persist(db_session, location_id=location.id)
    task_2_data = {"name": "Task 2", "riskLevel": "LOW", "id": str(task2.id)}
    report_request["id"] = str(report_2)
    report_request["taskSelection"]["selectedTasks"].insert(
        0, task_2_data
    )  # Order is kept
    response = await execute_report(execute_gql, report_request)
    report_3 = uuid.UUID(response["id"])
    assert report_3 == report_2
    assert response["sections"]["taskSelection"]["selectedTasks"] == [
        task_2_data,
        task_1_data,
    ]
    sections = (await db_data.daily_report(report_3)).sections_to_pydantic()
    assert sections
    assert sections.task_selection
    assert len(sections.task_selection.selected_tasks) == 2
    db_report_3_task_2 = sections.task_selection.selected_tasks[0]
    assert str(db_report_3_task_2.id) == task_2_data["id"]
    assert db_report_3_task_2.name == task_2_data["name"]
    assert db_report_3_task_2.risk_level.name == task_2_data["riskLevel"]
    db_report_3_task_1 = sections.task_selection.selected_tasks[1]
    assert str(db_report_3_task_1.id) == task_1_data["id"]
    assert db_report_3_task_1.name == task_1_data["name"]
    assert db_report_3_task_1.risk_level.name == task_1_data["riskLevel"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_duplicated_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)
    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    task_data = {"id": str(task.id), "name": "Task", "riskLevel": "HIGH"}
    report_request["taskSelection"] = {"selectedTasks": [task_data]}

    # Check duplicated tasks on create
    create_request = copy.deepcopy(report_request)
    create_request["taskSelection"]["selectedTasks"].append(task_data)
    response = await execute_report(execute_gql, create_request, raw=True)
    assert response.json().get("errors"), "No duplicated error raised on create"

    # Create
    response = await execute_report(execute_gql, report_request)
    report_request["id"] = response["id"]

    # Check duplicated tasks on update
    assert report_request["id"]
    update_request = copy.deepcopy(report_request)
    update_request["taskSelection"]["selectedTasks"].append(task_data)
    response = await execute_report(execute_gql, update_request, raw=True)
    assert response.json().get("errors"), "No duplicated error raised on update"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_invalid_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    report_request, _, location = await build_report_data(db_session)
    task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    report_request["taskSelection"] = {
        "selectedTasks": [{"id": str(task.id), "name": "Task", "riskLevel": "HIGH"}]
    }

    # Check invalid tasks on create
    invalid_request = copy.deepcopy(report_request)
    invalid_request["taskSelection"]["selectedTasks"].append(
        {"id": str(uuid.uuid4()), "name": "Task", "riskLevel": "HIGH"}
    )
    response = await execute_report(execute_gql, invalid_request, raw=True)
    assert response.json().get("errors"), "No invalid task error raised on create"

    # Check task not added to project location on create
    project = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=project.id)
    invalid_task: Task = await TaskFactory.persist(db_session, location_id=location.id)
    invalid_request = copy.deepcopy(report_request)
    invalid_request["taskSelection"]["selectedTasks"].append(
        {"id": str(invalid_task.id), "name": "Task", "riskLevel": "HIGH"}
    )
    response = await execute_report(execute_gql, invalid_request, raw=True)
    assert response.json().get("errors"), "No invalid task error raised on create"

    # Create
    response = await execute_report(execute_gql, report_request)
    report_request["id"] = response["id"]

    # Check invalid tasks on create
    invalid_request = copy.deepcopy(report_request)
    invalid_request["taskSelection"]["selectedTasks"].append(
        {"id": str(uuid.uuid4()), "name": "Task", "riskLevel": "HIGH"}
    )
    response = await execute_report(execute_gql, invalid_request, raw=True)
    assert response.json().get("errors"), "No invalid task error raised on update"

    # Check task not added to project location on create
    project = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=project.id)
    invalid_task = await TaskFactory.persist(db_session, location_id=location.id)
    invalid_request = copy.deepcopy(report_request)
    invalid_request["taskSelection"]["selectedTasks"].append(
        {"id": str(invalid_task.id), "name": "Task", "riskLevel": "HIGH"}
    )
    response = await execute_report(execute_gql, invalid_request, raw=True)
    assert response.json().get("errors"), "No invalid task error raised on update"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_daily_report_mutation_with_archived_task_selection(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    # Arrange
    report_request, _, location = await build_report_data(db_session)
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    task: Task = await TaskFactory.persist(
        db_session, location_id=location.id, archived_at=now
    )
    task_data = {"name": "Task 1", "riskLevel": "HIGH", "id": str(task.id)}
    report_request.update({"taskSelection": {"selectedTasks": [task_data]}})

    # Act
    response = await execute_report(execute_gql, report_request)

    # Assert
    assert response["sections"]["taskSelection"]["selectedTasks"] == [task_data]
