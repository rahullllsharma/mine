from worker_safety_service.dal.crua_manager import CRUAManager
from worker_safety_service.models import (
    AsyncSession,
    IncidentSeverity,
    IncidentSeverityCreate,
)
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


class IncidentSeverityManager(CRUAManager[IncidentSeverity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, entity_type=IncidentSeverity)

    async def create_severity(self, input: IncidentSeverityCreate) -> IncidentSeverity:
        # create the new incident severity
        severity_instance = IncidentSeverity(**input.dict())
        await self.create(severity_instance)

        return severity_instance
