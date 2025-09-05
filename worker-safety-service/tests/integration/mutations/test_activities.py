import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Union

import pytest
from faker import Faker
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlmodel import select

from tests.factories import (
    ActivityFactory,
    CrewFactory,
    LibraryActivityTypeFactory,
    LibraryTaskFactory,
    LocationFactory,
    SupervisorFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    gql_activity,
    gql_control,
    gql_hazard,
    update_configuration,
)
from worker_safety_service.dal.configurations import (
    ACTIVITY_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.models import (
    Activity,
    ActivityStatus,
    ActivitySupervisorLink,
    AsyncSession,
    Location,
    Supervisor,
    Task,
    TaskControl,
    TaskHazard,
)


async def fetch_activity(session: AsyncSession, id: Union[str, uuid.UUID]) -> Activity:
    statement = select(Activity).where(Activity.id == id)
    return (await session.exec(statement)).one()


async def fetch_tasks(
    session: AsyncSession, activity_id: Union[str, uuid.UUID]
) -> list[Task]:
    statement = select(Task).where(Task.activity_id == activity_id)
    return (await session.exec(statement)).all()


async def fetch_hazards(
    session: AsyncSession, task_id: Union[str, uuid.UUID]
) -> list[TaskHazard]:
    statement = select(TaskHazard).where(TaskHazard.task_id == task_id)
    return (await session.exec(statement)).all()


async def fetch_controls(
    session: AsyncSession, hazard_id: Union[str, uuid.UUID]
) -> list[TaskControl]:
    statement = select(TaskControl).where(TaskControl.task_hazard_id == hazard_id)
    return (await session.exec(statement)).all()


async def fetch_activity_supervisors(
    session: AsyncSession, activity_id: Union[str, uuid.UUID]
) -> list[Supervisor]:
    statement = (
        select(Supervisor)
        .join(
            ActivitySupervisorLink,
            onclause=Supervisor.id == ActivitySupervisorLink.supervisor_id,
        )
        .where(ActivitySupervisorLink.activity_id == activity_id)
    )

    return (await session.exec(statement)).all()


create_activity_mutation = {
    "operation_name": "CreateActivity",
    "query": """
mutation CreateActivity($activity: CreateActivityInput!) {
  activity: createActivity(activityData: $activity) {
    id
    name
    status
    isCritical
    criticalDescription
    startDate
    endDate,
    crew {
      id
    }
    libraryActivityType {
      id
    }
  }
}
""",
}

edit_activity_mutation = {
    "operation_name": "EditActivity",
    "query": """
mutation EditActivity($activity: EditActivityInput!) {
  activity: editActivity(activityData: $activity) {
    id
    name
    status
    isCritical
    criticalDescription
    startDate
    endDate,
    crew {
      id
    }
    libraryActivityType {
      id
    }
  }
}
""",
}

archive_activity_mutation = {
    "operation_name": "DeleteActivity",
    "query": """
mutation DeleteActivity($id: UUID!) {
  activity: deleteActivity(id: $id)
}
""",
}

add_supervisor_to_activity_mutation = {
    "operation_name": "AddSupervisorToActivity",
    "query": """
mutation AddSupervisorToActivity($activityId: UUID!, $supervisorId: UUID!) {
    result: addSupervisorToActivity(activityId: $activityId, supervisorId: $supervisorId)
}
    """,
}

remove_supervisor_from_activity_mutation = {
    "operation_name": "RemoveSupervisorFromActivity",
    "query": """
mutation RemoveSupervisorFromActivity($activityId: UUID!, $supervisorId: UUID!) {
    result: removeSupervisorFromActivity(activityId: $activityId, supervisorId: $supervisorId)
}
    """,
}

add_tasks_to_activity = {
    "operation_name": "addTasksToActivity",
    "query": """
    mutation addTasksToActivity($id:UUID!,$newTasks:AddActivityTasksInput!){
  addTasksToActivity(id:$id,newTasks:$newTasks){
    id
    name
    tasks{
      id
      name
    }
  }
}
""",
}

remove_tasks_from_activity = {
    "operation_name": "removeTasksFromActivity",
    "query": """
mutation removeTasksFromActivity($id:UUID!,$taskIds:RemoveActivityTasksInput!){
  removeTasksFromActivity(id:$id,taskIdsToBeRemoved:$taskIds){
    id
    name
    tasks{
      id
      name
    }
  }
}
    """,
}
################################################################################
# Add a activity to a location
################################################################################

TEST_DATE = date.today()

NOT_FOUND_ID = "00000000-0000-0000-0000-000000000000"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {"start_date": TEST_DATE, "end_date": TEST_DATE + timedelta(days=1)},
        {"start_date": TEST_DATE, "end_date": TEST_DATE},
    ],
)
async def test_create_activity(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)

    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)
    activity: Activity = ActivityFactory.build(
        library_activity_type_id=activity_type.id
    )
    extra_task = await TaskFactory.persist(db_session)

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]

    fetched = await fetch_activity(db_session, activity_data["id"])
    assert fetched
    assert fetched.status == activity.status
    assert fetched.start_date == params["start_date"]
    assert fetched.end_date == params["end_date"]
    assert fetched.library_activity_type_id == activity_type.id

    tasks = await fetch_tasks(db_session, activity_data["id"])
    assert len(tasks) == 1
    fetched_task = tasks[0]
    assert fetched_task.location_id == fetched.location_id
    assert fetched_task.status == fetched.status
    assert fetched_task.start_date == fetched.start_date
    assert fetched_task.end_date == fetched.end_date
    assert fetched_task.library_task_id == extra_task.library_task_id

    error = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [],
            }
        },
        raw=True,
    )
    errors = error.json()["errors"]
    assert errors[0]["message"] == "Activity must be created with tasks"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE + timedelta(days=1),
            "is_critical": True,
            "critical_description": "New Critical Description",
        },
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE,
            "is_critical": False,
            "critical_description": None,
        },
    ],
)
async def test_create_activity_with_critical_field_and_description(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)

    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)
    activity: Activity = ActivityFactory.build(
        library_activity_type_id=activity_type.id
    )
    extra_task = await TaskFactory.persist(db_session)

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "isCritical": params["is_critical"],
                "criticalDescription": params["critical_description"],
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]

    fetched = await fetch_activity(db_session, activity_data["id"])
    assert fetched
    assert fetched.status == activity.status
    assert fetched.start_date == params["start_date"]
    assert fetched.end_date == params["end_date"]
    assert fetched.library_activity_type_id == activity_type.id
    assert fetched.critical_description == params["critical_description"]
    assert fetched.is_critical == params["is_critical"]

    tasks = await fetch_tasks(db_session, activity_data["id"])
    assert len(tasks) == 1
    fetched_task = tasks[0]
    assert fetched_task.location_id == fetched.location_id
    assert fetched_task.status == fetched.status
    assert fetched_task.start_date == fetched.start_date
    assert fetched_task.end_date == fetched.end_date
    assert fetched_task.library_task_id == extra_task.library_task_id

    error = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [],
            }
        },
        raw=True,
    )
    errors = error.json()["errors"]
    assert errors[0]["message"] == "Activity must be created with tasks"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_without_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Make sure at least one task is defined for an activity
    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)
    location = await LocationFactory.persist(db_session)
    activity: Activity = ActivityFactory.build(
        library_activity_type_id=activity_type.id
    )

    response = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id"})),
                "locationId": location.id,
                "tasks": [],
            }
        },
        raw=True,
    )
    data = response.json()
    assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_activity_with_invalid_activity_type(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location = await LocationFactory.persist(db_session)
    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)
    library_task = await LibraryTaskFactory.persist(db_session)
    activity: Activity = ActivityFactory.build(
        library_activity_type_id=activity_type.id
    )
    variables = {
        "activity": {
            **gql_activity(activity.dict(exclude={"id"})),
            "locationId": location.id,
            "tasks": [
                {
                    "libraryTaskId": library_task.id,
                    "hazards": [],
                }
            ],
        }
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables=variables,
    )
    activity_id = data["activity"]["id"]
    assert activity_id

    # On create: Using same base data, create with invalid activity type
    invalid_tenant = await TenantFactory.persist(db_session)
    invalid_type = await LibraryActivityTypeFactory.with_link(
        db_session, invalid_tenant.id
    )
    variables["activity"]["libraryActivityTypeId"] = invalid_type.id
    response = await execute_gql(
        **create_activity_mutation,
        variables=variables,
        raw=True,
    )
    data = response.json()
    assert not data.get("data")
    assert data.get("errors")

    # On edit: test invalid activity type
    variables["activity"]["id"] = activity_id
    variables["activity"].pop("locationId")
    variables["activity"].pop("tasks")
    response = await execute_gql(
        **edit_activity_mutation,
        variables=variables,
        raw=True,
    )
    data = response.json()
    assert not data["data"].get("activity")
    assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_invalid_dates(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)
    library_task = await LibraryTaskFactory.persist(db_session)
    activity = ActivityFactory.build()
    variables = {
        "activity": {
            **gql_activity(activity.dict(exclude={"id"})),
            "locationId": location.id,
            "tasks": [
                {
                    "libraryTaskId": library_task.id,
                    "hazards": [],
                }
            ],
        }
    }

    # Valid creation
    data = await execute_gql(**create_activity_mutation, variables=variables)
    assert data["activity"]["id"]

    # Valid start date
    variables["activity"]["startDate"] = str(work_package.start_date)
    data = await execute_gql(**create_activity_mutation, variables=variables)
    assert data["activity"]["id"]
    assert data["activity"]["startDate"] == variables["activity"]["startDate"]

    # Valid end date
    variables["activity"]["endDate"] = str(work_package.end_date)
    data = await execute_gql(**create_activity_mutation, variables=variables)
    assert data["activity"]["id"]
    assert data["activity"]["endDate"] == variables["activity"]["endDate"]

    # Invalid start date
    variables["activity"]["startDate"] = str(
        work_package.start_date - timedelta(days=1)
    )
    response = await execute_gql(
        **create_activity_mutation, variables=variables, raw=True
    )
    data = response.json()
    assert not data["data"]
    assert data.get("errors")

    # Invalid end date
    variables["activity"]["startDate"] = str(work_package.start_date)
    variables["activity"]["endDate"] = str(work_package.end_date + timedelta(days=1))
    response = await execute_gql(
        **create_activity_mutation, variables=variables, raw=True
    )
    data = response.json()
    assert not data["data"]
    assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {"start_date": TEST_DATE, "end_date": TEST_DATE - timedelta(days=1)},
    ],
)
async def test_create_activity_fails(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()
    extra_task = await TaskFactory.persist(db_session)

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
        raw=True,
    )

    errors = data.json()["errors"]
    assert len(errors) > 0
    assert "Start date must be sooner than end date" in errors[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_archived_location(
    test_client: AsyncClient, db_session: AsyncSession
) -> None:
    """
    Asserts that an error is returned when a createActivity mutation is attempted on
    an archived project location.
    """
    location: Location = await LocationFactory.persist(db_session)
    location.archived_at = datetime.now(timezone.utc)
    await db_session.commit()

    activity: Activity = ActivityFactory.build()
    extra_task = await TaskFactory.persist(db_session)

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    post_data = {
        "operationName": create_activity_mutation["operation_name"],
        "query": create_activity_mutation["query"],
        "variables": jsonable_encoder(
            {
                "activity": {
                    **gql_activity(activity.dict(exclude={"id"})),
                    # use the archived location
                    "locationId": location.id,
                    "tasks": [new_task],
                }
            }
        ),
    }

    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "errors" in data
    messages = [x["message"] for x in data["errors"]]
    assert "Project location not found" in messages


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # extra models so we can use their relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id"})),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]

    fetched = await fetch_activity(db_session, activity_data["id"])
    assert fetched
    assert fetched.status == activity.status
    assert fetched.start_date == activity.start_date
    assert fetched.end_date == activity.end_date

    tasks = await fetch_tasks(db_session, activity_data["id"])
    assert len(tasks) == 1
    fetched_task = tasks[0]
    assert fetched_task.location_id == fetched.location_id
    assert fetched_task.status == fetched.status
    assert fetched_task.start_date == fetched.start_date
    assert fetched_task.end_date == fetched.end_date
    assert fetched_task.library_task_id == extra_task.library_task_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # extra models so we can use their relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)
    extra_hazard: TaskHazard = await TaskHazardFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()
    hazard: TaskHazard = TaskHazardFactory.build(is_applicable=True)

    new_hazard = {
        **gql_hazard(hazard.dict(exclude={"id", "library_hazard_id"})),
        "libraryHazardId": extra_hazard.library_hazard_id,
    }
    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [new_hazard],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id"})),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]

    fetched = await fetch_activity(db_session, activity_data["id"])
    assert fetched
    assert fetched.status == activity.status
    assert fetched.start_date == activity.start_date
    assert fetched.end_date == activity.end_date

    tasks = await fetch_tasks(db_session, activity_data["id"])
    assert len(tasks) == 1
    fetched_task = tasks[0]
    assert fetched_task.location_id == fetched.location_id
    assert fetched_task.status == fetched.status
    assert fetched_task.start_date == fetched.start_date
    assert fetched_task.end_date == fetched.end_date
    assert fetched_task.library_task_id == extra_task.library_task_id

    hazards = await fetch_hazards(db_session, fetched_task.id)
    assert len(hazards) == 1
    fetched_hazard = hazards[0]
    assert fetched_hazard.is_applicable == hazard.is_applicable
    assert fetched_hazard.library_hazard_id == extra_hazard.library_hazard_id
    assert fetched_hazard.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_hazard_and_control(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # extra models so we can use their relational data
    extra_activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)
    extra_hazard = await TaskHazardFactory.persist(db_session)
    extra_control = await TaskControlFactory.persist(db_session)

    activity = ActivityFactory.build()
    hazard = TaskHazardFactory.build(is_applicable=True)
    control = TaskControlFactory.build(is_applicable=True)

    new_hazard = {
        **gql_hazard(hazard.dict(exclude={"id", "library_hazard_id"})),
        "libraryHazardId": extra_hazard.library_hazard_id,
        "controls": [
            {
                **gql_control(control.dict(exclude={"id"})),
                "libraryControlId": extra_control.library_control_id,
            }
        ],
    }
    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [new_hazard],
    }
    data = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id"})),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]

    fetched = await fetch_activity(db_session, activity_data["id"])
    assert fetched
    assert fetched.location_id == extra_activity.location_id
    assert fetched.name == activity.name
    assert fetched.status == activity.status
    assert fetched.start_date == activity.start_date
    assert fetched.end_date == activity.end_date

    tasks = await fetch_tasks(db_session, activity_data["id"])
    assert len(tasks) == 1
    fetched_task = tasks[0]
    assert fetched_task.location_id == fetched.location_id
    assert fetched_task.status == fetched.status
    assert fetched_task.start_date == fetched.start_date
    assert fetched_task.end_date == fetched.end_date
    assert fetched_task.library_task_id == extra_task.library_task_id

    hazards = await fetch_hazards(db_session, fetched_task.id)
    assert len(hazards) == 1
    fetched_hazard = hazards[0]
    assert fetched_hazard.is_applicable == hazard.is_applicable
    assert fetched_hazard.library_hazard_id == extra_hazard.library_hazard_id
    assert fetched_hazard.position == 0

    controls = await fetch_controls(db_session, fetched_hazard.id)
    assert len(controls) == 1
    fetched_control = controls[0]
    assert fetched_control.is_applicable == control.is_applicable
    assert fetched_control.library_control_id == extra_control.library_control_id
    assert fetched_control.position == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_all_attributes_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    library_task = await LibraryTaskFactory.persist(db_session)
    activity = ActivityFactory.build(
        location_id=(await LocationFactory.persist(db_session)).id,
        crew_id=(await CrewFactory.persist(db_session)).id,
        library_activity_type_id=(
            await LibraryActivityTypeFactory.with_link(db_session, tenant_id)
        ).id,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        tenant_id,
        ACTIVITY_CONFIG,
        required_fields=None,  # Means all
    )

    activity_data = gql_activity(activity)
    activity_data["tasks"] = [
        {
            "libraryTaskId": library_task.id,
            "hazards": [],
        }
    ]
    data = await execute_gql(
        **create_activity_mutation,
        variables={"activity": activity_data},
    )
    assert data["activity"]["name"] == activity_data["name"]
    assert data["activity"]["crew"]["id"] == activity_data["crewId"]
    assert (
        data["activity"]["libraryActivityType"]["id"]
        == activity_data["libraryActivityTypeId"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_all_attributes_not_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    library_task = await LibraryTaskFactory.persist(db_session)
    activity = ActivityFactory.build(
        location_id=(await LocationFactory.persist(db_session)).id,
        crew_id=None,
        library_activity_type_id=None,
    ).dict(exclude={"id"})

    await update_configuration(
        configurations_manager,
        tenant_id,
        ACTIVITY_CONFIG,
        required_fields=[],
    )

    activity_data = gql_activity(activity)
    activity_data["tasks"] = [
        {
            "libraryTaskId": library_task.id,
            "hazards": [],
        }
    ]
    data = await execute_gql(
        **create_activity_mutation,
        variables={"activity": activity_data},
    )
    assert data["activity"]["name"] == activity_data["name"]
    assert data["activity"]["crew"] is None
    assert data["activity"]["libraryActivityType"] is None


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE + timedelta(days=1),
            "name": "Original Activity",
            "is_critical": True,
            "critical_description": "Original Critical Description",
        },
    ],
)
async def test_edit_activity(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)

    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": params["name"],
                "isCritical": params["is_critical"],
                "criticalDescription": params["critical_description"],
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )
    fetched = await fetch_activity(db_session, created_activity["activity"]["id"])
    assert fetched.library_activity_type_id is None

    updated_params = {
        "is_critical": False,
        "critical_description": "Updated Critical Description",
    }

    edited_activity = await execute_gql(
        **edit_activity_mutation,
        variables={
            "activity": {
                **gql_activity(
                    activity.dict(
                        exclude={"id", "start_date", "end_date", "location_id"}
                    )
                ),
                "id": created_activity["activity"]["id"],
                "name": "Edited Activity",
                "isCritical": updated_params["is_critical"],
                "criticalDescription": updated_params["critical_description"],
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": (params["start_date"] + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                ),
                "status": ActivityStatus.IN_PROGRESS.upper(),
                "libraryActivityTypeId": str(activity_type.id),
            }
        },
    )

    created_activity_data = created_activity["activity"]
    edited_activity_data = edited_activity["activity"]

    assert edited_activity_data is not None

    await db_session.refresh(fetched)
    assert str(fetched.id) == created_activity_data["id"]
    assert fetched.name == "Edited Activity"
    assert fetched.is_critical == edited_activity_data["isCritical"]
    assert fetched.critical_description == edited_activity_data["criticalDescription"]
    assert (
        str(ActivityStatus[fetched.status.name].value)
        == edited_activity_data["status"].lower()
    )
    assert str(fetched.start_date) == edited_activity_data["startDate"]
    assert str(fetched.end_date) == edited_activity_data["endDate"]
    assert fetched.library_activity_type_id == activity_type.id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE + timedelta(days=1),
            "name": "Original Activity",
        },
    ],
)
async def test_edit_activity_with_no_changes(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": params["name"],
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    edited_activity = await execute_gql(
        **edit_activity_mutation,
        variables={
            "activity": {
                **gql_activity(
                    activity.dict(
                        exclude={"id", "start_date", "end_date", "location_id"}
                    )
                ),
                "id": created_activity["activity"]["id"],
                "name": params["name"],
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
            }
        },
    )

    edited_activity_data = edited_activity["activity"]
    # Assert that when no changes are applied, endpoint returns None
    assert edited_activity_data is None

    original_activity_data = created_activity["activity"]
    fetched = await fetch_activity(db_session, original_activity_data["id"])

    # Assert original activity is unchanged
    assert fetched
    assert str(fetched.id) == original_activity_data["id"]
    assert fetched.name == original_activity_data["name"]
    assert (
        str(ActivityStatus[fetched.status.name].value)
        == original_activity_data["status"].lower()
    )
    assert str(fetched.start_date) == original_activity_data["startDate"]
    assert str(fetched.end_date) == original_activity_data["endDate"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_updates_task_dates(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": "Original Activity",
                "endDate": extra_activity.end_date,
                "startDate": extra_activity.start_date,
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )
    aid = created_activity["activity"]["id"]
    updated_task = (await fetch_tasks(db_session, aid))[0]

    dates = [
        {"start_date": extra_activity.start_date - timedelta(days=1)},
        {"end_date": extra_activity.end_date + timedelta(days=1)},
        {
            "start_date": extra_activity.start_date - timedelta(days=1),
            "end_date": extra_activity.end_date + timedelta(days=1),
        },
    ]
    for data in dates:
        start_date = data.get("start_date") or extra_activity.start_date
        end_date = data.get("end_date") or extra_activity.start_date
        await execute_gql(
            **edit_activity_mutation,
            variables={
                "activity": {
                    **gql_activity(
                        activity.dict(
                            exclude={"id", "start_date", "end_date", "location_id"}
                        )
                    ),
                    "id": aid,
                    "name": "Original Name",
                    "endDate": end_date.strftime("%Y-%m-%d"),
                    "startDate": start_date.strftime("%Y-%m-%d"),
                }
            },
        )
        await db_session.refresh(updated_task)

        assert updated_task.start_date == start_date
        assert updated_task.end_date == end_date


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE + timedelta(days=1),
            "name": "Original Activity",
        },
    ],
)
async def test_edit_activity_fail_when_date_is_in_past(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_task.library_task_id,
        "hazards": [],
    }
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": params["name"],
                "endDate": params["end_date"].strftime("%Y-%m-%d"),
                "startDate": params["start_date"].strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    try:
        edited_activity = await execute_gql(
            **edit_activity_mutation,
            variables={
                "activity": {
                    **gql_activity(
                        activity.dict(exclude={"id", "start_date", "end_date"})
                    ),
                    "id": created_activity["activity"]["id"],
                    "name": params["name"],
                    "endDate": params["end_date"].strftime("%Y-%m-%d"),
                    "startDate": (params["start_date"] - timedelta(days=10)).strftime(
                        "%Y-%m-%d"
                    ),
                },
            },
            raw=True,
        )
    except ValueError:
        errors = edited_activity.json()["errors"]
        assert len(errors) > 0
        assert "Start date must be sooner than end date" in errors[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "params",
    [
        {
            "start_date": TEST_DATE,
            "end_date": TEST_DATE + timedelta(days=1),
            "name": "Edited Activity",
        },
    ],
)
async def edit_activity_that_does_not_exist(
    execute_gql: ExecuteGQL, db_session: AsyncSession, params: dict
) -> None:
    activity: Activity = ActivityFactory.build()

    try:
        edited_activity = await execute_gql(
            **edit_activity_mutation,
            variables={
                "activity": {
                    **gql_activity(
                        activity.dict(exclude={"id", "start_date", "end_date"})
                    ),
                    "id": NOT_FOUND_ID,
                    "name": params["name"],
                    "endDate": params["end_date"].strftime("%Y-%m-%d"),
                    "startDate": params["start_date"].strftime("%Y-%m-%d"),
                }
            },
            raw=True,
        )
    except ValueError:
        errors = edited_activity.json()["errors"]
        assert len(errors) > 0
        assert "The activity is not found!" in errors[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_with_all_attributes_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    activity = await ActivityFactory.persist(db_session)

    await update_configuration(
        configurations_manager,
        tenant_id,
        ACTIVITY_CONFIG,
        required_fields=None,  # Means all
    )

    activity.crew_id = (await CrewFactory.persist(db_session)).id
    activity.library_activity_type_id = (
        await LibraryActivityTypeFactory.with_link(db_session, tenant_id)
    ).id
    activity_data = gql_activity(activity.dict(exclude={"location_id"}))
    data = await execute_gql(
        **edit_activity_mutation,
        variables={"activity": activity_data},
    )
    assert data["activity"]["name"] == activity_data["name"]
    assert data["activity"]["crew"]["id"] == activity_data["crewId"]
    assert (
        data["activity"]["libraryActivityType"]["id"]
        == activity_data["libraryActivityTypeId"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_with_all_attributes_not_required(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    activity = await ActivityFactory.persist(
        db_session,
        crew_id=(await CrewFactory.persist(db_session)).id,
        library_activity_type_id=(
            await LibraryActivityTypeFactory.with_link(db_session, tenant_id)
        ).id,
    )

    await update_configuration(
        configurations_manager,
        tenant_id,
        ACTIVITY_CONFIG,
        required_fields=[],
    )

    activity.crew_id = None
    activity.library_activity_type_id = None
    activity_data = gql_activity(activity.dict(exclude={"location_id"}))
    data = await execute_gql(
        **edit_activity_mutation,
        variables={"activity": activity_data},
    )
    assert data["activity"]["name"] == activity_data["name"]
    assert data["activity"]["crew"] is None
    assert data["activity"]["libraryActivityType"] is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_with_invalid_dates(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    work_package = await WorkPackageFactory.persist(db_session)
    location = await LocationFactory.persist(db_session, project_id=work_package.id)
    activity = await ActivityFactory.persist(db_session, location_id=location.id)
    variables = {"activity": gql_activity(activity.dict(exclude={"location_id"}))}

    # Valid start date
    variables["activity"]["startDate"] = str(work_package.start_date)
    data = await execute_gql(**edit_activity_mutation, variables=variables)
    assert data["activity"]["id"]
    assert data["activity"]["startDate"] == variables["activity"]["startDate"]

    # Valid end date
    variables["activity"]["endDate"] = str(work_package.end_date)
    data = await execute_gql(**edit_activity_mutation, variables=variables)
    assert data["activity"]["id"]
    assert data["activity"]["endDate"] == variables["activity"]["endDate"]

    # Invalid start date
    variables["activity"]["startDate"] = str(
        work_package.start_date - timedelta(days=1)
    )
    response = await execute_gql(
        **edit_activity_mutation, variables=variables, raw=True
    )
    data = response.json()
    assert not data["data"]["activity"]
    assert data.get("errors")

    # Invalid end date
    variables["activity"]["startDate"] = str(work_package.start_date)
    variables["activity"]["endDate"] = str(work_package.end_date + timedelta(days=1))
    response = await execute_gql(
        **edit_activity_mutation, variables=variables, raw=True
    )
    data = response.json()
    assert not data["data"]["activity"]
    assert data.get("errors")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_activity(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session, activity_id=extra_activity.id)

    response = await execute_gql(
        **archive_activity_mutation, variables={"id": extra_activity.id}
    )

    archived_activity = await fetch_activity(session=db_session, id=extra_activity.id)
    assert response["activity"]

    assert archived_activity
    assert archived_activity.id == extra_activity.id

    archived_tasks = await fetch_tasks(
        session=db_session, activity_id=extra_activity.id
    )
    assert len(archived_tasks) == 1
    archived_task = archived_tasks[0]
    assert archived_task
    assert archived_task.id == extra_task.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_activity_activity_not_found(
    execute_gql: ExecuteGQL,
) -> None:
    response = await execute_gql(
        **archive_activity_mutation, variables={"id": NOT_FOUND_ID}, raw=True
    )

    errors = response.json()["errors"]
    print("\nERRORS", errors)
    assert len(errors) > 0
    assert "The activity is not found!" in errors[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_supervisor_to_activity(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    fake = Faker()
    activity: Activity = await ActivityFactory.persist(db_session)
    supervisor = await SupervisorFactory.persist(db_session, external_key=fake.name())

    response = await execute_gql(
        **add_supervisor_to_activity_mutation,
        variables={
            "activityId": activity.id,
            "supervisorId": supervisor.id,
        },
    )

    assert response["result"]
    assert response["result"] is True

    linked_supervisors = await fetch_activity_supervisors(
        db_session, activity_id=activity.id
    )

    assert len(linked_supervisors) == 1
    assert linked_supervisors[0].id == supervisor.id
    assert linked_supervisors[0].external_key == supervisor.external_key


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_supervisor_from_activity(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    activity: Activity = await ActivityFactory.persist(db_session)
    supervisor = await SupervisorFactory.persist(
        db_session, external_key="Dr. Hendrickson"
    )

    add_response = await execute_gql(
        **add_supervisor_to_activity_mutation,
        variables={
            "activityId": activity.id,
            "supervisorId": supervisor.id,
        },
    )

    assert add_response["result"]
    assert add_response["result"] is True

    remove_response = await execute_gql(
        **remove_supervisor_from_activity_mutation,
        variables={
            "activityId": activity.id,
            "supervisorId": supervisor.id,
        },
    )

    assert remove_response["result"]
    assert remove_response["result"] is True

    linked_supervisors = await fetch_activity_supervisors(
        db_session, activity_id=activity.id
    )

    assert len(linked_supervisors) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_remove_none_existent_supervisor_from_activity(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    activity: Activity = await ActivityFactory.persist(db_session)

    with pytest.raises(Exception) as e:
        await execute_gql(
            **remove_supervisor_from_activity_mutation,
            variables={
                "activityId": activity.id,
                "supervisorId": NOT_FOUND_ID,
            },
        )
    e.match("This supervisor is not linked to this activity")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_with_new_tasks(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_tasks = await TaskFactory.persist_many(db_session, 4)

    activity: Activity = ActivityFactory.build()

    new_task = {
        "libraryTaskId": extra_tasks[0].library_task_id,
        "hazards": [],
    }
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": "Original Activity" + str(uuid.uuid4()),
                "isCritical": True,
                "criticalDescription": "Original Critical Description",
                "endDate": (TEST_DATE + timedelta(days=1)).strftime("%Y-%m-%d"),
                "startDate": TEST_DATE.strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )
    fetched = await fetch_activity(db_session, created_activity["activity"]["id"])
    assert fetched.library_activity_type_id is None
    assert len(fetched.tasks) == 1
    assert fetched.tasks[0].library_task_id == extra_tasks[0].library_task_id
    lib_task_ids = [t.library_task_id for t in extra_tasks]

    tasks_to_be_added = [
        {
            "libraryTaskId": et.library_task_id,
            "hazards": [],
        }
        for et in extra_tasks[1:]
    ]
    edited_activity = await execute_gql(
        **add_tasks_to_activity,
        variables={
            "id": created_activity["activity"]["id"],
            "newTasks": {"tasksToBeAdded": tasks_to_be_added},
        },
    )

    created_activity_data = created_activity["activity"]
    edited_activity_data = edited_activity["addTasksToActivity"]

    assert edited_activity_data is not None

    await db_session.refresh(fetched)
    assert str(fetched.id) == created_activity_data["id"]
    assert len(fetched.tasks) == 4
    for task in fetched.tasks:
        assert task.library_task_id in lib_task_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_remove_existing_task(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_tasks = await TaskFactory.persist_many(db_session, 4)

    activity: Activity = ActivityFactory.build()

    new_task = [
        {
            "libraryTaskId": et.library_task_id,
            "hazards": [],
        }
        for et in extra_tasks
    ]
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": "Original Activity" + str(uuid.uuid4()),
                "isCritical": True,
                "criticalDescription": "Original Critical Description",
                "endDate": (TEST_DATE + timedelta(days=1)).strftime("%Y-%m-%d"),
                "startDate": TEST_DATE.strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": new_task,
            }
        },
    )
    fetched = await fetch_activity(db_session, created_activity["activity"]["id"])
    assert fetched.library_activity_type_id is None
    assert len(fetched.tasks) == 4

    task_ids_to_be_deleted_lib_task_ids = [t.library_task_id for t in fetched.tasks[:2]]

    edited_activity = await execute_gql(
        **remove_tasks_from_activity,
        variables={
            "id": created_activity["activity"]["id"],
            "taskIds": {"taskIdsToBeRemoved": [str(t.id) for t in fetched.tasks[:2]]},
        },
    )

    created_activity_data = created_activity["activity"]
    edited_activity_data = edited_activity["removeTasksFromActivity"]

    assert edited_activity_data is not None

    await db_session.refresh(fetched)
    assert str(fetched.id) == created_activity_data["id"]
    assert len(fetched.tasks) == 2
    for task in fetched.tasks:
        assert task.library_task_id not in task_ids_to_be_deleted_lib_task_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_activity_remove_non_existent_task(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # create an extra activity so we can use its relational data
    extra_activity: Activity = await ActivityFactory.persist(db_session)
    extra_tasks = await TaskFactory.persist_many(db_session, 2)

    activity: Activity = ActivityFactory.build()

    new_task = [
        {
            "libraryTaskId": et.library_task_id,
            "hazards": [],
        }
        for et in extra_tasks
    ]
    created_activity = await execute_gql(
        **create_activity_mutation,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id", "start_date", "end_date"})),
                "name": "Original Activity" + str(uuid.uuid4()),
                "isCritical": True,
                "criticalDescription": "Original Critical Description",
                "endDate": (TEST_DATE + timedelta(days=1)).strftime("%Y-%m-%d"),
                "startDate": TEST_DATE.strftime("%Y-%m-%d"),
                "locationId": extra_activity.location_id,
                "tasks": new_task,
            }
        },
    )
    fetched = await fetch_activity(db_session, created_activity["activity"]["id"])
    assert fetched.library_activity_type_id is None
    assert len(fetched.tasks) == 2

    task_ids_to_be_deleted = [uuid.uuid4(), uuid.uuid4()]

    edited_activity = await execute_gql(
        **remove_tasks_from_activity,
        variables={
            "id": created_activity["activity"]["id"],
            "taskIds": {"taskIdsToBeRemoved": task_ids_to_be_deleted},
        },
    )

    created_activity_data = created_activity["activity"]
    edited_activity_data = edited_activity["removeTasksFromActivity"]

    assert edited_activity_data is not None

    await db_session.refresh(fetched)
    assert str(fetched.id) == created_activity_data["id"]
    assert len(fetched.tasks) == 2
