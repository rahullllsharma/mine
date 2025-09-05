from typing import Any, Tuple

from fastapi import APIRouter, HTTPException, Request, Security
from fastapi.security import APIKeyHeader

router = APIRouter(prefix="/test")

api_key_header = APIKeyHeader(name="X-API-Key")

valid_api_key = "ClNtQ7KKOIKtwVe_3PC-stCT0wBQm9acuhw3xA_ZsCk^^GeorgiaPower"


def get_api_key(api_key: str = Security(api_key_header)) -> Tuple[str, str]:
    incoming_api_key, tenant_name = api_key.split("^^")
    # ideally we will fetch the valid api key from a DB and validate if it's valid or not,
    # as this is just for a POC we are hardcoding the valid_api_key
    if api_key != valid_api_key or not tenant_name:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key",
        )

    return (incoming_api_key, tenant_name)


@router.get("/get-jsb-data", tags=["test"])
async def get_jsb_data(
    request: Request, api_key: Tuple[str, str] = Security(get_api_key)
) -> Any:
    # write logic to fetch the required data
    return {"mock_jsb_id": {"data": "mock_jsb_data"}}
