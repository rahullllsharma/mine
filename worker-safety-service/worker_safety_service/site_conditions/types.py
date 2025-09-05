import dataclasses
import enum
from typing import Any, Type, TypedDict, TypeVar

T = TypeVar("T", bound="TypeEnum")


class TypeEnum(str, enum.Enum):
    @classmethod
    def from_list(cls: Type[T], str_list: list[str]) -> set[T]:
        return {cls(i) for i in set(str_list).intersection(set(cls))}


@enum.unique
class SiteConditionHandleCode(TypeEnum):
    slip = "slip"
    cold_index = "cold_index"
    heat_index = "heat_index"
    wet_or_frozen_ground = "wet_or_frozen_ground"
    high_winds = "high_winds"
    fugitive_dust = "fugitive_dust"
    air_quality_index = "air_quality_index"
    crime = "crime"
    roadway = "roadway"
    cell_coverage = "cell_coverage"
    population_density = "population_density"
    building_density = "building_density"
    lightning_forecast = "lightning_forecast"
    extreme_topography = "extreme_topography"


@enum.unique
class MajorRoadwayClassification(TypeEnum):
    motorway = "motorway"
    motorway_link = "motorway_link"
    primary = "primary"
    primary_link = "primary_link"
    secondary = "secondary"
    secondary_link = "secondary_link"
    tertiary = "tertiary"
    tertiary_link = "tertiary_link"
    bus_stop = "bus_stop"
    busway = "busway"
    trunk = "trunk"
    trunk_link = "trunk_link"


@enum.unique
class MajorCarrier(TypeEnum):
    att = "att"
    tmobile = "tmobile"
    uscc = "uscc"
    verizon = "verizon"


@enum.unique
class WeatherAlertEvent(TypeEnum):
    severe_thunderstorm = "severe_thunderstorm"
    tornado = "tornado"
    hurricane = "hurricane"
    tropical_storm = "tropical_storm"


@enum.unique
class WeatherAlertEventType(TypeEnum):
    warning = "warning"
    watch = "watch"


@enum.unique
class LightningForecastEvent(TypeEnum):
    severe_thunderstorm = WeatherAlertEvent.severe_thunderstorm.value
    tornado = WeatherAlertEvent.tornado.value
    hurricane = WeatherAlertEvent.hurricane.value
    tropical_storm = WeatherAlertEvent.tropical_storm.value


@dataclasses.dataclass
class SiteConditionResult:
    condition_value: Any
    condition_name: str
    condition_applies: bool = False
    multiplier: float = 0.0
    # TODO: "alert" means it should be displayed in UI/UX
    # Check for reference: https://urbint.atlassian.net/browse/WS-392
    alert: bool = False
    applies_to_project: bool = False
    applies_to_task: bool = False
    applies_to_project_location: bool = False


class HeatIndexData(TypedDict):
    max_apparent_temperature: float


@dataclasses.dataclass
class HeatIndexSiteCondition(SiteConditionResult):
    condition_value: HeatIndexData | None = None
    condition_name: str = SiteConditionHandleCode.heat_index.value
    applies_to_project: bool = True


class SlipData(TypedDict):
    current_day_precipitation: int
    previous_day_precipitation: int


@dataclasses.dataclass
class SlipSiteCondition(SiteConditionResult):
    condition_value: SlipData | None
    condition_name: str = SiteConditionHandleCode.slip.value
    applies_to_project: bool = True


class WetOrFrozenGroundData(TypedDict):
    current_day_precipitation: int
    previous_day_precipitation: int
    min_temperature: float


@dataclasses.dataclass
class WetOrFrozenGroundSiteCondition(SiteConditionResult):
    condition_value: WetOrFrozenGroundData | None
    condition_name: str = SiteConditionHandleCode.wet_or_frozen_ground.value
    applies_to_task: bool = True


class ColdIndexData(TypedDict):
    min_temperature: float


@dataclasses.dataclass
class ColdIndexSiteCondition(SiteConditionResult):
    condition_value: ColdIndexData | None
    condition_name: str = SiteConditionHandleCode.cold_index.value
    applies_to_project: bool = True
    applies_to_task: bool = True


class HighWindsData(TypedDict):
    gust: float


@dataclasses.dataclass
class HighWindsSiteCondition(SiteConditionResult):
    condition_value: HighWindsData | None
    condition_name: str = SiteConditionHandleCode.high_winds.value
    applies_to_task: bool = True


class FugitiveDustData(TypedDict):
    humidity_pct: int
    wind_speed: float


@dataclasses.dataclass
class FugitiveDustSiteCondition(SiteConditionResult):
    condition_value: FugitiveDustData | None
    condition_name: str = SiteConditionHandleCode.fugitive_dust.value
    applies_to_project_location: bool = True


class AirQualityIndexData(TypedDict):
    air_quality_index: int


@dataclasses.dataclass
class AirQualityIndexCondition(SiteConditionResult):
    condition_value: AirQualityIndexData | None
    condition_name: str = SiteConditionHandleCode.air_quality_index
    applies_to_project_location: bool = True


class CrimeData(TypedDict):
    total_index: int


@dataclasses.dataclass
class CrimeCondition(SiteConditionResult):
    condition_value: CrimeData | None
    condition_name: str = SiteConditionHandleCode.crime
    applies_to_project: bool = True


class RoadwayData(TypedDict):
    radius: int
    classifications: list[str]
    major_classifications: list[MajorRoadwayClassification]


@dataclasses.dataclass
class RoadwayCondition(SiteConditionResult):
    condition_value: RoadwayData | None
    condition_name: str = SiteConditionHandleCode.roadway
    applies_to_project_location: bool = True


class CellCoverageData(TypedDict):
    carriers: list[str]
    major_carriers: list[MajorCarrier]


@dataclasses.dataclass
class CellCoverageCondition(SiteConditionResult):
    condition_value: CellCoverageData | None
    condition_name: str = SiteConditionHandleCode.cell_coverage
    applies_to_project_location: bool = True


class PopulationDensityData(TypedDict):
    density: int


@dataclasses.dataclass
class PopulationDensityCondition(SiteConditionResult):
    condition_value: PopulationDensityData | None
    condition_name: str = SiteConditionHandleCode.population_density
    applies_to_project_location: bool = True


class BuildingDensityData(TypedDict):
    density_pct: int


@dataclasses.dataclass
class BuildingDensityCondition(SiteConditionResult):
    condition_value: BuildingDensityData | None
    condition_name: str = SiteConditionHandleCode.building_density
    applies_to_project_location: bool = True


class WeatherAlertData(TypedDict):
    event: str
    event_type: str


class LightningForecastData(TypedDict):
    alerts: list[WeatherAlertData]


class ExtremeTopographyData(TypedDict):
    slope: float


@dataclasses.dataclass
class ExtremeTopographyCondition(SiteConditionResult):
    condition_value: ExtremeTopographyData | None
    condition_name: str = SiteConditionHandleCode.extreme_topography
    applies_to_project_location: bool = True


@dataclasses.dataclass
class LightningForecastCondition(SiteConditionResult):
    condition_value: LightningForecastData | None
    condition_name: str = SiteConditionHandleCode.lightning_forecast
    applies_to_project_location: bool = True
