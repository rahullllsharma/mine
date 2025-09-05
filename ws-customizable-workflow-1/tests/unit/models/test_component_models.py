from tests.factories.component_factory import (
    ActivitiesAndTasksFactory,
    CheckboxFactory,
    CheckboxPropertiesFactory,
    ChoiceFactory,
    ChoicePropertiesFactory,
    ContractorFactory,
    DocumentAttachmentFactory,
    DropdownFactory,
    DropdownPropertiesFactory,
    HazardsAndControlsFactory,
    InputDateTimeFactory,
    InputEmailFactory,
    InputEmailPropertiesFactory,
    InputLocationFactory,
    InputNumberFactory,
    InputNumberPropertiesFactory,
    InputPhoneNumberFactory,
    InputPhoneNumberPropertiesFactory,
    InputTextFactory,
    InputTextPropertiesFactory,
    LocationFactory,
    NearestHospitalFactory,
    OptionFactory,
    PersonnelComponentFactory,
    PhotoAttachmentFactory,
    RegionFactory,
    ReportDateFactory,
    RichTextEditorFactory,
    RichTextEditorPropertiesFactory,
    SiteConditionsFactory,
    SummaryFactory,
    YesOrNoFactory,
    YesOrNoPropertiesFactory,
)
from ws_customizable_workflow.models.component_models import (
    ActivitiesAndTasksProperties,
    CheckboxProperties,
    ContractorProperties,
    DropdownProperties,
    HazardsAndControlsProperties,
    InputDateTimeProperties,
    InputEmailProperties,
    InputLocationProperties,
    InputNumberProperties,
    InputPhoneNumberProperties,
    InputTextProperties,
    LocationProperties,
    NearestHospitalProperties,
    PersonnelComponentAppliesType,
    PersonnelComponentAttributes,
    PersonnelComponentProperties,
    RegionProperties,
    ReportDateProperties,
    SiteConditionsProperties,
    SummaryProperties,
    YesOrNoProperties,
)
from ws_customizable_workflow.models.element_models import ElementType


def test_option_creation() -> None:
    option = OptionFactory.build()
    assert option.value == "default_value"
    assert option.label == "Default Label"


def test_choice_properties_creation() -> None:
    choice_properties = ChoicePropertiesFactory.build()
    assert choice_properties.title == "Choice Title"
    assert len(choice_properties.options) == 2


def test_dropdown_properties_creation() -> None:
    dropdown_properties = DropdownPropertiesFactory.build()
    assert dropdown_properties.title == "Dropdown Title"
    assert len(dropdown_properties.options) == 2


def test_dropdown_properties_new_fields_default_values() -> None:
    """Test that the new fields have correct default values."""
    dropdown_properties = DropdownPropertiesFactory.build()
    assert dropdown_properties.include_other_input_box is False
    assert dropdown_properties.include_other_option is False
    assert dropdown_properties.include_NA_option is False


def test_dropdown_properties_new_fields_custom_values() -> None:
    """Test that the new fields can be set to custom values."""
    dropdown_properties = DropdownPropertiesFactory.build(
        include_other_input_box=True,
        include_other_option=True,
        include_NA_option=True,
    )
    assert dropdown_properties.include_other_input_box is True
    assert dropdown_properties.include_other_option is True
    assert dropdown_properties.include_NA_option is True


def test_dropdown_properties_new_fields_mixed_values() -> None:
    """Test that the new fields can be set to mixed boolean values."""
    dropdown_properties = DropdownPropertiesFactory.build(
        include_other_input_box=True,
        include_other_option=False,
        include_NA_option=True,
    )
    assert dropdown_properties.include_other_input_box is True
    assert dropdown_properties.include_other_option is False
    assert dropdown_properties.include_NA_option is True


def test_dropdown_properties_all_fields_integration() -> None:
    """Test that all fields work together correctly."""
    dropdown_properties = DropdownPropertiesFactory.build(
        title="Custom Dropdown",
        hint_text="Select an option",
        is_mandatory=True,
        response_option="custom_selected",
        multiple_choice=True,
        include_other_input_box=True,
        include_other_option=True,
        include_NA_option=False,
    )

    # Test all fields are set correctly
    assert dropdown_properties.title == "Custom Dropdown"
    assert dropdown_properties.hint_text == "Select an option"
    assert dropdown_properties.is_mandatory is True
    assert dropdown_properties.response_option == "custom_selected"
    assert dropdown_properties.multiple_choice is True
    assert dropdown_properties.include_other_input_box is True
    assert dropdown_properties.include_other_option is True
    assert dropdown_properties.include_NA_option is False


def test_yes_or_no_properties_creation() -> None:
    yes_or_no_properties = YesOrNoPropertiesFactory.build()
    assert yes_or_no_properties.title == "Yes or No Title"
    assert yes_or_no_properties.toggle_style == "switch"


def test_input_text_properties_creation() -> None:
    input_text_properties = InputTextPropertiesFactory.build()
    assert input_text_properties.title == "Input Text Title"
    assert input_text_properties.hint_text == "Enter text"


def test_choice_element_creation() -> None:
    choice_element = ChoiceFactory.build()
    assert choice_element.type == ElementType.CHOICE
    assert choice_element.properties.title == "Choice Title"


def test_input_number_properties_creation() -> None:
    input_number_props = InputNumberPropertiesFactory.build()
    assert input_number_props.title == "Input Number Title"
    assert "regex:\\d+" in input_number_props.validation


def test_input_phone_number_properties_creation() -> None:
    input_phone_props = InputPhoneNumberPropertiesFactory.build()
    assert input_phone_props.title == "Phone Number Title"
    assert "regex:\\d{10}" in input_phone_props.validation


def test_input_email_properties_creation() -> None:
    input_email_props = InputEmailPropertiesFactory.build()
    assert input_email_props.title == "Email Title"
    assert "regex:\\S+@\\S+\\.\\S+" in input_email_props.validation


def test_rich_text_editor_properties_creation() -> None:
    rich_text_editor_props = RichTextEditorPropertiesFactory.build()
    assert rich_text_editor_props.data == "<p>Example</p>"


def test_dropdown_creation() -> None:
    dropdown = DropdownFactory.build()
    assert dropdown.type == ElementType.DROPDOWN
    assert isinstance(dropdown.properties, DropdownProperties)


def test_yes_or_no_creation() -> None:
    yes_or_no = YesOrNoFactory.build()
    assert yes_or_no.type == ElementType.YES_OR_NO
    assert isinstance(yes_or_no.properties, YesOrNoProperties)


def test_input_text_creation() -> None:
    input_text = InputTextFactory.build()
    assert input_text.type == ElementType.INPUT_TEXT
    assert isinstance(input_text.properties, InputTextProperties)


def test_input_number_creation() -> None:
    input_number = InputNumberFactory.build()
    assert input_number.type == ElementType.INPUT_NUMBER
    assert isinstance(input_number.properties, InputNumberProperties)


def test_input_phone_number_creation() -> None:
    input_phone_number = InputPhoneNumberFactory.build()
    assert input_phone_number.type == ElementType.INPUT_PHONE_NUMBER
    assert isinstance(input_phone_number.properties, InputPhoneNumberProperties)


def test_input_email_creation() -> None:
    input_email = InputEmailFactory.build()
    assert input_email.type == ElementType.INPUT_EMAIL
    assert isinstance(input_email.properties, InputEmailProperties)


def test_input_location_creation() -> None:
    input_location = InputLocationFactory.build()
    assert input_location.type == ElementType.INPUT_LOCATION
    assert isinstance(input_location.properties, InputLocationProperties)


def test_rich_text_editor_element_creation() -> None:
    rich_text_editor = RichTextEditorFactory.build()
    assert rich_text_editor.type == ElementType.RICH_TEXT_EDITOR
    assert (
        rich_text_editor.properties.data == "<p>Example</p>"
    ), "The data property should contain the expected HTML content."


def test_photo_attachment_element_creation() -> None:
    photo_attachment = PhotoAttachmentFactory.build()
    assert photo_attachment.type == ElementType.ATTACHMENT
    assert photo_attachment.properties.attachment_type == "photo"


def test_document_attachment_element_creation() -> None:
    document_attachment = DocumentAttachmentFactory.build()
    assert document_attachment.type == ElementType.ATTACHMENT
    assert document_attachment.properties.attachment_type == "document"


def test_input_date_time_creation() -> None:
    input_date_time = InputDateTimeFactory.build()
    assert input_date_time.type == ElementType.INPUT_DATE_TIME
    assert isinstance(input_date_time.properties, InputDateTimeProperties)


def test_report_date_creation() -> None:
    report_date = ReportDateFactory.build()
    assert report_date.type == ElementType.REPORT_DATE
    assert isinstance(report_date.properties, ReportDateProperties)


def test_activities_and_tasks_creation() -> None:
    activities_and_tasks = ActivitiesAndTasksFactory.build()
    assert activities_and_tasks.type == ElementType.ACTIVITIES_AND_TASKS
    assert isinstance(activities_and_tasks.properties, ActivitiesAndTasksProperties)


def test_contractor_creation() -> None:
    contractor = ContractorFactory.build()
    assert contractor.type == ElementType.CONTRACTOR
    assert isinstance(contractor.properties, ContractorProperties)


def test_region_creation() -> None:
    region = RegionFactory.build()
    assert region.type == ElementType.REGION
    assert isinstance(region.properties, RegionProperties)


def test_hazards_and_controls_creation() -> None:
    hazards_and_controls = HazardsAndControlsFactory.build()
    assert hazards_and_controls.type == ElementType.HAZARDS_AND_CONTROLS
    assert isinstance(hazards_and_controls.properties, HazardsAndControlsProperties)
    assert (
        hazards_and_controls.properties.sub_title
        == "My custom hazards and controls sub title"
    )


def test_summary_creation() -> None:
    summary = SummaryFactory.build()
    assert summary.type == ElementType.SUMMARY
    assert isinstance(summary.properties, SummaryProperties)


def test_location_creation() -> None:
    location = LocationFactory.build()
    assert location.type == ElementType.LOCATION
    assert isinstance(location.properties, LocationProperties)


def test_nearest_hospital_creation() -> None:
    nearest_hospital = NearestHospitalFactory.build()
    assert nearest_hospital.type == ElementType.NEAREST_HOSPITAL
    assert isinstance(nearest_hospital.properties, NearestHospitalProperties)


def test_site_conditions_creation() -> None:
    site_conditions = SiteConditionsFactory.build()
    assert site_conditions.type == ElementType.SITE_CONDITIONS
    assert isinstance(site_conditions.properties, SiteConditionsProperties)


def test_personnel_component_creation() -> None:
    personnel_component = PersonnelComponentFactory.build()
    assert personnel_component.type == ElementType.PERSONNEL_COMPONENT
    assert isinstance(personnel_component.properties, PersonnelComponentProperties)
    attributes = personnel_component.properties.attributes
    assert isinstance(attributes, list)
    assert isinstance(attributes[0], PersonnelComponentAttributes)
    assert attributes[0].attribute_name == "Supervisor"
    assert attributes[0].is_required_for_form_completion is False
    assert isinstance(
        attributes[0].applies_to_user_value, PersonnelComponentAppliesType
    )


def test_checkbox_element_creation() -> None:
    checkbox_element = CheckboxFactory.build()
    assert checkbox_element.type == ElementType.CHECKBOX
    assert checkbox_element.properties.title == "Checkbox Title"


def test_checkbox_properties_creation() -> None:
    checkbox_properties = CheckboxPropertiesFactory.build()
    assert isinstance(checkbox_properties, CheckboxProperties)
    assert len(checkbox_properties.options) == 2
    assert checkbox_properties.is_mandatory is True
    assert "https://example1.com" in str(checkbox_properties.options[0].url)
