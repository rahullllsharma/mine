from typing import List, Optional, Union

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory

from ws_customizable_workflow.models.component_models import ContentElement
from ws_customizable_workflow.models.element_models import ElementType
from ws_customizable_workflow.models.shared_models import CopyRebriefSettings
from ws_customizable_workflow.models.template_models import (
    AvailabilitySettingOption,
    AvailabilitySettings,
    Page,
    PageProperties,
    Section,
    SectionProperties,
    Template,
    TemplateProperties,
    TemplateSettings,
    TemplateStatus,
    TemplateWorkType,
)


class TemplatePropertiesFactory(ModelFactory):
    __model__ = TemplateProperties
    title: str = "Test Template Title"
    description: str = "Default Template Description"
    status: TemplateStatus = TemplateStatus.DRAFT


class SectionPropertiesFactory(ModelFactory):
    __model__ = SectionProperties
    title: str = "Test Section Title"


class PagePropertiesFactory(ModelFactory):
    __model__ = PageProperties
    title: str = "Test Page Title"
    description: str = "Default Page Description"


class SectionFactory(ModelFactory):
    __model__ = Section
    type: ElementType = ElementType.SECTION
    properties: SectionProperties = SectionPropertiesFactory.build()
    contents: List[ContentElement] = []


class PageFactory(ModelFactory):
    __model__ = Page
    type: ElementType = ElementType.PAGE
    properties: PageProperties = PagePropertiesFactory.build()
    contents: List[Union[Section, ContentElement]] = []


class TemplateFactory(ModelFactory):
    __model__ = Template
    type: ElementType = ElementType.TEMPLATE
    properties: TemplateProperties = TemplatePropertiesFactory.build()
    contents: List[Page] = []
    order: int = 1
    is_latest_version = True


class AvailabilitySettingOptionFactory(ModelFactory):
    __model__ = AvailabilitySettingOption


class AvailabilitySettingsFactory(ModelFactory):
    __model__ = AvailabilitySettings

    adhoc: AvailabilitySettingOption = AvailabilitySettingOptionFactory.build()
    work_package: AvailabilitySettingOption = AvailabilitySettingOptionFactory.build()


class TemplateWorkTypeFactory(ModelFactory):
    __model__ = TemplateWorkType
    name: str = Faker().random_element(
        elements=[
            "Gas Transmission Construction",
            "Electric Distribution",
            "Gas Distribution",
            "Electric Transmission Construction",
        ]
    )


class TemplateCopyRebriefSettingsFactory(ModelFactory):
    __model__ = CopyRebriefSettings


class TemplateSettingsFactory(ModelFactory):
    __model__ = TemplateSettings

    availability: Optional[AvailabilitySettings] = AvailabilitySettingsFactory.build()
    work_types: List[TemplateWorkType] = [TemplateWorkTypeFactory.build()]
    copy_and_rebrief: Optional[
        CopyRebriefSettings
    ] = TemplateCopyRebriefSettingsFactory.build()
