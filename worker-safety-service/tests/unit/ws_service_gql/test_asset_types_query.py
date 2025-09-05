import pytest

from worker_safety_service.graphql.main import schema


@pytest.mark.asyncio
@pytest.mark.unit
async def test_asset_types_query() -> None:
    query = """
    query TestAssetTypesQuery{
      assetTypesLibrary {
        id
        name
      }
    }
    """

    result = await schema.execute(query)

    assert result.errors is not None
