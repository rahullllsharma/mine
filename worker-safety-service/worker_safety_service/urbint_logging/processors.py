from typing import Any

from .config import Settings


def inject_app_version(_: Any, __: Any, event_dict: dict) -> dict:
    """Inject App version info from environment."""
    if Settings.APP_VERSION:
        event_dict["app_version"] = Settings.APP_VERSION
    if Settings.APP_COMMIT_SHA:
        event_dict["app_commit_sha"] = Settings.APP_COMMIT_SHA
    return event_dict


def rename_message_key(_: Any, __: Any, event_dict: dict) -> dict:
    """Rename log text key from `event` to `message`.

    This makes structlog's output match other structured JSON loggers' defaults."""
    # See: https://github.com/hynek/structlog/issues/35#issuecomment-591321744
    event_dict["message"] = event_dict.pop("event")
    return event_dict
