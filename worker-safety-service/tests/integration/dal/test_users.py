from uuid import uuid4

import pytest

from tests.factories import TenantFactory, UserFactory
from worker_safety_service.dal.user import UserManager
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.user import UserCreate


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_or_create_creates(
    db_session: AsyncSession, user_manager: UserManager
) -> None:
    tenant = await TenantFactory.persist(db_session)

    keycloak_id = uuid4()
    user, created = await user_manager.get_or_create(
        keycloak_id=str(keycloak_id),
        tenant_id=tenant.id,
        user=UserCreate(
            first_name="test_name",
            last_name="test_last_name",
            email="aa@test.com",
            keycloak_id=keycloak_id,
            tenant_id=tenant.id,
        ),
    )
    assert user.id
    assert user.first_name == "test_name"
    assert user.last_name == "test_last_name"
    assert user.email == "aa@test.com"
    assert user.tenant_id == tenant.id
    assert user.keycloak_id == keycloak_id
    assert created is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_or_creates_gets_existing_user(
    db_session: AsyncSession, user_manager: UserManager
) -> None:
    tenant = await TenantFactory.persist(db_session)
    user = await UserFactory.persist(db_session, tenant_id=tenant.id)

    fetched_user, created = await user_manager.get_or_create(
        keycloak_id=user.keycloak_id,
        tenant_id=tenant.id,
        user=UserCreate(
            first_name="test_name",
            last_name="test_last_name",
            email="aa@test.com",
            keycloak_id=user.keycloak_id,
            tenant_id=tenant.id,
        ),
    )
    assert user.id == fetched_user.id
    assert user.keycloak_id == fetched_user.keycloak_id
    assert user.tenant_id == fetched_user.tenant_id
    assert created is False


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_by_keycloak_id_filters_by_tenent_id(
    db_session: AsyncSession, user_manager: UserManager
) -> None:
    tenant_1, tenant_2 = await TenantFactory.persist_many(db_session, size=2)
    user_1, user_2 = await UserFactory.persist_many(
        db_session,
        per_item_kwargs=[{"tenant_id": tenant_1.id}, {"tenant_id": tenant_2.id}],
    )
    fetched_user = await user_manager.get_by_keycloak_id(
        user_1.keycloak_id, user_2.tenant_id
    )
    assert fetched_user is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_non_archived_at_users(
    db_session: AsyncSession, user_manager: UserManager
) -> None:
    tenant = await TenantFactory.persist(db_session)

    keycloak_id = uuid4()
    user_1, created = await user_manager.get_or_create(
        keycloak_id=str(keycloak_id),
        tenant_id=tenant.id,
        user=UserCreate(
            first_name="test_name_1",
            last_name="test_last_name_1",
            email="aa_1@test.com",
            keycloak_id=keycloak_id,
            tenant_id=tenant.id,
        ),
    )

    user_1_is_archived = await user_manager.archive_user(user_1.id)

    assert user_1_is_archived

    keycloak_id = uuid4()
    user_2, created = await user_manager.get_or_create(
        keycloak_id=str(keycloak_id),
        tenant_id=tenant.id,
        user=UserCreate(
            first_name="test_name_2",
            last_name="test_last_name_2",
            email="aa_2@test.com",
            keycloak_id=keycloak_id,
            tenant_id=tenant.id,
        ),
    )

    get_non_archived_at_users = await user_manager.get_users(
        [user_1.id, user_2.id], allow_archived=False
    )

    assert len(get_non_archived_at_users) == 1
