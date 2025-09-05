from typing import Any

import pytest
from pydantic import ValidationError

from tests.factories.form_factory import (
    FormCopyRebriefSettingsFactory,
    FormsMetadataFactory,
    FormUpdateRequestFactory,
    LocationDetailsFactory,
    WorkPackageDetailsFactory,
)
from ws_customizable_workflow.models.form_models import (
    ComponentData,
    LocationComponentData,
)


# Tests
def test_valid_metadata() -> None:
    """Test that valid metadata is accepted."""
    metadata = FormsMetadataFactory.build()
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata == metadata
    assert form_request.metadata.work_package.name == metadata.work_package.name
    assert form_request.metadata.location.id == metadata.location.id
    assert form_request.metadata.supervisor[0].name == metadata.supervisor[0].name
    assert form_request.metadata.copy_and_rebrief == metadata.copy_and_rebrief


def test_partial_metadata() -> None:
    """Test that metadata can have only work_package or location."""
    # Only work_package
    metadata = FormsMetadataFactory.build(
        location=None,
        work_types=None,
        supervisor=None,
    )
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata.work_package is not None
    assert form_request.metadata.location is None

    # Only location
    metadata = FormsMetadataFactory.build(
        work_package=None,
        work_types=None,
        supervisor=None,
    )
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata.location is not None
    assert form_request.metadata.work_package is None

    # Only supervisor
    metadata = FormsMetadataFactory.build(
        location=None,
        work_package=None,
        work_types=None,
    )
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata.supervisor is not None
    assert form_request.metadata.work_package is None
    assert form_request.metadata.work_types is None
    assert form_request.metadata.location is None

    # Only copy_and_rebrief
    metadata = FormsMetadataFactory.build(
        work_package=None,
        location=None,
        work_types=None,
        supervisor=None,
    )
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata.copy_and_rebrief is not None
    assert form_request.metadata.work_package is None
    assert form_request.metadata.work_types is None
    assert form_request.metadata.location is None


def test_no_metadata() -> None:
    """Test that metadata is optional and defaults to None."""
    form_request = FormUpdateRequestFactory.build(metadata=None)
    assert form_request.metadata is None


def test_invalid_metadata() -> None:
    """Test that invalid metadata raises validation errors."""
    # Missing required fields in work_package
    with pytest.raises(ValidationError):
        WorkPackageDetailsFactory.build(name=None)  # Missing 'name'

    # Missing required fields in location
    with pytest.raises(ValidationError):
        LocationDetailsFactory.build(id=None)  # Missing 'id'

    # Invalid data types
    with pytest.raises(ValidationError):
        WorkPackageDetailsFactory.build(name=123)  # 'name' should be a string


def test_copy_rebrief_form_settings() -> None:
    copy_rebrief_form_settings = FormCopyRebriefSettingsFactory.build()
    assert (
        copy_rebrief_form_settings.copy_linked_form_id
        == "65ae4024-c328-47df-875f-c6626fa56f0f"
    )
    assert (
        copy_rebrief_form_settings.rebrief_linked_form_id
        == "65ae4024-c328-47df-875f-c6626fa56f0f"
    )
    assert (
        copy_rebrief_form_settings.linked_form_id
        == "65ae4024-c328-47df-875f-c6626fa56f0f"
    )
    assert hasattr(copy_rebrief_form_settings, "is_copy_enabled")


def test_component_data_as_none() -> None:
    """Test component_data is optional and defaults to None."""
    form_request = FormUpdateRequestFactory.build(component_data=None)
    assert form_request.component_data is None


def test_component_data_activities_default() -> None:
    form_request = FormUpdateRequestFactory.build()
    component_data = form_request.component_data
    assert isinstance(component_data, ComponentData)
    assert len(component_data.activities_tasks) == 2


def test_component_data_activities_any_schema() -> None:
    activities_tasks: list[dict[str, Any]] = [{"a": "b"}, {"c": "d", "e": 123}]
    form_request = FormUpdateRequestFactory.build(
        component_data=ComponentData(activities_tasks=activities_tasks)
    )
    assert form_request.component_data.activities_tasks == activities_tasks


def test_component_data_site_conditions_default() -> None:
    form_request = FormUpdateRequestFactory.build()
    component_data = form_request.component_data
    assert isinstance(component_data, ComponentData)
    assert len(component_data.site_conditions) == 2


def test_component_data_site_conditions_any_schema() -> None:
    site_conditions: list[dict[str, Any]] = [{"a": "b"}, {"c": "d", "e": 123}]
    form_request = FormUpdateRequestFactory.build(
        component_data=ComponentData(site_conditions=site_conditions)
    )
    assert form_request.component_data.site_conditions == site_conditions


def test_component_data_location_data_default() -> None:
    form_request = FormUpdateRequestFactory.build()
    component_data = form_request.component_data
    assert isinstance(component_data, ComponentData)
    assert isinstance(component_data.location_data, LocationComponentData)


def test_form_update_request_with_metadata() -> None:
    """Test the full FormUpdateRequest with metadata."""
    metadata = FormsMetadataFactory.build()
    form_request = FormUpdateRequestFactory.build(metadata=metadata)
    assert form_request.metadata == metadata
    assert form_request.properties.title == "Test Template Title"
    assert len(form_request.contents) == 2


def test_form_update_request_without_metadata() -> None:
    """Test the full FormUpdateRequest without metadata."""
    form_request = FormUpdateRequestFactory.build(metadata=None)
    assert form_request.metadata is None
    assert form_request.properties.description == "Default Template Description"


def test_component_data_hazards_default() -> None:
    form_request = FormUpdateRequestFactory.build()
    component_data = form_request.component_data
    assert isinstance(component_data, ComponentData)

    # assert len(component_data.hazards_controls) == 2


def test_component_data_hazards_any_schema() -> None:
    hazards_controls: list[dict[str, Any]] = [{"a": "b"}, {"c": "d", "e": 123}]
    form_request = FormUpdateRequestFactory.build(
        component_data=ComponentData(hazards_controls=hazards_controls)
    )
    assert form_request.component_data.hazards_controls == hazards_controls
