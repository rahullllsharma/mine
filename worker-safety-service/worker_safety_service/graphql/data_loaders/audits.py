import uuid
from typing import Optional

from strawberry.dataloader import DataLoader

from worker_safety_service.audit_events.dataclasses import (
    AuditEventTypeInput,
    ProjectDiff,
)
from worker_safety_service.dal.audit_events import AuditEventManager, AuditEventMetadata
from worker_safety_service.models.audit_events import AuditDiffType, AuditObjectType


class TenantAuditLoader:
    def __init__(self, manager: AuditEventManager, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id
        self.__manager = manager
        self.projects = DataLoader(load_fn=self.load_project_audit_logs)
        self.last_updates = DataLoader(load_fn=self.load_last_updates_by_object_ids)

    async def get_project_diffs(
        self, project_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, list[ProjectDiff]]:
        items = await self.__manager.get_project_diffs(
            project_ids=project_ids, tenant_id=self.tenant_id
        )
        return items

    async def load_last_updates_by_object_ids(
        self, object_ids: list[uuid.UUID]
    ) -> list[Optional[AuditEventMetadata]]:
        last_updates: dict[
            uuid.UUID, AuditEventMetadata
        ] = await self.__manager.get_last_updates(object_ids=object_ids)
        return [last_updates.get(i) or None for i in object_ids]

    async def load_project_audit_logs(
        self, project_ids: list[uuid.UUID]
    ) -> list[list[AuditEventTypeInput]]:
        diffs = await self.__manager.get_project_diffs(
            project_ids=project_ids, tenant_id=self.tenant_id
        )
        audits = {
            project_id: build_audit_trail(diffs) for project_id, diffs in diffs.items()
        }
        return [audits.get(i) or [] for i in project_ids]


SIMPLE_DIFFS = [
    AuditDiffType.created,
    AuditDiffType.archived,
    AuditDiffType.deleted,  # we don't really have .deleted types...
]

SUPPORTED_FOR_DIFF = {
    AuditObjectType.project: lambda field: field not in {"locations"},
    AuditObjectType.task: lambda field: field in {"start_date", "end_date", "status"},
    AuditObjectType.site_condition: lambda _field: False,
    AuditObjectType.daily_report: lambda field: field in {"status"},
}


def build_audit_trail(project_diffs: list[ProjectDiff]) -> list[AuditEventTypeInput]:
    diffs: list[AuditEventTypeInput] = []

    for diff in project_diffs:
        # created/archived diffs, and those without per-field handling
        if diff.diff.diff_type in SIMPLE_DIFFS or diff.diff.object_type in [
            AuditObjectType.site_condition
        ]:
            diffs += [AuditEventTypeInput(diff=diff)]
        elif diff.diff.diff_type == AuditDiffType.updated:
            # updated diffs need per-type handling
            field_names: set[str] = set()
            if diff.diff.new_values:
                field_names.update(diff.diff.new_values.keys())
            if diff.diff.old_values:
                field_names.update(diff.diff.old_values.keys())
            field_names = set(
                filter(SUPPORTED_FOR_DIFF[diff.diff.object_type], field_names)
            )
            diffs += [
                AuditEventTypeInput(diff=diff, field_name=field_name)
                for field_name in field_names
            ]
    return diffs
