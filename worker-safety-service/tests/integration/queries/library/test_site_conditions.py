import uuid
from typing import Any, Optional

import pytest
from sqlmodel import col, select

from tests.factories import (
    LibraryControlFactory,
    LibraryHazardFactory,
    LibrarySiteConditionFactory,
    LibrarySiteConditionRecommendationsFactory,
    TenantFactory,
    TenantLibrarySiteConditionSettingsFactory,
    WorkTypeFactory,
    WorkTypeLibrarySiteConditionLinkFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.queries.helpers import (
    asc_order,
    build_library_controls_for_order_by,
    build_library_hazards_for_order_by,
    build_library_site_conditions_for_order_by,
    desc_order,
    set_library_site_conditions_relations,
)
from worker_safety_service.models import (
    AsyncSession,
    TenantLibrarySiteConditionSettings,
    WorkTypeLibrarySiteConditionLink,
)

tenant_site_conditions_query = {
    "operation_name": "siteConditionsLibrary",
    "query": """
query siteConditionsLibrary ($tenantWorkTypeIds:[UUID!]!, $id: UUID, $withName: Boolean! = true, $withHazards: Boolean! = false, $orderBy: [OrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  tenantAndWorkTypeLinkedLibrarySiteConditions(orderBy: $orderBy, tenantWorkTypeIds: $tenantWorkTypeIds, id: $id) {
    id
    name @include(if: $withName)
    workTypes{
      name
      id
    }
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        isApplicable
        controls (orderBy: $controlsOrderBy) {
            id
            name
            isApplicable
        }
    }
  }
}
""",
}

site_conditions_query = {
    "operation_name": "siteConditionsLibrary",
    "query": """
query siteConditionsLibrary ($id: UUID, $withName: Boolean! = true, $withHazards: Boolean! = false, $orderBy: [OrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  siteConditionsLibrary(id: $id, orderBy: $orderBy) {
    id
    name @include(if: $withName)
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        isApplicable
        controls (orderBy: $controlsOrderBy) {
            id
            name
            isApplicable
        }
    }
  }
}
""",
}


async def call_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**site_conditions_query, variables=kwargs)
    site_conditions: list[dict] = data["siteConditionsLibrary"]
    return site_conditions


async def call_linked_query(execute_gql: ExecuteGQL, **kwargs: Any) -> list[dict]:
    data = await execute_gql(**tenant_site_conditions_query, variables=kwargs)
    site_conditions: list[dict] = data["tenantAndWorkTypeLinkedLibrarySiteConditions"]
    return site_conditions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_query(execute_gql: ExecuteGQL) -> None:
    """Simple library site conditions check"""

    # Check all site conditions
    site_conditions = await call_query(execute_gql)
    assert site_conditions
    first_site_condition = site_conditions[0]
    assert uuid.UUID(first_site_condition["id"])
    assert first_site_condition["name"]
    assert isinstance(first_site_condition["name"], str)

    # Check if filter have valid data
    site_conditions_one = await call_query(execute_gql, id=first_site_condition["id"])
    assert len(site_conditions_one) == 1
    assert site_conditions_one[0] == first_site_condition

    # Check if only id field is sent
    site_conditions_two = await call_query(execute_gql, withName=False)
    assert len(site_conditions_two) == len(site_conditions)
    assert all(uuid.UUID(i["id"]) for i in site_conditions_two)
    returned_fields: set[str] = set()
    for site_condition in site_conditions_two:
        returned_fields.update(site_condition.keys())
    assert returned_fields == {"id"}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_resolvers_query(execute_gql: ExecuteGQL) -> None:
    """Check library site conditions hazards and controls resolvers"""

    # Check if all resolvers are defined
    site_conditions = await call_query(execute_gql, withHazards=True)
    assert site_conditions
    assert all(isinstance(i["hazards"], list) for i in site_conditions)
    assert all(
        isinstance(h["controls"], list) for i in site_conditions for h in i["hazards"]
    )

    site_condition_1: Optional[dict] = None
    site_condition_2: Optional[dict] = None
    for site_condition in site_conditions:
        with_controls = False
        for hazard in site_condition["hazards"]:
            assert uuid.UUID(hazard["id"])
            assert isinstance(hazard["name"], str)
            assert hazard["isApplicable"] is True
            if hazard["controls"]:
                with_controls = True
            for control in hazard["controls"]:
                assert uuid.UUID(control["id"])
                assert isinstance(control["name"], str)
                assert control["isApplicable"] is True

        if with_controls and site_condition["hazards"]:
            if not site_condition_1:
                site_condition_1 = site_condition
            elif not site_condition_2:
                site_condition_2 = site_condition
    assert site_condition_1
    assert site_condition_2

    # Check if filters match resolvers
    response_site_condition_1 = (
        await call_query(execute_gql, id=site_condition_1["id"], withHazards=True)
    )[0]
    response_site_condition_2 = (
        await call_query(execute_gql, id=site_condition_2["id"], withHazards=True)
    )[0]

    # resolvers are not ordered, order it to check data
    site_condition_1["hazards"].sort(key=lambda i: i["id"])
    for hazard in site_condition_1["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    response_site_condition_1["hazards"].sort(key=lambda i: i["id"])
    for hazard in response_site_condition_1["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    site_condition_2["hazards"].sort(key=lambda i: i["id"])
    for hazard in site_condition_2["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])
    response_site_condition_2["hazards"].sort(key=lambda i: i["id"])
    for hazard in response_site_condition_2["hazards"]:
        hazard["controls"].sort(key=lambda i: i["id"])

    # Now check it
    assert response_site_condition_1 == site_condition_1
    assert response_site_condition_2 == site_condition_2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_duplicated_controls_query(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Make sure controls only return direct hazard relation
    If we have:
        site_condition 1 -> hazard 1 -> control 1 + control 2
        site_condition 2 -> hazard 1 -> control 1
        site_condition 2 resolvers sould only return "control 1"
    """

    site_condition1_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    site_condition2_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                for_tasks=False,
                for_site_conditions=True,
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session,
                for_tasks=False,
                for_site_conditions=True,
            )
        ).id
    )
    await set_library_site_conditions_relations(
        db_session, [site_condition1_id], [hazard1_id], [control1_id, control2_id]
    )
    await set_library_site_conditions_relations(
        db_session, [site_condition2_id], [hazard1_id], [control1_id]
    )

    expected_site_condition1_hazards = {hazard1_id}
    expected_site_condition1_controls = {control1_id, control2_id}
    expected_site_condition2_hazards = {hazard1_id}
    expected_site_condition2_controls = {control1_id}

    # Check if all resolvers are defined
    site_conditions = await call_query(execute_gql, withHazards=True)
    assert site_conditions
    site_conditions_by_id = {i["id"]: i for i in site_conditions}

    testing_site_condition1 = site_conditions_by_id[site_condition1_id]
    assert expected_site_condition1_hazards == {
        i["id"] for i in testing_site_condition1["hazards"]
    }
    assert expected_site_condition1_controls == {
        x["id"] for i in testing_site_condition1["hazards"] for x in i["controls"]
    }
    testing_site_condition2 = site_conditions_by_id[site_condition2_id]
    assert expected_site_condition2_hazards == {
        i["id"] for i in testing_site_condition2["hazards"]
    }
    assert expected_site_condition2_controls == {
        x["id"] for i in testing_site_condition2["hazards"] for x in i["controls"]
    }


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check library site conditions order"""

    expected_order = list(await build_library_site_conditions_for_order_by(db_session))

    # No order
    site_conditions = await call_query(execute_gql, orderBy=None)
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert set(site_conditions_ids) == set(expected_order)

    site_conditions = await call_query(execute_gql, orderBy=[])
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert set(site_conditions_ids) == set(expected_order)

    # ASC
    site_conditions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "ASC"}]
    )
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert site_conditions_ids == expected_order

    # DESC
    site_conditions = await call_query(
        execute_gql, orderBy=[{"field": "NAME", "direction": "DESC"}]
    )
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert site_conditions_ids == desc_order(expected_order)

    # with multiple order by should match first
    site_conditions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert site_conditions_ids == expected_order

    site_conditions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert site_conditions_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hazards_and_controls_order_on_site_conditions_library(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check hazards and controls order on library site conditions query"""

    expected_order = list(await build_library_site_conditions_for_order_by(db_session))
    expected_hazards_order = list(await build_library_hazards_for_order_by(db_session))
    expected_controls_order = list(
        await build_library_controls_for_order_by(db_session)
    )
    await set_library_site_conditions_relations(
        db_session, expected_order, expected_hazards_order, expected_controls_order
    )

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    for direction, set_order in available_order:
        for hazard_direction, hazard_set_order in available_order:
            for control_direction, control_set_order in available_order:
                site_conditions = await call_query(
                    execute_gql,
                    withHazards=True,
                    orderBy=[{"field": "NAME", "direction": direction}],
                    hazardsOrderBy=[{"field": "NAME", "direction": hazard_direction}],
                    controlsOrderBy=[{"field": "NAME", "direction": control_direction}],
                )
                site_conditions_ids = [
                    i["id"] for i in site_conditions if i["id"] in expected_order
                ]
                assert set_order(site_conditions_ids) == expected_order
                for site_condition in site_conditions:
                    if site_condition["id"] in expected_order:
                        hazards_ids = [
                            i["id"]
                            for i in site_condition["hazards"]
                            if i["id"] in expected_hazards_order
                        ]
                        assert hazard_set_order(hazards_ids) == expected_hazards_order
                        for hazard in site_condition["hazards"]:
                            controls_ids = [
                                i["id"]
                                for i in hazard["controls"]
                                if i["id"] in expected_controls_order
                            ]
                            assert (
                                control_set_order(controls_ids)
                                == expected_controls_order
                            )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    expected_order = sorted(
        await build_library_site_conditions_for_order_by(db_session, name="cenas")
    )

    site_conditions = await call_query(
        execute_gql,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    site_conditions_ids = [
        i["id"] for i in site_conditions if i["id"] in expected_order
    ]
    assert site_conditions_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_query_only_includes_recommended_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available hazards for a given library site condition"""

    site_condition_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    hazard2_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding only hazard1 as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard1_id,
        library_control_id=control_id,
    )  # hazard2 already exists, but is not recommended and shouldn't be listed

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if only the recommended hazard is listed for now
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard1_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control_id)

    # also adding hazard2 as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard2_id,
        library_control_id=control_id,
    )  # hazard2 exists and is recommended, so it should also be listed

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if both recommended hazards are listed
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 2
    assert site_condition["hazards"][0]["id"] in [str(hazard1_id), str(hazard2_id)]
    if site_condition["hazards"][0]["id"] == str(hazard1_id):
        assert site_condition["hazards"][1]["id"] == str(hazard2_id)
    elif site_condition["hazards"][0]["id"] == str(hazard2_id):
        assert site_condition["hazards"][1]["id"] == str(hazard1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe
    assert site_condition["hazards"][0]["controls"][0]["id"] == str(control_id)
    assert site_condition["hazards"][1]["controls"][0]["id"] == str(control_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_query_only_includes_recommended_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available controls for a given library site condition"""

    site_condition_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    hazard_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding control1 only as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard_id,
        library_control_id=control1_id,
    )  # control2 already exists, but is not recommended and shouldn't be listed

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if only the recommended control is listed for now
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control1_id)

    # also adding control2 as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard_id,
        library_control_id=control2_id,
    )  # control2 already exists and is recommended, so it should also be listed

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if both recommended controls are listed
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 2
    assert hazard["controls"][0]["id"] in [str(control1_id), str(control2_id)]
    if hazard["controls"][0]["id"] == str(control1_id):
        assert hazard["controls"][1]["id"] == str(control2_id)
    elif hazard["controls"][0]["id"] == str(control2_id):
        assert hazard["controls"][1]["id"] == str(control1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_recommended_hazards_list_updated_upon_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available hazards for a given library site condition"""

    site_condition_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    hazard1_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    hazard2_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding both hazards as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard1_id,
        library_control_id=control_id,
    )
    temp_recommendation = await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard2_id,
        library_control_id=control_id,
    )

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if both recommended hazards are listed
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 2
    assert site_condition["hazards"][0]["id"] in [str(hazard1_id), str(hazard2_id)]
    if site_condition["hazards"][0]["id"] == str(hazard1_id):
        assert site_condition["hazards"][1]["id"] == str(hazard2_id)
    elif site_condition["hazards"][0]["id"] == str(hazard2_id):
        assert site_condition["hazards"][1]["id"] == str(hazard1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe
    assert site_condition["hazards"][0]["controls"][0]["id"] == str(control_id)
    assert site_condition["hazards"][1]["controls"][0]["id"] == str(control_id)

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if only the recommended hazard is listed now
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard1_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_recommended_controls_list_updated_upon_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of available controls for a given library site condition"""

    site_condition_id = str((await LibrarySiteConditionFactory.persist(db_session)).id)
    hazard_id = str(
        (await LibraryHazardFactory.with_tenant_settings_link(db_session)).id
    )
    control1_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    control2_id = str(
        (
            await LibraryControlFactory.with_tenant_settings_link(
                db_session, for_tasks=False, for_site_conditions=True
            )
        ).id
    )
    # adding both controls as recommended for site_condition
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard_id,
        library_control_id=control1_id,
    )
    temp_recommendation = await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=site_condition_id,
        library_hazard_id=hazard_id,
        library_control_id=control2_id,
    )

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if both recommended controls are listed
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 2
    assert hazard["controls"][0]["id"] in [str(control1_id), str(control2_id)]
    if hazard["controls"][0]["id"] == str(control1_id):
        assert hazard["controls"][1]["id"] == str(control2_id)
    elif hazard["controls"][0]["id"] == str(control2_id):
        assert hazard["controls"][1]["id"] == str(control1_id)
    else:
        assert False  # we shouldn't get here, but just a failsafe

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    site_conditions = await call_query(
        execute_gql, id=site_condition_id, withHazards=True
    )

    # Check if only the recommended control is listed for now
    assert site_conditions
    site_condition = site_conditions[0]
    assert uuid.UUID(site_condition["id"])
    assert site_condition["id"] == str(site_condition_id)
    assert site_condition["hazards"]
    assert len(site_condition["hazards"]) == 1
    hazard = site_condition["hazards"][0]
    assert hazard["id"] == hazard_id
    assert len(hazard["controls"]) == 1
    assert hazard["controls"][0]["id"] == str(control1_id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_with_tenant_settings_with_correct_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # create Library SiteCondition linked to 2 work types
    library_site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2
    )
    await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
        db_session, work_types[0].id, library_site_conditions[0].id
    )
    await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
        db_session, work_types[1].id, library_site_conditions[1].id
    )

    await TenantLibrarySiteConditionSettingsFactory.persist(
        db_session,
        library_site_condition_id=library_site_conditions[0].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_site_condition_name",
    )

    site_condition = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[work_types[0].id]
    )
    assert len(site_condition) == 1
    assert len(site_condition[0]["workTypes"]) == 1
    assert site_condition[0]["workTypes"][0]["id"] == str(work_types[0].id)

    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibrarySiteConditionSettings).where(
                col(TenantLibrarySiteConditionSettings.library_site_condition_id).in_(
                    [library_site_conditions[0].id, library_site_conditions[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_with_tenant_settings_with_incorrect_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    library_site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2
    )
    await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
        db_session, work_types[1].id, library_site_conditions[1].id
    )

    await TenantLibrarySiteConditionSettingsFactory.persist(
        db_session,
        library_site_condition_id=library_site_conditions[0].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_site_condition_name",
    )

    site_condition = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[work_types[0].id]
    )
    assert len(site_condition) == 0
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibrarySiteConditionSettings).where(
                col(TenantLibrarySiteConditionSettings.library_site_condition_id).in_(
                    [library_site_conditions[0].id, library_site_conditions[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_library_with_tenant_settings_with_incorrect_tenant_mapping(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    # create 2 work types linked to default tenant
    work_types = await WorkTypeFactory.persist_many_tenant_wt(db_session, size=2)

    # create Library SiteCondition linked to 2 work types
    library_site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=2
    )
    await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
        db_session, work_types[0].id, library_site_conditions[0].id
    )
    await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
        db_session, work_types[1].id, library_site_conditions[1].id
    )

    await TenantLibrarySiteConditionSettingsFactory.persist(
        db_session,
        library_site_condition_id=library_site_conditions[1].id,
        tenant_id=work_types[0].tenant_id,
        alias="tenant_specific_site_condition_name",
    )

    site_condition = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[work_types[0].id]
    )
    assert len(site_condition) == 0
    wt_sc_link = (
        await db_session.exec(
            select(WorkTypeLibrarySiteConditionLink).where(
                col(WorkTypeLibrarySiteConditionLink.work_type_id).in_(
                    [work_types[0].id, work_types[1].id]
                ),
            )
        )
    ).all()
    assert wt_sc_link

    tsc_links = (
        await db_session.exec(
            select(TenantLibrarySiteConditionSettings).where(
                col(TenantLibrarySiteConditionSettings.library_site_condition_id).in_(
                    [library_site_conditions[0].id, library_site_conditions[1].id]
                ),
            )
        )
    ).all()
    assert tsc_links
    await WorkTypeLibrarySiteConditionLinkFactory.delete_many(db_session, wt_sc_link)
    await TenantLibrarySiteConditionSettingsFactory.delete_many(db_session, tsc_links)
    await WorkTypeFactory.delete_many(db_session, work_types)
    await LibrarySiteConditionFactory.delete_many(db_session, library_site_conditions)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tenant_and_work_type_linked_library_site_conditions_with_ids_filter(
    db_session: AsyncSession, execute_gql: ExecuteGQL
) -> None:
    """Test that tenant_and_work_type_linked_library_site_conditions query filters by ids correctly"""
    # Create tenant and work types
    tenant = await TenantFactory.default_tenant(db_session)
    work_types = await WorkTypeFactory.persist_many_tenant_wt(
        db_session, size=2, tenant_id=tenant.id
    )

    # Create multiple library site conditions
    library_site_conditions = await LibrarySiteConditionFactory.persist_many(
        db_session, size=3
    )

    # Create tenant settings for each site condition
    for site_condition in library_site_conditions:
        existing_settings = (
            await db_session.exec(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.tenant_id == tenant.id,
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == site_condition.id,
                )
            )
        ).first()

        if not existing_settings:
            await TenantLibrarySiteConditionSettingsFactory.persist(
                db_session,
                library_site_condition_id=site_condition.id,
                tenant_id=tenant.id,
            )

    # Link all site conditions to both work types
    for site_condition in library_site_conditions:
        for work_type in work_types:
            await WorkTypeLibrarySiteConditionLinkFactory.get_or_create_work_type_site_condition_link(
                db_session, work_type.id, site_condition.id
            )

    # Test without ids filter (should return all 3 site conditions)
    site_conditions_without_filter = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[str(wt.id) for wt in work_types]
    )
    assert len(site_conditions_without_filter) == 3

    # Test with id filter for first site condition
    selected_id = str(library_site_conditions[0].id)
    site_conditions_with_filter = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[str(wt.id) for wt in work_types], id=selected_id
    )

    # Should only return the 1 filtered site condition
    assert len(site_conditions_with_filter) == 1
    assert site_conditions_with_filter[0]["id"] == selected_id

    # Test with id filter for second site condition
    second_id = str(library_site_conditions[1].id)
    site_conditions_second = await call_linked_query(
        execute_gql, tenantWorkTypeIds=[str(wt.id) for wt in work_types], id=second_id
    )

    # Should only return the 1 filtered site condition
    assert len(site_conditions_second) == 1
    assert site_conditions_second[0]["id"] == second_id

    # Cleanup
    # Delete work type links
    for site_condition in library_site_conditions:
        for work_type in work_types:
            links = (
                await db_session.exec(
                    select(WorkTypeLibrarySiteConditionLink).where(
                        WorkTypeLibrarySiteConditionLink.work_type_id == work_type.id,
                        WorkTypeLibrarySiteConditionLink.library_site_condition_id
                        == site_condition.id,
                    )
                )
            ).all()
            for link in links:
                await db_session.delete(link)

    # Delete tenant settings
    for site_condition in library_site_conditions:
        settings = (
            await db_session.exec(
                select(TenantLibrarySiteConditionSettings).where(
                    TenantLibrarySiteConditionSettings.library_site_condition_id
                    == site_condition.id
                )
            )
        ).all()
        for setting in settings:
            await db_session.delete(setting)

    await db_session.commit()
