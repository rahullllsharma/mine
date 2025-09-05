import datetime
import uuid
from dataclasses import dataclass

from worker_safety_service.risk_model.triggers.base import Trigger


@dataclass(frozen=True)
class UpdateTaskRisk(Trigger):
    project_task_id: uuid.UUID
    date: datetime.date
