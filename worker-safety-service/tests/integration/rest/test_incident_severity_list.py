import json
from logging import getLogger
from typing import Callable

import pytest
from httpx import AsyncClient

from tests.factories import TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.incident_severity_list import (
    IncidentSeverityAttributes,
    IncidentSeverityRequest,
)

logger = getLogger(__name__)
INCIDENT_SEVERITY_LIST_ROUTE = "http://127.0.0.1:8000/rest/incident_severity"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_incident_severity_list_201_ok(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    incident_severity_request = IncidentSeverityRequest.pack(
        attributes=IncidentSeverityAttributes(
            ui_label="Low",
            api_value="low_severity",
            source="EEI/SCL",
            safety_climate_multiplier=0.007,
        )
    )
    response = await client.post(
        INCIDENT_SEVERITY_LIST_ROUTE, json=json.loads(incident_severity_request.json())
    )
    assert response.status_code == 201
    incident_severity_response = response.json()["data"]["attributes"]

    assert incident_severity_response["ui_label"] == "Low"
