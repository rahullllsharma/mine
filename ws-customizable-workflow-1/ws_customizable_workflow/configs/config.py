from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "local"
    MONGO_PROTOCOL: str = "mongodb"
    MONGO_HOST: str = "localhost"
    MONGO_USER: str = "root"
    MONGO_PASSWORD: str = "password"
    MONGO_DB: str = "asgard"
    MONGO_PORT: str = "27017"
    MAX_POOL_SIZE: int = 25
    APP_APM_ENABLED: bool = False
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    LIBS_LOG_LEVEL: str = "WARNING"
    LOG_DEV_CONSOLE: bool = False

    # HTTP client
    HTTP_TIMEOUT: float = 15.0
    # Number of max concurrent http connections
    HTTP_MAX_CONNECTIONS: int = 20
    # Number of max connections to keep from HTTP_MAX_CONNECTIONS
    HTTP_MAX_KEEPALIVE_CONNECTIONS: int = 2

    WORKER_SAFETY_SERVICE_REST_URL: str = "http://localhost:8000"
    WORKER_SAFETY_SERVICE_GQL_URL: str = "http://localhost:8001"
    AUDIT_TRAIL_URL: str = "http://localhost:7001"
    GS_BUCKET_NAME: str = "worker-safety-local-dev"
    GS_URL_EXPIRATION_MINUTES: int = 60 * 24
    GOOGLE_APPLICATION_CREDENTIALS: str = "/app/credentials.json"

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

    @property
    def mongo_dsn(self) -> str:
        if self.APP_ENV != "local":
            return f"{self.MONGO_PROTOCOL}://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}"
        else:
            return f"{self.MONGO_PROTOCOL}://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"

    @classmethod
    def get_settings(cls) -> "Settings":
        return Settings()
