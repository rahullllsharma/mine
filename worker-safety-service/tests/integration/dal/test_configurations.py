import datetime
import uuid
from typing import Optional

import pytest
from faker import Faker

from tests.factories import SupervisorUserFactory, TenantFactory, WorkTypeFactory
from tests.integration.helpers import update_configuration
from worker_safety_service.dal.configurations import (
    WORK_PACKAGE_CONFIG,
    ConfigurationsManager,
)
from worker_safety_service.models import AsyncSession, Tenant, WorkPackageCreate


async def default_tenant_id(
    db_session: AsyncSession,
) -> uuid.UUID:
    default_tenant = await TenantFactory.default_tenant(db_session)
    return default_tenant.id


async def known_tenant_ids(
    db_session: AsyncSession,
) -> list[uuid.UUID]:
    created_tenants: list[Tenant] = await TenantFactory.persist_many(
        session=db_session, size=2
    )
    return [
        await default_tenant_id(db_session),
        *map(lambda t: t.id, created_tenants),
    ]


@pytest.mark.parametrize("tenant_id", [None, default_tenant_id])
@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_after_write_single_tenant(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id: uuid.UUID,
) -> None:
    fake = Faker()
    if callable(tenant_id):
        tenant_id = await tenant_id(db_session)

    label = "TEST.MY_PROPERTY"
    expected_value = fake.name()

    await configurations_manager.store(label, expected_value, tenant_id=tenant_id)
    actual_value = await configurations_manager.load(label, tenant_id=tenant_id)

    assert actual_value == expected_value, "values must match"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_after_write_multi_tenant(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    fake = Faker()

    tenant_ids: list[Optional[uuid.UUID]] = [None]
    tenant_ids.extend(await known_tenant_ids(db_session))
    expected_values = list(map(lambda _: fake.name(), tenant_ids))

    label = "TEST.MY_PROPERTY_MULTI"
    for t_id, value in zip(tenant_ids, expected_values):
        await configurations_manager.store(label, value, tenant_id=t_id)

    actual_values = [
        await configurations_manager.load(label, tenant_id=t_id) for t_id in tenant_ids
    ]

    assert actual_values == expected_values, "values must match"


@pytest.mark.parametrize("tenant_id", [None, default_tenant_id])
@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_after_write_twice(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id: uuid.UUID,
) -> None:
    fake = Faker()
    if callable(tenant_id):
        tenant_id = await tenant_id(db_session)

    name = "TEST.MY_PROPERTY_TWICE"
    expected_value = fake.name()

    await configurations_manager.store(name, "BURNER VALUE", tenant_id=tenant_id)
    await configurations_manager.store(name, expected_value, tenant_id=tenant_id)

    actual_value = await configurations_manager.load(name, tenant_id=tenant_id)

    assert actual_value == expected_value, "values must match"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize("tenant_id", [None, default_tenant_id, uuid.uuid4()])
async def test_read_unknown(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id: uuid.UUID,
) -> None:
    if callable(tenant_id):
        tenant_id = await tenant_id(db_session)

    name = "TEST.MY_UNKNOWN_PROPERTY"

    value = await configurations_manager.load(name, tenant_id=tenant_id)
    assert value is None

    actual_value = await configurations_manager.load(name, tenant_id=tenant_id)
    assert actual_value is None


@pytest.mark.parametrize("tenant_id", [default_tenant_id, uuid.uuid4()])
@pytest.mark.asyncio
@pytest.mark.integration
async def test_read_default_value(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
    tenant_id: uuid.UUID,
) -> None:
    if callable(tenant_id):
        tenant_id = await tenant_id(db_session)

    default_value = "DEFAULT_VALUE"
    label = "TEST.MY_PROPERTY_DEFAULT"

    # Store the default value and check if it was store properly
    await configurations_manager.store(label, default_value, tenant_id=None)
    pre_condition_value = await configurations_manager.load(label, tenant_id=None)
    assert pre_condition_value == default_value

    actual_value = await configurations_manager.load(label, tenant_id=tenant_id)
    assert actual_value == default_value, "values must match"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_default_value_is_preserved(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = await default_tenant_id(db_session)

    default_value = "DEFAULT_VALUE"
    tenant_value = "TENANT_VALUE"
    label = "TEST.MY_PROPERTY_DEFAULT"

    # Store the default value and a tenant specific value
    await configurations_manager.store(label, default_value, tenant_id=None)
    await configurations_manager.store(label, tenant_value, tenant_id=tenant_id)

    actual = await configurations_manager.load(label, tenant_id=None)
    assert actual == default_value


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validate_model(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    supervisor_id = (
        await SupervisorUserFactory.persist(db_session, tenant_id=tenant_id)
    ).id
    work_type_id = (await WorkTypeFactory.persist(db_session)).id
    work_package = WorkPackageCreate(
        tenant_id=tenant_id,
        name="Test",
        start_date=datetime.date.today(),
        end_date=datetime.date.today(),
        primary_assigned_user_id=supervisor_id,
        additional_assigned_users_ids=[],
        work_type_ids=[work_type_id],
    )

    # Check if list=[] is required
    await update_configuration(
        configurations_manager,
        tenant_id,
        WORK_PACKAGE_CONFIG,
        required_fields=["additional_assigned_users_ids"],
    )
    with pytest.raises(ValueError):
        work_package.additional_assigned_users_ids = []
        await configurations_manager.validate_model(
            WORK_PACKAGE_CONFIG, work_package, tenant_id
        )

    # Check if None is required
    await update_configuration(
        configurations_manager,
        tenant_id,
        WORK_PACKAGE_CONFIG,
        required_fields=["description"],
    )
    with pytest.raises(ValueError):
        work_package.description = None
        await configurations_manager.validate_model(
            WORK_PACKAGE_CONFIG, work_package, tenant_id
        )

    # Check if string='' is required
    await update_configuration(
        configurations_manager,
        tenant_id,
        WORK_PACKAGE_CONFIG,
        required_fields=["description"],
    )
    with pytest.raises(ValueError):
        work_package.description = ""
        await configurations_manager.validate_model(
            WORK_PACKAGE_CONFIG, work_package, tenant_id
        )


async def test_changing_default_does_not_change_tenant(
    db_session: AsyncSession,
    configurations_manager: ConfigurationsManager,
) -> None:
    tenant_id = (await TenantFactory.default_tenant(db_session)).id
    default_value = "DEFAULT_VALUE"
    label = "TEST.MY_PROPERTY_DEFAULT"
    new_default_value = "NEW_DEFAULT_VALUE"
    await configurations_manager.store(label, default_value, tenant_id=None)
    await configurations_manager.store(label, default_value, tenant_id=tenant_id)
    actual_default_value = await configurations_manager.load(label, tenant_id=None)
    actual_tenant_value = await configurations_manager.load(label, tenant_id=tenant_id)
    assert actual_default_value == actual_tenant_value == default_value

    await configurations_manager.store(label, new_default_value, tenant_id=None)
    unchanged_tenant_value = await configurations_manager.load(
        label, tenant_id=tenant_id
    )
    updated_default_value = await configurations_manager.load(label, tenant_id=None)
    assert unchanged_tenant_value != updated_default_value
    assert updated_default_value == new_default_value
