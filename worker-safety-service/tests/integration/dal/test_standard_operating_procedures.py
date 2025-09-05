import uuid
from typing import Any

import pytest
from sqlalchemy import select

from tests.factories import (
    LibraryTaskFactory,
    StandardOperatingProcedureFactory,
    unique_id_factory,
)
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.dal.standard_operating_procedures import (
    StandardOperatingProcedureManager,
)
from worker_safety_service.models.standard_operating_procedures import (
    LibraryTaskStandardOperatingProcedure,
)
from worker_safety_service.models.utils import AsyncSession


async def get_all_library_task_standard_operating_procedures(
    db_session: AsyncSession,
    library_task_id: str | uuid.UUID | None = None,
    standard_operating_procedure_id: str | uuid.UUID | None = None,
) -> list[Any]:
    statement = select(LibraryTaskStandardOperatingProcedure)
    if library_task_id:
        statement.where(
            LibraryTaskStandardOperatingProcedure.library_task_id == library_task_id
        )
    if standard_operating_procedure_id:
        statement.where(
            LibraryTaskStandardOperatingProcedure.standard_operating_procedure_id
            == standard_operating_procedure_id
        )
    return (await db_session.execute(statement)).scalars().all()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_check_exists(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )

    # Act / Assert
    await standard_operating_procedure_manager.check_standard_operating_procedure_exists(
        standard_operating_procedure.id, standard_operating_procedure.tenant_id
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_check_not_exists(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure_1 = await StandardOperatingProcedureFactory.persist(
        db_session
    )
    standard_operating_procedure_2 = await StandardOperatingProcedureFactory.persist(
        db_session, default_tenant=False
    )
    # Act / Assert
    assert (
        standard_operating_procedure_1.tenant_id
        != standard_operating_procedure_2.tenant_id
    )
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.check_standard_operating_procedure_exists(
            standard_operating_procedure_1.id, standard_operating_procedure_2.tenant_id
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_check_library_task_exists(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    library_task = await LibraryTaskFactory.persist(db_session)

    # Act / Assert
    await standard_operating_procedure_manager.check_library_task_exists(
        library_task.id
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_check_library_task_not_exists(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    invalid_library_task_id = unique_id_factory()

    # Act / Assert
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.check_library_task_exists(
            invalid_library_task_id
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_many(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedures = (
        await StandardOperatingProcedureFactory.persist_many(db_session, size=4)
    )
    tenant_id = standard_operating_procedures[0].tenant_id

    # Act
    retrieved_standard_operating_procedures = (
        await standard_operating_procedure_manager.get_all(tenant_id)
    )

    assert not any(
        [
            standard_storing_procedure
            for standard_storing_procedure in retrieved_standard_operating_procedures
            if standard_storing_procedure.tenant_id != tenant_id
        ]
    )
    assert all(
        [
            standard_storing_procedure in standard_operating_procedures
            for standard_storing_procedure in standard_operating_procedures
        ]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_many_limit_after(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedures = (
        await StandardOperatingProcedureFactory.persist_many(db_session, size=2)
    )
    tenant_id = standard_operating_procedures[0].tenant_id
    standard_operating_procedures = await standard_operating_procedure_manager.get_all(
        tenant_id, limit=2
    )

    # Act / Assert
    retrieved_standard_operating_procedures = (
        await standard_operating_procedure_manager.get_all(tenant_id, limit=1)
    )

    assert len(retrieved_standard_operating_procedures) == 1
    assert (
        retrieved_standard_operating_procedures[0] == standard_operating_procedures[0]
    )

    retrieved_standard_operating_procedures = (
        await standard_operating_procedure_manager.get_all(
            tenant_id, limit=1, after=retrieved_standard_operating_procedures[0].id
        )
    )
    assert len(retrieved_standard_operating_procedures) == 1
    assert (
        retrieved_standard_operating_procedures[0] == standard_operating_procedures[1]
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_by_id(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )

    # Act
    retrieved_standard_operating_procedure = (
        await standard_operating_procedure_manager.get_by_id(
            standard_operating_procedure.id, standard_operating_procedure.tenant_id
        )
    )

    # Assert
    assert standard_operating_procedure == retrieved_standard_operating_procedure


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_get_by_id_not_found(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange / Act
    retrieved_standard_operating_procedure = (
        await standard_operating_procedure_manager.get_by_id(
            unique_id_factory(), unique_id_factory()
        )
    )

    # Assert
    assert retrieved_standard_operating_procedure is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_delete(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )

    # Act
    await standard_operating_procedure_manager.delete(
        standard_operating_procedure.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )

    # Assert
    standard_operating_procedure_saved = (
        await standard_operating_procedure_manager.get_by_id(
            standard_operating_procedure.id,
            tenant_id=standard_operating_procedure.tenant_id,
        )
    )
    assert standard_operating_procedure_saved is None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_delete_not_found(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    invalid_standard_operating_procedure_id = unique_id_factory()
    invalid_tenant_id = unique_id_factory()

    # Act /
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.delete(
            invalid_standard_operating_procedure_id,
            tenant_id=invalid_tenant_id,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_to_library_task(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )
    library_task = await LibraryTaskFactory.persist(db_session)

    # Act / Assert
    await standard_operating_procedure_manager.link_standard_operating_procedure_to_library_task(
        standard_operating_procedure_id=standard_operating_procedure.id,
        library_task_id=library_task.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )
    # it can be repeated
    await standard_operating_procedure_manager.link_standard_operating_procedure_to_library_task(
        standard_operating_procedure_id=standard_operating_procedure.id,
        library_task_id=library_task.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )
    links = await get_all_library_task_standard_operating_procedures(
        db_session,
        library_task_id=library_task.id,
        standard_operating_procedure_id=standard_operating_procedure.id,
    )
    assert any(links)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_link_to_library_task_not_found(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )
    library_task = await LibraryTaskFactory.persist(db_session)

    # Act / Assert
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.link_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=unique_id_factory(),
            library_task_id=library_task.id,
            tenant_id=standard_operating_procedure.tenant_id,
        )
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.link_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=standard_operating_procedure.id,
            library_task_id=unique_id_factory(),
            tenant_id=standard_operating_procedure.tenant_id,
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_unlink_to_library_task(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )
    library_task = await LibraryTaskFactory.persist(db_session)
    await standard_operating_procedure_manager.link_standard_operating_procedure_to_library_task(
        standard_operating_procedure_id=standard_operating_procedure.id,
        library_task_id=library_task.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )

    # Act / Assert
    await standard_operating_procedure_manager.unlink_standard_operating_procedure_to_library_task(
        standard_operating_procedure_id=standard_operating_procedure.id,
        library_task_id=library_task.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )
    # it can be repeated
    await standard_operating_procedure_manager.unlink_standard_operating_procedure_to_library_task(
        standard_operating_procedure_id=standard_operating_procedure.id,
        library_task_id=library_task.id,
        tenant_id=standard_operating_procedure.tenant_id,
    )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_standard_operating_procedures_unlink_to_library_task_not_found(
    db_session: AsyncSession,
    standard_operating_procedure_manager: StandardOperatingProcedureManager,
) -> None:
    # Arrange
    standard_operating_procedure = await StandardOperatingProcedureFactory.persist(
        db_session
    )
    library_task = await LibraryTaskFactory.persist(db_session)

    # Act / Assert
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.unlink_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=unique_id_factory(),
            library_task_id=library_task.id,
            tenant_id=standard_operating_procedure.tenant_id,
        )
    with pytest.raises(EntityNotFoundException):
        await standard_operating_procedure_manager.unlink_standard_operating_procedure_to_library_task(
            standard_operating_procedure_id=standard_operating_procedure.id,
            library_task_id=unique_id_factory(),
            tenant_id=standard_operating_procedure.tenant_id,
        )
