import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from tests.factories import TenantFactory, UserFactory
from worker_safety_service.models import AsyncSession


@pytest.mark.asyncio
@pytest.mark.integration
async def test_different_users_can_have_same_keycloak_id(
    db_session: AsyncSession,
) -> None:
    keycloak_id = uuid.uuid4()

    tenant_1 = await TenantFactory.persist(db_session)
    user_1 = await UserFactory.persist(
        db_session, tenant_id=tenant_1.id, keycloak_id=keycloak_id
    )
    tenant_2 = await TenantFactory.persist(db_session)
    user_2 = await UserFactory.persist(
        db_session, tenant_id=tenant_2.id, keycloak_id=keycloak_id
    )

    assert user_1.keycloak_id == user_2.keycloak_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_different_users_can_have_same_tenant_id(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)

    user_1 = await UserFactory.persist(
        db_session, tenant_id=tenant.id, keycloak_id=uuid.uuid4()
    )
    user_2 = await UserFactory.persist(
        db_session, tenant_id=tenant.id, keycloak_id=uuid.uuid4()
    )

    assert user_1.tenant_id == user_2.tenant_id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_different_users_cannot_have_same_tenant_and_keycloak_ids(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    keycloak_id = uuid.uuid4()

    # create user
    await UserFactory.persist(db_session, tenant_id=tenant.id, keycloak_id=keycloak_id)
    with pytest.raises(IntegrityError) as err:
        # try to create user with same tenant and keycloak_id
        await UserFactory.persist(
            db_session, tenant_id=tenant.id, keycloak_id=keycloak_id
        )
    assert err.match("users_tenant_keycloak_idx")
