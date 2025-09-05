from __future__ import annotations

import asyncio
import datetime
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any, Callable, Literal
from uuid import UUID

from httpx import HTTPError

from worker_safety_service import get_logger, models
from worker_safety_service.models.library import LibrarySiteCondition
from worker_safety_service.site_conditions.types import (
    AirQualityIndexCondition,
    AirQualityIndexData,
    BuildingDensityCondition,
    BuildingDensityData,
    CellCoverageCondition,
    CellCoverageData,
    ColdIndexData,
    ColdIndexSiteCondition,
    CrimeCondition,
    CrimeData,
    ExtremeTopographyCondition,
    ExtremeTopographyData,
    FugitiveDustData,
    FugitiveDustSiteCondition,
    HeatIndexData,
    HeatIndexSiteCondition,
    HighWindsData,
    HighWindsSiteCondition,
    LightningForecastCondition,
    LightningForecastData,
    LightningForecastEvent,
    MajorCarrier,
    MajorRoadwayClassification,
    PopulationDensityCondition,
    PopulationDensityData,
    RoadwayCondition,
    RoadwayData,
    SiteConditionResult,
    SlipData,
    SlipSiteCondition,
    WetOrFrozenGroundData,
    WetOrFrozenGroundSiteCondition,
)
from worker_safety_service.site_conditions.world_data import (
    AirQualityResponse,
    BuildingResponse,
    CellCoverageResponse,
    CrimeResponse,
    LocationRequestQuery,
    LocationResponse,
    PopulationResponse,
    RoadwayResponse,
    SlopeResponse,
    Sources,
    WeatherAlertResponse,
    WeatherDay,
    WorldDataClient,
)
from worker_safety_service.types import Point

if TYPE_CHECKING:
    from worker_safety_service.dal.library_site_conditions import (
        LibrarySiteConditionManager,
    )
    from worker_safety_service.dal.site_conditions import SiteConditionManager
    from worker_safety_service.dal.tasks import TaskManager
    from worker_safety_service.dal.work_packages import WorkPackageManager


SiteConditionHandler = Callable[
    [LibrarySiteCondition, dict[int, LocationResponse]], SiteConditionResult
]

logger = get_logger(__name__)

ONE_DAY = datetime.timedelta(days=1)

LOCATION_WORLD_DATA_SOURCES: set[str] = {
    sources.value for sources in Sources if sources != Sources.hospital
}

GenericLocationReponseSections = Literal[
    "airQuality",
    "crime",
    "roadway",
    "cellCoverage",
    "population",
    "building",
    "weatherAlerts",
    "slope",
]


class SectionNotFoundException(Exception):
    """Raised when a section is not found in the world data response."""

    def __init__(self, section_name: GenericLocationReponseSections) -> None:
        self.section_name = section_name
        super().__init__(f"Section {section_name} not found in world data response")


class SiteConditionsEvaluator:
    def __init__(
        self,
        work_package_manager: WorkPackageManager,
        site_conditions_manager: SiteConditionManager,
        task_manager: TaskManager,
        library_site_condition_manager: LibrarySiteConditionManager,
    ):
        self._work_package_manager = work_package_manager
        self._site_conditions_manager = site_conditions_manager
        self._task_manager = task_manager
        self._library_site_condition_manager = library_site_condition_manager

    # This method was originally used to get multipliers for site conditions
    # that applied to tasks.  That feature was never fully implemnted in that no
    # site conditions were ever linked to tasks, although this method was
    # created and at the time was doing what it was suposed to.  Sometime later,
    # this method was changed to return an empty list, presumably because the
    # actual nature of this feature had been lost to time.
    async def evaluate_project_location_task(
        self, task_id: UUID, date: datetime.date
    ) -> list[SiteConditionResult]:
        t = await self._task_manager.get_task(task_id)
        if not t:
            raise ValueError(f"Task {task_id} not found")
        library_task, task = t

        db_location = await self._work_package_manager.get_location(task.location_id)
        assert db_location

        # TODO: SERV-301 Check what's the correct implementation of this because the previous implementation was dead code.
        return []

    async def evaluate_location(
        self, location: models.Location, date: datetime.date
    ) -> list[tuple[LibrarySiteCondition, SiteConditionResult]]:
        """
        Evaluate all site conditions that apply to a location for a given date.

        Site conditions that have been manually added are always applied.

        The remaining site conditions apply given some criteria.

        We determine which criteria to check from the site condition's handle code
        """
        # Fetch all library site conditions and site conditions that have been
        # manually added to a location
        library_site_conditions, manually_added = await asyncio.gather(
            self._library_site_condition_manager.get_library_site_conditions(
                allow_archived=False
            ),
            self._site_conditions_manager.get_manually_added_site_conditions(
                location_ids=[location.id]
            ),
        )

        # Map manually added site condtions make sure the sets are distinct
        manually_added_lsc_map = {lsc.id: lsc for lsc, _ in manually_added}
        manually_added_site_condition_results = self.evaluate_manual_site_conditions(
            manually_added_lsc_map.values()
        )

        library_site_conditions_to_evaluate = [
            lsc
            for lsc in library_site_conditions
            if lsc.id not in manually_added_lsc_map
        ]

        world_data = await self.call_world_data(location.geom, date)
        site_conditions_to_set: list[
            tuple[LibrarySiteCondition, SiteConditionResult]
        ] = []

        if world_data is not None:
            automatic_site_condition_results = (
                await self.evaluate_automatic_site_conditions(
                    library_site_conditions_to_evaluate,
                    world_data,
                )
            )

            site_conditions_to_set = [
                (lsc, res)
                for lsc, res in automatic_site_condition_results
                if res.condition_applies
            ]

            await self._site_conditions_manager.set_evaluated_site_conditions(
                date=date,
                location=location,
                site_conditions=site_conditions_to_set,
            )

        return site_conditions_to_set + manually_added_site_condition_results

    def evaluate_manual_site_conditions(
        self,
        site_conditions: Iterable[LibrarySiteCondition],
    ) -> list[tuple[LibrarySiteCondition, SiteConditionResult]]:
        return [
            (lsc, TypesEvaluator.default_type_evaluator(lsc)) for lsc in site_conditions
        ]

    async def evaluate_automatic_site_conditions(
        self,
        site_conditions: Iterable[LibrarySiteCondition],
        world_data: dict[int, LocationResponse],
    ) -> list[tuple[LibrarySiteCondition, SiteConditionResult]]:
        results: list[tuple[LibrarySiteCondition, SiteConditionResult]] = []
        for site_condition in site_conditions:
            try:
                handler: SiteConditionHandler = getattr(
                    TypesEvaluator, site_condition.handle_code
                )
                result = handler(site_condition, world_data)
                results.append((site_condition, result))
            except AttributeError:
                # This is an expected error because not all site conditions have
                # evaluator functions
                logger.debug(
                    "No evaluator function found for site condition",
                    site_condition=site_condition,
                )
            except SectionNotFoundException as ex:
                # This exception is intentionally eaten because it's generally
                # not a problem if a section is not found
                logger.info(ex)

        return results

    async def call_world_data(
        self,
        point: Point,
        date: datetime.date,
    ) -> dict[int, LocationResponse] | None:
        queries: list[LocationRequestQuery] = [
            LocationRequestQuery(
                point=point, date=date, sources=LOCATION_WORLD_DATA_SOURCES
            )
        ]
        queries.append(
            LocationRequestQuery(point=point, date=date - ONE_DAY, sources={"weather"})
        )
        try:
            queries_data = await WorldDataClient.location_bulk(queries)
        except HTTPError as ex:
            logger.exception("Exception calling world data", ex=ex)
            queries_data = None

        return queries_data


def parse_weather_data(world_data: dict[int, LocationResponse]) -> WeatherDay:
    weather_data = world_data[0]["weather"]
    assert weather_data
    day_data = weather_data["day"]
    assert day_data
    return day_data


def parse_previous_weather_data(
    world_data: dict[int, LocationResponse]
) -> tuple[WeatherDay, WeatherDay]:
    weather_data = world_data[0]["weather"]
    assert weather_data
    day_data = weather_data["day"]
    assert day_data

    previous_data = world_data[1]
    assert previous_data
    previous_weather_data = previous_data["weather"]
    assert previous_weather_data
    previous_day_data = previous_weather_data["day"]

    return (day_data, previous_day_data)


def parse_generic_data(
    world_data: dict[int, LocationResponse],
    section_name: GenericLocationReponseSections,
) -> Any:
    section_data = world_data[0][section_name]
    if section_data is None:
        raise SectionNotFoundException(section_name)
    return section_data


class TypesEvaluator:
    @staticmethod
    def heat_index(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> HeatIndexSiteCondition:
        day = parse_weather_data(world_data)

        max_apparent_temperature = day["apparentTemperature"]["max"]
        assert max_apparent_temperature is not None

        multiplier = 0.0
        applies = max_apparent_temperature >= 91

        if applies:
            if max_apparent_temperature > 103:
                multiplier = site_condition.default_multiplier
            else:
                multiplier = 0.05

        return HeatIndexSiteCondition(
            condition_value=HeatIndexData(
                max_apparent_temperature=max_apparent_temperature
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def slip(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> SlipSiteCondition:
        day, previous_day = parse_previous_weather_data(world_data)

        # TODO what should happen if we don't precipitation data?
        precipitation = day["precipitation"]["probabilityPct"]
        previous_precipitation = previous_day["precipitation"]["probabilityPct"]
        assert precipitation is not None and previous_precipitation is not None

        applies = precipitation >= 80 or previous_precipitation >= 95
        multiplier = site_condition.default_multiplier if applies else 0.0
        return SlipSiteCondition(
            condition_value=SlipData(
                current_day_precipitation=precipitation,
                previous_day_precipitation=previous_precipitation,
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def cold_index(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> ColdIndexSiteCondition:
        day = parse_weather_data(world_data)
        min_temperature = day["temperature"]["min"]
        assert min_temperature is not None

        applies = min_temperature < 26
        multiplier = site_condition.default_multiplier if applies else 0.0

        return ColdIndexSiteCondition(
            condition_value=ColdIndexData(
                min_temperature=min_temperature,
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def wet_or_frozen_ground(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> WetOrFrozenGroundSiteCondition:
        day, previous_day = parse_previous_weather_data(world_data)

        precipitation = day["precipitation"]["probabilityPct"]
        previous_precipitation = previous_day["precipitation"]["probabilityPct"]
        assert precipitation is not None and previous_precipitation is not None
        min_temperature = day["temperature"]["min"]
        assert min_temperature is not None

        applies = (
            precipitation >= 80 or previous_precipitation >= 95
        ) and min_temperature <= 32

        multiplier = site_condition.default_multiplier if applies else 0.0

        return WetOrFrozenGroundSiteCondition(
            condition_value=WetOrFrozenGroundData(
                current_day_precipitation=precipitation,
                previous_day_precipitation=previous_precipitation,
                min_temperature=min_temperature,
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def high_winds(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> HighWindsSiteCondition:
        day = parse_weather_data(world_data)
        gust = day["wind"]["gust"]
        assert gust is not None

        applies = gust >= 30
        multiplier = 0.0
        if applies:
            if gust > 40:
                multiplier = site_condition.default_multiplier
            else:
                multiplier = 0.05

        return HighWindsSiteCondition(
            condition_value=HighWindsData(gust=gust),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def fugitive_dust(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> FugitiveDustSiteCondition:
        day = parse_weather_data(world_data)
        humidity_pct = day["humidityPct"]
        wind_speed = day["wind"]["speed"]
        assert humidity_pct is not None
        assert wind_speed is not None

        applies = humidity_pct < 50 and wind_speed > 12.0
        multiplier = site_condition.default_multiplier if applies else 0.0

        return FugitiveDustSiteCondition(
            condition_value=FugitiveDustData(
                humidity_pct=humidity_pct, wind_speed=wind_speed
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def air_quality_index(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> AirQualityIndexCondition:
        air_quality_response: AirQualityResponse = parse_generic_data(
            world_data, "airQuality"
        )

        aqi_value = air_quality_response["aqiValue"]

        applies = aqi_value > 150
        multiplier = site_condition.default_multiplier if applies else 0.0

        return AirQualityIndexCondition(
            condition_value=AirQualityIndexData(air_quality_index=aqi_value),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def crime(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> CrimeCondition:
        crime_response: CrimeResponse = parse_generic_data(world_data, "crime")

        total_index = crime_response["totalIndex"]

        applies = total_index >= 200
        multiplier = site_condition.default_multiplier if applies else 0.0

        return CrimeCondition(
            condition_value=CrimeData(total_index=total_index),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    # this one is wierd and can't use the default site condition modifier
    @staticmethod
    def roadway(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> RoadwayCondition:
        roadway_response: RoadwayResponse = parse_generic_data(world_data, "roadway")

        radius = roadway_response["radius"]
        classifications = roadway_response["classifications"]
        multiplier_matcher = {
            MajorRoadwayClassification.motorway: 0.1,
            MajorRoadwayClassification.motorway_link: 0.1,
            MajorRoadwayClassification.primary: 0.05,
            MajorRoadwayClassification.primary_link: 0.05,
            MajorRoadwayClassification.secondary: 0.05,
            MajorRoadwayClassification.secondary_link: 0.05,
            MajorRoadwayClassification.tertiary: 0.05,
            MajorRoadwayClassification.tertiary_link: 0.05,
            MajorRoadwayClassification.bus_stop: 0.05,
            MajorRoadwayClassification.busway: 0.05,
            MajorRoadwayClassification.trunk: 0.1,
            MajorRoadwayClassification.trunk_link: 0.1,
        }

        major_classifications = MajorRoadwayClassification.from_list(classifications)

        multiplier = max(
            [multiplier_matcher.get(c, 0.0) for c in major_classifications] or [0.0]
        )
        applies = bool(multiplier)

        return RoadwayCondition(
            condition_value=RoadwayData(
                radius=radius,
                classifications=classifications,
                major_classifications=list(major_classifications),
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def cell_coverage(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> CellCoverageCondition:
        cell_response: CellCoverageResponse = parse_generic_data(
            world_data, "cellCoverage"
        )

        carriers = cell_response["carriers"]

        multiplier = site_condition.default_multiplier
        applies = True
        present_major_carriers = MajorCarrier.from_list(carriers)

        if present_major_carriers:
            multiplier = 0.0
            applies = False

        return CellCoverageCondition(
            condition_value=CellCoverageData(
                carriers=carriers, major_carriers=list(present_major_carriers)
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def population_density(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> PopulationDensityCondition:
        population_response: PopulationResponse = parse_generic_data(
            world_data, "population"
        )

        density = population_response["density"]

        multiplier = 0.0
        if 2500 < density < 10000:
            multiplier = 0.05
        elif density >= 10000:
            multiplier = site_condition.default_multiplier

        applies = bool(multiplier)
        return PopulationDensityCondition(
            condition_value=PopulationDensityData(density=density),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def building_density(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> BuildingDensityCondition:
        building_response: BuildingResponse = parse_generic_data(world_data, "building")

        density_pct = building_response["densityPct"]

        applies = density_pct > 10
        multiplier = site_condition.default_multiplier if applies else 0.0

        return BuildingDensityCondition(
            condition_value=BuildingDensityData(density_pct=density_pct),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def lightning_forecast(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> LightningForecastCondition:
        weather_alert_response: WeatherAlertResponse = parse_generic_data(
            world_data, "weatherAlerts"
        )

        alerts = weather_alert_response["alerts"]

        LIGHTNING_FORCAST_EVENTS = {e.value for e in LightningForecastEvent}

        applies = False
        multiplier = 0.0

        if alerts:
            event_types = {
                alert["event_type"]
                for alert in alerts
                if alert["event"] in LIGHTNING_FORCAST_EVENTS
            }
            if "warning" in event_types:
                multiplier = site_condition.default_multiplier
            elif "watch" in event_types:
                multiplier = 0.05

        applies = bool(multiplier)
        return LightningForecastCondition(
            condition_value=LightningForecastData(
                alerts=alerts,
            ),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def extreme_topography(
        site_condition: LibrarySiteCondition,
        world_data: dict[int, LocationResponse],
    ) -> ExtremeTopographyCondition:
        slope_response: SlopeResponse = parse_generic_data(world_data, "slope")

        slope = slope_response["slope"]

        applies = slope >= 15.0
        multiplier = site_condition.default_multiplier if applies else 0.0

        return ExtremeTopographyCondition(
            condition_value=ExtremeTopographyData(slope=slope),
            condition_applies=applies,
            multiplier=multiplier,
            alert=applies,
        )

    @staticmethod
    def default_type_evaluator(
        library_site_condition: LibrarySiteCondition,
    ) -> SiteConditionResult:
        return SiteConditionResult(
            condition_name=library_site_condition.handle_code,
            condition_value=None,
            condition_applies=True,
            multiplier=library_site_condition.default_multiplier,
            alert=True,
        )
