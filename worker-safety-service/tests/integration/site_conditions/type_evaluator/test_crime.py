import pytest

from tests.integration.site_conditions.type_evaluator.helpers import (
    generate_location_response,
    get_library_site_condition,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.types import SiteConditionHandleCode


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("data", [(0.0, 199), (0.05, 200), (0.05, 2001)])
async def test_crime(
    data: tuple[float, int],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, crime_total_index) = data
    applies = bool(multiplier)
    alert = bool(multiplier)
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.crime
    )
    world_data = generate_location_response(
        sources={"crime"}, crime_total_index=crime_total_index
    )
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.crime
    assert site_condition.condition_value == {"total_index": crime_total_index}
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
    assert site_condition.alert == alert
