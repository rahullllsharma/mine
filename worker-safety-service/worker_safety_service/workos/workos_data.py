import asyncio
import dataclasses
import json
import time
import uuid
from typing import Any, List, Optional

from httpx import AsyncClient, Limits
from pydantic.types import Json

from worker_safety_service.config import settings
from worker_safety_service.constants import GeneralConstants
from worker_safety_service.redis_client import create_redis_client
from worker_safety_service.urbint_logging import get_logger

from .types import (
    DirectoryGroup,
    DirectoryUser,
    DirectoryUserEmail,
    DirectoryUserState,
    WorkOSDirectoryUserAPIResponse,
    WorkOSDirectoryUsersResponseType,
)

logger = get_logger(__name__)

HTTPClient = AsyncClient(
    timeout=settings.HTTP_TIMEOUT,
    limits=Limits(
        max_connections=settings.HTTP_MAX_CONNECTIONS,
        max_keepalive_connections=settings.HTTP_MAX_KEEPALIVE_CONNECTIONS,
    ),
)


async def shutdown_http_client() -> None:
    await HTTPClient.aclose()


@dataclasses.dataclass
class WorkOSRESTAPIResponse:
    data: list


@dataclasses.dataclass
class DirectoryUsersQuery:
    group: Optional[str]
    limit: Optional[str]
    before: Optional[str]
    after: Optional[str]
    order: Optional[str]

    def to_query_params(self) -> dict:
        params = {
            "limit": 100,
            "group": self.group,
            "before": self.before,
            "after": self.after,
            "order": self.order,
        }

        return {k: v for k, v in params.items() if v is not None}


class WorkOSCrewData:
    def __init__(self) -> None:
        self.redis_client = create_redis_client()

    async def fetch_cache(self, tenant_id: uuid.UUID) -> Json:
        key_name = f"{GeneralConstants.WORKOS_CREW_KEY_PREFIX}_{tenant_id}"
        data = await self.redis_client.get(key_name)
        if data:
            data = json.loads(data)
        return data

    async def update_cache(
        self, data: List[DirectoryUser], tenant_id: uuid.UUID
    ) -> None:
        key_name = f"{GeneralConstants.WORKOS_CREW_KEY_PREFIX}_{tenant_id}"
        serialized_data = []
        for item in data:
            value = item.__dict__
            serialized_data.append(value)
        await self.redis_client.set(
            key_name, value=json.dumps(serialized_data), ex=86400
        )

    async def deserialize_emails(self, data: List) -> List[DirectoryUser]:
        typed_data = []
        for item in data:
            if not isinstance(item, DirectoryUser):
                item = DirectoryUser(**item)
            typed_data.append(item)
            emails = []
            for email in item.emails:
                if not isinstance(email, DirectoryUserEmail):
                    email = DirectoryUserEmail(**email)
                emails.append(email)
            item.emails = emails
        return typed_data

    async def fetch_workos_crew_info(
        self,
        directory_ids: List[str],
        params: DirectoryUsersQuery,
        tenant_id: uuid.UUID,
        update_cache: Optional[bool] = False,
    ) -> WorkOSDirectoryUsersResponseType:
        result = await self.fetch_cache(tenant_id)
        is_cached = True
        if not result or update_cache:
            is_cached = False
            result = await WorkOSClient.get_directory_users_for_directory_ids(
                directory_ids=directory_ids, params=params
            )
            await self.update_cache(result, tenant_id)
        typed_data = await self.deserialize_emails(result)
        return WorkOSDirectoryUsersResponseType(data=typed_data, is_cached=is_cached)


class WorkOSClient:
    @classmethod
    async def get_directory_users_for_directory_ids(
        cls, directory_ids: list[str], params: DirectoryUsersQuery
    ) -> List[DirectoryUser]:
        combined_data = []

        api_calls = [
            WorkOSClient.get_all_directory_users(directory_id, params)
            for directory_id in directory_ids
        ]

        responses = await asyncio.gather(*api_calls)

        for response in responses:
            combined_data.extend(response["data"])

        combined_data = await WorkOSClient.format_directory_data(combined_data)
        return combined_data

    @classmethod
    async def format_directory_data(
        cls, combined_data: List[DirectoryUser]
    ) -> List[DirectoryUser]:
        formatted_combined_data = []
        default_raw_attributes = {
            "meta": {"resource_type": "User"},
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
                "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User",
            ],
        }
        for data in combined_data:
            formatted_data = {**data.__dict__}
            emails = [
                {"primary": email.primary, "type": email.type, "value": email.value}
                for email in data.emails
            ]
            groups = [
                {
                    "id": group.id,
                    "name": group.name,
                    "created_at": group.created_at,
                    "updated_at": group.updated_at,
                }
                for group in data.groups
            ]
            formatted_data["custom_attributes"]["emails"] = emails
            formatted_data["emails"] = emails
            formatted_data["groups"] = groups

            if not data.raw_attributes:
                custom_attr = data.custom_attributes or {}
                formatted_name = "{} {}".format(data.first_name, data.last_name)
                name = custom_attr.get("displayName", formatted_name)
                raw_attributes = {
                    **default_raw_attributes,
                    **{
                        "title": data.job_title,
                        "name": {
                            "formatted": formatted_name,
                            "givenName": data.first_name,
                            "familyName": data.last_name,
                        },
                        "active": data.state,
                        "nickName": "",
                        "emails": emails,
                        "userName": data.username,
                        "externalId": data.idp_id,
                        "displayName": name,
                        "manager_id": custom_attr.get("manager_id"),
                        "manager_name": "",
                        "custom_DisplayName": custom_attr.get(
                            "custom_DisplayName", name
                        ),
                        "custom_EmployeeNumber": custom_attr.get("employeeNumber"),
                        "urn:ietf:params:scim:schemas:extension:enterprise:2.0:User": {
                            "manager": {"value": ""},
                            "department": custom_attr.get("department_name", ""),
                            "organization": "",
                            "employeeNumber": custom_attr.get("employeeNumber"),
                        },
                    },
                }
                formatted_data["raw_attributes"] = raw_attributes
            formatted_combined_data.append(DirectoryUser(**formatted_data))
        return formatted_combined_data

    @classmethod
    async def get_all_directory_users(
        cls, directory_id: str, query: DirectoryUsersQuery
    ) -> WorkOSDirectoryUserAPIResponse:
        all_users = []

        response = await WorkOSClient.directory_users(directory_id, query)
        all_users.extend(response.get("data"))

        while response.get("before"):
            time.sleep(0.5)
            query.before = response.get("before")
            response = await WorkOSClient.directory_users(directory_id, query)
            all_users.extend(response.get("data"))

        sorted_results = sorted(
            all_users, key=lambda usr: usr.raw_attributes.get("displayName", "").lower()
        )

        return {"data": sorted_results}

    @classmethod
    async def directory_users(
        cls, directory_id: str, query: DirectoryUsersQuery
    ) -> Any:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.WORKOS_AUTHORIZATION_TOKEN}",
        }

        url = f"{settings.WORKOS_BASE_URL}/directory_users"

        query_params = query.to_query_params()
        query_params["directory"] = directory_id

        response = await HTTPClient.get(url, params=query_params, headers=headers)
        response.raise_for_status()
        resp_data = response.json()

        directory_users = []

        for user_data in resp_data.get("data"):
            emails = [
                DirectoryUserEmail(
                    type=email.get("type"),
                    value=email.get("value"),
                    primary=email.get("primary"),
                )
                for email in user_data.get("emails", [])
            ]

            groups = [
                DirectoryGroup(
                    id=group.get("id", ""),
                    idp_id=group.get("idp_id", ""),
                    directory_id=group.get("directory_id", ""),
                    organization_id=group.get("organization_id"),
                    name=group.get("name", ""),
                    created_at=group.get("created_at", ""),
                    updated_at=group.get("updated_at", ""),
                    raw_attributes=group.get("raw_attributes", {}),
                )
                for group in user_data.get("groups", [])
            ]

            directory_user = DirectoryUser(
                id=user_data["id"],
                idp_id=user_data["idp_id"],
                directory_id=user_data["directory_id"],
                organization_id=user_data.get("organization_id"),
                first_name=user_data.get("first_name"),
                last_name=user_data.get("last_name"),
                job_title=user_data.get("job_title"),
                emails=emails,
                username=user_data.get("username"),
                groups=groups,
                state=DirectoryUserState(user_data["state"]),
                custom_attributes=user_data.get("custom_attributes", {}),
                raw_attributes=user_data.get("raw_attributes", {}),
                role=user_data.get("role"),
                slug=user_data.get("role", {}).get("slug"),
                created_at=user_data["created_at"],
                updated_at=user_data["updated_at"],
            )
            directory_users.append(directory_user)

        return {"data": directory_users, "before": resp_data["list_metadata"]["before"]}
