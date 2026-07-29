"""Forwarding requests to a backend and streaming the reply back.

The constraints below were established before any code was written; see CLAUDE.md ("Observed request
shape") for the captured request they came from.

- Relay the request body byte for byte. Do not parse and rebuild it. Beyond forward-compatibility,
  the requests carry prompt-cache markers that match on the exact bytes of the prefix, so even a
  harmless-looking reserialization breaks cache hits and costs money on every call.
- Peek at the body only far enough to find the model name, which is all routing needs.
- Forward the path *and* its query string: the real path is `/v1/messages?beta=true`.
- Credentials: forward for cloud, strip for local. Pass `anthropic-beta` through untouched; one of
  its entries is what makes the bearer token acceptable, so trimming the list breaks authentication.
- Drop hop-by-hop and connection-describing headers (host, content-length) and let the HTTP client
  set fresh ones.
- Ask the backend for an uncompressed reply. Claude Code asks for compression on the way in, so
  this has to be overridden deliberately rather than merely left unset.
- Answer the `HEAD /` probe Claude Code sends before its first real call (see `app.py`).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import httpx
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from .config import Backend, Config
from .routing import BackendName, backend_for_model

# Headers describing the connection we arrived on rather than the message. The HTTP client sets its
# own; letting these through makes requests fail in confusing ways.
CONNECTION_HEADERS = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    }
)

# The credential Claude Code sends. Forwarded untouched to Anthropic, removed on the way to
# LM Studio, which has no use for it and might write it to a log.
CREDENTIAL_HEADERS = frozenset({"authorization", "x-api-key"})

# `content-length` and `accept-encoding` are re-derived below: the first by the HTTP client, the
# second overridden to `identity` so the reply arrives as readable bytes.
DROPPED_FROM_REQUEST = CONNECTION_HEADERS | {
    "host",
    "content-length",
    "accept-encoding",
}

# The reply goes back out as a stream over our own connection, so its framing and the headers
# describing *this* server are ours to set, not the backend's. Relaying the backend's `date` leaves
# the client holding two of them, which the HTTP spec does not allow.
DROPPED_FROM_RESPONSE = CONNECTION_HEADERS | {"content-length", "date", "server"}

# A model can think for minutes, so the usual short read timeout would cut replies off. Connecting
# should still fail fast: LM Studio simply not running is the common failure.
TIMEOUT = httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)


def create_client() -> httpx.AsyncClient:
    """The single HTTP client shared by every request, so connections are reused."""
    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False)


@dataclass(frozen=True)
class Proxy:
    """Sends requests onward to a backend and streams the reply back untouched."""

    config: Config
    client: httpx.AsyncClient
    api_keys: dict[str, str]

    async def messages(self, request: Request) -> Response:
        """`POST /v1/messages` — the call that names a model, so routing is decided from the body."""
        body = await request.body()
        model = peek_model(body)
        if model is None:
            return error_response(
                400,
                "invalid_request_error",
                "The request body carries no 'model' field, so there is no way to tell which "
                "backend it belongs to.",
            )
        name, backend = backend_for_model(model, self.config.backends)
        return await self.relay(request, body, name, backend)

    async def anything_else(self, request: Request) -> Response:
        """Any path we did not anticipate.

        Forwarded rather than refused, so an unexpected endpoint is not fatal. Without a model name
        there is nothing to route on, and Claude Code believes it is talking to Anthropic, so that
        is where such a request goes.
        """
        body = await request.body()
        model = peek_model(body)
        if model is None:
            name: BackendName = "anthropic"
            backend = self.config.backends.anthropic
        else:
            name, backend = backend_for_model(model, self.config.backends)
        return await self.relay(request, body, name, backend)

    async def relay(
        self, request: Request, body: bytes, name: BackendName, backend: Backend
    ) -> Response:
        """Send `body` to `backend` unchanged and stream the reply back as it arrives."""
        outgoing = self.client.build_request(
            request.method,
            target_url(backend.base_url, request),
            headers=outgoing_headers(request, backend, self.api_keys.get(name)),
            content=body,
        )
        try:
            reply = await self.client.send(outgoing, stream=True)
        except httpx.HTTPError as exc:
            return error_response(
                502,
                "api_error",
                f"Could not reach the {name} backend at {backend.base_url}: "
                f"{type(exc).__name__}: {exc}",
            )

        relayed = StreamingResponse(
            reply.aiter_raw(),
            status_code=reply.status_code,
            background=BackgroundTask(reply.aclose),
        )
        # Assigned rather than passed as `headers=`, so repeated header names survive intact.
        relayed.raw_headers = response_headers(reply)
        return relayed


def peek_model(body: bytes) -> str | None:
    """Return the model named in the request body, or None if there is not one.

    The body is read here, never rewritten: the original bytes are what gets forwarded, so the
    prompt-cache prefix stays byte-identical whatever this function does with its copy.
    """
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    model = payload.get("model")
    return model if isinstance(model, str) and model else None


def target_url(base_url: str, request: Request) -> httpx.URL:
    """The same path and query at the backend's address. The captured path carries `?beta=true`."""
    url = base_url + request.url.path
    if request.url.query:
        url = f"{url}?{request.url.query}"
    return httpx.URL(url)


def outgoing_headers(
    request: Request, backend: Backend, api_key: str | None
) -> list[tuple[bytes, bytes]]:
    """The incoming headers, minus the ones that described the old connection.

    Everything else is passed through as it arrived — including `anthropic-beta`, whose
    `oauth-2025-04-20` entry is what makes the bearer token acceptable to Anthropic.
    """
    dropped = set(DROPPED_FROM_REQUEST)
    if api_key is not None or backend.credential == "strip":
        dropped |= CREDENTIAL_HEADERS

    headers = [
        (name, value)
        for name, value in request.headers.raw
        if name.decode("latin-1").lower() not in dropped
    ]
    # Deliberate override: Claude Code asks for gzip and friends, but a compressed reply cannot be
    # read for `usage` on its way past (Phase 2) without decompressing it first.
    headers.append((b"accept-encoding", b"identity"))
    if api_key is not None:
        headers.append((b"authorization", f"Bearer {api_key}".encode()))
    return headers


def response_headers(reply: httpx.Response) -> list[tuple[bytes, bytes]]:
    """The backend's reply headers, minus the ones about how it framed its own connection."""
    return [
        (name.encode("latin-1"), value.encode("latin-1"))
        for name, value in reply.headers.multi_items()
        if name.lower() not in DROPPED_FROM_RESPONSE
    ]


def error_response(status: int, error_type: str, message: str) -> JSONResponse:
    """An error in the shape Anthropic uses, so Claude Code shows it rather than something raw."""
    return JSONResponse(
        status_code=status,
        content={"type": "error", "error": {"type": error_type, "message": message}},
    )
