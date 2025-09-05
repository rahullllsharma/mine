import asyncio
import datetime
import json
import uuid
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Iterable, List, Optional, cast

import strawberry
from fastapi.encoders import jsonable_encoder
from pydantic import validator
from strawberry.scalars import JSON
from strawberry.types.nodes import Selection

from worker_safety_service import models
from worker_safety_service.audit_events.dataclasses import (
    AuditEventTypeInput,
    ProjectDiff,
)
from worker_safety_service.context import Info
from worker_safety_service.dal.configurations import (
    AttributeConfiguration,
    EntityConfiguration,
)
from worker_safety_service.dal.ingest import IngestType as DALIngestType
from worker_safety_service.dal.library import LibraryFilterType as DALLibraryFilterType
from worker_safety_service.graphql.common import (
    BaseSupervisorType,
    LibraryTaskOrderByInput,
    ManagerType,
    OrderByInput,
    SupervisorType,
    TaskOrderByInput,
    UserType,
    order_by_to_pydantic,
)
from worker_safety_service.graphql.common.types import DictScalar, FileInput, JSONScalar
from worker_safety_service.graphql.permissions import CanReadProjectAudits
from worker_safety_service.models import (
    Activity,
    ApplicabilityLevel,
    DailyReport,
    EnergyLevel,
    EnergyType,
    LibraryActivityGroup,
    LibrarySiteCondition,
    LibraryTaskLibraryHazardLink,
    SiteCondition,
    Supervisor,
    User,
    WorkType,
)
from worker_safety_service.models.audit_events import AuditDiffType
from worker_safety_service.models.audit_events import (
    AuditObjectType as AuditObjectTypeModel,
)
from worker_safety_service.models.consumer_models import Incident, IncidentSeverityEnum
from worker_safety_service.models.forms import JSBFiltersOnEnum
from worker_safety_service.models.jsb_supervisor import JSBSupervisorLink
from worker_safety_service.models.library import TypeOfControl
from worker_safety_service.models.standard_operating_procedures import (
    StandardOperatingProcedure,
)
from worker_safety_service.risk_model import triggers
from worker_safety_service.risk_model.configs.tenant_metric_configs import (
    TaskSpecificRiskScoreMetricConfig,
)
from worker_safety_service.urbint_logging import get_logger
from worker_safety_service.utils import parse_input_date, validate_duplicates

logger = get_logger(__name__)


def snake_to_camel_case(s: str) -> str:
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def dict_keys_snake_to_camel(d: dict) -> dict:
    new_dict = {}
    for key, value in d.items():
        new_key = snake_to_camel_case(key)
        if isinstance(value, dict):
            value = dict_keys_snake_to_camel(value)
        elif isinstance(value, list):
            value = [
                dict_keys_snake_to_camel(item) if isinstance(item, dict) else item
                for item in value
            ]
        new_dict[new_key] = value
    return new_dict


@strawberry.enum
class ControlStatus(Enum):
    IMPLEMENTED = "implemented"
    NOT_IMPLEMENTED = "not_implemented"
    NOT_APPLICABLE = "not_applicable"


@strawberry.input
class RecalculateInput:
    trigger: triggers.Triggers
    id: uuid.UUID


@strawberry.interface
class Auditable:
    id: uuid.UUID


LibraryFilterType = strawberry.enum(DALLibraryFilterType)
ProjectStatus = strawberry.enum(models.ProjectStatus)
RiskLevel = strawberry.enum(models.RiskLevel)
ActivityStatus = strawberry.enum(models.ActivityStatus)
TaskStatus = strawberry.enum(models.TaskStatus)
IngestType = strawberry.enum(DALIngestType)
IncidentSeverity = strawberry.enum(IncidentSeverityEnum)
FormDefinitionStatus = strawberry.enum(models.FormDefinitionStatus)
FormStatus = strawberry.enum(models.FormStatus, name="FormStatus")
SourceInformation = strawberry.enum(models.SourceInformation, name="SourceInformation")
EnergyLevelEnum = strawberry.enum(EnergyLevel)
EnergyTypeEnum = strawberry.enum(EnergyType)
ApplicabilityLevelEnum = strawberry.enum(ApplicabilityLevel)
ControlTypeEnum = strawberry.enum(TypeOfControl)
JSBFilterOnEnum = strawberry.enum(JSBFiltersOnEnum)
LocationType = strawberry.enum(models.LocationType)
FormsType = strawberry.enum(models.FormType)
CrewInformationTypes = strawberry.enum(models.CrewInformationTypes, name="CrewType")
SourceAppInformation = strawberry.enum(
    models.SourceAppInformation, name="SourceAppInformation"
)
NotificationType = strawberry.enum(models.NotificationType, name="NotificationsType")


@strawberry.experimental.pydantic.input(model=models.TenantCreate, all_fields=True)
class CreateTenantInput:
    pass


@strawberry.experimental.pydantic.input(model=models.TenantEdit, all_fields=True)
class EditTenantInput:
    pass


@strawberry.type(name="JSBSupervisor")
class JSBSupervisorType:
    id: str
    name: str
    email: str

    @staticmethod
    def from_orm(jsb_supervisor: JSBSupervisorLink) -> "JSBSupervisorType":
        return JSBSupervisorType(
            id=jsb_supervisor.manager_id,
            name=jsb_supervisor.manager_name,
            email=jsb_supervisor.manager_email,
        )


@strawberry.type(name="Incident")
class IncidentType:
    id: uuid.UUID
    incident_date: datetime.date
    incident_type: str
    incident_id: Optional[str]
    task_type_id: Optional[uuid.UUID]
    severity_code: Optional[IncidentSeverityEnum]
    description: str
    tenant_id: strawberry.Private[uuid.UUID]
    task_type: Optional[str]
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def severity(self) -> str | None:
        if self.severity_code:
            return self.severity_code.to_ml_code()
        return None

    @staticmethod
    def from_orm(
        incident: Incident,
    ) -> "IncidentType":
        return IncidentType(
            id=incident.id,
            incident_date=incident.incident_date,
            incident_type=incident.incident_type,
            incident_id=incident.incident_id,
            task_type_id=incident.task_type_id,
            severity_code=incident.severity,
            description=incident.description,
            tenant_id=incident.tenant_id,
            task_type=incident.task_type,
            archived_at=incident.archived_at,
        )


@strawberry.type(name="FormDefinition")
class FormDefinitionType:
    id: uuid.UUID
    name: str
    external_key: str
    status: FormDefinitionStatus = strawberry.field(default=FormDefinitionStatus.ACTIVE)

    @staticmethod
    def from_orm(form_definition: models.FormDefinition) -> "FormDefinitionType":
        return FormDefinitionType(
            id=form_definition.id,
            name=form_definition.name,
            status=form_definition.status,
            external_key=form_definition.external_key,
        )


@strawberry.type(name="LibraryControl")
class LibraryControlType:
    id: uuid.UUID
    name: str
    is_applicable: bool
    ppe: bool | None = strawberry.field(default=False)
    control_type: ControlTypeEnum | None = strawberry.field(default=None)
    archived_at: Optional[datetime.datetime]

    @staticmethod
    def from_orm(library_control: models.LibraryControl) -> "LibraryControlType":
        return LibraryControlType(
            id=library_control.id,
            name=library_control.name,
            is_applicable=True,
            ppe=library_control.ppe,
            control_type=library_control.type,
            archived_at=library_control.archived_at,
        )


@strawberry.type(name="LinkedLibraryControl")
class LinkedLibraryControlType:
    id: uuid.UUID
    is_applicable: bool
    ppe: bool | None = strawberry.field(default=False)
    control_type: ControlTypeEnum | None = strawberry.field(default=None)
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = await info.context.tenant_library_control_settings.me.load(
            self.id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_control = await info.context.library_controls.me.load(self.id)
            if not library_control:
                logger.exception(f"LibraryControl with id {self.id} not found")
                return ""
            return library_control.name

    @staticmethod
    def from_orm(library_control: models.LibraryControl) -> "LinkedLibraryControlType":
        return LinkedLibraryControlType(
            id=library_control.id,
            is_applicable=True,
            ppe=library_control.ppe,
            control_type=library_control.type,
            archived_at=library_control.archived_at,
        )


@strawberry.type(name="TaskApplicabilityLevel")
class LibraryTaskLibraryHazardLinkType:
    task_id: uuid.UUID
    applicability_level: ApplicabilityLevelEnum

    @staticmethod
    def from_orm(
        applicability_level: LibraryTaskLibraryHazardLink,
    ) -> "LibraryTaskLibraryHazardLinkType":
        return LibraryTaskLibraryHazardLinkType(
            task_id=applicability_level.library_task_id,
            applicability_level=applicability_level.applicability_level,
        )


@strawberry.type(name="LibraryHazard")
class LibraryHazardType:
    id: uuid.UUID
    name: str
    is_applicable: bool
    parent_type: strawberry.Private[LibraryFilterType | None]
    parent_id: strawberry.Private[uuid.UUID | None]
    energy_type: Optional[EnergyTypeEnum]
    energy_level: Optional[EnergyLevelEnum]
    library_task_id: strawberry.Private[uuid.UUID | None]
    image_url: str
    image_url_png: str
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def controls(
        self, info: Info, order_by: Optional[list[OrderByInput]] = None
    ) -> list[LibraryControlType]:
        if self.parent_type == LibraryFilterType.TASK:
            loaded_controls = await info.context.library.task_controls(
                order_by=order_by_to_pydantic(order_by)
            ).load((self.parent_id, self.id))
        elif self.parent_type == LibraryFilterType.SITE_CONDITION:
            loaded_controls = await info.context.library.site_condition_controls(
                order_by=order_by_to_pydantic(order_by)
            ).load((self.parent_id, self.id))
        else:
            loaded_controls = await info.context.library.get_controls(
                type_key=None,
                library_hazard_id=self.id,
                order_by=order_by_to_pydantic(order_by),
            )

        return [
            LibraryControlType.from_orm(library_control)
            for library_control in loaded_controls
        ]

    @strawberry.field()
    async def task_applicability_levels(
        self, info: Info
    ) -> list[LibraryTaskLibraryHazardLinkType]:
        applicability_levels = (
            await info.context.library.task_applicability_levels.load(
                (self.id, self.library_task_id)
            )
        )

        return [
            LibraryTaskLibraryHazardLinkType.from_orm(applicability_level)
            for applicability_level in applicability_levels
        ]

    @staticmethod
    def from_orm(
        library_hazard: models.LibraryHazard,
        parent_type: LibraryFilterType | None = None,
        parent_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
    ) -> "LibraryHazardType":
        """`parent_id` as `LibraryTaskType.id` or `LibrarySiteConditionType.id`"""
        return LibraryHazardType(
            id=library_hazard.id,
            name=library_hazard.name,
            is_applicable=True,
            parent_type=parent_type,
            parent_id=parent_id,
            energy_level=library_hazard.energy_level,
            energy_type=library_hazard.energy_type,
            library_task_id=library_task_id,
            image_url=library_hazard.image_url,
            image_url_png=library_hazard.image_url_png,
            archived_at=library_hazard.archived_at,
        )


@strawberry.type(name="LinkedLibraryHazard")
class LinkedLibraryHazardType:
    id: uuid.UUID
    is_applicable: bool
    parent_type: strawberry.Private[LibraryFilterType | None]
    parent_id: strawberry.Private[uuid.UUID | None]
    energy_type: Optional[EnergyTypeEnum]
    energy_level: Optional[EnergyLevelEnum]
    library_task_id: strawberry.Private[uuid.UUID | None]
    image_url: str
    image_url_png: str
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = await info.context.tenant_library_hazard_settings.me.load(
            self.id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_hazard = await info.context.library_hazards.me.load(self.id)
            if not library_hazard:
                logger.exception(f"LibraryHazard with id {self.id} not found")
                return ""
            return library_hazard.name

    @strawberry.field()
    async def controls(
        self, info: Info, order_by: Optional[list[OrderByInput]] = None
    ) -> list[LinkedLibraryControlType]:
        if self.parent_type == LibraryFilterType.TASK:
            loaded_controls = await info.context.library.task_controls_v2(
                order_by=order_by_to_pydantic(order_by)
            ).load((self.parent_id, self.id))
        elif self.parent_type == LibraryFilterType.SITE_CONDITION:
            loaded_controls = await info.context.library.site_condition_controls_v2(
                order_by=order_by_to_pydantic(order_by)
            ).load((self.parent_id, self.id))
        else:
            loaded_controls = await info.context.library.get_controls_v2(
                type_key=None,
                library_hazard_id=self.id,
                order_by=order_by_to_pydantic(order_by),
            )

        return [
            LinkedLibraryControlType.from_orm(library_control)
            for library_control in loaded_controls
        ]

    @strawberry.field()
    async def task_applicability_levels(
        self, info: Info
    ) -> list[LibraryTaskLibraryHazardLinkType]:
        applicability_levels = (
            await info.context.library.task_applicability_levels.load(
                (self.id, self.library_task_id)
            )
        )

        return [
            LibraryTaskLibraryHazardLinkType.from_orm(applicability_level)
            for applicability_level in applicability_levels
        ]

    @staticmethod
    def from_orm(
        library_hazard: models.LibraryHazard,
        parent_type: LibraryFilterType | None = None,
        parent_id: uuid.UUID | None = None,
        library_task_id: uuid.UUID | None = None,
    ) -> "LinkedLibraryHazardType":
        """`parent_id` as `LibraryTaskType.id` or `LibrarySiteConditionType.id`"""
        return LinkedLibraryHazardType(
            id=library_hazard.id,
            is_applicable=True,
            parent_type=parent_type,
            parent_id=parent_id,
            energy_level=library_hazard.energy_level,
            energy_type=library_hazard.energy_type,
            library_task_id=library_task_id,
            image_url=library_hazard.image_url,
            image_url_png=library_hazard.image_url_png,
            archived_at=library_hazard.archived_at,
        )


@strawberry.type(name="WorkTypeWithActivityAliasType")
class WorkTypeWithActivityAliasType:
    id: uuid.UUID
    name: str
    core_work_type_ids: list[uuid.UUID] | None
    tenant_id: uuid.UUID | None
    code: Optional[str]
    alias: Optional[str]

    @staticmethod
    def from_orm(
        work_type: WorkType,
        alias: Optional[str] = None,
    ) -> "WorkTypeWithActivityAliasType":
        return WorkTypeWithActivityAliasType(
            id=work_type.id,
            name=work_type.name,
            core_work_type_ids=work_type.core_work_type_ids,
            tenant_id=work_type.tenant_id,
            code=work_type.code,
            alias=alias,
        )


@strawberry.type(name="LibraryActivityGroup")
class LibraryActivityGroupType:
    id: uuid.UUID
    name: str

    @strawberry.field()
    async def aliases(self, info: Info) -> List[Optional[str]]:
        work_type_ids = info.context.params.get("tenant_work_type_ids")
        key = (self.id, tuple(work_type_ids) if work_type_ids else ())
        activity_aliases = (
            await info.context.activity_work_type_settings.get_activity_aliases.load(
                key
            )
        )

        if activity_aliases and any(alias is not None for alias in activity_aliases):
            return cast(List[Optional[str]], activity_aliases)

        activity = await info.context.activities.by_id.load(self.id)

        if activity:
            return [activity.name]

        return []

    @strawberry.field()
    async def work_types(
        self, info: Info
    ) -> List[WorkTypeWithActivityAliasType] | None:
        """
        Returns a list of WorkTypeWithActivityAliasType for this activity group,
        using the get_work_types_and_aliases_by_library_tasks loader.
        Each work_type_id is sent as a separate key.
        """
        work_type_ids = info.context.params.get("tenant_work_type_ids") or []
        tenant_id = info.context.tenant_library_task_settings.tenant_id

        keys = [(work_type_id, self.id, tenant_id) for work_type_id in work_type_ids]
        results = await info.context.activity_work_type_settings.get_work_types_and_aliases_by_work_types.load_many(
            keys
        )

        work_types_with_aliases = []
        for result in results:
            for work_type_list in result.values():
                for work_type, alias in work_type_list:
                    work_types_with_aliases.append(
                        WorkTypeWithActivityAliasType(
                            id=work_type.id,
                            name=work_type.name,
                            core_work_type_ids=work_type.core_work_type_ids,
                            tenant_id=work_type.tenant_id,
                            code=work_type.code,
                            alias=alias,
                        )
                    )
        return work_types_with_aliases

    @strawberry.field
    async def tasks(
        self,
        info: Info,
        order_by: Optional[list[LibraryTaskOrderByInput]] = None,
    ) -> list["LibraryTaskType"]:
        library_tasks: list[
            models.LibraryTask
        ] = await info.context.library.tasks_by_activity_group(
            order_by=order_by_to_pydantic(order_by),
        ).load(
            self.id
        )
        return [
            LibraryTaskType.from_orm(library_task) for library_task in library_tasks
        ]

    @staticmethod
    def from_orm(
        activity_group: LibraryActivityGroup,
    ) -> "LibraryActivityGroupType":
        return LibraryActivityGroupType(id=activity_group.id, name=activity_group.name)


@strawberry.type(name="WorkType")
class WorkTypeType:
    id: uuid.UUID
    name: str
    core_work_type_ids: list[uuid.UUID] | None
    tenant_id: uuid.UUID | None
    code: Optional[str]

    @staticmethod
    def from_orm(
        work_type: WorkType,
    ) -> "WorkTypeType":
        return WorkTypeType(
            id=work_type.id,
            name=work_type.name,
            core_work_type_ids=work_type.core_work_type_ids,
            tenant_id=work_type.tenant_id,
            code=work_type.code,
        )


@strawberry.type(name="StandardOperatingProcedure")
class StandardOperatingProcedureType:
    id: uuid.UUID
    name: str
    link: str

    @staticmethod
    def from_orm(
        standard_operating_procedure: StandardOperatingProcedure,
    ) -> "StandardOperatingProcedureType":
        return StandardOperatingProcedureType(
            id=standard_operating_procedure.id,
            name=standard_operating_procedure.name,
            link=standard_operating_procedure.link,
        )


@strawberry.type(name="LibraryTask")
class LibraryTaskType:
    id: uuid.UUID
    name: str
    is_critical: bool
    category: Optional[str]
    hesp_score: int

    @strawberry.field()
    async def risk_level(self, info: Info) -> RiskLevel:
        thresholds = (
            await info.context.configurations.me.load(TaskSpecificRiskScoreMetricConfig)
        ).thresholds

        if thresholds is not None:
            if self.hesp_score < thresholds.low:
                return RiskLevel.LOW
            elif self.hesp_score < thresholds.medium:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.HIGH

        return RiskLevel.UNKNOWN

    @strawberry.field()
    async def activities_groups(
        self,
        info: Info,
    ) -> list[LibraryActivityGroupType] | None:
        library_task_activity_groups = (
            await info.context.library.activity_groups_by_library_task.load(self.id)
        )
        if library_task_activity_groups is not None:
            return [
                LibraryActivityGroupType.from_orm(library_task_activity_group)
                for library_task_activity_group in library_task_activity_groups
                if library_task_activity_group is not None
            ]
        return []

    @strawberry.field()
    async def work_types(
        self, info: Info, tenant_id: uuid.UUID | None = None
    ) -> list[WorkTypeType] | None:
        work_types = await info.context.library.work_types_by_library_task.load(self.id)
        if work_types:
            return [
                WorkTypeType.from_orm(work_type)
                for work_type in work_types
                if work_type is not None
            ]
        return None

    @strawberry.field()
    async def hazards(
        self, info: Info, order_by: list[OrderByInput] | None = None
    ) -> list[LibraryHazardType]:
        loaded_hazards = await info.context.library.task_hazards(
            order_by=order_by_to_pydantic(order_by)
        ).load(self.id)
        return [
            LibraryHazardType.from_orm(
                hazard,
                parent_type=LibraryFilterType.TASK,
                parent_id=self.id,
                library_task_id=self.id,
            )
            for hazard in loaded_hazards
        ]

    @strawberry.field()
    async def standard_operating_procedures(
        self, info: Info
    ) -> list[StandardOperatingProcedureType] | None:
        standard_operating_procedures = (
            await info.context.standard_operating_procedures.by_library_task.load(
                self.id
            )
        )
        return [
            StandardOperatingProcedureType.from_orm(standard_operating_procedure)
            for standard_operating_procedure in standard_operating_procedures or []
            if standard_operating_procedure is not None
        ]

    @staticmethod
    def from_orm(library_task: models.LibraryTask) -> "LibraryTaskType":
        return LibraryTaskType(
            id=library_task.id,
            name=library_task.name,
            is_critical=library_task.is_critical,
            category=library_task.category,
            hesp_score=library_task.hesp,
        )


@strawberry.type(name="LinkedLibraryTask")
class LinkedLibraryTaskType:
    id: uuid.UUID
    is_critical: bool
    category: Optional[str]
    hesp_score: int
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = await info.context.tenant_library_task_settings.me.load(
            self.id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_task = await info.context.library_tasks.me.load(self.id)
            if not library_task:
                logger.exception(f"LibraryTask with id {self.id} not found")
                return ""
            return library_task.name

    @strawberry.field()
    async def risk_level(self, info: Info) -> RiskLevel:
        thresholds = (
            await info.context.configurations.me.load(TaskSpecificRiskScoreMetricConfig)
        ).thresholds

        if thresholds is not None:
            if self.hesp_score < thresholds.low:
                return RiskLevel.LOW
            elif self.hesp_score < thresholds.medium:
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.HIGH

        return RiskLevel.UNKNOWN

    @strawberry.field()
    async def activities_groups(
        self,
        info: Info,
    ) -> list[LibraryActivityGroupType] | None:
        work_type_ids = info.context.params.get("tenant_work_type_ids")
        key = (self.id, tuple(work_type_ids) if work_type_ids else ())
        library_task_activity_groups = await info.context.library.work_type_linked_activity_groups_by_library_task.load(
            key
        )
        if library_task_activity_groups is not None:
            return [
                LibraryActivityGroupType.from_orm(library_task_activity_group)
                for library_task_activity_group in library_task_activity_groups
                if library_task_activity_group is not None
            ]
        return []

    @strawberry.field()
    async def work_types(
        self, info: Info, tenant_id: uuid.UUID | None = None
    ) -> list[WorkTypeType] | None:
        work_types = await info.context.library.work_types_by_library_task.load(self.id)
        if work_types:
            return [
                WorkTypeType.from_orm(work_type)
                for work_type in work_types
                if work_type is not None
            ]
        return None

    @strawberry.field()
    async def hazards(
        self, info: Info, order_by: list[OrderByInput] | None = None
    ) -> list[LinkedLibraryHazardType]:
        loaded_hazards = await info.context.library.task_hazards_v2(
            order_by=order_by_to_pydantic(order_by)
        ).load(self.id)
        return [
            LinkedLibraryHazardType.from_orm(
                hazard,
                parent_type=LibraryFilterType.TASK,
                parent_id=self.id,
                library_task_id=self.id,
            )
            for hazard in loaded_hazards
        ]

    @strawberry.field()
    async def standard_operating_procedures(
        self, info: Info
    ) -> list[StandardOperatingProcedureType] | None:
        standard_operating_procedures = (
            await info.context.standard_operating_procedures.by_library_task.load(
                self.id
            )
        )
        return [
            StandardOperatingProcedureType.from_orm(standard_operating_procedure)
            for standard_operating_procedure in standard_operating_procedures or []
            if standard_operating_procedure is not None
        ]

    @staticmethod
    def from_orm(library_task: models.LibraryTask) -> "LinkedLibraryTaskType":
        return LinkedLibraryTaskType(
            id=library_task.id,
            is_critical=library_task.is_critical,
            category=library_task.category,
            hesp_score=library_task.hesp,
            archived_at=library_task.archived_at,
        )


@strawberry.type(name="LinkedLibrarySiteCondition")
class LinkedLibrarySiteConditionType:
    id: uuid.UUID
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = (
            await info.context.tenant_library_site_condition_settings.me.load(self.id)
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_site_condition = await info.context.library_site_conditions.me.load(
                self.id
            )
            if not library_site_condition:
                logger.exception(f"LibrarySiteCondition with id {self.id} not found")
                return ""
            return library_site_condition.name

    @strawberry.field()
    async def hazards(
        self, info: Info, order_by: list[OrderByInput] | None = None
    ) -> list[LinkedLibraryHazardType]:
        loaded_hazards = await info.context.library.site_conditions_hazards_v2(
            order_by=order_by_to_pydantic(order_by)
        ).load(self.id)
        return [
            LinkedLibraryHazardType.from_orm(
                hazard,
                parent_type=LibraryFilterType.SITE_CONDITION,
                parent_id=self.id,
            )
            for hazard in loaded_hazards
        ]

    @strawberry.field()
    async def work_types(
        self, info: Info, tenant_id: uuid.UUID | None = None
    ) -> list[WorkTypeType] | None:
        work_types = (
            await info.context.library.work_types_by_library_site_condition.load(
                self.id
            )
        )
        if work_types:
            return [
                WorkTypeType.from_orm(work_type)
                for work_type in work_types
                if work_type is not None
            ]
        return None

    @staticmethod
    def from_orm(
        library_site_condition: models.LibrarySiteCondition,
    ) -> "LinkedLibrarySiteConditionType":
        return LinkedLibrarySiteConditionType(
            id=library_site_condition.id,
            archived_at=library_site_condition.archived_at,
        )


@strawberry.type(name="LibrarySiteCondition")
class LibrarySiteConditionType:
    id: uuid.UUID
    name: str
    archived_at: Optional[datetime.datetime]

    @strawberry.field()
    async def hazards(
        self, info: Info, order_by: list[OrderByInput] | None = None
    ) -> list[LibraryHazardType]:
        loaded_hazards = await info.context.library.site_conditions_hazards(
            order_by=order_by_to_pydantic(order_by)
        ).load(self.id)
        return [
            LibraryHazardType.from_orm(
                hazard,
                parent_type=LibraryFilterType.SITE_CONDITION,
                parent_id=self.id,
            )
            for hazard in loaded_hazards
        ]

    @staticmethod
    def from_orm(
        library_site_condition: models.LibrarySiteCondition,
    ) -> "LibrarySiteConditionType":
        return LibrarySiteConditionType(
            id=library_site_condition.id,
            name=library_site_condition.name,
            archived_at=library_site_condition.archived_at,
        )


@strawberry.type(name="LibraryDivision")
class LibraryDivisionType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(library_division: models.LibraryDivision) -> "LibraryDivisionType":
        return LibraryDivisionType(
            id=library_division.id,
            name=library_division.name,
        )


@strawberry.type(name="LibraryAsset")
class LibraryAssetType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(asset_type: models.LibraryAssetType) -> "LibraryAssetType":
        return LibraryAssetType(
            id=asset_type.id,
            name=asset_type.name,
        )


@strawberry.type(name="LibraryRegion")
class LibraryRegionType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(library_region: models.LibraryRegion) -> "LibraryRegionType":
        return LibraryRegionType(
            id=library_region.id,
            name=library_region.name,
        )


@strawberry.type(name="LibraryProjectType")
class LibraryProjectType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(
        library_project_type: models.LibraryProjectType,
    ) -> "LibraryProjectType":
        return LibraryProjectType(
            id=library_project_type.id,
            name=library_project_type.name,
        )


@strawberry.type(name="LibraryActivityType")
class LibraryActivityType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(activity_type: models.LibraryActivityType) -> "LibraryActivityType":
        return LibraryActivityType(
            id=activity_type.id,
            name=activity_type.name,
        )


@strawberry.type(name="Control")
class ControlType:
    id: uuid.UUID
    name: str
    status: ControlStatus
    isApplicable: bool = True


@strawberry.type(name="Hazard")
class HazardType:
    id: uuid.UUID
    name: str
    controls: list[ControlType]


@strawberry.type(name="SiteConditionHazardControl")
class SiteConditionHazardControlType:
    id: uuid.UUID
    is_applicable: bool
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    library_control: LibraryControlType

    @strawberry.field()
    async def name(self, info: Info) -> str:
        control_id = self.library_control.id
        tenant_setting = await info.context.tenant_library_control_settings.me.load(
            control_id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_control = await info.context.library_controls.me.load(control_id)
            if not library_control:
                logger.exception(f"LibraryControl with id {self.id} not found")
                return ""
            return library_control.name

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @staticmethod
    def from_orm(
        library_control: models.LibraryControl,
        control: models.SiteConditionControl,
    ) -> "SiteConditionHazardControlType":
        return SiteConditionHazardControlType(
            id=control.id,
            is_applicable=control.is_applicable,
            created_by_id=control.user_id,
            library_control=LibraryControlType.from_orm(library_control),
        )


@strawberry.type(name="SiteConditionHazard")
class SiteConditionHazardType:
    id: uuid.UUID
    is_applicable: bool
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    library_hazard: LibraryHazardType

    @strawberry.field()
    async def name(self, info: Info) -> str:
        hazard_id = self.library_hazard.id
        tenant_setting = await info.context.tenant_library_hazard_settings.me.load(
            hazard_id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_hazard = await info.context.library_hazards.me.load(hazard_id)
            if not library_hazard:
                logger.exception(f"LibraryHazard with id {self.id} not found")
                return ""
            return library_hazard.name

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def controls(
        self,
        info: Info,
        is_applicable: Optional[bool] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[SiteConditionHazardControlType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )

        return [
            SiteConditionHazardControlType.from_orm(library_control, control)
            for library_control, control in await info.context.site_conditions.controls(
                is_applicable=is_applicable,
                order_by=order_by_to_pydantic(order_by),
                filter_tenant_settings=filter_tenant_settings,
            ).load(self.id)
        ]

    @staticmethod
    def from_orm(
        library_hazard: models.LibraryHazard,
        hazard: models.SiteConditionHazard,
        library_site_condition_id: uuid.UUID,
    ) -> "SiteConditionHazardType":
        return SiteConditionHazardType(
            id=hazard.id,
            is_applicable=hazard.is_applicable,
            created_by_id=hazard.user_id,
            library_hazard=LibraryHazardType.from_orm(
                library_hazard,
                parent_type=LibraryFilterType.SITE_CONDITION,
                parent_id=library_site_condition_id,
            ),
        )


@strawberry.type(name="SiteCondition")
class SiteConditionType(Auditable):
    """
    This type returns ProjectLocationSiteCondition and ProjectLocationCalculationSiteCondition instances
    this can raise inconsistencies if the ids are used on a latter query.
    Might be worth to separate the concerns or changing it to an union type in a letter PR
    """

    id: uuid.UUID
    location_id: strawberry.Private[uuid.UUID]
    library_site_condition_id: strawberry.Private[uuid.UUID]
    # TODO: site_codition.risk_level is deprecated, needs to be removed
    risk_level: RiskLevel = strawberry.field(
        deprecation_reason="site_condition.risk_level is not used anymore, will be removed soon"
    )
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    is_manually_added: bool

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def hazards(
        self,
        info: Info,
        is_applicable: Optional[bool] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[SiteConditionHazardType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        return [
            SiteConditionHazardType.from_orm(
                library_hazard, hazard, self.library_site_condition_id
            )
            for library_hazard, hazard in await info.context.site_conditions.hazards(
                is_applicable=is_applicable,
                order_by=order_by_to_pydantic(order_by),
                filter_tenant_settings=filter_tenant_settings,
            ).load(self.id)
        ]

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = (
            await info.context.tenant_library_site_condition_settings.me.load(
                self.library_site_condition_id
            )
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_site_condition = await info.context.library_site_conditions.me.load(
                self.library_site_condition_id
            )
            if not library_site_condition:
                logger.exception(f"LibrarySiteCondition with id {self.id} not found")
                return ""
            return library_site_condition.name

    @strawberry.field()
    async def library_site_condition(
        self, info: Info
    ) -> "LinkedLibrarySiteConditionType":
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        key = (self.library_site_condition_id, filter_tenant_settings)
        library_site_conditions = await info.context.library_site_conditions.load_library_site_conditions_tenant.load(
            key
        )
        if not library_site_conditions:
            logger.exception(
                f"LibrarySiteCondition with id {self.library_site_condition_id} not found"
            )
            raise ValueError(
                f"LibrarySiteCondition with id {self.library_site_condition_id} not found"
            )
        return LinkedLibrarySiteConditionType.from_orm(library_site_conditions)

    @staticmethod
    def from_orm(
        site_condition: models.SiteCondition,
    ) -> "SiteConditionType":
        return SiteConditionType(
            id=site_condition.id,
            location_id=site_condition.location_id,
            library_site_condition_id=site_condition.library_site_condition_id,
            risk_level=RiskLevel.HIGH,
            created_by_id=site_condition.user_id,
            is_manually_added=site_condition.is_manually_added,
        )

    @strawberry.field()
    async def location(self, info: Info) -> "ProjectLocationType":
        location = await info.context.project_locations.with_archived.load(
            self.location_id
        )
        assert location
        return ProjectLocationType.from_orm(location)


@strawberry.type(name="TaskHazardControl")
class TaskHazardControlType:
    id: uuid.UUID
    is_applicable: bool
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    library_control: LibraryControlType

    @strawberry.field()
    async def name(self, info: Info) -> str:
        control_id = self.library_control.id
        tenant_setting = await info.context.tenant_library_control_settings.me.load(
            control_id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_control = await info.context.library_controls.me.load(control_id)
            if not library_control:
                logger.exception(f"LibraryControl with id {self.id} not found")
                return ""
            return library_control.name

    @strawberry.field()
    async def created_by(self, info: Info) -> UserType | None:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @staticmethod
    def from_orm(
        library_control: models.LibraryControl,
        control: models.TaskControl,
    ) -> "TaskHazardControlType":
        return TaskHazardControlType(
            id=control.id,
            is_applicable=control.is_applicable,
            created_by_id=control.user_id,
            library_control=LibraryControlType.from_orm(library_control),
        )


@strawberry.type(name="TaskHazard")
class TaskHazardType:
    id: uuid.UUID
    is_applicable: bool
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    library_hazard: LibraryHazardType

    @strawberry.field()
    async def name(self, info: Info) -> str:
        hazard_id = self.library_hazard.id
        tenant_setting = await info.context.tenant_library_hazard_settings.me.load(
            hazard_id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_hazard = await info.context.library_hazards.me.load(hazard_id)
            if not library_hazard:
                logger.exception(f"LibraryHazard with id {self.id} not found")
                return ""
            return library_hazard.name

    @strawberry.field()
    async def created_by(self, info: Info) -> UserType | None:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def controls(
        self,
        info: Info,
        is_applicable: bool | None = None,
        order_by: list[OrderByInput] | None = None,
    ) -> list[TaskHazardControlType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        return [
            TaskHazardControlType.from_orm(library_control, control)
            for library_control, control in await info.context.tasks.controls(
                is_applicable=is_applicable,
                order_by=order_by_to_pydantic(order_by),
                filter_tenant_settings=filter_tenant_settings,
            ).load(self.id)
        ]

    @staticmethod
    def from_orm(
        library_hazard: models.LibraryHazard,
        hazard: models.TaskHazard,
        library_task_id: uuid.UUID,
    ) -> "TaskHazardType":
        return TaskHazardType(
            id=hazard.id,
            is_applicable=hazard.is_applicable,
            created_by_id=hazard.user_id,
            library_hazard=LibraryHazardType.from_orm(
                library_hazard,
                parent_type=LibraryFilterType.TASK,
                parent_id=library_task_id,
            ),
        )


@strawberry.input
class DateRangeInput:
    start_date: datetime.date
    end_date: datetime.date


@strawberry.input
class RecieverInput:
    id: uuid.UUID
    name: str


@strawberry.input
class FormsNotificationsInput:
    form_type: FormsType
    receiver_ids: list[RecieverInput]
    notification_type: NotificationType
    created_at: Optional[datetime.datetime] = strawberry.field(default=None)


# Define the DynamicType type
@strawberry.type
class DatedRiskLevel:
    date: datetime.date
    risk_level: RiskLevel


@strawberry.type
class DatedSiteConditions:
    date: datetime.date
    site_conditions: list[SiteConditionType]


@strawberry.type(name="Task")
class TaskType(Auditable):
    id: uuid.UUID
    location_id: strawberry.Private[uuid.UUID]
    activity_id: strawberry.Private[Optional[uuid.UUID]]
    library_task_id: strawberry.Private[uuid.UUID]
    status: TaskStatus = strawberry.field(
        default=TaskStatus.NOT_STARTED,
        deprecation_reason="Will soon be replaced by status on Activity",
    )
    start_date: Optional[datetime.date] = strawberry.field(
        default=None,
        deprecation_reason="Will soon be replaced by start_date on Activity",
    )
    end_date: Optional[datetime.date] = strawberry.field(
        default=None, deprecation_reason="Will soon be replaced by end_date on Activity"
    )

    @strawberry.field()
    async def hazards(
        self,
        info: Info,
        is_applicable: Optional[bool] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[TaskHazardType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        return [
            TaskHazardType.from_orm(library_hazard, hazard, self.library_task_id)
            for library_hazard, hazard in await info.context.tasks.hazards(
                is_applicable=is_applicable,
                order_by=order_by_to_pydantic(order_by),
                filter_tenant_settings=filter_tenant_settings,
            ).load(self.id)
        ]

    @strawberry.field()
    async def risk_level(
        self, info: Info, date: Optional[datetime.date] = None
    ) -> RiskLevel:
        _date = parse_input_date(date)
        risk_level: RiskLevel = (
            await info.context.risk_model.task_specific_risk_score_ranking(_date).load(
                self.id
            )
        )
        return risk_level

    # When risk needs to be fetched for specific date ranges this field can be utilised.
    @strawberry.field()
    async def risk_levels(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
    ) -> list[DatedRiskLevel]:
        risk_dict: dict[datetime.date, RiskLevel] = {}

        current_date = filter_date_range.start_date
        while current_date <= filter_date_range.end_date:
            _date = parse_input_date(current_date)
            risk_level = await info.context.risk_model.task_specific_risk_score_ranking(
                _date
            ).load(self.id)
            risk_dict.update({_date: risk_level})
            current_date += datetime.timedelta(days=1)
        return [
            DatedRiskLevel(date=date, risk_level=RiskLevel(risk_level.value))
            for date, risk_level in risk_dict.items()
        ]

    @strawberry.field()
    async def location(self, info: Info) -> "ProjectLocationType":
        project_location = await info.context.project_locations.with_archived.load(
            self.location_id
        )
        assert project_location
        return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def library_task(self, info: Info) -> "LibraryTaskType":
        library_task = await info.context.library_tasks.me.load(self.library_task_id)
        if not library_task:
            logger.exception(
                f"LibraryTask with id {self.library_task_id} not found for Task with id {self.id}"
            )
            raise ValueError(
                f"LibraryTask with id {self.library_task_id} not found for Task with id {self.id}"
            )
        return LibraryTaskType.from_orm(library_task)

    @strawberry.field()
    async def name(self, info: Info) -> str:
        tenant_setting = await info.context.tenant_library_task_settings.me.load(
            self.library_task_id
        )
        if tenant_setting and tenant_setting.alias:
            return tenant_setting.alias
        else:
            library_task = await info.context.library_tasks.me.load(
                self.library_task_id
            )
            if not library_task:
                logger.exception(f"LibraryTask with id {self.id} not found")
                return ""
            return library_task.name

    @strawberry.field()
    async def activity(self, info: Info) -> Optional["ActivityType"]:
        if self.activity_id:
            activity = await info.context.activities.me.load(self.activity_id)
            assert activity
            return ActivityType.from_orm(activity)

        return None

    @strawberry.field()
    async def incidents(self, info: Info) -> list[IncidentType]:
        loaded_incidents = await info.context.incidents.incidents_for_library_task.load(
            self.library_task.id
        )
        return [IncidentType.from_orm(incident) for incident in loaded_incidents]

    @staticmethod
    def from_orm(task: models.Task) -> "TaskType":
        return TaskType(
            id=task.id,
            location_id=task.location_id,
            activity_id=task.activity_id,
            library_task_id=task.library_task_id,
            start_date=task.start_date,
            end_date=task.end_date,
            status=task.status,
        )


@strawberry.type(name="FirstAIDAEDLocation")
class FirstAIDAEDLocationType:
    id: uuid.UUID
    location_name: str
    location_type: LocationType

    @staticmethod
    def from_orm(location: models.FirstAidAedLocations) -> "FirstAIDAEDLocationType":
        return FirstAIDAEDLocationType(
            id=location.id,
            location_name=location.location_name,
            location_type=location.location_type,
        )


@strawberry.type(name="Crew")
class CrewType:
    id: uuid.UUID
    external_key: str

    @staticmethod
    def from_orm(crew: models.Crew) -> "CrewType":
        return CrewType(
            id=crew.id,
            external_key=crew.external_key,
        )


@strawberry.type(name="Activity")
class ActivityType:
    id: uuid.UUID
    is_critical: bool = strawberry.field(default=False)
    critical_description: str | None
    location_id: strawberry.Private[uuid.UUID]
    crew_id: strawberry.Private[Optional[uuid.UUID]]
    library_activity_type_id: strawberry.Private[Optional[uuid.UUID]]
    name: str
    status: ActivityStatus = strawberry.field(default=ActivityStatus.NOT_STARTED)
    start_date: Optional[datetime.date] = strawberry.field(default=None)
    end_date: Optional[datetime.date] = strawberry.field(default=None)

    @strawberry.field
    async def tasks(
        self,
        info: Info,
        date: Optional[datetime.date] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[TaskType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        tasks: list[models.Task] = await info.context.activities.tasks(
            date=date,
            filter_tenant_settings=filter_tenant_settings,
            order_by=order_by_to_pydantic(order_by),
        ).load(self.id)

        return [TaskType.from_orm(task) for task in tasks]

    @strawberry.field
    async def supervisors(self, info: Info) -> list[BaseSupervisorType]:
        supervisors: list[Supervisor] = await info.context.supervisors.by_activity.load(
            self.id
        )

        return [BaseSupervisorType.from_orm(supervisor) for supervisor in supervisors]

    @strawberry.field
    async def task_count(self, info: Info) -> int:
        return await info.context.activities.task_count.load(self.id)

    @strawberry.field
    async def location(self, info: Info) -> "ProjectLocationType":
        project_location = await info.context.project_locations.me.load(
            self.location_id
        )
        assert project_location
        return ProjectLocationType.from_orm(project_location)

    @strawberry.field
    async def crew(self, info: Info) -> CrewType | None:
        if not self.crew_id:
            return None

        crew = await info.context.crew.me.load(self.crew_id)
        assert crew
        return CrewType.from_orm(crew)

    @strawberry.field
    async def library_activity_type(self, info: Info) -> LibraryActivityType | None:
        if not self.library_activity_type_id:
            return None

        library_activity_type = await info.context.library.activity_types.load(
            self.library_activity_type_id
        )
        assert library_activity_type
        return LibraryActivityType.from_orm(library_activity_type)

    @staticmethod
    def from_orm(activity: models.Activity) -> "ActivityType":
        return ActivityType(
            id=activity.id,
            location_id=activity.location_id,
            name=activity.name,
            is_critical=activity.is_critical,
            critical_description=activity.critical_description,
            start_date=activity.start_date,
            end_date=activity.end_date,
            status=activity.status,
            crew_id=activity.crew_id,
            library_activity_type_id=activity.library_activity_type_id,
        )


@strawberry.input
class EditControlApplicabilityInput:
    id: uuid.UUID
    hazard_id: uuid.UUID
    is_applicable: bool


@strawberry.input
class EditHazardApplicabilityInput:
    id: uuid.UUID
    is_applicable: bool


@strawberry.type(name="RiskCalculationDetails")
class RiskCalculationDetailsType:
    project_location_id: strawberry.Private[uuid.UUID]
    supervisor_id: strawberry.Private[Optional[uuid.UUID]]
    project: strawberry.Private[models.WorkPackage]
    date: strawberry.Private[Optional[datetime.date]]

    @strawberry.field()
    async def total_task_risk_level(self, info: Info) -> RiskLevel:
        _date = parse_input_date(self.date)
        return await info.context.risk_model.total_task_risk_score_ranking(_date).load(
            self.project_location_id
        )

    @strawberry.field()
    async def is_supervisor_at_risk(self, info: Info) -> bool:
        if self.supervisor_id is None:
            return False

        return await info.context.risk_model.supervisor_safety_score_data.load(
            self.supervisor_id
        )

    @strawberry.field()
    async def is_contractor_at_risk(self, info: Info) -> bool:
        contractor_id = self.project.contractor_id
        if contractor_id:
            return await info.context.risk_model.contractor_safety_score_data.load(
                contractor_id
            )
        else:
            return False

    @strawberry.field
    async def is_crew_at_risk(self, info: Info) -> bool:
        # TODO: Move this date to another level
        _date = parse_input_date(self.date)
        loaded_activities: list["Activity"] = await info.context.activities.by_location(
            date=_date
        ).load(self.project_location_id)

        # Grab all the unique crew ids
        crew_ids = set()
        for activity in loaded_activities:
            if activity.crew_id is not None:
                crew_ids.add(activity.crew_id)

        # Call the DL and gather all the results
        results = await asyncio.gather(
            *map(info.context.risk_model.crew_score_data.load, crew_ids)
        )

        return any(results)


@strawberry.type(name="CriticalActivityType")
class DailySnapshotType:
    date: datetime.date
    is_critical: bool


@strawberry.type(name="ProjectLocation")
class ProjectLocationType:
    id: uuid.UUID
    name: str
    latitude: Decimal
    longitude: Decimal
    risk: RiskLevel
    start_date: Optional[datetime.date]  # Inherited from the project
    end_date: Optional[datetime.date]  # Inherited from the project
    supervisor_id: strawberry.Private[Optional[uuid.UUID]]
    additional_supervisor_ids: strawberry.Private[list[uuid.UUID]]
    _project: strawberry.Private[Optional[models.WorkPackage]]
    project_id: strawberry.Private[Optional[uuid.UUID]]
    preloaded_risk_level: strawberry.Private[Optional[RiskLevel]]
    external_key: Optional[str]
    address: Optional[str]

    @strawberry.field()
    async def dailySnapshots(
        self, info: Info, date_range: DateRangeInput
    ) -> list[DailySnapshotType]:
        activities = await info.context.activities.get_activities(
            start_date=date_range.start_date,
            end_date=date_range.end_date,
            location_ids=[self.id] if self.id else None,
        )
        activity_criticality_date_range = (
            info.context.activities.get_critical_activities_for_date_range(
                activities, date_range.start_date, date_range.end_date
            )
        )

        return [
            DailySnapshotType(date=snapshot_date, is_critical=activity_criticality)
            for snapshot_date, activity_criticality in activity_criticality_date_range.items()
        ]

    @strawberry.field()
    async def daily_reports(
        self, info: Info, date: Optional[datetime.date] = None
    ) -> list["DailyReportType"]:
        loaded_daily_reports = await info.context.project_locations.daily_reports(
            date=date
        ).load(self.id)
        return [
            DailyReportType.from_orm(daily_report)
            for daily_report in loaded_daily_reports
        ]

    @strawberry.field()
    async def job_safety_briefings(
        self, info: Info, date: Optional[datetime.date] = None
    ) -> list["JobSafetyBriefingType"]:
        loaded_job_safety_briefings = (
            await info.context.project_locations.job_safety_briefings(date=date).load(
                self.id
            )
        )
        return [
            JobSafetyBriefingType.from_orm(jsb) for jsb in loaded_job_safety_briefings
        ]

    @strawberry.field()
    async def site_conditions(
        self,
        info: Info,
        date: Optional[datetime.date] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[SiteConditionType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        loaded_site_conditions: list[
            tuple[LibrarySiteCondition, SiteCondition]
        ] = await info.context.project_locations.site_conditions(
            date=date,
            filter_tenant_settings=filter_tenant_settings,
            order_by=order_by_to_pydantic(order_by),
        ).load(
            self.id
        )
        return [
            SiteConditionType.from_orm(site_condition)
            for _, site_condition in loaded_site_conditions
        ]

    @strawberry.field()
    async def activities(
        self,
        info: Info,
        date: Optional[datetime.date] = None,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[ActivityType]:
        loaded_activities = await info.context.activities.by_location(
            date=date,
            start_date=start_date,
            end_date=end_date,
            order_by=order_by_to_pydantic(order_by),
        ).load(self.id)

        return [ActivityType.from_orm(activity) for activity in loaded_activities]

    @strawberry.field()
    async def tasks(
        self,
        info: Info,
        date: Optional[datetime.date] = None,
        order_by: Optional[list[TaskOrderByInput]] = None,
    ) -> list[TaskType]:
        filter_tenant_settings = info.context.params.get(
            "filter_tenant_settings", False
        )
        loaded_tasks = await info.context.project_locations.tasks(
            date=date,
            filter_tenant_settings=filter_tenant_settings,
            order_by=order_by_to_pydantic(order_by),
        ).load(self.id)
        return [TaskType.from_orm(task) for _, task in loaded_tasks]

    @strawberry.field()
    async def risk_calculation(
        self, date: Optional[datetime.date] = None
    ) -> RiskCalculationDetailsType | None:
        if self._project is not None:
            return RiskCalculationDetailsType(
                project_location_id=self.id,
                supervisor_id=self.supervisor_id,
                project=self._project,
                date=date,
            )
        else:
            return None

    @strawberry.field()
    async def risk_level(
        self, info: Info, date: Optional[datetime.date] = None
    ) -> RiskLevel:
        if self.preloaded_risk_level:
            return self.preloaded_risk_level

        _date = parse_input_date(date)
        risk_level: RiskLevel = (
            await info.context.risk_model.project_location_risk_level(_date).load(
                self.id
            )
        )
        return risk_level

    @strawberry.field()
    async def supervisor(self, info: Info) -> SupervisorType | None:
        if self.supervisor_id is None:
            return None

        supervisor = await info.context.users.me.load(self.supervisor_id)
        assert (
            supervisor
        ), f"Project location with invalid supervisor {self.supervisor_id}"
        return SupervisorType.from_orm(supervisor)

    @strawberry.field()
    async def additional_supervisors(self, info: Info) -> list[SupervisorType]:
        items: list[SupervisorType] = []
        if self.additional_supervisor_ids:
            supervisors = await info.context.users.me.load_many(
                self.additional_supervisor_ids
            )
            items.extend(SupervisorType.from_orm(i) for i in supervisors if i)
        return items

    @strawberry.field()
    async def project(self) -> Optional["ProjectType"]:
        if self._project is not None:
            return ProjectType.from_orm(self._project)
        else:
            return None

    @strawberry.field()
    async def hazard_control_settings(
        self, info: Info
    ) -> list["LocationHazardControlSettingsType"]:
        hazard_control_settings = (
            await info.context.library.get_location_hazard_control_settings(self.id)
        )

        return [
            LocationHazardControlSettingsType.from_orm(hazard_control_setting)
            for hazard_control_setting in hazard_control_settings
        ]

    @staticmethod
    def from_orm(
        location: models.Location,
        risk_level: RiskLevel | None = None,
    ) -> "ProjectLocationType":
        return ProjectLocationType(
            id=location.id,
            name=location.name,
            risk=location.risk,
            latitude=location.geom.decimal_latitude,
            longitude=location.geom.decimal_longitude,
            supervisor_id=location.supervisor_id or None,
            additional_supervisor_ids=location.additional_supervisor_ids,
            start_date=(
                location.project.start_date if location.project is not None else None
            ),
            end_date=(
                location.project.end_date if location.project is not None else None
            ),
            _project=location.project,
            project_id=location.project_id,
            preloaded_risk_level=risk_level,
            external_key=location.external_key,
            address=location.address,
        )


@strawberry.type(name="LocationHazardControlSettings")
class LocationHazardControlSettingsType:
    id: uuid.UUID
    location_id: uuid.UUID
    library_hazard_id: uuid.UUID
    library_control_id: Optional[uuid.UUID]
    created_at: datetime.datetime
    user_id: uuid.UUID
    disabled: bool

    @staticmethod
    def from_orm(
        hazard_control_setting: models.LocationHazardControlSettings,
    ) -> "LocationHazardControlSettingsType":
        return LocationHazardControlSettingsType(
            id=hazard_control_setting.id,
            library_hazard_id=hazard_control_setting.library_hazard_id,
            library_control_id=hazard_control_setting.library_control_id,
            location_id=hazard_control_setting.location_id,
            created_at=hazard_control_setting.created_at,
            user_id=hazard_control_setting.user_id,
            disabled=hazard_control_setting.disabled,
        )


@strawberry.input
class LocationHazardControlSettingsInput:
    location_id: uuid.UUID
    library_hazard_id: uuid.UUID
    library_control_id: Optional[uuid.UUID]


@strawberry.type(name="Project")
class ProjectType(Auditable):
    id: uuid.UUID
    name: str
    start_date: datetime.date
    end_date: datetime.date
    status: ProjectStatus
    number: str  # TODO delete
    external_key: Optional[str]
    description: Optional[str]
    library_region_id: strawberry.Private[Optional[uuid.UUID]]
    library_division_id: strawberry.Private[Optional[uuid.UUID]]
    # FIXME: To be deprecated
    library_project_type_id: strawberry.Private[Optional[uuid.UUID]]
    # TODO: To be made mandatory once all workpackages move to new project creation
    work_type_ids: strawberry.Private[Optional[list[uuid.UUID]]]
    manager_id: strawberry.Private[Optional[uuid.UUID]]
    supervisor_id: strawberry.Private[Optional[uuid.UUID]]
    additional_supervisor_ids: strawberry.Private[list[uuid.UUID]]
    contractor_id: strawberry.Private[Optional[uuid.UUID]]
    preloaded_risk_level: strawberry.Private[Optional[RiskLevel]]

    engineer_name: Optional[str]
    project_zip_code: Optional[str]
    contract_reference: Optional[str]
    contract_name: Optional[str]
    library_asset_type_id: strawberry.Private[Optional[uuid.UUID]]

    @strawberry.field()
    async def library_asset_type(self, info: Info) -> LibraryAssetType | None:
        if not self.library_asset_type_id:
            return None
        library_asset_type = await info.context.library.asset_types.load(
            self.library_asset_type_id
        )
        assert library_asset_type, f"Project {self.id} with invalid asset type"
        return LibraryAssetType.from_orm(library_asset_type)

    @strawberry.field()
    async def locations(
        self,
        info: Info,
        id: Optional[uuid.UUID] = None,
        search: Optional[str] = None,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[ProjectLocationType]:
        project_locations: list[models.Location] = []
        if id:
            project_location = await info.context.project_locations.me.load(id)
            if project_location and project_location.project_id == self.id:
                project_locations.append(project_location)
        else:
            project_locations.extend(
                await info.context.projects.locations(
                    order_by=order_by_to_pydantic(order_by)
                ).load(self.id)
            )

        return [
            ProjectLocationType.from_orm(location) for location in project_locations
        ]

    @strawberry.field()
    async def library_region(self, info: Info) -> Optional[LibraryRegionType]:
        if self.library_region_id is None:
            return None

        library_region = await info.context.library.regions.load(self.library_region_id)
        assert library_region, f"Project {self.id} with invalid region"
        return LibraryRegionType.from_orm(library_region)

    @strawberry.field()
    async def library_division(self, info: Info) -> Optional[LibraryDivisionType]:
        if self.library_division_id is None:
            return None

        library_division = await info.context.library.divisions.load(
            self.library_division_id
        )
        assert library_division, f"Project {self.id} with invalid division"
        return LibraryDivisionType.from_orm(library_division)

    # FIXME: To be deprecated
    @strawberry.field()
    async def library_project_type(self, info: Info) -> LibraryProjectType | None:
        if not self.library_project_type_id:
            return None

        library_project_type = await info.context.library.project_types.load(
            self.library_project_type_id
        )
        assert library_project_type, f"Project {self.id} with invalid project type"
        return LibraryProjectType.from_orm(library_project_type)

    @strawberry.field()
    async def work_types(self, info: Info) -> list[WorkTypeType]:
        if not self.work_type_ids:
            return []

        work_types = await info.context.library.work_types.load_many(self.work_type_ids)
        assert work_types, f"Project {self.id} with invalid work types"
        return [
            WorkTypeType.from_orm(work_type) for work_type in work_types if work_type
        ]

    @strawberry.field()
    async def risk_level(
        self, info: Info, date: Optional[datetime.date] = None
    ) -> RiskLevel:
        if self.preloaded_risk_level:
            return self.preloaded_risk_level

        _date = parse_input_date(date)
        ret: RiskLevel = await info.context.risk_model.total_project_risk_level(
            _date
        ).load(self.id)
        return ret

    @staticmethod
    def find_risk_level_date(
        projects_selection: list[Selection],
    ) -> datetime.date | None:
        for field in projects_selection:
            if getattr(field, "name", "") == "riskLevel":
                arguments: dict[str, Any] | None = getattr(field, "arguments", None)
                if arguments:
                    risk_level_date: datetime.date | None = arguments.get("date")
                    if risk_level_date and not isinstance(
                        risk_level_date, datetime.date
                    ):
                        return datetime.date.fromisoformat(risk_level_date)
                    return risk_level_date
                return None
        return None

    @strawberry.field()
    async def manager(self, info: Info) -> Optional[ManagerType]:
        if self.manager_id is None:
            return None

        manager = await info.context.users.me.load(self.manager_id)
        assert manager, f"Project with invalid manager {self.manager_id}"
        return ManagerType.from_orm(manager)

    @strawberry.field()
    async def supervisor(self, info: Info) -> SupervisorType | None:
        if not self.supervisor_id:
            return None

        supervisor = await info.context.users.me.load(self.supervisor_id)
        assert supervisor, f"Project with invalid supervisor {self.supervisor_id}"
        return SupervisorType.from_orm(supervisor)

    @strawberry.field()
    async def additional_supervisors(self, info: Info) -> list[SupervisorType]:
        items: list[SupervisorType] = []
        if self.additional_supervisor_ids:
            supervisors = await info.context.users.me.load_many(
                self.additional_supervisor_ids
            )
            items.extend(SupervisorType.from_orm(i) for i in supervisors if i)
        return items

    @strawberry.field()
    async def contractor(self, info: Info) -> Optional["ContractorType"]:
        if self.contractor_id is None:
            return None

        contractor = await info.context.contractors.me.load(self.contractor_id)
        assert contractor, f"Project with invalid contractor {self.contractor_id}"
        return ContractorType.from_orm(contractor)

    @strawberry.field(permission_classes=[CanReadProjectAudits])
    async def audits(self, info: Info) -> list["AuditEventType"]:
        diffs = await info.context.audit.projects.load(self.id)
        if diffs:
            return [AuditEventType.from_orm(diff) for diff in diffs]
        return []

    @strawberry.field()
    async def minimum_task_date(self, info: Info) -> Optional[datetime.date]:
        return await info.context.projects.minimum_task_date.load(self.id)

    @strawberry.field()
    async def maximum_task_date(self, info: Info) -> Optional[datetime.date]:
        return await info.context.projects.maximum_task_date.load(self.id)

    @staticmethod
    def from_orm(
        project: models.WorkPackage, risk_level: RiskLevel | None = None
    ) -> "ProjectType":
        return ProjectType(
            id=project.id,
            name=project.name,
            start_date=project.start_date,
            end_date=project.end_date,
            status=project.status,
            number=project.external_key or "",
            external_key=project.external_key,
            description=project.description,
            library_region_id=project.region_id,
            library_division_id=project.division_id,
            library_project_type_id=project.work_type_id,
            work_type_ids=project.work_type_ids,
            manager_id=project.manager_id,
            supervisor_id=project.primary_assigned_user_id,
            additional_supervisor_ids=project.additional_assigned_users_ids,
            contractor_id=project.contractor_id,
            engineer_name=project.engineer_name,
            project_zip_code=project.zip_code,
            contract_reference=project.contract_reference,
            contract_name=project.contract_name,
            library_asset_type_id=project.asset_type_id,
            preloaded_risk_level=risk_level,
        )


@strawberry.input
class ProjectLocationInput:
    name: str
    latitude: Decimal
    longitude: Decimal
    supervisor_id: Optional[uuid.UUID] = strawberry.field(default=None)
    additional_supervisors: Optional[list[uuid.UUID]] = strawberry.field(default=None)
    external_key: Optional[str] = strawberry.field(default=None)


@strawberry.input
class EditProjectLocationInput(ProjectLocationInput):
    id: Optional[uuid.UUID] = None


@strawberry.input
class BaseProjectInput:
    name: str
    start_date: datetime.date
    end_date: datetime.date


@strawberry.input
class CreateProjectInput(BaseProjectInput):
    locations: list[ProjectLocationInput]
    status: ProjectStatus = strawberry.field(default=ProjectStatus.PENDING)
    number: Optional[str] = strawberry.field(default=None)
    external_key: Optional[str] = strawberry.field(default=None)
    library_region_id: Optional[uuid.UUID] = strawberry.field(default=None)
    library_division_id: Optional[uuid.UUID] = strawberry.field(default=None)
    # FIXME: To be deprecated
    library_project_type_id: Optional[uuid.UUID] = strawberry.field(default=None)
    # TODO: Optional to be removed once work packsges are migrated
    work_type_ids: Optional[list[uuid.UUID]] = strawberry.field(default_factory=list)
    manager_id: Optional[uuid.UUID] = strawberry.field(default=None)
    supervisor_id: Optional[uuid.UUID] = strawberry.field(default=None)
    contractor_id: Optional[uuid.UUID] = strawberry.field(default=None)
    description: Optional[str] = strawberry.field(default=None)
    additional_supervisors: Optional[list[uuid.UUID]] = strawberry.field(default=None)
    engineer_name: Optional[str] = strawberry.field(default=None)
    project_zip_code: Optional[str] = strawberry.field(default=None)
    contract_reference: Optional[str] = strawberry.field(default=None)
    contract_name: Optional[str] = strawberry.field(default=None)
    library_asset_type_id: Optional[uuid.UUID] = strawberry.field(default=None)


@strawberry.input
class EditProjectInput(BaseProjectInput):
    id: uuid.UUID
    locations: list[EditProjectLocationInput]
    status: ProjectStatus
    number: Optional[str] = strawberry.field(default=None)
    external_key: Optional[str] = strawberry.field(default=None)
    library_region_id: Optional[uuid.UUID] = strawberry.field(default=None)
    library_division_id: Optional[uuid.UUID] = strawberry.field(default=None)
    # FIXME: To be deprecated
    library_project_type_id: Optional[uuid.UUID] = strawberry.field(default=None)
    # TODO: Optional to be removed once work packsges are migrated
    work_type_ids: Optional[list[uuid.UUID]] = strawberry.field(default_factory=list)
    manager_id: Optional[uuid.UUID] = strawberry.field(default=None)
    supervisor_id: Optional[uuid.UUID] = strawberry.field(default=None)
    contractor_id: Optional[uuid.UUID] = strawberry.field(default=None)
    description: Optional[str] = strawberry.field(default=None)
    additional_supervisors: Optional[list[uuid.UUID]] = strawberry.field(default=None)
    engineer_name: Optional[str] = strawberry.field(default=None)
    project_zip_code: Optional[str] = strawberry.field(default=None)
    contract_reference: Optional[str] = strawberry.field(default=None)
    contract_name: Optional[str] = strawberry.field(default=None)
    library_asset_type_id: Optional[uuid.UUID] = strawberry.field(default=None)


@strawberry.experimental.pydantic.input(
    model=models.BaseHazardControlCreate, all_fields=True
)
class CreateHazardControlInput:
    pass


@strawberry.experimental.pydantic.input(model=models.BaseHazardCreate, all_fields=True)
class CreateHazardInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.ActivityTaskCreate, all_fields=True
)
class CreateTaskInput:
    pass


@strawberry.experimental.pydantic.input(model=models.ActivityCreate)
class CreateActivityInput:
    location_id: strawberry.auto
    name: strawberry.auto
    is_critical: strawberry.auto
    critical_description: strawberry.auto
    start_date: strawberry.auto
    end_date: strawberry.auto
    status: strawberry.auto
    crew_id: strawberry.auto
    library_activity_type_id: strawberry.auto
    external_key: strawberry.auto
    meta_attributes: Optional[DictScalar]
    tasks: strawberry.auto


@strawberry.input
class EditActivityInput:
    id: uuid.UUID
    name: Optional[str] = None
    is_critical: Optional[bool] = False
    critical_description: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    status: Optional[ActivityStatus] = strawberry.field(
        default=ActivityStatus.NOT_STARTED
    )
    crew_id: Optional[uuid.UUID] = None
    library_activity_type_id: Optional[uuid.UUID] = None


@strawberry.experimental.pydantic.input(model=models.AddActivityTasks, all_fields=True)
class AddActivityTasksInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.RemoveActivityTasks, all_fields=True
)
class RemoveActivityTasksInput:
    pass


@strawberry.input
class CreateSiteConditionInput:
    location_id: uuid.UUID
    library_site_condition_id: uuid.UUID
    hazards: list[CreateHazardInput]


@strawberry.experimental.pydantic.input(
    model=models.BaseHazardControlEdit, all_fields=True
)
class EditHazardControlInput:
    pass


@strawberry.experimental.pydantic.input(model=models.BaseHazardEdit, all_fields=True)
class EditHazardInput:
    pass


@strawberry.input
class EditTaskInput:
    id: uuid.UUID
    hazards: list[EditHazardInput] = strawberry.field(default_factory=list)


@strawberry.input
class EditSiteConditionInput:
    id: uuid.UUID
    hazards: list[EditHazardInput] = strawberry.field(default_factory=list)


@strawberry.experimental.pydantic.type(
    model=models.GoogleCloudStorageBlob,
    name="FileUpload",
    all_fields=True,
)
class File:
    url: str


@strawberry.type
class SignedPostPolicy:
    """Google Cloud Storage Post Policy for file upload
    id: str = Blob name
    url: str = URL to GCS bucket
    fields: str = form data to include in POST request or HTML form as JSON string
    """

    id: str
    url: str
    fields: str

    @staticmethod
    def from_policy(policy: dict) -> "SignedPostPolicy":
        return SignedPostPolicy(
            id=policy["id"],
            url=policy["url"],
            fields=json.dumps(policy["fields"]),
        )

    @strawberry.field()
    async def signed_url(self, info: Info) -> str:
        url: str = await info.context.files.signed_urls.load(self.id)
        return url


@strawberry.type(name="Contractor")
class ContractorType:
    id: uuid.UUID
    name: str

    @staticmethod
    def from_orm(contractor: models.Contractor) -> "ContractorType":
        return ContractorType(
            id=contractor.id,
            name=contractor.name,
        )


@strawberry.experimental.pydantic.type(
    model=models.DailyReportWorkSchedule,
    name="WorkScheduleInput",
    is_input=True,
    all_fields=True,
)
class WorkScheduleInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportWorkSchedule, name="WorkSchedule", all_fields=True
)
class WorkScheduleType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportTaskSelection, name="TaskSelection", all_fields=True
)
class TaskSelectionType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportTaskSelectionSection,
    name="TaskSelectionSection",
    all_fields=True,
)
class TaskSelectionSectionType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportControlAnalysis,
    name="ControlAnalysis",
)
class ControlAnalysisSection:
    id: uuid.UUID
    implemented: strawberry.auto
    not_implemented_reason: strawberry.auto
    further_explanation: strawberry.auto
    name: str


@strawberry.experimental.pydantic.type(
    model=models.DailyReportHazardAnalysis,
    name="HazardAnalysis",
)
class HazardAnalysis:
    id: strawberry.auto
    isApplicable: strawberry.auto
    not_applicable_reason: strawberry.auto
    controls: strawberry.auto
    name: str


@strawberry.experimental.pydantic.type(
    model=models.DailyReportTaskAnalysis,
    name="TaskAnalysis",
)
class TaskAnalysisSection:
    id: strawberry.auto
    notes: strawberry.auto
    not_applicable_reason: strawberry.auto
    performed: strawberry.auto
    hazards: strawberry.auto
    section_is_valid: strawberry.auto
    name: str


@strawberry.experimental.pydantic.type(
    model=models.DailyReportSiteConditionAnalysis,
    name="SiteConditionAnalysis",
)
class SiteConditionAnalysisSection:
    id: strawberry.auto
    isApplicable: strawberry.auto
    hazards: strawberry.auto
    name: str


@strawberry.experimental.pydantic.type(
    model=models.DailyReportJobHazardAnalysisSection,
    name="JobHazardAnalysisSection",
    all_fields=True,
)
class JobHazardAnalysisSection:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportTaskSelection,
    name="TaskSelectionInput",
    is_input=True,
    all_fields=True,
)
class TaskSelectionInput:
    pass


class TaskSelectionSectionValidations(models.DailyReportTaskSelectionSection):
    # We need this class to skip validations in response model

    @validator("selected_tasks")
    def selected_tasks_duplicated(
        cls, selected_tasks: list[models.DailyReportTaskSelection]
    ) -> list[models.DailyReportTaskSelection]:
        validate_duplicates(
            [i.id for i in selected_tasks],
            "Task ID {duplicated_id} duplicated in task selection",
        )
        return selected_tasks


@strawberry.experimental.pydantic.type(
    model=TaskSelectionSectionValidations,
    name="TaskSelectionSectionInput",
    is_input=True,
    all_fields=True,
)
class TaskSelectionSectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportControlAnalysis,
    is_input=True,
)
class ControlAnalysisInput:
    id: uuid.UUID
    implemented: strawberry.auto
    not_implemented_reason: strawberry.auto
    further_explanation: strawberry.auto
    name: Optional[str] = None  # For FE use only


@strawberry.experimental.pydantic.type(
    model=models.DailyReportHazardAnalysis,
    is_input=True,
)
class HazardAnalysisInput:
    id: strawberry.auto
    isApplicable: strawberry.auto
    not_applicable_reason: strawberry.auto
    controls: strawberry.auto
    name: Optional[str] = None  # For FE use only


@strawberry.experimental.pydantic.type(
    model=models.DailyReportTaskAnalysis,
    is_input=True,
)
class TaskAnalysisInput:
    id: strawberry.auto
    notes: strawberry.auto
    not_applicable_reason: strawberry.auto
    performed: strawberry.auto
    hazards: strawberry.auto
    section_is_valid: strawberry.auto
    name: Optional[str] = None  # For FE use only


@strawberry.experimental.pydantic.type(
    model=models.DailyReportSiteConditionAnalysis,
    is_input=True,
)
class SiteConditionAnalysisInput:
    id: strawberry.auto
    isApplicable: strawberry.auto
    hazards: strawberry.auto
    name: Optional[str] = None  # For FE use only


@strawberry.experimental.pydantic.type(
    model=models.DailyReportJobHazardAnalysisSection,
    name="JobHazardAnalysisSectionInput",
    is_input=True,
    all_fields=True,
)
class JobHazardAnalysisSectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportCrewSection,
    name="CrewSection",
    all_fields=True,
)
class CrewSection:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportCrewSection,
    name="CrewSectionInput",
    is_input=True,
)
class CrewSectionInput:
    contractor: strawberry.auto
    foreman_name: strawberry.auto
    n_welders: strawberry.auto
    n_safety_prof: strawberry.auto
    n_operators: strawberry.auto
    n_flaggers: strawberry.auto
    n_laborers: strawberry.auto
    n_other_crew: strawberry.auto
    section_is_valid: Optional[bool] = strawberry.field(default=None)
    documents: Optional[list[FileInput]] = strawberry.field(default=None)


@strawberry.experimental.pydantic.type(
    model=models.DailyReportAttachmentSection,
    name="AttachmentSection",
    all_fields=True,
)
class AttachmentSection:
    pass


@strawberry.input
class AttachmentSectionInput:
    """Defined as regular strawberry input instead of pydantic input
    as strawberry does not seem to allow classes to inherit from pydantic
    unless at least one pydantic field is inherited.

    In this case both are changed to set the types as inputs
    """

    section_is_valid: Optional[bool] = strawberry.field(default=None)
    documents: Optional[list[FileInput]] = strawberry.field(default=None)
    photos: Optional[list[FileInput]] = strawberry.field(default=None)

    def to_pydantic(self) -> models.DailyReportAttachmentSection:
        """provide `to_pydantic` to share the same API as the other pydantic based inputs"""
        documents = (
            [document.to_pydantic() for document in self.documents]
            if self.documents is not None
            else None
        )
        photos = (
            [photo.to_pydantic() for photo in self.photos]
            if self.photos is not None
            else None
        )
        model = models.DailyReportAttachmentSection(
            documents=documents, photos=photos, section_is_valid=self.section_is_valid
        )
        return model


@strawberry.experimental.pydantic.type(
    model=models.DailyReportAdditionalInformationSection,
    name="AdditionalInformationSection",
    all_fields=True,
)
class AdditionalInformationSection:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportAdditionalInformationSection,
    name="AdditionalInformationSectionInput",
    is_input=True,
    all_fields=True,
)
class AdditionalInformationSectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.Completion,
    name="Completion",
)
class CompletionType:
    # https://github.com/strawberry-graphql/strawberry/issues/2674
    completed_by_id: strawberry.auto = strawberry.field(
        deprecation_reason="Use completedBy instead"
    )
    completed_at: strawberry.auto

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None


@strawberry.experimental.pydantic.input(
    model=models.SourceInformationConcepts,
    name="SourceInformationConceptsInput",
    all_fields=True,
)
class SourceInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.SourceInformationConcepts,
    name="SourceInformationConceptsType",
    all_fields=True,
)
class SourceInformationConceptsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.DailySourceInformationConcepts,
    name="DailySourceInformationConceptsInput",
    all_fields=True,
)
class DailySourceInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailySourceInformationConcepts,
    name="DailySourceInformationConceptsType",
    all_fields=True,
)
class DailySourceInformationConceptsType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DailyReportSections, name="Sections"
)
class SectionsType:
    work_schedule: strawberry.auto
    task_selection: strawberry.auto
    job_hazard_analysis: strawberry.auto
    safety_and_compliance: Optional[DictScalar]
    crew: strawberry.auto
    attachments: strawberry.auto
    additional_information: strawberry.auto
    completions: strawberry.auto
    dailySourceInfo: strawberry.auto


@strawberry.input
class SaveDailyReportInput:
    project_location_id: uuid.UUID
    date: datetime.date
    work_schedule: Optional[WorkScheduleInput] = strawberry.field(default=None)
    task_selection: Optional[TaskSelectionSectionInput] = strawberry.field(default=None)
    job_hazard_analysis: Optional[JobHazardAnalysisSectionInput] = strawberry.field(
        default=None
    )
    safety_and_compliance: Optional[DictScalar] = strawberry.field(default=None)
    crew: Optional[CrewSectionInput] = strawberry.field(default=None)
    attachments: Optional[AttachmentSectionInput] = strawberry.field(default=None)
    additional_information: Optional[
        AdditionalInformationSectionInput
    ] = strawberry.field(default=None)
    dailySourceInfo: Optional[DailySourceInformationInput] = strawberry.field(
        default=None
    )

    # If not ID sent, a daily report is created
    id: Optional[uuid.UUID] = strawberry.field(default=None)


@strawberry.type
class OptionItem:
    id: str
    name: str

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, OptionItem):
            return False
        return self.id == other.id and self.name.lower() == other.name.lower()

    def __hash__(self) -> int:
        return hash(self.id)

    def __lt__(self, other: "OptionItem") -> bool:  # type: ignore
        if isinstance(self, OptionItem):
            return self.name.lower() < other.name.lower()
        raise NotImplementedError(
            "Should be compared only with instances of the same class"
        )

    def __repr__(self) -> str:
        return f"OptionItem(id='{self.id}', name='{self.name}')"


@strawberry.input
class FormListFilterSearchInput:
    search_column: str
    search_value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "search_column": self.search_column,
            "search_value": self.search_value,
        }


@strawberry.type
class FormListFilterOptions:
    formIds: list[str]
    formNames: list[str]
    operatingHqs: list[str]
    createdByUsers: list[OptionItem]
    updatedByUsers: list[OptionItem]
    workPackages: list[OptionItem]
    locations: list[OptionItem]
    supervisors: list[OptionItem]


@strawberry.interface
class FormInterface:
    id: uuid.UUID
    status: FormStatus
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    date: datetime.date
    operating_hq: Optional[str]
    updated_at: Optional[datetime.datetime] = strawberry.field(default=None)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def work_package(self, info: Info) -> Optional[ProjectType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass


@strawberry.interface
class FormInterfaceWithContents:
    id: uuid.UUID
    status: FormStatus
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    date: datetime.date
    operating_hq: Optional[str]
    updated_at: Optional[datetime.datetime] = strawberry.field(default=None)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def work_package(self, info: Info) -> Optional[ProjectType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        # This method is intentionally left empty because it is meant to be implemented by subclasses.
        pass


@strawberry.type(name="DailyReport")
class DailyReportType(Auditable, FormInterface):
    id: uuid.UUID
    project_location_id: strawberry.Private[uuid.UUID]
    date: datetime.date
    status: FormStatus
    source: Optional[SourceInformation]
    form_id: Optional[str]
    _sections: strawberry.Private[Optional[SectionsType]]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    sectionsJSON: Optional[JSONScalar] = strawberry.field(default=None)
    operating_hq: Optional[str] = None

    @strawberry.field()
    async def sections(self, info: Info) -> Optional[SectionsType]:
        if self._sections and self._sections.job_hazard_analysis:
            await info.context.daily_reports.inject_job_hazard_analysis_names(
                self._sections.job_hazard_analysis
            )
        return self._sections

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def work_package(self, info: Info) -> ProjectType | None:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )

        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on daily report {self.id}"
            )
        if project_location.project is not None:
            return ProjectType.from_orm(project_location.project)
        else:
            return None

    @strawberry.field()
    async def location(self, info: Info) -> ProjectLocationType:
        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on daily report {self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        location: ProjectLocationType = await self.location(info)
        if location:
            return location.name
        else:
            return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @staticmethod
    def from_orm(
        daily_report: models.DailyReport, operating_hq: Optional[str] = None
    ) -> "DailyReportType":
        sections_type = None
        sections = daily_report.sections_to_pydantic()
        if sections is not None:
            sections_type = SectionsType.from_pydantic(sections)

        return DailyReportType(
            id=daily_report.id,
            date=daily_report.date_for,
            status=daily_report.status,
            created_by_id=daily_report.created_by_id,
            created_at=daily_report.created_at,
            completed_by_id=daily_report.completed_by_id,
            completed_at=daily_report.completed_at,
            sectionsJSON=sections.json() if sections else None,  # type: ignore
            _sections=sections_type,
            source=daily_report.source,
            form_id=daily_report.form_id,
            project_location_id=daily_report.project_location_id,
            operating_hq=operating_hq,
            updated_at=daily_report.updated_at,
        )


@strawberry.type(name="DailyReportCrewRecommendation")
class DailyReportCrewRecommendation:
    foreman_name: str | None = None
    construction_company: str | None = None


@strawberry.type(name="DailyReportSafetyAndComplianceRecommendation")
class DailyReportSafetyAndComplianceRecommendation:
    pha_completion: str | None = None
    sop_number: str | None = None
    sop_type: str | None = None
    steps_called_in: str | None = None


@strawberry.type(name="DailyReportRecommendation")
class DailyReportRecommendation:
    crew: DailyReportCrewRecommendation | None = None
    safety_and_compliance: DailyReportSafetyAndComplianceRecommendation | None = None

    @staticmethod
    def from_orm(report: DailyReport) -> Optional["DailyReportRecommendation"]:
        crew = None
        snc = None
        if report.sections:
            crew_data = report.sections.get("crew")
            if crew_data:
                crew = DailyReportCrewRecommendation(
                    foreman_name=crew_data.get("foreman_name"),
                    construction_company=crew_data.get("contractor"),
                )
            SandC = report.sections.get("safety_and_compliance")
            if SandC:
                op_procedures = SandC.get("systemOperatingProcedures", {})
                plans = SandC.get("plans", {})
                snc = DailyReportSafetyAndComplianceRecommendation(
                    pha_completion=plans.get("comprehensivePHAConducted"),
                    sop_number=op_procedures.get("sopId"),
                    sop_type=op_procedures.get("sopType"),
                    steps_called_in=op_procedures.get("sopStepsCalledIn"),
                )
        if crew or snc:
            return DailyReportRecommendation(crew=crew, safety_and_compliance=snc)
        return None

    @staticmethod
    def from_work_package(
        work_package: models.WorkPackage,
    ) -> Optional["DailyReportRecommendation"]:
        if work_package.contractor and work_package.contractor.name:
            crew = DailyReportCrewRecommendation(
                construction_company=work_package.contractor.name
            )
            return DailyReportRecommendation(crew=crew)
        return None


@strawberry.type(name="Recommendation")
class RecommendationType:
    @strawberry.field()
    async def daily_report(
        self, info: Info, project_location_id: uuid.UUID
    ) -> Optional[DailyReportRecommendation]:
        report = await info.context.daily_reports.get_daily_report_recommendation(
            project_location_id=project_location_id,
            created_by=info.context.user,
        )
        if report:
            return DailyReportRecommendation.from_orm(report)

        work_package = await info.context.projects.get_work_package_by_location(
            project_location_id
        )
        if work_package:
            return DailyReportRecommendation.from_work_package(work_package)

        return None


@strawberry.experimental.pydantic.input(model=AttributeConfiguration, all_fields=False)
class AttributeConfigurationInput:
    key: strawberry.auto
    label: strawberry.auto
    labelPlural: strawberry.auto
    visible: strawberry.auto
    required: strawberry.auto
    filterable: strawberry.auto

    # Only difference
    mappings: Optional[JSON] = None


@strawberry.experimental.pydantic.input(model=EntityConfiguration, all_fields=True)
class EntityConfigurationInput:
    pass


@strawberry.enum
class AuditActionType(Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"


@strawberry.enum
class AuditObjectType(Enum):
    TASK = "TASK"
    SITE_CONDITION = "SITE_CONDITION"
    PROJECT = "PROJECT"
    DAILY_REPORT = "DAILY_REPORT"


@strawberry.type
class AuditActor:
    id: uuid.UUID
    name: str
    role: str | None

    @staticmethod
    def from_orm(user: User) -> "AuditActor":
        return AuditActor(id=user.id, name=user.get_name(), role=user.role)


@strawberry.interface
class DiffValue:
    type: str | None = None


@strawberry.type
class DiffValueLiteral(DiffValue):
    old_value: str | None = None
    new_value: str | None = None
    type: str = "String"


@strawberry.type
class DiffValueScalar(DiffValue):
    old_values: list[str] | None = None
    new_values: list[str] | None = None
    added: list[str] | None = None
    removed: list[str] | None = None
    type: str = "List"


# Map field names previous used in database models
# that could occur in the audit log
# to their current equivalent
previously_used_field_names = {
    AuditObjectType.PROJECT: {
        "number": "external_key",
        "library_region_id": "region_id",
        "library_division_id": "division_id",
        "library_project_type_id": "work_type_id",
        "supervisor_id": "primary_assigned_user_id",
        "additional_supervisor_ids": "additional_assigned_users_ids",
        "project_zip_code": "zip_code",
        "library_asset_type_id": "asset_type_id",
    },
}


# Map the combination of audit object type and field name to unique values
# so we do not leak our database model details into the audit API.
# Enum Keys should be the GQL schema name for the object_type and field_name
# joined with an underscore.
# Enum Values should be the AuditObjectType and current model field_name.
#
# We only need to map value combinations used in the Audit Log.
# These are the combinations of
#  - all `Auditable` object types
#  - and any field_names used in Audit Log records
@strawberry.enum
class AuditKeyType(Enum):
    # tasks
    task = (AuditObjectType.TASK, None)
    task_startDate = (AuditObjectType.TASK, "start_date")
    task_endDate = (AuditObjectType.TASK, "end_date")
    task_status = (AuditObjectType.TASK, "status")
    # site conditions
    siteCondition = (AuditObjectType.SITE_CONDITION, None)
    # projects
    project = (AuditObjectType.PROJECT, None)
    project_name = (AuditObjectType.PROJECT, "name")
    project_startDate = (AuditObjectType.PROJECT, "start_date")
    project_endDate = (AuditObjectType.PROJECT, "end_date")
    project_externalKey = (AuditObjectType.PROJECT, "external_key")
    project_description = (AuditObjectType.PROJECT, "description")
    project_status = (AuditObjectType.PROJECT, "status")
    project_customerStatus = (AuditObjectType.PROJECT, "customer_status")
    project_libraryRegionId = (AuditObjectType.PROJECT, "region_id")
    project_libraryDivisionId = (AuditObjectType.PROJECT, "division_id")
    project_workTypeId = (AuditObjectType.PROJECT, "work_type_id")
    project_workTypeIds = (AuditObjectType.PROJECT, "work_type_ids")
    project_libraryProjectTypeId = (AuditObjectType.PROJECT, "project_type_id")
    project_managerId = (AuditObjectType.PROJECT, "manager_id")
    project_supervisorId = (AuditObjectType.PROJECT, "primary_assigned_user_id")
    project_additionalSupervisorIds = (
        AuditObjectType.PROJECT,
        "additional_assigned_users_ids",
    )
    project_contractorId = (AuditObjectType.PROJECT, "contractor_id")
    project_engineerName = (AuditObjectType.PROJECT, "engineer_name")
    project_projectZipCode = (AuditObjectType.PROJECT, "zip_code")
    project_contractReference = (AuditObjectType.PROJECT, "contract_reference")
    project_contractName = (AuditObjectType.PROJECT, "contract_name")
    project_libraryAssetTypeId = (AuditObjectType.PROJECT, "asset_type_id")
    # daily reports
    dailyReport = (AuditObjectType.DAILY_REPORT, None)
    dailyReport_status = (AuditObjectType.DAILY_REPORT, "status")


TO_GQL_OBJECT_TYPE = {
    AuditObjectTypeModel.project: AuditObjectType.PROJECT,
    AuditObjectTypeModel.task: AuditObjectType.TASK,
    AuditObjectTypeModel.site_condition: AuditObjectType.SITE_CONDITION,
    AuditObjectTypeModel.daily_report: AuditObjectType.DAILY_REPORT,
}

TO_GQL_ACTION_TYPE = {
    AuditDiffType.created: AuditActionType.CREATED,
    AuditDiffType.updated: AuditActionType.UPDATED,
    AuditDiffType.deleted: AuditActionType.DELETED,
    AuditDiffType.archived: AuditActionType.DELETED,
}


@strawberry.type(name="AuditEvent")
class AuditEventType:
    diff: strawberry.Private[ProjectDiff]
    field_name: strawberry.Private[str | None] = None

    @strawberry.field()
    def object_type(self) -> AuditObjectType:
        return TO_GQL_OBJECT_TYPE[self.diff.diff.object_type]

    @strawberry.field()
    def action_type(self) -> AuditActionType:
        return TO_GQL_ACTION_TYPE[self.diff.diff.diff_type]

    @strawberry.field()
    def transaction_id(self) -> uuid.UUID:
        return self.diff.diff.event_id

    @strawberry.field()
    def timestamp(self) -> datetime.datetime:
        return self.diff.diff.created_at

    @strawberry.field()
    def object_id(self) -> uuid.UUID:
        return self.diff.diff.object_id

    @strawberry.field()
    def audit_key(self) -> AuditKeyType:
        field_name = self.field_name
        if self.field_name and self.object_type() in previously_used_field_names:
            field_name = previously_used_field_names[self.object_type()].get(
                self.field_name, self.field_name
            )
        return AuditKeyType((self.object_type(), field_name))

    @strawberry.field()
    def actor(self) -> AuditActor | None:
        return AuditActor.from_orm(self.diff.user) if self.diff.user else None

    @strawberry.field()
    async def object_details(self, info: Info) -> Optional[Auditable]:
        if self.object_type() == AuditObjectType.PROJECT:
            loader = getattr(info.context, "projects")
            current = await loader.with_archived.load(self.object_id())
            return ProjectType.from_orm(current)

        elif self.object_type() == AuditObjectType.TASK:
            loader = getattr(info.context, "tasks")
            _, current = await loader.with_archived.load(self.object_id())
            return TaskType.from_orm(current)

        elif self.object_type() == AuditObjectType.SITE_CONDITION:
            loader = getattr(info.context, "site_conditions")
            _, current = await loader.manually_added_with_archived.load(
                self.object_id()
            )
            return SiteConditionType.from_orm(current)

        elif self.object_type() == AuditObjectType.DAILY_REPORT:
            loader = getattr(info.context, "daily_reports")
            current = await loader.me.load(self.object_id())
            return DailyReportType.from_orm(current)
        else:
            return None

    @strawberry.field()
    async def diff_values(self, info: Info) -> DiffValue | None:
        if not self.field_name:
            return None
        if self.object_type() in [AuditObjectType.TASK, AuditObjectType.DAILY_REPORT]:
            return _build_diff_value(self.diff, self.field_name)
        elif self.object_type() == AuditObjectType.PROJECT:
            name_attribute: dict[
                str, Callable
            ] = {  # load objects with a .name attribute
                "contractor_id": info.context.contractors.load_contractors,
                "library_division_id": info.context.library.load_divisions,
                "library_asset_type_id": info.context.library.load_asset_types,
                "library_project_type_id": info.context.library.load_project_types,
                "library_region_id": info.context.library.load_regions,
                "division_id": info.context.library.load_divisions,
                "asset_type_id": info.context.library.load_asset_types,
                "work_type_id": info.context.library.load_project_types,
                "region_id": info.context.library.load_regions,
            }
            name_method: dict[
                str, Callable
            ] = {  # load objects with a .get_name() method
                "manager_id": info.context.users.load_users,
                "supervisor_id": info.context.users.load_users,
                "primary_assigned_user_id": info.context.users.load_users,
            }
            # for fields with lists of objects that use .get_name() and work_type_ids
            list_field_by_name = [
                "additional_assigned_users_ids",
                "additional_supervisor_ids",
                "work_type_ids",
            ]

            original = (
                self.diff.diff.old_values.get(self.field_name)
                if self.diff.diff.old_values
                else None
            )
            updated = (
                self.diff.diff.new_values.get(self.field_name)
                if self.diff.diff.new_values
                else None
            )

            if self.field_name in name_attribute:
                ids = [uuid.UUID(id) for id in [original, updated] if id]
                values = {
                    str(model.id): model
                    for model in await name_attribute[self.field_name](ids)
                    if model is not None
                }

                old_value = values[original].name if original in values else ""
                new_value = values[updated].name if updated in values else ""

                return DiffValueLiteral(old_value=old_value, new_value=new_value)
            elif self.field_name in name_method:
                ids = [uuid.UUID(id) for id in [original, updated] if id]
                values = {
                    str(model.id): model
                    for model in await name_method[self.field_name](ids)
                    if model is not None
                }
                old_value = values[original].get_name() if original in values else ""
                new_value = values[updated].get_name() if updated in values else ""
                return DiffValueLiteral(old_value=old_value, new_value=new_value)
            elif self.field_name in list_field_by_name:
                # make mypy happy by casting to an iterable
                # original & updated should be lists of user names if field_name == "additional_supervisor_ids"
                original_ids = (
                    set(original) if isinstance(original, Iterable) else set([original])
                )
                updated_ids = (
                    set(updated) if isinstance(updated, Iterable) else set([updated])
                )

                removed_ids = list(original_ids - updated_ids)
                added_ids = list(updated_ids - original_ids)
                all_ids = [uuid.UUID(id) for id in original_ids | updated_ids]

                if self.field_name == "work_type_ids":
                    work_types = {
                        str(id): work_type
                        for id, work_type in zip(
                            all_ids,
                            await info.context.library.load_work_types(all_ids),
                        )
                        if work_type is not None
                    }
                    removed = [
                        work_types[id].name for id in removed_ids if id in work_types
                    ]
                    added = [
                        work_types[id].name for id in added_ids if id in work_types
                    ]
                    old_values = [work_types[id].name for id in original_ids]
                    new_values = [work_types[id].name for id in updated_ids]
                else:
                    users = {
                        str(id): user
                        for id, user in zip(
                            all_ids,
                            await info.context.users.load_users(all_ids),
                        )
                        if user is not None
                    }
                    removed = [
                        users[id].get_name() for id in removed_ids if id in users
                    ]
                    added = [users[id].get_name() for id in added_ids if id in users]
                    old_values = [users[id].get_name() for id in original_ids]
                    new_values = [users[id].get_name() for id in updated_ids]

                return DiffValueScalar(
                    old_values=old_values,
                    new_values=new_values,
                    added=added,
                    removed=removed,
                )
            else:
                old_value = original  # simple string
                new_value = updated  # simple string
                return DiffValueLiteral(old_value=old_value, new_value=new_value)
        return None

    @staticmethod
    def from_orm(audit: AuditEventTypeInput) -> "AuditEventType":
        return AuditEventType(diff=audit.diff, field_name=audit.field_name)


def _build_diff_value(
    project_diff: ProjectDiff, field_name: str
) -> DiffValueLiteral | DiffValueScalar | None:
    diff = project_diff.diff
    old_value = diff.old_values.get(field_name) if diff.old_values else None
    new_value = diff.new_values.get(field_name) if diff.new_values else None

    # could handle per object-type/field_name diff-value building here

    if old_value or new_value:
        return DiffValueLiteral(old_value=old_value, new_value=new_value)
    else:
        return None


@strawberry.type
class IngestColumn:
    attribute: str
    name: str
    required_on_ingest: bool
    ignore_on_ingest: bool


@strawberry.type
class IngestOption:
    id: IngestType
    name: str
    description: str
    columns: list[IngestColumn]


@strawberry.type
class IngestOptions:
    options: list[IngestOption]


@strawberry.type
class IngestOptionItems:
    items: list[DictScalar]


@strawberry.type
class IngestSubmitType:
    key: IngestType
    added: list[DictScalar]
    updated: list[DictScalar]
    deleted: list[DictScalar]

    @strawberry.field
    async def items(self, info: Info) -> list[DictScalar]:
        items = await info.context.ingest.get_items(self.key)
        return jsonable_encoder(items)  # type: ignore


# Job Safety Briefing Object Types


@strawberry.experimental.pydantic.input(
    model=models.JSBMetadata,
    name="JSBMetadataInput",
    all_fields=True,
)
class JSBMetadataInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.JSBMetadata,
    name="JSBMetadata",
    all_fields=True,
)
class JSBMetadataType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.GPSCoordinates,
    name="GPSCoordinatesInput",
    all_fields=True,
)
class GPSCoordinatesInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.GPSCoordinates,
    name="GPSCoordinates",
    all_fields=True,
)
class GPSCoordinatesType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.WorkLocation, name="WorkLocationInput", all_fields=True
)
class WorkLocationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.WorkLocation, name="WorkLocation", all_fields=True
)
class WorkLocationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EmergencyContact,
    name="EmergencyContactInput",
    all_fields=True,
)
class EmergencyContactInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EmergencyContact,
    name="EmergencyContact",
    all_fields=True,
)
class EmergencyContactType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.WorkPackageMetadata,
    name="WorkPackageMetadataInput",
    all_fields=True,
)
class WorkPackageMetadataInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.WorkPackageMetadata,
    name="WorkPackageMetadata",
    all_fields=True,
)
class WorkPackageMetadataType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.MedicalFacility,
    name="MedicalFacilityInput",
    all_fields=True,
)
class MedicalFacilityInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.MedicalFacility,
    name="MedicalFacility",
    all_fields=True,
)
class MedicalFacilityType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CustomMedicalFacility,
    name="CustomMedicalFacilityInput",
    all_fields=True,
)
class CustomMedicalFacilityInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CustomMedicalFacility,
    name="CustomMedicalFacility",
    all_fields=True,
)
class CustomMedicalFacilityType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.AEDInformation,
    name="AEDInformationInput",
    all_fields=True,
)
class AEDInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.AEDInformation,
    name="AEDInformation",
    all_fields=True,
)
class AEDInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.TaskSelectionConcept, name="TaskSelectionConceptInput", all_fields=True
)
class TaskSelectionConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.TaskSelectionConcept, name="TaskSelectionConcept", all_fields=True
)
class TaskSelectionConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.RecommendedTaskSelection,
    name="RecommendedTaskSelectionInput",
    all_fields=True,
)
class RecommendedTaskSelectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.RecommendedTaskSelection,
    name="RecommendedTaskSelection",
    all_fields=True,
)
class RecommendedTaskSelectionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CriticalRiskArea, name="CriticalRiskAreaInput", all_fields=True
)
class CriticalRiskAreaInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CriticalRiskArea, name="CriticalRiskArea", all_fields=True
)
class CriticalRiskAreaType:
    pass


VoltageTypeEnum = strawberry.enum(models.VoltageType)


@strawberry.experimental.pydantic.input(
    model=models.Voltage, name="VoltageInput", all_fields=True
)
class VoltageInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.Voltage, name="Voltage", all_fields=True
)
class VoltageType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EWPMetadata, name="EWPMetadataInput", all_fields=True
)
class EWPMetadataInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EWPMetadata, name="EWPMetadata", all_fields=True
)
class EWPMetadataType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EWPEquipmentInformation,
    name="EWPEquipmentInformationInput",
    all_fields=True,
)
class EWPEquipmentInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EWPEquipmentInformation,
    name="EquipmentInformation",
    all_fields=True,
)
class EWPEquipmentInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EWP, name="EWPInput", all_fields=True
)
class EWPInput:
    pass


@strawberry.experimental.pydantic.type(model=models.EWP, name="EWP", all_fields=True)
class EWPType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EnergySourceControl,
    name="EnergySourceControlInput",
    all_fields=True,
)
class EnergySourceControlInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EnergySourceControl,
    name="EnergySourceControl",
    all_fields=True,
)
class EnergySourceControlType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.SiteConditionSelection,
    name="SiteConditionSelectionInput",
    all_fields=True,
)
class SiteConditionSelectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.SiteConditionSelection,
    name="SiteConditionSelection",
    all_fields=True,
)
class SiteConditionSelectionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.ControlSelection,
    name="ControlSelectionInput",
    all_fields=True,
)
class ControlSelectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.ControlSelection,
    name="ControlSelection",
    all_fields=True,
)
class ControlSelectionType:
    pass


control_ids_deprecation_reason = "This field is deprecated due to redundancy with the 'controlSelections'. Please use 'controlSelections' going forward."


@strawberry.experimental.pydantic.input(
    model=models.ControlAssessment, name="ControlAssessmentInput"
)
class ControlAssessmentInput:
    hazard_id: strawberry.auto
    control_ids: strawberry.auto = strawberry.field(
        deprecation_reason=control_ids_deprecation_reason,
    )
    control_selections: strawberry.auto
    name: Optional[str]


@strawberry.experimental.pydantic.type(
    model=models.ControlAssessment,
    name="ControlAssessment",
)
class ControlAssessmentType:
    hazard_id: strawberry.auto
    control_ids: strawberry.auto = strawberry.field(
        deprecation_reason=control_ids_deprecation_reason,
    )
    control_selections: strawberry.auto


@strawberry.experimental.pydantic.type(
    model=models.WorkProcedureSelection,
    name="WorkProcedureSelection",
    all_fields=True,
)
class WorkProcedureSelectionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.WorkProcedureSelection,
    name="WorkProcedureSelectionInput",
    all_fields=True,
)
class WorkProcedureSelectionInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.WorkTypeConcept,
    name="WorkTypeConceptInput",
    all_fields=True,
)
class WorkTypeConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.WorkTypeConcept,
    name="WorkTypeConceptType",
    all_fields=True,
)
class WorkTypeConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.OpCoObservedConcept,
    name="OpCoObservedConceptInput",
    all_fields=True,
)
class OpCoObservedConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.OpCoObservedConcept,
    name="OpCoObservedConceptType",
    all_fields=True,
)
class OpCoObservedConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.DepartmentObservedConcept,
    name="DepartmentObservedConceptInput",
    all_fields=True,
)
class DepartmentObservedConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DepartmentObservedConcept,
    name="DepartmentObservedConceptType",
    all_fields=True,
)
class DepartmentObservedConceptType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CrewInformation,
    name="CrewInformationType",
    all_fields=True,
)
class CrewInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CrewInformation,
    name="CrewInformationInput",
    all_fields=True,
)
class CrewInformationInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.ActivityConcept,
    name="ActivityConceptInput",
    all_fields=True,
)
class ActivityConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.ActivityConcept,
    name="ActivityConceptType",
    all_fields=True,
)
class ActivityConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.GroupDiscussion,
    name="GroupDiscussionInput",
    all_fields=True,
)
class GroupDiscussionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.GroupDiscussion,
    name="GroupDiscussionType",
    all_fields=True,
)
class GroupDiscussionType:
    pass


# Can't use all_fields=True because `completions` should be ignored on input
@strawberry.experimental.pydantic.input(
    model=models.JobSafetyBriefingLayout, name="SaveJobSafetyBriefingInput"
)
class SaveJobSafetyBriefingInput:
    jsb_id: strawberry.auto
    jsb_metadata: strawberry.auto
    work_package_metadata: strawberry.auto
    gps_coordinates: strawberry.auto
    work_location: strawberry.auto
    emergency_contacts: strawberry.auto
    nearest_medical_facility: strawberry.auto
    custom_nearest_medical_facility: strawberry.auto
    aed_information: strawberry.auto
    task_selections: strawberry.auto
    recommended_task_selections: strawberry.auto
    activities: strawberry.auto
    critical_risk_area_selections: strawberry.auto
    energy_source_control: strawberry.auto
    work_procedure_selections: strawberry.auto
    other_work_procedures: strawberry.auto
    distribution_bulletin_selections: strawberry.auto
    minimum_approach_distance: strawberry.auto
    site_condition_selections: strawberry.auto
    control_assessment_selections: strawberry.auto
    additional_ppe: strawberry.auto
    hazards_and_controls_notes: strawberry.auto
    crew_sign_off: strawberry.auto
    photos: strawberry.auto
    group_discussion: strawberry.auto
    documents: strawberry.auto
    source_info: strawberry.auto


@strawberry.experimental.pydantic.input(
    model=models.ControlsConcept,
    name="ControlsConceptInput",
    all_fields=True,
)
class ControlsConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.ControlsConcept,
    name="ControlsConceptType",
    all_fields=True,
)
class ControlsConceptType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EBOControlsConcept,
    name="EBOControlsConceptType",
    all_fields=True,
)
class EBOControlsConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOControlsConcept,
    name="EBOControlsConceptInput",
    all_fields=True,
)
class EBOControlsConceptInput:
    pass


# Can't use all_fields=True because `jsb_id` is not optional
# in the object type
# TODO do this better by using generics and decorators, etc.
@strawberry.experimental.pydantic.type(
    model=models.JobSafetyBriefingLayout,
    name="JobSafetyBriefingLayout",
)
class JobSafetyBriefingLayoutType:
    jsb_id: uuid.UUID
    jsb_metadata: strawberry.auto
    work_package_metadata: strawberry.auto
    gps_coordinates: strawberry.auto
    work_location: strawberry.auto
    emergency_contacts: strawberry.auto
    nearest_medical_facility: strawberry.auto
    custom_nearest_medical_facility: strawberry.auto
    aed_information: strawberry.auto
    task_selections: strawberry.auto
    recommended_task_selections: strawberry.auto
    activities: strawberry.auto
    critical_risk_area_selections: strawberry.auto
    energy_source_control: strawberry.auto
    work_procedure_selections: strawberry.auto
    other_work_procedures: strawberry.auto
    distribution_bulletin_selections: strawberry.auto
    minimum_approach_distance: strawberry.auto
    site_condition_selections: strawberry.auto
    control_assessment_selections: strawberry.auto
    additional_ppe: strawberry.auto
    hazards_and_controls_notes: strawberry.auto
    crew_sign_off: strawberry.auto
    photos: strawberry.auto
    group_discussion: strawberry.auto
    documents: strawberry.auto
    completions: strawberry.auto
    source_info: strawberry.auto


@strawberry.type(name="JobSafetyBriefing")
class JobSafetyBriefingType(FormInterface):
    id: uuid.UUID
    _contents: strawberry.Private[JobSafetyBriefingLayoutType]
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    date: datetime.date
    archived_at: Optional[datetime.date]

    project_location_id: strawberry.Private[Optional[uuid.UUID]]
    name: str = strawberry.field(default="Job Safety Briefing")
    status: FormStatus

    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> JobSafetyBriefingLayoutType:
        return self._contents

    @strawberry.field()
    async def work_package(self, info: Info) -> ProjectType | None:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )

        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on Job Safety Briefing {self.id}"
            )
        if project_location.project is not None:
            return ProjectType.from_orm(project_location.project)
        else:
            return None

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on Job Safety Briefing{self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        work_location = await info.context.job_safety_briefings.with_work_location.load(
            self.id
        )
        if work_location:
            if not self.project_location_id:
                description = work_location.get("description")
                if description is not None:
                    return str(description)

            address = work_location.get("address")
            if address is not None:
                return str(address)

        return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        all_supervisors = await info.context.jsb_supervisors.jsb_supervisors.load_many(
            [self.id]
        )

        results: list[JSBSupervisorType] = []
        for supervisors in all_supervisors:
            if supervisors:
                for supervisor in supervisors:
                    if supervisor:
                        results.append(JSBSupervisorType.from_orm(supervisor))

        if len(results) == 0:
            return None

        return results

    @staticmethod
    def from_orm(
        jsb: models.JobSafetyBriefing, operating_hq: Optional[str] = None
    ) -> "JobSafetyBriefingType":
        raw_contents = jsb.contents or {}
        contents = models.JobSafetyBriefingLayout.parse_obj(raw_contents)
        contents.jsb_id = jsb.id
        return JobSafetyBriefingType(
            id=jsb.id,
            created_at=jsb.created_at,
            created_by_id=jsb.created_by_id,
            completed_at=jsb.completed_at,
            completed_by_id=jsb.completed_by_id,
            date=jsb.date_for,
            project_location_id=jsb.project_location_id,
            status=jsb.status,
            source=jsb.source,
            form_id=jsb.form_id,
            _contents=JobSafetyBriefingLayoutType.from_pydantic(contents),
            operating_hq=operating_hq,
            updated_at=jsb.updated_at,
            archived_at=jsb.archived_at,
        )


@strawberry.experimental.pydantic.input(
    model=models.DocumentsProvided,
    name="DocumentsProvidedInput",
    all_fields=True,
)
class DocumentsProvidedInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.DocumentsProvided,
    name="DocumentsProvidedType",
    all_fields=True,
)
class DocumentsProvidedType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EnergyControlInfo,
    name="EnergyControlInfoInput",
    all_fields=True,
)
class EnergyControlInfoInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.PointsOfProtection,
    name="PointsOfProtectionType",
    all_fields=True,
)
class PointsOfProtectionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.PointsOfProtection,
    name="PointsOfProtectionInput",
    all_fields=True,
)
class PointsOfProtectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EnergyControlInfo,
    name="EnergyControlInfoType",
    all_fields=True,
)
class EnergyControlInfoType:
    pass


@strawberry.type(name="UIConfigs")
class UIConfigType:
    id: uuid.UUID
    _contents: JSON
    tenant_id: strawberry.Private[uuid.UUID]
    form_type: Optional[FormsType]

    @strawberry.field
    async def contents(self) -> JSON:
        raw_contents = self._contents
        result = jsonable_encoder(raw_contents)
        return result

    @staticmethod
    def from_orm(config: models.UIConfig) -> "UIConfigType":
        raw_contents = config.contents or {}
        contents = raw_contents
        return UIConfigType(
            id=config.id,
            tenant_id=config.tenant_id,
            form_type=config.form_type,
            _contents=contents,
        )


@strawberry.experimental.pydantic.input(
    model=models.ObservationDetailsConcept,
    name="ObservationDetailsConceptInput",
    all_fields=True,
)
class ObservationDetailsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.ObservationDetailsConcept,
    name="ObservationDetailsConceptType",
    all_fields=True,
)
class ObservationDetailsType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.HazardObservationConcept,
    name="HazardObservationConceptType",
    all_fields=True,
)
class HazardObservationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.HazardObservationConcept,
    name="HazardObservationConceptInput",
    all_fields=True,
)
class HazardObservationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EBOHazardObservationConcept,
    name="EBOHazardObservationConceptType",
    all_fields=True,
)
class EBOHazardObservationConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOHazardObservationConcept,
    name="EBOHazardObservationConceptInput",
    all_fields=True,
)
class EBOHazardObservationConceptInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.HighEnergyTaskConcept,
    name="HighEnergyTaskConceptInput",
    all_fields=True,
)
class HighEnergyTaskConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.HighEnergyTaskConcept,
    name="HighEnergyTaskConceptType",
    all_fields=True,
)
class HighEnergyTaskConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.PersonnelConcept,
    name="PersonnelConceptInput",
    all_fields=True,
)
class PersonnelConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.PersonnelConcept,
    name="PersonnelConceptType",
    all_fields=True,
)
class PersonnelConceptType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EBOHighEnergyTaskConcept,
    name="EBOHighEnergyTaskConceptType",
    all_fields=True,
)
class EBOHighEnergyTaskConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOHighEnergyTaskConcept,
    name="EBOHighEnergyTaskConceptInput",
    all_fields=True,
)
class EBOHighEnergyTaskConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EBOTaskSelectionConcept,
    name="EBOTaskSelectionConceptType",
    all_fields=True,
)
class EBOTaskSelectionConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOTaskSelectionConcept,
    name="EBOTaskSelectionConceptInput",
    all_fields=True,
)
class EBOTaskSelectionConceptInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EBOActivityConcept, name="EBOActivityConceptType", all_fields=True
)
class EBOActivityConceptType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOActivityConcept, name="EBOActivityConceptInput", all_fields=False
)
class EBOActivityConceptInput:
    id: uuid.UUID
    name: strawberry.auto
    tasks: strawberry.auto


@strawberry.experimental.pydantic.type(
    model=models.EBOSummary, name="EBOSummaryType", all_fields=True
)
class EBOSummaryType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EBOSummary, name="EBOSummaryInput", all_fields=True
)
class EBOSummaryInput:
    pass


# Can't use all_fields=True because `completions` should be ignored on input
@strawberry.experimental.pydantic.input(
    model=models.EnergyBasedObservationLayout, name="EnergyBasedObservationInput"
)
class EnergyBasedObservationInput:
    details: strawberry.auto
    gps_coordinates: strawberry.auto
    activities: strawberry.auto
    high_energy_tasks: strawberry.auto
    historic_incidents: strawberry.auto
    additional_information: strawberry.auto
    photos: strawberry.auto
    summary: strawberry.auto
    personnel: strawberry.auto
    source_info: strawberry.auto


@strawberry.experimental.pydantic.type(
    model=models.EnergyBasedObservationLayout,
    name="EnergyBasedObservationLayout",
)
class EnergyBasedObservationLayoutType:
    details: strawberry.auto
    gps_coordinates: strawberry.auto
    activities: strawberry.auto
    high_energy_tasks: strawberry.auto
    historic_incidents: strawberry.auto
    additional_information: strawberry.auto
    photos: strawberry.auto
    summary: strawberry.auto
    personnel: strawberry.auto
    completions: strawberry.auto
    source_info: strawberry.auto


@strawberry.type(name="EnergyBasedObservation")
class EnergyBasedObservationType(FormInterface):
    id: uuid.UUID
    status: FormStatus
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    source: Optional[SourceInformation]
    form_id: Optional[str]
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    _contents: strawberry.Private[EnergyBasedObservationLayoutType]
    date: datetime.date
    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> EnergyBasedObservationLayoutType:
        return self._contents

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        work_location: str | None = (
            await info.context.energy_based_observations.with_work_location.load(
                self.id
            )
        )
        return work_location

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @staticmethod
    def from_orm(
        ebo: models.EnergyBasedObservation, operating_hq: Optional[str] = None
    ) -> "EnergyBasedObservationType":
        raw_contents = ebo.contents or {}
        contents = models.EnergyBasedObservationLayout.parse_obj(raw_contents)

        return EnergyBasedObservationType(
            id=ebo.id,
            status=ebo.status,
            created_by_id=ebo.created_by_id,
            created_at=ebo.created_at,
            completed_by_id=ebo.completed_by_id,
            completed_at=ebo.completed_at,
            date=ebo.date_for,
            source=ebo.source,
            form_id=ebo.form_id,
            _contents=EnergyBasedObservationLayoutType.from_pydantic(contents),
            operating_hq=operating_hq,
            updated_at=ebo.updated_at,
        )


@strawberry.type(name="Insight")
class InsightType:
    id: uuid.UUID
    tenant_id: strawberry.Private[uuid.UUID]
    name: str
    url: str
    description: Optional[str]
    visibility: bool
    created_at: datetime.datetime
    archived_at: strawberry.Private[Optional[datetime.datetime]]
    ordinal: strawberry.Private[int]

    @staticmethod
    def from_orm(insight: models.Insight) -> "InsightType":
        return InsightType(
            id=insight.id,
            tenant_id=insight.tenant_id,
            name=insight.name,
            url=insight.url,
            description=insight.description,
            visibility=insight.visibility,
            created_at=insight.created_at,
            archived_at=insight.archived_at,
            ordinal=insight.ordinal,
        )


@strawberry.input
class SiteLocationInput:
    latitude: Decimal
    longitude: Decimal
    date: datetime.date


@strawberry.experimental.pydantic.input(
    model=models.CreateInsightInput, all_fields=True
)
class CreateInsightInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.UpdateInsightInput, all_fields=True
)
class UpdateInsightInput:
    pass


@strawberry.type(name="CrewLeader")
class CrewLeaderType:
    id: uuid.UUID
    name: str
    created_at: datetime.datetime
    lanid: Optional[str]
    company_name: Optional[str]

    @staticmethod
    def from_orm(crew_leader: models.CrewLeader) -> "CrewLeaderType":
        return CrewLeaderType(
            id=crew_leader.id,
            name=crew_leader.name,
            created_at=crew_leader.created_at,
            lanid=crew_leader.lanid,
            company_name=crew_leader.company_name,
        )


@strawberry.type(name="RecentUsedCrewLeaderReturnType")
class RecentUsedCrewLeaderReturnType:
    name: str
    id: uuid.UUID

    def __hash__(self) -> int:
        return hash(self.name)  # Using name as the unique identifier

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RecentUsedCrewLeaderReturnType):
            return False
        return self.name == other.name


@strawberry.input
class MapExtentInput:
    x_min: float
    x_max: float
    y_max: float
    y_min: float


@strawberry.type(name="DatedActivitiesResponse")
class DatedActivitiesResponseType:
    date: datetime.date
    activities: list[ActivityType]


@strawberry.type(name="DatedTaskResponse")
class DatedTasksResponseType:
    date: datetime.date
    tasks: list[TaskType]


@strawberry.type(name="DatedJSBResponse")
class DatedJSBResponseType:
    date: datetime.date
    job_safety_briefings: list[JobSafetyBriefingType]


@strawberry.type(name="DatedReportsResponse")
class DatedReportsResponseType:
    date: datetime.date
    daily_reports: list[DailyReportType]


# Filter Location Date Range Type to be used when user wants to
# prefetch the data for specific date ranges for entities like
# Activities, JSB, Daily Reports, Tasks, Site Conditions.
@strawberry.type(name="FilterLocationDateRange")
class FilterLocationDateRangeType(ProjectLocationType):
    @strawberry.field()
    async def daily_reports(
        self, info: Info, filter_date_range: DateRangeInput
    ) -> list[DatedReportsResponseType]:
        loaded_daily_reports = await info.context.project_locations.daily_reports(
            filter_start_date=filter_date_range.start_date,
            filter_end_date=filter_date_range.end_date,
        ).load(self.id)

        # Initialize dictionary to store reports for each date
        reports_by_date = defaultdict(list)

        # Organize daily reports into dictionary by date
        for report in loaded_daily_reports:
            report_date = report.date_for
            # Ensure daily report falls within the specified date range
            if (
                filter_date_range.start_date
                <= report_date
                <= filter_date_range.end_date
            ):
                reports_by_date[report_date].append(report)

        # Convert dictionary to list of DatedDailyReports objects
        dated_reports_response = [
            DatedReportsResponseType(
                date=date,
                daily_reports=[DailyReportType.from_orm(report) for report in reports],
            )
            for date, reports in reports_by_date.items()
        ]
        return dated_reports_response

    @strawberry.field()
    async def job_safety_briefings(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
    ) -> list[DatedJSBResponseType]:
        loaded_job_safety_briefings = (
            await info.context.project_locations.job_safety_briefings(
                filter_start_date=filter_date_range.start_date,
                filter_end_date=filter_date_range.end_date,
            ).load(self.id)
        )
        # Initialize dictionary to store JSB for each date
        briefings_by_date = defaultdict(list)

        # Organize JSB into dictionary by date
        for briefing in loaded_job_safety_briefings:
            briefing_date = briefing.date_for

            # Ensure briefing falls within the specified date range
            if (
                filter_date_range.start_date
                <= briefing_date
                <= filter_date_range.end_date
            ):
                briefings_by_date[briefing_date].append(briefing)

        # Convert dictionary to list of DatedActivitiesResponseType objects
        dated_briefings_response = [
            DatedJSBResponseType(
                date=date,
                job_safety_briefings=[
                    JobSafetyBriefingType.from_orm(briefing) for briefing in briefings
                ],
            )
            for date, briefings in briefings_by_date.items()
        ]

        return dated_briefings_response

    @strawberry.field()
    async def dated_site_conditions(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[DatedSiteConditions]:
        filter_tenant_settings: bool = info.context.params.get(
            "filter_tenant_settings", False
        )

        date_range = [
            filter_date_range.start_date + timedelta(days=i)
            for i in range(
                (filter_date_range.end_date - filter_date_range.start_date).days + 1
            )
        ]

        loaded_site_conditions: list[
            tuple[LibrarySiteCondition, SiteCondition]
        ] = await info.context.project_locations.site_conditions(
            filter_start_date=filter_date_range.start_date,
            filter_end_date=filter_date_range.end_date,
            order_by=order_by_to_pydantic(order_by),
            filter_tenant_settings=filter_tenant_settings,
        ).load(
            self.id
        )

        # Initialize a dictionary to store site conditions segregated by date
        dated_site_conditions: dict[datetime.date, list[SiteConditionType]] = {
            date: [] for date in date_range
        }
        # Iterate over loaded site conditions
        for library_site_condition, site_condition in loaded_site_conditions:
            site_condition_type = SiteConditionType.from_orm(site_condition)
            date = site_condition.date

            if date is None:
                # If the date is None, it is applicable to all dates within the range
                for date_in_range in date_range:
                    dated_site_conditions[date_in_range].append(site_condition_type)
            else:
                # Otherwise, append the site condition to the corresponding date
                dated_site_conditions[date].append(site_condition_type)

        # Filter out dates with no site conditions
        dated_site_conditions = {
            date: site_conditions
            for date, site_conditions in dated_site_conditions.items()
            if site_conditions
        }

        return [
            DatedSiteConditions(date=date, site_conditions=site_conditions)
            for date, site_conditions in dated_site_conditions.items()
        ]

    @strawberry.field()
    async def dated_activities(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
        order_by: Optional[list[OrderByInput]] = None,
    ) -> list[DatedActivitiesResponseType]:
        # Load all activities within the given date range
        all_activities = await info.context.activities.by_location(
            filter_start_date=filter_date_range.start_date,
            filter_end_date=filter_date_range.end_date,
            order_by=order_by_to_pydantic(order_by),
        ).load(self.id)

        # Initialize dictionary to store activities for each date
        activities_by_date = defaultdict(list)

        # Organize activities into dictionary by date
        for activity in all_activities:
            start_date = activity.start_date
            end_date = activity.end_date

            # Ensure activities span the date range
            if (
                start_date <= filter_date_range.end_date
                and end_date >= filter_date_range.start_date
            ):
                # Calculate intersection of dates to ensure activities within range are included
                start = max(start_date, filter_date_range.start_date)
                end = min(end_date, filter_date_range.end_date)

                # Iterate through dates and add activity to corresponding date
                for date in range((end - start).days + 1):
                    current_date = start + timedelta(days=date)
                    activities_by_date[current_date].append(activity)

        # Convert dictionary to list of DatedActivitiesResponseType objects
        dated_activities_response = [
            DatedActivitiesResponseType(
                date=date,
                activities=[ActivityType.from_orm(activity) for activity in activities],
            )
            for date, activities in activities_by_date.items()
        ]

        return dated_activities_response

    @strawberry.field()
    async def dated_tasks(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
        order_by: Optional[list[TaskOrderByInput]] = None,
    ) -> list[DatedTasksResponseType]:
        loaded_tasks = await info.context.project_locations.tasks(
            filter_start_date=filter_date_range.start_date,
            filter_end_date=filter_date_range.end_date,
            order_by=order_by_to_pydantic(order_by),
        ).load(self.id)
        # Initialize dictionary to store tasks for each date
        tasks_by_date = defaultdict(list)

        # Organize tasks into dictionary by date
        for task in loaded_tasks:
            task_date = task[1]
            start_date = task_date.start_date
            end_date = task_date.end_date

            # Ensure tasks span the date range
            if (
                start_date <= filter_date_range.end_date
                and end_date >= filter_date_range.start_date
            ):
                # Calculate intersection of dates to ensure tasks within range are included
                start = max(start_date, filter_date_range.start_date)
                end = min(end_date, filter_date_range.end_date)

                # Iterate through dates and add tasks to corresponding date
                for date in range((end - start).days + 1):
                    current_date = start + timedelta(days=date)
                    tasks_by_date[current_date].append(task_date)

        # Convert dictionary to list of DatedTasksResponseType objects
        dated_tasks_response = [
            DatedTasksResponseType(
                date=date,
                tasks=[TaskType.from_orm(task) for task in tasks],
            )
            for date, tasks in tasks_by_date.items()
        ]

        return dated_tasks_response

    # When risk needs to be fetched for specific date ranges this field can be utilised.
    @strawberry.field()
    async def risk_levels(
        self,
        info: Info,
        filter_date_range: DateRangeInput,
    ) -> list[DatedRiskLevel]:
        risk_dict: dict[datetime.date, RiskLevel] = {}

        current_date = filter_date_range.start_date
        while current_date <= filter_date_range.end_date:
            _date = parse_input_date(current_date)
            risk_level = await info.context.risk_model.project_location_risk_level(
                _date
            ).load(self.id)
            risk_dict.update({_date: risk_level})
            current_date += datetime.timedelta(days=1)
        return [
            DatedRiskLevel(date=date, risk_level=RiskLevel(risk_level.value))
            for date, risk_level in risk_dict.items()
        ]


@strawberry.type(name="ProjectLocationResponse")
class ProjectLocationResponseType:
    locations_count: int
    filter_locations_date_range: list[FilterLocationDateRangeType]


@strawberry.type(name="JobSafetyBriefingFormsList")
class JobSafetyBriefingFormsListType(FormInterfaceWithContents):
    id: uuid.UUID
    _contents: JSON
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    date: datetime.date
    project_location_id: strawberry.Private[Optional[uuid.UUID]]
    name: str = strawberry.field(default="Job Safety Briefing")
    status: FormStatus
    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> JSON:
        raw_contents = self._contents
        encoded_contents = jsonable_encoder(raw_contents)
        result = dict_keys_snake_to_camel(encoded_contents)
        return result

    @strawberry.field()
    async def work_package(self, info: Info) -> ProjectType | None:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )

        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on Job Safety Briefing {self.id}"
            )
        if project_location.project is not None:
            return ProjectType.from_orm(project_location.project)
        else:
            return None

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on Job Safety Briefing{self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        work_location = await info.context.job_safety_briefings.with_work_location.load(
            self.id
        )
        if work_location:
            if not self.project_location_id:
                description = work_location.get("description")
                if description is not None:
                    return str(description)

            address = work_location.get("address")
            if address is not None:
                return str(address)

        return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        all_supervisors = await info.context.jsb_supervisors.jsb_supervisors.load_many(
            [self.id]
        )

        results: list[JSBSupervisorType] = []
        for supervisors in all_supervisors:
            if supervisors:
                for supervisor in supervisors:
                    if supervisor:
                        results.append(JSBSupervisorType.from_orm(supervisor))

        if len(results) == 0:
            return None

        return results

    @staticmethod
    def from_orm(
        jsb: models.JobSafetyBriefing, operating_hq: Optional[str] = None
    ) -> "JobSafetyBriefingFormsListType":
        raw_contents = jsb.contents or {}
        contents = raw_contents
        contents["jsb_id"] = str(jsb.id)
        return JobSafetyBriefingFormsListType(
            id=jsb.id,
            created_at=jsb.created_at,
            created_by_id=jsb.created_by_id,
            completed_at=jsb.completed_at,
            completed_by_id=jsb.completed_by_id,
            date=jsb.date_for,
            project_location_id=jsb.project_location_id,
            status=jsb.status,
            source=jsb.source,
            form_id=jsb.form_id,
            _contents=contents,
            operating_hq=operating_hq,
            updated_at=jsb.updated_at,
        )


@strawberry.type(name="EnergyBasedObservationFormsList")
class EnergyBasedObservationFormsListType(FormInterfaceWithContents):
    id: uuid.UUID
    status: FormStatus
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    _contents: JSON
    date: datetime.date
    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> JSON:
        raw_contents = self._contents
        encoded_contents = jsonable_encoder(raw_contents)
        result = dict_keys_snake_to_camel(encoded_contents)
        return result

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        work_location: str | None = (
            await info.context.energy_based_observations.with_work_location.load(
                self.id
            )
        )
        return work_location

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @staticmethod
    def from_orm(
        ebo: models.EnergyBasedObservation, operating_hq: Optional[str] = None
    ) -> "EnergyBasedObservationFormsListType":
        raw_contents = ebo.contents or {}
        contents = raw_contents

        return EnergyBasedObservationFormsListType(
            id=ebo.id,
            status=ebo.status,
            created_by_id=ebo.created_by_id,
            created_at=ebo.created_at,
            completed_by_id=ebo.completed_by_id,
            completed_at=ebo.completed_at,
            date=ebo.date_for,
            source=ebo.source,
            form_id=ebo.form_id,
            _contents=contents,
            operating_hq=operating_hq,
            updated_at=ebo.updated_at,
        )


@strawberry.type(name="DailyReportFormsList")
class DailyReportFormsListType(Auditable, FormInterfaceWithContents):
    id: uuid.UUID
    project_location_id: strawberry.Private[uuid.UUID]
    date: datetime.date
    status: FormStatus
    source: Optional[SourceInformation]
    form_id: Optional[str]
    _sections: strawberry.Private[Optional[SectionsType]]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    sectionsJSON: Optional[JSONScalar] = strawberry.field(default=None)
    operating_hq: Optional[str] = None

    @strawberry.field()
    async def sections(self, info: Info) -> Optional[SectionsType]:
        if self._sections and self._sections.job_hazard_analysis:
            await info.context.daily_reports.inject_job_hazard_analysis_names(
                self._sections.job_hazard_analysis
            )
        return self._sections

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)
        else:
            return None

    @strawberry.field()
    async def work_package(self, info: Info) -> ProjectType | None:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )

        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on daily report {self.id}"
            )
        if project_location.project is not None:
            return ProjectType.from_orm(project_location.project)
        else:
            return None

    @strawberry.field()
    async def location(self, info: Info) -> ProjectLocationType:
        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on daily report {self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        location: ProjectLocationType = await self.location(info)
        if location:
            return location.name
        else:
            return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        return False

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @staticmethod
    def from_orm(
        daily_report: models.DailyReport, operating_hq: Optional[str] = None
    ) -> "DailyReportFormsListType":
        sections_type = None
        sections = daily_report.sections_to_pydantic()
        if sections is not None:
            sections_type = SectionsType.from_pydantic(sections)

        return DailyReportFormsListType(
            id=daily_report.id,
            date=daily_report.date_for,
            status=daily_report.status,
            created_by_id=daily_report.created_by_id,
            created_at=daily_report.created_at,
            completed_by_id=daily_report.completed_by_id,
            completed_at=daily_report.completed_at,
            sectionsJSON=sections.json() if sections else None,  # type: ignore
            _sections=sections_type,
            source=daily_report.source,
            form_id=daily_report.form_id,
            project_location_id=daily_report.project_location_id,
            operating_hq=operating_hq,
            updated_at=daily_report.updated_at,
        )


@strawberry.experimental.pydantic.input(
    model=models.LocationInformation,
    name="LocationInformationInput",
    all_fields=True,
)
class LocationInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.LocationInformation,
    name="LocationInformationType",
    all_fields=True,
)
class LocationInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.BarnLocation,
    name="BarnLocationInput",
    all_fields=True,
)
class BarnLocationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.BarnLocation,
    name="BarnLocationType",
    all_fields=True,
)
class BarnLocationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.MininimumApproachDistance,
    name="MininimumApproachDistanceInput",
    all_fields=True,
)
class MininimumApproachDistanceInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.MininimumApproachDistance,
    name="MininimumApproachDistanceType",
    all_fields=True,
)
class MininimumApproachDistanceType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.VoltageInformationFromConfig,
    name="VoltageInformationFromConfigInput",
    all_fields=True,
)
class VoltageInformationFromConfigInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.VoltageInformationFromConfig,
    name="VoltageInformationFromConfigType",
    all_fields=True,
)
class VoltageInformationFromConfigType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.VoltageInformationV2,
    name="VoltageInformationV2Input",
    all_fields=True,
)
class VoltageInformationV2Input:
    pass


@strawberry.experimental.pydantic.type(
    model=models.VoltageInformationV2,
    name="VoltageInformationV2Type",
    all_fields=True,
)
class VoltageInformationV2Type:
    pass


@strawberry.experimental.pydantic.input(
    model=models.LocationInformationV2,
    name="LocationInformationV2Input",
    all_fields=True,
)
class LocationInformationV2Input:
    pass


@strawberry.experimental.pydantic.type(
    model=models.LocationInformationV2,
    name="LocationInformationV2Type",
    all_fields=True,
)
class LocationInformationV2Type:
    pass


@strawberry.experimental.pydantic.input(
    model=models.VoltageInformation,
    name="VoltageInformationInput",
    all_fields=True,
)
class VoltageInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.VoltageInformation,
    name="VoltageInformationType",
    all_fields=True,
)
class VoltageInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.FirstAidLocation,
    name="FirstAidLocationInput",
    all_fields=True,
)
class FirstAidLocationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.FirstAidLocation,
    name="FirstAidLocationType",
    all_fields=True,
)
class FirstAidLocationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.BurnKitLocation,
    name="BurnKitLocationInput",
    all_fields=True,
)
class BurnKitLocationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.BurnKitLocation,
    name="BurnKitLocationType",
    all_fields=True,
)
class BurnKitLocationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.PrimaryFireSupressionLocation,
    name="PrimaryFireSupressionLocationInput",
    all_fields=True,
)
class PrimaryFireSupressionLocationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.PrimaryFireSupressionLocation,
    name="PrimaryFireSupressionLocationType",
    all_fields=True,
)
class PrimaryFireSupressionLocationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.AEDInformationData,
    name="AEDInformationDataInput",
    all_fields=True,
)
class AEDInformationDataInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.AEDInformationData,
    name="AEDInformationDataType",
    all_fields=True,
)
class AEDInformationDataType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.MedicalInformation,
    name="MedicalInformationInput",
    all_fields=True,
)
class MedicalInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.MedicalInformation,
    name="MedicalInformationType",
    all_fields=True,
)
class MedicalInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CriticalTasksSelection,
    name="CriticalTasksSelectionInput",
    all_fields=True,
)
class CriticalTasksSelectionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CriticalTasksSelection,
    name="CriticalTasksSelectionType",
    all_fields=True,
)
class CriticalTasksSelectionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.NatGridSiteCondition,
    name="NatGridSiteConditionInput",
    all_fields=True,
)
class NatGridSiteConditionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.NatGridSiteCondition,
    name="NatGridSiteConditionType",
    all_fields=True,
)
class NatGridSiteConditionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.NatGridTaskHistoricIncident,
    name="NatGridTaskHistoricIncidentInput",
    all_fields=True,
)
class NatGridTaskHistoricIncidentInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.NatGridTaskHistoricIncident,
    name="NatGridTaskHistoricIncidentType",
    all_fields=True,
)
class NatGridTaskHistoricIncidentType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.GeneralReferenceMaterial,
    name="GeneralReferenceMaterialInput",
    all_fields=True,
)
class GeneralReferenceMaterialInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.GeneralReferenceMaterial,
    name="GeneralReferenceMaterialType",
    all_fields=True,
)
class GeneralReferenceMaterialType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.ClearanceTypes,
    name="ClearanceTypesInput",
    all_fields=True,
)
class ClearanceTypesInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.ClearanceTypes,
    name="ClearanceTypesType",
    all_fields=True,
)
class ClearanceTypesType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.NatGridEnergySourceControl,
    name="NatGridEnergySourceControlInput",
    all_fields=True,
)
class NatGridEnergySourceControlInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.NatGridEnergySourceControl,
    name="NatGridEnergySourceControlType",
    all_fields=True,
)
class NatGridEnergySourceControlType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.Attachments,
    name="AttachmentsInput",
    all_fields=True,
)
class AttachmentsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.Attachments,
    name="AttachmentsType",
    all_fields=True,
)
class AttachmentsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.GroupDiscussionInformation,
    name="GroupDiscussionInformationInput",
    all_fields=True,
)
class GroupDiscussionInformationInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.GroupDiscussionInformation,
    name="GroupDiscussionInformationType",
    all_fields=True,
)
class GroupDiscussionInformationType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.UserInfo,
    name="UserInfoInput",
    all_fields=True,
)
class UserInfoInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.UserInfo,
    name="UserInfoType",
    all_fields=True,
)
class UserInfoType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.MultipleCrews,
    name="MultipleCrewsInput",
    all_fields=True,
)
class MultipleCrewsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.MultipleCrews,
    name="MultipleCrewsType",
    all_fields=True,
)
class MultipleCrewsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CrewInfo,
    name="CrewInfoInput",
    all_fields=True,
)
class CrewInfoInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CrewInfo,
    name="CrewInfoType",
    all_fields=True,
)
class CrewInfoType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CrewSignOff,
    name="CrewSignOffInput",
    all_fields=True,
)
class CrewSignOffInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CrewSignOff,
    name="CrewSignOffType",
    all_fields=True,
)
class CrewSignOffType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.PostJobBriefDiscussion,
    name="PostJobBriefDiscussionInput",
    all_fields=True,
)
class PostJobBriefDiscussionInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.PostJobBriefDiscussion,
    name="PostJobBriefDiscussionType",
    all_fields=True,
)
class PostJobBriefDiscussionType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.PostJobBrief,
    name="PostJobBriefInput",
    all_fields=True,
)
class PostJobBriefInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.PostJobBrief,
    name="PostJobBriefType",
    all_fields=True,
)
class PostJobBriefType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CrewInformationData,
    name="CrewInformationDataInput",
    all_fields=True,
)
class CrewInformationDataInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CrewInformationData,
    name="CrewInformationDataType",
    all_fields=True,
)
class CrewInformationDataType:
    pass


@strawberry.experimental.pydantic.type(
    model=models.SupervisorSignOff,
    name="SupervisorSignOffType",
    all_fields=True,
)
class SupervisorSignOffType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.SupervisorSignOff,
    name="SupervisorSignOffInput",
    all_fields=True,
)
class SupervisorSignOffInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.OperatingProcedure,
    name="OperatingProcedureType",
    all_fields=True,
)
class OperatingProcedureType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.OperatingProcedure,
    name="OperatingProcedureInput",
    all_fields=True,
)
class OperatingProcedureInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.TaskStandardOperatingProcedure,
    name="TaskStandardOperatingProcedureType",
    all_fields=True,
)
class TaskStandardOperatingProcedureType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EnergyControls,
    name="EnergyControlsInput",
    all_fields=True,
)
class EnergyControlsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EnergyControls,
    name="EnergyControlsype",
    all_fields=True,
)
class EnergyControlsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.EnergyHazards,
    name="EnergyHazardsInput",
    all_fields=True,
)
class EnergyHazardsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.EnergyHazards,
    name="EnergyHazardsType",
    all_fields=True,
)
class EnergyHazardsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.HighLowEnergyHazards,
    name="HighLowEnergyHazardsInput",
    all_fields=True,
)
class HighLowEnergyHazardsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.HighLowEnergyHazards,
    name="HighLowEnergyHazardsType",
    all_fields=True,
)
class HighLowEnergyHazardsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.CustomHazards,
    name="CustomHazardsInput",
    all_fields=True,
)
class CustomHazardsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.CustomHazards,
    name="CustomHazardsType",
    all_fields=True,
)
class CustomHazardsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.TaskSiteConditonEnergyHazards,
    name="TaskSiteConditonEnergyHazardsInput",
    all_fields=True,
)
class TaskSiteConditonEnergyHazardsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.TaskSiteConditonEnergyHazards,
    name="TaskSiteConditonEnergyHazardsType",
    all_fields=True,
)
class TaskSiteConditonEnergyHazardsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.HazardsControls,
    name="HazardsControlsInput",
    all_fields=True,
)
class HazardsControlsInput:
    pass


@strawberry.experimental.pydantic.type(
    model=models.HazardsControls,
    name="HazardsControlsType",
    all_fields=True,
)
class HazardsControlsType:
    pass


@strawberry.experimental.pydantic.input(
    model=models.TaskStandardOperatingProcedure,
    name="TaskStandardOperatingProcedureInput",
    all_fields=True,
)
class TaskStandardOperatingProcedureInput:
    pass


@strawberry.experimental.pydantic.input(
    model=models.NatGridJobSafetyBriefingLayout,
    name="NatGridJobSafetyBriefingInput",
)
class NatGridJobSafetyBriefingInput:
    jsb_id: strawberry.auto
    jsb_metadata: strawberry.auto
    work_package_metadata: strawberry.auto
    gps_coordinates: strawberry.auto
    barn_location: strawberry.auto
    work_location: strawberry.auto
    work_location_with_voltage_info: strawberry.auto
    voltage_info: strawberry.auto
    medical_information: strawberry.auto
    activities: strawberry.auto
    critical_tasks_selections: strawberry.auto
    hazards_control: strawberry.auto
    energy_source_control: strawberry.auto
    attachment_section: strawberry.auto
    task_historic_incidents: strawberry.auto
    standard_operating_procedure: strawberry.auto
    general_reference_materials: strawberry.auto
    group_discussion: strawberry.auto
    crew_sign_off: strawberry.auto
    post_job_brief: strawberry.auto
    supervisor_sign_off: strawberry.auto
    site_conditions: strawberry.auto
    source_info: strawberry.auto


@strawberry.experimental.pydantic.type(
    model=models.NatGridJobSafetyBriefingLayout,
    name="NatGridJobSafetyBriefingLayout",
)
class NatGridJobSafetyBriefingLayoutType:
    jsb_id: strawberry.auto
    jsb_metadata: strawberry.auto
    work_package_metadata: strawberry.auto
    gps_coordinates: strawberry.auto
    barn_location: strawberry.auto
    work_location: strawberry.auto
    work_location_with_voltage_info: strawberry.auto
    voltage_info: strawberry.auto
    medical_information: strawberry.auto
    activities: strawberry.auto
    critical_tasks_selections: strawberry.auto
    hazards_control: strawberry.auto
    energy_source_control: strawberry.auto
    attachment_section: strawberry.auto
    task_historic_incidents: strawberry.auto
    standard_operating_procedure: strawberry.auto
    general_reference_materials: strawberry.auto
    group_discussion: strawberry.auto
    crew_sign_off: strawberry.auto
    post_job_brief: strawberry.auto
    supervisor_sign_off: strawberry.auto
    completions: strawberry.auto
    site_conditions: strawberry.auto
    source_info: strawberry.auto


@strawberry.type(name="NatGridJobSafetyBriefing")
class NatGridJobSafetyBriefingType(FormInterface):
    id: uuid.UUID
    _contents: strawberry.Private[NatGridJobSafetyBriefingLayoutType]
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    date: datetime.date
    project_location_id: strawberry.Private[Optional[uuid.UUID]]
    name: str = strawberry.field(default="NG Job Safety Briefing")
    status: FormStatus
    archived_at: Optional[datetime.date]
    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> NatGridJobSafetyBriefingLayoutType:
        return self._contents

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on NG Job Safety Briefing{self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        # work_location = (
        #     await info.context.natgrid_job_safety_briefings.with_work_location.load(
        #         self.id
        #     )
        # )
        work_location_with_voltage_info = await info.context.natgrid_job_safety_briefings.with_multiple_work_locations.load(
            self.id
        )
        if work_location_with_voltage_info:
            address = work_location_with_voltage_info[0].get("address")
            if address is not None:
                return str(address)

        return None

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        work_location_with_voltage_info = await info.context.natgrid_job_safety_briefings.with_multiple_work_locations.load(
            self.id
        )
        if work_location_with_voltage_info:
            if len(work_location_with_voltage_info) > 1:
                return True
            else:
                return False
        else:
            return None

    @strawberry.field()
    async def barn_location(self, info: Info) -> Optional[BarnLocationType]:
        barn_locations = (
            await info.context.natgrid_job_safety_briefings.with_barn_locations.load(
                self.id
            )
        )
        if barn_locations:
            return BarnLocationType(**barn_locations)

        return None

    @staticmethod
    def from_orm(
        jsb: models.NatGridJobSafetyBriefing, operating_hq: Optional[str] = None
    ) -> "NatGridJobSafetyBriefingType":
        raw_contents = jsb.contents or {}
        contents = models.NatGridJobSafetyBriefingLayout.parse_obj(raw_contents)
        contents.jsb_id = jsb.id
        return NatGridJobSafetyBriefingType(
            id=jsb.id,
            created_at=jsb.created_at,
            created_by_id=jsb.created_by_id,
            completed_at=jsb.completed_at,
            completed_by_id=jsb.completed_by_id,
            date=jsb.date_for,
            project_location_id=jsb.project_location_id,
            status=jsb.status,
            source=jsb.source,
            form_id=jsb.form_id,
            _contents=NatGridJobSafetyBriefingLayoutType.from_pydantic(contents),
            operating_hq=operating_hq,
            updated_at=jsb.updated_at,
            archived_at=jsb.archived_at,
        )


@strawberry.type(name="NatGridJobSafetyBriefingFormsList")
class NatGridJobSafetyBriefingFormsListType(FormInterfaceWithContents):
    id: uuid.UUID
    _contents: JSON
    source: Optional[SourceInformation]
    form_id: Optional[str]
    created_by_id: strawberry.Private[Optional[uuid.UUID]]
    created_at: datetime.datetime
    completed_by_id: strawberry.Private[Optional[uuid.UUID]]
    completed_at: Optional[datetime.datetime] = strawberry.field(default=None)
    date: datetime.date
    project_location_id: strawberry.Private[Optional[uuid.UUID]]
    name: str = strawberry.field(default=" NG Job Safety Briefing")
    status: FormStatus
    operating_hq: Optional[str] = None

    @strawberry.field
    async def contents(self) -> JSON:
        raw_contents = self._contents
        encoded_contents = jsonable_encoder(raw_contents)
        result = dict_keys_snake_to_camel(encoded_contents)
        return result

    @strawberry.field()
    async def work_package(self, info: Info) -> ProjectType | None:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )

        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on NatGrid Job Safety Briefing {self.id}"
            )
        if project_location.project is not None:
            return ProjectType.from_orm(project_location.project)
        else:
            return None

    @strawberry.field()
    async def location(self, info: Info) -> Optional[ProjectLocationType]:
        if not self.project_location_id:
            return None

        project_location = await info.context.project_locations.with_archived.load(
            self.project_location_id
        )
        if not project_location:
            raise ValueError(
                f"Invalid location {self.project_location_id} on NG Job Safety Briefing{self.id}"
            )
        else:
            return ProjectLocationType.from_orm(project_location)

    @strawberry.field()
    async def location_name(self, info: Info) -> Optional[str]:
        # work_location = (
        #     await info.context.natgrid_job_safety_briefings.with_work_location.load(
        #         self.id
        #     )
        # )
        work_locations_with_voltage_info = await info.context.natgrid_job_safety_briefings.with_multiple_work_locations.load(
            self.id
        )
        if work_locations_with_voltage_info:
            address = work_locations_with_voltage_info[0].get("address")
            if address is not None:
                return str(address)

        return None

    @strawberry.field()
    async def multiple_location(self, info: Info) -> Optional[bool]:
        work_location_with_voltage_info = await info.context.natgrid_job_safety_briefings.with_multiple_work_locations.load(
            self.id
        )
        if work_location_with_voltage_info:
            if len(work_location_with_voltage_info) > 1:
                return True
            else:
                return False
        else:
            return None

    @strawberry.field()
    async def created_by(self, info: Info) -> Optional[UserType]:
        if self.created_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.created_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def completed_by(self, info: Info) -> Optional[UserType]:
        if self.completed_by_id is None:
            return None
        else:
            user = await info.context.users.me.load(self.completed_by_id)
            assert user
            return UserType.from_orm(user)

    @strawberry.field()
    async def updated_by(self, info: Info) -> Optional[UserType]:
        audit_event_metadata = await info.context.audit.last_updates.load(self.id)
        return (
            UserType.from_orm(audit_event_metadata.user)
            if audit_event_metadata
            else None
        )

    @strawberry.field()
    async def supervisor(self, info: Info) -> Optional[list[JSBSupervisorType]]:
        return None

    @staticmethod
    def from_orm(
        natgrid_jsb: models.NatGridJobSafetyBriefing, operating_hq: Optional[str] = None
    ) -> "NatGridJobSafetyBriefingFormsListType":
        raw_contents = natgrid_jsb.contents or {}
        contents = raw_contents
        contents["jsb_id"] = str(natgrid_jsb.id)
        return NatGridJobSafetyBriefingFormsListType(
            id=natgrid_jsb.id,
            created_at=natgrid_jsb.created_at,
            created_by_id=natgrid_jsb.created_by_id,
            completed_at=natgrid_jsb.completed_at,
            completed_by_id=natgrid_jsb.completed_by_id,
            date=natgrid_jsb.date_for,
            project_location_id=natgrid_jsb.project_location_id,
            status=natgrid_jsb.status,
            source=natgrid_jsb.source,
            form_id=natgrid_jsb.form_id,
            _contents=contents,
            operating_hq=operating_hq,
            updated_at=natgrid_jsb.updated_at,
        )


@strawberry.input
class FormStatusInput:
    status: FormStatus


@strawberry.type(name="RestApiWrapper")
class RestApiWrapperType:
    endpoint: str
    method: str
    payload: Optional[str] = None
    response: Optional[JSON] = None


@strawberry.type(name="LocationReturnType")
class LocationReturnType:
    id: uuid.UUID
