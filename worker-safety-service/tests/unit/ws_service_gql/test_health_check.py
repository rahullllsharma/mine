import pytest
from fastapi import status
from httpx import AsyncClient

from worker_safety_service.graphql.main import app

client = AsyncClient(app=app, base_url="http://test")


@pytest.mark.asyncio
async def test_livez_200_OK() -> None:
    response = await client.get("/livez")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_readyz_200_OK() -> None:
    response = await client.get("/readyz")
    assert response.status_code == status.HTTP_200_OK
