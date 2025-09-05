import uuid

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.user import UserManager
from worker_safety_service.models import User
from worker_safety_service.types import OrderBy


class TenantUsersLoader:
    def __init__(self, manager: UserManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.me = DataLoader(load_fn=self.load_users)
        self.__manager = manager

    async def load_users(
        self, ids: list[uuid.UUID], allow_archived: bool = True
    ) -> list[User | None]:
        items = await self.__manager.get_users_by_id(
            ids=ids, tenant_id=self.tenant_id, allow_archived=allow_archived
        )
        return [items.get(i) for i in ids]

    async def by_role(
        self,
        role: str,
        order_by: list[OrderBy] | None = None,
        allow_archived: bool = True,
    ) -> list[User]:
        return await self.__manager.get_users(
            role=role,
            order_by=order_by,
            tenant_id=self.tenant_id,
            allow_archived=allow_archived,
        )
