import pytest

from worker_safety_service.graphql.main import schema


@pytest.mark.asyncio
@pytest.mark.unit
async def test_site_conditions_query_requires_project_location_id() -> None:
    query = """
    query TestSiteConditionsQueryRequiresProjectLocationId($date: Date!){
      siteConditions(date: $date) {
        id
        name
        riskLevel
      }
    }
    """

    result = await schema.execute(query, variable_values={"date": "2022-01-01"})

    assert result.errors is not None


@pytest.mark.asyncio
@pytest.mark.unit
async def test_site_conditions_query_requires_date() -> None:
    query = """
    query TestSiteConditionsQueryRequiresDate($locationId: UUID!){
      siteConditions(locationId: $locationId) {
        id
        name
        riskLevel
      }
    }
    """

    result = await schema.execute(
        query,
        variable_values={"locationId": "5891fdf6-e6ac-47e0-be1e-33ea8c708b7e"},
    )

    assert result.errors is not None
