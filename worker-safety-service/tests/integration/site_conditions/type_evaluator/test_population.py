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
        (0.0, 2500.0),
        (0.05, 2501.0),
        (0.05, 9999.0),
        (0.1, 10000.0),
    ],
)
async def test_population_density(
    data: tuple[float, float],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, density) = data
    applies = bool(multiplier)
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.population_density
    )
    world_data = generate_location_response(
        sources={"population"}, population_density=density  # type: ignore
    )
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.population_density
    assert site_condition.condition_value == {"density": density}
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
    assert site_condition.alert is applies
