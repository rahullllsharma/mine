from decimal import Decimal

from worker_safety_service.dal.medical_facilities import MedicalFacilitiesManager
from worker_safety_service.models import MedicalFacility


class MedicalFacilitiesLoader:
    def __init__(self, manager: MedicalFacilitiesManager):
        self.__manager = manager

    async def load_nearest_medical_facilities(
        self, latitude: Decimal, longitude: Decimal
    ) -> list[MedicalFacility]:
        items = await self.__manager.get_nearest_medical_facilities_by_location(
            latitude, longitude
        )
        return items
