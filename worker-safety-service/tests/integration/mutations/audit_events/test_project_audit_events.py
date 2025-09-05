from datetime import datetime, timedelta, timezone
from typing import Any

import pytest
from fastapi.encoders import jsonable_encoder

import tests.factories as factories
from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    LocationFactory,
    SupervisorUserFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import (
    assert_recent_datetime,
    create_project_mutation,
    edit_project_mutation,
    gql_location,
    gql_project,
)
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
    diffs_by_object_type,
)
from tests.integration.queries.insights.helpers import (
    SampleControl,
    batch_upsert_control_report,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    AuditObjectType,
    Location,
    WorkPackage,
)
from worker_safety_service.utils import decimal_to_string

################################################################################
# Create Project
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_project_mutation_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Creates a new project with a single location via createProject gql mutation.

    Asserts on the AuditEvent and two AuditEventDiffs to be sure the created data
    matches the input data.
    """

    super_1 = (await SupervisorUserFactory.persist(db_session)).id
    super_2 = (await SupervisorUserFactory.persist(db_session)).id
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project = WorkPackageFactory.build(name="My new project", work_type_ids=[wt_1])
    await WorkPackageFactory.db_deps(db_session, project)
    project.additional_assigned_users_ids.append(super_2)
    location = LocationFactory.build(name="My new location")
    location.supervisor_id = super_1
    location.additional_supervisor_ids.append(super_2)

    location_data = gql_location(location.dict(exclude={"id"}))
    project_data = gql_project(project.dict(exclude={"id"}))
    project_data["locations"] = [location_data]

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **create_project_mutation, variables={"project": project_data}
    )

    # ensure expected data
    response_data = data["project"]
    assert response_data["name"] == project.name
    location_id = response_data["locations"][0]["id"]

    events = await audit_events_for_object(
        db_session,
        response_data["id"],
    )
    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.project_created

    # one for the project, one for the location
    assert len(await db_data.audit_event_diffs(event.id)) == 2
    diffs_by_type = await diffs_by_object_type(db_session, event)
    proj_diff = diffs_by_type[AuditObjectType.project][0]
    loc_diff = diffs_by_type[AuditObjectType.project_location][0]
    assert proj_diff.diff_type == AuditDiffType.created
    assert loc_diff.diff_type == AuditDiffType.created

    # testing the full new_values dict on creation is brittle,
    # as this test will need to be updated with every additional
    # field on the project - instead we assert on the knowns for
    # this test.
    assert proj_diff.new_values
    assert proj_diff.new_values["name"] == project.name
    assert proj_diff.new_values["start_date"] == project_data["startDate"]
    assert proj_diff.new_values["end_date"] == project_data["endDate"]
    assert proj_diff.new_values["locations"] == [location_id]
    assert (
        proj_diff.new_values["primary_assigned_user_id"] == project_data["supervisorId"]
    )
    assert (
        proj_diff.new_values["additional_assigned_users_ids"]
        == project_data["additionalSupervisors"]
    )

    assert loc_diff.new_values
    assert loc_diff.new_values["project_id"] == str(proj_diff.object_id)
    assert loc_diff.new_values["name"] == location_data["name"]
    assert loc_diff.new_values["geom"]["longitude"] == location_data["longitude"]
    assert loc_diff.new_values["geom"]["latitude"] == location_data["latitude"]
    assert loc_diff.new_values["supervisor_id"] == location_data["supervisorId"]
    assert (
        loc_diff.new_values["additional_supervisor_ids"]
        == location_data["additionalSupervisors"]
    )
    assert "id" not in loc_diff.new_values


################################################################################
# Update Project
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_project_mutation_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Tests that an existing project and it's location can be updated,
    and that the expected event and 2 diffs are created.
    """
    wt_1 = (await WorkTypeFactory.persist(db_session)).id
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session, work_type_ids=[wt_1]
    )
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id
    )
    new_super = str((await SupervisorUserFactory.persist(db_session)).id)
    old_super = str(project.primary_assigned_user_id)
    # required b/c the location creation marks the project as dirty
    await db_session.refresh(project)
    await db_session.refresh(location)

    # handles stringifying date fields
    proj_dict = jsonable_encoder(project)
    proj_new_values = {
        "name": "My edited project",
        "end_date": str((datetime.today() + timedelta(days=52)).date()),
        "primary_assigned_user_id": new_super,
        "additional_assigned_users_ids": [old_super],
    }
    proj_old_values = {k: proj_dict[k] for k in proj_new_values.keys()}

    loc_dict = location.dict()
    # pydantic/sqlmodel returns uuids as UUID, not str
    # update any UUID values to str if asserting on them
    # so they match the gql input
    loc_dict["supervisor_id"] = str(loc_dict["supervisor_id"])
    loc_new_values = {
        "name": "My edited location",
        "geom": {"latitude": str(location.geom.latitude), "longitude": "10.0"},
        "supervisor_id": new_super,
        "additional_supervisor_ids": [old_super],
    }
    loc_old_values = {k: loc_dict[k] for k in loc_new_values.keys()}
    loc_old_values["geom"] = {
        "latitude": decimal_to_string(loc_old_values["geom"].decimal_latitude),
        "longitude": decimal_to_string(loc_old_values["geom"].decimal_longitude),
    }

    location_update = gql_location(
        {
            **location.dict(),
            **loc_new_values,
        }
    )
    project_update = gql_project(
        {
            **proj_dict,
            **proj_new_values,
        },
    )

    project_update["locations"] = [location_update]

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        **edit_project_mutation, variables={"project": project_update}, user=user
    )

    # ensure expected data
    response_data = data["project"]
    assert response_data["name"] == project_update["name"]

    events = await audit_events_for_object(
        db_session,
        id=project.id,
        event_type=AuditEventType.project_updated,
    )
    assert len(events) == 1
    event = events[0]
    await assert_created_at(db_session, event)
    assert event.user_id == user.id
    assert event.event_type == AuditEventType.project_updated

    assert len(await db_data.audit_event_diffs(event.id)) == 2
    diffs_by_type = await diffs_by_object_type(db_session, event)
    proj_diff = diffs_by_type[AuditObjectType.project][0]
    loc_diff = diffs_by_type[AuditObjectType.project_location][0]
    assert proj_diff.diff_type == AuditDiffType.updated
    assert loc_diff.diff_type == AuditDiffType.updated

    # TODO: Add to the test once the GraphQL API is working.
    for attr in ["customer_status"]:
        for d in [proj_diff.old_values, proj_diff.new_values]:
            if d is not None and attr in d:
                d.pop(attr)
    # assert old_values and new_values match the exdb values and the input
    assert proj_diff.old_values == proj_old_values
    assert proj_diff.new_values == proj_new_values
    assert loc_diff.old_values == loc_old_values
    assert loc_diff.new_values == loc_new_values


################################################################################
# Archive Project
################################################################################

archive_project_mutation = """
mutation TestQuery($deleteProjectId: UUID!) {
  deleteProject(id: $deleteProjectId)
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_project_mutation_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Archives the indicated project by project_id, and all it's children
    (locations, daily-reports, tasks, site-conds, hazards, controls).
    """
    day = datetime.now(timezone.utc)

    (
        _,
        project,
        location,
        task,
        t_hazard,
    ) = await factories.TaskControlFactory.with_relations(
        db_session,
    )
    stub_activity = (
        factories.ActivityFactory.build()
    )  # TODO: Add to return statement of TaskControlFactory.with_relations

    (
        _,
        project,
        location_2,
        site_condition,
        sc_hazard,
    ) = await factories.SiteConditionControlFactory.with_relations(
        db_session,
        project=project,
    )

    await batch_upsert_control_report(
        db_session,
        {
            day: [
                SampleControl(location=location, task=task, hazard=t_hazard),
                SampleControl(
                    location=location_2, site_condition=site_condition, hazard=sc_hazard
                ),
            ]
        },
    )

    to_be_archived: list[Any] = (
        [
            project,
            location,
            stub_activity,
            task,
            t_hazard,
            location_2,
            site_condition,
            sc_hazard,
        ]
        # 2 controls
        + (await db_data.task_hazard_controls(t_hazard.id))
        # 2 controls
        + (await db_data.site_condition_hazard_controls(sc_hazard.id))
        # 1 report
        + (await db_data.location_daily_reports(location.id))
        # 1 report
        + (await db_data.location_daily_reports(location_2.id))
    )

    # we expect 14 objects to live under this project
    assert len(to_be_archived) == 14

    data = await execute_gql(
        query=archive_project_mutation, variables={"deleteProjectId": project.id}
    )
    assert data

    events = await audit_events_for_object(
        db_session,
        id=project.id,
        event_type=AuditEventType.project_updated,
    )
    assert len(events) == 1
    event = events[0]
    await assert_created_at(db_session, event)
    assert event.user_id  # should have some user set
    assert event.event_type == AuditEventType.project_archived

    diffs_by_type = await diffs_by_object_type(db_session, event)
    types = set(diffs_by_type.keys())
    expected_object_types = {
        AuditObjectType.activity,
        AuditObjectType.project,
        AuditObjectType.project_location,
        AuditObjectType.task,
        AuditObjectType.task_hazard,
        AuditObjectType.task_control,
        AuditObjectType.site_condition,
        AuditObjectType.site_condition_hazard,
        AuditObjectType.site_condition_control,
        AuditObjectType.daily_report,
    }
    assert types == expected_object_types

    # should be 14 diffs
    event_diffs = await db_data.audit_event_diffs(event.id)
    assert len(event_diffs) == len(to_be_archived)
    # ensure the objs still exist in the db, and have archived_at set
    for d in event_diffs:
        assert d.diff_type == AuditDiffType.archived
        assert d.new_values
        assert d.old_values
        if d.object_type == AuditObjectType.daily_report:
            assert ["updated_at"] == [list(d.new_values.keys())[0]]
            assert ["updated_at"] == [list(d.old_values.keys())[0]]
            assert ["archived_at"] == [list(d.new_values.keys())[1]]
            assert ["archived_at"] == [list(d.old_values.keys())[1]]
        else:
            assert ["archived_at"] == [list(d.new_values.keys())[0]]
            assert ["archived_at"] == [list(d.old_values.keys())[0]]

        assert_recent_datetime(datetime.fromisoformat(d.new_values["archived_at"]))
