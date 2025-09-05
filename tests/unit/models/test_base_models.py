from tests.factories.base_factory import (
    BaseListWrapperFactory,
    CrewInformationFactory,
    FileFactory,
    MetadataFactory,
)
from ws_customizable_workflow.models.base import File, Metadata


def test_metadata_creation_and_functionality() -> None:
    metadata_instance = MetadataFactory.build()
    metadata_instance.set_scroll(skip=20)
    expected_scroll_value = "3/10"
    assert metadata_instance.scroll == expected_scroll_value


def test_base_list_wrapper_creation() -> None:
    base_list_wrapper_instance = BaseListWrapperFactory.build()
    assert isinstance(base_list_wrapper_instance.data, list)
    assert isinstance(base_list_wrapper_instance.metadata, Metadata)


def test_file_creation() -> None:
    file_instance = FileFactory.build()
    assert file_instance.name == "My file name"
    assert isinstance(file_instance.category, str)
    assert file_instance.category == "HASP"


def test_crew_information_creation() -> None:
    crew_information_instance = CrewInformationFactory.build()
    assert isinstance(crew_information_instance.signature, File)
    assert isinstance(crew_information_instance.type, str)
    assert crew_information_instance.name == "John Doe"
    assert crew_information_instance.type == "Other"
