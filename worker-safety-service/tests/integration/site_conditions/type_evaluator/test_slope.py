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
@pytest.mark.parametrize(
    "data",
    [
        (0.0, 14.9),
        (0.05, 15.0),
        (0.05, 16.0),
    ],
)
async def test_extreme_topography(
    data: tuple[float, float],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, slope) = data
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.extreme_topography
    )
    world_data = generate_location_response(sources={"slope"}, slope=slope)
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.extreme_topography
    assert site_condition.condition_value["slope"] == slope
    assert site_condition.condition_applies == bool(multiplier)
    assert site_condition.multiplier == multiplier
    assert site_condition.alert is bool(multiplier)
