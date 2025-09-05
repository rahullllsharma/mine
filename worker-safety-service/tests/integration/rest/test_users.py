from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import TenantFactory, UserFactory
from worker_safety_service.models import AsyncSession

logger = getLogger(__name__)
USER_ROUTE = "http://127.0.0.1:8000/rest/users"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_user(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    user = await UserFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    response = await client.delete(f"{USER_ROUTE}/{user.id}")
    assert response.status_code == 200
    assert response.text == "true"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_users_200_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    db_users = await UserFactory.persist_many(db_session, tenant_id=tenant.id, size=3)

    response = await client.put(
        f"{USER_ROUTE}/{str(db_users[0].id)}?external_id=test_external_id",
    )
    assert response.status_code == 200

    await db_session.refresh(db_users[0])
    assert db_users[0].external_id == "test_external_id"
