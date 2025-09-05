import json
from typing import Callable

import pytest
from faker import Faker
from httpx import AsyncClient

from tests.factories import TenantFactory
from worker_safety_service.models import AsyncSession
from worker_safety_service.rest.routers.ui_config import (
    UIConfigInputRequest,
    UIConfigInputRequestAttributes,
)

UI_CONFIG_ROUTE = "http://127.0.0.1:8000/rest/ui-config"
fake = Faker()


@pytest.mark.fresh_db
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_ui_config_data(
    rest_client: Callable[..., AsyncClient],
    db_session: AsyncSession,
) -> None:
    tenant = await TenantFactory.persist(db_session)
    client = rest_client(custom_tenant=tenant)
    form_type = "natgrid_job_safety_briefing"
    ui_config_data = {
        "clearance_types": [{"id": 1, "name": "My crews clearance"}],
        "status_workflow": [
            {
                "color_code": "#F8F8F8",
                "new_status": "in_progress",
                "action_button": "save_and_continue",
                "current_status": "in_progress",
            }
        ],
        "points_of_protection": [
            {"id": 1, "name": "NRA's", "description_allowed": True}
        ],
        "notification_settings": {
            "configurable": True,
            "notification_duration_days": "7",
        },
        "minimum_approach_distances": [
            {
                "id": "edebc83c-5302-4383-bad0-88c3578d5203",
                "location": "New England",
                "voltages": "NE 50 V – 300 V",
                "phase_to_phase": "Avoid Contact",
                "phase_to_ground": "Avoid Contact",
            }
        ],
        "general_reference_materials": [
            {
                "id": 1,
                "name": "Distribution Overhead Construction Standards (Main)",
                "link": "https://nationalgridplc.sharepoint.com/:b:/s/GRP-INT-US-ElectricStandardsSharePoint/Ee0WAr9nrjlKi2awNVkJxzsBd5iRnXee-gm-ccMiOc8EQg?e=Zn7Ouy",
                "category": "Distribution Overhead Construction Standards",
            }
        ],
        "minimum_approach_distances_links": [
            {
                "id": "c6a19f11-edfb-4859-8d41-1280ac62ff92",
                "url": "https://storage.googleapis.com/worker-safety-public-bucket/natgrid/pdf/jsb/NE%20MAD%20Tables%20-%20Employee%20Safety%20Handbook_final.pdf",
                "description": "New England MAD Table",
            }
        ],
        "energy_wheel_color": [{"id": 1, "name": "Biological", "color": "#5CC9E6"}],
        "energy_source_control": [
            {"id": 1, "name": "Grounds are applied", "description_allowed": True},
            {"id": 2, "name": "ARC Flash Assessment", "description_allowed": True},
            {
                "id": 3,
                "name": "Insulate / Isolate (hose / blankets)",
                "description_allowed": True,
            },
            {"id": 4, "name": "Potential Back Feed", "description_allowed": True},
        ],
        "documents_provided": [
            {"id": 1, "name": "Maps"},
            {"id": 2, "name": "ONE Line Diagram"},
            {"id": 3, "name": "Clearance + Control Form"},
            {"id": 4, "name": "Other"},
        ],
    }
    ui_config_request = UIConfigInputRequest.pack(
        attributes=UIConfigInputRequestAttributes(
            contents=ui_config_data, form_type=form_type
        )
    )
    response = await client.post(
        UI_CONFIG_ROUTE,
        json=json.loads(ui_config_request.json()),
    )
    assert response.status_code == 201
    config_response = response.json()["data"]["attributes"]
    assert config_response["form_type"] == form_type
