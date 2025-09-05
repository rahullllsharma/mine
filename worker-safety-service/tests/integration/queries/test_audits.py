from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from tests.db_data import DBData
from tests.factories import (
    AdminUserFactory,
    AuditEventDiffFactory,
    AuditEventFactory,
    ContractorFactory,
    DailyReportFactory,
    LibraryAssetTypeFactory,
    LibraryDivisionFactory,
    LibraryProjectTypeFactory,
    LibraryRegionFactory,
    LocationFactory,
    ManagerUserFactory,
    SiteConditionFactory,
    SupervisorUserFactory,
    TaskFactory,
    TenantFactory,
    UserFactory,
    WorkPackageFactory,
    WorkTypeFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.graphql.types import AuditActionType
from worker_safety_service.graphql.types import AuditObjectType as AuditObjectTypeGQL
from worker_safety_service.models import (
    AsyncSession,
    AuditEventType,
    Location,
    ProjectStatus,
    SiteCondition,
    Task,
    User,
    WorkPackage,
)
from worker_safety_service.models.audit_events import AuditDiffType, AuditObjectType

project_with_audits_query = """
query TestQuery($projectId: UUID!) {
    project(projectId: $projectId) {
        id
        name
        audits {
            transactionId
            timestamp
            actor {
                id
                name
                role
            }
            actionType
            objectType
            auditKey
            diffValues {
                ... on DiffValueLiteral {
                    oldValue
                    newValue
                }
                ... on DiffValueScalar {
                    oldValues
                    newValues
                    added
                    removed
                }
            }
            objectDetails {
                id
                ... on Project {
                    id
                    name
                }
                ... on DailyReport {
                    id
                    location {
                        id
                        name
                    }
                }
                ... on SiteCondition {
                    id
                    name
                    location {
                        id
                        name
                    }
                }
                ... on Task {
                    id
                    name
                    location {
                        id
                        name
                    }
                }
            }
        }
    }
}
"""


async def assert_project_location_audit_response(
    db_session: AsyncSession,
    audit: dict[str, Any],
    user: User,
    project: WorkPackage,
    location: Location,
    site_condition: SiteCondition,
    created_at: datetime,
    action_type: AuditActionType = AuditActionType.UPDATED,
    audit_key: str | None = None,
    new_value: str | list[str] | None = None,
    old_value: str | list[str] | None = None,
    added: list[str] | None = None,
    removed: list[str] | None = None,
) -> None:
    library_sc = await DBData(db_session).library_site_condition(
        site_condition.library_site_condition_id
    )
    assert audit
    assert audit["actionType"] == action_type.value
    assert audit["actor"]
    assert audit["actor"]["id"] == str(user.id)
    assert audit["actor"]["name"] == f"{user.first_name} {user.last_name}"
    assert audit["actor"]["role"] == user.role
    assert audit["objectDetails"]
    assert audit["objectDetails"]["id"] == str(site_condition.id)
    assert audit["objectDetails"]["name"] == library_sc.name
    assert audit["objectDetails"]["location"]["id"] == str(location.id)
    assert audit["objectDetails"]["location"]["name"] == location.name
    assert audit["objectType"] == AuditObjectTypeGQL.SITE_CONDITION.value
    assert audit["timestamp"] == str(created_at).replace(" ", "T")
    assert audit["auditKey"] == audit_key

    if not audit.get("diffValues"):
        return
    if isinstance(new_value, list) or isinstance(old_value, list):
        assert audit["diffValues"]["newValues"] == new_value
        assert audit["diffValues"]["oldValues"] == old_value
        assert audit["diffValues"]["added"] == added
        assert audit["diffValues"]["removed"] == removed
    else:
        assert audit["diffValues"]["newValue"] == new_value
        assert audit["diffValues"]["oldValue"] == old_value


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_audits_for_archived_location(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    user: User = await UserFactory.persist(db_session)
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=project.id, archived_at=datetime.now(timezone.utc)
    )
    (
        created_site_condition,
        deleted_site_condition,
        archived_site_condition,
    ) = await SiteConditionFactory.persist_many(
        db_session, size=3, location_id=location.id
    )
    (
        updated_task,
        created_task,
        deleted_task,
        archived_task,
    ) = await TaskFactory.persist_many(db_session, size=4, location_id=location.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=user.id,
        event_type=AuditEventType.site_condition_created,
    )
    audit_models = [
        (
            created_site_condition,
            AuditObjectType.site_condition,
            AuditDiffType.created,
        ),
        (
            deleted_site_condition,
            AuditObjectType.site_condition,
            AuditDiffType.deleted,
        ),
        (
            archived_site_condition,
            AuditObjectType.site_condition,
            AuditDiffType.archived,
        ),
        (created_task, AuditObjectType.task, AuditDiffType.created),
        (deleted_task, AuditObjectType.task, AuditDiffType.deleted),
        (archived_task, AuditObjectType.task, AuditDiffType.archived),
    ]

    for model, object_type, diff_type in audit_models:
        created_at = datetime.now(timezone.utc)
        await AuditEventDiffFactory.persist(
            db_session,
            event_id=event.id,
            diff_type=diff_type,
            object_type=object_type,
            object_id=model.id,  # type: ignore
            created_at=created_at,
            old_values=None,
            new_values=None,
        )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
    )
    assert response["project"]
    assert response["project"]["id"] == str(project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 6

    for audit, audit_map in zip(response["project"]["audits"], audit_models[::-1]):
        model, aot, adt = audit_map
        assert audit["objectDetails"]["id"] == str(model.id)  # type: ignore


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_site_condition_audits(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    work_package: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=work_package.id
    )
    (
        created_site_condition,
        deleted_site_condition,
        archived_site_condition,
    ) = await SiteConditionFactory.persist_many(
        db_session, size=3, location_id=location.id
    )

    user: User = await UserFactory.persist(db_session)
    event = await AuditEventFactory.persist(
        db_session,
        user_id=user.id,
        event_type=AuditEventType.site_condition_created,
    )

    created_at = datetime.now(timezone.utc)

    # 1 diff from created, always returns only one AuditEventType
    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.created,
        object_type=AuditObjectType.site_condition,
        object_id=created_site_condition.id,
        created_at=created_at,
        old_values=None,
        new_values={"start_date": "A", "end_date": "B"},
    )
    # 1 diff from deleted, always returns only one AuditEventType
    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.deleted,
        object_type=AuditObjectType.site_condition,
        object_id=deleted_site_condition.id,
        created_at=created_at,
        old_values={"start_date": "A", "end_date": "B"},
        new_values=None,
    )
    # 1 diff from archived, always returns only one AuditEventType, as deleted
    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.archived,
        object_type=AuditObjectType.site_condition,
        object_id=archived_site_condition.id,
        created_at=created_at,
        old_values={"archived_at": None},
        new_values={"archived_at": str(created_at)},
    )

    response = await execute_gql(
        query=project_with_audits_query, variables={"projectId": str(work_package.id)}
    )

    assert response["project"]
    assert response["project"]["id"] == str(work_package.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 3

    for audit in response["project"]["audits"]:
        if audit.get("actionType") == AuditActionType.CREATED.value:
            await assert_project_location_audit_response(
                db_session,
                audit,
                user=user,
                project=work_package,
                location=location,
                site_condition=created_site_condition,
                created_at=created_at,
                action_type=AuditActionType.CREATED,
                audit_key="siteCondition",
            )
        elif audit.get("actionType") == AuditActionType.DELETED.value:
            if audit.get("objectDetails", {}).get("id") == str(
                deleted_site_condition.id
            ):
                await assert_project_location_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    site_condition=deleted_site_condition,
                    created_at=created_at,
                    action_type=AuditActionType.DELETED,
                    audit_key="siteCondition",
                )
            else:
                await assert_project_location_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    site_condition=archived_site_condition,
                    created_at=created_at,
                    action_type=AuditActionType.DELETED,
                    audit_key="siteCondition",
                )
        else:
            assert False


async def assert_task_audit_response(
    db_session: AsyncSession,
    audit: dict[str, Any],
    user: User,
    project: WorkPackage,
    location: Location,
    task: Task,
    created_at: datetime,
    action_type: AuditActionType = AuditActionType.UPDATED,
    audit_key: str | None = None,
    new_value: str | list[str] | None = None,
    old_value: str | list[str] | None = None,
    added: list[str] | None = None,
    removed: list[str] | None = None,
) -> None:
    library_task = await DBData(db_session).library_task(task.library_task_id)
    assert audit
    assert audit["actionType"] == action_type.value
    assert audit["actor"]
    assert audit["actor"]["id"] == str(user.id)
    assert audit["actor"]["name"] == f"{user.first_name} {user.last_name}"
    assert audit["actor"]["role"] == user.role
    assert audit["objectDetails"]
    assert audit["objectDetails"]["id"] == str(task.id)
    assert audit["objectDetails"]["name"] == str(library_task.name)
    assert audit["objectDetails"]["location"]["id"] == str(location.id)
    assert audit["objectDetails"]["location"]["name"] == location.name
    assert audit["objectType"] == AuditObjectTypeGQL.TASK.value
    assert audit["timestamp"] == str(created_at).replace(" ", "T")
    assert audit["auditKey"] == audit_key

    if not audit.get("diffValues"):
        return
    if isinstance(new_value, list) or isinstance(old_value, list):
        assert audit["diffValues"]["newValues"] == new_value
        assert audit["diffValues"]["oldValues"] == old_value
        assert audit["diffValues"]["added"] == added
        assert audit["diffValues"]["removed"] == removed
    else:
        assert audit["diffValues"]["newValue"] == new_value
        assert audit["diffValues"]["oldValue"] == old_value


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_task_audits(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    work_package: WorkPackage = await WorkPackageFactory.persist(db_session)
    location: Location = await LocationFactory.persist(
        db_session, project_id=work_package.id
    )
    (
        updated_task,
        created_task,
        deleted_task,
        archived_task,
    ) = await TaskFactory.persist_many(db_session, size=4, location_id=location.id)

    user: User = await UserFactory.persist(db_session)
    event = await AuditEventFactory.persist(
        db_session,
        user_id=user.id,
        event_type=AuditEventType.task_updated,
    )

    created_at = datetime.now(timezone.utc)
    adt = AuditDiffType
    audit_data = [
        (
            adt.updated,
            updated_task.id,
            {"start_date": "x", "end_date": "y"},
            {"start_date": "A", "end_date": "B"},
        ),
        (adt.created, created_task.id, None, {"start_date": "A", "end_date": "B"}),
        (adt.deleted, deleted_task.id, {"start_date": "A", "end_date": "B"}, None),
        (
            adt.archived,
            archived_task.id,
            {"archived_at": None},
            {"archived_at": str(created_at)},
        ),
    ]
    for diff_type, task, old, new in audit_data:
        await AuditEventDiffFactory.persist(
            db_session,
            event_id=event.id,
            diff_type=diff_type,
            object_type=AuditObjectType.task,
            object_id=task,
            created_at=created_at,
            old_values=old,
            new_values=new,
        )

    response = await execute_gql(
        query=project_with_audits_query, variables={"projectId": str(work_package.id)}
    )

    assert response["project"]
    assert response["project"]["id"] == str(work_package.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 5

    for audit in response["project"]["audits"]:
        if audit.get("actionType") == AuditActionType.CREATED.value:
            await assert_task_audit_response(
                db_session,
                audit,
                user=user,
                project=work_package,
                location=location,
                task=created_task,
                created_at=created_at,
                action_type=AuditActionType.CREATED,
                audit_key="task",
            )
        elif audit.get("actionType") == AuditActionType.DELETED.value:
            if audit.get("objectDetails", {}).get("id") == str(deleted_task.id):
                await assert_task_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    task=deleted_task,
                    created_at=created_at,
                    action_type=AuditActionType.DELETED,
                    audit_key="task",
                )
            else:
                await assert_task_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    task=archived_task,
                    created_at=created_at,
                    action_type=AuditActionType.DELETED,
                    audit_key="task",
                )
        elif audit.get("actionType") == AuditActionType.UPDATED.value:
            if audit.get("auditKey") == "task_endDate":
                await assert_task_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    task=updated_task,
                    created_at=created_at,
                    audit_key="task_endDate",
                    old_value="y",
                    new_value="B",
                )
            else:
                await assert_task_audit_response(
                    db_session,
                    audit,
                    user=user,
                    project=work_package,
                    location=location,
                    task=updated_task,
                    created_at=created_at,
                    audit_key="task_startDate",
                    old_value="x",
                    new_value="A",
                )
        else:
            assert False


def assert_project_audit_response(
    audit: dict[str, Any],
    user: User,
    project: WorkPackage,
    created_at: datetime,
    action_type: AuditActionType = AuditActionType.UPDATED,
    audit_key: str | None = None,
    new_value: str | list[str] | None = None,
    old_value: str | list[str] | None = None,
    added: list[str] | None = None,
    removed: list[str] | None = None,
) -> None:
    assert audit
    assert audit["actionType"] == action_type.value
    assert audit["actor"]
    assert audit["actor"]["id"] == str(user.id)
    assert audit["actor"]["name"] == f"{user.first_name} {user.last_name}"
    assert audit["actor"]["role"] == user.role
    assert audit["objectDetails"]
    assert audit["objectDetails"]["id"] == str(project.id)
    assert audit["objectDetails"]["name"] == str(project.name)
    assert audit["objectType"] == AuditObjectTypeGQL.PROJECT.value
    assert audit["timestamp"] == str(created_at).replace(" ", "T")
    assert audit["auditKey"] == audit_key

    if not audit.get("diffValues"):
        return
    if isinstance(new_value, list) and isinstance(old_value, list):
        assert isinstance(added, list)
        assert isinstance(removed, list)
        assert not set(audit["diffValues"]["newValues"]) ^ set(new_value)
        assert not set(audit["diffValues"]["oldValues"]) ^ set(old_value)
        if added or audit["diffValues"]["added"]:
            assert not set(audit["diffValues"]["added"]) ^ set(added)
        if removed or audit["diffValues"]["removed"]:
            assert not set(audit["diffValues"]["removed"]) ^ set(removed)
    else:
        assert audit["diffValues"]["newValue"] == new_value
        assert audit["diffValues"]["oldValue"] == old_value


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_status_audits(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)
    work_package = await WorkPackageFactory.persist(
        db_session, status=ProjectStatus.COMPLETED
    )
    await LocationFactory.persist(db_session, project_id=work_package.id)

    status = [
        (None, "pending", AuditDiffType.created, AuditEventType.project_created),
        ("pending", "active", AuditDiffType.updated, AuditEventType.project_updated),
        ("active", "complete", AuditDiffType.updated, AuditEventType.project_updated),
    ]
    created_at = datetime.now(timezone.utc)
    for old, new, diff_type, event_type in status:
        event = await AuditEventFactory.persist(
            db_session,
            user_id=admin.id,
            event_type=event_type,
        )
        await AuditEventDiffFactory.persist(
            db_session,
            event_id=event.id,
            diff_type=diff_type,
            object_type=AuditObjectType.project,
            object_id=work_package.id,
            created_at=created_at,
            old_values={"status": old} if old else None,
            new_values={"status": new},
        )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(work_package.id)},
        user=admin,
    )

    assert response["project"]
    assert response["project"]["id"] == str(work_package.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 3
    action_types = [
        AuditActionType.CREATED,
        AuditActionType.UPDATED,
        AuditActionType.UPDATED,
    ]
    assert_values = [
        (None, "pending", "project"),
        ("pending", "active", "project_status"),
        ("active", "complete", "project_status"),
    ]
    for audit, action_type, values in zip(
        response["project"]["audits"], action_types, assert_values
    ):
        old, new, key = values
        assert_project_audit_response(
            audit,
            user=admin,
            project=work_package,
            created_at=created_at,
            action_type=action_type,
            audit_key=key,
            old_value=old,
            new_value=new,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_dates(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)

    created_at = datetime.now(timezone.utc)

    updated_project: WorkPackage = await WorkPackageFactory.persist(
        db_session, tenant_id=tenant.id
    )
    _ = await LocationFactory.persist(db_session, project_id=updated_project.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 2 diffs from update audit with 2 distinct keys on old/new values
    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=updated_project.id,
        created_at=created_at,
        old_values={"start_date": "x", "end_date": "y"},
        new_values={"start_date": "A", "end_date": "B"},
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(updated_project.id)},
        user=admin,
    )
    assert response["project"]
    assert response["project"]["id"] == str(updated_project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 2
    for audit in response["project"]["audits"]:
        if audit.get("auditKey") == "project_startDate":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_startDate",
                old_value="x",
                new_value="A",
            )
        elif audit.get("auditKey") == "project_endDate":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_endDate",
                old_value="y",
                new_value="B",
            )
        else:
            assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_library_data(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)

    created_at = datetime.now(timezone.utc)

    updated_project: WorkPackage = await WorkPackageFactory.persist(db_session)
    _ = await LocationFactory.persist(db_session, project_id=updated_project.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 1 field diff in the update audit implies a single set of old/new values
    old_library_division = await LibraryDivisionFactory.persist(db_session)
    new_library_division = await LibraryDivisionFactory.persist(db_session)
    old_library_asset_type = await LibraryAssetTypeFactory.persist(db_session)
    new_library_asset_type = await LibraryAssetTypeFactory.persist(db_session)
    old_library_project_type = await LibraryProjectTypeFactory.persist(db_session)
    new_library_project_type = await LibraryProjectTypeFactory.persist(db_session)
    old_work_type = await WorkTypeFactory.persist(db_session)
    new_work_type = await WorkTypeFactory.persist(db_session)
    old_library_region = await LibraryRegionFactory.persist(db_session)
    new_library_region = await LibraryRegionFactory.persist(db_session)

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=updated_project.id,
        created_at=created_at,
        old_values={
            "library_division_id": str(old_library_division.id),
            "library_asset_type_id": str(old_library_asset_type.id),
            "library_project_type_id": str(old_library_project_type.id),
            "work_type_ids": [str(old_work_type.id)],
            "library_region_id": str(old_library_region.id),
        },
        new_values={
            "library_division_id": str(new_library_division.id),
            "library_asset_type_id": str(new_library_asset_type.id),
            "library_project_type_id": str(new_library_project_type.id),
            "work_type_ids": [str(new_work_type.id)],
            "library_region_id": str(new_library_region.id),
        },
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(updated_project.id)},
        user=admin,
    )

    assert response["project"]
    assert response["project"]["id"] == str(updated_project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 5
    for audit in response["project"]["audits"]:
        if audit.get("auditKey") == "project_libraryDivisionId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_libraryDivisionId",
                old_value=old_library_division.name,
                new_value=new_library_division.name,
            )
        elif audit.get("auditKey") == "project_libraryAssetTypeId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_libraryAssetTypeId",
                old_value=old_library_asset_type.name,
                new_value=new_library_asset_type.name,
            )
        elif audit.get("auditKey") == "project_libraryProjectTypeId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_libraryProjectTypeId",
                old_value=old_library_project_type.name,
                new_value=new_library_project_type.name,
            )
        elif audit.get("auditKey") == "project_workTypeId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_workTypeId",
                old_value=old_library_project_type.name,
                new_value=new_library_project_type.name,
            )
        elif audit.get("auditKey") == "project_workTypeIds":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_workTypeIds",
                old_value=[old_work_type.name],
                new_value=[new_work_type.name],
                added=[new_work_type.name],
                removed=[old_work_type.name],
            )
        elif audit.get("auditKey") == "project_libraryRegionId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_libraryRegionId",
                old_value=old_library_region.name,
                new_value=new_library_region.name,
            )
        else:
            assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_contractor(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)

    created_at = datetime.now(timezone.utc)

    updated_project: WorkPackage = await WorkPackageFactory.persist(db_session)
    _ = await LocationFactory.persist(db_session, project_id=updated_project.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 1 field diff in the update audit implies a single set of old/new values
    old_contractor = await ContractorFactory.persist(db_session)
    new_contractor = await ContractorFactory.persist(db_session)

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=updated_project.id,
        created_at=created_at,
        old_values={"contractor_id": str(old_contractor.id)},
        new_values={"contractor_id": str(new_contractor.id)},
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(updated_project.id)},
        user=admin,
    )

    assert response["project"]
    assert response["project"]["id"] == str(updated_project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 1
    for audit in response["project"]["audits"]:
        if audit.get("auditKey") == "project_contractorId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_contractorId",
                old_value=old_contractor.name,
                new_value=new_contractor.name,
            )
        else:
            assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_manager(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)

    created_at = datetime.now(timezone.utc)

    updated_project: WorkPackage = await WorkPackageFactory.persist(db_session)
    _ = await LocationFactory.persist(db_session, project_id=updated_project.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 1 field diff in the update audit implies a single set of old/new values
    old_manager = await ManagerUserFactory.persist(db_session)
    new_manager = await ManagerUserFactory.persist(db_session)

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=updated_project.id,
        created_at=created_at,
        old_values={"manager_id": str(old_manager.id)},
        new_values={"manager_id": str(new_manager.id)},
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(updated_project.id)},
        user=admin,
    )

    assert response["project"]
    assert response["project"]["id"] == str(updated_project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 1
    for audit in response["project"]["audits"]:
        if audit.get("auditKey") == "project_managerId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_managerId",
                old_value=old_manager.get_name(),
                new_value=new_manager.get_name(),
            )
        else:
            assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_supervisor(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)

    created_at = datetime.now(timezone.utc)

    updated_project: WorkPackage = await WorkPackageFactory.persist(db_session)
    _ = await LocationFactory.persist(db_session, project_id=updated_project.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 1 field diff in the update audit implies a single set of old/new values
    old_supervisor = await SupervisorUserFactory.persist(db_session)
    new_supervisor = await SupervisorUserFactory.persist(db_session)

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=updated_project.id,
        created_at=created_at,
        old_values={"supervisor_id": str(old_supervisor.id)},
        new_values={"supervisor_id": str(new_supervisor.id)},
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(updated_project.id)},
        user=admin,
    )

    assert response["project"]
    assert response["project"]["id"] == str(updated_project.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 1
    for audit in response["project"]["audits"]:
        if audit.get("auditKey") == "project_supervisorId":
            assert_project_audit_response(
                audit,
                user=admin,
                project=updated_project,
                created_at=created_at,
                audit_key="project_supervisorId",
                old_value=old_supervisor.get_name(),
                new_value=new_supervisor.get_name(),
            )
        else:
            assert False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_updated_additional_supervisors(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    admin = await AdminUserFactory.persist(db_session)
    created_at = datetime.now(timezone.utc)
    work_package: WorkPackage = await WorkPackageFactory.persist(db_session)
    _ = await LocationFactory.persist(db_session, project_id=work_package.id)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    # 1 field diff in the update audit implies a single set of old/new values
    old_supervisors = await SupervisorUserFactory.persist_many(db_session, size=3)
    new_supervisors = await SupervisorUserFactory.persist_many(db_session, size=5)

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.project,
        object_id=work_package.id,
        created_at=created_at,
        old_values={
            "additional_supervisor_ids": [str(sup.id) for sup in old_supervisors]
        },
        new_values={
            "additional_supervisor_ids": [str(sup.id) for sup in new_supervisors]
        },
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(work_package.id)},
        user=admin,
    )

    old_names = [sup.get_name() for sup in old_supervisors]
    new_names = [sup.get_name() for sup in new_supervisors]

    assert response["project"]
    assert response["project"]["id"] == str(work_package.id)
    assert response["project"]["audits"]
    assert len(response["project"]["audits"]) == 1
    audit = response["project"]["audits"][0]
    assert_project_audit_response(
        audit,
        user=admin,
        project=work_package,
        created_at=created_at,
        audit_key="project_additionalSupervisorIds",
        old_value=old_names,
        new_value=new_names,
        added=new_names,
        removed=old_names,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_archived_objects(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    db_data: DBData,
) -> None:
    """Retrieve audit records for archived task, site condition, and daily report objects
    when all are archived
    and the associated location is also archived
    """

    admin = await AdminUserFactory.persist(db_session)
    archived_at = datetime.now(timezone.utc) + timedelta(days=1)
    work_package = await WorkPackageFactory.persist(
        db_session, status=ProjectStatus.COMPLETED
    )
    await LocationFactory.persist(db_session, project_id=work_package.id)
    loc = await LocationFactory.persist(
        db_session, project_id=work_package.id, archived_at=archived_at
    )
    sc = await SiteConditionFactory.persist(
        db_session,
        location_id=loc.id,
        archived_at=archived_at,
    )
    library_sc = await db_data.library_site_condition(sc.library_site_condition_id)
    task = await TaskFactory.persist(
        db_session,
        location_id=loc.id,
        archived_at=archived_at,
    )
    library_task = await db_data.library_task(task.library_task_id)
    dr = await DailyReportFactory.persist(
        db_session, project_location_id=loc.id, archived_at=archived_at
    )
    # alias types for shorter names
    adt = AuditDiffType
    aot = AuditObjectType
    aet = AuditEventType
    models = [
        (sc, aot.site_condition),
        (task, aot.task),
        (dr, aot.daily_report),
    ]
    audit_types = [
        [
            (aet.site_condition_created, adt.created),
            (aet.site_condition_archived, adt.archived),
        ],
        [
            (aet.task_created, adt.created),
            (aet.task_archived, adt.archived),
        ],
        [
            (aet.daily_report_created, adt.created),
            (aet.daily_report_archived, adt.archived),
        ],
    ]

    events = []
    diffs = []
    # for the task, site condition, and daily report
    # build an audit event and diff
    # for the created and archived states
    for _model, _audits in zip(models, audit_types):
        model, model_type = _model
        for event_type, diff_type in _audits:
            event = await AuditEventFactory.persist(
                db_session,
                user_id=admin.id,
                event_type=event_type,
            )
            events.append(event)
            diff = await AuditEventDiffFactory.persist(
                db_session,
                event_id=event.id,
                diff_type=diff_type,
                object_type=model_type,
                object_id=model.id,  # type: ignore
                created_at=datetime.now(timezone.utc),
                old_values=None,
                new_values=None,
            )
            diffs.append(diff)

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(work_package.id)},
        user=admin,
    )
    audits = response["project"]["audits"]
    assert len(audits) == len(diffs) == len(events) == 6
    for audit, diff in zip(audits, diffs[::-1]):
        assert audit["actor"]["id"] == str(admin.id)
        assert audit["actor"]["name"] == str(admin.get_name())
        assert audit["actor"]["role"] == admin.role
        assert audit["objectDetails"]["id"] == str(diff.object_id)
        if diff.object_type == aot.daily_report:
            assert "name" not in audit["objectDetails"]
        elif diff.object_type == aot.task:
            assert audit["objectDetails"]["name"] == library_task.name
        elif diff.object_type == aot.site_condition:
            assert audit["objectDetails"]["name"] == library_sc.name
        assert audit["objectDetails"]["location"]["name"] == loc.name
        assert audit["objectDetails"]["location"]["name"] == loc.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_audits_archived_evaluated_site_conditions(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Check we do not display either the create or archive audits
    for evaluated site conditions (remove with WSAPP-125)
    """
    admin = await AdminUserFactory.persist(db_session)
    project: WorkPackage = await WorkPackageFactory.persist(db_session)
    archive_time = datetime.now(timezone.utc)
    location = await LocationFactory.persist(
        db_session, project_id=project.id, archived_at=archive_time
    )
    # evaluated site conditions are not created with a `user_id`
    sc = await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location.id,
        archived_at=archive_time,
    )

    # evaluated event and diff when site condition created (evaluated)
    event_evaluated = await AuditEventFactory.persist(
        db_session,
        user_id=None,
        event_type=AuditEventType.site_condition_evaluated,
    )
    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event_evaluated.id,
        diff_type=AuditDiffType.created,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        created_at=datetime.now(timezone.utc),
        old_values=None,
        new_values={"some": "site-condition-data"},
    )

    # event and diff when location archive cascades and archives site condition
    event_create = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event_create.id,
        diff_type=AuditDiffType.archived,
        object_type=AuditObjectType.site_condition,
        object_id=sc.id,
        created_at=datetime.now(timezone.utc),
        old_values={"archived_at": None},
        new_values={"archived_at": str(datetime.now(timezone.utc))},
    )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        user=admin,
    )

    assert "errors" not in response

    assert len(response["project"]["audits"]) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_update_from_null_values(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Check we show audit history when a project field is updated to or from None
    for nullable and not nullable project fields
    """
    admin = await AdminUserFactory.persist(db_session)
    manager = await ManagerUserFactory.persist(db_session)
    supervisor = await SupervisorUserFactory.persist(db_session)
    contractor = await ContractorFactory.persist(db_session)
    project: WorkPackage = await WorkPackageFactory.persist(
        db_session,
        asset_type_id=None,
    )
    await LocationFactory.persist(db_session, project_id=project.id)
    lat = await LibraryAssetTypeFactory.persist(db_session)
    lr = await LibraryRegionFactory.persist(db_session)
    ld = await LibraryDivisionFactory.persist(db_session)
    lpt = await LibraryProjectTypeFactory.persist(db_session)

    event = await AuditEventFactory.persist(
        db_session,
        user_id=admin.id,
        event_type=AuditEventType.project_updated,
    )
    test_inputs = [
        ("contractor_id", str(contractor.id)),
        ("asset_type_id", str(lat.id)),
        ("division_id", str(ld.id)),
        ("region_id", str(lr.id)),
        ("work_type_id", str(lpt.id)),
        ("manager_id", str(manager.id)),
        ("primary_assigned_user_id", str(supervisor.id)),
    ]
    for key, value in test_inputs:
        await AuditEventDiffFactory.persist(
            db_session,
            event_id=event.id,
            diff_type=AuditDiffType.updated,
            object_type=AuditObjectType.project,
            object_id=project.id,
            created_at=datetime.now(timezone.utc),
            old_values={key: None},
            new_values={key: value},
        )
        await AuditEventDiffFactory.persist(
            db_session,
            event_id=event.id,
            diff_type=AuditDiffType.updated,
            object_type=AuditObjectType.project,
            object_id=project.id,
            created_at=datetime.now(timezone.utc),
            old_values={key: value},
            new_values={key: None},
        )

    response = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        user=admin,
    )
    test_values = [
        ("project_contractorId", str(contractor.id)),
        ("project_libraryAssetTypeId", str(lat.id)),
        ("project_libraryDivisionId", str(ld.id)),
        ("project_libraryRegionId", str(lr.id)),
        ("project_workTypeId", str(lpt.id)),
        ("project_managerId", str(manager.id)),
        ("project_supervisorId", str(supervisor.id)),
    ]
    assert "errors" not in response
    assert response["project"]
    assert response["project"]["audits"]
    project_audits = response["project"]["audits"]
    assert len(project_audits) == len(test_values) * 2
    count = 0
    # reverse ordering to match project audit order
    for key, value in test_values[::-1]:
        # check two diffs per test value
        for i in [count, count + 1]:
            assert project_audits[i]["auditKey"] == key
        count += 2
