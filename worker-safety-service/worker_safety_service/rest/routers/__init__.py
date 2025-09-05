from enum import Enum

from fastapi.routing import APIRouter

from worker_safety_service.rest.routers.activities import router as activities_router
from worker_safety_service.rest.routers.auth_token import router as auth_token_router
from worker_safety_service.rest.routers.configs import router as configs_router
from worker_safety_service.rest.routers.crew_leaders import (
    router as crew_leaders_router,
)
from worker_safety_service.rest.routers.feature_flag import (
    router as feature_flags_router,
)
from worker_safety_service.rest.routers.first_aid_aed_locations import (
    router as first_aid_and_aed_location_router,
)
from worker_safety_service.rest.routers.incidents import router as incidents_router
from worker_safety_service.rest.routers.insights import router as insights_router
from worker_safety_service.rest.routers.jsb_supervisors import (
    router as jsb_supervisors_router,
)
from worker_safety_service.rest.routers.locations import router as locations_router
from worker_safety_service.rest.routers.mock_powerbi_auth import (
    router as mock_powerbi_auth_router,
)
from worker_safety_service.rest.routers.tasks import router as tasks_router
from worker_safety_service.rest.routers.tiles import router as tiles_router
from worker_safety_service.rest.routers.ui_config import router as ui_config_router
from worker_safety_service.rest.routers.uploads import router as uploads_router
from worker_safety_service.rest.routers.work_packages import (
    router as work_packages_router,
)


class OpenapiSpecRouters(str, Enum):
    activities = "activities"
    configs = "configs"
    crew_leaders = "crew_leaders"
    locations = "locations"
    tasks = "tasks"
    tiles = "tiles"
    work_packages = "work_packages"
    insights = "insights"
    feature_flags = "feature_flags"
    incidents = "incidents"
    test = "test"
    auth_token = "auth_token"
    first_aid_aed_locations = "first_aid_aed_locations"
    ui_config = "ui_config"
    jsb_supervisors = "jsb_supervisors"
    uploads = "uploads"

    def get_router(self) -> APIRouter:
        match self.value:
            case self.activities:
                return activities_router
            case self.configs:
                return configs_router
            case self.incidents:
                return incidents_router
            case self.locations:
                return locations_router
            case self.tasks:
                return tasks_router
            case self.tiles:
                return tiles_router
            case self.work_packages:
                return work_packages_router
            case self.insights:
                return insights_router
            case self.feature_flags:
                return feature_flags_router
            case self.crew_leaders:
                return crew_leaders_router
            case self.test:
                return mock_powerbi_auth_router
            case self.auth_token:
                return auth_token_router
            case self.first_aid_aed_locations:
                return first_aid_and_aed_location_router
            case self.ui_config:
                return ui_config_router
            case self.jsb_supervisors:
                return jsb_supervisors_router
            case self.uploads:
                return uploads_router

        raise ValueError("router not found")
