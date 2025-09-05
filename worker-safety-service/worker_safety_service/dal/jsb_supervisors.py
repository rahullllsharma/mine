from typing import Any, Optional
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy import select as sa_select
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import col, select

from worker_safety_service.models import AsyncSession
from worker_safety_service.models.concepts import CrewInformation
from worker_safety_service.models.forms import JobSafetyBriefing
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink
from worker_safety_service.models.tenants import WorkOS
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class JSBSupervisorsManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_jsb_supervisors(
        self,
        limit: Optional[int] = None,
        offset: int | None = None,
    ) -> list[JSBSupervisorLink]:
        query = select(JSBSupervisorLink).distinct(JSBSupervisorLink.manager_id)
        if limit:
            query = query.limit(max(1, limit)).offset(max(0, offset or 0))
        results = await self.session.exec(query)
        return results.all()

    async def get_jsb_supervisors_by_jsb_ids(
        self,
        jsb_ids: list[UUID],
    ) -> dict[UUID, Optional[list[JSBSupervisorLink]]]:
        query = select(JSBSupervisorLink).where(
            col(JSBSupervisorLink.jsb_id).in_(jsb_ids)
        )
        results = await self.session.exec(query)
        result_list = results.all()

        result_dict: dict[UUID, list[JSBSupervisorLink]] = {}
        for row in result_list:
            if row.jsb_id not in result_dict:
                result_dict[row.jsb_id] = []
            result_dict[row.jsb_id].append(row)

        return {jsb_id: result_dict.get(jsb_id) for jsb_id in jsb_ids}

    async def update_supervisor_jsb_data(
        self, jsb_id: UUID, crew_infos: list[CrewInformation]
    ) -> None:
        input_data = []
        contains_other = False
        unique_manager_ids = set()
        for crew_info in crew_infos:
            if crew_info.type and str(crew_info.type.value).lower().strip() == "other":
                contains_other = True
            manager_id = crew_info.manager_id
            if manager_id and manager_id not in unique_manager_ids:
                input_data.append(
                    {
                        "jsb_id": jsb_id,
                        "manager_id": manager_id,
                        "manager_email": crew_info.manager_email,
                        "manager_name": crew_info.manager_name,
                    }
                )
                unique_manager_ids.add(manager_id)

        # This is required to ensure no new data including "Other" type crew is added if request
        # data is empty
        if not input_data and not contains_other:
            return

        # For storing the details of supervisors we are deleting all existing supervisors for a JSB
        # and then reinserted with the data received in payload. This approach is taken to support offline mode in mobile app.
        delete_query = delete(JSBSupervisorLink).where(
            JSBSupervisorLink.jsb_id == jsb_id
        )
        await self.session.execute(delete_query)
        await self.session.commit()

        # This is required for the scenario where "Other" type crew is added and no workos crew is there
        # to ensure any linked supervisors get deleted from jsb linking
        if not input_data and contains_other:
            return

        stmt = insert(JSBSupervisorLink).values(input_data)
        # on_conflict_do_update will update the manager_name and manager_email values if the constraint is matched.
        # For more details on understanding on_conflict_do_update see below links
        # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#postgresql-insert-on-conflict
        # https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#sqlalchemy.dialects.postgresql.Insert.on_conflict_do_update
        stmt = stmt.on_conflict_do_update(
            constraint="jsb_id_supervisor_id_contraint_unique",
            set_={
                "manager_email": stmt.excluded.manager_email,
                "manager_name": stmt.excluded.manager_name,
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def get_jsb_supervisors_without_crew(
        self,
    ) -> list[Any]:
        query = (
            sa_select(
                JSBSupervisorLink.jsb_id,
                JSBSupervisorLink.manager_id,
                JobSafetyBriefing.contents,
                JobSafetyBriefing.tenant_id,
                WorkOS.workos_directory_id,
            )
            .join(JobSafetyBriefing, JSBSupervisorLink.jsb_id == JobSafetyBriefing.id)
            .join(WorkOS, JobSafetyBriefing.tenant_id == WorkOS.tenant_id)
        )
        results = await self.session.exec(query)  # type: ignore
        return results.all()  # type: ignore

    async def delete_jsb_supervisors_by_jsb_id_and_manager_id(
        self, jsb_id: str, manager_id: str
    ) -> int:
        query = delete(JSBSupervisorLink).where(
            JSBSupervisorLink.jsb_id == jsb_id,
            JSBSupervisorLink.manager_id == manager_id,
        )
        results = await self.session.exec(query)  # type: ignore
        return results.rowcount  # type: ignore
