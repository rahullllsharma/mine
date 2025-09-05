import uuid
from typing import Any

import pytest

from tests.factories import LibraryRegionFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_regions_query = {
    "operation_name": "regionsLibrary",
    "query": """
query regionsLibrary ($orderBy: [OrderBy!]) {
  regionsLibrary (orderBy: $orderBy) {
    id
    name
  }
}
""",
}


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    user = None
    if "user" in kwargs:
        user = kwargs["user"]
        del kwargs["user"]
    data = await execute_gql(**library_regions_query, variables=kwargs, user=user)
    regions: list[dict] = data["regionsLibrary"]
    return regions


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_regions_library_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Simple library regions check"""

    # Check all regions
    regions = await call_query(execute_gql)
    assert regions
    first_region = regions[0]
    assert uuid.UUID(first_region["id"])
    assert first_region["name"]
    assert isinstance(first_region["name"], str)

    # just adding a region does not show it for a tenant
    new_region_id = str(
        (await LibraryRegionFactory.persist(db_session, name="new_region")).id
    )
    regions = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in regions}
    assert new_region_id not in ids

    # we must link it to a tenant explicitly
    tenant = await TenantFactory.default_tenant(db_session)
    new_tenant_region = await LibraryRegionFactory.with_link(
        tenant.id, db_session, name="linked to a tenant"
    )
    regions = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in regions}
    assert str(new_tenant_region.id) in ids

    # and new tenants do not have library regions
    new_tenant, new_admin = await TenantFactory.new_with_admin(db_session)
    regions = await call_query(execute_gql, orderBy=None, user=new_admin)
    assert regions == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_regions_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library regions order"""

    tenant = await TenantFactory.default_tenant(db_session)
    region3_id = str(
        (await LibraryRegionFactory.with_link(tenant.id, db_session, name="a 3")).id
    )
    region1_id = str(
        (await LibraryRegionFactory.with_link(tenant.id, db_session, name="á 1")).id
    )
    region2_id = str(
        (await LibraryRegionFactory.with_link(tenant.id, db_session, name="A 2")).id
    )
    expected_order = [region1_id, region2_id, region3_id]

    # No order result equal to NAME ASC
    regions = await call_query(execute_gql, orderBy=None)
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == expected_order

    regions = await call_query(execute_gql, orderBy=[])
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == expected_order

    # NAME ASC
    regions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == expected_order

    # NAME DESC
    regions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == list(reversed(expected_order))

    # with multiple order by should match first
    regions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == expected_order

    regions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_regions_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    region1_id = str(
        (await LibraryRegionFactory.with_link(tenant.id, db_session, name="cenas")).id
    )
    region2_id = str(
        (await LibraryRegionFactory.with_link(tenant.id, db_session, name="Cenas")).id
    )
    expected_order = sorted([region1_id, region2_id])

    regions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    regions_ids = [i["id"] for i in regions if i["id"] in expected_order]
    assert regions_ids == expected_order
