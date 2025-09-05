import pytest

from tests.factories import (
    AdminUserFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import valid_project_request
from worker_safety_service.models import AsyncSession

create_project_mutation = {
    "operation_name": "CreateProject",
    "query": """
mutation CreateProject($project: CreateProjectInput!) {
  project: createProject(project: $project) {
    id name locations { id }
  }
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_create_project(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a project under roles that do have that permission
    """

    manager = await ManagerUserFactory.persist(db_session)
    project = await valid_project_request(db_session)
    data = await execute_gql(
        **create_project_mutation, variables={"project": project}, user=manager
    )

    assert "project" in data

    admin = await AdminUserFactory.persist(db_session)
    project = await valid_project_request(db_session)
    data = await execute_gql(
        **create_project_mutation, variables={"project": project}, user=admin
    )

    assert "project" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_can_not_create_project(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Attempts to create a project for roles that do not have the permission
    """
    viewer = await ViewerUserFactory.persist(db_session)

    project = await valid_project_request(db_session)
    resp = await execute_gql(
        **create_project_mutation, variables={"project": project}, raw=True, user=viewer
    )
    data = resp.json()

    assert "errors" in data
    messages = [x["message"] for x in data["errors"]]
    message = messages[0]
    assert "User is not authorized to create projects" in message

    supervisor = await SupervisorUserFactory.persist(db_session)

    project = await valid_project_request(db_session)
    resp = await execute_gql(
        **create_project_mutation,
        variables={"project": project},
        raw=True,
        user=supervisor
    )
    data = resp.json()

    assert "errors" in data
    messages = [x["message"] for x in data["errors"]]
    message = messages[0]
    assert "User is not authorized to create projects" in message
