from decimal import Decimal

from worker_safety_service.models import AsyncSession, MedicalFacility
from worker_safety_service.site_conditions.world_data import (
    HospitalsResponse,
    Sources,
    WorldDataClient,
)


class MedicalFacilitiesManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_nearest_medical_facilities_by_location(
        self, lat: Decimal, lon: Decimal
    ) -> list[MedicalFacility]:
        hospitals = await WorldDataClient.request_resource(
            lat, lon, Sources.hospital, HospitalsResponse
        )

        results = [
            MedicalFacility(
                description=hospital["name"],
                distance_from_job=hospital["distance"],
                phone_number=hospital["telephone"],
                address=hospital["address"],
                city=hospital["city"],
                state=hospital["state"],
                zip=hospital["zip"],
            )
            for hospital in hospitals["hospitals"]
        ]

        return results
