import pytest

from tests.factories import TenantFactory
from worker_safety_service.dal.opco_manager import OpcoManager
from worker_safety_service.models import AsyncSession, OpcoCreate
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


# Successfully creating an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_opco(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco_manager = OpcoManager(db_session)

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 0

    new_opco_1 = await opco_manager.create_opco(
        OpcoCreate(name="opco_1", full_name="Opco_full_name_1", tenant_id=tenant.id)
    )
    assert new_opco_1
    assert new_opco_1.name == "opco_1"

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 1

    new_opco_2 = await opco_manager.create_opco(
        OpcoCreate(
            name="opco_2",
            full_name="opco_full_name_2",
            tenant_id=tenant.id,
            parent_id=new_opco_1.id,
        )
    )
    assert new_opco_2
    assert new_opco_2.name == "opco_2"
    assert new_opco_2.parent_id == new_opco_1.id

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_opco_by_name(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco_manager = OpcoManager(db_session)

    new_opco = await opco_manager.create_opco(
        OpcoCreate(
            name="opco_1",
            full_name="Opco_full_name_1",
            tenant_id=tenant.id,
        ),
    )

    opco_found = await opco_manager.get_opco_by_name(tenant.id, "Opco_full_name_1")

    assert opco_found
    assert opco_found.id == new_opco.id
    assert opco_found.name == new_opco.name

    opco_not_found = await opco_manager.get_opco_by_name(tenant.id, "not_a_opco_name")

    assert opco_not_found is None


# Update Opco
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_opco(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco_manager = OpcoManager(db_session)

    opco_one = await opco_manager.create_opco(
        OpcoCreate(name="opco_1", full_name="Opco_full_name_1", tenant_id=tenant.id)
    )
    opco_two = await opco_manager.create_opco(
        OpcoCreate(
            name="opco_2",
            full_name="opco_full_name_2",
            tenant_id=tenant.id,
            parent_id=opco_one.id,
        )
    )

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 2
    assert opcos[0].name == opco_one.name
    assert opcos[1].name == opco_two.name

    opco_one.name = "opco_1_updated"
    await opco_manager.edit_opco(opco=opco_one)

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 2
    assert opcos[0].name == opco_one.name
    assert opcos[1].name == opco_two.name


# Delete opco with no sub opco
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_opco_with_no_subopco(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco_manager = OpcoManager(db_session)

    opco_one = await opco_manager.create_opco(
        OpcoCreate(name="opco_1", full_name="Opco_full_name_1", tenant_id=tenant.id)
    )

    opco_two = await opco_manager.create_opco(
        OpcoCreate(
            name="opco_2",
            full_name="opco_full_name_2",
            tenant_id=tenant.id,
            parent_id=opco_one.id,
        )
    )

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 2

    await opco_manager.delete_opco(opco_two.id)

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 1
    assert opcos[0].name == opco_one.name

    await opco_manager.delete_opco(opco_one.id)
    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 0


# Delete opco with sub opco
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_opco_with_subopco(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    opco_manager = OpcoManager(db_session)

    opco_one = await opco_manager.create_opco(
        OpcoCreate(name="opco_1", full_name="Opco_full_name_1", tenant_id=tenant.id)
    )

    await opco_manager.create_opco(
        OpcoCreate(
            name="opco_2",
            full_name="opco_full_name_2",
            tenant_id=tenant.id,
            parent_id=opco_one.id,
        )
    )

    delete_opco = await opco_manager.delete_opco(opco_one.id)
    assert delete_opco.error is not None

    opcos = await opco_manager.get_all_opco(tenant_id=tenant.id)
    assert len(opcos) == 2
