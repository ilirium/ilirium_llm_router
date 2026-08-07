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

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass

import httpx
from starlette.background import BackgroundTask
from starlette.requests import ClientDisconnect, Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from .config import Backend, Config
from .observe import (
    Call,
    Scanner,
    describe_exception,
    is_sse,
    scanner_for,
    transport_error_code,
)
from .routing import BackendName, backend_for_model
from .stats import StatsWriter

logger = logging.getLogger(__name__)

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
    stats: StatsWriter

    async def begin(self, request: Request) -> tuple[Call, bytes, Peeked]:
        """What both entry points do before routing: start the clocks, read the body, peek at it.

        `Call` is built first, so both clocks start when the request arrived rather than after the
        body has been read — a 118 KB body is not free.

        That size is also why the read can fail: every call re-sends the whole conversation, so
        there is a real window in which the caller can go away mid-upload. It is the same failure
        the relay already records, only earlier, and it gets the same `client_disconnect` row — with
        `backend` empty, because routing needs a body and there was never one to route on. The
        exception carries on to `app.py`, which answers it without a traceback; nothing can be
        delivered to a caller that has already gone.
        """
        call = Call(request)
        try:
            body = await request.body()
        except ClientDisconnect:
            call.failed(
                "client_disconnect",
                "client_disconnect",
                "The caller went away while its request body was still arriving.",
            )
            self.record(call)
            raise
        call.request_bytes = len(body)
        peeked = peek(body)
        call.model = peeked.model or ""
        call.stream = peeked.stream
        return call, body, peeked

    async def messages(self, request: Request) -> Response:
        """`POST /v1/messages` — the call that names a model, so routing is decided from the body."""
        call, body, peeked = await self.begin(request)

        if peeked.model is None:
            # Refused before any backend was chosen, so `backend` stays empty. It still gets a row:
            # a call the router turned away is a call, and a silent gap is worse than blanks.
            call.failed("http_error", "400", "The request body carries no 'model' field.")
            self.record(call)
            return error_response(
                400,
                "invalid_request_error",
                "The request body carries no 'model' field, so there is no way to tell which "
                "backend it belongs to.",
            )
        name, backend = backend_for_model(peeked.model, self.config.backends)
        return await self.relay(request, call, body, name, backend)

    async def anything_else(self, request: Request) -> Response:
        """Any path we did not anticipate.

        Forwarded rather than refused, so an unexpected endpoint is not fatal. Without a model name
        there is nothing to route on, and Claude Code believes it is talking to Anthropic, so that
        is where such a request goes.
        """
        call, body, peeked = await self.begin(request)

        if peeked.model is None:
            name: BackendName = "anthropic"
            backend = self.config.backends.anthropic
        else:
            name, backend = backend_for_model(peeked.model, self.config.backends)
        return await self.relay(request, call, body, name, backend)

    async def relay(
        self,
        request: Request,
        call: Call,
        body: bytes,
        name: BackendName,
        backend: Backend,
    ) -> Response:
        """Send `body` to `backend` unchanged and stream the reply back as it arrives."""
        call.backend = name
        outgoing = self.client.build_request(
            request.method,
            target_url(backend.base_url, request),
            headers=outgoing_headers(request, backend, self.api_keys.get(name)),
            content=body,
        )
        try:
            reply = await self.client.send(outgoing, stream=True)
        except httpx.HTTPError as exc:
            # No HTTP status ever existed here, so a symbolic code stands in for one. LM Studio not
            # running is the common failure, and it lands as `connect_error`.
            call.failed("transport_error", transport_error_code(exc), describe_exception(exc))
            self.record(call)
            return error_response(
                502,
                "api_error",
                f"Could not reach the {name} backend at {backend.base_url}: "
                f"{describe_exception(exc)}",
            )

        if reply.status_code >= 400:
            # The status is known now; the backend's own wording, if it sends any, is picked up off
            # the tee and filled in when the row is written.
            call.failed("http_error", str(reply.status_code), "")

        relayed = StreamingResponse(
            self.watch(reply, call),
            status_code=reply.status_code,
            # Kept alongside the close in `watch`'s `finally`, which covers the disconnect case this
            # task is skipped for. This one covers the opposite gap: a generator that never runs at
            # all, and so never reaches its own `finally`.
            background=BackgroundTask(reply.aclose),
        )
        # Assigned rather than passed as `headers=`, so repeated header names survive intact.
        relayed.raw_headers = response_headers(reply)
        return relayed

    async def watch(self, reply: httpx.Response, call: Call) -> AsyncIterator[bytes]:
        """Relay the reply's bytes untouched while reading a copy of each one.

        The chunk is yielded exactly as it arrived; the scanner only ever sees a reference to the
        same bytes. Nothing in here can change what the caller receives, and every failure is
        recorded rather than raised — except the client going away, which has to propagate.

        The one thing this generator does add to the stream is an error event when the relay breaks
        under it, which is a deliberate exception to byte-relay and is written up as such in
        `CLAUDE.md`. Nothing is ever *altered*: the injected event only ever follows bytes that have
        already gone out untouched.
        """
        streamed = is_sse(reply.headers.get("content-type", ""))
        scanner = scanner_for(reply.headers.get("content-type", ""))
        try:
            async for chunk in reply.aiter_raw():
                call.saw_bytes(len(chunk))
                scanner.feed(chunk)
                yield chunk
        except (asyncio.CancelledError, GeneratorExit):
            # Neither a success nor a backend failure — the reply was fine and nobody was left to
            # read it. This is the case the old `is_error` boolean could not express.
            call.failed(
                "client_disconnect",
                "client_disconnect",
                "The caller went away before the reply finished.",
            )
            raise
        except httpx.HTTPError as exc:
            # The status line already went out as 200, so the failure cannot be put in a status
            # code. It can still be *said*, if the reply is a stream of events: one more event ends
            # the truncation as an error instead of as a silence.
            call.failed("transport_error", transport_error_code(exc), describe_exception(exc))
            if streamed:
                yield sse_error_event(
                    f"The {call.backend or 'upstream'} backend's reply broke off mid-stream: "
                    f"{describe_exception(exc)}"
                )
        finally:
            scanner.finish()
            self.record(call, scanner)
            # Closing here rather than only in the `BackgroundTask` below: starlette skips that
            # task when the caller disconnects on ASGI spec 2.4, which is exactly the case that
            # leaves an upstream connection with nobody to end it. `aclose` is guarded by httpx's
            # own `is_closed`, so the two paths cannot double-close.
            await close_quietly(reply)

    def record(self, call: Call, scanner: Scanner | None = None) -> None:
        """Write the row and the log line. Never raises: telemetry does not get to break a call."""
        try:
            row = call.record(scanner.observation if scanner else None)
            self.stats.write(row)
            # The log line is read from the finished row rather than measured again, so the two
            # traces of one call can never disagree about how long it took.
            outcome = (
                "ok" if row.error_status == "ok" else f"{row.error_status} {row.error_code}".strip()
            )
            logger.info(
                "%s  %s → %s  %s  %d ms, %d bytes",
                row.path,
                row.model or "(no model)",
                row.backend or "(unrouted)",
                outcome,
                row.duration_ms,
                row.response_bytes,
            )
        except Exception as exc:  # noqa: BLE001 — telemetry must never break a call
            logger.warning("Could not record a call: %s: %s", type(exc).__name__, exc)


@dataclass(frozen=True)
class Peeked:
    """The two body fields the router looks at. Both `None` when the body is not usable JSON."""

    model: str | None
    stream: bool | None


def peek(body: bytes) -> Peeked:
    """Return the model and stream flag named in the request body.

    The body is read here, never rewritten: the original bytes are what gets forwarded, so the
    prompt-cache prefix stays byte-identical whatever this function does with its copy.

    `stream` comes out of the same parse as `model`, which is why it costs nothing to record. It is
    not what picks the scanner — the response content-type does that — so the column's real use is
    diagnosing the recorder rather than the call: empty token columns with `stream` true means the
    SSE path came up empty, empty with `stream` false means the buffered one did.

    That diagnosis only works if `false` is written as `false`. **An absent `stream` is a
    non-streaming request**, since the API defaults it to false and Claude Code omits the field
    rather than sending it — measured on 2026-07-31, where every non-streaming row in
    `docs/phase-2-step-6-session/calls.csv` has the column blank. Reading absence as unknown left 83
    of 142 rows saying nothing, and left an empty cell meaning two different things.

    So an empty cell now means only what it should: the body never parsed, or it said something
    about `stream` that was not a boolean.
    """
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return Peeked(None, None)
    if not isinstance(payload, dict):
        return Peeked(None, None)

    model = payload.get("model")
    stream = payload.get("stream")
    if stream is None:
        streaming: bool | None = False
    elif isinstance(stream, bool):
        streaming = stream
    else:
        # Present but not a boolean. The backend will make its own judgement; this column declines
        # to guess, which is what the empty cell is for.
        streaming = None

    return Peeked(
        model=model if isinstance(model, str) and model else None,
        stream=streaming,
    )


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

    The credential is decided by `backend.credential` alone, never by whether a key happens to
    exist. `api_key` carries the value for `inject` and is ignored by the other two modes.
    """
    dropped = set(DROPPED_FROM_REQUEST)
    if backend.credential in {"strip", "inject"}:
        dropped |= CREDENTIAL_HEADERS

    headers = [
        (name, value)
        for name, value in request.headers.raw
        if name.decode("latin-1").lower() not in dropped
    ]
    # Deliberate override: Claude Code asks for gzip and friends, but a compressed reply cannot be
    # read for `usage` on its way past (Phase 2) without decompressing it first.
    headers.append((b"accept-encoding", b"identity"))
    if backend.credential == "inject" and api_key is not None:
        headers.append((b"authorization", f"Bearer {api_key}".encode()))
    return headers


def response_headers(reply: httpx.Response) -> list[tuple[bytes, bytes]]:
    """The backend's reply headers, minus the ones about how it framed its own connection."""
    return [
        (name.encode("latin-1"), value.encode("latin-1"))
        for name, value in reply.headers.multi_items()
        if name.lower() not in DROPPED_FROM_RESPONSE
    ]


def sse_error_event(message: str) -> bytes:
    """Anthropic's `error` event, for a stream that broke after its 200 had gone out.

    The one place the router writes bytes of its own into a relayed reply. Without it a backend
    dying mid-answer is indistinguishable from a model that simply stopped talking: the caller sees
    a stream that ends, with no event saying why. The shape is the one Anthropic sends, so a client
    that already handles a mid-stream error handles this one too.

    Deliberately *not* counted in `response_bytes` and not fed to the scanner. Both measure what the
    backend sent, and these bytes are ours — a row whose byte count included the router's own
    apology would be lying about the reply it is describing.
    """
    payload = json.dumps({"type": "error", "error": {"type": "api_error", "message": message}})
    return f"event: error\ndata: {payload}\n\n".encode()


async def close_quietly(reply: httpx.Response) -> None:
    """Release the upstream connection, whatever happened to the reply.

    Failing to close is not worth raising over — the caller is already being dealt with, and httpx
    reclaims the connection eventually — but it is worth a line, since a connection that is never
    released is the shape of a leak that only appears under load.
    """
    try:
        await reply.aclose()
    except Exception as exc:  # noqa: BLE001 — a close that fails must not break the response
        logger.debug("Could not close the upstream reply: %s: %s", type(exc).__name__, exc)


def error_response(status: int, error_type: str, message: str) -> JSONResponse:
    """An error in the shape Anthropic uses, so Claude Code shows it rather than something raw."""
    return JSONResponse(
        status_code=status,
        content={"type": "error", "error": {"type": error_type, "message": message}},
    )
