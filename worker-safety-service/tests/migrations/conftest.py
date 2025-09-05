import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, Coroutine

import pytest
from _pytest.fixtures import SubRequest
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from tests.db_data import (
    DB_REUSE_NAME,
    RecreateDB,
    create_template_db,
    get_or_create_asgard_tenant,
    remove_template_db,
    run_db_upgrade,
)
from worker_safety_service.config import settings
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.utils import create_engine, create_sessionmaker


def pytest_configure(config: pytest.Config) -> None:
    logger = logging.getLogger("alembic.runtime.migration")
    logger.disabled = True

    asyncio.run(create_template_db())


def pytest_unconfigure(config: pytest.Config) -> None:
    asyncio.run(remove_template_db())


@pytest.mark.asyncio
@pytest.fixture
async def db_dsn(request: SubRequest) -> AsyncGenerator[str, None]:
    if any(i.name == "fresh_db" for i in request.node.iter_markers()):
        async with RecreateDB() as db:
            yield db.dsn
    else:
        yield settings.build_db_dsn(db=DB_REUSE_NAME)


@pytest.fixture
async def engine(db_dsn: str) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_engine(db_dsn, poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture
def async_sessionmaker(engine: AsyncEngine) -> sessionmaker:
    return create_sessionmaker(engine)


@pytest.fixture
async def db_session(
    async_sessionmaker: sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = async_sessionmaker()
    async with session as with_session:
        yield with_session


@pytest.fixture
def migrate_upto() -> Callable[..., Coroutine[Any, Any, None]]:
    async def _migrate(revision: str) -> None:
        from tests.factories import (
            AdminUserFactory,
            ManagerUserFactory,
            SupervisorUserFactory,
        )

        _engine = create_engine(
            settings.build_db_dsn(db=DB_REUSE_NAME),
            # disable pooling to prevent test-runner deadlock
            poolclass=NullPool,
        )
        async with _engine.connect() as connection:
            await connection.run_sync(lambda _c: run_db_upgrade(_c, revision))

        # Add default roles
        async with AsyncSession(_engine) as session:
            asgard_tenant = await get_or_create_asgard_tenant(session=session)

            session.add_all(
                [
                    AdminUserFactory.build(tenant_id=asgard_tenant.id),
                    ManagerUserFactory.build(tenant_id=asgard_tenant.id),
                    SupervisorUserFactory.build(tenant_id=asgard_tenant.id),
                ]
            )
            await session.commit()

        await _engine.dispose()

    return _migrate
