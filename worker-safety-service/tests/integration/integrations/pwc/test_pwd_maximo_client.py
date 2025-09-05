import uuid
from typing import Awaitable, Callable
from unittest import TestCase
from uuid import UUID

import pytest

from worker_safety_service import settings
from worker_safety_service.integrations.pwc.pwd_maximo_client import PwCMaximoClient
from worker_safety_service.models import RiskLevel
from worker_safety_service.site_conditions.world_data import HTTPClient


@pytest.fixture
def pwc_maximo_client() -> PwCMaximoClient:
    return PwCMaximoClient(
        HTTPClient,
        "DUMB_CLIENT_ID",
        "DUMB_CLIENT_SECRET",
        settings.PRISM_BASE_URL,
        "http://localhost:8001",
    )


METHODS = [
    PwCMaximoClient.post_work_package_updates,
    PwCMaximoClient.post_location_updates,
]


@pytest.mark.skip
@pytest.mark.parametrize(
    "method",
    METHODS,
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_method_request(
    pwc_maximo_client: PwCMaximoClient,
    method: Callable[
        [PwCMaximoClient, list[tuple[UUID, str, RiskLevel]]], Awaitable[None]
    ],
) -> None:
    risk_summaries: list[tuple[UUID, str, RiskLevel]] = [
        (uuid.uuid4(), str(uuid.uuid4()), RiskLevel(rl))
        for rl in [RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW, RiskLevel.UNKNOWN]
    ]

    await method(pwc_maximo_client, risk_summaries)


@pytest.mark.skip
@pytest.mark.parametrize(
    "method",
    METHODS,
)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_method_fails_with_recalculating(
    pwc_maximo_client: PwCMaximoClient,
    method: Callable[
        [PwCMaximoClient, list[tuple[UUID, str, RiskLevel]]], Awaitable[None]
    ],
) -> None:
    risk_summaries: list[tuple[UUID, str, RiskLevel]] = [
        (uuid.uuid4(), str(uuid.uuid4()), RiskLevel.RECALCULATING)
    ]

    test = TestCase()
    with test.assertRaises(Exception):
        await method(pwc_maximo_client, risk_summaries)
