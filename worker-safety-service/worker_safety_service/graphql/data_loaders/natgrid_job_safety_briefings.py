import uuid
from typing import Optional, Union

from strawberry.dataloader import DataLoader

from worker_safety_service.dal.natgrid_jsb import NatGridJobSafetyBriefingManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    NatGridJobSafetyBriefing,
    NatGridJobSafetyBriefingLayout,
    User,
)
from worker_safety_service.models.concepts import FormStatus


class TenantNatGridJobSafetyBriefingLoader:
    def __init__(
        self,
        manager: NatGridJobSafetyBriefingManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.with_work_location = DataLoader(
            load_fn=self.get_work_location_on_natgrid_jsb_id
        )
        self.with_multiple_work_locations = DataLoader(
            load_fn=self.get_multiple_work_locations_on_natgrid_jsb_id
        )
        self.with_barn_locations = DataLoader(
            load_fn=self.get_barn_location_on_natgrid_jsb_id
        )

    async def get_natgrid_job_safety_briefing(
        self, id: uuid.UUID, allow_archived: bool | None = True
    ) -> NatGridJobSafetyBriefing:
        assert allow_archived is not None
        jsb = await self.__manager.get_by_id(
            id, allow_archived=allow_archived, tenant_id=self.tenant_id
        )
        if jsb is None:
            raise ResourceReferenceException("NG Job Safety Briefing not found")
        return jsb

    async def get_natgrid_job_safety_briefings_by_user_id(
        self,
        user_id: uuid.UUID,
        limit: Optional[int],
        allow_archived: bool | None = True,
    ) -> list[tuple[uuid.UUID, Optional[dict]]]:
        assert allow_archived is not None
        return await self.__manager.get_by_user_id(
            user_id=user_id, allow_archived=allow_archived, limit=limit
        )

    async def get_last_natgrid_job_safety_briefing_by_user_id(
        self,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        allow_archived: bool | None = True,
    ) -> NatGridJobSafetyBriefing:
        ng_jsb = await self.__manager.get_last_natgrid_jsb_by_user_id(
            user_id=user_id,
            allow_archived=allow_archived,
            tenant_id=tenant_id,
        )
        if ng_jsb is None:
            raise ResourceReferenceException("NG Job Safety Briefing not found")
        return ng_jsb

    async def save_natgrid_job_safety_briefing(
        self,
        actor: User,
        data: NatGridJobSafetyBriefingLayout,
        form_status: FormStatus | None,
        work_type_id: uuid.UUID | None,
    ) -> NatGridJobSafetyBriefing:
        return await self.__manager.save(
            data=data,
            actor=actor,
            tenant_id=self.tenant_id,
            form_status=form_status,
            work_type_id=work_type_id,
        )

    async def reopen_natgrid_job_safety_briefing(
        self, jsb_id: uuid.UUID, user: User
    ) -> NatGridJobSafetyBriefing:
        return await self.__manager.reopen_natgrid_jsb(jsb_id, actor=user)

    async def archive_natgrid_job_safety_briefing(
        self, jsb_id: uuid.UUID, user: User
    ) -> None:
        await self.__manager.archive(jsb_id, user, tenant_id=self.tenant_id)

    async def get_work_location_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[Union[str, None, dict]]:
        jsbs = await self.__manager.get_work_locations_on_natgrid_jsb_id(
            jsb_ids=jsb_ids
        )
        items: dict[uuid.UUID, Union[str, None, dict]] = {i[0]: i[1] for i in jsbs}
        return [items.get(i) for i in jsb_ids]

    async def get_multiple_work_locations_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[Union[str, None, dict, list]]:
        jsbs = await self.__manager.get_multiple_work_locations_on_natgrid_jsb_id(
            jsb_ids=jsb_ids
        )
        items: dict[uuid.UUID, Union[str, None, dict]] = {i[0]: i[1] for i in jsbs}
        return [items.get(i) for i in jsb_ids]

    async def get_barn_location_on_natgrid_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[Union[str, None, dict]]:
        jsbs = await self.__manager.get_barn_location_on_natgrid_jsb_id(jsb_ids=jsb_ids)
        items: dict[uuid.UUID, str] = {i[0]: i[1] for i in jsbs}
        return [items.get(i) for i in jsb_ids]
