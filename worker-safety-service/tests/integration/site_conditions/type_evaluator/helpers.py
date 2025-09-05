from datetime import date as DATE

from sqlmodel import select

from tests.factories import LibrarySiteConditionFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.library import LibrarySiteCondition
from worker_safety_service.site_conditions import LOCATION_WORLD_DATA_SOURCES
from worker_safety_service.site_conditions.types import SiteConditionHandleCode
from worker_safety_service.site_conditions.world_data import (
    AirQualityResponse,
    BuildingResponse,
    CellCoverageResponse,
    CrimeResponse,
    DayWeatherTemperature,
    LocationResponse,
    PopulationResponse,
    Precipitation,
    RoadwayResponse,
    SlopeResponse,
    WeatherAlert,
    WeatherAlertResponse,
    WeatherDay,
    WeatherResponse,
    Wind,
)
from worker_safety_service.types import Point

LOCATION = Point(-113.4944, 38.5816)


async def get_library_site_condition(
    db_session: AsyncSession, condition_type: SiteConditionHandleCode
) -> LibrarySiteCondition:
    condition: LibrarySiteCondition | None = (
        await db_session.exec(
            select(LibrarySiteCondition).where(
                LibrarySiteCondition.handle_code == condition_type.value
            )
        )
    ).first()
    if condition is None:
        condition = await LibrarySiteConditionFactory.persist(
            db_session, handle_code=condition_type.value
        )
    return condition


def generate_location_response(
    sources: set[str],
    min_temperature: float = 50.1,
    max_temperature: float = 60.1,
    min_apparent_temperature: float = 51.1,
    max_apparent_temperature: float = 60.1,
    gust: float = 30.1,
    wind_speed: float = 4.3,
    precipitation_probability_pct: int = 80,
    humidity_pct: int = 53,
    aqi_value: int = 100,
    crime_total_index: int = 100,
    roadway_radius: int = 100,
    roadway_classifications: list[str] = [],
    carriers: list[str] = [],
    population_density: int = 0,
    building_density_pct: int = 0,
    weather_alerts: list[WeatherAlert] = [],
    slope: float = 0.0,
) -> LocationResponse:
    response = LocationResponse(
        weather=None,
        airQuality=None,
        crime=None,
        roadway=None,
        cellCoverage=None,
        population=None,
        building=None,
        weatherAlerts=None,
        slope=None,
        hospital=None,
    )

    if "weather" in sources:
        response["weather"] = WeatherResponse(
            day=WeatherDay(
                humidityPct=humidity_pct,
                temperature=DayWeatherTemperature(
                    min=min_temperature, max=max_temperature
                ),
                apparentTemperature=DayWeatherTemperature(
                    min=min_apparent_temperature, max=max_apparent_temperature
                ),
                wind=Wind(gust=gust, speed=wind_speed),
                precipitation=Precipitation(
                    probabilityPct=precipitation_probability_pct
                ),
            )
        )

    if "airQuality" in sources:
        response["airQuality"] = AirQualityResponse(aqiValue=aqi_value)

    if "crime" in sources:
        response["crime"] = CrimeResponse(totalIndex=crime_total_index)

    if "roadway" in sources:
        response["roadway"] = RoadwayResponse(
            radius=roadway_radius, classifications=roadway_classifications
        )

    if "cellCoverage" in sources:
        response["cellCoverage"] = CellCoverageResponse(carriers=carriers)

    if "population" in sources:
        response["population"] = PopulationResponse(density=population_density)

    if "building" in sources:
        response["building"] = BuildingResponse(densityPct=building_density_pct)

    if "weatherAlerts" in sources:
        response["weatherAlerts"] = WeatherAlertResponse(alerts=weather_alerts)

    if "slope" in sources:
        response["slope"] = SlopeResponse(slope=slope)

    return response


# triggers 5 automatic site conditions
# 1. high heat
# 2. slip
# 3. cell coverage
# 4. wet or frozen ground
# 5. high winds
def call_world_data_side_effect(
    point: Point,
    date: DATE,
) -> dict[int, LocationResponse]:
    todays_query = generate_location_response(
        sources=LOCATION_WORLD_DATA_SOURCES,
        min_temperature=30.7,
        max_apparent_temperature=99.9,
        precipitation_probability_pct=0,
    )

    tomorrows_query = generate_location_response(
        sources={"weather"},
        precipitation_probability_pct=96,
    )

    return {
        0: todays_query,
        1: tomorrows_query,
    }
