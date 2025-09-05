import pytest

from tests.integration.conftest import ExecuteGQL
from worker_safety_service.config import settings

query_system = """
query TestQuery {
  system {
    version
  }
}
"""


@pytest.mark.asyncio
@pytest.mark.integration
async def test_query_system(execute_gql: ExecuteGQL) -> None:
    data = await execute_gql(query=query_system)
    assert data["system"]["version"] == settings.APP_VERSION
