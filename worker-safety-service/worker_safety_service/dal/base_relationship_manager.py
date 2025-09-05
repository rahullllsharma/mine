import re
from typing import Generic, TypeVar

from _operator import eq
from sqlalchemy import and_, delete
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel

from worker_safety_service import get_logger
from worker_safety_service.dal.crud_manager import (
    ERROR_MSG_PATTERN as DUPLICATED_ENTITY_ERROR_MSG_PATTERN,
)
from worker_safety_service.models import AsyncSession

logger = get_logger(__name__)

T = TypeVar("T", bound=SQLModel)


class BaseRelationshipManager(Generic[T]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entity: T) -> None:
        """
        Adds a new relationship entity.
        Adding an existing entity should not yield an error.
        """
        try:
            async with self.session.begin_nested():
                self.session.add(entity)
        except IntegrityError as ex:
            # Skip the duplicated error
            match = re.search(DUPLICATED_ENTITY_ERROR_MSG_PATTERN, str(ex))
            if not match:
                raise ex

    async def delete(self, entity: T) -> None:
        entity_type = type(entity)
        clauses = [
            eq(getattr(entity_type, fieldname), value)
            for fieldname, value in entity.dict().items()
        ]

        stm = delete(entity_type).where(and_(*clauses))

        async with self.session.begin_nested():
            await self.session.execute(stm)
