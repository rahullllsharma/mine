from uuid import uuid4

import pytest
from faker import Faker
from pydantic.error_wrappers import ValidationError

from tests.factories import CrewLeaderFactory, TenantFactory
from worker_safety_service.dal.crew_leader_manager import CrewLeaderManager
from worker_safety_service.exceptions import DuplicateKeyException
from worker_safety_service.models import (
    AsyncSession,
    CreateCrewLeaderInput,
    Tenant,
    UpdateCrewLeaderInput,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)
fake = Faker()


# Successfully creating an crew leader
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    crew_leader_manager = CrewLeaderManager(db_session)
    crew_leaders = await crew_leader_manager.get_all(tenant_id=tenant.id)
    assert len(crew_leaders) == 0

    name = fake.name() + str(uuid4())
    new_crew_leader = await crew_leader_manager.create(
        CreateCrewLeaderInput(
            name=name,
        ),
        tenant_id=tenant.id,
    )
    assert new_crew_leader
    assert new_crew_leader.name == name
    assert new_crew_leader.tenant == tenant
    assert new_crew_leader.archived_at is None
    assert new_crew_leader.lanid is None
    assert new_crew_leader.company_name is None

    crew_leaders = await crew_leader_manager.get_all(tenant_id=tenant.id)
    assert len(crew_leaders) == 1

    name1 = fake.name() + str(uuid4())
    new_crew_leader = await crew_leader_manager.create(
        CreateCrewLeaderInput(
            name=name1,
        ),
        tenant_id=tenant.id,
    )
    assert new_crew_leader.name == name1
    assert new_crew_leader.tenant == tenant
    assert new_crew_leader.archived_at is None
    assert new_crew_leader.lanid is None
    assert new_crew_leader.company_name is None

    crew_leaders = await crew_leader_manager.get_all(tenant_id=tenant.id)
    assert len(crew_leaders) == 2


# Successfully updating an crew leader
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_crew_leader(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_crew_leaders = await CrewLeaderFactory.persist_many(
        db_session, tenant_id=tenant.id, size=3
    )
    crew_leader_manager = CrewLeaderManager(db_session)
    crew_leader_to_be_updated = db_crew_leaders[0]
    assert crew_leader_to_be_updated.name
    assert crew_leader_to_be_updated.archived_at is None

    await crew_leader_manager.update(
        id=crew_leader_to_be_updated.id,
        tenant_id=tenant.id,
        input=UpdateCrewLeaderInput(name="updated_name_in_test"),
    )
    await db_session.refresh(crew_leader_to_be_updated)
    assert crew_leader_to_be_updated.name == "updated_name_in_test"
    assert crew_leader_to_be_updated.tenant == tenant
    assert crew_leader_to_be_updated.archived_at is None


# Successfully deleting an crew leader
@pytest.mark.asyncio
@pytest.mark.integration
async def test_archive_crew_leader(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    db_crew_leaders = []
    for _ in range(1, 4):
        crew_leader = await CrewLeaderFactory.persist(db_session, tenant_id=tenant.id)
        db_crew_leaders.append(crew_leader)

    crew_leader_manager = CrewLeaderManager(db_session)

    crew_leader_to_be_archived = db_crew_leaders[1]
    assert crew_leader_to_be_archived.archived_at is None

    assert await crew_leader_manager.archive(
        id=crew_leader_to_be_archived.id, tenant_id=tenant.id
    )

    await db_session.refresh(crew_leader_to_be_archived)
    assert crew_leader_to_be_archived.archived_at

    await db_session.refresh(db_crew_leaders[0])
    assert not db_crew_leaders[0].archived_at


# Successfully querying all crew leaders for a tenant
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_crew_leaders(db_session: AsyncSession) -> None:
    tenant = await TenantFactory.persist(db_session)
    crew_leader_manager = CrewLeaderManager(db_session)
    await create_10_crew_leaders(tenant=tenant, crew_leader_manager=crew_leader_manager)
    crew_leaders_all = await crew_leader_manager.get_all(tenant.id)
    assert len(crew_leaders_all) == 10
    crew_leaders_first_5 = await crew_leader_manager.get_all(tenant.id, limit=5)
    assert len(crew_leaders_first_5) == 5
    crew_leaders_last_3 = await crew_leader_manager.get_all(
        tenant.id, limit=3, offset=7
    )
    assert len(crew_leaders_last_3) == 3
    crew_leaders_last_1 = await crew_leader_manager.get_all(
        tenant.id, limit=3, offset=9
    )
    assert len(crew_leaders_last_1) == 1


# Should not be able to create an crew leader if mandatory fields are not provided
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader_error_missing_required_fields(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    crew_leader_manager = CrewLeaderManager(db_session)
    with pytest.raises(ValidationError):
        await crew_leader_manager.create(
            CreateCrewLeaderInput(),  # type:ignore # name missing
            tenant_id=tenant.id,
        )
    # logger.debug(f"ERROR --> {e.value.args[0]}")


# Should not be able to create duplicate crew_leader(name cannot be duplicate)
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_crew_leader_error_duplicate_name(
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    crew_leader_manager = CrewLeaderManager(db_session)
    await create_10_crew_leaders(tenant=tenant, crew_leader_manager=crew_leader_manager)
    with pytest.raises(DuplicateKeyException) as e:
        await crew_leader_manager.create(
            CreateCrewLeaderInput(
                name="test1",
            ),
            tenant_id=tenant.id,
        )

    assert (
        e.value.args[0]
        == "Crew Leader with name 'test1' already exists. Please select a unique name"
    )


async def create_10_crew_leaders(
    tenant: Tenant, crew_leader_manager: CrewLeaderManager
) -> None:
    for i in range(1, 11):
        crew_leader = await crew_leader_manager.create(
            CreateCrewLeaderInput(
                name=f"test{i}",
            ),
            tenant_id=tenant.id,
        )
        assert crew_leader
