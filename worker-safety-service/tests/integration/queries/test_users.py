import uuid
from typing import Any

import pytest

from tests.factories import (
    AdminUserFactory,
    ManagerUserFactory,
    SupervisorUserFactory,
    UserFactory,
    ViewerUserFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

query_managers_shape = """
query TestQuery ($orderBy: [OrderBy!]) {
  managers (orderBy: $orderBy) {
    id
    firstName
    lastName
  }
}
"""

query_supervisors_shape = """
query TestQuery ($orderBy: [OrderBy!]) {
  supervisors (orderBy: $orderBy) {
    id
    firstName
    lastName
  }
}
"""


async def call_managers_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(query=query_managers_shape, variables=kwargs)
    managers: list[dict] = data["managers"]
    return managers


async def build_managers_for_sort(
    db_session: AsyncSession, name: str | None = None
) -> list[str]:
    manager1_id = str(
        (
            await ManagerUserFactory.persist(
                db_session, first_name=name or "á 1", last_name=name or ""
            )
        ).id
    )
    manager2_id = str(
        (
            await ManagerUserFactory.persist(
                db_session, first_name=name or "", last_name=name or "A 2"
            )
        ).id
    )
    manager3_id = str(
        (
            await ManagerUserFactory.persist(
                db_session, first_name=name or "a 3", last_name=name or ""
            )
        ).id
    )
    expected_order = [manager1_id, manager2_id, manager3_id]
    return sorted(expected_order) if name else expected_order


async def call_supervisors_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(query=query_supervisors_shape, variables=kwargs)
    supervisors: list[dict] = data["supervisors"]
    return supervisors


async def build_supervisors_for_sort(
    db_session: AsyncSession, name: str | None = None
) -> list[str]:
    supervisor1_id = str(
        (
            await SupervisorUserFactory.persist(
                db_session, first_name=name or "á 1", last_name=name or ""
            )
        ).id
    )
    supervisor2_id = str(
        (
            await SupervisorUserFactory.persist(
                db_session, first_name=name or "", last_name=name or "A 2"
            )
        ).id
    )
    supervisor3_id = str(
        (
            await SupervisorUserFactory.persist(
                db_session, first_name=name or "a 3", last_name=name or ""
            )
        ).id
    )
    expected_order = [supervisor1_id, supervisor2_id, supervisor3_id]
    return sorted(expected_order) if name else expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_permissions_viewer_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    viewer = await ViewerUserFactory.persist(db_session)
    data = await execute_gql(query=query_managers_shape, raw=True, user=viewer)
    assert not data.json().get("errors"), f"On role {viewer.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_permissions_supervisor_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    supervisor = await SupervisorUserFactory.persist(db_session)
    data = await execute_gql(query=query_managers_shape, raw=True, user=supervisor)
    assert not data.json().get("errors"), f"On role {supervisor.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_permissions_manager_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    manager = await ManagerUserFactory.persist(db_session)
    data = await execute_gql(query=query_managers_shape, raw=True, user=manager)
    assert not data.json().get("errors"), f"On role {manager.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_permissions_admin_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    admin = await AdminUserFactory.persist(db_session)
    data = await execute_gql(query=query_managers_shape, raw=True, user=admin)
    assert not data.json().get("errors"), f"On role {admin.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    user = await UserFactory.persist(db_session)
    admin = await AdminUserFactory.persist(db_session)
    supervisor = await SupervisorUserFactory.persist(db_session)
    manager = await ManagerUserFactory.persist(db_session)

    # Check query without filter
    data = await call_managers_query(execute_gql)
    users_by_id = {uuid.UUID(i["id"]): i for i in data}
    assert admin.id not in users_by_id
    assert supervisor.id not in users_by_id
    assert user.id not in users_by_id
    manager_data = users_by_id[manager.id]
    assert manager_data["firstName"] == manager.first_name
    assert manager_data["lastName"] == manager.last_name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_no_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check managers without order"""

    expected_order = await build_managers_for_sort(db_session)

    managers = await call_managers_query(execute_gql, orderBy=None)
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert set(managers_ids) == set(expected_order)

    managers = await call_managers_query(execute_gql, orderBy=[])
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert set(managers_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_asc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check managers asc order"""

    expected_order = await build_managers_for_sort(db_session)

    managers = await call_managers_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert managers_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_desc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check managers desc order"""

    expected_order = await build_managers_for_sort(db_session)

    managers = await call_managers_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert managers_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_managers_duplicated_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check managers with duplicated field order"""

    expected_order = await build_managers_for_sort(db_session)

    managers = await call_managers_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert managers_ids == expected_order

    managers = await call_managers_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert managers_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.fresh_db
async def test_managers_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    expected_order = await build_managers_for_sort(db_session, name="cenas")

    managers = await call_managers_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    managers_ids = [i["id"] for i in managers if i["id"] in expected_order]
    assert managers_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_permissions_viewer_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Not allowed
    viewer = await ViewerUserFactory.persist(db_session)
    data = await execute_gql(query=query_supervisors_shape, raw=True, user=viewer)
    assert not data.json().get("errors"), f"On role {viewer.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_permissions_supervisor_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    supervisor = await SupervisorUserFactory.persist(db_session)
    data = await execute_gql(query=query_supervisors_shape, raw=True, user=supervisor)
    assert not data.json().get("errors"), f"On role {supervisor.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_permissions_manager_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    manager = await ManagerUserFactory.persist(db_session)
    data = await execute_gql(query=query_supervisors_shape, raw=True, user=manager)
    assert not data.json().get("errors"), f"On role {manager.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_permissions_admin_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    # Allowed
    admin = await AdminUserFactory.persist(db_session)
    data = await execute_gql(query=query_supervisors_shape, raw=True, user=admin)
    assert not data.json().get("errors"), f"On role {admin.role}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    user = await UserFactory.persist(db_session)
    admin = await AdminUserFactory.persist(db_session)
    supervisor = await SupervisorUserFactory.persist(db_session)
    manager = await ManagerUserFactory.persist(db_session)

    # Check query without filter
    data = await call_supervisors_query(execute_gql)
    users_by_id = {uuid.UUID(i["id"]): i for i in data}
    assert admin.id not in users_by_id
    assert manager.id not in users_by_id
    assert user.id not in users_by_id
    supervisor_data = users_by_id[supervisor.id]
    assert supervisor_data["firstName"] == supervisor.first_name
    assert supervisor_data["lastName"] == supervisor.last_name


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_no_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check supervisors without order"""

    expected_order = await build_supervisors_for_sort(db_session)

    supervisors = await call_supervisors_query(execute_gql, orderBy=None)
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert set(supervisors_ids) == set(expected_order)

    supervisors = await call_supervisors_query(execute_gql, orderBy=[])
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert set(supervisors_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_asc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check supervisors asc order"""

    expected_order = await build_supervisors_for_sort(db_session)

    supervisors = await call_supervisors_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert supervisors_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_desc_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check supervisors desc order"""

    expected_order = await build_supervisors_for_sort(db_session)

    supervisors = await call_supervisors_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert supervisors_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_duplicated_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check supervisors with duplicated field order"""

    expected_order = await build_supervisors_for_sort(db_session)

    supervisors = await call_supervisors_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert supervisors_ids == expected_order

    supervisors = await call_supervisors_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert supervisors_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_supervisors_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    expected_order = await build_supervisors_for_sort(db_session, name="cenas")

    supervisors = await call_supervisors_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    supervisors_ids = [i["id"] for i in supervisors if i["id"] in expected_order]
    assert supervisors_ids == expected_order
