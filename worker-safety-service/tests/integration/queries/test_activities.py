import uuid
from datetime import date

import pytest
from faker import Faker

from tests.factories import (
    ActivityFactory,
    ActivitySupervisorLinkFactory,
    CrewFactory,
    LibraryActivityTypeFactory,
    SupervisorFactory,
    TaskFactory,
    TenantFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

activities_by_location_query = """
query TestLocationActivities($locationId: UUID!) {
    projectLocations(id: $locationId) {
        id
        name
        activities {
            id,
            name,
            status,
            startDate,
            endDate
        }
    }
}
"""

ordered_activities = """
query TestActivityOrder($orderBy: [OrderBy!]){
  activities(orderBy: $orderBy) {
    name
  }
}
"""

ordered_activities_by_location = """
query TestActivityOrderByLocation($orderBy: [OrderBy!], $id: UUID!){
  projectLocations(id: $id) {
    activities(orderBy: $orderBy) {
      name
    }
  }
}
"""

activities_by_location_query_with_date_filter = """
query TestLocationActivities($locationId: UUID!, $date: Date) {
    projectLocations(id: $locationId) {
        id
        name
        activities(date: $date) {
            id,
            name,
            status,
            startDate,
            endDate
        }
    }
}
"""

activities_query_by_id = """
query TestActivites($id: UUID!) {
    activities(id: $id) {
        id,
        name,
        isCritical,
        criticalDescription,
        status,
        startDate,
        endDate
        crew {
            id
            externalKey
        }
        libraryActivityType {
            id
            name
        }
        supervisors {
            id
            externalKey
        }
    }
}
"""

activities_query_by_location = """
query TestActivites($locationId: UUID!) {
    activities(locationId: $locationId) {
        id,
        name,
        isCritical,
        criticalDescription,
        status,
        startDate,
        endDate
    }
}
"""

activities_query_by_id_with_task_count = """
query TestActivites($id: UUID!) {
    activities(id: $id) {
        id,
        name,
        status,
        startDate,
        endDate,
        taskCount
    }
}
"""


activities_query_by_location_with_date_filter = """
query TestActivites($locationId: UUID!, $date: Date) {
    activities(locationId: $locationId, date: $date) {
        id,
        name,
        status,
        startDate,
        endDate
    }
}
"""

critical_activity_within_given_date_range = """
query TestCriticalActivity($locationId: UUID, $startDate:Date!, $endDate:Date!) {
  projectLocations(id: $locationId) {
    dailySnapshots(dateRange: {startDate: $startDate, endDate: $endDate}) {
      date
      isCritical
    }
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_order_by(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"name": "Activity"}
    )
    await ActivityFactory.persist_many(db_session, size=3, location_id=location.id)

    activities_asc = await execute_gql(
        operation_name="TestActivityOrder",
        query=ordered_activities,
        variables={"orderBy": {"field": "NAME", "direction": "ASC"}},
    )
    activities_desc = await execute_gql(
        operation_name="TestActivityOrder",
        query=ordered_activities,
        variables={"orderBy": {"field": "NAME", "direction": "DESC"}},
    )

    # check the list of all activities ordered by name asc
    # against the reversed list ordered by desc
    assert [a.get("name") for a in activities_asc["activities"]] == [
        a.get("name") for a in activities_desc["activities"][::-1]
    ]

    loc_activities_asc = await execute_gql(
        operation_name="TestActivityOrderByLocation",
        query=ordered_activities_by_location,
        variables={
            "orderBy": {"field": "NAME", "direction": "ASC"},
            "id": str(location.id),
        },
    )
    loc_activities_desc = await execute_gql(
        operation_name="TestActivityOrderByLocation",
        query=ordered_activities_by_location,
        variables={
            "orderBy": {"field": "NAME", "direction": "DESC"},
            "id": str(location.id),
        },
    )
    assert [
        a.get("name") for a in loc_activities_asc["projectLocations"][0]["activities"]
    ] == [
        a.get("name")
        for a in loc_activities_desc["projectLocations"][0]["activities"][::-1]
    ]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_for_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should fetch all activities within a location"""

    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"name": "New Activity"}
    )

    response = await execute_gql(
        operation_name="TestLocationActivities",
        query=activities_by_location_query,
        variables={"locationId": str(location.id)},
    )

    project_location_data = response["projectLocations"][0]

    assert project_location_data["id"] == str(location.id)
    assert project_location_data["activities"]

    activity_data = project_location_data["activities"][0]

    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_for_location_not_in_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should return an empty list when activities are not within date range"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Missing Activity",
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )

    response = await execute_gql(
        operation_name="TestLocationActivities",
        query=activities_by_location_query_with_date_filter,
        variables={"locationId": str(location.id), "date": date(2022, 11, 2)},
    )

    project_location_data = response["projectLocations"][0]

    assert project_location_data["id"] == str(location.id)
    assert project_location_data["activities"] == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_critical_activity_for_given_date(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should return an Critical Activity criticality for every input date list"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Critical Activity",
            "is_critical": True,
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )

    response = await execute_gql(
        operation_name="TestCriticalActivity",
        query=critical_activity_within_given_date_range,
        variables={
            "locationId": str(location.id),
            "startDate": date(2022, 11, 2),
            "endDate": date(2022, 11, 5),
        },
    )
    print(response)
    assert all(
        snapshot["isCritical"] is False
        for snapshot in response["projectLocations"][0]["dailySnapshots"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_critical_activity_for_date_criticality_true(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should return an Critical Activity criticality for every input date list"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Critical Activity",
            "is_critical": True,
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )

    response = await execute_gql(
        operation_name="TestCriticalActivity",
        query=critical_activity_within_given_date_range,
        variables={
            "startDate": date(2022, 10, 5),
            "endDate": date(2022, 10, 15),
            "locationId": str(location.id),
        },
    )
    assert all(
        snapshot["isCritical"] is True
        for snapshot in response["projectLocations"][0]["dailySnapshots"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should fetch all activities by location"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"name": "Another Activity"}
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_location,
        variables={"locationId": str(location.id)},
    )

    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["isCritical"] == activity.is_critical
    assert activity_data["criticalDescription"] == activity.critical_description


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activity_with_critical_and_description_field(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should fetch an activity by id"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={"name": "Another Activity"},
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )

    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["isCritical"] == activity.is_critical
    assert activity_data["criticalDescription"] == activity.critical_description


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activity_with_updated_critical_and_description_field(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should fetch an activity by id"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "is_critical": True,
            "critical_description": "Updated Description",
        },
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )

    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["isCritical"] is True
    assert activity_data["criticalDescription"] == str(activity.critical_description)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activity(execute_gql: ExecuteGQL, db_session: AsyncSession) -> None:
    """Should fetch an activity by id"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"name": "Another Activity"}
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )

    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_not_within_date_range(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should return an empty list because no activities within date range"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_location_with_date_filter,
        variables={"locationId": str(location.id), "date": date(2022, 11, 2)},
    )

    activity_data = response["activities"]

    assert activity_data == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_with_task_count(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Should return an activity along with a count of how many tasks it has"""
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )
    tasks = await TaskFactory.persist_many(db_session, size=2, activity_id=activity.id)

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id_with_task_count,
        variables={"id": str(activity.id)},
    )
    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["taskCount"] == len(tasks)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_with_crew(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "start_date": date(2022, 10, 1),
            "end_date": date(2022, 11, 1),
        },
    )
    crew = await CrewFactory.persist(db_session)

    # Update it on db because we don't have a mutation yet
    activity.crew_id = crew.id
    await db_session.commit()

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )
    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["crew"]["id"] == str(crew.id)
    assert activity_data["crew"]["externalKey"] == crew.external_key


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_with_activity_type(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(db_session, tenant.id)
    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "library_activity_type_id": activity_type.id,
        },
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )
    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["libraryActivityType"]["id"] == str(activity_type.id)
    assert activity_data["libraryActivityType"]["name"] == activity_type.name

    # If activity type don't belong to the tenant (shouldn't happen), we still send it
    other_tenant = await TenantFactory.persist(db_session)
    activity_type = await LibraryActivityTypeFactory.with_link(
        db_session, other_tenant.id
    )
    (activity, project, location) = await ActivityFactory.with_project_and_location(
        db_session,
        activity_kwargs={
            "name": "Another Activity",
            "library_activity_type_id": activity_type.id,
        },
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )
    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)
    assert activity_data["libraryActivityType"]["id"] == str(activity_type.id)
    assert activity_data["libraryActivityType"]["name"] == activity_type.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_activities_with_supervisors(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    fake = Faker()
    supervisor1_ex_key = fake.name() + str(uuid.uuid4())
    supervisor2_ex_key = fake.name() + str(uuid.uuid4())
    supervisor1 = await SupervisorFactory.persist(
        db_session, external_key=supervisor1_ex_key
    )
    supervisor2 = await SupervisorFactory.persist(
        db_session, external_key=supervisor2_ex_key
    )
    (
        activity,
        project,
        location,
    ) = await ActivityFactory.with_project_and_location(
        db_session, activity_kwargs={"name": "New Activity"}
    )

    await ActivitySupervisorLinkFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"activity_id": activity.id, "supervisor_id": supervisor1.id},
            {"activity_id": activity.id, "supervisor_id": supervisor2.id},
        ],
    )

    response = await execute_gql(
        operation_name="TestActivites",
        query=activities_query_by_id,
        variables={"id": str(activity.id)},
    )
    activity_data = response["activities"][0]

    assert activity_data
    assert activity_data["id"] == str(activity.id)
    assert activity_data["name"] == str(activity.name)

    supervisor1_data = activity_data["supervisors"][0]

    assert supervisor1_data["id"] == str(supervisor1.id)
    assert supervisor1_data["externalKey"] == supervisor1_ex_key

    supervisor2_data = activity_data["supervisors"][1]

    assert supervisor2_data["id"] == str(supervisor2.id)
    assert supervisor2_data["externalKey"] == supervisor2_ex_key
