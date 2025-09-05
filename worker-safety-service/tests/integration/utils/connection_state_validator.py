import functools
from typing import Any, AsyncGenerator, Callable, Concatenate, ParamSpec, TypeVar

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from worker_safety_service.models import AsyncSession

P = ParamSpec("P")
T = TypeVar("T")


def validate_connection_state_on_teardown(
    fn: Callable[Concatenate[AsyncSession, P], T]
) -> Callable[Concatenate[AsyncSession, P], AsyncGenerator[T, None]]:
    @functools.wraps(fn)
    async def wrapper(
        db_session: AsyncSession, *args: Any, **kwargs: Any
    ) -> AsyncGenerator[T, None]:
        dal_manager = fn(db_session, *args, **kwargs)
        yield dal_manager
        assert db_session.is_active, "Session must be active"
        try:
            # Ping to check if the query works, it should be a better way but I didn't found out.
            await db_session.execute(text("SELECT 1"))
        except DBAPIError:
            pytest.fail("Failing because connection was left in a wrong state.")

    return wrapper
