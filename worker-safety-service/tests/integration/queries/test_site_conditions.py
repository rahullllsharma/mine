import uuid
from collections import defaultdict
from datetime import date as DATE_TYPE
from datetime import datetime, timedelta
from typing import Any, Callable

import pytest
from httpx import AsyncClient

from tests.factories import (
    LibrarySiteConditionRecommendationsFactory,
    SiteConditionControlFactory,
    SiteConditionFactory,
    SiteConditionHazardFactory,
)
from tests.integration.conftest import ExecuteGQL
from tests.integration.helpers import valid_project_request
from tests.integration.queries.helpers import (
    asc_order,
    build_library_controls_for_order_by,
    build_library_hazards_for_order_by,
    build_library_site_conditions_for_order_by,
    create_site_conditions_for_sort,
    desc_order,
    set_library_site_conditions_relations,
)
from worker_safety_service.models import AsyncSession

site_conditions_query = """
query TestQuery ($siteConditionId: UUID, $locationId: UUID, $date: Date, $withHazards: Boolean! = false, $orderBy: [OrderBy!], $hazardsOrderBy: [OrderBy!], $controlsOrderBy: [OrderBy!]) {
  siteConditions(id: $siteConditionId, locationId: $locationId, date: $date, orderBy: $orderBy) {
    id
    name
    librarySiteCondition { id name }
    hazards (orderBy: $hazardsOrderBy) @include(if: $withHazards) {
        id
        name
        controls (orderBy: $controlsOrderBy) {
            id
            name
        }
    }
  }
}
"""


async def call_query(
    execute_gql: ExecuteGQL,
    site_condition_id: str | uuid.UUID | None = None,
    location_id: str | uuid.UUID | None = None,
    date: DATE_TYPE | None = None,
    **kwargs: Any,
) -> list[dict]:
    if site_condition_id:
        kwargs["siteConditionId"] = site_condition_id
    elif location_id:
        kwargs["locationId"] = location_id
        kwargs["date"] = date

    data = await execute_gql(query=site_conditions_query, variables=kwargs)
    site_conditions: list[dict] = data["siteConditions"]
    return site_conditions


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_no_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check site conditions no order"""

    location_id, expected_order = await create_site_conditions_for_sort(db_session)
    site_conditions = await call_query(
        execute_gql, location_id=location_id, orderBy=None
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert set(site_conditions_ids) == set(expected_order)

    site_conditions = await call_query(execute_gql, location_id=location_id, orderBy=[])
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert set(site_conditions_ids) == set(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_asc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check site conditions asc order"""

    location_id, expected_order = await create_site_conditions_for_sort(db_session)
    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert site_conditions_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_desc_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check site conditions desc order"""

    location_id, expected_order = await create_site_conditions_for_sort(db_session)
    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[{"field": "NAME", "direction": "DESC"}],
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert site_conditions_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_multiple_sort(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check site conditions multiple and duplicated order fields"""

    location_id, expected_order = await create_site_conditions_for_sort(db_session)
    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "NAME", "direction": "DESC"},
        ],
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert site_conditions_ids == expected_order

    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[
            {"field": "NAME", "direction": "DESC"},
            {"field": "NAME", "direction": "ASC"},
        ],
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert site_conditions_ids == desc_order(expected_order)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hazards_and_controls_order_on_site_conditions(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """Check hazards and controls order on site conditions query"""

    project_data = await valid_project_request(db_session, persist=True)
    location_id = project_data["locations"][0]["id"]
    library_site_condition_ids = await build_library_site_conditions_for_order_by(
        db_session
    )
    size = len(library_site_condition_ids)
    db_site_conditions = await SiteConditionFactory.persist_many(
        db_session,
        location_id=location_id,
        per_item_kwargs=[
            {"library_site_condition_id": i} for i in library_site_condition_ids
        ],
    )
    library_hazard_ids = await build_library_hazards_for_order_by(db_session, size=size)
    hazards = await SiteConditionHazardFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "site_condition_id": db_site_conditions[int(idx / size)].id,
                "library_hazard_id": library_hazard_id,
            }
            for idx, library_hazard_id in enumerate(library_hazard_ids)
        ],
    )
    library_control_ids = await build_library_controls_for_order_by(
        db_session, size=len(library_hazard_ids)
    )
    controls = await SiteConditionControlFactory.persist_many(
        db_session,
        per_item_kwargs=[
            {
                "site_condition_hazard_id": hazards[int(idx / size)].id,
                "library_control_id": library_control_id,
            }
            for idx, library_control_id in enumerate(library_control_ids)
        ],
    )

    expected_order = [str(i.id) for i in db_site_conditions]
    expected_hazards_order = defaultdict(list)
    for hazard in hazards:
        expected_hazards_order[str(hazard.site_condition_id)].append(str(hazard.id))
    expected_controls_order = defaultdict(list)
    for control in controls:
        expected_controls_order[str(control.site_condition_hazard_id)].append(
            str(control.id)
        )

    available_order = [("ASC", asc_order), ("DESC", desc_order)]
    for direction, set_order in available_order:
        for hazard_direction, hazard_set_order in available_order:
            for control_direction, control_set_order in available_order:
                site_conditions = await call_query(
                    execute_gql,
                    location_id=location_id,
                    withHazards=True,
                    orderBy=[{"field": "NAME", "direction": direction}],
                    hazardsOrderBy=[{"field": "NAME", "direction": hazard_direction}],
                    controlsOrderBy=[{"field": "NAME", "direction": control_direction}],
                )
                site_conditions_ids = [i["id"] for i in site_conditions]
                assert set_order(site_conditions_ids) == expected_order
                for site_condition_item in site_conditions:
                    hazards_ids = [i["id"] for i in site_condition_item["hazards"]]
                    assert (
                        hazard_set_order(hazards_ids)
                        == expected_hazards_order[site_condition_item["id"]]
                    )
                    for hazard_item in site_condition_item["hazards"]:
                        controls_ids = [i["id"] for i in hazard_item["controls"]]
                        assert (
                            control_set_order(controls_ids)
                            == expected_controls_order[hazard_item["id"]]
                        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_duplicated_name(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location_id, expected_order = await create_site_conditions_for_sort(
        db_session, name="cenas"
    )
    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[
            {"field": "NAME", "direction": "ASC"},
            {"field": "ID", "direction": "ASC"},
        ],
    )
    site_conditions_ids = [i["id"] for i in site_conditions]
    assert site_conditions_ids == expected_order


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_none_found(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (_, _, _) = await SiteConditionFactory.with_project_and_location(db_session)
    test_id = uuid.uuid4()
    site_conditions: list[dict] = await call_query(
        execute_gql, site_condition_id=test_id
    )
    assert len(site_conditions) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_found(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        site_condition,
        _,
        _,
    ) = await SiteConditionFactory.with_project_and_location(db_session)
    site_conditions: list[dict] = await call_query(
        execute_gql, site_condition_id=site_condition.id
    )
    assert len(site_conditions) == 1
    assert site_conditions[0]["id"] == str(site_condition.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_with_alert_found(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        _,
        _,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)
    date = datetime.now().date()
    site_condition_with_alert = await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location.id,
        alert=True,
        date=date,
    )
    site_conditions: list[dict] = await call_query(
        execute_gql, site_condition_id=site_condition_with_alert.id
    )
    assert len(site_conditions) == 1
    assert site_conditions[0]["id"] == str(site_condition_with_alert.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_without_alert_not_found(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        _,
        _,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)
    date = datetime.now().date()
    site_condition_with_alert = await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location.id,
        alert=False,
        date=date,
    )
    site_conditions: list[dict] = await call_query(
        execute_gql, site_condition_id=site_condition_with_alert.id
    )
    assert len(site_conditions) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_with_alert_not_found_with_wrong_date(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        site_condition,
        _,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)
    date = datetime.now().date()
    site_condition_with_alert = await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location.id,
        alert=True,
        date=date,
    )
    query_date = date - timedelta(days=5)

    site_conditions: list[dict] = await call_query(
        execute_gql, location_id=location.id, date=query_date
    )
    assert len(site_conditions) == 1
    assert site_conditions[0]["id"] == str(site_condition.id)
    assert site_conditions[0]["id"] != str(site_condition_with_alert.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_with_alert_found_with_correct_date(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    (
        _,
        _,
        location,
    ) = await SiteConditionFactory.with_project_and_location(db_session)
    date = datetime.now().date()
    await SiteConditionFactory.persist_evaluated(
        db_session,
        location_id=location.id,
        alert=True,
        date=date,
    )

    site_conditions: list[dict] = await call_query(
        execute_gql, location_id=location.id, date=date
    )
    assert len(site_conditions) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_includes_even_nonrecommended_hazards(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of hazards for a site condition regardless of recommendations from the library"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, lh2, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lsc1, _, _ = await build_library_site_conditions_for_order_by(
        db_session
    )  # IDs for library site conditions
    await set_library_site_conditions_relations(
        db_session, [lsc1], [lh1], [lc1, lc2]
    )  # library site condition 1 only has recommendations for a single hazard with 2 controls

    # set up SiteCondition and its hazards and controls
    site_condition_1 = await SiteConditionFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
    )
    hazard_1 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh1,
    )
    hazard_2 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh2,
    )
    control_11 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc1,
    )
    control_12 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc2,
    )
    control_21 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_2.id,
        library_control_id=lc1,
    )
    # site_condition_1 will have a hazard of type lh2, even though it's not recommended

    queried_site_conditions = await call_query(
        execute_gql, siteConditionId=site_condition_1.id, withHazards=True
    )

    # Check if both hazards are listed
    assert queried_site_conditions
    queried_site_condition = queried_site_conditions[0]
    assert uuid.UUID(queried_site_condition["id"])
    assert queried_site_condition["id"] == str(site_condition_1.id)
    assert queried_site_condition["hazards"]
    assert len(queried_site_condition["hazards"]) == 2

    if queried_site_condition["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_site_condition["hazards"][0]
        second_hazard = queried_site_condition["hazards"][1]
    elif queried_site_condition["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_site_condition["hazards"][1]
        second_hazard = queried_site_condition["hazards"][0]
    else:
        assert False  # we shouldn't get here, but just failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 2
    assert first_hazard["controls"][0]["id"] in [str(control_11.id), str(control_12.id)]
    assert first_hazard["controls"][1]["id"] in [str(control_11.id), str(control_12.id)]
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_21.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_includes_even_nonrecommended_controls(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of controls for a site condition regardless of recommendations from the library"""

    # set up library and recommendations
    lc1, lc2, lc3 = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, _, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lsc1, _, _ = await build_library_site_conditions_for_order_by(
        db_session
    )  # IDs for library site conditions
    await set_library_site_conditions_relations(
        db_session, [lsc1], [lh1], [lc1, lc2]
    )  # library site condition 1 has recommendations of hazard 1 with controls 1 and 2

    # set up SiteConditions and their hazards and controls
    site_condition_1 = await SiteConditionFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
    )
    hazard_1 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh1,
    )  # will have all recommended controls
    control11 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc1,
    )
    control12 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc2,
    )

    site_condition_2 = await SiteConditionFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
    )
    hazard_2 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_2.id,
        library_hazard_id=lh1,
    )  # won't have all recommended controls, and also one that is not recommended
    control21 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_2.id,
        library_control_id=lc1,
    )
    control23 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_2.id,
        library_control_id=lc3,
    )  # not recommended for library hazard 1

    first_queried_site_conditions = await call_query(
        execute_gql, siteConditionId=site_condition_1.id, withHazards=True
    )
    second_queried_site_conditions = await call_query(
        execute_gql, siteConditionId=site_condition_2.id, withHazards=True
    )

    # Check if both hazards list all their controls
    assert first_queried_site_conditions
    assert second_queried_site_conditions

    first_sc = first_queried_site_conditions[0]
    second_sc = second_queried_site_conditions[0]

    assert len(first_sc["hazards"]) == 1
    first_hazard = first_sc["hazards"][0]
    assert len(second_sc["hazards"]) == 1
    second_hazard = second_sc["hazards"][0]

    assert first_hazard["id"] == str(hazard_1.id)
    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 2
    assert first_hazard["controls"][0]["id"] in [str(control11.id), str(control12.id)]
    assert first_hazard["controls"][1]["id"] in [str(control11.id), str(control12.id)]
    assert len(second_hazard["controls"]) == 2
    assert second_hazard["controls"][0]["id"] in [str(control21.id), str(control23.id)]
    assert second_hazard["controls"][1]["id"] in [str(control21.id), str(control23.id)]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_still_includes_hazards_after_recommendation_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of hazards for a given library site condition regardless of recommendation availability"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, lh2, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lsc1, _, _ = await build_library_site_conditions_for_order_by(
        db_session
    )  # IDs for library site conditions
    # adding both hazards and controls as recommended for site condition 1
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
        library_hazard_id=lh1,
        library_control_id=lc1,
    )
    temp_recommendation = await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
        library_hazard_id=lh2,
        library_control_id=lc2,
    )

    # set up SiteCondition with its recommended hazards and controls
    site_condition_1 = await SiteConditionFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
    )
    location_id = site_condition_1.location_id
    hazard_1 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh1,
    )
    control_1 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc1,
    )
    hazard_2 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh2,
    )
    control_2 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_2.id,
        library_control_id=lc2,
    )

    queried_site_conditions = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if both hazards are listed
    assert queried_site_conditions
    queried_site_condition = queried_site_conditions[0]
    assert uuid.UUID(queried_site_condition["id"])
    assert queried_site_condition["id"] == str(site_condition_1.id)
    assert queried_site_condition["hazards"]
    assert len(queried_site_condition["hazards"]) == 2

    if queried_site_condition["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_site_condition["hazards"][0]
        second_hazard = queried_site_condition["hazards"][1]
    elif queried_site_condition["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_site_condition["hazards"][1]
        second_hazard = queried_site_condition["hazards"][0]
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 1
    assert first_hazard["controls"][0]["id"] == str(control_1.id)
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_2.id)

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    # Check if site_condition1's hazards are both still listed
    assert queried_site_conditions
    queried_site_condition = queried_site_conditions[0]
    assert uuid.UUID(queried_site_condition["id"])
    assert queried_site_condition["id"] == str(site_condition_1.id)
    assert queried_site_condition["hazards"]
    assert len(queried_site_condition["hazards"]) == 2

    if queried_site_condition["hazards"][0]["id"] == str(hazard_1.id):
        first_hazard = queried_site_condition["hazards"][0]
        second_hazard = queried_site_condition["hazards"][1]
    elif queried_site_condition["hazards"][0]["id"] == str(hazard_2.id):
        first_hazard = queried_site_condition["hazards"][1]
        second_hazard = queried_site_condition["hazards"][0]
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    assert second_hazard["id"] == str(hazard_2.id)
    assert len(first_hazard["controls"]) == 1
    assert first_hazard["controls"][0]["id"] == str(control_1.id)
    assert len(second_hazard["controls"]) == 1
    assert second_hazard["controls"][0]["id"] == str(control_2.id)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_still_includes_controls_after_recommendation_removal(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """Check sanity of controls for a given library site_condition regardless of recommendation availability"""

    # set up library and recommendations
    lc1, lc2, _ = await build_library_controls_for_order_by(
        db_session
    )  # IDs for library controls
    lh1, _, _ = await build_library_hazards_for_order_by(
        db_session
    )  # IDs for library hazards
    lsc1, _, _ = await build_library_site_conditions_for_order_by(
        db_session
    )  # IDs for library site_conditions
    # adding both hazards and controls as recommended for site_condition 1
    await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
        library_hazard_id=lh1,
        library_control_id=lc1,
    )
    temp_recommendation = await LibrarySiteConditionRecommendationsFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
        library_hazard_id=lh1,
        library_control_id=lc2,
    )

    # set up SiteCondition with its recommended hazards and controls
    site_condition_1 = await SiteConditionFactory.persist(
        db_session,
        library_site_condition_id=lsc1,
    )
    location_id = site_condition_1.location_id
    hazard_1 = await SiteConditionHazardFactory.persist(
        db_session,
        site_condition_id=site_condition_1.id,
        library_hazard_id=lh1,
    )
    control_1 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc1,
    )
    control_2 = await SiteConditionControlFactory.persist(
        db_session,
        site_condition_hazard_id=hazard_1.id,
        library_control_id=lc2,
    )

    queried_site_conditions = await call_query(
        execute_gql, location_id=location_id, withHazards=True
    )

    # Check if the site condition's hazard lists both controls
    assert queried_site_conditions
    assert len(queried_site_conditions) == 1
    queried_site_condition = queried_site_conditions[0]
    assert len(queried_site_condition["hazards"]) == 1
    queried_hazard = queried_site_condition["hazards"][0]
    assert len(queried_hazard["controls"]) == 2
    if queried_hazard["controls"][0]["id"] == str(control_1.id):
        assert queried_hazard["controls"][1]["id"] == str(control_2.id)
    elif queried_hazard["controls"][0]["id"] == str(control_2.id):
        assert queried_hazard["controls"][1]["id"] == str(control_1.id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case

    # Remove one of the recommendations
    await db_session.delete(temp_recommendation)
    await db_session.commit()

    # Check if the site condition's hazard still lists both controls, even the one that is no longer recommended
    assert queried_site_conditions
    assert len(queried_site_conditions) == 1
    queried_site_condition = queried_site_conditions[0]
    assert len(queried_site_condition["hazards"]) == 1
    queried_hazard = queried_site_condition["hazards"][0]
    assert len(queried_hazard["controls"]) == 2
    if queried_hazard["controls"][0]["id"] == str(control_1.id):
        assert queried_hazard["controls"][1]["id"] == str(control_2.id)
    elif queried_hazard["controls"][0]["id"] == str(control_2.id):
        assert queried_hazard["controls"][1]["id"] == str(control_1.id)
    else:
        assert False  # we shouldn't get here, but failsafe just in case


@pytest.mark.asyncio
@pytest.mark.integration
async def test_post_archiving_library_site_condition_site_condition_name_change(
    rest_client: Callable[..., AsyncClient],
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    location_id, _ = await create_site_conditions_for_sort(db_session)

    site_conditions = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    names_before_archiving = {sc["name"] for sc in site_conditions}
    assert names_before_archiving == {"á 1", "A 2", "a 3"}

    # archive Library Site Condition
    sc_1 = site_conditions[1]
    library_site_condition_id = sc_1["librarySiteCondition"]["id"]
    response = await rest_client().delete(
        url=f"http://127.0.0.1:8000/rest/library-site-conditions/{library_site_condition_id}"
    )
    assert response.status_code == 204

    # retest names getting updated
    site_conditions_1 = await call_query(
        execute_gql,
        location_id=location_id,
        orderBy=[{"field": "NAME", "direction": "ASC"}],
    )
    names_after_archiving = {sc["name"] for sc in site_conditions_1}
    assert names_after_archiving == {"á 1", "A 2 (archived)", "a 3"}
