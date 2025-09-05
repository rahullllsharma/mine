import datetime
import uuid
from copy import deepcopy
from decimal import Decimal

import pytest

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    LocationFactory,
    ManagerUserFactory,
    SiteConditionControlFactory,
    SiteConditionFactory,
    SiteConditionHazardFactory,
    SupervisorUserFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    create_project,
    create_project_gql,
    create_project_mutation,
    edit_project_gql,
    edit_project_mutation,
    gql_location,
    gql_project,
    valid_project_location_request,
    valid_project_request,
)
from worker_safety_service.models import (
    AsyncSession,
    Location,
    SiteCondition,
    SiteConditionControl,
    SiteConditionHazard,
    Task,
    TaskControl,
    TaskHazard,
    WorkPackage,
)

################################################################################
# Add a location to a Project
################################################################################

# Scale we should support, meaning, it will keep same numbers up to this scale
LOCATION_GEOM_SCALE = 10

save_location_from_lat_lon_mutation = {
    "operation_name": "createLocationFromLatLon",
    "query": """
        mutation createLocationFromLatLon($gpsCoordinates: GPSCoordinatesInput!, $name: String!, $date: DateTime) {
            createLocationFromLatLon(gpsCoordinates: $gpsCoordinates, name: $name, date: $date) {
                id
        }
    }
    """,
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_location(execute_gql: ExecuteGQL, db_session: AsyncSession) -> None:
    project_data, data = await create_project(execute_gql, db_session)

    location_data = project_data["locations"][0]
    location = data["locations"][0]
    assert location["name"] == location_data["name"]
    assert location["supervisor"]["id"] == location_data["supervisorId"]
    assert {i["id"] for i in location["additionalSupervisors"]} == set(
        location_data["additionalSupervisors"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_invalid_location_lat_lon(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    project_data = await valid_project_request(db_session)
    location_data = project_data["locations"][0]
    location_data["longitude"] = 0

    # latitude is required
    location_data.pop("latitude")
    data = await create_project_gql(execute_gql, project_data, with_errors=True)
    assert data["errors"]

    # Invalid latitude
    for value in (
        "invalid",
        "90.000000001",
        "-90.000000001",
        90.000000001,
        -90.000000001,
    ):
        location_data["latitude"] = value
        data = await create_project_gql(execute_gql, project_data, with_errors=True)
        assert data["errors"]

    location_data["latitude"] = 0

    # longitude is required
    location_data.pop("longitude")
    data = await create_project_gql(execute_gql, project_data, with_errors=True)
    assert data["errors"]

    # Invalid longitude
    for value in (
        "invalid",
        "180.000000001",
        "-180.000000001",
        180.000000001,
        -180.000000001,
    ):
        location_data["longitude"] = value
        data = await create_project_gql(execute_gql, project_data, with_errors=True)
        assert data["errors"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(60)
async def test_add_location_lat_lon(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    project_data = await valid_project_request(db_session)
    location_data = project_data["locations"][0]
    data = await create_project_gql(execute_gql, project_data)
    assert data["locations"][0]["latitude"] == location_data["latitude"]
    assert data["locations"][0]["longitude"] == location_data["longitude"]

    for key in ("latitude", "longitude"):
        # It should keep same value if decimal have more than supported
        location_data[key] = Decimal("10." + "0" * LOCATION_GEOM_SCALE + "1")
        data = await create_project_gql(execute_gql, project_data)
        assert isinstance(data["locations"][0][key], str)
        db_location = await db_data.location(data["locations"][0]["id"])
        assert (
            str(getattr(db_location.geom, key))[: LOCATION_GEOM_SCALE + 3]
            == "10." + "0" * LOCATION_GEOM_SCALE
        )

        # It should keep the decimal
        location_data[key] = Decimal("10." + "0" * (LOCATION_GEOM_SCALE - 1) + "1")
        data = await create_project_gql(execute_gql, project_data)
        assert isinstance(data["locations"][0][key], str)
        assert data["locations"][0][key] == str(location_data[key])

        # It should always return Decimal str
        location_data[key] = 0
        data = await create_project_gql(execute_gql, project_data)
        assert data["locations"][0][key] == "0"
        db_location = await db_data.location(data["locations"][0]["id"])
        assert isinstance(getattr(db_location.geom, f"decimal_{key}"), Decimal)
        assert getattr(db_location.geom, key) == 0

        assert data["locations"][0][key] == "0"


################################################################################
# Edit a location's data
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_location_on_edit_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    project_data = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=1, archived_at=None
    )
    project_data["locations"] = [gql_location(loc) for loc in locations]
    first_location_id = project_data["locations"][0]["id"]

    # Add location
    location_data = await valid_project_location_request(db_session)
    project_data["locations"].append(location_data)
    data = await edit_project_gql(execute_gql, project_data)
    locations_by_id = {i["id"]: i for i in data["locations"]}
    assert len(locations_by_id) == 2
    assert locations_by_id.pop(first_location_id)
    location = locations_by_id.popitem()[1]
    assert location["name"] == location_data["name"]
    assert location["supervisor"]["id"] == location_data["supervisorId"]
    assert {i["id"] for i in location["additionalSupervisors"]} == set(
        location_data["additionalSupervisors"]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_location_on_edit_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    project_data = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=2, archived_at=None
    )
    project_data["locations"] = [gql_location(loc) for loc in locations]

    # Delete location
    keep_location_id = project_data["locations"][0]["id"]
    project_data["locations"].pop(1)["id"]  # location to delete
    data = await edit_project_gql(execute_gql, project_data)
    assert [i["id"] for i in data["locations"]] == [keep_location_id]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_location_data(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    project_data = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=2, archived_at=None
    )
    project_data["locations"] = [gql_location(loc) for loc in locations]

    # Edit data (only the first one)
    project_data["locations"][0].update(
        await valid_project_location_request(db_session)
    )
    data = await edit_project_gql(execute_gql, project_data)
    locations_by_id = {i["id"]: i for i in project_data["locations"]}
    assert set(locations_by_id.keys()) == {i["id"] for i in data["locations"]}
    for location in data["locations"]:
        location_data = locations_by_id[location["id"]]
        assert location["name"] == location_data["name"]
        assert location["supervisor"]["id"] == location_data["supervisorId"]
        assert {i["id"] for i in location["additionalSupervisors"]} == set(
            location_data["additionalSupervisors"]
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_supervisor(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin_id = (await AdminUserFactory.persist(db_session)).id
    manager_id = (await ManagerUserFactory.persist(db_session)).id

    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    pd = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=1, archived_at=None
    )
    pd["locations"] = [gql_location(loc) for loc in locations]
    for user_id in [admin_id, manager_id, uuid.uuid4()]:
        error_messages = [
            f"Not a supervisor {user_id}",
            f"Supervisor {user_id} not found",
        ]
        # Test create
        project_data = await valid_project_request(db_session)
        project_data["locations"][0]["supervisorId"] = user_id
        data = await execute_gql(
            **create_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any(msg in errors[0]["message"] for msg in error_messages)
        location_data = await valid_project_location_request(db_session)
        location_data["supervisorId"] = user_id
        project_data = deepcopy(pd)
        project_data["locations"].append(location_data)
        data = await execute_gql(
            **edit_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any(msg in errors[0]["message"] for msg in error_messages)

        # Test edit
        project_data["locations"][0]["supervisorId"] = user_id
        data = await execute_gql(
            **edit_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any(msg in errors[0]["message"] for msg in error_messages)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_additional_supervisors(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin_id = (await AdminUserFactory.persist(db_session)).id
    manager_id = (await ManagerUserFactory.persist(db_session)).id

    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    pd = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=1, archived_at=None
    )
    pd["locations"] = [gql_location(loc) for loc in locations]

    for user_id in [admin_id, manager_id, uuid.uuid4()]:
        error_messages = [
            f"Not a supervisor {user_id}",
            f"Supervisor {user_id} not found",
        ]

        # Test create
        project_data = await valid_project_request(db_session)
        project_data["locations"][0]["additionalSupervisors"] = [user_id]
        data = await execute_gql(
            **create_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any([msg in errors[0]["message"] for msg in error_messages])

        location_data = await valid_project_location_request(db_session)
        location_data["additionalSupervisors"] = [user_id]
        project_data = deepcopy(pd)
        project_data["locations"].append(location_data)
        data = await execute_gql(
            **edit_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any([msg in errors[0]["message"] for msg in error_messages])

        # Test edit
        project_data["locations"][0]["additionalSupervisors"] = [user_id]
        data = await execute_gql(
            **edit_project_mutation, variables={"project": project_data}, raw=True
        )
        errors = data.json().get("errors")
        assert errors
        assert any([msg in errors[0]["message"] for msg in error_messages])


@pytest.mark.asyncio
@pytest.mark.integration
async def test_duplicated_supervisors(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    supervisor_id = (await SupervisorUserFactory.persist(db_session)).id
    supervisor_2_id = (await SupervisorUserFactory.persist(db_session)).id

    # Test create
    project_data = await valid_project_request(db_session)
    project_data["locations"][0]["supervisorId"] = supervisor_id
    project_data["locations"][0]["additionalSupervisors"] = [supervisor_id]
    data = await execute_gql(
        **create_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_id} duplicated" in errors[0]["message"]

    project_data["locations"][0]["additionalSupervisors"] = [
        supervisor_2_id,
        supervisor_2_id,
    ]
    data = await execute_gql(
        **create_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_2_id} duplicated" in errors[0]["message"]

    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    pd = gql_project(project)
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=1, archived_at=None
    )
    pd["locations"] = [gql_location(loc) for loc in locations]

    location_data = await valid_project_location_request(db_session)
    location_data["supervisorId"] = supervisor_id
    location_data["additionalSupervisors"] = [supervisor_id]
    project_data = deepcopy(pd)
    project_data["locations"].append(location_data)
    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_id} duplicated" in errors[0]["message"]

    location_data["additionalSupervisors"] = [supervisor_2_id, supervisor_2_id]
    project_data["locations"].append(location_data)
    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_2_id} duplicated" in errors[0]["message"]

    project_data = deepcopy(pd)
    project_data["locations"][0]["supervisorId"] = supervisor_id
    project_data["locations"][0]["additionalSupervisors"] = [supervisor_id]
    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_id} duplicated" in errors[0]["message"]

    project_data["locations"][0]["additionalSupervisors"] = [
        supervisor_2_id,
        supervisor_2_id,
    ]
    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_data}, raw=True
    )
    errors = data.json().get("errors")
    assert errors
    assert f"Supervisor ID {supervisor_2_id} duplicated" in errors[0]["message"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_invalid_location_lat_lon(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    project_data, _ = await create_project(execute_gql, db_session, populate_ids=True)
    location_data = project_data["locations"][0]

    # latitude is required
    location_data.pop("latitude")
    data = await edit_project_gql(execute_gql, project_data, with_errors=True)
    assert data["errors"]

    # Invalid latitude
    for value in (
        "invalid",
        "90.000000001",
        "-90.000000001",
        90.000000001,
        -90.000000001,
    ):
        location_data["latitude"] = value
        data = await edit_project_gql(execute_gql, project_data, with_errors=True)
        assert data["errors"]

    location_data["latitude"] = 0

    # longitude is required
    location_data.pop("longitude")
    data = await edit_project_gql(execute_gql, project_data, with_errors=True)
    assert data["errors"]

    # Invalid longitude
    for value in (
        "invalid",
        "180.000000001",
        "-180.000000001",
        180.000000001,
        -180.000000001,
    ):
        location_data["longitude"] = value
        data = await edit_project_gql(execute_gql, project_data, with_errors=True)
        assert data["errors"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.timeout(60)
async def test_edit_location_lat_lon(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    project_data, _ = await create_project(execute_gql, db_session, populate_ids=True)
    location_data = project_data["locations"][0]
    db_location = await db_data.location(location_data["id"])

    for key in ("latitude", "longitude"):
        # It should keep same value if decimal have more than supported
        location_data[key] = Decimal("10." + "0" * LOCATION_GEOM_SCALE + "1")
        data = await edit_project_gql(execute_gql, project_data)
        assert isinstance(data["locations"][0][key], str)
        # On update we don't refresh data saved to DB
        assert data["locations"][0][key] == str(location_data[key])
        # But on fetch, it should be OK in DB
        await db_session.refresh(db_location)
        assert str(getattr(db_location.geom, key)) == str(location_data[key])
        assert isinstance(getattr(db_location.geom, f"decimal_{key}"), Decimal)

        # It should keep the decimal
        location_data[key] = Decimal("10." + "0" * (LOCATION_GEOM_SCALE - 1) + "1")
        data = await edit_project_gql(execute_gql, project_data)
        assert isinstance(data["locations"][0][key], str)
        # On update we don't refresh data saved to DB
        assert data["locations"][0][key] == str(location_data[key])
        # But on fetch, it should be OK in DB
        await db_session.refresh(db_location)
        assert str(getattr(db_location.geom, key)) == str(location_data[key])
        assert isinstance(getattr(db_location.geom, f"decimal_{key}"), Decimal)

        # It should always return str
        location_data[key] = 0
        data = await edit_project_gql(execute_gql, project_data)
        assert isinstance(data["locations"][0][key], str)
        assert data["locations"][0][key] == "0"
        await db_session.refresh(db_location)
        assert getattr(db_location.geom, key) == 0.0
        assert isinstance(getattr(db_location.geom, f"decimal_{key}"), Decimal)


################################################################################
# Archive an existing location
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_location(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Creates a project with several locations, then sends an editProject mutation
    without one of the location, triggering a location archive.
    """

    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=4, archived_at=None
    )
    to_archive = locations[2]  # grab a location to be archived

    await db_session.refresh(project)

    project_update = gql_project(project)
    project_update["locations"] = [
        # exclude the to_archive location
        gql_location(x)
        for x in locations
        if not x.id == to_archive.id
    ]

    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_update}
    )

    ###########################################################
    # ensure only the non-archived locations are returned

    project_data = data["project"]
    assert project_data["id"] == str(project.id)

    returned_locations = project_data["locations"]
    returned_loc_ids: set[uuid.UUID] = {i["id"] for i in returned_locations}

    assert len(returned_loc_ids) == 3
    assert str(to_archive) not in returned_loc_ids
    loc_ids = set(map(lambda x: str(x.id), locations))
    loc_ids.remove(str(to_archive.id))
    assert loc_ids == returned_loc_ids

    ###########################################################
    # ensure the location still exists in the db, and is archived

    await db_session.refresh(to_archive)
    assert_recent_datetime(to_archive.archived_at)

    # making double sure - fetch a new version of the same obj.
    archived_location = await db_data.location(to_archive.id)
    assert_recent_datetime(archived_location.archived_at)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_location_archives_nested_objs(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Similar to the previous test, but includes assertions for nested tasks,
    site conditions, hazards, and controls.
    """

    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=3, archived_at=None
    )
    to_archive = locations[1]  # grab a location to be archived

    task: Task = await TaskFactory.persist(db_session, location_id=to_archive.id)
    task_hazard: TaskHazard = await TaskHazardFactory.persist(
        db_session,
        task_id=task.id,
    )
    task_control: TaskControl = await TaskControlFactory.persist(
        db_session, task_hazard_id=task_hazard.id, user_id=uuid.uuid4()
    )

    site_condition: SiteCondition = await SiteConditionFactory.persist(
        db_session, location_id=to_archive.id
    )
    site_condition_hazard: SiteConditionHazard = (
        await SiteConditionHazardFactory.persist(
            db_session,
            site_condition_id=site_condition.id,
        )
    )
    site_condition_control: SiteConditionControl = (
        await SiteConditionControlFactory.persist(
            db_session,
            site_condition_hazard_id=site_condition_hazard.id,
            user_id=uuid.uuid4(),
        )
    )

    await db_session.refresh(to_archive)
    await db_session.refresh(project)

    project_update = gql_project(project)
    project_update["locations"] = [
        # exclude the to_archive location
        gql_location(x)
        for x in locations
        if not x.id == to_archive.id
    ]

    await execute_gql(**edit_project_mutation, variables={"project": project_update})

    # ensure the location still exists in the db, and is archived

    await db_session.refresh(to_archive)
    assert_recent_datetime(to_archive.archived_at)

    # making double sure - fetch a new version of the same obj.
    archived_location = await db_data.location(to_archive.id)
    assert_recent_datetime(archived_location.archived_at)

    # ensure the objs still exist in the db, and have archived_at set
    for d in [
        task,
        task_hazard,
        task_control,
        site_condition,
        site_condition_hazard,
        site_condition_control,
    ]:
        await db_session.refresh(d)
        assert_recent_datetime(d.archived_at)  # type: ignore


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_create_location_from_lat_lon(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a location from lat lon
    """

    gps_coords = {
        "latitude": 12.9539974,
        "longitude": 77.6309395,
    }
    name = "Test Location"
    date = datetime.datetime.now()
    data = await execute_gql(
        **save_location_from_lat_lon_mutation,
        variables={"gpsCoordinates": gps_coords, "name": name, "date": date},
    )
    assert "createLocationFromLatLon" in data
    assert "id" in data["createLocationFromLatLon"]
