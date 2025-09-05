import time
import uuid
from collections.abc import AsyncGenerator
from queue import Empty
from unittest import TestCase
from unittest.mock import patch

import pytest

from worker_safety_service.risk_model.riskmodel_container import RiskModelContainer
from worker_safety_service.risk_model.riskmodelreactor_redis import (
    RiskModelReactorRedisImpl,
    __rebuild_redis_assets,
)
from worker_safety_service.risk_model.triggers.project_changed import ProjectChanged


@pytest.mark.asyncio
@pytest.fixture
async def reactor_impl(
    app_container: RiskModelContainer,
) -> AsyncGenerator[RiskModelReactorRedisImpl, None]:
    redis_database = await app_container.redis_database()
    reactor = RiskModelReactorRedisImpl(redis_database)
    await __rebuild_redis_assets(reactor)
    yield reactor


@pytest.mark.asyncio
@pytest.mark.integration
async def test_basic_call_workflow_1(reactor_impl: RiskModelReactorRedisImpl) -> None:
    is_empty = await reactor_impl._is_empty()
    assert is_empty

    expected_calculation = ProjectChanged(uuid.uuid4())
    await reactor_impl.add(expected_calculation)

    is_empty = await reactor_impl._is_empty()
    assert is_empty is False

    calculation = await reactor_impl._fetch()
    assert calculation == expected_calculation

    is_empty = await reactor_impl._is_empty()
    assert is_empty


@pytest.mark.asyncio
@pytest.mark.integration
async def test_retries_on_empty_queue(reactor_impl: RiskModelReactorRedisImpl) -> None:
    test = TestCase()
    with patch.object(
        reactor_impl, "fetch_from_redis", wraps=reactor_impl.fetch_from_redis
    ) as spyed_call:
        start_counter = time.perf_counter()

        with test.assertRaises(Empty):
            await reactor_impl._fetch(1)

        elapsed_time = time.perf_counter() - start_counter
        # Added 1s of tolerance and 2 calls
        assert 1.0 <= elapsed_time < 2.0
        assert 3 <= spyed_call.call_count <= 5
