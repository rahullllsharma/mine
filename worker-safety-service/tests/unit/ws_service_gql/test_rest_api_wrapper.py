import asyncio
import json
from types import SimpleNamespace
from typing import Any, AsyncGenerator, cast

import pytest
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from worker_safety_service.context import Info
from worker_safety_service.graphql.queries.resolvers import rest_api_wrapper


class MockInfo:
    def __init__(self, token: str):
        self.context = SimpleNamespace(token=token)


dummy_app = FastAPI()


@dummy_app.post("/api/success")
async def success_endpoint(request: Request) -> JSONResponse:
    # Check authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != "Bearer test_token":
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    try:
        body = await request.json()
    except Exception:
        body = {}

    return JSONResponse(content={"data": "success", "received": body}, status_code=200)


@dummy_app.get("/api/data")
async def get_data_endpoint(request: Request) -> JSONResponse:
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != "Bearer test_token":
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    return JSONResponse(content={"result": "data"}, status_code=200)


@dummy_app.post("/api/server-error")
async def server_error_endpoint(request: Request) -> JSONResponse:
    return JSONResponse(content={"message": "Internal Server Error"}, status_code=500)


@dummy_app.post("/api/client-error")
async def client_error_endpoint(request: Request) -> JSONResponse:
    return JSONResponse(content={"message": "Bad Request"}, status_code=400)


@dummy_app.post("/api/text-response")
async def text_response_endpoint(request: Request) -> PlainTextResponse:
    return PlainTextResponse(content="This is a plain text response", status_code=200)


# Test server fixture
@pytest.fixture
async def dummy_server() -> AsyncGenerator[str, None]:
    config = uvicorn.Config(
        app=dummy_app, host="127.0.0.1", port=8000, log_level="error"
    )
    server = uvicorn.Server(config)

    server_task = asyncio.create_task(server.serve())
    await asyncio.sleep(0.1)

    yield "http://127.0.0.1:8000"

    server.should_exit = True
    await server_task


@pytest.mark.asyncio
async def test_rest_api_wrapper_successful_post(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/success"
    method = "POST"
    payload = json.dumps({"key": "value"})
    info = cast(Info, MockInfo(token="test_token"))

    result = await rest_api_wrapper(info, endpoint, method, payload)
    response: Any = result.response

    assert result.endpoint == endpoint
    assert result.method == method
    assert response["data"] == "success"
    assert response["received"]["key"] == "value"


@pytest.mark.asyncio
async def test_rest_api_wrapper_get_request(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/data"
    method = "GET"
    info = cast(Info, MockInfo(token="test_token"))

    result = await rest_api_wrapper(info, endpoint, method)
    response: Any = result.response

    assert result.endpoint == endpoint
    assert result.method == method
    assert response["result"] == "data"


@pytest.mark.asyncio
async def test_rest_api_wrapper_invalid_method(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/success"
    method = "INVALID"
    info = cast(Info, MockInfo(token="test_token"))

    # result = await rest_api_wrapper(info, endpoint, method)

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method)

    assert "Invalid method: INVALID." in str(excinfo.value)


@pytest.mark.asyncio
async def test_rest_api_wrapper_invalid_json_payload(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/success"
    method = "POST"
    payload = "{invalid json}"
    info = cast(Info, MockInfo(token="test_token"))

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method, payload)

    assert "Invalid JSON payload" in str(excinfo.value)


@pytest.mark.asyncio
async def test_rest_api_wrapper_server_error(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/server-error"
    method = "POST"
    info = cast(Info, MockInfo(token="test_token"))

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method)

    assert "HTTP error: 500" in str(excinfo.value)


@pytest.mark.asyncio
async def test_rest_api_wrapper_client_error(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/client-error"
    method = "POST"
    info = cast(Info, MockInfo(token="test_token"))

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method)

    assert "HTTP error: 400" in str(excinfo.value)


@pytest.mark.asyncio
async def test_rest_api_wrapper_text_response(dummy_server: str) -> None:
    endpoint = f"{dummy_server}/api/text-response"
    method = "POST"
    info = cast(Info, MockInfo(token="test_token"))

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method)

    assert "Unexpected error:" in str(excinfo.value)


@pytest.mark.asyncio
async def test_rest_api_wrapper_connection_error() -> None:
    endpoint = "http://non-existent-server:12345/api"
    method = "POST"
    info = cast(Info, MockInfo(token="test_token"))

    with pytest.raises(ValueError) as excinfo:
        await rest_api_wrapper(info, endpoint, method)

    assert "Request error:" in str(excinfo.value)
