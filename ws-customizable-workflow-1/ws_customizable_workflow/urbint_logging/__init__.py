import logging
import os
from typing import Any

import structlog

from .processors import inject_app_version, rename_message_key

# Use StdLib logging levels: https://docs.python.org/3/library/logging.html#logging-levels
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

DEFAULT_JSON_RENDERER = structlog.processors.JSONRenderer()
DEFAULT_SHARED_PROCESSORS = [
    structlog.contextvars.merge_contextvars,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.stdlib.PositionalArgumentsFormatter(),
    structlog.processors.StackInfoRenderer(),
    structlog.processors.format_exc_info,
    structlog.processors.UnicodeDecoder(),
    inject_app_version,
    rename_message_key,
]
DEFAULT_PROCESSORS: list = [structlog.stdlib.filter_by_level]
DEFAULT_PROCESSORS.extend(DEFAULT_SHARED_PROCESSORS)
DEFAULT_PROCESSORS.append(structlog.stdlib.ProcessorFormatter.wrap_for_formatter)
DEFAULT_LOGGER_FACTORY = structlog.stdlib.LoggerFactory()
DEFAULT_WRAPPER_CLASS = structlog.stdlib.BoundLogger
DEFAULT_CACHE_LOGGER_ON_FIRST_USE = True

TRUE_OPTIONS = ("1", "on", "t", "true", "y", "yes")


def _add_ddtrace_injector(processors: list) -> list:
    if os.environ.get("APP_APM_ENABLED", "0").lower() in TRUE_OPTIONS:
        from .datadog import inject_trace

        processors.insert(-1, inject_trace)
    return processors


def configure_defaults(
    level: int | None = None,
    processors: list = DEFAULT_PROCESSORS,
    shared_processors: list = DEFAULT_SHARED_PROCESSORS,
    logger_factory: Any = DEFAULT_LOGGER_FACTORY,
    wrapper_class: Any = DEFAULT_WRAPPER_CLASS,
    cache_logger_on_first_use: bool = DEFAULT_CACHE_LOGGER_ON_FIRST_USE,
    extra_handler: Any = None,
) -> None:
    """Configure structlog using Urbint's defaults.

    If `level` is set it will create a bound logger, making filtering faster but making the level
    unable to be changed later.
    """
    processors = _add_ddtrace_injector(processors)

    if level is not None:
        wrapper_class = structlog.make_filtering_bound_logger(level)

    structlog.configure_once(
        processors=processors,
        logger_factory=logger_factory,
        wrapper_class=wrapper_class,
        cache_logger_on_first_use=cache_logger_on_first_use,
    )
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=DEFAULT_JSON_RENDERER,
        foreign_pre_chain=shared_processors,
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    if extra_handler:
        root_logger.addHandler(extra_handler)
    if level is not None:
        root_logger.setLevel(level)


def get_logger(*args: Any, **initial_values: Any) -> Any:
    return structlog.get_logger(*args, **initial_values)


getLogger = get_logger
