import enum
from datetime import date as DATE
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


@enum.unique
class FileCategory(str, enum.Enum):
    JHA = "JHA"
    PSSR = "PSSR"
    HASP = "HASP"
    OTHER = "Other"


class GoogleCloudStorageBlob(SQLModel, table=True):
    __tablename__ = "google_cloud_storage_blob"
    id: str = Field(primary_key=True, nullable=False)
    bucket_name: str
    file_name: Optional[str]
    mimetype: Optional[str]
    md5: Optional[str]
    crc32c: Optional[str]


class File(BaseModel):
    url: str = ""
    name: str
    description: Optional[str]
    display_name: str
    size: Optional[str]
    date: Optional[DATE]
    time: Optional[str]
    id: Optional[str] = ""
    mimetype: Optional[str]
    md5: Optional[str]
    crc32c: Optional[str]
    signed_url: Optional[str]
    category: Optional[FileCategory]


class SignedPostPolicy(BaseModel):
    """Google Cloud Storage Post Policy for file upload
    id: str = Blob name
    url: str = URL to GCS bucket
    fields: str = form data to include in POST request or HTML form as JSON string
    """

    id: str
    url: str
    fields: str
