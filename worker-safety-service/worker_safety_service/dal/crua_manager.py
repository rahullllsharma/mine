import uuid
from typing import TypeVar

import pendulum
from sqlalchemy import update
from sqlalchemy.sql.operators import is_, is_not
from sqlmodel import SQLModel

from worker_safety_service import get_logger
from worker_safety_service.dal.crud_manager import CRUDManager

logger = get_logger(__name__)

T = TypeVar("T", bound=SQLModel)


class CRUAManager(CRUDManager[T]):
    """
    CRUA -> Create, Read, Update, Archive
    """

    async def delete(self, entity_id: uuid.UUID) -> None:
        raise NotImplementedError()

    async def archive(self, entity_id: uuid.UUID) -> None:
        """
        Archives an entity.
        """
        _datetime = pendulum.now(pendulum.UTC)
        stm = (
            update(self._entity_type)
            .where(getattr(self._entity_type, "id") == entity_id)
            .where(is_(getattr(self._entity_type, "archived_at"), None))
            .values(archived_at=_datetime)
            .returning("*")
        )

        async with self.session.begin_nested():
            result = await self.session.execute(stm)
            rc = getattr(result, "rowcount")

        # Check if we need to throw a entity not found exception
        if rc != 1:
            await self._assert_entity_exists(entity_id)

    async def unarchive(self, entity_id: uuid.UUID) -> None:
        """
        Bring an archived entity back to business.
        """
        stm = (
            update(self._entity_type)
            .where(getattr(self._entity_type, "id") == entity_id)
            .where(is_not(getattr(self._entity_type, "archived_at"), None))
            .values(archived_at=None)
            .returning("*")
        )

        async with self.session.begin_nested():
            result = await self.session.execute(stm)
            rc = getattr(result, "rowcount")

        # Check if we need to throw a entity not found exception
        if rc != 1:
            await self._assert_entity_exists(entity_id)
