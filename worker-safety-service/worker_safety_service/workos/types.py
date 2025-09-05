from enum import Enum
from typing import List, Optional, TypedDict

import strawberry
from strawberry.scalars import JSON


@strawberry.enum
class InputSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


@strawberry.input
class DirectoryUsersInput:
    directory: Optional[str] = None
    group: Optional[str] = None
    limit: Optional[str] = None
    before: Optional[str] = None
    after: Optional[str] = None
    order: Optional[InputSortOrder] = None


@strawberry.type
class ListMetadata:
    before: Optional[str] = None
    after: Optional[str] = None


@strawberry.type
class DirectoryUserEmail:
    type: Optional[str] = None
    value: Optional[str] = None
    primary: Optional[bool] = None


@strawberry.enum
class DirectoryUserState(str, Enum):
    active = "active"
    inactive = "inactive"


@strawberry.type
class DirectoryGroup:
    id: str
    idp_id: str
    directory_id: str
    organization_id: Optional[str] = None
    name: str
    created_at: str
    updated_at: str
    raw_attributes: Optional[JSON] = strawberry.field(
        default_factory=dict,
        deprecation_reason="Deprecated due to  change in WorkOS API.",
    )


@strawberry.type
class DirectoryUser:
    id: str
    idp_id: str
    directory_id: str
    organization_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    emails: List[DirectoryUserEmail] = strawberry.field(default_factory=list)
    username: Optional[str] = None
    groups: List[DirectoryGroup] = strawberry.field(default_factory=list)
    state: DirectoryUserState
    raw_attributes: Optional[JSON] = strawberry.field(
        default_factory=dict,
        deprecation_reason="Deprecated due to change in WorkOS API. Use custom_attributes.",
    )
    custom_attributes: JSON = strawberry.field(default_factory=dict)
    role: Optional[JSON] = None
    slug: Optional[str] = None
    created_at: str
    updated_at: str


class WorkOSDirectoryUserAPIResponse(TypedDict):
    data: list[DirectoryUser]


@strawberry.type
class WorkOSDirectoryUsersResponseType:
    data: list[DirectoryUser]
    is_cached: Optional[bool] = False
