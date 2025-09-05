import pytest

from worker_safety_service.dal.incident_severity_list_manager import (
    IncidentSeverityManager,
)
from worker_safety_service.models import AsyncSession, IncidentSeverityCreate
from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)


# Successfully creating an insight
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incident_severity(db_session: AsyncSession) -> None:
    incident_severity_manager = IncidentSeverityManager(db_session)

    incident_severities = await incident_severity_manager.get_all()
    assert len(incident_severities) == 0

    new_incident_severity = await incident_severity_manager.create_severity(
        IncidentSeverityCreate(
            ui_label="Low",
            api_value="low_severity",
            source="EEI/SCL",
            safety_climate_multiplier=0.007,
        )
    )
    assert new_incident_severity
    assert new_incident_severity.ui_label == "Low"

    incident_severities = await incident_severity_manager.get_all()
    assert len(incident_severities) == 1

    new_incident_severity = await incident_severity_manager.create_severity(
        IncidentSeverityCreate(
            ui_label="High",
            api_value="high_severity",
            source="EEI/SCL",
            safety_climate_multiplier=0.1,
        )
    )
    assert new_incident_severity
    assert new_incident_severity.ui_label == "High"

    incident_severities = await incident_severity_manager.get_all()
    assert len(incident_severities) == 2
