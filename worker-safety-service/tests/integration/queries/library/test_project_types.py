import uuid
from typing import Any

import pytest

from tests.factories import LibraryProjectTypeFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

library_project_types_query = {
    "operation_name": "projectTypesLibrary",
    "query": """
query projectTypesLibrary ($orderBy: [OrderBy!]) {
  projectTypesLibrary (orderBy: $orderBy) {
    id
    name
  }
}
""",
}


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**library_project_types_query, variables=kwargs)
    project_types: list[dict] = data["projectTypesLibrary"]
    return project_types


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_types_library_query(execute_gql: ExecuteGQL) -> None:
    """Simple library project types check"""

    # Check all project types
    project_types = await call_query(execute_gql)
    assert project_types
    first_project_type = project_types[0]
    assert uuid.UUID(first_project_type["id"])
    assert first_project_type["name"]
    assert isinstance(first_project_type["name"], str)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_types_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check library project types order"""

    project_type1_id = str(
        (await LibraryProjectTypeFactory.persist(db_session, name="á 1")).id
    )
    project_type2_id = str(
        (await LibraryProjectTypeFactory.persist(db_session, name="A 2")).id
    )
    project_type3_id = str(
        (await LibraryProjectTypeFactory.persist(db_session, name="a 3")).id
    )
    expected_order = [project_type1_id, project_type2_id, project_type3_id]

    # No order
    project_types = await call_query(execute_gql, orderBy=None)
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert set(project_types_ids) == set(expected_order)

    project_types = await call_query(execute_gql, orderBy=[])
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert set(project_types_ids) == set(expected_order)

    # ASC
    project_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert project_types_ids == expected_order

    # DESC
    project_types = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert project_types_ids == list(reversed(expected_order))

    # with multiple order by should match first
    project_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert project_types_ids == expected_order

    project_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert project_types_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
async def test_project_types_library_dupliacted_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    project_type1_id = str(
        (await LibraryProjectTypeFactory.persist(db_session, name="cenas")).id
    )
    project_type2_id = str(
        (await LibraryProjectTypeFactory.persist(db_session, name="Cenas")).id
    )
    expected_order = sorted([project_type1_id, project_type2_id])

    project_types = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    project_types_ids = [i["id"] for i in project_types if i["id"] in expected_order]
    assert project_types_ids == expected_order
