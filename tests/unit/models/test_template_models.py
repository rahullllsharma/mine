from unittest.mock import MagicMock, patch

from tests.conftest import get_user_override
from tests.factories.template_factory import (
    AvailabilitySettingOptionFactory,
    AvailabilitySettingsFactory,
    PageFactory,
    SectionFactory,
    TemplateCopyRebriefSettingsFactory,
    TemplateFactory,
)
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.template_models import (
    AvailabilitySettingOption,
    AvailabilitySettings,
    CopyRebriefSettings,
)
from ws_customizable_workflow.models.users import User


@patch("ws_customizable_workflow.models.template_models.Template.get_motor_collection")
async def test_template_creation(mock_get_motor_collection: MagicMock) -> None:
    mock_get_motor_collection.return_value = None
    test_user = await get_user_override()
    template = TemplateFactory.build(created_by=User(**test_user.model_dump()))
    template.contents.append(PageFactory.build())
    assert template.type == ElementType.TEMPLATE
    assert template.properties.title == "Test Template Title"
    assert len(template.contents) == 1
    assert template.created_by.user_name == "Test User"


def test_page_creation() -> None:
    page = PageFactory.build()
    page.contents.append(SectionFactory.build())
    assert page.type == ElementType.PAGE
    assert page.properties.title == "Test Page Title"
    assert len(page.contents) == 1
    assert page.contents[0].type == ElementType.SECTION


def test_section_creation() -> None:
    section = SectionFactory.build()
    assert section.type == ElementType.SECTION
    assert section.properties.title == "Test Section Title"
    assert section.contents == []


def test_availability_settings_factory_build() -> None:
    availability_settings = AvailabilitySettingsFactory.build()
    assert isinstance(availability_settings, AvailabilitySettings)
    assert isinstance(availability_settings.adhoc, AvailabilitySettingOption)
    assert isinstance(availability_settings.work_package, AvailabilitySettingOption)


def test_availability_settings_factory_build_with_custom_values() -> None:
    availability_settings = AvailabilitySettingsFactory.build(
        adhoc=AvailabilitySettingOptionFactory.build(selected=False),
        work_package=AvailabilitySettingOptionFactory.build(selected=True),
    )
    assert not availability_settings.adhoc.selected
    assert availability_settings.work_package.selected


def test_copy_rebrief_settings_factory_build() -> None:
    copy_rebrief_settings = TemplateCopyRebriefSettingsFactory.build()
    assert isinstance(copy_rebrief_settings, CopyRebriefSettings)
    assert isinstance(copy_rebrief_settings.is_copy_enabled, bool)
    assert isinstance(copy_rebrief_settings.is_rebrief_enabled, bool)


def test_copy_rebrief_settings_factory_build_with_custom_values() -> None:
    copy_rebrief_settings = TemplateCopyRebriefSettingsFactory.build(
        is_copy_enabled=True,
        is_rebrief_enabled=False,
        is_allow_linked_form=True,
    )
    assert copy_rebrief_settings.is_copy_enabled
    assert not copy_rebrief_settings.is_rebrief_enabled
    assert copy_rebrief_settings.is_allow_linked_form
