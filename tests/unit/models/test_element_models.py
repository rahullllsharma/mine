from tests.factories.element_factory import ElementFactory
from ws_customizable_workflow.models.element_models import (
    ElementProperties,
    ElementType,
)


def test_element_creation() -> None:
    element = ElementFactory.build()
    assert element.type == ElementType.TEMPLATE
    assert element.order == 1
    assert isinstance(element.properties, ElementProperties)
    assert element.contents == [], "Expected 'contents' to be an empty list by default."
