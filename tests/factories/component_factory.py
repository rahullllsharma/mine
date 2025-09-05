from typing import List

from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import HttpUrl

from ws_customizable_workflow.models.component_models import (
    ActivitiesAndTasks,
    ActivitiesAndTasksProperties,
    API_Details,
    Attachment,
    AttachmentProperties,
    AttachmentType,
    Checkbox,
    CheckboxOption,
    CheckboxProperties,
    Choice,
    ChoiceProperties,
    ChoiceType,
    Contractor,
    ContractorProperties,
    Dropdown,
    DropdownProperties,
    HazardsAndControls,
    HazardsAndControlsProperties,
    InputDateTime,
    InputDateTimeProperties,
    InputEmail,
    InputEmailProperties,
    InputLocation,
    InputLocationProperties,
    InputNumber,
    InputNumberProperties,
    InputPhoneNumber,
    InputPhoneNumberProperties,
    InputText,
    InputTextProperties,
    Location,
    LocationProperties,
    NearestHospital,
    NearestHospitalProperties,
    Option,
    PersonnelComponent,
    PersonnelComponentAppliesType,
    PersonnelComponentAttributes,
    PersonnelComponentProperties,
    Region,
    RegionProperties,
    ReportDate,
    ReportDateProperties,
    RichTextEditor,
    RichTextEditorProperties,
    SiteConditions,
    SiteConditionsProperties,
    Summary,
    SummaryProperties,
    YesOrNo,
    YesOrNoProperties,
)
from ws_customizable_workflow.models.element_models import ElementType


class OptionFactory(ModelFactory):
    __model__ = Option
    value: str = "default_value"
    label: str = "Default Label"


class CheckboxOptionFactory(ModelFactory):
    __model__ = CheckboxOption

    value: str = "value1"
    label: str = "Label1"
    url: HttpUrl = HttpUrl("https://example1.com")
    url_display_text: str = "Example 1"


class ChoicePropertiesFactory(ModelFactory):
    __model__ = ChoiceProperties
    title: str = "Choice Title"
    hint_text: str = "Hint Text"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    choice_type: str = ChoiceType.SINGLE_CHOICE
    response_option: str = "manual_entry"
    options: List[Option] = [OptionFactory.build() for _ in range(2)]
    include_other_option: bool = False
    include_NA_option: bool = False


class DropdownPropertiesFactory(ModelFactory):
    __model__ = DropdownProperties
    title: str = "Dropdown Title"
    hint_text: str = "Select one"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "selected"
    options: List[dict] = [
        {"label": "Test", "value": "test"},
        {"label": "Test1", "value": "test1"},
    ]
    multiple_choice: bool = False
    include_other_input_box: bool = False
    include_other_option: bool = False
    include_NA_option: bool = False
    user_other_value: str | None = None


class YesOrNoPropertiesFactory(ModelFactory):
    __model__ = YesOrNoProperties
    title: str = "Yes or No Title"
    hint_text: str = "Choose Yes or No"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    toggle_style: str = "switch"
    toggle_options: List[dict] = [
        {"label": "Yes", "value": True},
        {"label": "No", "value": False},
    ]


class InputTextPropertiesFactory(ModelFactory):
    __model__ = InputTextProperties
    title: str = "Input Text Title"
    hint_text: str = "Enter text"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "string"
    validation: List[str] = ["regex:.*"]


class ChoiceFactory(ModelFactory):
    __model__ = Choice
    type: ElementType = ElementType.CHOICE
    properties: ChoiceProperties = ChoicePropertiesFactory.build()


class InputNumberPropertiesFactory(ModelFactory):
    __model__ = InputNumberProperties
    title: str = "Input Number Title"
    hint_text: str = "Enter a number"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "allowDecimals"
    validation: List[str] = ["regex:\\d+"]


class InputPhoneNumberPropertiesFactory(ModelFactory):
    __model__ = InputPhoneNumberProperties
    title: str = "Phone Number Title"
    hint_text: str = "Enter your phone number"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "phone"
    validation: List[str] = ["regex:\\d{10}"]


class InputEmailPropertiesFactory(ModelFactory):
    __model__ = InputEmailProperties
    title: str = "Email Title"
    hint_text: str = "Enter your email"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "manual_input"
    validation: List[str] = ["regex:\\S+@\\S+\\.\\S+"]


class InputLocationPropertiesFactory(ModelFactory):
    __model__ = InputLocationProperties
    title: str = "Location Title"
    hint_text: str = "Enter your location"
    is_mandatory: bool = True
    attachments_allowed: bool = False
    comments_allowed: bool = False
    response_option: str = "manual_address_input"
    is_show_map_preview: bool = True
    validation: List[str] = [
        "regex:^\\d+\\s[A-Za-z]+(\\s[A-Za-z]+)*$",
    ]


class SummaryPropertiesFactory(ModelFactory):
    __model__ = SummaryProperties
    title = "Summary Title"
    hint_text = "Summary Hint Text"
    is_mandatory: bool = False


class LocationPropertiesFactory(ModelFactory):
    __model__ = LocationProperties
    title = "Location Title"
    hint_text = "Location Hint Text"
    smart_address: bool = False
    is_mandatory: bool = False


class NearestHospitalPropertiesFactory(ModelFactory):
    __model__ = NearestHospitalProperties
    title = "Nearest Hospital Title"
    hint_text = "Nearest Hospital Hint Text"
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False


class PersonnelComponentPropertiesFactory(ModelFactory):
    __model__ = PersonnelComponentProperties
    title = "Personnel"
    hint_text = "Personnel Hint Text"
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    is_signature_enabled = True

    attributes = [
        PersonnelComponentAttributes(
            attribute_name="Supervisor",
            applies_to_user_value=PersonnelComponentAppliesType.SINGLE_NAME,
        )
    ]


class InputDateTimePropertiesFactory(ModelFactory):
    __model__ = InputDateTimeProperties


class ReportDatePropertiesFactory(ModelFactory):
    __model__ = ReportDateProperties


class API_DetailsFactory(ModelFactory):
    __model__ = API_Details

    name = "Get activities and tasks"
    description = "API to retrieve activities and tasks"
    endpoint = "/graphql"
    method = "POST"
    headers = {
        "Authorization": "Bearer {auth_token}",
        "Content-Type": "application/json",
    }
    request = {"body": {"work_type_id": "{work_type_id}"}}
    response = {"status_code": 200, "body": {}}


class ActivitiesAndTasksPropertiesFactory(ModelFactory):
    __model__ = ActivitiesAndTasksProperties

    title = "My custom activities and tasks name"
    hint_text = None
    description = None
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    user_value = None
    user_comments = None
    user_attachments = None
    add_button_enabled = True
    api_details = API_DetailsFactory.build()


class HazardsAndControlsPropertiesFactory(ModelFactory):
    __model__ = HazardsAndControlsProperties

    title = "My custom hazards and controls name"
    sub_title = "My custom hazards and controls sub title"
    hint_text = None
    description = None
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    user_value = None
    user_comments = None
    user_attachments = None
    add_button_enabled = True
    api_details = API_DetailsFactory.build()


class ContractorPropertiesFactory(ModelFactory):
    __model__ = ContractorProperties

    title = "My custom contractors"
    hint_text = None
    description = None
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    user_value = None
    user_comments = None
    user_attachments = None
    api_details = API_DetailsFactory.build()


class RegionPropertiesFactory(ModelFactory):
    __model__ = RegionProperties

    title = "My custom Region"
    hint_text = None
    description = None
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    user_value = None
    user_comments = None
    user_attachments = None
    api_details = API_DetailsFactory.build()


class SiteConditionPropertiesFactory(ModelFactory):
    __model__ = SiteConditionsProperties

    title = "My custom site condition label name"
    hint_text = None
    description = None
    is_mandatory = False
    attachments_allowed = False
    comments_allowed = False
    user_value = None
    user_comments = None
    user_attachments = None
    add_button_enabled = True
    api_details = API_DetailsFactory.build()


class RichTextEditorPropertiesFactory(ModelFactory):
    __model__ = RichTextEditorProperties
    data: str = "<p>Example</p>"


class CheckboxPropertiesFactory(ModelFactory):
    __model__ = CheckboxProperties

    title: str = "Checkbox Title"

    choice_type: str = ChoiceType.SINGLE_CHOICE
    options: List[CheckboxOption] = [CheckboxOptionFactory.build() for _ in range(2)]
    is_mandatory = True
    attachments_allowed = False
    comments_allowed = False


class RichTextEditorFactory(ModelFactory):
    __model__ = RichTextEditor
    type: ElementType = ElementType.RICH_TEXT_EDITOR
    properties: RichTextEditorProperties = RichTextEditorPropertiesFactory.build()


class DropdownFactory(ModelFactory):
    __model__ = Dropdown
    type: ElementType = ElementType.DROPDOWN
    properties: DropdownProperties = DropdownPropertiesFactory.build()


class YesOrNoFactory(ModelFactory):
    __model__ = YesOrNo
    type: ElementType = ElementType.YES_OR_NO
    properties: YesOrNoProperties = YesOrNoPropertiesFactory.build()


class InputTextFactory(ModelFactory):
    __model__ = InputText
    type: ElementType = ElementType.INPUT_TEXT
    properties: InputTextProperties = InputTextPropertiesFactory.build()


class InputNumberFactory(ModelFactory):
    __model__ = InputNumber
    type: ElementType = ElementType.INPUT_NUMBER
    properties: InputNumberProperties = InputNumberPropertiesFactory.build()


class InputPhoneNumberFactory(ModelFactory):
    __model__ = InputPhoneNumber
    type: ElementType = ElementType.INPUT_PHONE_NUMBER
    properties: InputPhoneNumberProperties = InputPhoneNumberPropertiesFactory.build()


class InputEmailFactory(ModelFactory):
    __model__ = InputEmail
    type: ElementType = ElementType.INPUT_EMAIL
    properties: InputEmailProperties = InputEmailPropertiesFactory.build()


class InputLocationFactory(ModelFactory):
    __model__ = InputLocation
    type: ElementType = ElementType.INPUT_LOCATION
    properties: InputLocationProperties = InputLocationPropertiesFactory.build()


class SummaryFactory(ModelFactory):
    __model__ = Summary
    type: ElementType = ElementType.SUMMARY
    properties: SummaryProperties = SummaryPropertiesFactory.build()


class LocationFactory(ModelFactory):
    __model__ = Location
    type: ElementType = ElementType.LOCATION
    properties: LocationProperties = LocationPropertiesFactory.build()


class NearestHospitalFactory(ModelFactory):
    __model__ = NearestHospital
    type: ElementType = ElementType.NEAREST_HOSPITAL
    properties: NearestHospitalProperties = NearestHospitalPropertiesFactory.build()


class PersonnelComponentFactory(ModelFactory):
    __model__ = PersonnelComponent
    type: ElementType = ElementType.PERSONNEL_COMPONENT
    properties: PersonnelComponentProperties = (
        PersonnelComponentPropertiesFactory.build()
    )


class AttachmentPropertiesFactory(ModelFactory):
    __model__ = AttachmentProperties
    title: str = "Attachment Title"
    attachment_type: AttachmentType = AttachmentType.PHOTO
    attachment_max_count: int = 20

    @classmethod
    def build_for_type(cls, _type: AttachmentType) -> AttachmentProperties:
        return AttachmentProperties(
            title=cls.title,
            attachment_type=_type,
            attachment_max_count=cls.attachment_max_count,
        )


class PhotoAttachmentFactory(ModelFactory):
    __model__ = Attachment
    type: ElementType = ElementType.ATTACHMENT
    properties: AttachmentProperties = AttachmentPropertiesFactory.build_for_type(
        AttachmentType.PHOTO
    )


class DocumentAttachmentFactory(ModelFactory):
    __model__ = Attachment
    type: ElementType = ElementType.ATTACHMENT
    properties: AttachmentProperties = AttachmentPropertiesFactory.build_for_type(
        AttachmentType.DOCUMENT
    )


class InputDateTimeFactory(ModelFactory):
    __model__ = InputDateTime
    type: ElementType = ElementType.INPUT_DATE_TIME
    properties: InputDateTimeProperties = InputDateTimePropertiesFactory.build()


class ReportDateFactory(ModelFactory):
    __model__ = ReportDate
    type: ElementType = ElementType.REPORT_DATE
    properties: ReportDateProperties = ReportDatePropertiesFactory.build()


class ActivitiesAndTasksFactory(ModelFactory):
    __model__ = ActivitiesAndTasks
    type: ElementType = ElementType.ACTIVITIES_AND_TASKS
    properties: ActivitiesAndTasksProperties = (
        ActivitiesAndTasksPropertiesFactory.build()
    )


class HazardsAndControlsFactory(ModelFactory):
    __model__ = HazardsAndControls
    type: ElementType = ElementType.HAZARDS_AND_CONTROLS
    properties: HazardsAndControlsProperties = (
        HazardsAndControlsPropertiesFactory.build()
    )


class SiteConditionsFactory(ModelFactory):
    __model__ = SiteConditions
    type: ElementType = ElementType.SITE_CONDITIONS
    properties: SiteConditionsProperties = SiteConditionPropertiesFactory.build()


class ContractorFactory(ModelFactory):
    __model__ = Contractor
    type: ElementType = ElementType.CONTRACTOR
    properties: ContractorProperties = ContractorPropertiesFactory.build()


class RegionFactory(ModelFactory):
    __model__ = Region
    type: ElementType = ElementType.REGION
    properties: RegionProperties = RegionPropertiesFactory.build()


class CheckboxFactory(ModelFactory):
    __model__ = Checkbox
    type: ElementType = ElementType.CHECKBOX
    properties: CheckboxProperties = CheckboxPropertiesFactory.build()
