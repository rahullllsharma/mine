import datetime
import json
import uuid
from typing import List, Optional

import strawberry
from pydantic import BaseModel
from strawberry.scalars import JSON

from worker_safety_service import models
from worker_safety_service.context import Info
from worker_safety_service.dal.configurations import (
    AttributeConfigurationExt,
    EntityConfigurationExt,
)
from worker_safety_service.models import DictModel, Supervisor, User
from worker_safety_service.permissions import Permission as PermissionEnum
from worker_safety_service.permissions import permissions_for_role
from worker_safety_service.types import (
    DefaultOrderByField,
    FormListOrderByField,
    LibraryTaskOrderByField,
    LocationFilterByField,
    LocationOrderByField,
    OrderBy,
    OrderByDirection,
    ProjectLocationOrderByField,
    ProjectOrderByField,
    TaskOrderByField,
)

OrderByFieldType = strawberry.enum(DefaultOrderByField, name="OrderByField")
LocationOrderByFieldType = strawberry.enum(
    LocationOrderByField, name="LocationOrderByField"
)
FormListOrderByFieldType = strawberry.enum(FormListOrderByField)
LibraryTaskOrderByFieldType = strawberry.enum(
    LibraryTaskOrderByField, name="LibraryTaskOrderByField"
)
TaskOrderByFieldType = strawberry.enum(TaskOrderByField, name="TaskOrderByField")
ProjectOrderByFieldType = strawberry.enum(
    ProjectOrderByField, name="ProjectOrderByField"
)
ProjectLocationOrderByFieldType = strawberry.enum(
    ProjectLocationOrderByField, name="ProjectLocationOrderByField"
)
OrderByDirectionType = strawberry.enum(OrderByDirection)
LocationFilterByFieldType = strawberry.enum(
    LocationFilterByField, name="LocationFilterByField"
)
UserPreferenceEntityType = strawberry.enum(models.UserPreferenceEntityType)


@strawberry.scalar(
    parse_value=lambda v: json.loads(v),
    description="The JSONScalar scalar type is a serialized JSON object.",
)
class JSONScalar(str):
    pass


@strawberry.scalar(
    parse_value=(
        lambda v: json.loads(v) if isinstance(v, (str, bytes, bytearray)) else v
    ),
    description="The DictScalar scalar type is a serialized JSON object.",
)
class DictScalar(DictModel):
    pass


@strawberry.type(name="User")
class UserType:
    id: uuid.UUID
    name: str
    first_name: str | None = None
    last_name: str | None = None

    @staticmethod
    def from_orm(user: User) -> "UserType":
        return UserType(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.get_name(),
        )


Permission = strawberry.enum(PermissionEnum)


@strawberry.experimental.pydantic.type(
    name="AttributeConfiguration",
    model=AttributeConfigurationExt,
    all_fields=False,
)
class AttributeConfigurationType:
    key: strawberry.auto
    label: strawberry.auto
    labelPlural: strawberry.auto
    visible: strawberry.auto
    required: strawberry.auto
    filterable: strawberry.auto

    defaultLabel: strawberry.auto
    defaultLabelPlural: strawberry.auto
    mandatory: strawberry.auto

    # Only difference
    mappings: Optional[JSON] = None


@strawberry.type(name="WorkPackageConfiguration")
@strawberry.experimental.pydantic.type(
    name="EntityConfiguration",
    model=EntityConfigurationExt,
    all_fields=True,
)
class EntityConfigurationType:
    pass


@strawberry.type(name="TenantConfigurations")
class TenantConfigurationsType:
    @strawberry.field()
    async def entities(self, info: Info) -> List[EntityConfigurationType]:
        entity_cfgs = await info.context.configurations.get_entities()
        ret = list(map(EntityConfigurationType.from_pydantic, entity_cfgs))
        return ret


@strawberry.type(name="WorkOS")
class WorkOSType:
    workos_org_id: str
    workos_directory_id: str

    @staticmethod
    def from_orm(workos: models.WorkOS) -> "WorkOSType":
        return WorkOSType(
            workos_org_id=workos.workos_org_id,
            workos_directory_id=workos.workos_directory_id,
        )


@strawberry.type(name="MyTenant")
class MyTenantType:
    name: str
    auth_realm: str | None = None
    display_name: str
    workos: List[WorkOSType]

    @strawberry.field()
    async def configurations(self, info: Info) -> TenantConfigurationsType:
        return TenantConfigurationsType()

    @staticmethod
    def from_orm(tenant: models.Tenant) -> "MyTenantType":
        workos_entries = [WorkOSType.from_orm(entry) for entry in tenant.workos]
        return MyTenantType(
            name=tenant.tenant_name,
            display_name=tenant.display_name,
            auth_realm=tenant.auth_realm_name,
            workos=workos_entries,
        )


@strawberry.type(name="Department")
class DepartmentType:
    id: uuid.UUID
    opco_id: strawberry.Private[uuid.UUID]
    name: str
    created_at: datetime.datetime

    @strawberry.field
    async def opco(self, info: Info) -> "OpcoType":
        opco = await info.context.opcos.me.load(self.opco_id)
        assert opco
        return OpcoType.from_orm(opco)

    @staticmethod
    def from_orm(department: models.Department) -> "DepartmentType":
        return DepartmentType(
            id=department.id,
            name=department.name,
            opco_id=department.opco_id,
            created_at=department.created_at,
        )


@strawberry.type(name="Opco")
class OpcoType:
    id: uuid.UUID
    name: str
    full_name: Optional[str]
    parent_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime

    @strawberry.field
    async def departments(self, info: Info) -> list["DepartmentType"]:
        departments = await info.context.departments.by_opco.load(self.id)
        return [DepartmentType.from_orm(department) for department in departments]

    @strawberry.field
    async def parent_opco(self, info: Info) -> Optional["OpcoType"]:
        if self.parent_id:
            opco = await info.context.opcos.me.load(self.parent_id)
            if opco:
                return OpcoType.from_orm(opco)
        return None

    @staticmethod
    def from_orm(opco: models.Opco) -> "OpcoType":
        return OpcoType(
            id=opco.id,
            name=opco.name,
            full_name=opco.full_name,
            parent_id=opco.parent_id,
            created_at=opco.created_at,
        )


@strawberry.type(name="UserPreference")
class UserPreferenceType:
    id: uuid.UUID
    user_id: uuid.UUID
    entity_type: UserPreferenceEntityType
    contents: JSON
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @staticmethod
    def from_orm(user_preference: models.UserPreference) -> "UserPreferenceType":
        return UserPreferenceType(
            id=user_preference.id,
            user_id=user_preference.user_id,
            entity_type=user_preference.entity_type,
            contents=user_preference.contents,
            created_at=user_preference.created_at,
            updated_at=user_preference.updated_at,
        )


@strawberry.type(name="System")
class SystemType:
    version: str


@strawberry.type(name="Me")
class MeType:
    id: uuid.UUID
    name: str
    first_name: str | None = None
    last_name: str | None = None
    role: str | None = None
    email: str | None = None
    permissions: list[Permission] | None = None

    @strawberry.field
    async def tenant(self, info: Info) -> MyTenantType:
        tenant = await info.context.tenants.me_by_id.load(info.context.tenant_id)
        assert tenant
        return MyTenantType(
            name=tenant.tenant_name,
            display_name=tenant.display_name,
            workos=[WorkOSType.from_orm(entry) for entry in tenant.workos],
        )

    # TODO delete and replace with tenant.name on FE
    @strawberry.field
    async def tenant_name(self, info: Info) -> str:
        tenant = await info.context.tenants.me_by_id.load(info.context.tenant_id)
        assert tenant
        return tenant.tenant_name

    @strawberry.field
    async def opco(self, info: Info) -> Optional["OpcoType"]:
        opco = await info.context.opcos.by_user.load(self.id)
        if opco:
            return OpcoType.from_orm(opco)
        else:
            return None

    @strawberry.field
    async def user_preferences(self, info: Info) -> list[UserPreferenceType]:
        xs = await info.context.user_preference.by_user_id.load(self.id)
        return [UserPreferenceType.from_orm(x) for x in xs]

    @staticmethod
    def from_orm(user: User) -> "MeType":
        return MeType(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            name=user.get_name(),
            role=user.role,
            permissions=permissions_for_role(user.role),
        )


@strawberry.type(name="Manager")
class ManagerType:
    id: uuid.UUID
    name: str
    first_name: str | None = None
    last_name: str | None = None

    @staticmethod
    def from_orm(user: User) -> "ManagerType":
        return ManagerType(
            id=user.id,
            name=user.get_name(prefix_on_empty="Manager"),
            first_name=user.first_name,
            last_name=user.last_name,
        )


@strawberry.type(name="Supervisor")
class SupervisorType:
    id: uuid.UUID
    name: str
    first_name: str | None = None
    last_name: str | None = None

    @staticmethod
    def from_orm(user: User) -> "SupervisorType":
        return SupervisorType(
            id=user.id,
            name=user.get_name(prefix_on_empty="Supervisor"),
            first_name=user.first_name,
            last_name=user.last_name,
        )


@strawberry.type(name="BaseSupervisor")
class BaseSupervisorType:
    id: uuid.UUID
    name: str  # TODO delete (check FE)
    external_key: str
    tenant_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None

    @staticmethod
    def from_orm(supervisor: Supervisor) -> "BaseSupervisorType":
        return BaseSupervisorType(
            id=supervisor.id,
            name=supervisor.external_key,
            external_key=supervisor.external_key,
            tenant_id=supervisor.tenant_id,
            user_id=supervisor.user_id,
        )


FileCategoryType = strawberry.enum(models.FileCategory)


@strawberry.experimental.pydantic.type(
    model=models.File,
    name="File",
)
class File:
    url: strawberry.auto
    name: strawberry.auto
    display_name: strawberry.auto
    size: strawberry.auto
    date: strawberry.auto
    time: strawberry.auto
    mimetype: strawberry.auto
    category: Optional[FileCategoryType]
    md5: strawberry.auto
    crc32c: strawberry.auto
    description: strawberry.auto

    @strawberry.field()
    async def id(self, info: Info) -> str:
        return info.context.files.blob_id_from_unsigned_url(self.url)

    @strawberry.field()
    async def signed_url(self, info: Info) -> str:
        blob = info.context.files.blob_id_from_unsigned_url(self.url)
        return await info.context.files.signed_urls.load(blob)

    @strawberry.field()
    async def exists(self, info: Info) -> bool:
        blob = info.context.files.blob_id_from_unsigned_url(self.url)
        return await info.context.files.exists.load(blob)


@strawberry.experimental.pydantic.input(model=models.File, all_fields=True)
class FileInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.SignedPostPolicy,
    name="SignedPostPolicy",
    all_fields=True,
)
class SignedPostPolicy:
    """Google Cloud Storage Post Policy for file upload
    id: str = Blob name
    url: str = URL to GCS bucket
    fields: str = form data to include in POST request or HTML form as JSON string
    """

    @staticmethod
    def from_policy(policy: dict) -> "SignedPostPolicy":
        return SignedPostPolicy(
            id=policy["id"],
            url=policy["url"],
            fields=json.dumps(policy["fields"]),
        )


@strawberry.input(name="OrderBy")
class OrderByInput:
    field: OrderByFieldType
    direction: OrderByDirectionType


@strawberry.input(name="LocationOrderBy")
class LocationOrderByInput:
    field: LocationOrderByFieldType
    direction: OrderByDirectionType


@strawberry.input(name="FormListOrderBy")
class FormListOrderByInput:
    field: FormListOrderByField
    direction: OrderByDirectionType


@strawberry.input(name="LibraryTaskOrderBy")
class LibraryTaskOrderByInput:
    field: LibraryTaskOrderByFieldType
    direction: OrderByDirectionType


@strawberry.input(name="ProjectOrderBy")
class ProjectOrderByInput:
    field: ProjectOrderByFieldType
    direction: OrderByDirectionType


@strawberry.input(name="ProjectLocationOrderBy")
class ProjectLocationOrderByInput:
    field: ProjectLocationOrderByFieldType
    direction: OrderByDirectionType


@strawberry.input(name="TaskOrderBy")
class TaskOrderByInput:
    field: TaskOrderByFieldType
    direction: OrderByDirectionType


def order_by_to_pydantic(
    order_by: (
        Optional[list[OrderByInput]]
        | Optional[list[LibraryTaskOrderByInput]]
        | Optional[list[ProjectOrderByInput]]
        | Optional[list[ProjectLocationOrderByInput]]
        | Optional[list[TaskOrderByInput]]
        | Optional[list[FormListOrderByInput]]
        | Optional[list[LocationOrderByInput]]
    ),
) -> list[OrderBy] | None:
    if order_by:
        return [OrderBy(field=i.field.value, direction=i.direction) for i in order_by]
    else:
        return None


@strawberry.input(name="LocationFilterBy")
class LocationFilterByInput:
    field: LocationFilterByFieldType
    values: list[str]


class InternalLocationFilterBy(BaseModel):
    library_region_ids: list[uuid.UUID] | None = None
    library_division_ids: list[uuid.UUID] | None = None
    # FIXME: To be deprecated
    library_project_type_ids: list[uuid.UUID] | None = None
    work_type_ids: list[uuid.UUID] | None = None
    project_ids: list[uuid.UUID] | None = None
    contractor_ids: list[uuid.UUID] | None = None
    supervisor_ids: list[uuid.UUID] | None = None
    risk_levels: list[models.RiskLevel] | None = None
    project_status: list[models.ProjectStatus] | None = None


RISK_LEVEL_MAPPER = {i.name: i.value for i in models.RiskLevel}
PROJECT_STATUS_MAPPER = {i.value: i for i in models.ProjectStatus}
INTERNAL_LOCATION_FILTER_MAPPER = {
    LocationFilterByField.RISK.value: "risk_levels",
    LocationFilterByField.REGIONS.value: "library_region_ids",
    LocationFilterByField.DIVISIONS.value: "library_division_ids",
    # FIXME: To be deprecated
    LocationFilterByField.TYPES.value: "library_project_type_ids",
    LocationFilterByField.WORK_TYPES.value: "work_type_ids",
    LocationFilterByField.PROJECT.value: "project_ids",
    LocationFilterByField.CONTRACTOR.value: "contractor_ids",
    LocationFilterByField.SUPERVISOR.value: "supervisor_ids",
    LocationFilterByField.PROJECT_STATUS.value: "project_status",
}
