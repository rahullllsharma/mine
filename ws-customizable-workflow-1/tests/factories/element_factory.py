from typing import Sequence

from polyfactory.factories.pydantic_factory import ModelFactory

from ws_customizable_workflow.models.element_models import (
    Element,
    ElementProperties,
    ElementType,
)


class ElementPropertiesFactory(ModelFactory):
    __model__ = ElementProperties


class ElementFactory(ModelFactory):
    __model__ = Element
    type: ElementType = ElementType.TEMPLATE
    order: int = 1
    properties: ElementProperties = ElementPropertiesFactory.build()
    contents: Sequence["Element"] = []


class ElementFactoryWithContents(ElementFactory):
    contents: Sequence["Element"] = []
