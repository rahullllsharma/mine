import uuid

from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from worker_safety_service.dal.base_relationship_manager import BaseRelationshipManager
from worker_safety_service.dal.crud_manager import CRUDManager
from worker_safety_service.dal.exceptions.entity_in_use import EntityInUseException
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.models import AsyncSession, StandardOperatingProcedure
from worker_safety_service.models.library import LibraryTask
from worker_safety_service.models.standard_operating_procedures import (
    LibraryTaskStandardOperatingProcedure,
)


class StandardOperatingProcedureManager(CRUDManager[StandardOperatingProcedure]):
    def __init__(self, session: AsyncSession):
        super().__init__(
            session, StandardOperatingProcedure, immutable_fields=["id", "tenant_id"]
        )
        self._relationship_manager: BaseRelationshipManager[
            LibraryTaskStandardOperatingProcedure
        ] = BaseRelationshipManager(session)

    async def check_standard_operating_procedure_exists(
        self, id: uuid.UUID, tenant_id: uuid.UUID
    ) -> None:
        existing_tasks = await self.get_by_id(id, tenant_id)
        if not existing_tasks:
            raise EntityNotFoundException(id, StandardOperatingProcedure)

    async def check_library_task_exists(self, id: uuid.UUID) -> None:
        statement = select(LibraryTask).where(LibraryTask.id == id)
        library_task = (await self.session.execute(statement)).scalar_one_or_none()
        if not library_task:
            raise EntityNotFoundException(id, LibraryTask)

    async def get_all(  # type: ignore
        self,
        tenant_id: uuid.UUID,
        after: uuid.UUID | None = None,
        limit: int | None = None,
    ) -> list[StandardOperatingProcedure]:
        statement = select(StandardOperatingProcedure).where(
            StandardOperatingProcedure.tenant_id == tenant_id
        )
        if after:
            statement = statement.where(StandardOperatingProcedure.id > after)
        if limit:
            statement = statement.limit(limit)
        statement = statement.order_by(StandardOperatingProcedure.id)
        return (await self.session.exec(statement)).all()

    async def get_by_id(  # type: ignore
        self, id: uuid.UUID, tenant_id: uuid.UUID
    ) -> StandardOperatingProcedure | None:
        statement = (
            select(StandardOperatingProcedure)
            .where(StandardOperatingProcedure.id == id)
            .where(StandardOperatingProcedure.tenant_id == tenant_id)
        )
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def delete(self, id: uuid.UUID, tenant_id: uuid.UUID) -> None:  # type: ignore
        await self.check_standard_operating_procedure_exists(id, tenant_id)
        statement = (
            delete(StandardOperatingProcedure)
            .where(StandardOperatingProcedure.id == id)
            .where(StandardOperatingProcedure.tenant_id == tenant_id)
        )

        try:
            async with self.session.begin_nested():
                await self.session.execute(statement)
        except IntegrityError:
            raise EntityInUseException(id)

    async def link_standard_operating_procedure_to_library_task(
        self,
        standard_operating_procedure_id: uuid.UUID,
        library_task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> None:
        await self.check_standard_operating_procedure_exists(
            standard_operating_procedure_id, tenant_id
        )
        await self.check_library_task_exists(library_task_id)
        link = LibraryTaskStandardOperatingProcedure(
            standard_operating_procedure_id=standard_operating_procedure_id,
            library_task_id=library_task_id,
        )
        await self._relationship_manager.create(link)

    async def unlink_standard_operating_procedure_to_library_task(
        self,
        standard_operating_procedure_id: uuid.UUID,
        library_task_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> None:
        await self.check_standard_operating_procedure_exists(
            standard_operating_procedure_id, tenant_id
        )
        await self.check_library_task_exists(library_task_id)
        link = LibraryTaskStandardOperatingProcedure(
            standard_operating_procedure_id=standard_operating_procedure_id,
            library_task_id=library_task_id,
        )
        await self._relationship_manager.delete(link)

    async def get_standard_operating_procedures_by_library_task(
        self, library_task_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[StandardOperatingProcedure]:
        statement = (
            select(StandardOperatingProcedure)
            .join(
                LibraryTaskStandardOperatingProcedure,
                onclause=LibraryTaskStandardOperatingProcedure.standard_operating_procedure_id
                == StandardOperatingProcedure.id,
            )
            .where(
                LibraryTaskStandardOperatingProcedure.library_task_id == library_task_id
            )
            .where(StandardOperatingProcedure.tenant_id == tenant_id)
        )
        return (await self.session.exec(statement)).all()
