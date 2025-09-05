from typing import Any, Optional

from polyfactory.factories.pydantic_factory import ModelFactory

from ws_customizable_workflow.models.base import (
    BaseListWrapper,
    CrewInformation,
    File,
    Metadata,
    Signature,
)


class MetadataFactory(ModelFactory):
    __model__ = Metadata
    count: int = 100
    results_per_page: int = 10
    scroll: Optional[str] = None


class BaseListWrapperFactory(ModelFactory):
    __model__ = BaseListWrapper
    data: list[Any] = [{"key": "value"}]
    metadata: Metadata = MetadataFactory.build()


class FileFactory(ModelFactory):
    __model__ = File

    name: str = "My file name"
    category: str = "HASP"


class SignatureFactory(ModelFactory):
    __model__ = Signature

    signedUrl: str = "https://signed_url"
    displayName: str = "Display Name"


class CrewInformationFactory(ModelFactory):
    __model__ = CrewInformation

    name: str = "John Doe"
    signature: Signature = SignatureFactory.build()
    type: str = "Other"
