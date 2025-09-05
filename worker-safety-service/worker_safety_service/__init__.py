import logging

import structlog

from worker_safety_service.config import settings
from worker_safety_service.urbint_logging import (
    DEFAULT_SHARED_PROCESSORS,
    configure_defaults,
    get_logger,
)

try:
    # Use color support for dev console logging if we have it!
    import colorama  # noqa: F401

    COLORS = True
except ImportError:
    COLORS = False


if settings.APP_APM_ENABLED:
    from ddtrace import config, patch_all

    config.version = settings.APP_VERSION
    patch_all()

dev_console_handler = None
if settings.LOG_DEV_CONSOLE:
    dev_console_handler = logging.StreamHandler()
    dev_console_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.dev.ConsoleRenderer(colors=COLORS),
            foreign_pre_chain=DEFAULT_SHARED_PROCESSORS,  # type: ignore
        )
    )

configure_defaults(
    level=logging.getLevelName(settings.LOG_LEVEL),
    extra_handler=dev_console_handler,
)

# Ignore some libs logs
logging.getLogger("faker.factory").setLevel(
    logging.getLevelName(settings.LIBS_LOG_LEVEL)
)

logger = get_logger(__name__)
logger.info("Logging configured.")
