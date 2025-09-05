import pytest

from tests.factories import CrewLeaderFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

all_crew_leaders_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery {
  crewLeaders {
    id
    name
    lanid
    companyName
  }
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_crew_leaders_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    await CrewLeaderFactory.persist_many(db_session, size=4)

    response = await execute_gql(**all_crew_leaders_query)

    assert len(response["crewLeaders"]) == 4
