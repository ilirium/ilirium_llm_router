"""Forwarding requests to a backend and streaming the reply back.

The constraints below were established before any code was written; see
`docs/reference/architecture.md` ("Observed request shape") for the captured request they came
from.

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
import zlib
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import httpx
from starlette.background import BackgroundTask
from starlette.requests import ClientDisconnect, Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from .config import Backend, Config
from .corpus import CorpusWriter
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

# What a failed reply is allowed to tell the log about why it failed. An EXPLICIT LIST OF NAMES, and
# never a copy of the reply's headers: `docs/reference/corpus.md` promises that no credential
# reaches disk, and the only thing keeping that true when a response one day carries one is that
# nothing unnamed is ever written. `authorization`, `x-api-key` and `set-cookie` are what this list
# exists to exclude.
#
# Note this is NOT the inverse of DROPPED_FROM_RESPONSE above. That one governs what the *client*
# receives; this one governs what is *written down*. A header can be in both, in neither, or in one.
RECORDED_RESPONSE_HEADERS = frozenset(
    {
        # How long until the call may be retried.
        "retry-after",
        # The four buckets Anthropic meters, each as limit / remaining / reset.
        "anthropic-ratelimit-requests-limit",
        "anthropic-ratelimit-requests-remaining",
        "anthropic-ratelimit-requests-reset",
        "anthropic-ratelimit-tokens-limit",
        "anthropic-ratelimit-tokens-remaining",
        "anthropic-ratelimit-tokens-reset",
        "anthropic-ratelimit-input-tokens-limit",
        "anthropic-ratelimit-input-tokens-remaining",
        "anthropic-ratelimit-input-tokens-reset",
        "anthropic-ratelimit-output-tokens-limit",
        "anthropic-ratelimit-output-tokens-remaining",
        "anthropic-ratelimit-output-tokens-reset",
        # The id that ties a rejection to Anthropic's own record of it. It is also in the error
        # body, but the body only reaches disk when the corpus is on -- and the corpus is off by
        # default, so the log line has to carry it. Both spellings, because which one arrives is not
        # known from here and neither can hold a secret.
        "request-id",
        "anthropic-request-id",
        # The UNIFIED family, which is what a subscription credential is actually metered by.
        # Discovered 2026-09-18 by the prefix catch below: the twelve above it are the documented
        # API-key buckets and NOT ONE of them arrives on an OAuth token, so a list built from the
        # documentation alone would have recorded nothing and looked correct doing it.
        "anthropic-ratelimit-unified-status",
        "anthropic-ratelimit-unified-reset",
        "anthropic-ratelimit-unified-5h-status",
        "anthropic-ratelimit-unified-5h-reset",
        "anthropic-ratelimit-unified-5h-utilization",
        "anthropic-ratelimit-unified-7d-status",
        "anthropic-ratelimit-unified-7d-reset",
        "anthropic-ratelimit-unified-7d-utilization",
        "anthropic-ratelimit-unified-fallback-percentage",
        # Appeared on 2026-09-18 at 12:13 and NOT in the 11:19 sample of the same account, which is
        # the prefix catch doing its job a second time. Added on the same test as the eleven above:
        # it sits in the metering family beside `-fallback-percentage` and cannot plausibly hold a
        # credential. Unlike `-representative-claim`, its name says what kind of thing it is.
        "anthropic-ratelimit-unified-fallback",
        "anthropic-ratelimit-unified-overage-status",
        "anthropic-ratelimit-unified-overage-disabled-reason",
        # `anthropic-ratelimit-unified-representative-claim` is DELIBERATELY NOT HERE. It was seen
        # alongside the eleven above and its name does not say what it holds -- "claim" is the
        # vocabulary of tokens and assertions, not of counters. The eleven are plainly a status, a
        # timestamp or a number; this one is not plainly anything.
        #
        # It keeps being reported BY NAME through the prefix catch, so it is not lost and not
        # forgotten -- it is waiting for somebody to find out what is in it. Adding a name to this
        # list is one line; taking a value back out of a log file is not.
    }
)

# A bucket Anthropic adds after this list was written would otherwise be invisible. Its NAME is
# logged and its VALUE is discarded, so a new one becomes something a person can see and add
# deliberately -- without the value of anything unnamed ever being written.
#
# A name cannot leak a credential; a value can. That asymmetry is the whole of why this is safe, and
# it is why the prefix is `anthropic-ratelimit-` rather than the broader `anthropic-`.
RECORDED_HEADER_PREFIX = "anthropic-ratelimit-"

# A model can think for minutes, so the usual short read timeout would cut replies off. Connecting
# should still fail fast: LM Studio simply not running is the common failure.
#
# `read` here is only the fallback for a client built without a config. The real one is per backend
# and set on each request below, because Phase 4 found a single shared 600 s killing a healthy local
# prefill while being far longer than Anthropic has ever needed.
TIMEOUT = httpx.Timeout(connect=5.0, read=600.0, write=30.0, pool=5.0)


def create_client() -> httpx.AsyncClient:
    """The single HTTP client shared by every request, so connections are reused."""
    return httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False)


def backend_timeout(backend: Backend) -> httpx.Timeout:
    """The shared timeouts, with this backend's own tolerance for silence.

    Only `read` varies. Connecting, writing and waiting for a pool slot are properties of this
    machine rather than of the model at the other end, and a backend that cannot be *reached*
    should still fail fast whichever one it is.
    """
    return httpx.Timeout(
        connect=TIMEOUT.connect,
        read=backend.read_timeout,
        write=TIMEOUT.write,
        pool=TIMEOUT.pool,
    )


@dataclass
class Counters:
    """Calls that arrived against rows that were written.

    **The difference is calls in flight plus calls silently lost.** A gap that persists, or a
    non-zero gap after shutdown, is the one blind spot nothing else reports: a row that fails to
    write already logs a warning, and a body that is not stored already has a word in its ref cell,
    but a call that never reaches `record()` at all leaves no trace whatsoever.

    Deliberately two integers and nothing else. A metrics endpoint and a sequence column in
    `calls.csv` were both considered and reserved to `docs/backlog.md`; the second is forbidden
    outright, since that file not changing is a milestone non-goal.
    """

    arrived: int = 0
    recorded: int = 0

    @property
    def lost(self) -> int:
        return self.arrived - self.recorded


@dataclass
class Once:
    """A latch that lets the first caller through and nobody after it.

    Mutable, and held by the frozen `Proxy` the same way `Counters` is — a frozen dataclass can hold
    something that changes, it just cannot be reassigned.
    """

    fired: bool = False

    def take(self) -> bool:
        """True exactly once, for the first caller."""
        if self.fired:
            return False
        self.fired = True
        return True


@dataclass(frozen=True)
class Proxy:
    """Sends requests onward to a backend and streams the reply back untouched."""

    config: Config
    client: httpx.AsyncClient
    api_keys: dict[str, str]
    stats: StatsWriter
    corpus: CorpusWriter | None = None
    headers_sampled: Once = field(default_factory=Once)
    """**The control for the failure line below, and it exists to stop one sentence being assumed.**

    A `429` that names no exhausted bucket is only evidence if a *successful* reply on the same
    credential names one. Without this, "the rejection carried no rate-limit headers" and "this
    credential is never sent rate-limit headers" are indistinguishable, and only the first reads
    like a finding.

    Once per process, on the first reply that is **not** an error — a failure must not consume it,
    or a session that opens with a burst of 429s never samples a success at all."""
    counters: Counters = field(default_factory=Counters)
    """**Always on, independent of `corpus.enabled`**, and that is why it lives here rather than in
    `corpus.py`. It answers a `calls.csv` question — *was a row never written at all?* — and
    `calls.csv` is always on while the corpus is opt-in. Built inside the corpus it would be absent
    on the default machine, which is the only machine the question is about."""

    async def begin(self, request: Request) -> tuple[Call, bytes, Peeked, str | None]:
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
        self.counters.arrived += 1
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
        if self.corpus is not None:
            # Held until `record()`, which against a local model is minutes rather than the
            # microseconds it lived for before. The corpus does not change *whether* the request
            # body is held whole -- `await request.body()` above already does that -- only *how
            # long*, and that is the cost this line adds.
            call.request_body = body
        # `for_routing` is a THROWAWAY copy, inflated only if the body arrived compressed. `body`
        # -- what arrived -- is what gets relayed and what the corpus stores, byte for byte.
        for_routing = body
        unreadable: str | None = None
        try:
            for_routing = decoded_for_peek(body, request.headers.get("content-encoding"))
        except BodyUnreadable as exc:
            unreadable = str(exc)
        peeked = peek(for_routing) if unreadable is None else Peeked(None, None)
        call.model = peeked.model or ""
        call.stream = peeked.stream
        return call, body, peeked, unreadable

    async def messages(self, request: Request) -> Response:
        """`POST /v1/messages` — the call that names a model, so routing is decided from the body."""
        call, body, peeked, unreadable = await self.begin(request)

        if peeked.model is None:
            # Refused before any backend was chosen, so `backend` stays empty. It still gets a row:
            # a call the router turned away is a call, and a silent gap is worse than blanks.
            #
            # `unreadable` separates "the body says nothing about a model" from "the body could not
            # be read at all" -- which used to print the same sentence and sent a session hunting
            # for a field that was there, compressed.
            detail = unreadable or (
                "The request body carries no 'model' field, so there is no way to tell which "
                "backend it belongs to."
            )
            call.failed("http_error", "400", detail)
            self.record(call)
            return error_response(400, "invalid_request_error", detail)
        name, backend = backend_for_model(peeked.model, self.config.backends)
        return await self.relay(request, call, body, name, backend)

    async def anything_else(self, request: Request) -> Response:
        """Any path we did not anticipate.

        Forwarded rather than refused, so an unexpected endpoint is not fatal. Without a model name
        there is nothing to route on, and Claude Code believes it is talking to Anthropic, so that
        is where such a request goes.
        """
        call, body, peeked, _ = await self.begin(request)

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
            timeout=backend_timeout(backend),
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
            # And the headers say what the body cannot. A 429 body is the single word "Error"; which
            # bucket was hit and when it clears are here or nowhere. Logged rather than put in a
            # column: `calls.csv` taking new columns is a Milestone 2 non-goal, and where this
            # durably lives is not this task's to decide.
            logger.warning(
                "%s replied %s to %s: %s",
                name,
                reply.status_code,
                request.url.path,
                describe_headers(*recorded_headers(reply)),
            )
        elif request.url.path.startswith("/v1/messages") and self.headers_sampled.take():
            # The control, once per process. Logged at INFO rather than WARNING because nothing is
            # wrong, and once rather than always because every call reporting its buckets would
            # drown the file the failure lines have to be found in.
            #
            # PATH-GATED, and this is not a refinement -- the first version was WRONG. Claude Code
            # probes `/api/hello` before its first real call, the router forwards it, and it comes
            # back 200. So the latch was spent on an endpoint that meters nothing, and the control
            # line read `(none)` on the 2026-09-18 11:50 run. **That is the exact string the failure
            # lines print**, and reading it as "successes carry no buckets either" would have
            # reversed the phase's conclusion a second time -- this time through the instrument
            # built to stop that happening.
            logger.info(
                "%s replied %s to %s, sampling rate-limit headers once: %s",
                name,
                reply.status_code,
                request.url.path,
                describe_headers(*recorded_headers(reply)),
            )


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
        `docs/reference/design-decisions.md`. Nothing is ever *altered*: the injected event only
        ever follows bytes that have already gone out untouched.
        """
        streamed = is_sse(reply.headers.get("content-type", ""))
        scanner = scanner_for(reply.headers.get("content-type", ""))
        # The corpus's copy, accumulated only when there is somewhere for it to go. This is the one
        # thing the router has never done -- hold a whole response -- so nothing bounds it unless
        # something is made to, and `body_max_bytes` is that bound. Checked on every chunk, because
        # the memory is spent while the call runs and the queue's bound is not checked until after.
        copy: list[bytes] | None = [] if self.corpus is not None else None
        copied = 0
        cap = self.config.corpus.body_max_bytes
        try:
            async for chunk in reply.aiter_raw():
                call.saw_bytes(len(chunk))
                scanner.feed(chunk)
                if copy is not None:
                    copied += len(chunk)
                    if copied > cap:
                        # Discard what was accumulated and stop: a prefix labelled as a whole body
                        # is worse than a hole. The relay is untouched -- every byte still streams
                        # to the caller, because the copy was never in the path.
                        copy = None
                        call.response_over_cap = True
                    else:
                        copy.append(chunk)
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
            if copy is not None:
                call.response_body = b"".join(copy)
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
            self.counters.recorded += 1
            if self.corpus is not None:
                self.corpus.submit(
                    row, call.request_body, call.response_body, call.response_over_cap
                )
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


PEEK_MAX_DECOMPRESSED = 4 * 1024 * 1024

# What `decoded_for_peek` can undo. `br` and `zstd` are deliberately absent: neither is in the
# dependency list, and Claude Code sends `gzip`. An encoding outside this set is refused by name
# rather than guessed at.
PEEKABLE_ENCODINGS = frozenset({"gzip", "deflate", "x-gzip"})


class BodyUnreadable(Exception):
    """The body could not be inflated far enough to route it, with a reason fit to show a caller."""


def decoded_for_peek(body: bytes, content_encoding: str | None) -> bytes:
    """A copy of `body` inflated far enough to read, or `body` itself when it is not encoded.

    ***The original bytes are never replaced.*** This returns a throwaway used only by `peek`;
    `relay` forwards what arrived and the corpus stores what arrived, both byte for byte, which is
    the promise prompt caching rests on.

    **Why this exists.** The router reads `model` out of the body to choose a backend. ***A
    first-party Claude Code gzips some request bodies*** -- measured 2026-09-19, and one pointed at
    a custom `ANTHROPIC_BASE_URL` never has in any capture -- so the peek was reading compressed
    bytes, finding no `model`, and refusing a valid request with *"carries no 'model' field"*. The
    field was there; the router could not see it.

    Raises `BodyUnreadable` rather than returning the original on failure, so the caller can say
    *which* of the two things went wrong instead of blaming a missing field for both.
    """
    if not content_encoding:
        return body
    encoding = content_encoding.strip().lower()
    if encoding in {"identity", ""}:
        return body
    if encoding not in PEEKABLE_ENCODINGS:
        raise BodyUnreadable(
            f"the body is {encoding!r}-encoded and this router cannot read it to find the model"
        )

    # `wbits=47` accepts a gzip or a zlib stream and detects which; `-15` is a raw deflate body,
    # which some clients send under the name `deflate`. Both are tried because the header does not
    # distinguish them and guessing wrong looks identical to a corrupt body.
    for wbits in (47, -15):
        machine = zlib.decompressobj(wbits)
        try:
            out = machine.decompress(body, PEEK_MAX_DECOMPRESSED)
        except zlib.error:
            continue
        if machine.unconsumed_tail:
            raise BodyUnreadable(
                f"the {encoding} body inflates past {PEEK_MAX_DECOMPRESSED} bytes, "
                "which is more than this router will read to find the model"
            )
        return out
    raise BodyUnreadable(f"the body is labelled {encoding} and did not decompress")


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
    `docs/milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv`
    has the column blank. Reading absence as unknown left 83 of 142 rows saying nothing, and left an
    empty cell meaning two different things.

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


def recorded_headers(reply: httpx.Response) -> tuple[dict[str, str], list[str]]:
    """What a failed reply is allowed to say about why it failed, and what it said unasked.

    Returns the allowlisted headers with their values, and the *names* of any
    `anthropic-ratelimit-*` header not on the list. The second half is what makes a bucket added
    after `RECORDED_RESPONSE_HEADERS` was written visible instead of silently dropped; its values
    are discarded, because a name cannot carry a credential and a value can.

    Reads the reply and changes nothing. The relayed bytes never pass through here -- headers are a
    separate object from the body stream, so this cannot touch what the caller receives.
    """
    recorded: dict[str, str] = {}
    unlisted: list[str] = []
    for name, value in reply.headers.multi_items():
        lowered = name.lower()
        if lowered in RECORDED_RESPONSE_HEADERS:
            recorded[lowered] = value
        elif lowered.startswith(RECORDED_HEADER_PREFIX):
            unlisted.append(lowered)
    return recorded, unlisted


def describe_headers(recorded: dict[str, str], unlisted: list[str]) -> str:
    """The log line's payload: `name=value` for what was asked for, bare names for what was not.

    `(none)` rather than an empty string when a reply carried neither, because **that is the
    interesting case** -- a `rate_limit_error` naming no exhausted bucket is not a rate limit, and a
    blank tail would read as a logging failure instead of as the finding it is.
    """
    parts = [f"{name}={value}" for name, value in sorted(recorded.items())]
    parts += [f"{name}=<unlisted>" for name in sorted(set(unlisted))]
    return " ".join(parts) if parts else "(none)"


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
