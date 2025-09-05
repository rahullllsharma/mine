import dataclasses
import datetime
import enum
import json
from decimal import Decimal
from typing import Any, Type, TypedDict, TypeVar, Union

from httpx import AsyncClient, Limits

from worker_safety_service.config import settings
from worker_safety_service.types import Point
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.urbint_logging.fastapi_utils import Stats, get_correlation_id

logger = get_logger(__name__)

HTTPClient = AsyncClient(
    timeout=settings.HTTP_TIMEOUT,
    limits=Limits(
        max_connections=settings.HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
    ),
)


async def shutdown_http_client() -> None:
    await HTTPClient.aclose()


@enum.unique
class Sources(enum.Enum):
    traffic = "traffic"
    weather = "weather"
    roadway = "roadway"
    crime = "crime"
    population = "population"
    building = "building"
    cellCoverage = "cellCoverage"
    airQuality = "airQuality"
    weatherAlerts = "weatherAlerts"
    elevation = "elevation"
    slope = "slope"
    hospital = "hospital"


class WorldDataClient:
    @classmethod
    async def location_bulk(
        cls,
        queries: list["LocationRequestQuery"],
    ) -> dict[int, "LocationResponse"]:
        """This returns the requested queries as `dict[query.index, LocationResponse]`

        Example:
        ```
        query1 = LocationRequestQuery(...)
        query2 = LocationRequestQuery(...)
        data = WorldDataClient.location_bulk([query1, query2])

        # Data is returned with query index as dict key
        query1_data = data[0]
        query2_data = data[1]
        ```
        """

        request_queries = [
            {
                "lat": str(query.point.latitude),
                "lon": str(query.point.longitude),
                # Set for noon because we need day weather (avoid timezone issues)
                "datetime": query.date.strftime("%Y-%m-%dT12:00:00Z"),
                "roadwayRadius": 100,
                "sources": list(query.sources),
            }
            for query in queries
        ]

        headers = {"Content-Type": "application/json"}
        url = f"{settings.WORLD_DATA_BASE_URL}/location/bulk"
        bulk_data: "LocationBulkResponse" = await cls._post_request(
            url,
            content=json.dumps(request_queries).encode(),
            headers=headers,
        )

        errors = bulk_data.get("errors")
        if errors:
            message = "World-data request with errors"
            logger.error(
                message,
                errors=errors,
                queries=request_queries,
            )
            raise ValueError(message)

        data: dict[int, "LocationResponse"] = dict(bulk_data["data"])
        return data

    @classmethod
    async def request_resource(
        cls, lat: Decimal, lon: Decimal, source: Sources, response_type: Type["T"]
    ) -> "T":
        with Stats("world-data"):
            params = {"lat": str(lat), "lon": str(lon)}
            response = await HTTPClient.get(
                f"{settings.WORLD_DATA_BASE_URL}/{source.value}", params=params
            )
            response.raise_for_status()

            content = json.loads(response.content)

        errors = content.get("errors")
        if errors:
            message = "World-data source request with errors"
            logger.error(
                message,
                errors=errors,
                source=source.value,
            )
            raise ValueError(message)

        data: T = content["data"]

        return data

    @staticmethod
    async def _post_request(
        url: str, content: bytes, headers: dict[str, Any] | None = None
    ) -> Any:
        headers = headers or {}
        headers["X-Correlation-ID"] = get_correlation_id()
        if settings.WORLD_DATA_TOKEN:
            headers["Authorization"] = settings.WORLD_DATA_TOKEN

        with Stats("world-data"):
            response = await HTTPClient.post(url, content=content, headers=headers)
            response.raise_for_status()
            return json.loads(response.content)


@dataclasses.dataclass
class LocationRequestQuery:
    point: Point
    date: datetime.date
    sources: set[str]


class Wind(TypedDict):
    gust: float | None
    speed: float | None


class Precipitation(TypedDict):
    probabilityPct: int | None


class DayWeatherTemperature(TypedDict):
    min: float | None
    max: float | None


class WeatherDay(TypedDict):
    humidityPct: int | None
    temperature: DayWeatherTemperature
    apparentTemperature: DayWeatherTemperature
    wind: Wind
    precipitation: Precipitation


class WeatherResponse(TypedDict):
    day: WeatherDay


class AirQualityResponse(TypedDict):
    aqiValue: int


class CrimeResponse(TypedDict):
    totalIndex: int


class RoadwayResponse(TypedDict):
    radius: int
    classifications: list[str]


class CellCoverageResponse(TypedDict):
    carriers: list[str]


class PopulationResponse(TypedDict):
    density: int


class BuildingResponse(TypedDict):
    densityPct: int


class WeatherAlert(TypedDict):
    event: str
    event_type: str


class WeatherAlertResponse(TypedDict):
    alerts: list[WeatherAlert]


class SlopeResponse(TypedDict):
    slope: float


class HospitalData(TypedDict):
    name: str
    trauma: str
    helipad: str
    beds: int
    distance: float
    telephone: str
    address: str
    city: str
    state: str
    zip: str


class HospitalsResponse(TypedDict):
    hospitals: list[HospitalData]


class LocationResponse(TypedDict):
    # Keys would be missing if no data for the source
    weather: WeatherResponse | None
    airQuality: AirQualityResponse | None
    crime: CrimeResponse | None
    roadway: RoadwayResponse | None
    cellCoverage: CellCoverageResponse | None
    population: PopulationResponse | None
    building: BuildingResponse | None
    weatherAlerts: WeatherAlertResponse | None
    slope: SlopeResponse | None
    hospital: HospitalsResponse | None


class ErrorResponse(TypedDict):
    status: int
    code: str
    detail: str
    meta: dict[str, Any]


class LocationBulkResponse(TypedDict):
    data: list[tuple[int, LocationResponse]]
    errors: list[ErrorResponse] | None


SourceResponseUnion = Union[
    WeatherResponse,
    AirQualityResponse,
    CrimeResponse,
    RoadwayResponse,
    CellCoverageResponse,
    PopulationResponse,
    BuildingResponse,
    WeatherAlertResponse,
    SlopeResponse,
    HospitalsResponse,
]


T = TypeVar("T", bound=SourceResponseUnion)
