import uuid
from datetime import date, datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from worker_safety_service import get_logger
from worker_safety_service.dal.daily_reports import DailyReportManager
from worker_safety_service.dal.energy_based_observations import (
    EnergyBasedObservationManager,
)
from worker_safety_service.dal.jsb import JobSafetyBriefingManager
from worker_safety_service.gcloud import FileStorage, get_file_storage
from worker_safety_service.gcloud.cache import Cache, CachedFileStorage, get_cache_impl
from worker_safety_service.models.daily_reports import DailyReport
from worker_safety_service.models.forms import EnergyBasedObservation, JobSafetyBriefing
from worker_safety_service.models.user import UserBase
from worker_safety_service.reports_auth.utils import get_tenant_id
from worker_safety_service.rest.dependency_injection.managers import (
    get_daily_report_manager,
    get_ebo_manager,
    get_job_safety_briefings_manager,
)

router = APIRouter(prefix="/reports")

logger = get_logger(__name__)


class FormType(Enum):
    EBO = "ebo"
    JSB = "jsb"
    DIR = "dir"


class FormAttributes(BaseModel):
    id: uuid.UUID
    form_id: Optional[str]
    date_for: date = Field(description="date of creation")
    updated_at: datetime = Field(description="timestamp of updation")
    completed_at: datetime | None = Field(None, description="timestamp of creation")
    status: str
    contents: Optional[dict] = None
    created_by: Optional[UserBase] = None
    completed_by: Optional[UserBase] = None
    sections: Optional[dict] = None


# TODO: Extract these args to a common place
@router.get(
    "/{form_type}",
    response_model=list[FormAttributes],
    status_code=200,
    tags=["reports"],
    openapi_extra={"security": [{"OAuth2": []}]},
)
async def get_reports(
    form_type: FormType,
    skip: int = Query(default=0, ge=0, alias="page[skip]"),
    limit: int = Query(default=50, le=200, ge=1, alias="page[limit]"),
    initial_load: bool = Query(default=False),
    start_date: datetime = Query(..., alias="filter[start-date]"),
    end_date: datetime = Query(..., alias="filter[end-date]"),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
    ebo_manager: EnergyBasedObservationManager = Depends(get_ebo_manager),
    jsb_manager: JobSafetyBriefingManager = Depends(get_job_safety_briefings_manager),
    daily_reports_manager: DailyReportManager = Depends(get_daily_report_manager),
    file_storage: FileStorage = Depends(get_file_storage),
    cache: Cache = Depends(get_cache_impl),
) -> list[EnergyBasedObservation] | list[JobSafetyBriefing] | list[DailyReport]:
    if form_type == FormType.EBO:
        cached_file_storage = CachedFileStorage(file_storage, cache)
        return await ebo_manager.get_all_with_refreshed_urls(
            cached_file_storage=cached_file_storage,
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            tenant_id=tenant_id,
            initial_load=initial_load,
        )
    elif form_type == FormType.JSB:
        return await jsb_manager.get_all(
            skip=skip,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
            tenant_id=tenant_id,
            initial_load=initial_load,
        )
    elif form_type == FormType.DIR:
        return await daily_reports_manager.get_daily_reports(
            skip=skip,
            limit=limit,
            updated_at_start_date=start_date,
            updated_at_end_date=end_date,
            tenant_id=tenant_id,
            initial_load=initial_load,
        )
