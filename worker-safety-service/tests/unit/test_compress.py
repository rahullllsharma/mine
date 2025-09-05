import gzip
import io
import json
import zlib
from typing import AsyncGenerator

import brotli
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.testclient import TestClient

from worker_safety_service.middleware import CompressMiddleware

app = FastAPI()
app.add_middleware(CompressMiddleware, mimetypes={"application/json"}, minimum_size=100)
client = TestClient(app)

DUMMY_BIG_RESPONSE_LENGTH = 100000
DUMMY_RESPONSE = {f"msg{i}": "Hello World" for i in range(100)}
DUMMY_SMALL_RESPONSE = {"msg": "Hello World"}
DUMMY_HTML_RESPONSE = "<html></html>"


@app.get("/")
async def dummy_view() -> dict:
    return DUMMY_RESPONSE


@app.get("/big")
async def dummy_big_view() -> list:
    return ["some text just to duplicate"] * DUMMY_BIG_RESPONSE_LENGTH


@app.get("/small")
async def dummy_small_view() -> dict:
    return DUMMY_SMALL_RESPONSE


@app.get("/stream")
async def dummy_streaming_view() -> StreamingResponse:
    bytes_fp = io.BytesIO(json.dumps(DUMMY_RESPONSE).encode())
    bytes_fp.seek(0)

    async def body_stream() -> AsyncGenerator[bytes, None]:
        while True:
            content = bytes_fp.read(10)
            if content:
                yield content
            else:
                bytes_fp.close()
                break

    return StreamingResponse(body_stream(), media_type="application/json")


@app.get("/html")
async def dummy_html_view() -> HTMLResponse:
    return HTMLResponse(DUMMY_HTML_RESPONSE)


def test_compress_types() -> None:
    with client.stream("GET", "/", headers={"Accept-Encoding": "br"}) as response:
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Encoding"] == "br"
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(brotli.decompress(byte_array))
        assert data == DUMMY_RESPONSE

    with client.stream("GET", "/", headers={"Accept-Encoding": "gzip"}) as response:
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Encoding"] == "gzip"
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(gzip.decompress(byte_array))
        assert data == DUMMY_RESPONSE

    with client.stream("GET", "/", headers={"Accept-Encoding": "deflate"}) as response:
        assert response.headers["Content-Encoding"] == "deflate"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(zlib.decompress(byte_array))
        assert data == DUMMY_RESPONSE


def test_streaming_compress_types() -> None:
    with client.stream("GET", "/stream", headers={"Accept-Encoding": "br"}) as response:
        assert "Content-Length" not in response.headers
        assert response.headers["Content-Encoding"] == "br"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        data = json.loads(brotli.decompress(byte_array))
        assert data == DUMMY_RESPONSE

    with client.stream(
        "GET", "/stream", headers={"Accept-Encoding": "gzip"}
    ) as response:
        assert "Content-Length" not in response.headers
        assert response.headers["Content-Encoding"] == "gzip"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        data = json.loads(gzip.decompress(byte_array))
        assert data == DUMMY_RESPONSE

    with client.stream(
        "GET", "/stream", headers={"Accept-Encoding": "deflate"}
    ) as response:
        assert "Content-Length" not in response.headers
        assert response.headers["Content-Encoding"] == "deflate"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        data = json.loads(zlib.decompress(byte_array))
        assert data == DUMMY_RESPONSE


def test_big_compress_types() -> None:
    with client.stream("GET", "/big", headers={"Accept-Encoding": "br"}) as response:
        assert response.headers["Content-Encoding"] == "br"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(brotli.decompress(byte_array))
        assert len(data) == DUMMY_BIG_RESPONSE_LENGTH

    with client.stream("GET", "/big", headers={"Accept-Encoding": "gzip"}) as response:
        assert response.headers["Content-Encoding"] == "gzip"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(gzip.decompress(byte_array))
        assert len(data) == DUMMY_BIG_RESPONSE_LENGTH

    with client.stream(
        "GET", "/big", headers={"Accept-Encoding": "deflate"}
    ) as response:
        assert response.headers["Content-Encoding"] == "deflate"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(zlib.decompress(byte_array))
        assert len(data) == DUMMY_BIG_RESPONSE_LENGTH


def test_no_compress() -> None:
    with client.stream("GET", "/html", headers={"Accept-Encoding": "br"}) as response:
        assert not response.headers.get("Content-Encoding")
        binary = response.read()
        assert response.headers["Content-Length"] == str(len(binary))
        assert binary.decode() == DUMMY_HTML_RESPONSE


def test_no_compress_too_small_body() -> None:
    with client.stream("GET", "/small", headers={"Accept-Encoding": "br"}) as response:
        assert not response.headers.get("Content-Encoding")
        binary = response.read()
        assert response.headers["Content-Length"] == str(len(binary))
        assert json.loads(binary) == DUMMY_SMALL_RESPONSE


def test_compress_brotli_should_go_first() -> None:
    with client.stream(
        "GET", "/", headers={"Accept-Encoding": "deflate, br"}
    ) as response:
        assert response.headers["Content-Encoding"] == "br"
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))


def test_invalid_compress() -> None:
    with client.stream("GET", "/", headers={"Accept-Encoding": "xpto"}) as response:
        assert not response.headers.get("Content-Encoding")
        raw_list = list(response.iter_raw())
        byte_array = raw_list[0]
        assert response.headers["Content-Length"] == str(len(byte_array))
        data = json.loads(byte_array)
        assert data == DUMMY_RESPONSE


def test_missing_brotli() -> None:
    from worker_safety_service.middleware import ENCODERS, BrotliEncoder

    idx = ENCODERS.index(BrotliEncoder)
    ENCODERS.remove(BrotliEncoder)

    try:
        with client.stream("GET", "/", headers={"Accept-Encoding": "br"}) as response:
            assert not response.headers.get("Content-Encoding")
            raw_list = list(response.iter_raw())
            byte_array = raw_list[0]
            assert response.headers["Content-Length"] == str(len(byte_array))

        with client.stream(
            "GET", "/", headers={"Accept-Encoding": "br, gzip"}
        ) as response:
            assert response.headers["Content-Encoding"] == "gzip"
            raw_list = list(response.iter_raw())
            byte_array = raw_list[0]
            assert response.headers["Content-Length"] == str(len(byte_array))
    finally:
        ENCODERS.insert(idx, BrotliEncoder)
