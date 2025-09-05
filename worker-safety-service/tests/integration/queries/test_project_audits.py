import pytest

from tests.factories import (
    AdminUserFactory,
    AuditEventDiffFactory,
    AuditEventFactory,
    ManagerUserFactory,
    SiteConditionFactory,
    SupervisorUserFactory,
    TenantFactory,
    ViewerUserFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import (
    AsyncSession,
    AuditDiffType,
    AuditEventType,
    AuditObjectType,
    WorkPackage,
)

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
            }
            actionType
            objectType
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
                    name
                }
                ... on SiteCondition {
                    name
                    location {
                        name
                    }
                }
                ... on Task {
                    name
                    location {
                        name
                    }
                }
                ... on DailyReport {
                    location {
                        name
                    }
                }
            }
        }
    }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_query_requires_supervisor_access(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    project: WorkPackage = await WorkPackageFactory.persist(db_session)

    viewer = await ViewerUserFactory.persist(db_session)
    data = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        raw=True,
        user=viewer,
    )
    assert data.json().get("errors"), f"On role {viewer.role}"

    supervisor = await SupervisorUserFactory.persist(db_session)
    data = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        raw=True,
        user=supervisor,
    )
    assert data.json().get("errors") is None
    assert data.json()["data"]["project"]["id"] == str(project.id)

    manager = await ManagerUserFactory.persist(db_session)
    data = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        raw=True,
        user=manager,
    )
    assert data.json().get("errors") is None
    assert data.json()["data"]["project"]["id"] == str(project.id)

    admin = await AdminUserFactory.persist(db_session)
    data = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        raw=True,
        user=admin,
    )
    assert data.json().get("errors") is None
    assert data.json()["data"]["project"]["id"] == str(project.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_query_with_empty_user(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant, admin = await TenantFactory.new_with_admin(db_session)
    (
        updated_site_condition,
        project,
        _,
    ) = await SiteConditionFactory.with_project_and_location(
        db_session, project_kwargs={"tenant_id": tenant.id}
    )
    event = await AuditEventFactory.persist(
        db_session,
        # NOTE site_condition_evaluated events are ignored in the audit trail
        event_type=AuditEventType.site_condition_created,
    )

    await AuditEventDiffFactory.persist(
        db_session,
        event_id=event.id,
        diff_type=AuditDiffType.updated,
        object_type=AuditObjectType.site_condition,
        object_id=updated_site_condition.id,
        old_values={"start_date": "x"},
        new_values={"start_date": "A"},
    )

    data = await execute_gql(
        query=project_with_audits_query,
        variables={"projectId": str(project.id)},
        user=admin,
    )
    assert data["project"]["id"] == str(project.id)
    audits = data["project"]["audits"]
    assert len(audits) == 1
    assert audits[0]["actor"] is None
