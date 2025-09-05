import re
import uuid
from abc import ABC
from typing import Any, Generic, TypeVar, cast

from _operator import eq
from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.operators import is_
from sqlmodel import SQLModel

from worker_safety_service import get_logger
from worker_safety_service.dal.exceptions.could_not_perform_update import (
    CouldNotPerformUpdateException,
)
from worker_safety_service.dal.exceptions.entity_already_exists import (
    EntityAlreadyExistsException,
)
from worker_safety_service.dal.exceptions.entity_in_use import EntityInUseException
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.models import AsyncSession
from worker_safety_service.models.utils import db_default_utcnow

logger = get_logger(__name__)

ERROR_MSG_PATTERN = r"duplicate key value violates unique constraint \"(\S+)\""

T = TypeVar("T", bound=SQLModel)


class CRUDManager(ABC, Generic[T]):
    """
    CRUD -> Create, Read, Update, Delete
    """

    def __init__(
        self,
        session: AsyncSession,
        entity_type: type[T],
        immutable_fields: list[str] | None = None,
    ) -> None:
        super().__init__()
        self.session = session
        self._entity_type = entity_type
        self._immutable_fields = immutable_fields or ["id"]

    async def _convert_constaintname_to_fieldname(self, constraint_name: str) -> str:
        return "id"

    async def get_by_id(
        self, entity_id: uuid.UUID, allow_archived: bool = False
    ) -> T | None:
        stm = select(self._entity_type).where(
            getattr(self._entity_type, "id") == entity_id
        )

        if hasattr(self._entity_type, "archived_at") and not allow_archived:
            stm = stm.where(is_(getattr(self._entity_type, "archived_at"), None))

        r = await self.session.execute(stm)
        return r.scalar_one_or_none()

    async def create(self, entity: T) -> T:
        """
        Adds a new Entity.
        """
        try:
            self.session.add(entity)
            await self.session.commit()
            await self.session.refresh(entity)
            return entity
        except IntegrityError as ex:
            await self.session.rollback()
            match = re.search(ERROR_MSG_PATTERN, str(ex))
            if match:
                constraint_name = match.group(1)
                field_name = await self._convert_constaintname_to_fieldname(
                    constraint_name
                )
                raise EntityAlreadyExistsException(field_name)
            else:
                raise ex
        except Exception as e:
            await self.session.rollback()
            logger.exception("unknown error occurred while committing to db")
            raise e

    async def update(self, entity: T) -> None:
        """
        Updates some properties of a given entity.
        Only mutable fields can be updated.
        An error will be thrown if the user tries to change immutable fields.

        You also are not able to update archived entities.
        """
        if (
            hasattr(self._entity_type, "archived_at")
            and getattr(entity, "archived_at") is not None
        ):
            raise RuntimeError("Cannot update archived tasks.")

        entity_type = type(entity)
        clauses = [
            eq(getattr(entity_type, fieldname), getattr(entity, fieldname))
            for fieldname in self._immutable_fields
        ]
        if hasattr(entity_type, "archived_at"):
            clauses.append(is_(getattr(entity_type, "archived_at"), None))

        if hasattr(entity_type, "updated_at"):
            entity.updated_at = db_default_utcnow()

        excluded_immutable_fields = {*self._immutable_fields, "archived_at"}
        stm = (
            update(entity_type)
            .where(and_(*clauses))
            .values(**entity.dict(exclude=excluded_immutable_fields))
            .returning("*")
        )

        rc: int | None = None
        async with self.session.begin_nested():
            result = await self.session.execute(stm)
            rc = getattr(result, "rowcount")

        if rc != 1:
            # TODO: Check if we can give a better error message. It will probably complicate the query.
            raise CouldNotPerformUpdateException(excluded_immutable_fields)

    async def delete(self, entity_id: uuid.UUID) -> None:
        """
        Delete and entity by id.
        """

        stm = delete(self._entity_type).where(
            getattr(self._entity_type, "id") == entity_id
        )

        try:
            async with self.session.begin_nested():
                await self.session.execute(stm)
        except IntegrityError:
            raise EntityInUseException(entity_id)

    async def _assert_entity_exists(self, entity_id: uuid.UUID) -> None:
        existing_tasks = await self.get_by_id(entity_id, allow_archived=True)
        if not existing_tasks:
            raise EntityNotFoundException(entity_id, self._entity_type)

    async def get_all(
        self,
        limit: int | None = None,
        order_by_attribute: str | None = "id",
        additional_where_clause: list[Any] | None = None,
    ) -> list[T]:
        query = select(self._entity_type)

        if additional_where_clause:
            query = query.where(and_(*additional_where_clause))
        if limit:
            query = query.limit(limit)
        if order_by_attribute:
            query = query.order_by(getattr(self._entity_type, order_by_attribute))

        result = await self.session.exec(query)  # type:ignore
        entities = result.scalars().all()
        return cast(list[T], entities)
