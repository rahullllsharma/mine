import uuid
from typing import Any

import pytest

from tests.factories import (
    AdminUserFactory,
    ContractorFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

query_contractors_shape = """
query TestQuery ($orderBy: [OrderBy!]) {
  contractors (orderBy: $orderBy) {
    id
    name
  }
}
"""


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(query=query_contractors_shape, variables=kwargs)
    contractors: list[dict] = data["contractors"]
    return contractors


async def build_contractors_for_sort(
    db_session: AsyncSession, name: str | None = None
) -> list[str]:
    key = uuid.uuid4().hex
    contractor1_id = str(
        (await ContractorFactory.persist(db_session, name=name or f"á 1 {key}")).id
    )
    contractor2_id = str(
        (await ContractorFactory.persist(db_session, name=name or f"A 2 {key}")).id
    )
    contractor3_id = str(
        (await ContractorFactory.persist(db_session, name=name or f"a 3 {key}")).id
    )
    expected_order = [contractor1_id, contractor2_id, contractor3_id]
    return sorted(expected_order) if name else expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_permissions_viewer_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed, because viewer can see Learnings, and we need contractors list to filter insights
    viewer = await ViewerUserFactory.persist(db_session)
    data = await execute_gql(query=query_contractors_shape, raw=True, user=viewer)
    assert not data.json().get("errors"), f"On role {viewer.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_permissions_supervisor_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    supervisor = await SupervisorUserFactory.persist(db_session)
    data = await execute_gql(query=query_contractors_shape, raw=True, user=supervisor)
    assert not data.json().get("errors"), f"On role {supervisor.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_permissions_manager_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    manager = await ManagerUserFactory.persist(db_session)
    data = await execute_gql(query=query_contractors_shape, raw=True, user=manager)
    assert not data.json().get("errors"), f"On role {manager.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_permissions_admin_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    admin = await AdminUserFactory.persist(db_session)
    data = await execute_gql(query=query_contractors_shape, raw=True, user=admin)
    assert not data.json().get("errors"), f"On role {admin.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    contractor_1 = await ContractorFactory.persist(db_session)
    contractor_2 = await ContractorFactory.persist(db_session)

    data = await call_query(execute_gql)
    contractors_by_id = {uuid.UUID(i["id"]): i for i in data}
    contractor_data = contractors_by_id[contractor_1.id]
    assert contractor_data["name"] == contractor_1.name
    contractor_data = contractors_by_id[contractor_2.id]
    assert contractor_data["name"] == contractor_2.name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_no_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check contractors without order"""

    expected_order = await build_contractors_for_sort(db_session)

    contractors = await call_query(execute_gql, orderBy=None)
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert set(contractors_ids) == set(expected_order)

    contractors = await call_query(execute_gql, orderBy=[])
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert set(contractors_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_asc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check contractors asc order"""

    expected_order = await build_contractors_for_sort(db_session)

    contractors = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert contractors_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_desc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check contractors desc order"""

    expected_order = await build_contractors_for_sort(db_session)

    contractors = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert contractors_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_duplicated_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check contractors with duplicated field order"""

    expected_order = await build_contractors_for_sort(db_session)

    contractors = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert contractors_ids == expected_order

    contractors = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert contractors_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_contractors_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    expected_order = await build_contractors_for_sort(db_session, name="cenas")
    contractors = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    contractors_ids = [i["id"] for i in contractors if i["id"] in expected_order]
    assert contractors_ids == expected_order
