import uuid
from datetime import datetime, timedelta, timezone

import pytest

import tests.factories as factories
from tests.factories import LocationFactory, SiteConditionFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.models import AsyncSession, Location, SiteCondition

project_with_locations_and_site_conditions_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($projectId: UUID!, $date: Date) {
  project(projectId: $projectId) {
    id
    name
    locations {
      id
      siteConditions(date: $date){
        id
      }
    }
  }
}
""",
}

all_locations_with_site_conditions_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($date: Date) {
  projectLocations {
    id
    siteConditions(date: $date){
      id
    }
  }
}
""",
}

all_site_conditions_query = {
    "operation_name": "TestQuery",
    "query": """
query TestQuery($locationId: UUID) {
  siteConditions(locationId: $locationId) {
    id
  }
}
""",
}


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_query_with_archiving(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Creates a few site_conditions, archives one, and ensures the archived never leaves.

    Tests fetching a few different ways:
    - `project(projectId)` - fetch a single project
    - `projectLocation` - fetch a single project
    - `siteConditions` - fetch all site conditions
    """

    location: Location = await LocationFactory.persist(db_session)
    site_conditions: list[SiteCondition] = await SiteConditionFactory.persist_many(
        db_session, size=3, location_id=location.id
    )
    to_archive = site_conditions[1]
    to_archive.archived_at = datetime.now(timezone.utc)
    await db_session.commit()
    expected_site_condition_ids = set(
        map(
            lambda x: str(x.id),
            filter(lambda x: not x.id == to_archive.id, site_conditions),
        )
    )

    ###########################################################
    # project_with_locations_and_site_conditions_query

    data = await execute_gql(
        **project_with_locations_and_site_conditions_query,
        variables={"projectId": str(location.project_id)},
    )
    assert data["project"]["id"] == str(location.project_id)  # sanity check
    fetched_site_conditions = data["project"]["locations"][0]["siteConditions"]
    fetched_site_condition_ids: set[uuid.UUID] = {
        i["id"] for i in fetched_site_conditions
    }

    assert len(fetched_site_conditions) == 2
    assert expected_site_condition_ids == fetched_site_condition_ids

    ###########################################################
    # all_locations_with_site_conditions_query

    data = await execute_gql(**all_locations_with_site_conditions_query)
    fetched_locs = data["projectLocations"]
    loc = list(filter(lambda x: x["id"] == str(location.id), fetched_locs))[0]
    fetched_site_conditions = loc["siteConditions"]
    fetched_site_condition_ids = {i["id"] for i in fetched_site_conditions}

    assert len(fetched_site_conditions) == 2
    assert expected_site_condition_ids == fetched_site_condition_ids

    ###########################################################
    # all_site_conditions_query

    data = await execute_gql(**all_site_conditions_query)
    fetched_site_conditions = data["siteConditions"]
    fetched_site_condition_ids = {i["id"] for i in fetched_site_conditions}

    assert str(to_archive.id) not in fetched_site_condition_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_with_date_filter(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    """
    Filters by date on:
    - Project.locations.siteConditions
    - ProjectLocation.siteConditions
    - SiteConditions
    """
    location = await LocationFactory.persist(db_session)
    site_conditions: dict[uuid.UUID, SiteCondition] = {
        i.library_site_condition_id: i
        for i in await SiteConditionFactory.persist_many(
            db_session, size=3, location_id=location.id
        )
    }

    date = datetime.now().date()
    evaluated_site_conditions = await SiteConditionFactory.persist_many_evaluated(
        db_session,
        [
            {
                "location_id": location.id,
                "alert": True,
                "date": date,
                "library_site_condition_id": sc.library_site_condition_id,
            }
            for sc in site_conditions.values()
        ],
    )

    # Set site_condition[0] to lower date
    old_date = date - timedelta(days=10)
    old_evaluated = evaluated_site_conditions[0]
    old_evaluated.date = old_date
    await db_session.commit()

    # We should return evaluation instead if manually added
    expected_site_condition_ids = {str(i.id) for i in evaluated_site_conditions[1:]}
    # We should return manually added if no evaluation is present
    expected_site_condition_ids.add(
        str(site_conditions[old_evaluated.library_site_condition_id].id)
    )
    date_str = date.strftime("%Y-%m-%d")

    # Test Project.locations.siteConditions Query
    data = await execute_gql(
        **project_with_locations_and_site_conditions_query,
        variables={"projectId": str(location.project_id), "date": date_str},
    )
    assert data["project"]["id"] == str(location.project_id)  # sanity check
    fetched_site_conditions = data["project"]["locations"][0]["siteConditions"]
    fetched_site_condition_ids = {x["id"] for x in fetched_site_conditions}
    assert fetched_site_condition_ids == expected_site_condition_ids

    # Test ProjectLocation.siteConditions Query
    data = await execute_gql(
        **all_locations_with_site_conditions_query, variables={"date": date_str}
    )
    fetched_locs = data["projectLocations"]
    loc = [fl for fl in fetched_locs if fl["id"] == str(location.id)][0]
    fetched_site_conditions = loc["siteConditions"]
    fetched_site_condition_ids = {x["id"] for x in fetched_site_conditions}
    assert fetched_site_condition_ids == expected_site_condition_ids


@pytest.mark.asyncio
@pytest.mark.integration
async def test_site_conditions_query_returns_manually_added_and_auto_populated_conditions_with_alert(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    [
        lib_site_condition1,
        lib_site_condition2,
        lib_site_condition3,
        lib_site_condition4,
    ] = await factories.LibrarySiteConditionFactory.persist_many(db_session, size=4)
    project = await factories.WorkPackageFactory.persist(db_session)
    location = await factories.LocationFactory.persist(
        db_session, project_id=project.id
    )
    await factories.SiteConditionFactory.batch_with_project_and_location(
        db_session,
        [
            {
                "project": project,
                "location": location,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition1.id
                },
            },
            {
                "project": project,
                "location": location,
                "site_condition_kwargs": {
                    "library_site_condition_id": lib_site_condition2.id
                },
            },
        ],
    )
    date = datetime.now().date()
    await factories.SiteConditionFactory.persist_many_evaluated(
        db_session,
        [
            {
                "location_id": location.id,
                "library_site_condition_id": lib_site_condition3.id,
                "alert": True,
                "date": date,
            },
            {
                "location_id": location.id,
                "library_site_condition_id": lib_site_condition4.id,
                "alert": False,
                "date": date,
            },
        ],
    )

    date_str = date.strftime("%Y-%m-%d")

    data = await execute_gql(
        **project_with_locations_and_site_conditions_query,
        variables={
            "projectId": str(location.project_id),
            "date": date_str,
        },
    )

    fetched_site_conditions = data["project"]["locations"][0]["siteConditions"]
    assert len(fetched_site_conditions) == 3
