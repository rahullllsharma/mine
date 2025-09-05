import asyncio
import csv
from collections.abc import Iterable
from functools import wraps
from pathlib import Path
from time import sleep
from typing import Any, Callable, Optional

import typer
from redis.asyncio import Redis

from worker_safety_service.models import AsyncSession, get_session
from worker_safety_service.redis_client import with_redis_client


class TyperContext(typer.Context):
    session: AsyncSession
    redis: Redis


def run_async(func: Callable) -> Any:
    """
    Decorator to allow async commands
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Optional[Any]) -> Any:
        coro = func(*args, **kwargs)

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass
        else:
            # This should only be used with testing
            task = loop.create_task(coro)
            while True:
                if task.done():
                    return task.result()
                else:
                    sleep(0.5)

        # Run this here so we don't have RuntimeError traceback if something fails
        return asyncio.run(coro)

    return wrapper


def with_session(func: Callable) -> Any:
    """
    Inject async db session to CLI command
    Note that command needs to have `TyperContext` annotation:

    ```
        @app.command(name="test")
        @run_async
        @with_session
        async def test(
            ctx: TyperContext,
        ) -> None:
            await ctx.session.exec(...).all()
    ```
    """

    assert (
        func.__annotations__.get("ctx") is TyperContext
    ), f"{func.__name__} func must have `ctx: TyperContext` arg"

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with get_session() as session:
            ctx: TyperContext = kwargs["ctx"]
            ctx.session = session
            return await func(*args, **kwargs)

    return wrapper


def with_redis(func: Callable) -> Any:
    """
    Inject redis to CLI command
    Note that command needs to have `TyperContext` annotation:
    ```
        @app.command(name="test")
        @run_async
        @with_redis
        async def test(
            ctx: TyperContext,
        ) -> None:
            await ctx.redis.get("test")
    ```
    """

    assert (
        func.__annotations__.get("ctx") is TyperContext
    ), f"{func.__name__} func must have `ctx: TyperContext` arg"

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        async with with_redis_client() as redis:
            ctx: TyperContext = kwargs["ctx"]
            ctx.redis = redis
            return await func(*args, **kwargs)

    return wrapper


def find_csv_header(columns: dict[str, str], row: list[str]) -> dict[str, int]:
    clean_columns = {key.strip().lower(): value for key, value in columns.items()}
    assert len(clean_columns) == len(columns)

    position: dict[str, int] = {}
    for index, value in enumerate(row):
        column_name = clean_columns.get(value.strip().lower())
        if column_name:
            if column_name in position:
                raise ValueError(f'Duplicated column name "{value}" column:{index + 1}')
            position[column_name] = index

    if len(position) != len(columns):
        position.clear()
    return position


def iter_csv(
    path: Path | str,
    columns: dict[str, str],
    delimiter: str = ",",
    allow_empty_values: bool = False,
) -> Iterable[tuple[int, dict[str, str]]]:
    with open(path, "r") as fp:
        columns_position: dict[str, int] = {}
        for row_index, row in enumerate(csv.reader(fp, delimiter=delimiter)):
            if not columns_position:
                columns_position = find_csv_header(columns, row)
            else:
                data: dict[str, str] = {}
                for column_name, index in columns_position.items():
                    value = row[index].strip()
                    if not allow_empty_values and not value:
                        raise ValueError(
                            f"Empty value on row:{row_index + 1} column:{index + 1}"
                        )
                    data[column_name] = value

                yield row_index, data

        if not columns_position:
            raise ValueError("Not able to find columns reference")
