from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

import pymongo
from pydantic import BaseModel, Field, validator

from ws_customizable_workflow.models.base import (
    BaseDocument,
    FormStatus,
    OptionItem,
    OrderBy,
    SuggestionType,
)
from ws_customizable_workflow.models.element_models import (
    ElementProperties,
    ElementType,
    RootElement,
)
from ws_customizable_workflow.models.shared_models import (
    CopyRebriefSettings,
    EnergyWheelSettings,
    WorkTypeBase,
)


class FormProperties(ElementProperties):
    title: str
    description: Optional[str] = None
    status: FormStatus = FormStatus.INPROGRESS
    report_start_date: Optional[datetime] = None


class WorkPackageDetails(BaseModel):
    name: str
    id: str


class LocationDetails(BaseModel):
    name: str
    id: str


class RegionDetails(BaseModel):
    name: str
    id: str


class SupervisorDetails(BaseModel):
    id: str | None = None
    name: str | None = None
    email: str | None = None


class FormCopyRebriefSettings(CopyRebriefSettings):
    copy_linked_form_id: str | None = None
    rebrief_linked_form_id: str | None = None
    linked_form_id: str | None = None


class FormsMetadata(EnergyWheelSettings):
    work_package: Optional[WorkPackageDetails] = None
    location: Optional[LocationDetails] = None
    region: Optional[RegionDetails] = None
    work_types: Optional[List[WorkTypeBase]] = None
    supervisor: List[SupervisorDetails] | None = None
    copy_and_rebrief: FormCopyRebriefSettings = Field(
        default_factory=FormCopyRebriefSettings
    )


class GPSCoordinates(BaseModel):
    latitude: float
    longitude: float


class LocationComponentData(BaseModel):
    name: Optional[str] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    description: Optional[str] = None
    manual_location: Optional[bool] = False


class NearestHospitalComponentData(BaseModel):
    name: Optional[str] = None
    gps_coordinates: Optional[GPSCoordinates] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    other: Optional[bool] = False
    distance: Optional[str] = None


class ComponentData(BaseModel):
    activities_tasks: list[dict[str, Any]] = []
    hazards_controls: Optional[Any] = None
    site_conditions: list[dict[str, Any]] = []
    location_data: Optional[LocationComponentData] = None
    nearest_hospital: Optional[NearestHospitalComponentData] = None


class FormUpdateRequest(BaseModel):
    contents: List[Any]
    properties: FormProperties
    metadata: Optional[FormsMetadata] = None
    component_data: Optional[ComponentData] = None
    edit_expiry_time: Optional[datetime] = None
    edit_expiry_days: Optional[int] = 0


class FormInput(FormUpdateRequest):
    template_id: UUID


class CompletionAttributes(BaseModel):
    completed_at: Optional[datetime] = None


class Form(BaseDocument, FormInput, RootElement, CompletionAttributes):
    type: ElementType = ElementType.FORM
    order: int = 0

    class Settings:
        name = "forms"
        indexes = [
            pymongo.IndexModel([("status", pymongo.ASCENDING)], name="status_index"),
        ]


class FormListRow(BaseDocument, FormProperties, CompletionAttributes):
    metadata: Optional[FormsMetadata] = None
    location_data: Optional[LocationComponentData] = None


class ListFormRequest(BaseModel):
    limit: int = Field(50, ge=1, le=50)
    skip: int = Field(0, ge=0, alias="offset")
    order_by: OrderBy = OrderBy()
    titles: Optional[list[str]] = Field(None, alias="form_names")
    created_by: Optional[list[str]] = None
    updated_by: Optional[list[str]] = None
    created_at_start_date: Optional[datetime] = None
    created_at_end_date: Optional[datetime] = None
    updated_at_start_date: Optional[datetime] = None
    updated_at_end_date: Optional[datetime] = None
    completed_at_start_date: Optional[datetime] = None
    completed_at_end_date: Optional[datetime] = None
    reported_at_start_date: Optional[datetime] = None
    reported_at_end_date: Optional[datetime] = None
    status: Optional[list[FormStatus]] = None
    search: Optional[str] = None
    work_package_id: Optional[list[str]] = None
    location_id: Optional[list[str]] = None
    region_id: Optional[list[str]] = None
    group_by: Optional[str] = None
    is_group_by_used: bool = False
    report_start_date: Optional[datetime] = None
    supervisor_id: List[str] | None = None

    @validator("created_at_end_date", pre=True, always=True)
    def validate_created_dates(cls, value: str, values: dict[str, Any]) -> str:
        start_date = values.get("created_at_start_date")
        if (
            start_date
            and value
            and start_date > datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        ):
            raise ValueError(
                "created_at_end_date must be greater than or equal to created_at_start_date"
            )
        return value

    @validator("completed_at_end_date", pre=True, always=True)
    def validate_completed_dates(cls, value: str, values: dict[str, Any]) -> str:
        start_date = values.get("completed_at_start_date")
        if (
            start_date
            and value
            and start_date > datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        ):
            raise ValueError(
                "completed_at_end_date must be greater than or equal to completed_at_start_date"
            )
        return value

    @validator("reported_at_end_date", pre=True, always=True)
    def validate_reported_dates(cls, value: str, values: dict[str, Any]) -> str:
        start_date = values.get("reported_at_start_date")
        if (
            start_date
            and value
            and start_date > datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        ):
            raise ValueError(
                "reported_at_end_date must be greater than or equal to reported_at_start_date"
            )
        return value


class FormsFilterOptions(BaseModel):
    names: list[str] = []
    created_by_users: list[OptionItem] = []
    updated_by_users: list[OptionItem] = []
    work_package: Optional[list[WorkPackageDetails]] = None
    location: Optional[list[LocationDetails]] = None
    region: Optional[list[RegionDetails]] = None
    supervisor: List[SupervisorDetails] = []


class FormsSuggestion(BaseModel):
    suggestion_type: SuggestionType
    template_id: UUID
    element_type: ElementType
