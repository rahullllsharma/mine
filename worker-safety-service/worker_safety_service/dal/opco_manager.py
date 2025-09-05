from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlmodel import col, select

from worker_safety_service.dal.crud_manager import CRUDManager
from worker_safety_service.models import (
    AsyncSession,
    Opco,
    OpcoCreate,
    OpcoDelete,
    User,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class OpcoManager(CRUDManager[Opco]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=Opco)

    async def create_opco(self, input: OpcoCreate) -> Opco:
        # create the new opco
        opco_instance = Opco(**input.dict())
        await self.create(opco_instance)

        return opco_instance

    async def get_opco_by_name(self, tenant_id: UUID, name: str) -> Opco | None:
        query = (
            select(Opco)
            .where(Opco.tenant_id == tenant_id)
            .where(Opco.full_name == name)
        )

        return (await self.session.exec(query)).first()

    async def get_opcos_by_user_id(
        self, tenant_id: UUID, user_ids: list[UUID]
    ) -> dict[UUID, Opco]:
        query = (
            select(Opco, User.id)
            .where(Opco.id == User.opco_id)
            .where(Opco.tenant_id == tenant_id)
            .where(col(User.id).in_(user_ids))
        )

        opco_data = (await self.session.exec(query)).all()

        return {user_id: opco for opco, user_id in opco_data}

    async def get_all_opco(
        self,
        tenant_id: UUID,
        opco_ids: Optional[list[UUID]] = None,
        limit: Optional[int] = None,
        after: Optional[UUID] = None,
    ) -> list[Opco]:
        query = select(Opco).where(Opco.tenant_id == tenant_id)

        if opco_ids is not None:
            query = query.where(col(Opco.id).in_(opco_ids))
        if after is not None:
            after_opco = await self.get_by_id(after)
            if after_opco is not None:
                query = query.where(Opco.created_at > after_opco.created_at)
        if limit:
            query = query.limit(limit)

        opcos = await self.session.exec(query.order_by(Opco.name))

        return opcos.all()

    async def edit_opco(self, opco: Opco) -> Optional[Opco]:
        await super().update(opco)

        return await self.get_by_id(opco.id)

    async def delete_opco(self, id: UUID) -> OpcoDelete:
        query = select(func.count()).select_from(Opco).where(Opco.parent_id == id)  # type: ignore
        subopco_count = (await self.session.exec(query)).one()

        if subopco_count != 0:
            return OpcoDelete(error="sub_opco found, can't be deleted")
        else:
            await super().delete(id)
            return OpcoDelete(error=None)
