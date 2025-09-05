import uuid
from typing import Any

import pytest

from tests.factories import LibraryActivityGroupFactory, TenantFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_activity_groups_query = {
    "operation_name": "activityGroupsLibrary",
    "query": """
query activityGroupsLibrary ($orderBy: [OrderBy!], $tasksOrderBy: [LibraryTaskOrderBy!]) {
  activityGroupsLibrary (orderBy: $orderBy) {
    id
    name
    tasks (orderBy: $tasksOrderBy) {
        id
        name
    }
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
        **library_activity_groups_query, variables=kwargs, user=user
    )
    activity_groups: list[dict] = data["activityGroupsLibrary"]
    return activity_groups


@pytest.mark.asyncio
@pytest.mark.integration
async def test_activity_groups_library_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Simple library activity groups check"""

    tenant = await TenantFactory.default_tenant(db_session)
    await LibraryActivityGroupFactory.many_with_link(db_session, tenant.id, size=2)

    # Check all activity_groups
    activity_groups = await call_query(execute_gql)
    assert activity_groups
    first_activity_group = activity_groups[0]
    assert uuid.UUID(first_activity_group["id"])
    assert first_activity_group["name"]
    assert isinstance(first_activity_group["name"], str)

    # just adding a activity group does not show it for a tenant
    new_activity_group_id = str(
        (await LibraryActivityGroupFactory.persist(db_session)).id
    )
    activity_groups = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in activity_groups}
    assert new_activity_group_id not in ids

    # we must link it to a tenant explicitly
    new_tenant_activity_group = await LibraryActivityGroupFactory.with_link(
        db_session, tenant.id
    )
    activity_groups = await call_query(execute_gql, orderBy=None)
    ids = {d["id"] for d in activity_groups}
    assert str(new_tenant_activity_group.id) in ids

    # and new tenants do not have library activity_groups
    _, new_admin = await TenantFactory.new_with_admin(db_session)
    activity_groups = await call_query(execute_gql, orderBy=None, user=new_admin)
    assert activity_groups == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_groups_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library activity groups order"""

    tenant = await TenantFactory.default_tenant(db_session)
    activity_group1_id, activity_group2_id, activity_group3_id = [
        str(item.id)
        for item in await LibraryActivityGroupFactory.many_with_link(
            db_session,
            tenant.id,
            per_item_kwargs=[{"name": "á 1"}, {"name": "A 2"}, {"name": "a 3"}],
        )
    ]
    expected_order = [activity_group1_id, activity_group2_id, activity_group3_id]

    # No order
    activity_groups = await call_query(execute_gql, orderBy=None)
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert set(activity_groups_ids) == set(expected_order)

    activity_groups = await call_query(execute_gql, orderBy=[])
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert set(activity_groups_ids) == set(expected_order)

    # ASC
    activity_groups = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert activity_groups_ids == expected_order

    # DESC
    activity_groups = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert activity_groups_ids == list(reversed(expected_order))

    # with multiple order by should match first
    activity_groups = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert activity_groups_ids == expected_order

    activity_groups = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert activity_groups_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_activity_groups_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    activity_group1_id, activity_group2_id = [
        str(item.id)
        for item in await LibraryActivityGroupFactory.many_with_link(
            db_session,
            tenant.id,
            per_item_kwargs=[{"name": "cenas"}, {"name": "Cenas"}],
        )
    ]
    expected_order = sorted([activity_group1_id, activity_group2_id])

    activity_groups = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    activity_groups_ids = [
        i["id"] for i in activity_groups if i["id"] in expected_order
    ]
    assert activity_groups_ids == expected_order
