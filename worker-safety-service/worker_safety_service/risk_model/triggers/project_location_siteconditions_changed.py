import uuid
from dataclasses import dataclass

from worker_safety_service.risk_model.triggers.base import Trigger


@dataclass(frozen=True)
class ProjectLocationSiteConditionsChanged(Trigger):
    project_location_id: uuid.UUID
