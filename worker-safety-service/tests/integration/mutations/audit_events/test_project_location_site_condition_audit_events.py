from datetime import datetime

import pytest
from fastapi.encoders import jsonable_encoder

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    LibrarySiteConditionFactory,
    SiteConditionControlFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import assert_recent_datetime, gql_control, gql_hazard
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

create_site_condition_mutation = {
    "operation_name": "CreateSiteCondition",
    "query": """
mutation CreateSiteCondition($site_condition: CreateSiteConditionInput!) {
  siteCondition: createSiteCondition(data: $site_condition) {
    id
    hazards {
      id
    }
  }
}
""",
}

edit_site_condition_mutation = {
    "operation_name": "EditSiteCondition",
    "query": """
mutation EditSiteCondition($site_condition: EditSiteConditionInput!) {
  siteCondition: editSiteCondition(data: $site_condition) { id hazards {id }}
}
""",
}

delete_site_condition_mutation = {
    "operation_name": "DeleteSiteCondition",
    "query": """
mutation DeleteSiteCondition($id: UUID!) { siteCondition: deleteSiteCondition(id: $id) }
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_site_condition_with_hazard_and_control_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Creates a site_condition with recommended hazards and controls, then asserts on the
    resulting audit event and diffs.
    """

    library_site_condition = await LibrarySiteConditionFactory.persist(db_session)

    # using recommended objs to get related library_ids, for consistent user_id behavior
    (
        extra_control,
        _,
        _,
        site_condition,
        extra_hazard,
    ) = await SiteConditionControlFactory.with_relations(db_session)

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user,
        **create_site_condition_mutation,
        variables={
            "site_condition": {
                "locationId": site_condition.location_id,
                "librarySiteConditionId": library_site_condition.id,
                "hazards": [
                    {
                        "libraryHazardId": extra_hazard.library_hazard_id,
                        "isApplicable": True,
                        "controls": [
                            {
                                "libraryControlId": extra_control.library_control_id,
                                "isApplicable": True,
                            }
                        ],
                    },
                ],
            }
        }
    )

    site_condition_data = data["siteCondition"]
    hazard_data = site_condition_data["hazards"][0]
    events = await audit_events_for_object(db_session, site_condition_data["id"])

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.site_condition_created

    assert len(await db_data.audit_event_diffs(event.id)) == 3
    diffs_by_type = await diffs_by_object_type(db_session, event)
    site_condition_diff = diffs_by_type[AuditObjectType.site_condition][0]
    hazard_diff = diffs_by_type[AuditObjectType.site_condition_hazard][0]
    control_diff = diffs_by_type[AuditObjectType.site_condition_control][0]

    for d in [site_condition_diff, hazard_diff, control_diff]:
        assert d.diff_type == AuditDiffType.created
        assert d.old_values is None

    assert site_condition_diff.new_values
    assert site_condition_diff.new_values == jsonable_encoder(
        {
            "date": None,
            "alert": None,
            "multiplier": None,
            "details": None,
            "archived_at": None,
            "is_manually_added": True,
            "user_id": user.id,
            "location_id": str(site_condition.location_id),
            "library_site_condition_id": str(library_site_condition.id),
        }
    )

    assert hazard_diff.new_values
    assert hazard_diff.new_values == jsonable_encoder(
        {
            "library_hazard_id": str(extra_hazard.library_hazard_id),
            "site_condition_id": site_condition_data["id"],
            "user_id": user.id,
            "is_applicable": True,
            "archived_at": None,
            "position": 0,
        }
    )

    assert control_diff.new_values
    assert control_diff.new_values == jsonable_encoder(
        {
            "library_control_id": str(extra_control.library_control_id),
            "site_condition_hazard_id": hazard_data["id"],
            "user_id": user.id,
            "is_applicable": True,
            "archived_at": None,
            "position": 0,
        }
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_site_condition_hazard_and_control_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Asserts that updating a site_condition's hazard and control result in the expected
    audit_event and audit_event_diffs.
    """
    (
        control,
        _,
        _,
        site_condition,
        hazard,
    ) = await SiteConditionControlFactory.with_relations(db_session)

    hazard.position = 0  # not relevant to our diff
    control.position = 0  # not relevant to our diff
    hazard.user_id = None  # clear user so we can toggle applicable
    control.user_id = None  # clear user so we can toggle applicable
    await db_session.commit()
    await db_session.refresh(hazard)
    await db_session.refresh(control)
    await db_session.refresh(site_condition)

    new_hazard_is_applicable = not hazard.is_applicable
    new_control_is_applicable = not control.is_applicable
    old_hazard_is_applicable = hazard.is_applicable
    old_control_is_applicable = control.is_applicable

    updated_control = {
        **gql_control(control),
        "isApplicable": new_control_is_applicable,
    }
    updated_hazard = {
        **gql_hazard(hazard),
        "isApplicable": new_hazard_is_applicable,
        "controls": [updated_control],
    }
    updated_site_condition = {
        "id": site_condition.id,
        "hazards": [updated_hazard],
    }
    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user,
        **edit_site_condition_mutation,
        variables={"site_condition": updated_site_condition}
    )

    assert data["siteCondition"]  # sanity check, should be something here
    events = await audit_events_for_object(db_session, hazard.id)

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.site_condition_updated

    assert len(await db_data.audit_event_diffs(event.id)) == 2
    diffs_by_type = await diffs_by_object_type(db_session, event)
    hazard_diff = diffs_by_type[AuditObjectType.site_condition_hazard][0]
    control_diff = diffs_by_type[AuditObjectType.site_condition_control][0]

    old_is_applicable = hazard_diff.old_values

    for d in [hazard_diff, control_diff]:
        assert d.diff_type == AuditDiffType.updated
        assert d.old_values
        assert d.new_values

    assert old_is_applicable == {"is_applicable": old_hazard_is_applicable}
    assert hazard_diff.new_values == {"is_applicable": new_hazard_is_applicable}

    assert control_diff.old_values == {"is_applicable": old_control_is_applicable}
    assert control_diff.new_values == {"is_applicable": new_control_is_applicable}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_site_condition_audit(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """
    Asserts that deleting a site_condition results in the expected audit_event and
    audit_event_diffs.
    """
    _, _, _, site_condition, _ = await SiteConditionControlFactory.with_relations(
        db_session
    )

    user = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        user=user, **delete_site_condition_mutation, variables={"id": site_condition.id}
    )

    assert data["siteCondition"]  # bool is returned
    events = await audit_events_for_object(db_session, site_condition.id)

    assert len(events) == 1
    event = events[0]
    assert event.user_id == user.id
    await assert_created_at(db_session, event)
    assert event.event_type == AuditEventType.site_condition_archived

    assert len(await db_data.audit_event_diffs(event.id)) == 3
    diffs_by_type = await diffs_by_object_type(db_session, event)
    assert set(diffs_by_type.keys()) == {
        AuditObjectType.site_condition,
        AuditObjectType.site_condition_hazard,
        AuditObjectType.site_condition_control,
    }

    # ensure the objs still exist in the db, and have archived_at set
    for d in await db_data.audit_event_diffs(event.id):
        assert d.diff_type == AuditDiffType.archived
        assert d.new_values
        assert d.old_values
        assert ["archived_at"] == list(d.new_values.keys())
        assert ["archived_at"] == list(d.old_values.keys())
        assert_recent_datetime(datetime.fromisoformat(d.new_values["archived_at"]))
