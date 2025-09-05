import uuid
from typing import Any

import pytest

from tests.factories import LibraryAssetTypeFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_asset_types_query = {
    "operation_name": "assetTypesLibrary",
    "query": """
query assetTypesLibrary ($orderBy: [OrderBy!]) {
  assetTypesLibrary (orderBy: $orderBy) {
    id
    name
  }
}
""",
}


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**library_asset_types_query, variables=kwargs)
    asset_types: list[dict] = data["assetTypesLibrary"]
    return asset_types


@pytest.mark.asyncio
@pytest.mark.integration
async def test_asset_types_library_query(execute_gql: ExecuteGQL) -> None:
    """Simple library asset types check"""

    # Check all asset types
    asset_types = await call_query(execute_gql)
    assert asset_types
    first_asset_type = asset_types[0]
    assert uuid.UUID(first_asset_type["id"])
    assert first_asset_type["name"]
    assert isinstance(first_asset_type["name"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_asset_types_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library asset types order"""

    asset_type1_id = str(
        (await LibraryAssetTypeFactory.persist(db_session, name="á 1")).id
    )
    asset_type2_id = str(
        (await LibraryAssetTypeFactory.persist(db_session, name="A 2")).id
    )
    asset_type3_id = str(
        (await LibraryAssetTypeFactory.persist(db_session, name="a 3")).id
    )
    expected_order = [asset_type1_id, asset_type2_id, asset_type3_id]

    # No order
    asset_types = await call_query(execute_gql, orderBy=None)
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert set(asset_types_ids) == set(expected_order)

    asset_types = await call_query(execute_gql, orderBy=[])
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert set(asset_types_ids) == set(expected_order)

    # ASC
    asset_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert asset_types_ids == expected_order

    # DESC
    asset_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert asset_types_ids == list(reversed(expected_order))

    # with multiple order by should match first
    asset_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert asset_types_ids == expected_order

    asset_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert asset_types_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_asset_types_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    asset_type1_id = str(
        (await LibraryAssetTypeFactory.persist(db_session, name="cenas")).id
    )
    asset_type2_id = str(
        (await LibraryAssetTypeFactory.persist(db_session, name="Cenas")).id
    )
    expected_order = sorted([asset_type1_id, asset_type2_id])

    # duplicated name
    asset_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    asset_types_ids = [i["id"] for i in asset_types if i["id"] in expected_order]
    assert asset_types_ids == expected_order
