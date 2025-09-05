import uuid
from typing import Any

import pytest

from tests.factories import LibraryDivisionFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_divisions_query = {
    "operation_name": "divisionsLibrary",
    "query": """
query divisionsLibrary ($orderBy: [OrderBy!]) {
  divisionsLibrary (orderBy: $orderBy) {
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
    data = await execute_gql(**library_divisions_query, variables=kwargs, user=user)
    divisions: list[dict] = data["divisionsLibrary"]
    return divisions


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_divisions_library_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Simple library divisions check"""
    # Check all divisions
    divisions = await call_query(execute_gql)
    assert divisions
    first_division = divisions[0]
    assert uuid.UUID(first_division["id"])
    assert first_division["name"]
    assert isinstance(first_division["name"], str)

    # just adding a division does not show it for a tenant
    new_division_id = str(
        (await LibraryDivisionFactory.persist(db_session, name="new_division")).id
    )
    divisions = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in divisions}
    assert new_division_id not in ids

    # we must link it to a tenant explicitly
    tenant = await TenantFactory.default_tenant(db_session)
    new_tenant_division = await LibraryDivisionFactory.with_link(
        tenant.id, db_session, name="linked to a tenant"
    )
    divisions = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in divisions}
    assert str(new_tenant_division.id) in ids

    # and new tenants do not have library divisions
    new_tenant, new_admin = await TenantFactory.new_with_admin(db_session)
    divisions = await call_query(execute_gql, orderBy=None, user=new_admin)
    assert divisions == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_divisions_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library divisions order"""
    tenant = await TenantFactory.default_tenant(db_session)

    division1_id = str(
        (await LibraryDivisionFactory.with_link(tenant.id, db_session, name="á 1")).id
    )
    division2_id = str(
        (await LibraryDivisionFactory.with_link(tenant.id, db_session, name="A 2")).id
    )
    division3_id = str(
        (await LibraryDivisionFactory.with_link(tenant.id, db_session, name="a 3")).id
    )
    expected_order = [division1_id, division2_id, division3_id]

    # No order
    divisions = await call_query(execute_gql, orderBy=None)
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert set(divisions_ids) == set(expected_order)

    divisions = await call_query(execute_gql, orderBy=[])
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert set(divisions_ids) == set(expected_order)

    # ASC
    divisions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert divisions_ids == expected_order

    # DESC
    divisions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert divisions_ids == list(reversed(expected_order))

    # with multiple order by should match first
    divisions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert divisions_ids == expected_order

    divisions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert divisions_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_divisions_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    division1_id = str(
        (await LibraryDivisionFactory.with_link(tenant.id, db_session, name="cenas")).id
    )
    division2_id = str(
        (await LibraryDivisionFactory.with_link(tenant.id, db_session, name="cenas")).id
    )
    expected_order = sorted([division1_id, division2_id])

    divisions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    divisions_ids = [i["id"] for i in divisions if i["id"] in expected_order]
    assert divisions_ids == expected_order
