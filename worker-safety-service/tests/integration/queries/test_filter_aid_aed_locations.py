from typing import Any

import pytest

from tests.factories import FirstAidAedLocationsFactory
from tests.integration.conftest import ExecuteGQL
from worker_safety_service.graphql.types import LocationType as location
from worker_safety_service.models import AsyncSession, LocationType

first_aid_aed_location_query = {
    "operation_name": "TestQuery",
    "query": """
     query TestQuery($locationType: LocationType!) {
        firstAidAedLocation(locationType: $locationType) {
          id
          locationName
          locationType
    }
}
""",
}


async def execute_query(execute_gql: ExecuteGQL, location_type: location) -> Any:
    variables = {"locationType": location_type.name}
    response = await execute_gql(**first_aid_aed_location_query, variables=variables)
    return response


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_first_aid_location_by_location_type_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location_type = "first_aid_location"
    await FirstAidAedLocationsFactory.persist_many(db_session, size=4)
    await FirstAidAedLocationsFactory.persist_many(
        db_session, size=5, location_type=location_type
    )
    response = await execute_query(
        execute_gql, location_type=LocationType.FIRST_AID_LOCATION
    )

    assert len(response["firstAidAedLocation"]) == 5


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_aed_location_by_location_type_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location_type = "first_aid_location"
    await FirstAidAedLocationsFactory.persist_many(db_session, size=7)
    await FirstAidAedLocationsFactory.persist_many(
        db_session, size=5, location_type=location_type
    )
    response = await execute_query(execute_gql, location_type=LocationType.AED_LOCATION)

    assert len(response["firstAidAedLocation"]) == 7


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_filter_burn_kit_location_by_location_type_query(
    execute_gql: ExecuteGQL, db_session: AsyncSession
) -> None:
    location_type = "burn_kit_location"
    await FirstAidAedLocationsFactory.persist_many(db_session, size=7)
    await FirstAidAedLocationsFactory.persist_many(
        db_session, size=5, location_type=location_type
    )
    response = await execute_query(
        execute_gql, location_type=LocationType.BURN_KIT_LOCATION
    )

    assert len(response["firstAidAedLocation"]) == 5
