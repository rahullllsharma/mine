from enum import Enum
from typing import Sequence

from pydantic import BaseModel


class ElementType(str, Enum):
    TEMPLATE = "template"
    FORM = "form"
    PAGE = "page"
    SECTION = "section"
    SUB_PAGE = "sub_page"
    CHOICE = "choice"
    DROPDOWN = "dropdown"
    YES_OR_NO = "yes_or_no"
    INPUT_TEXT = "input_text"
    INPUT_NUMBER = "input_number"
    INPUT_PHONE_NUMBER = "input_phone_number"
    INPUT_EMAIL = "input_email"
    RICH_TEXT_EDITOR = "rich_text_editor"
    INPUT_LOCATION = "input_location"
    INPUT_DATE_TIME = "input_date_time"
    ATTACHMENT = "attachment"
    REPORT_DATE = "report_date"
    ACTIVITIES_AND_TASKS = "activities_and_tasks"
    HAZARDS_AND_CONTROLS = "hazards_and_controls"
    SITE_CONDITIONS = "site_conditions"
    CONTRACTOR = "contractor"
    REGION = "region"
    SUMMARY = "summary"
    LOCATION = "location"
    NEAREST_HOSPITAL = "nearest_hospital"
    PERSONNEL_COMPONENT = "personnel_component"
    CHECKBOX = "checkbox"


class ElementProperties(BaseModel):
    pass


class RootElement(BaseModel):
    type: ElementType
    properties: ElementProperties
    contents: Sequence["Element"] = []


class Element(RootElement):
    id: str
    order: int
