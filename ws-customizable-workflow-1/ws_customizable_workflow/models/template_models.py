from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID

import pymongo
import pymongo.collation
from pydantic import BaseModel, Field, validator

from ws_customizable_workflow.models.base import (
    BaseDocument,
    BaseListQueryParams,
    BaseListWrapper,
    NonEmptyTitleMixin,
    OptionItem,
    OrderBy,
    OrderByFields,
    PrePopulationRules,
    TemplateAvailability,
    TemplateStatus,
)
from ws_customizable_workflow.models.component_models import (
    ELEMENT_CLASS_MAP,
    ContentElement,
)
from ws_customizable_workflow.models.element_models import (
    Element,
    ElementProperties,
    ElementType,
    RootElement,
)
from ws_customizable_workflow.models.form_models import Form, FormListRow
from ws_customizable_workflow.models.shared_models import (
    CopyRebriefSettings,
    EnergyWheelSettings,
    WorkTypeBase,
)


class TemplateInputProperties(NonEmptyTitleMixin, ElementProperties):
    title: str
    description: Optional[str] = None
    status: TemplateStatus = TemplateStatus.DRAFT


class PageUpdateStatus(str, Enum):
    """
    Represents the status of a page within a multi-step process.

    Members:
        DEFAULT: The page has not been modified or submitted.
        SAVED: The page's data was successfully submitted and saved.
        ERROR: The user navigated away from the page without saving, indicating potential data loss.
    """

    DEFAULT = "default"
    SAVED = "saved"
    ERROR = "error"


class TemplateProperties(TemplateInputProperties):
    template_unique_id: UUID


class PageProperties(NonEmptyTitleMixin, ElementProperties):
    """Extended properties class for types that require a description."""

    title: str
    description: Optional[str] = None
    page_update_status: PageUpdateStatus = PageUpdateStatus.DEFAULT
    include_in_summary: bool = False


class SectionProperties(NonEmptyTitleMixin, ElementProperties):
    """Extended properties class for types that require a description."""

    title: str
    is_repeatable: bool = False
    include_in_summary: bool = False
    include_in_widget: bool = False


class Section(Element):
    """Section class, extending from BaseContent."""

    type: ElementType = ElementType.SECTION
    properties: SectionProperties
    contents: List[ContentElement] = []

    @validator("contents", pre=True, each_item=True)
    def set_contents_type(cls, value: Dict[str, Any]) -> Element:
        if "type" not in value:
            raise ValueError("Type must be specified for each content element.")
        element_type = value["type"]

        if element_type in ELEMENT_CLASS_MAP:
            return ELEMENT_CLASS_MAP[element_type](**value)
        else:
            raise ValueError(f"Unknown type: {element_type}")


class Page(Element):
    """Page class, extending from BaseContent. Can contain Sections and SubPages and Widgets."""

    type: ElementType = ElementType.PAGE
    properties: PageProperties
    contents: List[Union["Section", "SubPage", ContentElement]] = []

    @validator("contents", pre=True, each_item=True)
    def set_contents_type(cls, value: Dict[str, Any]) -> Element:
        if "type" not in value:
            raise ValueError("Type must be specified for each content element.")
        element_type = value["type"]
        if element_type == ElementType.SECTION.value:
            return Section(**value)
        elif element_type == ElementType.SUB_PAGE.value:
            return SubPage(**value)
        elif element_type in ELEMENT_CLASS_MAP:
            return ELEMENT_CLASS_MAP[element_type](**value)
        else:
            raise ValueError(f"Unknown type: {element_type}")


class SubPage(Element):
    """SubPage class, extending from BaseContent. Can contain Sections and Widgets."""

    type: ElementType = ElementType.SUB_PAGE
    properties: PageProperties
    contents: List[Union["Section", ContentElement]] = []

    @validator("contents", pre=True, each_item=True)
    def set_contents_type(cls, value: Dict[str, Any]) -> Element:
        if "type" not in value:
            raise ValueError("Type must be specified for each content element.")
        element_type = value["type"]
        if element_type == ElementType.SECTION.value:
            return Section(**value)
        elif element_type in ELEMENT_CLASS_MAP:
            return ELEMENT_CLASS_MAP[element_type](**value)
        else:
            raise ValueError(f"Unknown type: {element_type}")


class AvailabilitySettingOption(BaseModel):
    selected: bool = False


class AvailabilitySettings(BaseModel):
    adhoc: AvailabilitySettingOption = Field(
        default_factory=lambda: AvailabilitySettingOption(selected=True)
    )
    work_package: AvailabilitySettingOption = Field(
        default_factory=AvailabilitySettingOption
    )


class TemplateMetadata(EnergyWheelSettings):
    is_report_date_included: bool = False
    is_activities_and_tasks_included: bool = False
    is_hazards_and_controls_included: bool = False
    is_summary_included: bool = False
    is_site_conditions_included: bool = False
    is_location_included: bool = False
    is_nearest_hospital_included: bool = False
    is_contractor_included: bool = False
    is_region_included: bool = False


class TemplateWorkType(WorkTypeBase):
    prepopulate: bool = False


class TemplateSettings(BaseModel):
    availability: AvailabilitySettings = Field(default_factory=AvailabilitySettings)
    edit_expiry_days: Optional[int] = 0
    work_types: List[TemplateWorkType] | None = None
    copy_and_rebrief: CopyRebriefSettings = Field(default_factory=CopyRebriefSettings)
    maximum_widgets: Optional[int] = 15
    widgets_added: Optional[int] = 0


class TemplateInput(BaseModel):
    properties: TemplateInputProperties
    contents: List[Page] = []
    settings: TemplateSettings = Field(default_factory=TemplateSettings)
    metadata: TemplateMetadata = Field(default_factory=TemplateMetadata)
    is_report_date_included: bool = (
        False  # Deprecated, this field will be removed in a future version
    )
    pre_population_rule_paths: Optional[Dict[PrePopulationRules, List[str]]] = None


class Template(TemplateInput, RootElement, BaseDocument):
    """Template class, extending from BaseContent. Can contain Pages."""

    properties: TemplateProperties
    type: ElementType = ElementType.TEMPLATE
    is_latest_version: bool = True
    order: int = 1
    is_report_date_included: bool = False

    class Settings:
        name = "templates"
        indexes = [
            pymongo.IndexModel(  # to support list
                [("is_latest_version", pymongo.ASCENDING)],
                name="latest_version_index",
            ),
            pymongo.IndexModel(  # to support filter-options
                [("properties.status", pymongo.ASCENDING)],
                name="properties_status_index",
            ),
            pymongo.IndexModel(  # to support add-options
                [
                    ("published_at", pymongo.DESCENDING),
                    ("properties.status", pymongo.ASCENDING),
                    ("is_latest_version", pymongo.ASCENDING),
                    ("settings.availability.adhoc.selected", pymongo.ASCENDING),
                    ("settings.availability.work_package.selected", pymongo.ASCENDING),
                ],
                name="add_options_query_index",
            ),
        ]


class TemplateListRow(BaseDocument):
    title: str
    template_unique_id: UUID
    status: Optional[TemplateStatus] = TemplateStatus.PUBLISHED
    is_latest_version: bool


T = TypeVar("T", bound=Union[TemplateListRow, FormListRow, Form])


class GroupedData(BaseModel, Generic[T]):
    _id: str
    group_by_key: str
    forms: List[T]


class ListWrapper(BaseListWrapper, Generic[T]):
    data: List[T]


class GroupedListWrapper(BaseListWrapper, Generic[T]):
    data: List[GroupedData[T]]


class CommonListQueryParams(BaseListQueryParams):
    order_by: OrderByFields = OrderByFields.PUBLISHED_AT


CONTENT_ELEMENT_PROPERTIES_MAP: dict[ElementType, Type[ElementProperties]] = {
    ElementType.TEMPLATE: TemplateProperties,
    ElementType.PAGE: PageProperties,
    ElementType.SECTION: SectionProperties,
    ElementType.SUB_PAGE: PageProperties,
}


class ListTemplateRequest(BaseModel):
    limit: int = Field(50, ge=1, le=50)
    skip: int = Field(0, ge=0, alias="offset")
    order_by: OrderBy = OrderBy()
    titles: Optional[list[str]] = Field(None, alias="template_names")
    published_by: Optional[list[str]] = None
    updated_by: Optional[list[str]] = None
    published_at_start_date: Optional[datetime] = None
    published_at_end_date: Optional[datetime] = None
    updated_at_start_date: Optional[datetime] = None
    updated_at_end_date: Optional[datetime] = None
    status: Optional[list[TemplateStatus]] = Field(None, alias="template_status")
    search: Optional[str] = None

    @validator("published_at_end_date", pre=True, always=True)
    def validate_published_dates(cls, value: str, values: Dict[str, Any]) -> str:
        start_date = values.get("published_at_start_date")
        if (
            start_date
            and value
            and start_date > datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        ):
            raise ValueError(
                "published_at_end_date must be greater than or equal to published_at_start_date"
            )
        return value


class ListTemplateVersionsRequest(BaseModel):
    title: str
    limit: int = Field(50, ge=1, le=50)
    skip: int = Field(0, ge=0, alias="offset")
    order_by: OrderBy = OrderBy(field=OrderByFields.PUBLISHED_AT, desc=True)


class TemplatesFilterOptions(BaseModel):
    names: list[str] = []
    published_by_users: list[OptionItem] = []
    updated_by_users: list[OptionItem] = []


class TemplateOptionItem(OptionItem):
    work_types: List[TemplateWorkType] = []


class TemplatesAddOptions(BaseModel):
    data: list[OptionItem] = []


class TemplateAddOptionsWithWorkTypes(BaseModel):
    data: list[TemplateOptionItem] = []


class TemplateAddOptionsRequest(BaseModel):
    status: TemplateStatus
    availability: TemplateAvailability
    work_type_ids: List[UUID] = Field(
        default_factory=list,
        description="Filter results to those related to these work types",
    )


class TemplatesPublishedList(BaseModel):
    """
    This class is deprecated and will be removed in a future version.
    """

    templates: list[OptionItem] = []


class TemplatesListResponse(BaseModel):
    templates: List[Template]
