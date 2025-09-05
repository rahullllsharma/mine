import string

import pytest

from tests.factories import AdminUserFactory
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import create_project_mutation, valid_project_request
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_project_number_as_alphanumeric(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # TODO maybe this should be extend to test project create

    # Create project data
    user = await AdminUserFactory.persist(db_session)
    project_data = await valid_project_request(db_session)

    # Allowed to be None
    # TODO: Should be allowed to be None but the GraphQL API still does not support it.

    # Not allowed to be empty
    project_data["number"] = ""
    data = await execute_gql(
        user=user,
        **create_project_mutation,
        variables={"project": project_data},
        raw=True,
    )
    assert data.json()["errors"], "Project number must have at least 1 length"

    # All alpha numeric
    project_data["number"] = string.ascii_letters + string.digits
    data = await execute_gql(
        user=user, **create_project_mutation, variables={"project": project_data}
    )
    assert data["project"]["number"] == project_data["number"]

    # Only alpha numeric
    for invalid_char in " .;_-":
        project_data["number"] = "aaaa" + invalid_char
        data = await execute_gql(
            user=user,
            **create_project_mutation,
            variables={"project": project_data},
        )
        assert data["project"]["number"] == project_data["number"]
