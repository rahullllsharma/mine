import pytest
from fastapi.encoders import jsonable_encoder

from tests.db_data import DBData
from tests.factories import (
    ActivityFactory,
    AdminUserFactory,
    CrewFactory,
    LibraryActivityTypeFactory,
    TaskControlFactory,
    TaskFactory,
    TaskHazardFactory,
    TenantFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import gql_activity, gql_control, gql_hazard
from tests.integration.mutations.audit_events.helpers import (
    assert_created_at,
    audit_events_for_object,
    diffs_by_object_type,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    AuditObjectType,
)

create_activity_mutation = {
    "operation_name": "CreateActivity",
    "query": """
mutation CreateActivity($activity: CreateActivityInput!) {
  activity: createActivity(activityData: $activity) { id tasks {id hazards {id} }}
}
""",
}


################################################################################
# Create Activity
################################################################################


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_activity_with_hazard_and_control_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Creates a activity with recommended hazards and controls, then asserts on the
    resulting audit event and diffs.
    """
    user = await AdminUserFactory.persist(db_session)

    # extra models so we can use their relational data
    extra_activity = await ActivityFactory.persist(db_session)
    extra_task = await TaskFactory.persist(db_session)
    extra_hazard = await TaskHazardFactory.persist(db_session)
    extra_control = await TaskControlFactory.persist(db_session)

    # activity needs to have crew_id and library_activity_type_id, for some reason the default tenant configs are being set to have these fields required
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    activity = ActivityFactory.build(
        external_key=None,
        meta_attributes=None,
        crew_id=(await CrewFactory.persist(db_session)).id,
        library_activity_type_id=(
            await LibraryActivityTypeFactory.with_link(db_session, tenant_id)
        ).id,
    )
    hazard = TaskHazardFactory.build(is_applicable=True, position=0, user_id=user.id)
    control = TaskControlFactory.build(is_applicable=True, position=0, user_id=user.id)

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
        user=user,
        variables={
            "activity": {
                **gql_activity(activity.dict(exclude={"id"})),
                "locationId": extra_activity.location_id,
                "tasks": [new_task],
            }
        },
    )

    activity_data = data["activity"]
    events = await audit_events_for_object(db_session, activity_data["id"])

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.activity_created

    assert len(await db_data.audit_event_diffs(event.id)) == 4
    diffs_by_type = await diffs_by_object_type(db_session, event)
    activity_diff = diffs_by_type[AuditObjectType.activity][0]
    task_diff = diffs_by_type[AuditObjectType.task][0]
    hazard_diff = diffs_by_type[AuditObjectType.task_hazard][0]
    control_diff = diffs_by_type[AuditObjectType.task_control][0]

    for d in [activity_diff, task_diff, hazard_diff, control_diff]:
        assert d.diff_type == AuditDiffType.created
        assert d.old_values is None

    assert activity_diff.new_values
    assert activity_diff.new_values == jsonable_encoder(
        {
            **activity.dict(exclude={"id", "meta_attributes"}),
            "location_id": str(extra_activity.location_id),
            "tasks": [task["id"] for task in activity_data["tasks"]],
            "critical_description": None,
            "is_critical": False,
        }
    )

    assert task_diff.new_values
    assert task_diff.new_values == jsonable_encoder(
        {
            "activity_id": activity_data["id"],
            "library_task_id": str(extra_task.library_task_id),
            **activity.dict(
                exclude={
                    "id",
                    "name",
                    "crew_id",
                    "library_activity_type_id",
                    "external_key",
                    "critical_description",
                    "is_critical",
                    "meta_attributes",
                }
            ),
            "location_id": str(extra_activity.location_id),
        }
    )

    task_data = activity_data["tasks"][0]
    assert hazard_diff.new_values
    assert hazard_diff.new_values == jsonable_encoder(
        {
            **hazard.dict(exclude={"id"}),
            "library_hazard_id": str(extra_hazard.library_hazard_id),
            "task_id": task_data["id"],
        }
    )

    hazard_data = task_data["hazards"][0]
    assert control_diff.new_values
    assert control_diff.new_values == jsonable_encoder(
        {
            **control.dict(exclude={"id"}),
            "library_control_id": str(extra_control.library_control_id),
            "task_hazard_id": hazard_data["id"],
        }
    )
