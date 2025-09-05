import pytest

from tests.factories import TenantFactory
from worker_safety_service.dal.tenant import TenantManager
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tenant_by_auth_realm_filters_audiences(
    db_session: AsyncSession, tenant_manager: TenantManager
) -> None:
    realm_name = "realm_1"

    aud_1 = "aud_1"
    aud_2 = "aud_2"
    tenant_1 = await TenantFactory.persist(
        db_session, auth_realm_name=realm_name, tenant_name=aud_1
    )
    tenant_2 = await TenantFactory.persist(
        db_session, auth_realm_name=realm_name, tenant_name=aud_2
    )

    fetched_tenant_1 = await tenant_manager.get_tenant_by_auth_realm(
        auth_realm_name=realm_name, audience=aud_1
    )
    assert fetched_tenant_1
    assert fetched_tenant_1.id == tenant_1.id

    fetched_tenant_2 = await tenant_manager.get_tenant_by_auth_realm(
        auth_realm_name=realm_name, audience=aud_2
    )
    assert fetched_tenant_2
    assert fetched_tenant_2.id == tenant_2.id
