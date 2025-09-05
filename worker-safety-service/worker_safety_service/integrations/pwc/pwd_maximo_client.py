import json
from dataclasses import dataclass
from typing import TypeVar
from urllib.parse import urljoin
from uuid import UUID

from httpx import AsyncClient

from worker_safety_service.models import RiskLevel
from worker_safety_service.site_conditions.world_data import HTTPClient
from worker_safety_service.urbint_logging.fastapi_utils import Stats


@dataclass(frozen=True)
class EntityRiskSummary:
    entity_id: UUID
    external_key: str
    risk_level: RiskLevel


@dataclass(frozen=True)
class LocationRiskSummary(EntityRiskSummary):
    work_package_id: UUID


ERS = TypeVar("ERS", bound=EntityRiskSummary)


class PwCMaximoClient:
    _entity_type_attribute_mappings = {
        EntityRiskSummary: "workOrderId",
        LocationRiskSummary: "multiId",
    }

    # TODO: Probably reorganize the arguments so that the client secret come in the end
    def __init__(
        self,
        http_client: AsyncClient,
        client_id: str,
        client_secret: str,
        target_endpoint: str,
        ws_base_url: str,
        max_batch_size: int = 20,
    ) -> None:
        self._http_client = http_client
        self._target_endpoint = urljoin(
            target_endpoint, "workorders/updateRiskSummaries"
        )
        self._ws_base_url = ws_base_url

        self._headers = {
            "Content-Type": "application/json",
            "Source-System": "Urbint",
            "Target-System": "Maximo",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        self.max_batch_size = max_batch_size

    async def _execute_update_request(self, summaries: list[ERS]) -> None:
        def convert_to_payload(summary: ERS) -> dict:
            # TODO: Check if we can check it on the typing, move this to the class constructor
            if summary.risk_level not in [
                RiskLevel.LOW,
                RiskLevel.MEDIUM,
                RiskLevel.HIGH,
                RiskLevel.UNKNOWN,
            ]:
                raise RuntimeError(f"Illegal Risk Level supplied: {summary.risk_level}")

            if summary.__class__ == LocationRiskSummary:
                _summary: LocationRiskSummary = summary  # type: ignore
                link_url = f"{self._ws_base_url}/projects/{_summary.work_package_id}?location={summary.entity_id}"
            else:
                # It's a work package then!!
                link_url = f"{self._ws_base_url}/projects/{summary.entity_id}"

            return {
                self._entity_type_attribute_mappings[
                    summary.__class__
                ]: summary.external_key,
                "ueRiskScore": summary.risk_level.upper(),
                "ueRiskSourceSys": "URBINT",
                "ueRiskSourceId": str(summary.entity_id),
                "ueRiskSourceURL": link_url,
            }

        batches = []
        for start_pos in range(0, len(summaries), self.max_batch_size):
            summaries = summaries[start_pos : start_pos + self.max_batch_size]
            batch = list(map(convert_to_payload, summaries))
            batches.append(batch)

        for batch in batches:
            await self._post(batch)

    async def post_work_package_updates(
        self, work_package_summaries: list[EntityRiskSummary]
    ) -> None:
        await self._execute_update_request(work_package_summaries)

    async def post_location_updates(
        self, location_summaries: list[LocationRiskSummary]
    ) -> None:
        await self._execute_update_request(location_summaries)

    async def _post(self, content: list[dict] | dict) -> None:
        # TODO: Do we need a "X-Correlation-ID"
        with Stats("pwc-maximo-client"):
            json_content = json.dumps(content)
            response = await HTTPClient.post(
                self._target_endpoint, content=json_content, headers=self._headers
            )
            response.raise_for_status()
            # TODO: Handle Errors, continue, not continue etc.
