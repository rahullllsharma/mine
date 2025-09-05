import datetime
import uuid
from abc import ABC
from typing import Any, Generic, TypeVar, cast

from sqlalchemy.sql.operators import is_
from sqlmodel import SQLModel, select

from worker_safety_service import get_logger
from worker_safety_service.audit_trail import audit_archive, audit_create, audit_update
from worker_safety_service.dal.audit_events import AuditContext
from worker_safety_service.dal.exceptions.entity_not_found import (
    EntityNotFoundException,
)
from worker_safety_service.models import (
    AsyncSession,
    AuditEventType,
    AuditObjectType,
    User,
)

logger = get_logger(__name__)

T = TypeVar("T", bound=SQLModel)


class CRUAAuditableManager(ABC, Generic[T]):
    def __init__(
        self,
        session: AsyncSession,
        entity_type: type[T],
        audit_object_type: AuditObjectType,
    ):
        super().__init__()
        self.session = session
        self._entity_type = entity_type
        self._audit_object_type = audit_object_type

    # TODO This is becoming a lot like `CRUDManager` - can we merge them?
    async def get_by_id(
        self,
        entity_id: uuid.UUID,
        allow_archived: bool = True,
        tenant_id: uuid.UUID | None = None,
    ) -> T | None:
        stm = select(self._entity_type).where(
            getattr(self._entity_type, "id") == entity_id
        )

        if tenant_id is not None:
            stm = stm.where(getattr(self._entity_type, "tenant_id") == tenant_id)

        if hasattr(self._entity_type, "archived_at") and not allow_archived:
            stm = stm.where(is_(getattr(self._entity_type, "archived_at"), None))

        r = await self.session.execute(stm)
        return r.scalar_one_or_none()

    async def get_all(
        self,
        allow_archived: bool = False,
        tenant_id: uuid.UUID | None = None,
        start_date: datetime.datetime | None = None,
        end_date: datetime.datetime | None = None,
        skip: int | None = None,
        limit: int = 50,
        initial_load: bool = False,
    ) -> list[T]:
        stm = select(self._entity_type)

        if tenant_id is not None:
            stm = stm.where(getattr(self._entity_type, "tenant_id") == tenant_id)

        if hasattr(self._entity_type, "archived_at") and not allow_archived:
            stm = stm.where(is_(getattr(self._entity_type, "archived_at"), None))

        if start_date:
            stm = stm.where(getattr(self._entity_type, "updated_at") >= start_date)
        if end_date:
            stm = stm.where(getattr(self._entity_type, "updated_at") <= end_date)

        if hasattr(self._entity_type, "updated_at"):
            stm = stm.order_by(getattr(self._entity_type, "updated_at").desc())

        if skip is not None:
            stm = stm.offset(skip)
        if limit and not initial_load:
            stm = stm.limit(limit)

        result = await self.session.execute(stm)
        entities = result.scalars().all()
        return cast(list[T], entities)

    @audit_create
    async def create(self, entity: T, actor: User, **kwargs: Any) -> T:
        with AuditContext(self.session) as audit_context:
            self.session.add(entity)
            audit_event_type = AuditEventType[self._audit_object_type.name + "_created"]
            await audit_context.create(audit_event_type, actor)
            await self.session.commit()

            return entity

    @audit_update
    async def update(self, entity: T, actor: User, **kwargs: Any) -> T:
        with AuditContext(self.session) as audit_context:
            audit_event_type = AuditEventType[self._audit_object_type.name + "_updated"]
            await audit_context.create(audit_event_type, actor)
            await self.session.commit()

            return entity

    @audit_archive
    async def archive(
        self,
        entity_id: uuid.UUID,
        actor: User,
        tenant_id: uuid.UUID | None = None,
        **kwargs: Any,
    ) -> T:
        entity = await self.get_by_id(
            entity_id=entity_id, allow_archived=False, tenant_id=tenant_id
        )

        if entity is None:
            raise EntityNotFoundException(entity_id, self._entity_type)

        if getattr(entity, "archived_at") is not None:
            raise ValueError(f"Entity {entity_id} is already archived")

        archived_at = datetime.datetime.now(datetime.timezone.utc)
        updated_at = datetime.datetime.now(datetime.timezone.utc)

        with AuditContext(self.session) as audit_context:
            setattr(entity, "archived_at", archived_at)
            setattr(entity, "updated_at", updated_at)
            audit_event_type = AuditEventType[
                self._audit_object_type.name + "_archived"
            ]

            await audit_context.create(audit_event_type, actor)
            await self.session.commit()

            return entity

    async def unarchive(self, entity_id: uuid.UUID) -> None:
        raise NotImplementedError()
