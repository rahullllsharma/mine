import functools
import sys
import uuid
from collections import defaultdict
from contextvars import ContextVar
from time import time
from types import TracebackType
from typing import Any, Type, TypedDict

import typer
from starlette.staticfiles import StaticFiles
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from structlog.contextvars import (
    bind_contextvars,
    bound_contextvars,
    clear_contextvars,
    unbind_contextvars,
)

from . import get_logger

logger = get_logger(__name__)

SQLALCHEMY_STATS_REGISTERED = False
CTX_STATS_CALLS: ContextVar[defaultdict[str, int]] = ContextVar("request_stats_calls")
CTX_STATS_TIME: ContextVar[defaultdict[str, float]] = ContextVar("request_stats_time")
CTX_STATS_ITEMS: ContextVar[defaultdict[str, int]] = ContextVar("request_stats_items")
CTX_CORRELATION: ContextVar[str] = ContextVar("request_correlation_id")


class LogMiddlewareInfo(TypedDict):
    sent_bytes: int
    original_bytes: int
    request_id: str
    correlation_id: str
    status_code: str | None
    first_byte_at: float | None


class ClearContextVarsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        clear_contextvars()
        await self.app(scope, receive, send)


class RequestContextLogMiddleware:
    def __init__(self, app: ASGIApp, with_sqlalchemy_stats: bool = False) -> None:
        self.app = app

        if with_sqlalchemy_stats:
            # Register sqlalchemy stats because we have stats context
            watch_sqlachemy_stats()

    @staticmethod
    async def send(info: LogMiddlewareInfo, send: Send, message: Message) -> None:
        if message["type"] == "http.response.start":
            # Extend response headers
            message["headers"].extend(
                (
                    (b"x-request-id", info["request_id"].encode()),
                    (b"x-correlation-id", info["correlation_id"].encode()),
                )
            )

            info["status_code"] = message.get("status")
            info["first_byte_at"] = time()
        else:
            if body := message.get("body"):
                info["sent_bytes"] += len(body)
            if original_bytes := message.get("original_bytes"):
                info["original_bytes"] += original_bytes

        await send(message)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request_start = time()
        correlation_id = find_correlation_id(scope)

        with LogSession(correlation_id=correlation_id) as log_session:
            # Catch response info
            info = LogMiddlewareInfo(
                sent_bytes=0,
                original_bytes=0,
                request_id=log_session.request_id,
                correlation_id=log_session.correlation_id,
                status_code=None,
                first_byte_at=None,
            )
            wrapped_send = functools.partial(self.send, info, send)

            try:
                await self.app(scope, receive, wrapped_send)
            except:  # noqa: E722
                # Log and raise so that the exception can still run it's course
                logger.exception("Uncaught error during request.")
                raise
            finally:
                now = time()
                first_byte_at = info["first_byte_at"] or now
                logger.info(
                    "Request done",
                    status_code=info["status_code"],
                    sent_bytes=info["sent_bytes"],
                    original_bytes=info["original_bytes"] or info["sent_bytes"],
                    first_byte_took=round(first_byte_at - request_start, 4),
                    took=round(now - request_start, 4),
                    **get_scope_details(scope),
                    **{f"{k}_calls": v for k, v in CTX_STATS_CALLS.get().items()},
                    **{
                        f"{k}_time": round(v, 5)
                        for k, v in CTX_STATS_TIME.get().items()
                    },
                    **{f"{k}_items": v for k, v in CTX_STATS_ITEMS.get().items()},
                )


class TyperLogWrapper(typer.Typer):
    def __init__(self, *args: Any, **kwargs: Any):
        self.with_sqlalchemy_stats = kwargs.pop("with_sqlalchemy_stats", False)
        super().__init__(*args, **kwargs)

    @staticmethod
    def find_called_command() -> dict[str, str]:
        # TODO: do we have a better way to find called command?
        info: dict[str, str] = {}
        wss_index: int | None = None
        try:
            wss_index = sys.argv.index("wss")
        except ValueError:
            for index, item in enumerate(sys.argv):
                if item == "wss" or item.endswith("/wss"):
                    wss_index = index
                    break
        if wss_index is not None:
            try:
                info["cli_group"] = sys.argv[wss_index + 1]
                info["cli_command"] = sys.argv[wss_index + 2]
            except IndexError:
                pass

        return info

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        clear_contextvars()

        if self.with_sqlalchemy_stats:
            # Register sqlalchemy stats because we have stats context
            watch_sqlachemy_stats()

        request_start = time()
        with LogSession():
            with bound_contextvars(**self.find_called_command()):
                try:
                    return super().__call__(*args, **kwargs)
                except (SystemExit, typer.Exit) as error:
                    if hasattr(error, "code"):
                        # SystemExit
                        code = error.code
                    else:
                        # typer.Exit
                        code = error.exit_code

                    if code != 0:
                        logger.error(
                            "CLI failed with exit code",
                            code=code,
                            error_context=str(getattr(error, "__context__", "")),
                        )

                    raise
                except:  # noqa: E722, B001
                    logger.exception("CLI failed")
                finally:
                    logger.info(
                        "CLI done",
                        took=round(time() - request_start, 4),
                        **{f"{k}_calls": v for k, v in CTX_STATS_CALLS.get().items()},
                        **{
                            f"{k}_time": round(v, 5)
                            for k, v in CTX_STATS_TIME.get().items()
                        },
                    )

                # raise it here so we don't log the traceback twice
                raise typer.Exit(code=1)


class LogSession:
    request_id: str
    correlation_id: str

    __slots__ = (
        "ctx_calls_token",
        "ctx_times_token",
        "ctx_items_token",
        "ctx_correlation_token",
        "request_id",
        "correlation_id",
    )

    def __init__(self, correlation_id: str | None = None) -> None:
        self.request_id = str(uuid.uuid4())
        self.correlation_id = correlation_id or self.request_id

    def __enter__(self) -> "LogSession":
        # I/O stats (db, redis, etc)
        self.ctx_calls_token = CTX_STATS_CALLS.set(defaultdict(int))
        self.ctx_times_token = CTX_STATS_TIME.set(defaultdict(float))
        self.ctx_items_token = CTX_STATS_ITEMS.set(defaultdict(int))

        # Request information for tracking
        self.ctx_correlation_token = CTX_CORRELATION.set(self.correlation_id)

        bind_contextvars(request_id=self.request_id, correlation_id=self.correlation_id)
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        unbind_contextvars("request_id", "correlation_id")
        CTX_STATS_CALLS.reset(self.ctx_calls_token)
        CTX_STATS_TIME.reset(self.ctx_times_token)
        CTX_STATS_ITEMS.reset(self.ctx_items_token)
        CTX_CORRELATION.reset(self.ctx_correlation_token)


def watch_sqlachemy_stats() -> None:
    global SQLALCHEMY_STATS_REGISTERED
    if not SQLALCHEMY_STATS_REGISTERED:
        SQLALCHEMY_STATS_REGISTERED = True

        from sqlalchemy import event
        from sqlalchemy.engine import Connection, Engine

        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn: Connection, *args: Any, **kwargs: Any) -> None:
            if "query_start_time" not in conn.info:
                conn.info["query_start_time"] = [time()]
            else:
                conn.info["query_start_time"].append(time())

        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn: Connection, *args: Any, **kwargs: Any) -> None:
            Stats.inc("db", time() - conn.info["query_start_time"].pop(-1))


class Stats:
    __slots__ = ("key", "calls", "start")

    def __init__(self, key: str, calls: int | None = None) -> None:
        self.key = key
        self.calls = calls if calls is not None else 1

    def __enter__(self) -> None:
        self.start = time()

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.inc(self.key, time() - self.start, calls=self.calls)

    @classmethod
    def inc(cls, name: str, took: float, calls: int = 1) -> None:
        CTX_STATS_CALLS.get()[name] += calls
        CTX_STATS_TIME.get()[name] += took

    @classmethod
    def items(cls, name: str, length: int) -> None:
        CTX_STATS_ITEMS.get()[name] += length


def find_correlation_id(scope: Scope) -> str | None:
    for header_name, header_value in scope["headers"]:
        if header_name == b"x-correlation-id":
            try:
                return header_value.decode()[:64].strip() or None
            except:  # noqa: E722 B001
                pass  # In case the header have non-utf8 data
    return None


def get_correlation_id() -> str:
    return CTX_CORRELATION.get()


def get_scope_details(scope: Scope) -> dict[str, Any]:
    endpoint = scope.get("endpoint")
    request_endpoint = None

    if endpoint is not None:
        if isinstance(endpoint, StaticFiles):
            request_endpoint = "StaticFiles"
        else:
            request_endpoint = getattr(endpoint, "__name__", None)

    return {
        "request_type": scope.get("type"),
        "request_method": scope.get("method"),
        "request_path": scope.get("path"),
        "request_endpoint": request_endpoint,
        "ip_address": scope.get("client", [None])[0],
    }
