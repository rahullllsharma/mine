import uuid
from typing import Any, Callable, Optional

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
from worker_safety_service.models import AsyncSession, LibraryHazard

library_hazards_query = {
    "operation_name": "hazardsLibrary",
    "query": """
query hazardsLibrary ($type: LibraryFilterType!, $id: UUID, $withControls: Boolean! = false, $libraryTaskId: UUID, $librarySiteConditionId: UUID, $orderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  hazardsLibrary(id: $id, type: $type, libraryTaskId: $libraryTaskId, librarySiteConditionId: $librarySiteConditionId, orderBy: $orderBy) {
    id
    name
    isApplicable
    energyLevel
    imageUrl
    controls (orderBy: $controlsOrderBy) @include(if: $withControls) {
        id
        name
        isApplicable
    }
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
    data = await execute_gql(
        **library_hazards_query, variables={"type": type, **kwargs}
    )
    hazards: list[dict] = data["hazardsLibrary"]
    return hazards


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("hazard_type", [i.name for i in LibraryFilterType])
async def test_hazards_library_query(execute_gql: ExecuteGQL, hazard_type: str) -> None:
    """Simple library hazards check"""

    # Check all hazards
    hazards = await call_query(execute_gql, hazard_type)
    assert hazards
    first_hazard = hazards[0]
    assert uuid.UUID(first_hazard["id"])
    assert first_hazard["name"]
    assert isinstance(first_hazard["name"], str)

    # Check if filter have valid data
    hazards_one = await call_query(execute_gql, hazard_type, id=first_hazard["id"])
    assert len(hazards_one) == 1
    assert hazards_one[0] == first_hazard


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("hazard_type", [i.name for i in LibraryFilterType])
async def test_hazards_resolvers_query(
    execute_gql: ExecuteGQL, hazard_type: str
) -> None:
    """Simple controls check on hazards query"""

    # Check if all resolvers are defined
    hazards = await call_query(execute_gql, hazard_type, withControls=True)
    assert hazards
    assert all(isinstance(i["controls"], list) for i in hazards)

    hazard_1: Optional[dict] = None
    hazard_2: Optional[dict] = None
    for hazard in hazards:
        for control in hazard["controls"]:
            assert uuid.UUID(control["id"])
            assert isinstance(control["name"], str)
            assert control["isApplicable"] is True

        if hazard["controls"]:
            if not hazard_1:
                hazard_1 = hazard
            elif not hazard_2:
                hazard_2 = hazard
    assert hazard_1
    assert hazard_2

    # Check if filters match resolvers
    response_hazard_1 = (
        await call_query(execute_gql, hazard_type, withControls=True, id=hazard_1["id"])
    )[0]
    response_hazard_2 = (
        await call_query(execute_gql, hazard_type, withControls=True, id=hazard_2["id"])
    )[0]

    # resolvers are not ordered, order it to check data
    hazard_1["controls"].sort(key=lambda i: i["id"])
    response_hazard_1["controls"].sort(key=lambda i: i["id"])
    hazard_2["controls"].sort(key=lambda i: i["id"])
    response_hazard_2["controls"].sort(key=lambda i: i["id"])

    # Now check it
    assert response_hazard_1 == hazard_1
    assert response_hazard_2 == hazard_2


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "hazard_info",
    [
        ("TASK", "for_tasks"),
        ("SITE_CONDITION", "for_site_conditions"),
    ],
)
async def test_hazards_not_recommendated_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession, hazard_info: tuple[str, str]
) -> None:
    """Make sure only hazards defined for a type (task/site condition) are returned"""
    tenant = await TenantFactory.default_tenant(db_session)
    # Not recommended hazards should be returned
    hazard_type, for_filter_column = hazard_info

    invalid_kwargs = {
        i: False for i in LibraryHazard.__annotations__.keys() if i.startswith("for_")
    }
    kwargs = {**invalid_kwargs, for_filter_column: True}
    hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **kwargs
            )
        ).id
    )
    invalid_hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **invalid_kwargs
            )
        ).id
    )

    hazards = await call_query(execute_gql, hazard_type, withControls=True)
    assert hazards
    hazards_by_id = {i["id"]: i for i in hazards}
    assert hazard_id in hazards_by_id
    assert not hazards_by_id[hazard_id]["controls"]
    assert invalid_hazard_id not in hazards_by_id


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "hazard_info",
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
async def test_hazards_recommendated_query(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    hazard_info: tuple[str, str, str, dict],
) -> None:
    """Make sure only recommended hazards are returned for a main type id (task/site condition)"""
    tenant = await TenantFactory.default_tenant(db_session)
    # Not recommended hazards should be ignored with task/site condition filter
    hazard_type, for_filter_column, filter_name, query_for_filter = hazard_info

    # Get recommendation
    recommendation: Any | None = None
    data = await execute_gql(**query_for_filter)
    for item in data[query_for_filter["operation_name"]]:
        if any(i["controls"] for i in item["hazards"]):
            recommendation = item
            break
    assert recommendation
    recommendation_id: str = recommendation["id"]

    # Create hazards that are not a recommendation
    invalid_kwargs = {
        i: False for i in LibraryHazard.__annotations__.keys() if i.startswith("for_")
    }
    kwargs = {**invalid_kwargs, for_filter_column: True}
    hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **kwargs
            )
        ).id
    )
    invalid_hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **invalid_kwargs
            )
        ).id
    )

    hazards = await call_query(
        execute_gql, hazard_type, withControls=True, **{filter_name: recommendation_id}
    )
    assert hazards
    hazards_by_id = {i["id"]: i for i in hazards}
    assert hazard_id not in hazards_by_id
    assert invalid_hazard_id not in hazards_by_id
    assert set(hazards_by_id.keys()) == {i["id"] for i in recommendation["hazards"]}
    for recommendation_hazard in recommendation["hazards"]:
        test_hazard = hazards_by_id[recommendation_hazard["id"]]
        assert {i["id"] for i in recommendation_hazard["controls"]} == {
            i["id"] for i in test_hazard["controls"]
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
    db_session: AsyncSession,
    parent_info: tuple[str, Callable, Callable, str],
) -> None:
    """Make sure controls only return direct hazard relation
    If we have:
        task 1 -> hazard 1 -> control 1 + control 2
        task 2 -> hazard 1 -> control 1
        hazard 2 resolvers (with type id filter) should only return "control 1"
    """
    tenant = await TenantFactory.default_tenant(db_session)
    (
        hazard_type,
        build_library,
        build_library_recommendation,
        filter_column,
    ) = parent_info

    parent1_id = str((await build_library(db_session)).id)
    parent2_id = str((await build_library(db_session)).id)
    hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                for_tasks=False,
                for_site_conditions=False,
            )
        ).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                for_tasks=True,
                for_site_conditions=False,
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                for_tasks=True,
                for_site_conditions=False,
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard_id, control2_id)
    await build_library_recommendation(db_session, parent2_id, hazard_id, control1_id)

    expected_controls_1 = {control1_id, control2_id}
    expected_controls_2 = {control1_id}

    # Check if controls match
    hazards = await call_query(
        execute_gql, hazard_type, withControls=True, **{filter_column: parent1_id}
    )
    assert len(hazards) == 1
    hazard = hazards[0]
    assert hazard["id"] == hazard_id
    assert expected_controls_1 == {i["id"] for i in hazard["controls"]}

    # Check if controls match
    hazards = await call_query(
        execute_gql, hazard_type, withControls=True, **{filter_column: parent2_id}
    )
    assert len(hazards) == 1
    hazard = hazards[0]
    assert hazard["id"] == hazard_id
    assert expected_controls_2 == {i["id"] for i in hazard["controls"]}


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
        ),
    ],
)
async def test_no_duplicated_controls_without_context_query(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    parent_info: tuple[str, Callable, Callable],
) -> None:
    """Make sure we have unique controls
    If we have:
        task 1 -> hazard 1 -> control 1 + control 2
        task 2 -> hazard 1 -> control 1
        hazard 2 resolvers (without filter) should only return "control 1" and "control 2"
    """
    tenant = await TenantFactory.default_tenant(db_session)
    (
        hazard_type,
        build_library,
        build_library_recommendation,
    ) = parent_info

    kwargs = {
        i: True for i in LibraryHazard.__annotations__.keys() if i.startswith("for_")
    }

    parent1_id = str((await build_library(db_session)).id)
    parent2_id = str((await build_library(db_session)).id)
    hazard_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **kwargs
            )
        ).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **kwargs
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, tenant_id=tenant.id, **kwargs
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard_id, control2_id)
    await build_library_recommendation(db_session, parent2_id, hazard_id, control1_id)

    expected_controls = sorted([control1_id, control2_id])

    # Check if controls are not duplicated
    hazards = await call_query(
        execute_gql, hazard_type, withControls=True, id=hazard_id
    )
    assert len(hazards) == 1
    hazard = hazards[0]
    assert hazard["id"] == hazard_id
    assert expected_controls == sorted(i["id"] for i in hazard["controls"])

    # Check if controls are not duplicated (without filters)
    hazards = await call_query(execute_gql, hazard_type, withControls=True)
    hazards_by_id = {i["id"]: i for i in hazards}
    hazard = hazards_by_id[hazard_id]
    assert expected_controls == sorted(i["id"] for i in hazard["controls"])


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("hazard_type", ["TASK", "SITE_CONDITION"])
async def test_hazards_library_sort(
    execute_gql: ExecuteGQL, db_session: AsyncSession, hazard_type: str
) -> None:
    """Check library hazards order"""
    tenant = await TenantFactory.default_tenant(db_session)
    hazard1_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="á 1",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    hazard2_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="A 2",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    hazard3_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="a 3",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    expected_order = [hazard1_id, hazard2_id, hazard3_id]

    # No order
    hazards = await call_query(execute_gql, hazard_type, orderBy=None)
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert set(hazards_ids) == set(expected_order)

    hazards = await call_query(execute_gql, hazard_type, orderBy=[])
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert set(hazards_ids) == set(expected_order)

    # ASC
    hazards = await call_query(
        execute_gql, hazard_type, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert hazards_ids == expected_order

    # DESC
    hazards = await call_query(
        execute_gql, hazard_type, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert hazards_ids == list(reversed(expected_order))

    # with multiple order by should match first
    hazards = await call_query(
        execute_gql,
        hazard_type,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert hazards_ids == expected_order

    hazards = await call_query(
        execute_gql,
        hazard_type,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert hazards_ids == list(reversed(expected_order))


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("hazard_type", ["TASK", "SITE_CONDITION"])
async def test_hazards_library_duplicated_name(
    execute_gql: ExecuteGQL, db_session: AsyncSession, hazard_type: str
) -> None:
    tenant = await TenantFactory.default_tenant(db_session)
    hazard1_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="cenas",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    hazard2_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="Cenas",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    expected_order = sorted([hazard1_id, hazard2_id])

    hazards = await call_query(
        execute_gql,
        hazard_type,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_order]
    assert hazards_ids == expected_order


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
        ),
    ],
)
async def test_controls_order_on_hazards_library(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    parent_info: tuple[str, Callable, Callable],
) -> None:
    """Check controls order on library hazards"""
    tenant = await TenantFactory.default_tenant(db_session)
    (
        hazard_type,
        build_library,
        build_library_recommendation,
    ) = parent_info

    parent1_id = str((await build_library(db_session)).id)
    hazard1_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="á 1",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
                name="a 3",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control2_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control3_id)

    expected_order = [control1_id, control2_id, control3_id]

    # No order
    hazards = await call_query(
        execute_gql, hazard_type, id=hazard1_id, withControls=True, controlsOrderBy=None
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert set(controls_ids) == set(expected_order)

    hazards = await call_query(
        execute_gql, hazard_type, id=hazard1_id, withControls=True, controlsOrderBy=[]
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert set(controls_ids) == set(expected_order)

    # ASC
    hazards = await call_query(
        execute_gql,
        hazard_type,
        id=hazard1_id,
        withControls=True,
        controlsOrderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert controls_ids == expected_order

    # DESC
    hazards = await call_query(
        execute_gql,
        hazard_type,
        id=hazard1_id,
        withControls=True,
        controlsOrderBy=[{"field": "NAME", "direction": "DESC"}],
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert controls_ids == list(reversed(expected_order))

    # with multiple order by should match first
    hazards = await call_query(
        execute_gql,
        hazard_type,
        id=hazard1_id,
        withControls=True,
        controlsOrderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert controls_ids == expected_order

    hazards = await call_query(
        execute_gql,
        hazard_type,
        id=hazard1_id,
        withControls=True,
        controlsOrderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    controls_ids = [
        i["id"] for i in hazards[0]["controls"] if i["id"] in expected_order
    ]
    assert controls_ids == list(reversed(expected_order))


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
        ),
    ],
)
async def test_controls_order_with_different_order(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
    parent_info: tuple[str, Callable, Callable],
) -> None:
    """Check if controls have different order from library hazards"""
    tenant = await TenantFactory.default_tenant(db_session)
    (
        hazard_type,
        build_library,
        build_library_recommendation,
    ) = parent_info

    parent1_id = str((await build_library(db_session)).id)
    hazard1_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="á 1",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    hazard2_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="A 2",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    hazard3_id = str(
        (
            await LibraryHazardFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
                name="a 3",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
                name="a 3",
                for_tasks=True,
                for_site_conditions=True,
            )
        ).id
    )
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control2_id)
    await build_library_recommendation(db_session, parent1_id, hazard1_id, control3_id)
    await build_library_recommendation(db_session, parent1_id, hazard2_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard2_id, control2_id)
    await build_library_recommendation(db_session, parent1_id, hazard2_id, control3_id)
    await build_library_recommendation(db_session, parent1_id, hazard3_id, control1_id)
    await build_library_recommendation(db_session, parent1_id, hazard3_id, control2_id)
    await build_library_recommendation(db_session, parent1_id, hazard3_id, control3_id)

    expected_hazards_order = [hazard1_id, hazard2_id, hazard3_id]
    expected_order = [control1_id, control2_id, control3_id]

    # ASC
    hazards = await call_query(
        execute_gql,
        hazard_type,
        withControls=True,
        orderBy=[{"field": "NAME", "direction": "DESC"}],
        controlsOrderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_hazards_order]
    assert hazards_ids == list(reversed(expected_hazards_order))
    hazard_controls = {i["id"]: i["controls"] for i in hazards}
    for hazard_id in expected_hazards_order:
        controls_ids = [
            i["id"] for i in hazard_controls[hazard_id] if i["id"] in expected_order
        ]
        assert controls_ids == expected_order

    # DESC
    hazards = await call_query(
        execute_gql,
        hazard_type,
        withControls=True,
        orderBy=[{"field": "NAME", "direction": "ASC"}],
        controlsOrderBy=[{"field": "NAME", "direction": "DESC"}],
    )
    hazards_ids = [i["id"] for i in hazards if i["id"] in expected_hazards_order]
    assert hazards_ids == expected_hazards_order
    hazard_controls = {i["id"]: i["controls"] for i in hazards}
    for hazard_id in expected_hazards_order:
        controls_ids = [
            i["id"] for i in hazard_controls[hazard_id] if i["id"] in expected_order
        ]
        assert controls_ids == list(reversed(expected_order))
