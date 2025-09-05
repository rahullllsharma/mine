import uuid
from typing import Union

from fastapi.encoders import jsonable_encoder
from strawberry.dataloader import DataLoader

from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.exceptions import ResourceReferenceException
from worker_safety_service.models import (
    JobSafetyBriefing,
    JobSafetyBriefingLayout,
    User,
)


class TenantJobSafetyBriefingLoader:
    def __init__(
        self,
        manager: JobSafetyBriefingManager,
        tenant_id: uuid.UUID,
    ):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.with_work_location = DataLoader(load_fn=self.get_work_location_on_jsb_id)

    async def get_job_safety_briefing(
        self, id: uuid.UUID, allow_archived: bool | None = True
    ) -> JobSafetyBriefing:
        assert allow_archived is not None
        jsb = await self.__manager.get_by_id(
            id, allow_archived=allow_archived, tenant_id=self.tenant_id
        )
        if jsb is None:
            raise ResourceReferenceException("Job Safety Briefing not found")
        return jsb

    async def save_job_safety_briefing(
        self,
        actor: User,
        data: JobSafetyBriefingLayout,
        token: str | None = None,
    ) -> JobSafetyBriefing:
        return await self.__manager.save(
            data=data, actor=actor, tenant_id=self.tenant_id, token=token
        )

    async def complete_job_safety_briefing(
        self,
        actor: User,
        data: JobSafetyBriefingLayout,
        token: str | None = None,
    ) -> JobSafetyBriefing:
        return await self.__manager.complete(
            tenant_id=self.tenant_id,
            actor=actor,
            data=data,
            token=token,
        )

    async def reopen_job_safety_briefing(
        self, jsb_id: uuid.UUID, user: User, token: str | None = None
    ) -> JobSafetyBriefing:
        return await self.__manager.reopen(jsb_id, actor=user, token=token)

    async def archive_job_safety_briefing(
        self, jsb_id: uuid.UUID, user: User, token: str | None = None
    ) -> None:
        await self.__manager.archive(
            entity_id=jsb_id, actor=user, tenant_id=self.tenant_id, token=token
        )

    async def get_last_adhoc_jsb(self, actor: User) -> JobSafetyBriefing:
        emergency_contacts = None
        aed_information = None
        work_location = None
        nearest_medical_facility = None
        last_added_jsb_on_user: JobSafetyBriefing | None = (
            await self.__manager.get_last_adhoc_jsb(
                tenant_id=self.tenant_id, actor=actor, allowed_archived=False
            )
        )
        if (
            last_added_jsb_on_user is not None
            and last_added_jsb_on_user.contents is not None
        ):
            emergency_contacts = last_added_jsb_on_user.contents.get(
                "emergency_contacts"
            )
            aed_information = last_added_jsb_on_user.contents.get("aed_information")
            work_location = last_added_jsb_on_user.contents.get("work_location")
            nearest_medical_facility = last_added_jsb_on_user.contents.get(
                "nearest_medical_facility"
            )

        last_jsb_layout = JobSafetyBriefingLayout(
            emergency_contacts=emergency_contacts,
            nearest_medical_facility=nearest_medical_facility,
            aed_information=aed_information,
            work_location=work_location,
        )
        encoded_data = jsonable_encoder(last_jsb_layout)

        new_jsb = JobSafetyBriefing(contents=encoded_data)
        return new_jsb

    async def get_last_jsb(
        self,
        actor: User,
        project_location_id: uuid.UUID | None = None,
    ) -> JobSafetyBriefing | None:
        emergency_contacts = None
        aed_information = None
        work_location = None
        nearest_medical_facility = None

        if project_location_id is not None:
            last_added_jsb_on_project_loc: JobSafetyBriefing | None = (
                await self.__manager.get_last_jsb_on_project_loc(
                    tenant_id=self.tenant_id,
                    project_location_id=project_location_id,
                    allowed_archived=False,
                )
            )
            if (
                last_added_jsb_on_project_loc is not None
                and last_added_jsb_on_project_loc.contents is not None
            ):
                work_location = last_added_jsb_on_project_loc.contents.get(
                    "work_location"
                )
                nearest_medical_facility = last_added_jsb_on_project_loc.contents.get(
                    "nearest_medical_facility"
                )

        last_added_jsb_on_user: JobSafetyBriefing | None = (
            await self.__manager.get_last_jsb_on_user_id(
                tenant_id=self.tenant_id, actor=actor, allowed_archived=False
            )
        )

        if (
            last_added_jsb_on_user is not None
            and last_added_jsb_on_user.contents is not None
        ):
            emergency_contacts = last_added_jsb_on_user.contents.get(
                "emergency_contacts"
            )
            aed_information = last_added_jsb_on_user.contents.get("aed_information")

        last_jsb_layout = JobSafetyBriefingLayout(
            emergency_contacts=emergency_contacts,
            nearest_medical_facility=nearest_medical_facility,
            aed_information=aed_information,
            work_location=work_location,
        )
        encoded_data = jsonable_encoder(last_jsb_layout)

        new_jsb = JobSafetyBriefing(
            contents=encoded_data,
        )

        return new_jsb

    async def get_work_location_on_jsb_id(
        self, jsb_ids: list[uuid.UUID]
    ) -> list[Union[str, None, dict]]:
        jsbs = await self.__manager.get_work_locations_on_jsb_id(jsb_ids=jsb_ids)
        items: dict[uuid.UUID, Union[str, None, dict]] = {i[0]: i[1] for i in jsbs}
        return [items.get(i) for i in jsb_ids]
