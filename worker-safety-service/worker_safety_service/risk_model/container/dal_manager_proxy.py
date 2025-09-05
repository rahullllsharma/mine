import functools
import inspect
from typing import Any, Awaitable, Callable

import wrapt
from sqlalchemy.orm import sessionmaker
from wrapt import BoundFunctionWrapper


def session_injector(
    session_factory: sessionmaker,
    wrapped: Callable[[Any], Awaitable[Any]],
    instance: Any,
    args: Any,
    kwargs: Any,
) -> Awaitable[Any]:
    if not inspect.iscoroutinefunction(wrapped):
        return wrapped(*args, **kwargs)

    async def inject_session_object() -> Any:
        session = session_factory()
        instance.session = session
        try:
            return await wrapped(*args, **kwargs)
        finally:
            instance.session = None
            await session.close()

    return inject_session_object()


class DALManagerProxy(wrapt.ObjectProxy):
    def __init__(self, wrapped: Any, session_factory: sessionmaker):
        super(DALManagerProxy, self).__init__(wrapped)
        self.session_factory = session_factory

    def __getattr__(self, name: str) -> Any:
        function = super(DALManagerProxy, self).__getattr__(name)
        instance = super(DALManagerProxy, self).__wrapped__
        session_factory = super(DALManagerProxy, self).__getattr__("session_factory")
        return BoundFunctionWrapper(
            function, instance, functools.partial(session_injector, session_factory)
        )
