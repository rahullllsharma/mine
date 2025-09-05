from datetime import datetime, timedelta, timezone
from uuid import UUID

import jsonpatch
import pytest
from fastapi.encoders import jsonable_encoder
from sqlmodel import select

from tests.db_data import DBData
from tests.factories import (
    AuditEventDiffFactory,
    AuditEventFactory,
    DailyReportFactory,
    LocationFactory,
    SiteConditionFactory,
    TaskFactory,
    UserFactory,
    WorkPackageFactory,
)
from worker_safety_service.audit_events.dataclasses import ProjectDiff
from worker_safety_service.dal.audit_events import (
    AuditContext,
    AuditEventManager,
    diffs_from_session,
    register_audit_event_diffs,
)
from worker_safety_service.dal.work_packages import WorkPackageManager
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEvent,
    AuditEventDiff,
    AuditEventType,
    AuditObjectType,
    Location,
    User,
    WorkPackage,
)

audit_object_to_event_map = {
    AuditObjectType.project: [
        (AuditEventType.project_created, AuditDiffType.created),
        (AuditEventType.project_updated, AuditDiffType.updated),
        (AuditEventType.project_archived, AuditDiffType.archived),
    ],
    AuditObjectType.task: [
        (AuditEventType.task_created, AuditDiffType.created),
        (AuditEventType.task_updated, AuditDiffType.updated),
        (AuditEventType.task_archived, AuditDiffType.archived),
    ],
    AuditObjectType.site_condition: [
        (AuditEventType.site_condition_created, AuditDiffType.created),
        (AuditEventType.site_condition_updated, AuditDiffType.updated),
        (
            AuditEventType.site_condition_evaluated,
            AuditDiffType.created,
        ),
        (
            AuditEventType.site_condition_archived,
            AuditDiffType.archived,
        ),
    ],
    AuditObjectType.daily_report: [
        (AuditEventType.daily_report_created, AuditDiffType.created),
        (AuditEventType.daily_report_updated, AuditDiffType.updated),
        (AuditEventType.daily_report_archived, AuditDiffType.archived),
    ],
    AuditObjectType.project_location: [
        (AuditEventType.project_location_created, AuditDiffType.created),
        (AuditEventType.project_location_updated, AuditDiffType.updated),
        (AuditEventType.project_location_archived, AuditDiffType.archived),
    ],
}


@pytest.mark.skip  # Broken when changing db_session to scope="session"
@pytest.mark.asyncio
@pytest.mark.integration
async def test_diffs_from_session_supports_new_objects(
    db_session: AsyncSession,
) -> None:
    project = WorkPackageFactory.build()
    db_session.add(project)
    diffs = diffs_from_session(db_session)

    assert len(diffs) == 1

    diff = diffs[0]

    assert diff.diff_type == AuditDiffType.created
    assert diff.object_type == AuditObjectType.project
    assert diff.object_id == project.id

    assert not diff.old_values  # nothing in old_vals
    assert diff.new_values

    # sanity check some new_vals
    expected_fields = ["name", "status"]
    assert expected_fields
    for f in expected_fields:
        assert f in diff.new_values

    # new_values is a json-friendly dict without the 'id'
    assert diff.new_values == jsonable_encoder(project.dict(exclude={"id"}))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_diffs_from_session_supports_updating_objects(
    db_session: AsyncSession,
) -> None:
    project_id = (await WorkPackageFactory.persist(db_session)).id

    project = (
        await db_session.exec(select(WorkPackage).where(WorkPackage.id == project_id))
    ).first()
    assert project
    old_name = project.name
    project.name = "some new name"

    diffs = diffs_from_session(db_session)

    assert len(diffs) == 1

    diff = diffs[0]

    assert diff.diff_type == AuditDiffType.updated
    assert diff.object_type == AuditObjectType.project
    assert diff.object_id == project.id

    assert diff.old_values == {"name": old_name}
    assert diff.new_values == {"name": project.name}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_diffs_from_session_supports_deleting_objects(
    db_session: AsyncSession,
) -> None:
    project_id = (await WorkPackageFactory.persist(db_session)).id

    project = (
        await db_session.exec(select(WorkPackage).where(WorkPackage.id == project_id))
    ).first()
    assert project
    await db_session.delete(project)
    diffs = diffs_from_session(db_session)

    assert len(diffs) == 1

    diff = diffs[0]

    assert diff.diff_type == AuditDiffType.deleted
    assert diff.object_type == AuditObjectType.project
    assert diff.object_id == project.id

    assert not diff.new_values  # nothing in new_vals
    assert diff.old_values

    # sanity check some old_vals
    expected_fields = ["name", "status"]
    assert expected_fields
    for f in expected_fields:
        assert f in diff.old_values

    # old_values is a json-friendly dict without the 'id'
    assert diff.old_values == jsonable_encoder(
        project.dict(exclude={"id", "meta_attributes"})
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_diffs_from_session_supports_archiving_objects(
    db_session: AsyncSession,
) -> None:
    """
    Archiving is a special 'update' case - if changes are made to an attribute
    with a key matching 'archived_at', the diff is given an 'archived' DiffType.

    Using a project_location, as that type already has an `archived_at` column.
    """
    location_id = (await LocationFactory.persist(db_session)).id

    location = (
        await db_session.exec(select(Location).where(Location.id == location_id))
    ).first()
    assert location
    now = datetime.now(timezone.utc)
    location.archived_at = now
    diffs = diffs_from_session(db_session)

    assert len(diffs) == 1

    diff = diffs[0]

    assert diff.diff_type == AuditDiffType.archived
    assert diff.object_type == AuditObjectType.project_location
    assert diff.object_id == location.id

    assert diff.old_values == {"archived_at": None}
    # using jsonable_encoder to get the same date formatting
    assert diff.new_values == jsonable_encoder({"archived_at": now})


async def _setup_event(
    session: AsyncSession,
    event_type: AuditEventType,
    object_type: AuditObjectType,
    object_id: UUID,
    n_diffs: int = 1,
    user_id: UUID | None = None,
    created_at: datetime = datetime.now(),
) -> tuple[AuditEvent, list[AuditEventDiff]]:
    event = await AuditEventFactory.persist(
        session,
        user_id=user_id,
        created_at=created_at,
        event_type=event_type,
    )
    event_diffs = await AuditEventDiffFactory.persist_many(
        session,
        size=n_diffs,
        event_id=event.id,
        object_id=object_id,
        object_type=object_type,
        created_at=created_at,
    )
    return event, event_diffs


@pytest.mark.asyncio
@pytest.mark.integration
async def test_diffs_for_json_columns(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """
    JSON columns are audited differently than non-structured data.
    A log of changes is recorded to get from old->new and new->old.

    Changes are generated using `jsonpatch`
    """
    location = await LocationFactory.persist(db_session)
    drf = DailyReportFactory.build()
    drf.project_location_id = location.id
    drf.created_by_id = test_user.id
    drf.tenant_id = location.tenant_id
    sections = {
        "work_schedule": {
            "end_datetime": "2022-03-24T04:14:00.000",
            "start_datetime": "2022-03-24T02:12:00.000",
            "section_is_valid": True,
        },
        "task_selection": {"selected_tasks": [], "section_is_valid": True},
        "job_hazard_analysis": {
            "tasks": [],
            "site_conditions": [],
            "section_is_valid": True,
        },
    }
    new_values = []
    old_values = []
    for section in sections.keys():
        original = {}
        original.update(drf.sections)
        swap = {}
        swap.update(drf.sections)
        swap.update({section: sections[section]})
        drf.sections = swap
        db_session.add(drf)
        diffs = diffs_from_session(db_session)

        assert diffs[0]
        # assert patching forwards
        if diffs[0].new_values:
            patch = jsonpatch.JsonPatch(diffs[0].new_values["sections"])
            new_values.append(patch)
            patched = patch.apply(original)
            assert patched == swap
        # assert patching backwards
        if diffs[0].old_values:
            patch = jsonpatch.JsonPatch(diffs[0].old_values["sections"])
            old_values.append(patch)
            patched = patch.apply(swap)
            assert patched == original

        await db_session.commit()
    assert drf.sections == sections
    # check that we can traverse patches from the original (empty) object to the final object
    original = {}
    for patch in new_values:
        original = patch.apply(original)
    assert original == sections == drf.sections


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_diff_object_ids_for_projects_excludes_evaluated_scs(
    db_session: AsyncSession, audit_event_manager: AuditEventManager
) -> None:
    user = await UserFactory.persist(db_session)
    (
        sc,
        project,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)

    _, evaluated_diff = await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_evaluated,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        user_id=user.id,
    )

    _, created_diff = await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_created,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        user_id=user.id,
    )

    diffs = await audit_event_manager.get_project_diffs(
        project_ids=[project.id], tenant_id=user.tenant_id
    )

    assert project.id in diffs
    project_diffs = diffs[project.id]
    assert len(project_diffs) == 1
    diff = project_diffs[0]
    assert isinstance(diff, ProjectDiff)
    assert diff.project_id == project.id
    assert diff.diff.object_id == sc.id
    assert diff.user
    assert diff.user.id == user.id
    assert diff.diff.id == created_diff[0].id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_site_condition_ids_for_projects(
    db_session: AsyncSession, audit_event_manager: AuditEventManager
) -> None:
    user = await UserFactory.persist(db_session)
    (
        sc,
        project,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)

    _, evaluated_diff = await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_evaluated,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        user_id=user.id,
    )

    _, created_diff = await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_created,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        user_id=user.id,
    )

    diffs = await audit_event_manager.get_project_diffs(
        project_ids=[project.id], tenant_id=user.tenant_id
    )

    assert project.id in diffs
    project_diffs = diffs[project.id]
    assert len(project_diffs) == 1
    diff = project_diffs[0]
    assert isinstance(diff, ProjectDiff)
    assert diff.project_id == project.id
    assert diff.diff.object_id == sc.id
    assert diff.user
    assert diff.user.id == user.id
    assert diff.diff.id == created_diff[0].id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_diff_object_ids_for_projects(
    db_session: AsyncSession, audit_event_manager: AuditEventManager
) -> None:
    user = await UserFactory.persist(db_session)
    (
        task,
        project,
        location,
    ) = await TaskFactory.with_project_and_location(db_session)
    sc = await SiteConditionFactory.persist(db_session, location_id=location.id)
    dr = await DailyReportFactory.persist(db_session, project_location_id=location.id)

    # for each audit object type gathered in project audits
    # create an audit event and diff
    # for each event type for that object type
    _diffs = []
    event_types = []
    events = await AuditEventFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {"user_id": user.id, "created_at": datetime.now(), "event_type": event_type}
            for object_type in audit_object_to_event_map.keys()
            for event_type, _ in audit_object_to_event_map[object_type]
        ],
    )

    idx = 0
    diff_items = []
    for object_type, model in zip(
        audit_object_to_event_map.keys(), [project, task, sc, dr]
    ):
        for event_type, diff_type in audit_object_to_event_map[object_type]:
            diff_items.append(
                {
                    "event_id": events[idx].id,
                    "object_id": model.id,  # type: ignore
                    "object_type": object_type,
                    "diff_type": diff_type,
                    "created_at": datetime.now(),
                }
            )
            idx += 1

    idx = 0
    events_diffs = await AuditEventDiffFactory.persist_many(
        db_session, per_item_kwargs=diff_items
    )
    for object_type, model in zip(
        audit_object_to_event_map.keys(), [project, task, sc, dr]
    ):
        for event_type, diff_type in audit_object_to_event_map[object_type]:
            if event_type != AuditEventType.site_condition_evaluated:
                event_types.append(event_type)
                _diffs.append(events_diffs[idx])
            idx += 1

    diffs = await audit_event_manager.get_project_diffs(
        project_ids=[project.id], tenant_id=user.tenant_id
    )

    assert project.id in diffs
    project_diffs = diffs[project.id]
    assert len(project_diffs) == 12
    found_diff_types = []

    for pd, diff, event_type in zip(project_diffs[::-1], _diffs, event_types):
        if event_type == AuditEventType.site_condition_evaluated:
            # we currently skip evaluated audit events
            continue
        found_diff_types.append(event_type)
        assert pd.diff.object_id == diff.object_id
        assert pd.diff.event.event_type == event_type
        assert pd.diff.id == diff.id
        assert pd.project_id == project.id
        assert pd.user
        assert pd.user.id == user.id
    assert len(found_diff_types) == 12
    assert AuditEventType.site_condition_evaluated not in found_diff_types


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_get_all_project_task_diffs_default_order(
    db_session: AsyncSession, audit_event_manager: AuditEventManager
) -> None:
    user = await UserFactory.persist(db_session)
    task, project, _ = await TaskFactory.with_project_and_location(db_session)

    created_at_1 = datetime.now(timezone.utc)
    await _setup_event(
        db_session,
        event_type=AuditEventType.task_created,
        object_type=AuditObjectType.task,
        object_id=task.id,
        user_id=user.id,
        created_at=created_at_1,
    )

    created_at_2 = created_at_1 - timedelta(days=1)
    await _setup_event(
        db_session,
        event_type=AuditEventType.task_created,
        object_type=AuditObjectType.task,
        object_id=task.id,
        user_id=user.id,
        created_at=created_at_2,
    )

    created_at_3 = created_at_1 + timedelta(days=1)
    await _setup_event(
        db_session,
        event_type=AuditEventType.task_created,
        object_type=AuditObjectType.task,
        object_id=task.id,
        user_id=user.id,
        created_at=created_at_3,
    )

    diffs = await audit_event_manager.get_project_diffs(
        project_ids=[project.id], tenant_id=user.tenant_id
    )

    assert project.id in diffs
    project_diffs = diffs[project.id]
    assert len(project_diffs) == 3
    assert project_diffs[0].diff.created_at == created_at_3
    assert project_diffs[1].diff.created_at == created_at_1
    assert project_diffs[2].diff.created_at == created_at_2


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_get_all_project_site_condition_diffs_default_order(
    db_session: AsyncSession, audit_event_manager: AuditEventManager
) -> None:
    user = await UserFactory.persist(db_session)
    (
        site_condition,
        project,
        _,
    ) = await SiteConditionFactory.with_project_and_location(db_session)

    created_at_1 = datetime.now(timezone.utc)
    await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_created,
        object_type=AuditObjectType.site_condition,
        object_id=site_condition.id,
        user_id=user.id,
        created_at=created_at_1,
    )

    created_at_2 = created_at_1 - timedelta(days=1)
    await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_created,
        object_type=AuditObjectType.site_condition,
        object_id=site_condition.id,
        user_id=user.id,
        created_at=created_at_2,
    )

    created_at_3 = created_at_1 + timedelta(days=1)
    await _setup_event(
        db_session,
        event_type=AuditEventType.site_condition_created,
        object_type=AuditObjectType.site_condition,
        object_id=site_condition.id,
        user_id=user.id,
        created_at=created_at_3,
    )

    diffs = await audit_event_manager.get_project_diffs(
        project_ids=[project.id], tenant_id=user.tenant_id
    )

    assert project.id in diffs
    project_diffs = diffs[project.id]
    assert len(project_diffs) == 3
    assert project_diffs[0].diff.created_at == created_at_3
    assert project_diffs[1].diff.created_at == created_at_1
    assert project_diffs[2].diff.created_at == created_at_2


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_audit_context_should_be_single(db_session: AsyncSession) -> None:
    """Make sure we don't allow AuditContext don't start twice for same session"""

    with AuditContext(db_session):
        with pytest.raises(RuntimeError):
            with AuditContext(db_session):
                pass


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_audit_context_should_not_leave_diffs_to_add_on_exit(
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """When AuditContext is used, all audit diffs should be consumed"""

    project = await WorkPackageFactory.persist(db_session)
    new_values = project.dict()

    # For registered audit events (no sqlalchemy unflushed history)
    with pytest.raises(RuntimeError):
        with AuditContext(db_session):
            register_audit_event_diffs(
                db_session,
                WorkPackage,
                AuditDiffType.archived,
                [project.id],
                new_values=new_values,
            )

    # Just check if no session history exists, so next test works as expected
    with AuditContext(db_session):
        pass

    # Should raise if sqlalchemy obj is updated
    async_project = await db_data.project(project.id)
    assert async_project
    with pytest.raises(RuntimeError):
        with AuditContext(db_session):
            async_project.name = "cenas"

    # Clear session
    await db_session.commit()
    # Just check if no session history exists, so next test works as expected
    with AuditContext(db_session):
        pass

    # Should raise if sqlalchemy obj is deleted
    with pytest.raises(RuntimeError):
        with AuditContext(db_session):
            async_project = await db_data.project(project.id)
            await db_session.delete(async_project)

    # Clear session
    await db_session.commit()
    # Just check if no session history exists, so next test works as expected
    with AuditContext(db_session):
        pass

    # Should raise if sqlalchemy obj is added
    with pytest.raises(RuntimeError):
        with AuditContext(db_session):
            db_session.add(WorkPackageFactory.build())


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_audit_context_autoflush(db_session: AsyncSession) -> None:
    """Autoflush should be disabled when running with AuditContext
    this way we keep session.new, session.dirty and session.deleted states,
    but should be set to normal when it ends
    """

    # On normal flow
    assert db_session.autoflush is True
    with AuditContext(db_session):
        assert db_session.autoflush is False
    assert db_session.autoflush is True

    # On error
    assert db_session.autoflush is True
    with pytest.raises(RuntimeError):
        with AuditContext(db_session):
            assert db_session.autoflush is False
            db_session.add(WorkPackageFactory.build())
    assert db_session.autoflush is True


@pytest.mark.asyncio
@pytest.mark.integration
async def tests_audit_context_should_diffs_all(
    db_session: AsyncSession,
    db_data: DBData,
    work_package_manager: WorkPackageManager,
) -> None:
    """Make sure AuditContext.create have all available diffs created"""

    user: User = await UserFactory.persist(db_session)
    project = await WorkPackageFactory.persist(db_session, name="sem cenas")
    project_dict = project.dict()
    project_dict.pop("id")
    project_dict.pop("meta_attributes")
    project_id_updated = project.id
    project_updated = await db_data.project(project_id_updated)
    assert project_updated
    project_deleted_dict = (await WorkPackageFactory.persist(db_session)).dict()
    project_deleted_dict.pop("meta_attributes")
    project_id_deleted = project_deleted_dict.pop("id")
    project_deleted = await db_data.project(project_id_deleted)
    assert project_deleted

    with AuditContext(db_session) as audit:
        project_added = WorkPackage(**project_dict)
        project_id_added = project_added.id
        # session add
        db_session.add(project_added)
        # session dirty
        project_updated.name = "cenas"
        # no sqlalchemy session registry
        register_audit_event_diffs(
            db_session,
            WorkPackage,
            AuditDiffType.archived,
            [project_id_updated],
            new_values={"nothing": True},
        )
        # session deleted
        await db_session.delete(project_deleted)

        # Create audit event
        await audit.create(AuditEventType.project_created, user)
        await db_session.commit()

    # Make sure everything was committed
    # Make sure a different session is used
    assert (
        await db_session.exec(
            select(WorkPackage).where(WorkPackage.id == project_id_added)
        )
    ).first() is not None
    assert (
        (
            await db_session.exec(
                select(WorkPackage).where(WorkPackage.id == project_id_updated)
            )
        ).one()
    ).name == "cenas"
    assert (
        await db_session.exec(
            select(WorkPackage).where(WorkPackage.id == project_id_deleted)
        )
    ).first() is None

    # Check audit diffs
    audit_event = (
        await db_session.exec(select(AuditEvent).where(AuditEvent.user_id == user.id))
    ).one()
    diffs = (
        await db_session.exec(
            select(AuditEventDiff).where(AuditEventDiff.event_id == audit_event.id)
        )
    ).all()
    assert len(diffs) == 4
    diffs_by_type = {i.diff_type: i for i in diffs}

    # Check created
    created = diffs_by_type[AuditDiffType.created]
    assert created.object_type == AuditObjectType.project
    assert created.object_id == project_id_added
    assert created.old_values is None
    assert created.new_values == jsonable_encoder(project_dict)

    # Check updated
    updated = diffs_by_type[AuditDiffType.updated]
    assert updated.object_type == AuditObjectType.project
    assert updated.object_id == project_id_updated
    assert updated.old_values == {"name": "sem cenas"}
    assert updated.new_values == {"name": "cenas"}

    # Check no sqlalchemy
    archived = diffs_by_type[AuditDiffType.archived]
    assert archived.object_type == AuditObjectType.project
    assert archived.object_id == project_id_updated
    assert archived.old_values is None
    assert archived.new_values == {"nothing": True}

    # Check deleted
    deleted = diffs_by_type[AuditDiffType.deleted]
    assert deleted.object_type == AuditObjectType.project
    assert deleted.object_id == project_id_deleted
    assert deleted.old_values == jsonable_encoder(project_deleted_dict)
    assert deleted.new_values is None
