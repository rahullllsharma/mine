import decimal
import os
from datetime import timedelta
from typing import Any, List, Optional

import tomli
from fastapi.encoders import ENCODERS_BY_TYPE
from pydantic import AnyHttpUrl, BaseSettings
from strawberry.schema.types.base_scalars import Decimal

from worker_safety_service.urbint_logging.config import Settings as log_settings
from worker_safety_service.utils import decimal_to_string

HERE = os.path.abspath(os.path.dirname(__file__))
PYPROJECT_PATH = os.path.abspath(os.path.join(HERE, "..", "pyproject.toml"))


class Settings(BaseSettings):
    CORS_ORIGINS: List[AnyHttpUrl] = []
    CORS_ORIGIN_REGEX: str | None = None
    API_VERSION: str = "1.0.0"
    APP_APM_ENABLED: bool = False
    APP_ENV: str = "local"
    APP_VERSION: str = "unknown"  # Defined by pyproject.toml
    APP_COMMIT_SHA: str = "unknown"
    LOG_LEVEL: str = "INFO"
    LIBS_LOG_LEVEL: str = "WARNING"
    LOG_DEV_CONSOLE: bool = False
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_DSN: str = ""
    POSTGRES_POOL_SIZE: int = 25
    POSTGRES_POOL_MAX_OVERFLOW: int = 10
    POSTGRES_APPLICATION_NAME: str | None = None
    # If a docker postgres is being used, set it to True
    # It should speed up asyncpg driver usage, more details on https://github.com/MagicStack/asyncpg/issues/530
    POSTGRES_DISABLE_JIT: bool = False

    WORKER_SAFETY_SERVICE_URL: str = "http://localhost:8000"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8002"
    KEYCLOAK_BASE_URL: str = "http://localhost:8080"
    KEYCLOAK_REALM: str = "asgard"

    # Time (seconds) we cache (in memory) keycloak signing keys
    KEYCLOAK_CACHE_EXPIRE: int = 24 * 60 * 60
    WORLD_DATA_BASE_URL: str = "https://world-data.urbinternal.com"
    WORLD_DATA_TOKEN: str | None = None

    # audit trail service

    AUDIT_TRAIL_URL: str = "http://localhost:7001"

    # google cloud storage
    # FIREBASE_APP_CREDENTIALS: str = ".firebase-dev-service-account.json"
    GS_BUCKET_NAME: str = "worker-safety-local-dev"
    GS_PROJECT_ID: str = "urbint-1259"
    GS_URL_EXPIRATION_MINUTES: int = 60 * 24
    GS_UPLOAD_EXPIRATION_MINUTES: int = 10
    GS_URL_EXPIRATION: timedelta = timedelta(minutes=60 * 24)
    GS_UPLOAD_EXPIRATION: timedelta = timedelta(minutes=10)

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_CA_CERTS: Optional[str] = None
    REDIS_KEYFILE: Optional[str] = None
    REDIS_CERTFILE: Optional[str] = None
    REDIS_DB: str = "0"
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_MAX_RETRIES: int = 5
    REDIS_BACKOFF_BASE: float = 0.100

    # HTTP client
    HTTP_TIMEOUT: float = 15.0
    # Number of max concurrent http connections
    HTTP_MAX_CONNECTIONS: int = 20
    # Number of max connections to keep from HTTP_MAX_CONNECTIONS
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 2

    # We compress responses using gzip, brotli and deflate
    # This defines the minimun size to do it
    COMPRESS_MIN_SIZE: int = 500

    # Default SRID we use to add/edit geom columns
    DEFAULT_SRID: int = 4326
    MAPBOX_SRID: int = 3857

    GRAPHQL_MAX_QUERY_DEPTH: int = 25

    # TODO: Change this INTO a test specific config.
    PRISM_BASE_URL: str = "http://localhost:8010"

    LAUNCH_DARKLY_SDK_KEY: str = ""
    LAUNCH_DARKLY_MOBILE_KEY: str = ""

    REPORTS_JWT_HASH_KEY: str = "wzPkf0m1cEZadQ19KCdh-Fpula0wgnbD8tKim3TeRoc"  # This is the Hash key used to sign JWT token for reports API
    REPORTS_HASH_ALGO: str = (
        "HS256"  # this is the algo to be used to sign JWT token for reports API
    )
    REPORTS_JWT_LIFESPAN_DAYS = 180  # This is number of days the JWT token will be valid for Reports API from time of generation

    WORKOS_BASE_URL: str = "https://api.workos.com"

    WORKOS_AUTHORIZATION_TOKEN: str = ""

    REST_API_WRAPPER_READ_TIMEOUT: float = 120.0

    class Config:
        case_sensitive = True

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super(Settings, self).__init__(*args, **kwargs)
        self.POSTGRES_DSN = self.build_db_dsn()

        self.GS_URL_EXPIRATION: timedelta = timedelta(
            minutes=self.GS_URL_EXPIRATION_MINUTES
        )
        self.GS_UPLOAD_EXPIRATION: timedelta = timedelta(
            minutes=self.GS_UPLOAD_EXPIRATION_MINUTES
        )

        # Find version
        with open(PYPROJECT_PATH, "rb") as fp:
            self.APP_VERSION = tomli.load(fp)["tool"]["poetry"]["version"]

        # Define logging settings
        log_settings.APP_VERSION = self.APP_VERSION
        log_settings.APP_COMMIT_SHA = self.APP_COMMIT_SHA

    def build_db_dsn(
        self, *, protocol: str = "postgresql+asyncpg", db: str | None = None
    ) -> str:
        return f"{protocol}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db or self.POSTGRES_DB}"


settings = Settings()

# Make pydantic/fastapi convert decimal to str instead of float/int
# This way we have pydantic/fastapi working the same way as strawberry/graphql, and:
#   - Keep decimal as string to avoid precision issues
#   - Remove trailing 0
ENCODERS_BY_TYPE[decimal.Decimal] = decimal_to_string
Decimal._scalar_definition.serialize = decimal_to_string  # type: ignore
