import pytest
from fastapi import status
from httpx import AsyncClient

from tests.factories import (
    ContractorFactory,
    LocationFactory,
    ManagerUserFactory,
    SiteConditionFactory,
    SupervisorUserFactory,
    TaskFactory,
    TenantFactory,
    WorkPackageFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

query_managers = """
query Query {
  managers {
    id
  }
}
"""

query_contractors = """
query Query {
  contractors {
    id
  }
}
"""

query_supervisors = """
query Query {
  supervisors {
    id
  }
}
"""

query_project = """
  query project($projectId: UUID!) {
    project(projectId: $projectId) {
      id
    }
  }
"""


query_projects = """
  query Projects {
    projects {
      id
    }
  }
"""

query_project_locations = """
query Query {
  projectLocations {
    id
  }
}
"""

query_site_conditions = """
query Query {
  siteConditions {
    id
  }
}
"""

query_tasks = """
query Query {
  tasks {
    id
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrieve_managers_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded = await ManagerUserFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )

    # Query item in tenant
    post_data = {"operation_name": "Query", "query": query_managers}
    response = await execute_gql(**post_data, raw=True)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["data"]["managers"]
    managers = [m["id"] for m in data["data"]["managers"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in managers)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrive_supervisors_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded = await SupervisorUserFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )

    # Retrieve on primary tenant
    post_data = {"operation_name": "Query", "query": query_supervisors}
    response = await execute_gql(**post_data, raw=True)
    data = response.json()

    assert data["data"]["supervisors"] is not None
    supervisor_ids = [c["id"] for c in data["data"]["supervisors"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in supervisor_ids)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skip  # TODO: Enable when tenants are implemented for contractors
async def test_can_not_retrive_contractors_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded = await ContractorFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )

    # Retrieve on primary tenant
    post_data = {"operation_name": "Query", "query": query_contractors}
    response = await execute_gql(**post_data, raw=True)
    data = response.json()

    assert data["data"]["contractors"] is not None
    contractor_ids = [c["id"] for c in data["data"]["contractors"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in contractor_ids)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrieve_project_from_other_tenant(
    db_session: AsyncSession, test_client: AsyncClient
) -> None:
    """
    Creates a project in a secondary tenant and tried to retrieve in the default
    tenant. This should fail.
    """

    secondary_tenant = await TenantFactory.persist(db_session)
    project = await WorkPackageFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )

    post_data = {
        "operationName": "project",
        "query": query_project,
        "variables": {"projectId": str(project.id)},
    }
    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    message = data["errors"][0]["message"]
    assert "not found" in message


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrieve_multiple_projects_from_other_tenant(
    db_session: AsyncSession, test_client: AsyncClient
) -> None:
    """
    Creates a project in a secondary tenant and tried to retrieve in the default
    tenant. This should fail.
    """

    # Create 3 in secondary tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded = await WorkPackageFactory.persist(
        db_session,
        tenant_id=secondary_tenant.id,
    )

    # Create 3 in default tenant
    await WorkPackageFactory.persist_many(
        db_session,
        size=3,
    )

    post_data = {
        "operationName": "Projects",
        "query": query_projects,
    }
    response = await test_client.post("/graphql", json=post_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["data"]["projects"]
    project_ids = [c["id"] for c in data["data"]["projects"]]

    assert not (str(excluded.id) in project_ids)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrive_project_location_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded_project = await WorkPackageFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )
    excluded = await LocationFactory.persist(db_session, project_id=excluded_project.id)

    # Retrieve on primary tenant
    post_data = {"operation_name": "Query", "query": query_project_locations}
    response = await execute_gql(**post_data, raw=True)
    data = response.json()

    assert data["data"]["projectLocations"] is not None
    project_location_ids = [c["id"] for c in data["data"]["projectLocations"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in project_location_ids)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrive_site_conditions_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded_project = await WorkPackageFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )
    excluded_project_location = await LocationFactory.persist(
        db_session, project_id=excluded_project.id
    )
    excluded = await SiteConditionFactory.persist(
        db_session, location_id=excluded_project_location.id
    )

    # Retrieve on primary tenant
    post_data = {"operation_name": "Query", "query": query_site_conditions}
    response = await execute_gql(**post_data, raw=True)
    data = response.json()

    assert data["data"]["siteConditions"] is not None
    site_condition_ids = [c["id"] for c in data["data"]["siteConditions"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in site_condition_ids)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_retrive_tasks_from_other_tenants(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Create item not in tenant
    secondary_tenant = await TenantFactory.persist(db_session)
    excluded_project = await WorkPackageFactory.persist(
        db_session, tenant_id=secondary_tenant.id
    )
    excluded_project_location = await LocationFactory.persist(
        db_session, project_id=excluded_project.id
    )
    excluded = await TaskFactory.persist(
        db_session, location_id=excluded_project_location.id
    )

    # Retrieve on primary tenant
    post_data = {"operation_name": "Query", "query": query_tasks}
    response = await execute_gql(**post_data, raw=True)
    data = response.json()

    assert data["data"]["tasks"] is not None
    task_ids = [c["id"] for c in data["data"]["tasks"]]

    # Assert item really is not in tenant
    assert not (str(excluded.id) in task_ids)
