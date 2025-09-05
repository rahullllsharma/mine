from typing import Optional

from worker_safety_service.dal.first_aid_aed_locations import (
    FirstAIDAEDLocationsManager,
)
from worker_safety_service.models import FirstAidAedLocations, LocationType
from worker_safety_service.types import OrderBy


class FirstAIDAEDLocationsLoader:
    def __init__(self, manager: FirstAIDAEDLocationsManager):
        self.__manager = manager

    async def load_first_aid_aed_locations(
        self,
        location_type: Optional[LocationType] = None,
        order_by: list[OrderBy] | None = None,
    ) -> list[FirstAidAedLocations]:
        loaded_first_aid_aed_locations = (
            await self.__manager.get_first_aid_aed_location_from_location_type(
                location_type=location_type,
                order_by=order_by,
            )
        )
        return loaded_first_aid_aed_locations
