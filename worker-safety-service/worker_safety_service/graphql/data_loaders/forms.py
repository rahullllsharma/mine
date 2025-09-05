import datetime
from typing import Optional
from uuid import UUID

from worker_safety_service.dal.forms import Form, FormsManager
from worker_safety_service.models import FormDefinition, FormStatus, OrderBy


class TenantFormLoader:
    def __init__(self, manager: FormsManager, tenant_id: UUID):
        self.tenant_id = tenant_id
        self.__manager = manager

    async def get_form_definitions(self) -> list[FormDefinition]:
        return await self.__manager.get_form_definitions(self.tenant_id)

    async def get_forms(
        self,
        form_name: Optional[list[str]] = None,
        form_id: Optional[list[str]] = None,
        form_status: Optional[list[FormStatus]] = None,
        project_ids: list[UUID] | None = None,
        location_ids: list[UUID] | None = None,
        created_by_ids: list[UUID] | None = None,
        updated_by_ids: list[UUID] | None = None,
        start_created_at: Optional[datetime.date] = None,
        end_created_at: Optional[datetime.date] = None,
        start_updated_at: Optional[datetime.date] = None,
        end_updated_at: Optional[datetime.date] = None,
        order_by: Optional[list[OrderBy]] = None,
        limit: int | None = None,
        offset: int | None = None,
        search: Optional[str] = None,
        filter_search: Optional[dict] = None,
        ad_hoc: bool = False,
        with_archived: bool = False,
        with_contents: bool = False,
        start_completed_at: Optional[datetime.date] = None,
        end_completed_at: Optional[datetime.date] = None,
        start_report_date: Optional[datetime.date] = None,
        end_report_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        operating_region_names: Optional[list[str]] = None,
        manager_ids: Optional[list[str]] | None = None,
    ) -> list[tuple[Form, Optional[str]]]:
        return await self.__manager.get_forms(
            form_name=form_name,
            form_id=form_id,
            form_status=form_status,
            project_ids=project_ids,
            location_ids=location_ids,
            created_by_ids=created_by_ids,
            updated_by_ids=updated_by_ids,
            start_created_at=start_created_at,
            end_created_at=end_created_at,
            start_updated_at=start_updated_at,
            end_updated_at=end_updated_at,
            order_by=order_by,
            limit=limit,
            offset=offset,
            search=search,
            filter_search=filter_search,
            ad_hoc=ad_hoc,
            with_archived=with_archived,
            tenant_id=self.tenant_id,
            with_contents=with_contents,
            start_completed_at=start_completed_at,
            end_completed_at=end_completed_at,
            start_report_date=start_report_date,
            end_report_date=end_report_date,
            start_date=start_date,
            end_date=end_date,
            operating_region_names=operating_region_names,
            manager_ids=manager_ids,
        )

    async def get_forms_count(
        self,
        form_name: Optional[list[str]] = None,
        form_id: Optional[list[str]] = None,
        form_status: Optional[list[FormStatus]] = None,
        project_ids: list[UUID] | None = None,
        location_ids: list[UUID] | None = None,
        created_by_ids: list[UUID] | None = None,
        updated_by_ids: list[UUID] | None = None,
        start_created_at: Optional[datetime.date] = None,
        end_created_at: Optional[datetime.date] = None,
        start_updated_at: Optional[datetime.date] = None,
        end_updated_at: Optional[datetime.date] = None,
        search: Optional[str] = None,
        ad_hoc: bool = False,
        with_archived: bool = False,
        start_completed_at: Optional[datetime.date] = None,
        end_completed_at: Optional[datetime.date] = None,
        start_report_date: Optional[datetime.date] = None,
        end_report_date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        operating_region_names: Optional[list[str]] = None,
        manager_ids: Optional[list[str]] = None,
    ) -> int:
        return await self.__manager.get_forms_count(
            form_name=form_name,
            form_id=form_id,
            form_status=form_status,
            project_ids=project_ids,
            location_ids=location_ids,
            created_by_ids=created_by_ids,
            updated_by_ids=updated_by_ids,
            start_created_at=start_created_at,
            end_created_at=end_created_at,
            start_updated_at=start_updated_at,
            end_updated_at=end_updated_at,
            search=search,
            ad_hoc=ad_hoc,
            with_archived=with_archived,
            tenant_id=self.tenant_id,
            start_completed_at=start_completed_at,
            end_completed_at=end_completed_at,
            start_report_date=start_report_date,
            end_report_date=end_report_date,
            start_date=start_date,
            end_date=end_date,
            operating_region_names=operating_region_names,
            manager_ids=manager_ids,
        )
