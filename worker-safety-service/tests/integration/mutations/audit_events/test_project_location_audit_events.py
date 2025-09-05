import uuid
from datetime import datetime
from itertools import chain

import pytest

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    LocationFactory,
    SiteConditionControlFactory,
    SiteConditionFactory,
    SiteConditionHazardFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    edit_project_mutation,
    gql_location,
    gql_project,
)
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
    diffs_by_object_type,
    last_audit_event,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    AuditObjectType,
    Location,
    SiteCondition,
    SiteConditionHazard,
    Task,
    TaskHazard,
    WorkPackage,
)

################################################################################
# Add a location to a Project
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_add_location_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=4, archived_at=None
    )
    existing_loc_ids = list(map(lambda x: str(x.id), locations))
    await db_session.refresh(project)

    new_location = {
        "name": "new location",
        "geom": {"latitude": "0.0", "longitude": "0.0"},
        "supervisor_id": str(locations[0].supervisor_id),
        "additional_supervisor_ids": [],
        "external_key": None,
        "address": None,
        "risk": "unknown",
        "tenant_id": str(project.tenant_id),
    }

    project_update = gql_project(project)
    project_update["locations"] = [gql_location(x) for x in locations] + [
        gql_location(new_location)
    ]

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **edit_project_mutation, variables={"project": project_update}
    )

    response_data = data["project"]
    assert response_data["id"] == str(project.id)

    # fetch the event for the project
    event = await last_audit_event(
        db_session, event_type=AuditEventType.project_updated
    )
    assert event
    assert event.user_id == user.id
    await assert_created_at(db_session, event)

    assert len(await db_data.audit_event_diffs(event.id)) == 1
    diffs_by_type = await diffs_by_object_type(db_session, event)
    loc_diff = diffs_by_type[AuditObjectType.project_location][0]
    assert loc_diff.diff_type == AuditDiffType.created

    assert str(loc_diff.object_id) not in existing_loc_ids
    assert loc_diff.new_values
    assert not loc_diff.old_values

    assert loc_diff.new_values["project_id"] == str(project.id)
    assert loc_diff.new_values["archived_at"] is None
    # removing this just to make the assertion simpler
    del loc_diff.new_values["archived_at"]
    new_location["project_id"] = str(project.id)
    assert loc_diff.new_values == new_location


################################################################################
# Edit a location's data
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_location_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    locations: list[Location] = await LocationFactory.persist_many(
        db_session, project_id=project.id, size=4, archived_at=None
    )
    to_update = locations[2]  # grab a location to be archived
    old_name = to_update.name

    await db_session.refresh(project)

    project_update = gql_project(project)
    project_update["locations"] = [
        # exclude the update
        gql_location(x)
        for x in locations
        if not x.id == to_update.id
    ]

    loc_update = {**gql_location(to_update), "name": "updated name"}
    project_update["locations"].append(loc_update)

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **edit_project_mutation, variables={"project": project_update}
    )

    response_data = data["project"]
    assert response_data["id"] == str(project.id)

    # fetch the event for the updatedlocation
    events = await audit_events_for_object(
        db_session,
        id=to_update.id,
        event_type=AuditEventType.project_updated,
    )
    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.project_updated

    # TODO: Revert once the GraphQL interface is migrate to work packages
    diffs_by_type = await diffs_by_object_type(db_session, event)
    diffs_by_type.pop(AuditObjectType.project, None)
    assert len(list(chain.from_iterable(diffs_by_type.values()))) == 1
    loc_diff = diffs_by_type[AuditObjectType.project_location][0]
    assert loc_diff.diff_type == AuditDiffType.updated

    assert loc_diff.new_values == {"name": loc_update["name"]}
    assert loc_diff.old_values == {"name": old_name}


################################################################################
# Delete an existing location
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_location_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Creates a project with several locations, then sends an editProject mutation
    without one of the location, triggering a location archival.
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

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **edit_project_mutation, variables={"project": project_update}
    )

    response_data = data["project"]
    assert response_data["id"] == str(project.id)

    # fetch the event for the removed location
    events = await audit_events_for_object(
        db_session,
        id=to_archive.id,
        event_type=AuditEventType.project_updated,
    )
    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.project_updated

    # TODO: Revert once the GraphQL interface is migrate to work packages
    diffs_by_type = await diffs_by_object_type(db_session, event)
    diffs_by_type.pop(AuditObjectType.project, None)
    assert len(list(chain.from_iterable(diffs_by_type.values()))) == 1
    loc_diffs = diffs_by_type[AuditObjectType.project_location]
    assert len(loc_diffs) == 1
    loc_diff = loc_diffs[0]
    assert loc_diff.diff_type == AuditDiffType.archived

    assert loc_diff.new_values
    assert loc_diff.old_values

    # should be the only updated key
    assert ["archived_at"] == list(loc_diff.new_values.keys())
    assert ["archived_at"] == list(loc_diff.old_values.keys())
    assert_recent_datetime(datetime.fromisoformat(loc_diff.new_values["archived_at"]))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_location_audit_includes_nested_archive_diffs(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
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
    await TaskControlFactory.persist(
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

    await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=site_condition_hazard.id,
        user_id=uuid.uuid4(),
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

    user = await AdminUserFactory.persist(db_session)
    await execute_gql(
        user=user, **edit_project_mutation, variables={"project": project_update}
    )

    # fetch the event for the removed location
    events = await audit_events_for_object(
        db_session,
        id=to_archive.id,
        event_type=AuditEventType.project_updated,
    )
    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.project_updated

    # TODO: Revert once the GraphQL interface is migrate to work packages
    diffs_by_type = await diffs_by_object_type(db_session, event)
    diffs_by_type.pop(AuditObjectType.project, None)
    assert len(list(chain.from_iterable(diffs_by_type.values()))) == 7
    # ensure all of these diff types are present
    assert set(diffs_by_type.keys()) == {
        AuditObjectType.project_location,
        AuditObjectType.task,
        AuditObjectType.task_hazard,
        AuditObjectType.task_control,
        AuditObjectType.site_condition,
        AuditObjectType.site_condition_hazard,
        AuditObjectType.site_condition_control,
    }

    # ensure the objs still exist in the db, and have archived_at set
    for d in chain.from_iterable(diffs_by_type.values()):
        assert d.diff_type == AuditDiffType.archived
        assert d.new_values
        assert d.old_values
        assert ["archived_at"] == list(d.new_values.keys())
        assert ["archived_at"] == list(d.old_values.keys())
        assert_recent_datetime(datetime.fromisoformat(d.new_values["archived_at"]))
