import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

import tests.factories as factories
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession

from .helpers import (
    HazardsResult,
    SampleControl,
    assert_hazards_count,
    assert_hazards_data,
    batch_upsert_control_report,
    to_portfolio_input,
    to_project_input,
)

################################################################################
# Test Query and helper

project_site_condition_query = """
query TestQuery($filter: ProjectLearningsInput!,
  $libraryHazardId: UUID!,
) {
  projectLearnings(projectLearningsInput: $filter) {
    applicableHazardsBySiteCondition(libraryHazardId: $libraryHazardId) {
      count librarySiteCondition { id name }
    }
  }
}
"""

portfolio_site_condition_query = """
query TestQuery($filter: PortfolioLearningsInput!,
  $libraryHazardId: UUID!,
) {
  portfolioLearnings(portfolioLearningsInput: $filter) {
    applicableHazardsBySiteCondition(libraryHazardId: $libraryHazardId) {
      count librarySiteCondition { id name }
    }
  }
}
"""


async def execute_applicable_hazards(
    execute_gql: ExecuteGQL,
    query: str,
    user: Any,
    library_hazard_id: uuid.UUID,
    **filters: Any,
) -> Any:
    filt = None
    query_name = None
    sub_query_name = None
    if query in [project_site_condition_query]:
        filt = to_project_input(**filters)
        query_name = "projectLearnings"
    elif query in [portfolio_site_condition_query]:
        filt = to_portfolio_input(**filters)
        query_name = "portfolioLearnings"

    if query in [project_site_condition_query, portfolio_site_condition_query]:
        sub_query_name = "applicableHazardsBySiteCondition"
    assert sub_query_name

    data = await execute_gql(
        query=query,
        user=user,
        variables={"filter": filt, "libraryHazardId": library_hazard_id},
    )
    return data[query_name][sub_query_name]


async def assert_applicable_hazards(
    execute_gql: ExecuteGQL,
    query: str,
    filters: Any,
    expected_data: dict[uuid.UUID, HazardsResult] | None = None,
    expected_count: list[int] | None = None,
    user: Any = None,
) -> None:
    hazards_data = await execute_applicable_hazards(execute_gql, query, user, **filters)

    if isinstance(expected_count, list):
        assert_hazards_count(expected_count, hazards_data)

    if expected_data:
        assert_hazards_data(expected_data, hazards_data)


################################################################################
# Tests


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_site_condition(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    Creates applicable hazards on daily-reports across 3 site_conditions.
    Queries for applicable-hazards-by-site_condition for each library_hazard.
    Tests for both project and portfolio learnings.
    """
    tenant, admin = await factories.TenantFactory.new_with_admin(db_session)
    project = await factories.WorkPackageFactory.persist(
        db_session, tenant_id=tenant.id
    )
    (
        lib_site_condition1,
        lib_site_condition2,
        lib_site_condition3,
    ) = await factories.LibrarySiteConditionFactory.persist_many(db_session, size=3)
    (
        (
            site_condition1,
            _,
            _,
        ),
        (
            site_condition2,
            _,
            _,
        ),
        (
            site_condition3,
            _,
            _,
        ),
    ) = await factories.SiteConditionFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition1.id
                },
            },
            {
                "project": project,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition2.id
                },
            },
            {
                "project": project,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition3.id
                },
            },
        ],
    )
    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
        },
    )

    # portfolio site_condition, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={**filters, "library_hazard_id": hazard1.id},
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=2, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )
    # portfolio site_condition, hazard2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={**filters, "library_hazard_id": hazard2.id},
        expected_data={
            lib_site_condition3.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition3.name
            ),
        },
    )

    # portfolio site_condition, hazard1, only day 2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={**filters, "library_hazard_id": hazard1.id, "start_date": day2},
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )

    # project site_condition, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=2, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )
    # project site_condition, hazard2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
        },
        expected_data={
            lib_site_condition3.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition3.name
            ),
        },
    )

    # project site_condition, hazard1, only day 2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "start_date": day2,
            "project_id": project.id,
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_site_condition_location_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant, admin = await factories.TenantFactory.new_with_admin(db_session)
    project = await factories.WorkPackageFactory.persist(
        db_session, tenant_id=tenant.id
    )
    location1, location2 = await factories.LocationFactory.persist_many(
        db_session, project_id=project.id, size=2
    )
    (
        lib_site_condition1,
        lib_site_condition2,
        lib_site_condition3,
    ) = await factories.LibrarySiteConditionFactory.persist_many(db_session, size=3)
    (
        (
            site_condition1,
            _,
            _,
        ),
        (
            site_condition2,
            _,
            _,
        ),
        (
            site_condition3,
            _,
            _,
        ),
    ) = await factories.SiteConditionFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location1,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition1.id
                },
            },
            {
                "project": project,
                "location": location2,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition2.id
                },
            },
            {
                "project": project,
                "location": location2,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition3.id
                },
            },
        ],
    )
    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
        },
    )

    # project site_condition, both locations, hazard 1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=2, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )
    # project site_condition, both locations, hazard 2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id, location2.id],
        },
        expected_data={
            lib_site_condition3.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition3.name
            ),
        },
    )

    # project site_condition, location1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
        },
    )
    # project site_condition, location1, hazard2
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard2.id,
            "project_id": project.id,
            "location_ids": [location1.id],
        },
        expected_data={},
        expected_count=[],
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_site_condition_project_filter(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    tenant, admin = await factories.TenantFactory.new_with_admin(db_session)
    project1, project2 = await factories.WorkPackageFactory.persist_many(
        db_session, size=2, tenant_id=tenant.id
    )
    (
        lib_site_condition1,
        lib_site_condition2,
        lib_site_condition3,
    ) = await factories.LibrarySiteConditionFactory.persist_many(db_session, size=3)
    (
        (
            site_condition1,
            _,
            _,
        ),
        (
            site_condition2,
            _,
            _,
        ),
        (
            site_condition3,
            _,
            _,
        ),
    ) = await factories.SiteConditionFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project1,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition1.id
                },
            },
            {
                "project": project2,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition2.id
                },
            },
            {
                "project": project2,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition3.id
                },
            },
        ],
    )
    day1, day2 = [datetime.now(timezone.utc) + timedelta(days=n) for n in range(2)]
    hazard1, hazard2 = await factories.LibraryHazardFactory.persist_many(
        db_session, size=2
    )
    filters = dict(start_date=day1, end_date=day2)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
            day2: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard1,
                    site_condition=site_condition2,
                ),
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=hazard2,
                    site_condition=site_condition3,
                ),
            ],
        },
    )

    # portfolio site_condition, both projects, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id, project2.id],
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
            lib_site_condition2.id: HazardsResult(
                count=2, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )

    # portfolio site_condition, project1, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project1.id],
        },
        expected_data={
            lib_site_condition1.id: HazardsResult(
                count=1, library_site_condition_name=lib_site_condition1.name
            ),
        },
    )

    # portfolio site_condition, project2, hazard1
    await assert_applicable_hazards(
        execute_gql,
        user=admin,
        query=portfolio_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": hazard1.id,
            "project_ids": [project2.id],
        },
        expected_data={
            lib_site_condition2.id: HazardsResult(
                count=2, library_site_condition_name=lib_site_condition2.name
            ),
        },
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_site_condition_limit_ten(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should return the ten largest applicable count.
    """
    day1 = datetime.now(timezone.utc)
    library_site_conditions = await factories.LibrarySiteConditionFactory.persist_many(
        db_session, size=11
    )
    project = await factories.WorkPackageFactory.persist(db_session)
    site_condition_tuples = (
        await factories.SiteConditionFactory.batch_with_project_and_location(
            db_session,
            [
                {
                    "project": project,
                    "site_condition_kwargs": {
                        "library_site_condition_id": lib_site_condition.id
                    },
                }
                for lib_site_condition in library_site_conditions
            ],
        )
    )
    site_conditions = list(map(lambda t: t[0], site_condition_tuples))
    library_hazard = await factories.LibraryHazardFactory.persist(db_session)
    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=library_hazard,
                    site_condition=site_condition,
                )
                for site_condition in site_conditions
            ]
        },
    )

    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_site_condition_query,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1] * 10,
    )
    await assert_applicable_hazards(
        execute_gql,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": library_hazard.id,
            "project_id": project.id,
        },
        expected_count=[1] * 10,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_applicable_hazards_by_site_condition_drop_zeroes(
    execute_gql: ExecuteGQL,
    db_session: AsyncSession,
) -> None:
    """
    This endpoint should drop zeroes.
    """
    day1 = datetime.now(timezone.utc)
    library_site_conditions = await factories.LibrarySiteConditionFactory.persist_many(
        db_session, size=2
    )
    project = await factories.WorkPackageFactory.persist(db_session)
    site_condition_tuples = (
        await factories.SiteConditionFactory.batch_with_project_and_location(
            db_session,
            [
                {
                    "project": project,
                    "site_condition_kwargs": {
                        "library_site_condition_id": lib_site_condition.id
                    },
                }
                for lib_site_condition in library_site_conditions
            ],
        )
    )
    site_condition1, site_condition2 = list(map(lambda t: t[0], site_condition_tuples))
    library_hazard = await factories.LibraryHazardFactory.persist(db_session)
    filters = dict(start_date=day1, end_date=day1)

    await batch_upsert_control_report(
        db_session,
        {
            day1: [
                SampleControl(
                    hazard_is_applicable=True,
                    library_hazard=library_hazard,
                    site_condition=site_condition1,
                ),
                SampleControl(
                    hazard_is_applicable=False,
                    library_hazard=library_hazard,
                    site_condition=site_condition2,
                ),
            ]
        },
    )

    # portfolio site_condition
    await assert_applicable_hazards(
        execute_gql,
        query=portfolio_site_condition_query,
        filters={**filters, "library_hazard_id": library_hazard.id},
        expected_count=[1],
    )
    # project site_condition
    await assert_applicable_hazards(
        execute_gql,
        query=project_site_condition_query,
        filters={
            **filters,
            "library_hazard_id": library_hazard.id,
            "project_id": project.id,
        },
        expected_count=[1],
    )
