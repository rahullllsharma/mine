import math
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, Union
from uuid import UUID, uuid4

from beanie import Document
from pydantic import BaseModel, Field, validator

from ws_customizable_workflow.models.users import Tenant, User


class InclusiveType(str, Enum):
    START = "start"
    END = "end"
    BOTH = "both"


class PrePopulationRules(str, Enum):
    USER_LAST_COMPLETED = "user_last_completed_form"


class SuggestionType(str, Enum):
    RECENTLY_SELECTED_CREW_DETAILS = "recently_selected_crew_details"


class BaseDocument(Document):
    id: UUID = Field(default_factory=uuid4, serialization_alias="id")  # type: ignore
    created_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[User] = None
    updated_at: datetime = Field(default_factory=datetime.now)
    updated_by: Optional[User] = None
    archived_by: Optional[User] = None
    archived_at: Optional[datetime] = None
    is_archived: bool = False
    published_at: Optional[datetime] = None
    published_by: Optional[User] = None
    version: int = Field(1, ge=1)


class Metadata(BaseModel):
    count: int
    results_per_page: int
    scroll: Optional[str] = None

    def set_scroll(self, skip: int) -> None:
        scroll_value = (
            str(math.ceil((skip + 1) / self.results_per_page))
            + "/"
            + str(math.ceil(self.count / self.results_per_page))
        )
        self.scroll = scroll_value


class BaseListWrapper(BaseModel):
    data: list[Any]
    metadata: Metadata


class OrderByFields(str, Enum):
    TITLE = "title"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PUBLISHED_AT = "published_at"


class BaseListQueryParams(BaseModel):
    order_by: OrderByFields
    skip: int = 0
    limit: int = 50
    desc: bool = True
    is_group_by_used: bool = False


class TemplateStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class TemplateAvailability(str, Enum):
    ADHOC = "adhoc"
    WORK_PACKAGE = "work-package"


class FormStatus(str, Enum):
    INPROGRESS = "in_progress"
    COMPLETE = "completed"


class BaseFilterArgs(BaseModel):
    search: Optional[str] = None
    title: Optional[str] = None
    titles: Optional[list[str]] = None
    template_unique_id: Optional[UUID] = None
    updated_at_start_date: Optional[datetime] = None
    updated_at_end_date: Optional[datetime] = None
    created_at_start_date: Optional[datetime] = None
    created_at_end_date: Optional[datetime] = None
    completed_at_start_date: Optional[datetime] = None
    completed_at_end_date: Optional[datetime] = None
    reported_at_start_date: Optional[datetime] = None
    reported_at_end_date: Optional[datetime] = None
    status: Optional[Union[list[TemplateStatus], list[FormStatus]]] = None
    published_at_start_date: Optional[datetime] = None
    published_at_end_date: Optional[datetime] = None
    published_by: Optional[list[str]] = None
    created_by: Optional[list[str]] = None
    updated_by: Optional[list[str]] = None
    is_archived: bool = False
    is_latest_version: Optional[bool] = None
    work_package_id: Optional[list[str]] = None
    location_id: Optional[list[str]] = None
    region_id: Optional[list[str]] = None
    group_by: Optional[str] = None
    report_start_date: Optional[datetime] = None
    supervisor_id: List[str] | None = None


class OrderBy(BaseModel):
    field: Optional[OrderByFields] = OrderByFields.UPDATED_AT
    desc: bool = True


class Tenants(Tenant, Document):
    ...

    class Settings:
        name = "tenants"


class NonEmptyTitleMixin(BaseModel):
    @validator("title", check_fields=False)
    def title_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title cannot be empty")
        return value


class OptionItem(BaseModel):
    id: str
    name: str


class FileCategory(str, Enum):
    JHA = "JHA"
    PSSR = "PSSR"
    HASP = "HASP"
    OTHER = "Other"


class File(BaseModel):
    id: Optional[str] = ""
    url: str = ""
    name: str
    display_name: str
    size: Optional[str]
    date: Optional[date]
    time: Optional[str]
    last_modified: Optional[datetime]
    mimetype: Optional[str]
    md5: Optional[str]
    crc32c: Optional[str]
    signed_url: Optional[str]
    description: Optional[str]
    category: Optional[FileCategory]


class Signature(File):
    signedUrl: str
    displayName: str
    lastModified: Optional[datetime]


class CrewInformationTypes(str, Enum):
    PERSONNEL = "Personnel"
    OTHER = "Other"


class CrewInformation(BaseModel):
    name: Optional[str]
    signature: Optional[Signature] = None
    type: Optional[CrewInformationTypes] = None
    external_id: Optional[str]
    employee_number: Optional[str]
    display_name: Optional[str]
    email: Optional[str]
    job_title: Optional[str]
    department: Optional[str]
    company_name: Optional[str]
    manager_id: Optional[str]
    manager_name: Optional[str]
    manager_email: Optional[str]
    primary: Optional[bool]
