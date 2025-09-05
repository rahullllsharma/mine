from dataclasses import dataclass
from typing import Any
from uuid import UUID

from worker_safety_service.models import AuditEventDiff, User


@dataclass
class AuditDiff:
    user: User | None
    diff: AuditEventDiff


@dataclass
class ProjectDiff(AuditDiff):
    project_id: UUID


@dataclass
class DiffValue:
    id: UUID | None = None
    model: Any | None = None
    type: str | None = None


@dataclass
class DiffValueLiteral(DiffValue):
    old_value: str | None = None
    new_value: str | None = None
    type: str = "String"


@dataclass
class DiffValueScalar(DiffValue):
    old_values: list[str] | None = None
    new_values: list[str] | None = None
    added: list[str] | None = None
    removed: list[str] | None = None
    type: str = "List"


@dataclass
class AuditEventTypeInput:
    diff: ProjectDiff
    diff_values: Any | None = None
    field_name: str | None = None
