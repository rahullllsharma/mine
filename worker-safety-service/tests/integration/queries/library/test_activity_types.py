import uuid
from typing import Any

import pytest

from tests.factories import LibraryActivityTypeFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_activity_types_query = {
    "operation_name": "activityTypesLibrary",
    "query": """
query activityTypesLibrary ($orderBy: [OrderBy!]) {
  activityTypesLibrary (orderBy: $orderBy) {
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
    data = await execute_gql(
        **library_activity_types_query, variables=kwargs, user=user
    )
    activity_types: list[dict] = data["activityTypesLibrary"]
    return activity_types


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_types_library_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Simple library activity types check"""

    tenant = await TenantFactory.default_tenant(db_session)
    await LibraryActivityTypeFactory.many_with_link(db_session, tenant.id, size=2)

    # Check all activity_types
    activity_types = await call_query(execute_gql)
    assert activity_types
    first_activity_type = activity_types[0]
    assert uuid.UUID(first_activity_type["id"])
    assert first_activity_type["name"]
    assert isinstance(first_activity_type["name"], str)

    # just adding a activity type does not show it for a tenant
    new_activity_type_id = str(
        (
            await LibraryActivityTypeFactory.persist(
                db_session, name="new_activity_type"
            )
        ).id
    )
    activity_types = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in activity_types}
    assert new_activity_type_id not in ids

    # we must link it to a tenant explicitly
    new_tenant_activity_type = await LibraryActivityTypeFactory.with_link(
        db_session, tenant.id, name="linked to a tenant"
    )
    activity_types = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in activity_types}
    assert str(new_tenant_activity_type.id) in ids

    # and new tenants do not have library activity_types
    new_tenant, new_admin = await TenantFactory.new_with_admin(db_session)
    activity_types = await call_query(execute_gql, orderBy=None, user=new_admin)
    assert activity_types == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_types_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library activity types order"""

    tenant = await TenantFactory.default_tenant(db_session)
    activity_type1_id, activity_type2_id, activity_type3_id = [
        str(item.id)
        for item in await LibraryActivityTypeFactory.many_with_link(
            db_session,
            tenant.id,
            per_item_kwargs=[{"name": "á 1"}, {"name": "A 2"}, {"name": "a 3"}],
        )
    ]
    expected_order = [activity_type1_id, activity_type2_id, activity_type3_id]

    # No order
    activity_types = await call_query(execute_gql, orderBy=None)
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert set(activity_types_ids) == set(expected_order)

    activity_types = await call_query(execute_gql, orderBy=[])
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert set(activity_types_ids) == set(expected_order)

    # ASC
    activity_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert activity_types_ids == expected_order

    # DESC
    activity_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert activity_types_ids == list(reversed(expected_order))

    # with multiple order by should match first
    activity_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert activity_types_ids == expected_order

    activity_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert activity_types_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_types_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    activity_type1_id, activity_type2_id = [
        str(item.id)
        for item in await LibraryActivityTypeFactory.many_with_link(
            db_session,
            tenant.id,
            per_item_kwargs=[{"name": "cenas"}, {"name": "Cenas"}],
        )
    ]
    expected_order = sorted([activity_type1_id, activity_type2_id])

    activity_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    activity_types_ids = [i["id"] for i in activity_types if i["id"] in expected_order]
    assert activity_types_ids == expected_order
