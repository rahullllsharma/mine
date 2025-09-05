import os


class Settings:
    APP_VERSION: str | None = os.environ.get("APP_VERSION") or None
    APP_COMMIT_SHA: str | None = os.environ.get("APP_COMMIT_SHA") or None
