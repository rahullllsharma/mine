import enum
import functools
import json
import uuid
from collections.abc import Callable
from datetime import date, datetime, timezone
from typing import Any, AsyncGenerator, Optional, Type

from fastapi.encoders import jsonable_encoder
from shapely.geometry import Point as ShapelyPoint
from shapely.geometry import Polygon as ShapelyPolygon
from shapely.wkb import dumps as shapely_wkb_dumps
from shapely.wkb import loads as shapely_wkb_loads
from sqlalchemy.dialects.postgresql import UUID as SqlUUID
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
from sqlalchemy.types import ARRAY, UserDefinedType
from sqlmodel import Column, Enum, Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from worker_safety_service.config import settings
from worker_safety_service.types import Point, Polygon


def get_server_settings() -> dict[str, str] | None:
    server_settings: dict[str, str] = {}
    if settings.POSTGRES_DISABLE_JIT:
        server_settings["jit"] = "off"
    if settings.POSTGRES_APPLICATION_NAME:
        server_settings["application_name"] = settings.POSTGRES_APPLICATION_NAME
    return server_settings or None


def dumps(d: Any) -> str:
    return json.dumps(d, default=jsonable_encoder)


def create_engine(dsn: str, poolclass: Type[Pool] | None = None) -> AsyncEngine:
    kwargs: dict[str, Any] = {}
    if poolclass:
        kwargs["poolclass"] = poolclass
    else:
        kwargs.update(
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_POOL_MAX_OVERFLOW,
        )

    if "asyncpg" in dsn.lower():
        server_settings = get_server_settings()
        if server_settings:
            kwargs["connect_args"] = {"server_settings": server_settings}

    return create_async_engine(dsn, **kwargs, json_serializer=dumps)


@functools.cache
def get_engine() -> AsyncEngine:
    return create_engine(settings.POSTGRES_DSN)


def create_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    # expire_on_commit=False
    #   So we don't need to refresh the model everytime we make a commit
    return sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@functools.cache
def get_sessionmaker() -> sessionmaker:
    return create_sessionmaker(get_engine())


def get_session() -> AsyncSession:
    session: AsyncSession = get_sessionmaker()()
    return session


async def with_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session() as session:
        yield session


def db_default_utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EnumValues(Enum):
    """This class allows to use Enum values instead of names on DB

    For python enum:

    ```
    @enum.unique
    class ProjectStatus(str, enum.Enum):
        PENDING = "pending"
        ACTIVE = "active"

    class ProjectBase(SQLModel):
        status: ProjectStatus = Field(sa_column=Column(EnumValues(ProjectStatus)))
    ```

    We store `pending` and `active` into the DB.
    And, we can still send the enum name to the client as:

    ```
    ProjectStatus = strawberry.enum(models.ProjectStatus)
    ```

    This make `Enum` as client to DB translation
    """

    def __init__(self, *enums: Type[enum.Enum], **kw: Any):
        kw["values_callable"] = lambda obj: [i.value for i in obj]
        super().__init__(*enums, **kw)


def start_date_before_end_date_validator(
    start_date: Optional[date], end_date: Optional[date]
) -> None:
    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date must be sooner than end date")


class PointColumn(UserDefinedType):
    cache_ok = False

    def get_col_spec(self) -> str:
        return "geometry('POINT')"

    def bind_processor(self, dialect: Any) -> Callable[[Any], str | None]:
        def process(value: Point | None) -> str | None:
            if value:
                geom_hex: str = shapely_wkb_dumps(
                    value, srid=settings.DEFAULT_SRID, hex=True
                )
                return geom_hex
            else:
                return None

        return process

    def result_processor(
        self, dialect: Any, coltype: Any
    ) -> Callable[[str | None], Point | None]:
        def process(value: str | None) -> Point | None:
            if value is not None:
                geom: ShapelyPoint = shapely_wkb_loads(value, hex=True)
                return Point(geom.x, geom.y)
            else:
                return None

        return process


class PolygonColumn(UserDefinedType):
    cache_ok = False

    def get_col_spec(self) -> str:
        return "geometry('POLYGON')"

    def bind_processor(self, dialect: Any) -> Callable[[Any], str | None]:
        def process(value: Polygon | None) -> str | None:
            if value:
                geom_hex: str = shapely_wkb_dumps(
                    value, srid=settings.DEFAULT_SRID, hex=True
                )
                return geom_hex
            else:
                return None

        return process

    def result_processor(
        self, dialect: Any, coltype: Any
    ) -> Callable[[str | None], Polygon | None]:
        def process(value: str | None) -> Polygon | None:
            if value is not None:
                geom: ShapelyPolygon = shapely_wkb_loads(value, hex=True)
                geom.__class__ = Polygon
                return geom  # type: ignore
            else:
                return None

        return process


class ClusteringModelBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, nullable=False)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id")
    zoom: int
    geom: Polygon = Field(
        sa_column=Column(PolygonColumn(), nullable=False),
    )
    geom_centroid: Point = Field(
        sa_column=Column(PointColumn(), nullable=False),
    )


class ClusteringObjectModelBase(SQLModel):
    class Config:
        arbitrary_types_allowed = True

    id: Any
    geom: Point
    clustering: list[Optional[uuid.UUID]] = Field(
        sa_column=Column(ARRAY(SqlUUID(as_uuid=True)), nullable=False)
    )
