from unittest.mock import patch

import pytest

from tests.factories import TenantFactory
from tests.integration.dataloaders.conftest import MockedSQLResult
from worker_safety_service.graphql.data_loaders.tenants import TenantLoader
from worker_safety_service.models import AsyncSession, Tenant


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_tenants_order(
    db_session: AsyncSession, tenant_loader: TenantLoader
) -> None:
    """Make sure order returned by dataloaders match request"""
    prim_tenant = await TenantFactory.default_tenant(db_session)
    sec_tenant: Tenant = await TenantFactory.persist(db_session)

    # Reserve db results so we can check if dataloader still keeps the order
    names = [prim_tenant.tenant_name, sec_tenant.tenant_name]
    reversed_db_result = [sec_tenant, prim_tenant]

    with patch.object(
        db_session, "exec", return_value=MockedSQLResult(reversed_db_result)
    ):
        # Direct call
        tenants = await tenant_loader.load_tenants(names)
        assert tenants == [prim_tenant, sec_tenant]

        # Dataloader for many
        tenants = await tenant_loader.me.load_many(names)
        assert tenants == [prim_tenant, sec_tenant]

        # Dataloader for one
        # This tests too if for some reason the query returns more than expected
        tenant = await tenant_loader.me.load(names[0])
        assert tenant == prim_tenant


@pytest.mark.asyncio
@pytest.mark.integration
async def test_load_tenants_missing(
    db_session: AsyncSession, tenant_loader: TenantLoader
) -> None:
    """Return None and don't raise an error when tenant don't exists"""
    prim_tenant = await TenantFactory.default_tenant(db_session)
    names = [prim_tenant.tenant_name, "some-invalid"]

    # Direct call
    tenants = await tenant_loader.load_tenants(names)
    assert tenants == [prim_tenant, None]

    # Dataloader for many
    tenants = await tenant_loader.me.load_many(names)
    assert tenants == [prim_tenant, None]

    # Dataloader for one
    tenant = await tenant_loader.me.load(names[0])
    assert tenant == prim_tenant

    # Dataloader for one
    tenant = await tenant_loader.me.load(names[1])
    assert tenant is None
