import uuid
from dataclasses import dataclass

from worker_safety_service.risk_model.triggers.base import Trigger


@dataclass(frozen=True)
class ActivityChanged(Trigger):
    activity_id: uuid.UUID
