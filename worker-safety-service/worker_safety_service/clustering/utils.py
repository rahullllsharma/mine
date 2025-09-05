import math
import uuid
from collections import defaultdict
from collections.abc import Callable, Iterable
from functools import wraps
from typing import Any, TypeAlias

from shapely.geometry import CAP_STYLE
from shapely.geometry import Point as ShapelyPoint
from shapely.wkb import loads as shapely_wkb_loads

try:
    import google.protobuf.descriptor

    google.protobuf.descriptor._Deprecated.count = 0
except:  # noqa: E722
    pass

from worker_safety_service.clustering import vector_tile_p3_pb2
from worker_safety_service.models.utils import (
    ClusteringModelBase,
    ClusteringObjectModelBase,
)
from worker_safety_service.types import Point, Polygon
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

X_Coordinate: TypeAlias = int
Y_Coordinate: TypeAlias = int
Coordinates: TypeAlias = tuple[X_Coordinate, Y_Coordinate]


class SphericalMercator:
    @classmethod
    def buffer(cls, point: Point, zoom: int, radius: int) -> Polygon:
        buffer_radius = radius / (512 * math.pow(2, zoom))
        polygon = Point(
            cls.lng_to_x(point.longitude), cls.lat_to_y(point.latitude)
        ).buffer(buffer_radius, cap_style=CAP_STYLE.square)
        return Polygon(
            [
                (cls.x_to_lng(longitude), cls.y_to_lat(latitude))
                for longitude, latitude in polygon.exterior.coords
            ]
        )

    @staticmethod
    def lng_to_x(lng: float) -> float:
        return lng / 360 + 0.5

    @staticmethod
    def lat_to_y(lat: float) -> float:
        sin = math.sin(lat * math.pi / 180)
        if sin == -1:
            return 1.0
        elif sin == 1:
            return 0.0
        else:
            y = 0.5 - 0.25 * math.log((1 + sin) / (1 - sin)) / math.pi
            if y < 0:
                return 0.0
            elif y > 1:
                return 1.0
            else:
                return y

    @staticmethod
    def x_to_lng(x: float) -> float:
        return (x - 0.5) * 360

    @staticmethod
    def y_to_lat(y: float) -> float:
        y2 = (180 - y * 360) * math.pi / 180
        return 360 * math.atan(math.exp(y2)) / math.pi - 90


def point_hex_to_tile(geom_hex: str) -> Coordinates:
    point: ShapelyPoint = shapely_wkb_loads(geom_hex, hex=True)
    return (tile_zigzag(int(point.x)), tile_zigzag(int(point.y)))


def tile_zigzag(delta: int) -> int:
    return (delta << 1) ^ (delta >> 31)


class BuildTile:
    def __init__(self, name: str) -> None:
        self.values_indexes: dict[Any, int] = {}

        self.tile = vector_tile_p3_pb2.tile()

        self.layer = self.tile.layers.add()
        self.layer.name = name
        self.layer.version = 1
        self.layer.extent = 4096  # Default on DB function ST_AsMVTGeom

    def add_keys(self, *keys: str) -> None:
        self.layer.keys.extend(keys)

    def get_index(self, value: Any, value_type: str = "string") -> int:
        index = self.values_indexes.get(value)
        if index is None:
            layer_value = self.layer.values.add()
            setattr(layer_value, f"{value_type}_value", value)
            self.values_indexes[value] = index = len(self.values_indexes)
        return index

    def get_int_index(self, value: Any) -> int:
        return self.get_index(value, "int")

    def add_point(self, tile_geom: tuple[int, int]) -> Any:
        feature = self.layer.features.add()
        feature.type = self.tile.Point
        feature.geometry.extend((9, *tile_geom))
        return feature

    def add_hex_point(self, hex_geom: str) -> Any:
        return self.add_point(point_hex_to_tile(hex_geom))

    def build(self) -> bytes:
        binary: bytes = self.tile.SerializeToString()
        return binary


class NewClustering:
    def __init__(self, max_zoom: int) -> None:
        self.max_zoom = max_zoom
        self.clusters: dict[uuid.UUID, ClusteringModelBase] = {}
        self.geoms: dict[Any, Point] = {}
        self.data: dict[Any, list[uuid.UUID | None]] = {}

    def add_models(self, models: Iterable[ClusteringObjectModelBase]) -> None:
        for model in models:
            self.data[model.id] = [None] * (self.max_zoom + 1)
            self.geoms[model.id] = model.geom

    def set_cluster(
        self, cluster: ClusteringModelBase, model_ids: Iterable[Any]
    ) -> None:
        self.clusters[cluster.id] = cluster
        for model_id in model_ids:
            self.data[model_id][cluster.zoom] = cluster.id

    def find(self, zoom: int, model_id: Any) -> ClusteringModelBase | None:
        cluster_id = self.data[model_id][zoom]
        if cluster_id:
            return self.clusters[cluster_id]
        return None

    def matching(
        self, cluster: ClusteringModelBase, model_ids: Iterable[Any]
    ) -> list[Any]:
        return [
            model_id
            for model_id in model_ids
            if self.data[model_id][cluster.zoom] == cluster.id
        ]

    def intersects(
        self, zoom: int, geom_buffer: Polygon, model_ids: Iterable[Any]
    ) -> list[Any]:
        return [
            model_id
            for model_id in model_ids
            if (
                # It should intersect but be without a cluster already defined
                not self.data[model_id][zoom]
                and geom_buffer.intersects(self.geoms[model_id])
            )
        ]

    def get(self, model_id: Any) -> list[uuid.UUID | None]:
        return self.data[model_id]

    def get_geom(self, model_id: Any) -> Point:
        return self.geoms[model_id]

    def all_ids(self) -> set[Any]:
        return set(self.data.keys())

    def with_items(self) -> bool:
        return bool(self.data)

    @staticmethod
    def build_buffer(zoom: int, geom: Point, radius: int) -> Polygon:
        return SphericalMercator.buffer(geom, zoom, radius)

    def get_buffer(
        self, radius: int, zoom: int, model_id: Any, cluster: ClusteringModelBase | None
    ) -> tuple[Point, Polygon]:
        if cluster:
            return cluster.geom_centroid, cluster.geom
        else:
            geom_centroid = self.geoms[model_id]
            geom_buffer = self.build_buffer(zoom, geom_centroid, radius)
            return geom_centroid, geom_buffer


class PostponeClustering:
    def __init__(self) -> None:
        self.clusters: defaultdict[int, list[uuid.UUID]] = defaultdict(list)
        self.items: defaultdict[int, list[Any]] = defaultdict(list)
        self.items_geom: dict[Any, Point] = {}

    def add_cluster(self, cluster: ClusteringModelBase) -> None:
        self.clusters[cluster.zoom].append(cluster.id)

    def add_model_without_cluster(
        self, zoom: int, model_id: Any, model_geom: Point
    ) -> None:
        self.items[zoom].append(model_id)
        self.items_geom[model_id] = model_geom

    def build_values(self, radius: int) -> list[tuple[int, Any, Polygon]]:
        return [
            (
                zoom,
                model_id,
                SphericalMercator.buffer(self.items_geom[model_id], zoom, radius),
            )
            for zoom, model_ids in self.items.items()
            for model_id in model_ids
        ]


def ignore_errors(func: Callable) -> Any:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any | None:
        try:
            return await func(*args, **kwargs)
        except:  # noqa: E722
            logger.exception(
                "Failed to calculate clustering, please run 'clustering check-empty' and 'check-clusters' CLI",
                func_name=func.__name__,
                func_args=str(list(args)),
                func_kwargs=str(list(kwargs)),
            )
            return None

    return wrapper
