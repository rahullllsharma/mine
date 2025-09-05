import pytest

from tests.integration.site_conditions.type_evaluator.helpers import (
    generate_location_response,
    get_library_site_condition,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.site_conditions import SiteConditionsEvaluator
from worker_safety_service.site_conditions.types import (
    LightningForecastEvent,
    SiteConditionHandleCode,
    WeatherAlertEventType,
)
from worker_safety_service.site_conditions.world_data import WeatherAlert


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "data",
    [
        # handles empty alert list
        (0.0, [], False),
        # ignores unkown events
        (
            0.0,
            [
                WeatherAlert(
                    event="unkown_event", event_type=WeatherAlertEventType.warning.value
                )
            ],
            False,
        ),
        # watch
        (
            0.05,
            [
                WeatherAlert(
                    event=LightningForecastEvent.severe_thunderstorm.value,
                    event_type=WeatherAlertEventType.watch.value,
                )
            ],
            True,
        ),
        (
            0.05,
            [
                WeatherAlert(
                    event=LightningForecastEvent.tornado.value,
                    event_type=WeatherAlertEventType.watch.value,
                )
            ],
            True,
        ),
        (
            0.05,
            [
                WeatherAlert(
                    event=LightningForecastEvent.hurricane.value,
                    event_type=WeatherAlertEventType.watch.value,
                )
            ],
            True,
        ),
        (
            0.05,
            [
                WeatherAlert(
                    event=LightningForecastEvent.tropical_storm.value,
                    event_type=WeatherAlertEventType.watch.value,
                )
            ],
            True,
        ),
        # warning
        (
            0.1,
            [
                WeatherAlert(
                    event=LightningForecastEvent.severe_thunderstorm.value,
                    event_type=WeatherAlertEventType.warning.value,
                )
            ],
            True,
        ),
        (
            0.1,
            [
                WeatherAlert(
                    event=LightningForecastEvent.tornado.value,
                    event_type=WeatherAlertEventType.warning.value,
                )
            ],
            True,
        ),
        (
            0.1,
            [
                WeatherAlert(
                    event=LightningForecastEvent.hurricane.value,
                    event_type=WeatherAlertEventType.warning.value,
                )
            ],
            True,
        ),
        (
            0.1,
            [
                WeatherAlert(
                    event=LightningForecastEvent.tropical_storm.value,
                    event_type=WeatherAlertEventType.warning.value,
                )
            ],
            True,
        ),
        # always return biggest multiplier
        (
            0.1,
            [
                WeatherAlert(
                    event=LightningForecastEvent.severe_thunderstorm.value,
                    event_type=WeatherAlertEventType.warning.value,
                ),
                WeatherAlert(
                    event=LightningForecastEvent.severe_thunderstorm.value,
                    event_type=WeatherAlertEventType.watch.value,
                ),
            ],
            True,
        ),
    ],
)
async def test_lightning_forecast(
    data: tuple[float, list[WeatherAlert], bool],
    db_session: AsyncSession,
    evaluator: SiteConditionsEvaluator,
) -> None:
    (multiplier, alerts, trigger_alert) = data
    applies = bool(multiplier)
    library_site_condition = await get_library_site_condition(
        db_session, SiteConditionHandleCode.lightning_forecast
    )
    world_data = generate_location_response(
        sources={"weatherAlerts"}, weather_alerts=alerts
    )
    world_data_dict = {0: world_data}
    response = await evaluator.evaluate_automatic_site_conditions(
        [library_site_condition], world_data_dict
    )

    assert len(response) == 1
    site_condition = response[0][1]
    assert site_condition.condition_name == SiteConditionHandleCode.lightning_forecast
    assert site_condition.condition_value == {"alerts": alerts}
    assert site_condition.condition_applies == applies
    assert site_condition.multiplier == multiplier
    assert site_condition.alert == trigger_alert
