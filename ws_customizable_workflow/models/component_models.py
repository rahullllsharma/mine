from enum import Enum
from typing import Any, List, Optional, Type, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from ws_customizable_workflow.models.base import (
    CrewInformation,
    File,
    NonEmptyTitleMixin,
    PrePopulationRules,
)
from ws_customizable_workflow.models.element_models import (
    Element,
    ElementProperties,
    ElementType,
)
from ws_customizable_workflow.models.shared_models import HistoricalIncident


class ChoiceType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class DateTimeType(str, Enum):
    DATE_TIME = "date_time"
    DATE_ONLY = "date_only"
    TIME_ONLY = "time_only"


class ResponseOptionType(str, Enum):
    MANUAL_ENTRY = "manual_entry"
    IMAGE = "image"


class Option(BaseModel):
    value: str
    label: str
    image_url: Optional[str] = None


class ToggleOption(BaseModel):
    value: bool
    label: str


class CheckboxOption(BaseModel):
    value: str
    label: str
    url: HttpUrl
    url_display_text: Optional[str]


class InputTextType(str, Enum):
    SHORT_TEXT = "short_text"
    LONG_TEXT = "long_text"


class PersonnelComponentAppliesType(str, Enum):
    SINGLE_NAME = "single_name"
    MULTIPLE_NAMES = "multiple_names"


class InputTextResponseOption(str, Enum):
    STRING = ("string",)
    ALPHANUMERIC = ("alphanumeric",)
    ONLY_ALPHABETS = ("only_alphabets",)
    REGEX = ("regex",)
    ALLOW_SPECIAL_CHARACTERS = "allow_special_characters"


class InputNumberResponseOption(str, Enum):
    ALLOW_DECIMALS = ("allowDecimals",)
    ALLOW_NEGATIVE_NUMBER = "allowNegativeNumbers"


class InputLocationResponseOption(str, Enum):
    GOOGLE_API_SEARCH = ("google_api_search",)
    MANUAL_ADDRESS_INPUT = ("manual_address_input",)
    LAT_LON = ("lat_lon",)
    AUTO_POPULATE_CURRENT_LOCATION = ("auto_populate_current_location",)


class InputEmailResponseOption(str, Enum):
    AUTO_POPULATE_USER_EMAIL = ("auto_populate_user_email",)
    MANUAL_INPUT = ("manual_input",)


class API_Details(BaseModel):
    name: str
    description: str
    endpoint: str
    method: str
    headers: dict[str, str]
    request: dict[str, Any]
    response: dict[str, Any]


class AttachmentType(str, Enum):
    PHOTO = "photo"
    DOCUMENT = "document"


class WidgetProperties(NonEmptyTitleMixin, ElementProperties):
    title: str
    hint_text: Optional[str] = None
    description: Optional[str] = None
    is_mandatory: bool = False
    attachments_allowed: bool = False
    comments_allowed: bool = False

    user_value: Optional[Any] = None
    user_comments: Optional[List[Any]] = None
    user_attachments: Optional[List[Any]] = None


class PrePopulationWidgetProperties(WidgetProperties):
    pre_population_rule_name: Optional[PrePopulationRules] = None


class ChoiceProperties(PrePopulationWidgetProperties):
    choice_type: ChoiceType = ChoiceType.SINGLE_CHOICE
    response_option: ResponseOptionType = ResponseOptionType.MANUAL_ENTRY
    options: List[Option] = []
    include_other_option: bool = False
    include_NA_option: bool = False
    include_in_summary: bool = False
    include_in_widget: bool = False


class DropdownProperties(PrePopulationWidgetProperties):
    response_option: str
    options: List[Option] = []
    multiple_choice: bool = False
    include_other_input_box: bool = False
    include_other_option: bool = False
    include_NA_option: bool = False
    user_other_value: Optional[str] = None
    include_in_summary: bool = False
    include_in_widget: bool = False
    api_details: Optional[API_Details] = None


class YesOrNoProperties(PrePopulationWidgetProperties):
    toggle_style: str
    toggle_options: List[ToggleOption]
    include_in_summary: bool = False
    include_in_widget: bool = False


class InputTextProperties(PrePopulationWidgetProperties):
    response_option: InputTextResponseOption = InputTextResponseOption.STRING
    validation: Optional[List[str]] = None
    input_type: InputTextType = InputTextType.SHORT_TEXT
    sub_label: Optional[str] = None
    placeholder: Optional[str] = None
    visible_lines: Optional[int] = 4  # visible lines to vertical scrolling.
    include_in_summary: bool = False
    include_in_widget: bool = False


class InputNumberProperties(PrePopulationWidgetProperties):
    response_option: InputNumberResponseOption = (
        InputNumberResponseOption.ALLOW_DECIMALS
    )
    display_units: bool = False
    unit_name: Optional[str] = None
    validation: Optional[List[str]] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class InputLocationProperties(PrePopulationWidgetProperties):
    response_option: InputLocationResponseOption = (
        InputLocationResponseOption.MANUAL_ADDRESS_INPUT
    )
    is_show_map_preview: bool = False
    validation: Optional[List[str]] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class AttachmentProperties(NonEmptyTitleMixin, ElementProperties):
    title: str
    attachment_type: AttachmentType
    attachment_max_count: int = 20
    user_value: Optional[List[File]] = None
    include_in_summary: bool = False


class SummaryProperties(WidgetProperties):
    user_value: Optional[list[str]] = None
    historical_incident_label: Optional[str] = None
    historical_incident: Optional[HistoricalIncident] = None


class LocationProperties(WidgetProperties):
    user_value: Optional[list[dict[str, Any]]] = None
    include_in_summary: bool = False
    smart_address: bool = False


class NearestHospitalProperties(WidgetProperties):
    include_in_summary: bool = False


class PersonnelComponentAttributes(BaseModel):
    attribute_id: UUID = Field(default_factory=uuid4)
    attribute_name: str
    is_required_for_form_completion: bool = False
    applies_to_user_value: PersonnelComponentAppliesType


class PersonnelComponentData(BaseModel):
    crew_details: CrewInformation
    selected_attribute_ids: List[UUID] = Field(default_factory=list)


class PersonnelComponentProperties(WidgetProperties):
    attributes: List[PersonnelComponentAttributes] = Field(default_factory=list)
    user_value: List[PersonnelComponentData] = Field(default_factory=list)
    include_in_summary: bool = False
    is_signature_enabled: bool = False


class CheckboxProperties(PrePopulationWidgetProperties):
    choice_type: ChoiceType
    options: List[CheckboxOption] = []
    include_in_summary: bool = False
    include_in_widget: bool = False


class DateOptions(str, Enum):
    SINGLE_DATE = "single_date"
    DATE_RANGE = "date_range"


class DateResponseType(str, Enum):
    AUTO_POPULATE_CURRENT_DATE = "auto_populate_current_date"
    MANUAL_INPUT = "manual_input"
    CALENDAR = "calendar"


class TimeResponseType(str, Enum):
    AUTO_POPULATE_CURRENT_TIME = "auto_populate_current_time"
    MANUAL_INPUT = "manual_input"


class DateValidation(str, Enum):
    ALLOW_FUTURE_DATE = "allow_future_date"
    ALLOW_PAST_DATE = "allow_past_date"


class TimeValidation(str, Enum):
    ALLOW_FUTURE_TIME = "allow_future_time"
    ALLOW_PAST_TIME = "allow_past_time"


class InputDateTimeProperties(PrePopulationWidgetProperties):
    selected_type: DateTimeType = DateTimeType.DATE_TIME

    date_response_type: DateResponseType = DateResponseType.MANUAL_INPUT
    date_options: DateOptions = DateOptions.SINGLE_DATE
    date_validation: Optional[DateValidation] = None
    date_type: DateOptions = DateOptions.SINGLE_DATE

    time_response_type: TimeResponseType = TimeResponseType.MANUAL_INPUT
    time_validation: Optional[TimeValidation] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class ReportDateProperties(InputDateTimeProperties):
    include_in_widget: bool = False


class InputPhoneNumberProperties(PrePopulationWidgetProperties):
    response_option: str
    validation: Optional[List[str]] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class InputEmailProperties(PrePopulationWidgetProperties):
    response_option: InputEmailResponseOption = InputEmailResponseOption.MANUAL_INPUT
    validation: Optional[List[str]] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class ContractorProperties(PrePopulationWidgetProperties):
    api_details: Optional[API_Details] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class RegionProperties(PrePopulationWidgetProperties):
    api_details: Optional[API_Details] = None
    include_in_summary: bool = False
    include_in_widget: bool = False


class RichTextEditorProperties(ElementProperties):
    data: str
    include_in_summary: bool = False


class ActivitiesAndTasksProperties(WidgetProperties):
    add_button_enabled: bool = True
    api_details: Optional[API_Details] = None
    include_in_summary: bool = False


class HazardsAndControlsProperties(WidgetProperties):
    sub_title: str | None = None
    add_button_enabled: bool = True
    api_details: Optional[API_Details] = None
    include_in_summary: bool = False


class SiteConditionsProperties(WidgetProperties):
    add_button_enabled: bool = True
    api_details: Optional[API_Details] = None
    include_in_summary: bool = False


class Choice(Element):
    type: ElementType = ElementType.CHOICE
    properties: ChoiceProperties


class Dropdown(Element):
    type: ElementType = ElementType.DROPDOWN
    properties: DropdownProperties


class YesOrNo(Element):
    type: ElementType = ElementType.YES_OR_NO
    properties: YesOrNoProperties


class InputText(Element):
    type: ElementType = ElementType.INPUT_TEXT
    properties: InputTextProperties


class InputNumber(Element):
    type: ElementType = ElementType.INPUT_NUMBER
    properties: InputNumberProperties


class InputPhoneNumber(Element):
    type: ElementType = ElementType.INPUT_PHONE_NUMBER
    properties: InputPhoneNumberProperties


class InputEmail(Element):
    type: ElementType = ElementType.INPUT_EMAIL
    properties: InputEmailProperties


class InputLocation(Element):
    type: ElementType = ElementType.INPUT_LOCATION
    properties: InputLocationProperties


class InputDateTime(Element):
    type: ElementType = ElementType.INPUT_DATE_TIME
    properties: InputDateTimeProperties


class RichTextEditor(Element):
    type: ElementType = ElementType.RICH_TEXT_EDITOR
    properties: RichTextEditorProperties


class Attachment(Element):
    type: ElementType = ElementType.ATTACHMENT
    properties: AttachmentProperties
    is_mandatory: bool = False


class Summary(Element):
    type: ElementType = ElementType.SUMMARY
    properties: SummaryProperties


class ReportDate(Element):
    type: ElementType = ElementType.REPORT_DATE
    properties: ReportDateProperties


class ActivitiesAndTasks(Element):
    type: ElementType = ElementType.ACTIVITIES_AND_TASKS
    properties: ActivitiesAndTasksProperties


class HazardsAndControls(Element):
    type: ElementType = ElementType.HAZARDS_AND_CONTROLS
    properties: HazardsAndControlsProperties


class SiteConditions(Element):
    type: ElementType = ElementType.SITE_CONDITIONS
    properties: SiteConditionsProperties


class Location(Element):
    type: ElementType = ElementType.LOCATION
    properties: LocationProperties


class NearestHospital(Element):
    type: ElementType = ElementType.NEAREST_HOSPITAL
    properties: NearestHospitalProperties


class Contractor(Element):
    type: ElementType = ElementType.CONTRACTOR
    properties: ContractorProperties


class Region(Element):
    type: ElementType = ElementType.REGION
    properties: RegionProperties


class PersonnelComponent(Element):
    type: ElementType = ElementType.PERSONNEL_COMPONENT
    properties: PersonnelComponentProperties


class Checkbox(Element):
    type: ElementType = ElementType.CHECKBOX
    properties: CheckboxProperties


ContentElement = Union[
    Choice,
    Dropdown,
    YesOrNo,
    InputText,
    InputNumber,
    InputPhoneNumber,
    InputEmail,
    RichTextEditor,
    InputLocation,
    InputDateTime,
    Attachment,
    Summary,
    ReportDate,
    ActivitiesAndTasks,
    HazardsAndControls,
    SiteConditions,
    Contractor,
    Region,
    Location,
    NearestHospital,
    PersonnelComponent,
    Checkbox,
]


ELEMENT_PROPERTIES_MAP: dict[ElementType, Type[ElementProperties]] = {
    ElementType.CHOICE: ChoiceProperties,
    ElementType.DROPDOWN: DropdownProperties,
    ElementType.YES_OR_NO: YesOrNoProperties,
    ElementType.INPUT_TEXT: InputTextProperties,
    ElementType.INPUT_NUMBER: InputNumberProperties,
    ElementType.INPUT_PHONE_NUMBER: InputPhoneNumberProperties,
    ElementType.INPUT_EMAIL: InputEmailProperties,
    ElementType.RICH_TEXT_EDITOR: RichTextEditorProperties,
    ElementType.INPUT_LOCATION: InputLocationProperties,
    ElementType.INPUT_DATE_TIME: InputDateTimeProperties,
    ElementType.ATTACHMENT: AttachmentProperties,
    ElementType.SUMMARY: SummaryProperties,
    ElementType.REPORT_DATE: InputDateTimeProperties,
    ElementType.ACTIVITIES_AND_TASKS: ActivitiesAndTasksProperties,
    ElementType.HAZARDS_AND_CONTROLS: HazardsAndControlsProperties,
    ElementType.SITE_CONDITIONS: SiteConditionsProperties,
    ElementType.CONTRACTOR: ContractorProperties,
    ElementType.REGION: RegionProperties,
    ElementType.LOCATION: LocationProperties,
    ElementType.NEAREST_HOSPITAL: NearestHospitalProperties,
    ElementType.PERSONNEL_COMPONENT: PersonnelComponentProperties,
    ElementType.CHECKBOX: CheckboxProperties,
}

ELEMENT_CLASS_MAP: dict[ElementType, Type[Element]] = {
    ElementType.CHOICE: Choice,
    ElementType.DROPDOWN: Dropdown,
    ElementType.YES_OR_NO: YesOrNo,
    ElementType.INPUT_TEXT: InputText,
    ElementType.INPUT_NUMBER: InputNumber,
    ElementType.INPUT_PHONE_NUMBER: InputPhoneNumber,
    ElementType.INPUT_EMAIL: InputEmail,
    ElementType.INPUT_LOCATION: InputLocation,
    ElementType.INPUT_DATE_TIME: InputDateTime,
    ElementType.RICH_TEXT_EDITOR: RichTextEditor,
    ElementType.ATTACHMENT: Attachment,
    ElementType.SUMMARY: Summary,
    ElementType.REPORT_DATE: ReportDate,
    ElementType.ACTIVITIES_AND_TASKS: ActivitiesAndTasks,
    ElementType.HAZARDS_AND_CONTROLS: HazardsAndControls,
    ElementType.SITE_CONDITIONS: SiteConditions,
    ElementType.CONTRACTOR: Contractor,
    ElementType.REGION: Region,
    ElementType.LOCATION: Location,
    ElementType.NEAREST_HOSPITAL: NearestHospital,
    ElementType.PERSONNEL_COMPONENT: PersonnelComponent,
    ElementType.CHECKBOX: Checkbox,
}
