import uuid
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlmodel import col, select
from sqlmodel.sql.expression import SelectOfScalar

from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    AsyncSession,
    User,
    UserCreate,
    UserEdit,
    set_item_order_by,
    string_column_for_order_by,
    unique_order_by_fields,
)
from worker_safety_service.types import OrderBy, OrderByDirection
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


def selectWithOptionalTenant(tenant_id: Optional[uuid.UUID]) -> SelectOfScalar[User]:
    if tenant_id:
        return select(User).where(User.tenant_id == tenant_id)
    return select(User)


class UserManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_users(
        self,
        ids: Iterable[uuid.UUID] | None = None,
        role: str | None = None,
        order_by: list[OrderBy] | None = None,
        tenant_id: Optional[uuid.UUID] = None,
        allow_archived: bool = True,
    ) -> list[User]:
        if ids is not None and not ids:
            return []

        statement = selectWithOptionalTenant(tenant_id)
        if ids:
            statement = statement.where(col(User.id).in_(ids))
        if role:
            statement = statement.where(User.role == role)
        if allow_archived is False:
            statement = statement.where(col(User.archived_at).is_(None))

        for order_by_item in unique_order_by_fields(order_by):
            if order_by_item.field == "name":
                column = string_column_for_order_by(func.ltrim(User.get_name_sql()))
                if order_by_item.direction == OrderByDirection.DESC:
                    column = column.desc()
                statement = statement.order_by(column)
            else:
                statement = set_item_order_by(statement, User, order_by_item)

        return (await self.session.exec(statement)).all()

    async def get_users_by_id(
        self,
        ids: Iterable[uuid.UUID],
        tenant_id: Optional[uuid.UUID] = None,
        allow_archived: bool = True,
    ) -> dict[uuid.UUID, User]:
        return {
            i.id: i
            for i in await self.get_users(
                ids=ids, tenant_id=tenant_id, allow_archived=allow_archived
            )
        }

    async def get_by_keycloak_id(
        self, keycloak_id: str | uuid.UUID, tenant_id: uuid.UUID
    ) -> User | None:
        """
        Retrieve a user by its keycloak_id
        """
        statement = (
            select(User)
            .where(User.keycloak_id == keycloak_id)
            .where(User.tenant_id == tenant_id)
        )
        return (await self.session.exec(statement)).first()

    async def get_by_email(
        self, email: str, tenant_id: Optional[uuid.UUID] = None
    ) -> User | None:
        statement = select(User).where(User.email == email)
        if tenant_id:
            statement = statement.where(User.tenant_id == tenant_id)
        return (await self.session.exec(statement)).first()

    async def create(self, user: UserCreate) -> User:
        db_user = User.from_orm(user)
        self.session.add(db_user)
        await self.session.commit()
        logger.info(
            "User created",
            user_id=str(db_user.id),
            keycloak_id=str(db_user.keycloak_id),
        )
        return db_user

    async def get_or_create(
        self, keycloak_id: str | uuid.UUID, tenant_id: uuid.UUID, user: UserCreate
    ) -> tuple[User, bool]:
        """
        Returns an existing user by keycloak_id, if it doesn't exist creates it.
        NOTE: user existance is checked by catchin sqlalchemy.exc.IntegrityError to prevent
              race conditions between 2 requests that create a user
        """
        created = False
        db_user = await self.get_by_keycloak_id(keycloak_id, tenant_id)
        if not db_user:
            try:
                db_user = await self.create(user)
                created = True
            except IntegrityError as e:
                # rollback previously thrown create call
                await self.session.rollback()
                if any("users_tenant_keycloak_idx" in arg for arg in e.args):
                    db_user = await self.get_by_keycloak_id(keycloak_id, tenant_id)
                else:
                    raise e
            assert db_user is not None

        return db_user, created

    async def edit(self, db_user: User, user: UserEdit) -> User:
        updated: bool = False

        for key, value in user.dict().items():
            if getattr(db_user, key) != value:
                setattr(db_user, key, value)
                updated = True

        if updated:
            await self.session.commit()
            logger.info("User updated", user_id=str(db_user.id))

        return db_user

    async def archive_user(self, user_id: uuid.UUID) -> bool:
        user_list = await self.get_users_by_id(ids=[user_id])
        user_to_be_archived = user_list.get(user_id)

        if not user_to_be_archived:
            raise ResourceReferenceException(f"No user found with id - {id}")

        user_to_be_archived.archived_at = datetime.now(timezone.utc)
        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            raise db_err

        return True

    async def update_external_id(self, user_id: uuid.UUID, external_id: str) -> bool:
        users = await self.get_users_by_id([user_id])
        user_to_be_updated = users.get(user_id)
        if not user_to_be_updated:
            raise ResourceReferenceException(f"No user found with id - {id}")

        user_to_be_updated.external_id = external_id
        try:
            await self.session.commit()
        except DBAPIError as db_err:
            await self.session.rollback()
            raise db_err

        return True
