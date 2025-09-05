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
        (SiteConditionHandleCode.heat_index, {"max_apparent_temperature": 200.00}, 0.1),
        (SiteConditionHandleCode.heat_index, {"max_apparent_temperature": 103.01}, 0.1),
        (SiteConditionHandleCode.heat_index, {"max_apparent_temperature": 103.0}, 0.05),
        (SiteConditionHandleCode.heat_index, {"max_apparent_temperature": 91.0}, 0.05),
        (SiteConditionHandleCode.heat_index, {"max_apparent_temperature": 89.99}, 0.0),
        (SiteConditionHandleCode.cold_index, {"min_temperature": -100.0}, 0.05),
        (SiteConditionHandleCode.cold_index, {"min_temperature": 25.99}, 0.05),
        (SiteConditionHandleCode.cold_index, {"min_temperature": 26}, 0.0),
        (SiteConditionHandleCode.high_winds, {"gust": 200.00}, 0.1),
        (SiteConditionHandleCode.high_winds, {"gust": 40.01}, 0.1),
        (SiteConditionHandleCode.high_winds, {"gust": 40.0}, 0.05),
        (SiteConditionHandleCode.high_winds, {"gust": 30.0}, 0.05),
        (SiteConditionHandleCode.high_winds, {"gust": 29.99}, 0.0),
    ],
)
async def test_day_signature(
    data: tuple[SiteConditionHandleCode, dict, float | None],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    site_condition_type, weather_data, multiplier = data
    applies = bool(multiplier)

    library_site_condition = await get_library_site_condition(
        db_session, site_condition_type
    )
    world_data = generate_location_response(sources={"weather"}, **weather_data)
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == site_condition_type
    assert site_condition.condition_value == weather_data
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        (0.1, 80, 0),
        (0.1, 0, 95),
        (0.0, 79, 94),
    ],
)
async def test_slip(
    data: tuple[float | None, int, int],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (
        multiplier,
        precipitation_probability_pct,
        previous_precipitation_probability_pct,
    ) = data
    applies = bool(multiplier)

    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.slip
    )

    world_data_day = generate_location_response(
        sources={"weather"}, precipitation_probability_pct=precipitation_probability_pct
    )
    world_data_previous = generate_location_response(
        sources={"weather"},
        precipitation_probability_pct=previous_precipitation_probability_pct,
    )
    world_data_dict = {0: world_data_day, 1: world_data_previous}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )

    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.slip
    assert site_condition.condition_value == {
        "current_day_precipitation": precipitation_probability_pct,
        "previous_day_precipitation": previous_precipitation_probability_pct,
    }
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        (0.1, 80, 0, 32),
        (0.1, 0, 95, 32),
        (0.1, 80, 95, 32),
        (0.0, 80, 95, 32.01),
        (0.0, 0, 0, -100.0),
        (0.0, 100, 100, 50.0),
    ],
)
async def test_wet_or_frozen_ground(
    data: tuple[float | None, int, int, float],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (
        multiplier,
        precipitation_probability_pct,
        previous_precipitation_probability_pct,
        min_temperature,
    ) = data
    applies = bool(multiplier)

    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.wet_or_frozen_ground
    )
    world_data_day = generate_location_response(
        sources={"weather"},
        precipitation_probability_pct=precipitation_probability_pct,
        min_temperature=min_temperature,
    )
    world_data_previous = generate_location_response(
        sources={"weather"},
        precipitation_probability_pct=previous_precipitation_probability_pct,
    )
    world_data_dict = {0: world_data_day, 1: world_data_previous}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.wet_or_frozen_ground
    assert site_condition.condition_value == {
        "current_day_precipitation": precipitation_probability_pct,
        "previous_day_precipitation": previous_precipitation_probability_pct,
        "min_temperature": min_temperature,
    }
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data", [(0.0, 60, 5), (0.0, 60, 30), (0.0, 10, 5), (0.05, 5, 30)]
)
async def test_fugitive_dust(
    data: tuple[float, int, float],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, humidity_pct, wind_speed) = data
    applies = bool(multiplier)
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.fugitive_dust
    )
    world_data = generate_location_response(
        sources={"weather"}, humidity_pct=humidity_pct, wind_speed=wind_speed
    )
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )
    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.fugitive_dust
    assert site_condition.condition_value == {
        "humidity_pct": humidity_pct,
        "wind_speed": wind_speed,
    }
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
