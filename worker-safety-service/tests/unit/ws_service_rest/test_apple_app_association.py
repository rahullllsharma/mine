import pytest
from fastapi import status
from httpx import AsyncClient

from worker_safety_service.rest.main import app

client = AsyncClient(app=app, base_url="http://test")

expected_response = '{\n    "applinks": {\n        "apps": [],\n        "details": [\n             {\n               "appIDs": [ "V2X3GY37LK.com.urbint.workersafety-dev", "V2X3GY37LK.com.urbint.workersafety-int" ,"V2X3GY37LK.com.urbint.workersafety"],\n               "components": [\n\n                 {\n                    "/": "/?login"\n                 }\n\n               ]\n             }\n         ]\n    }\n}\n'


@pytest.mark.asyncio
async def test_apple_app_association() -> None:
    response = await client.get("/.well-known/apple-app-site-association")
    assert response.status_code == status.HTTP_200_OK
    assert response.text == expected_response
