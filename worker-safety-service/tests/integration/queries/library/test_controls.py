import uuid
from typing import Any, Awaitable, Callable

import pytest

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibrarySiteConditionRecommendationsFactory,
    LibraryTaskFactory,
    LibraryTaskRecommendationsFactory,
    TenantFactory,
)
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.dal.library import LibraryFilterType
from worker_safety_service.models import AsyncSession, LibraryControl

controls_query = {
    "operation_name": "controlsLibrary",
    "query": """
query controlsLibrary ($type: LibraryFilterType!, $id: UUID, $libraryTaskId: UUID, $librarySiteConditionId: UUID, $libraryHazardId: UUID, $orderBy: [OrderBy!]) {
  controlsLibrary(id: $id, type: $type, libraryTaskId: $libraryTaskId, librarySiteConditionId: $librarySiteConditionId, libraryHazardId: $libraryHazardId, orderBy: $orderBy) {
    id
    name
    isApplicable
  }
}
""",
}

tasks_query = {
    "operation_name": "tasksLibrary",
    "query": """
query tasksLibrary {
  tasksLibrary {
    id
    hazards {
        id
        controls {
            id
        }
    }
  }
}
""",
}

site_conditions_query = {
    "operation_name": "siteConditionsLibrary",
    "query": """
query siteConditionsLibrary {
  siteConditionsLibrary {
    id
    hazards {
        id
        controls {
            id
        }
    }
  }
}
""",
}


async def call_query(execute_gql: ExecuteGQL, type: str, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**controls_query, variables={"type": type, **kwargs})
    controls: list[dict] = data["controlsLibrary"]
    return controls


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("control_type", [i.name for i in LibraryFilterType])
async def test_controls_library_query(
    execute_gql: ExecuteGQL, control_type: str
) -> None:
    """Simple library controls check"""

    # Check all controls
    controls = await call_query(execute_gql, control_type)
    assert controls
    first_control = controls[0]
    assert uuid.UUID(first_control["id"])
    assert first_control["name"]
    assert isinstance(first_control["name"], str)

    # Check if filter have valid data
    controls = await call_query(execute_gql, control_type, id=first_control["id"])
    assert len(controls) == 1
    assert controls[0] == first_control


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "control_info",
    [
        ("TASK", "for_tasks"),
        ("SITE_CONDITION", "for_site_conditions"),
    ],
)
async def test_controls_not_recommendated_query(
    execute_gql: ExecuteGQL,
    control_info: tuple[str, str],
    db_session: AsyncSession,
) -> None:
    """Make sure only controls defined for a type (task/site condition) are returned"""
    tenant = await TenantFactory.default_tenant(db_session)
    # Not recommended controls should be returned
    control_type, for_filter_column = control_info

    invalid_kwargs = {
        i: False for i in LibraryControl.__annotations__.keys() if i.startswith("for_")
    }
    kwargs = {**invalid_kwargs, for_filter_column: True}
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, **kwargs
            )
        ).id
    )
    invalid_control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, **invalid_kwargs
            )
        ).id
    )

    controls = await call_query(execute_gql, control_type)
    assert controls
    controls_by_id = {i["id"]: i for i in controls}
    assert control_id in controls_by_id
    assert invalid_control_id not in controls_by_id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "control_info",
    [
        ("TASK", "for_tasks", "libraryTaskId", tasks_query),
        (
            "SITE_CONDITION",
            "for_site_conditions",
            "librarySiteConditionId",
            site_conditions_query,
        ),
    ],
)
async def test_controls_recommendated_query(
    execute_gql: ExecuteGQL,
    control_info: tuple[str, str, str, dict],
    db_session: AsyncSession,
) -> None:
    """Make sure only recommended controls are returned for a main type id (task/site condition)"""

    # Not recommended controls should be ignored with task/site condition filter
    control_type, for_filter_column, filter_name, query_for_filter = control_info

    # Get recommendation
    data = await execute_gql(**query_for_filter)
    recommendation: Any | None = None
    for item in data[query_for_filter["operation_name"]]:
        if any(i["controls"] for i in item["hazards"]):
            recommendation = item
            break
    assert recommendation
    recommendation_id: str = recommendation["id"]

    # Create controls that are not a recommendation
    invalid_kwargs = {
        i: False for i in LibraryControl.__annotations__.keys() if i.startswith("for_")
    }
    kwargs = {**invalid_kwargs, for_filter_column: True}
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, None, **kwargs
            )
        ).id
    )
    invalid_control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, None, **invalid_kwargs
            )
        ).id
    )

    controls = await call_query(
        execute_gql, control_type, **{filter_name: recommendation_id}
    )
    assert controls
    controls_by_id = {i["id"]: i for i in controls}
    assert control_id not in controls_by_id
    assert invalid_control_id not in controls_by_id
    assert set(controls_by_id.keys()) == {
        i["id"] for h in recommendation["hazards"] for i in h["controls"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "parent_info",
    [
        (
            "TASK",
            lambda s: LibraryTaskFactory.persist(s),
            lambda s, i, h, c: LibraryTaskRecommendationsFactory.persist(
                s,
                library_task_id=i,
                library_hazard_id=h,
                library_control_id=c,
            ),
            "libraryTaskId",
        ),
        (
            "SITE_CONDITION",
            lambda s: LibrarySiteConditionFactory.persist(s),
            lambda s, i, h, c: LibrarySiteConditionRecommendationsFactory.persist(
                s,
                library_site_condition_id=i,
                library_hazard_id=h,
                library_control_id=c,
            ),
            "librarySiteConditionId",
        ),
    ],
)
async def test_no_duplicated_controls_query(
    execute_gql: ExecuteGQL,
    parent_info: tuple[
        str,
        Callable[[Any], Awaitable[Any]],
        Callable[[Any, Any, Any, Any], Awaitable[Any]],
        str,
    ],
    db_session: AsyncSession,
) -> None:
    """Make sure controls only return direct hazard relation
    If we have:
        task 1 -> hazard 1 -> control 1 + control 2
        task 2 -> hazard 1 -> control 1
    hazard 1 resolvers (with type id filter) should only return "control 1"
    """
    tenant = await TenantFactory.default_tenant(db_session)

    (
        control_type,
        build_library,
        build_library_recommendation,
        filter_column,
    ) = parent_info

    parent1_id = str((await build_library(db_session)).id)
    parent2_id = str((await build_library(db_session)).id)
    hazard1_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant.id, for_tasks=False, for_site_conditions=False
            )
        ).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control2_id)
    await build_library_recommendation(db_session, parent2_id, hazard1_id, control_id)

    # Check if controls match
    controls = await call_query(
        execute_gql, control_type, **{filter_column: parent1_id}
    )
    assert len(controls) == 2
    assert {control_id, control2_id} == {i["id"] for i in controls}

    # Check if controls match
    controls = await call_query(
        execute_gql, control_type, **{filter_column: parent2_id}
    )
    assert len(controls) == 1
    control = controls[0]
    assert control["id"] == control_id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "parent_info",
    [
        (
            "TASK",
            lambda s: LibraryTaskFactory.persist(s),
            lambda s, i, h, c: LibraryTaskRecommendationsFactory.persist(
                s,
                library_task_id=i,
                library_hazard_id=h,
                library_control_id=c,
            ),
            "libraryTaskId",
        ),
        (
            "SITE_CONDITION",
            lambda s: LibrarySiteConditionFactory.persist(s),
            lambda s, i, h, c: LibrarySiteConditionRecommendationsFactory.persist(
                s,
                library_site_condition_id=i,
                library_hazard_id=h,
                library_control_id=c,
            ),
            "librarySiteConditionId",
        ),
    ],
)
async def test_controls_with_hazard_filter_query(
    execute_gql: ExecuteGQL,
    parent_info: tuple[str, Callable, Callable, str],
    db_session: AsyncSession,
) -> None:
    """Make sure controls only return direct hazard relation
    If we have:
        task 1 -> hazard 1 -> control 1 + control 2
        task 2 -> hazard 1 -> control 1
    hazard 1 resolvers (with type id filter) should only return "control 1"
    """
    tenant = await TenantFactory.default_tenant(db_session)
    (
        control_type,
        build_library,
        build_library_recommendation,
        filter_column,
    ) = parent_info

    parent1_id = str((await build_library(db_session)).id)
    parent2_id = str((await build_library(db_session)).id)
    hazard1_id = str(
        (
            await LibraryHazardFactory.persist(
                db_session, for_tasks=False, for_site_conditions=False
            )
        ).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant.id, for_tasks=True, for_site_conditions=False
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control2_id)
    await build_library_recommendation(db_session, parent2_id, hazard1_id, control_id)

    # Check if controls match
    controls = await call_query(
        execute_gql, control_type, **{filter_column: parent1_id}
    )
    assert len(controls) == 2
    assert {control_id, control2_id} == {i["id"] for i in controls}

    # Check if controls match
    controls = await call_query(
        execute_gql, control_type, **{filter_column: parent2_id}
    )
    assert len(controls) == 1
    control = controls[0]
    assert control["id"] == control_id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("control_type", ["TASK", "SITE_CONDITION"])
async def test_controls_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession, control_type: str
) -> None:
    """Check library controls order"""
    tenant = await TenantFactory.default_tenant(db_session)
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant.id,
                name="á 1",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant.id,
                name="A 2",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    control3_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant.id,
                name="a 3",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    expected_order = [control1_id, control2_id, control3_id]

    # No order
    controls = await call_query(execute_gql, control_type, orderBy=None)
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert set(controls_ids) == set(expected_order)

    controls = await call_query(execute_gql, control_type, orderBy=[])
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert set(controls_ids) == set(expected_order)

    # ASC
    controls = await call_query(
        execute_gql, control_type, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert controls_ids == expected_order

    # DESC
    controls = await call_query(
        execute_gql, control_type, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert controls_ids == list(reversed(expected_order))

    # with multiple order by should match first
    controls = await call_query(
        execute_gql,
        control_type,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert controls_ids == expected_order

    controls = await call_query(
        execute_gql,
        control_type,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert controls_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("control_type", ["TASK", "SITE_CONDITION"])
async def test_controls_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession, control_type: str
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant.id,
                name="cenas",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant.id,
                name="Cenas",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    expected_order = sorted([control1_id, control2_id])

    controls = await call_query(
        execute_gql,
        control_type,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    controls_ids = [i["id"] for i in controls if i["id"] in expected_order]
    assert controls_ids == expected_order
