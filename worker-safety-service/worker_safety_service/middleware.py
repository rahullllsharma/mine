import gzip
import io
import zlib
from typing import Iterable, Optional, Type

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

try:
    import brotli
except ImportError:  # pragma: no cover
    brotli = None

from worker_safety_service.urbint_logging import get_logger

logger = get_logger(__name__)

# For body small than 10kb use level 1, 10kb-20kb level 2, etc
COMPRESS_LEVEL_EVERY = 10000

ACCEPT_ENCODING_HEADER = "Accept-Encoding"
CONTENT_TYPE_HEADER = "Content-Type"


class CompressMiddleware:
    """Handles brotli, gzip, deflate responses for any request that includes
        "br", "gzip" or "deflate" in the Accept-Encoding header.

    The middleware will handle both standard and streaming responses.

    The following arguments are supported:
    - minimum_size - Do not compress responses if content is smaller.
        If no minimum_size is defined, all responses are compressed (default)
        Note that minimum_size always compress streaming responses
    - mimetypes - Content-Type header to match with this option.
        If no mimetypes defined, all types are compressed"""

    def __init__(
        self,
        app: ASGIApp,
        mimetypes: Optional[Iterable[str]] = None,
        minimum_size: Optional[int] = None,
    ) -> None:
        self.app = app
        self.minimum_size = minimum_size
        self.mimetypes = {i.lower().strip() for i in mimetypes} if mimetypes else None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = Headers(scope=scope)
            accept_encodings = {
                i.strip()
                for i in headers.get(ACCEPT_ENCODING_HEADER, "").lower().split(",")
            }
            for encoder in ENCODERS:
                if encoder.name in accept_encodings:
                    responder = CompressResponder(
                        self.app,
                        encoder(),
                        mimetypes=self.mimetypes,
                        minimum_size=self.minimum_size,
                    )
                    await responder(scope, receive, send)
                    return

        await self.app(scope, receive, send)


class Encoder:
    name: str

    def __call__(self, body: bytes, close: bool = False) -> bytes:  # pragma: no cover
        raise NotImplementedError()


class BrotliEncoder(Encoder):
    name = "br"
    max_quality = 3

    def __init__(self) -> None:
        self.compressor: Optional[brotli.Compressor] = None

    def __call__(self, body: bytes, close: bool = False) -> bytes:
        if self.compressor is None:
            if close:
                quality = min(self.max_quality, int(len(body) / COMPRESS_LEVEL_EVERY))
            else:
                quality = self.max_quality
            self.compressor = brotli.Compressor(mode=brotli.MODE_TEXT, quality=quality)

        if close:
            end_data: bytes = self.compressor.process(body) + self.compressor.finish()
            return end_data
        else:
            data: bytes = self.compressor.process(body)
            return data


class GzipEncoder(Encoder):
    name = "gzip"
    max_compresslevel = 4

    def __init__(self) -> None:
        self.buffer: Optional[io.BytesIO] = None
        self.file: Optional[gzip.GzipFile] = None

    def __call__(self, body: bytes, close: bool = False) -> bytes:
        if self.buffer is None:
            self.buffer = io.BytesIO()
            if close:
                compresslevel = min(
                    self.max_compresslevel, int(len(body) / COMPRESS_LEVEL_EVERY) + 1
                )
            else:
                compresslevel = self.max_compresslevel
            self.file = gzip.GzipFile(
                mode="wb", fileobj=self.buffer, compresslevel=compresslevel
            )
        else:
            self.buffer.seek(0)
            self.buffer.truncate()
            assert self.file

        self.file.write(body)
        if close:
            self.file.close()
        compressed = self.buffer.getvalue()
        if close:
            self.buffer.close()
        return compressed


class DeflateEncoder(Encoder):
    name = "deflate"
    max_level = 4

    def __init__(self) -> None:
        self.compressor: Optional[zlib._Compress] = None

    def __call__(self, body: bytes, close: bool = False) -> bytes:
        if self.compressor is None:
            if close:
                level = min(self.max_level, int(len(body) / COMPRESS_LEVEL_EVERY) + 1)
            else:
                level = self.max_level
            self.compressor = zlib.compressobj(level=level)

        if close:
            return self.compressor.compress(body) + self.compressor.flush()
        else:
            return self.compressor.compress(body)


class CompressResponder:
    def __init__(
        self,
        app: ASGIApp,
        encoder: Encoder,
        mimetypes: Optional[set[str]] = None,
        minimum_size: Optional[int] = None,
    ) -> None:
        self.app = app
        self.encoder = encoder
        self.mimetypes = mimetypes
        self.minimum_size = minimum_size
        self.send: Optional[Send] = None

        self.started = False
        self.initial_message: Message = {}
        self.headers: Optional[MutableHeaders] = None
        self.encode = False

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.send = send
        await self.app(scope, receive, self.send_and_compress)

    async def send_and_compress(self, message: Message) -> None:
        assert self.send

        message_type = message["type"]
        if message_type == "http.response.start":
            self.initial_message = message
            self.headers = MutableHeaders(raw=self.initial_message["headers"])
            self.encode = bool(
                not self.mimetypes
                or self.headers.get(CONTENT_TYPE_HEADER, "").lower() in self.mimetypes
            )
            return None

        elif message_type == "http.response.body":
            body = message.get("body", b"")
            message["original_bytes"] = len(body)

            more_body = message.get("more_body", False)
            if not self.started:
                if self.encode:
                    if (
                        not more_body
                        and self.minimum_size
                        and len(body) < self.minimum_size
                    ):
                        self.encode = False
                    else:
                        message["body"] = self.encoder(body, close=not more_body)
                        assert self.headers
                        self.headers["Content-Encoding"] = self.encoder.name
                        if not more_body:
                            self.headers["Content-Length"] = str(len(message["body"]))
                        else:
                            del self.headers["Content-Length"]

                self.started = True
                await self.send(self.initial_message)

            elif self.encode:
                message["body"] = self.encoder(body, close=not more_body)

        await self.send(message)


# Keep order
ENCODERS: list[Type[Encoder]] = []
if brotli is not None:
    ENCODERS.append(BrotliEncoder)
ENCODERS.append(GzipEncoder)
ENCODERS.append(DeflateEncoder)
