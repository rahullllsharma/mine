import enum
import math
from decimal import Decimal
from typing import Any, Callable, TypedDict

from fastapi.encoders import ENCODERS_BY_TYPE
from pydantic import BaseModel
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon


@enum.unique
class OrderByDirection(enum.Enum):
    ASC = "asc"
    DESC = "desc"


class OrderBy(BaseModel):
    field: str
    direction: OrderByDirection
    # callable typing: [[statement, column, direction], statement]
    # matching worker_safety_service.models.__init__.py::set_column_order_by
    custom_order_by: Callable[[Any, Any, OrderByDirection], Any] | None = None


@enum.unique
class DefaultOrderByField(enum.Enum):
    ID = "id"
    NAME = "name"


@enum.unique
class LocationOrderByField(enum.Enum):
    LOCATION_NAME = "location_name"


@enum.unique
class DailyReportOrderByField(enum.Enum):
    COMPLETED_AT = "completed_at"


class FormListOrderByField(enum.Enum):
    ID = "id"
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


@enum.unique
class LibraryTaskOrderByField(enum.Enum):
    ID = "id"
    NAME = "name"
    CATEGORY = "category"


@enum.unique
class TaskOrderByField(enum.Enum):
    ID = "id"
    NAME = "name"  # same as LibraryTaskOrderByField
    CATEGORY = "category"  # same as LibraryTaskOrderByField
    START_DATE = "start_date"
    END_DATE = "end_date"
    STATUS = "status"
    PROJECT_NAME = "project_name"
    PROJECT_LOCATION_NAME = "project_location_name"


@enum.unique
class ProjectOrderByField(enum.Enum):
    ID = "id"
    NAME = "name"
    RISK_LEVEL = "risk_level"


@enum.unique
class ProjectLocationOrderByField(enum.Enum):
    ID = "id"
    NAME = "name"
    RISK_LEVEL = "risk_level"


@enum.unique
class LocationFilterByField(enum.Enum):
    RISK = "risk"
    REGIONS = "library_region_id"
    DIVISIONS = "library_division_id"
    TYPES = "library_project_type_id"
    WORK_TYPES = "work_type_id"
    PROJECT = "project"
    PROJECT_STATUS = "status"
    CONTRACTOR = "contractor_id"
    # Filter on supervisor_id and additional_supervisor_ids
    SUPERVISOR = "supervisor"


class JSONPoint(TypedDict):
    longitude: str
    latitude: str


class Point(ShapelyPoint):
    x: float
    y: float

    @property
    def longitude(self) -> float:
        return self.x

    @property
    def decimal_longitude(self) -> Decimal:
        return Decimal(str(self.longitude))

    @property
    def latitude(self) -> float:
        return self.y

    @property
    def decimal_latitude(self) -> Decimal:
        return Decimal(str(self.latitude))

    def __hash__(self) -> int:
        return hash((self.x, self.y))

    def __repr__(self) -> str:
        return f"Point({self.longitude}, {self.latitude})"

    def for_json(self) -> JSONPoint:
        return JSONPoint(longitude=str(self.longitude), latitude=str(self.latitude))

    def to_tile_bbox(self, zoom: int) -> tuple[int, int, int]:
        sin = math.sin(self.latitude * math.pi / 180)
        z2 = math.pow(2, zoom)
        x = z2 * (self.longitude / 360 + 0.5)

        if sin == 1.0:
            y = 0.0
        else:
            if sin == -1.0:
                sin = -0.9999999999999999
            y = z2 * (0.5 - 0.25 * math.log((1 + sin) / (1 - sin)) / math.pi)

        x = x % z2
        if x < 0:
            x += z2

        return zoom, int(x), int(y)


class Polygon(ShapelyPolygon):
    def __hash__(self) -> int:
        return hash(tuple(self.exterior.coords))


# Make pydantic/fastapi convert Point to dict
ENCODERS_BY_TYPE[Point] = Point.for_json
