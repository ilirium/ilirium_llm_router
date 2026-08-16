"""Watching a reply go past without touching it.

The bytes going downstream are the bytes that arrived. These scanners are fed a *copy* of each chunk
and pick the numbers out of it; nothing here can change what the caller receives. Kept out of
`proxy.py` so the forwarding path stays readable.

Which path runs is decided by the response `content-type`, not by the request's `stream` flag. The
content-type describes what the bytes *are*; the flag describes what was *asked for*. They are also
separate columns in the CSV, so a disagreement between them is visible rather than invisible.

The trap this file exists to avoid, verified against LM Studio on 2026-07-29
(`docs/procedures/lmstudio-usage-check.md`): a streamed reply carries `input_tokens` in
`message_start` and
`output_tokens` in the final `message_delta`, but **LM Studio also repeats `input_tokens` in
`message_delta` and Anthropic does not**. A scanner keyed on `message_delta` alone would look
correct against the local backend and silently record empty input counts for every Anthropic call.
So `message_start` is the only place `input_tokens` is ever read from.

Nothing here may raise. A scanner runs inside the response stream, so an exception would break the
call it is only supposed to watch — every entry point catches and gives up instead. Giving up costs
the token columns and never the reply.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from starlette.requests import Request

from .stats import CallRecord, ErrorStatus

logger = logging.getLogger(__name__)

# Copied straight off the request headers — a dictionary lookup, no body parsing, which is the whole
# reason these two columns are affordable. `agent_id` arrives only on a subagent's call, so an empty
# one means the main conversation rather than a missing value.
SESSION_HEADER = "x-claude-code-session-id"
AGENT_HEADER = "x-claude-code-agent-id"

# A ceiling on what a scanner will hold in memory, for the buffered body and for a single unbroken
# SSE line alike. One number because it answers one question: how much is it worth remembering
# about a reply nobody enumerated? The catch-all route forwards any path, so the reply to an
# unanticipated endpoint could be any size at all, and this turns "memory decided by a stranger"
# into a known ceiling. 1 MiB is roughly four times the worst realistic reply, and the same order as
# the request body `proxy.py` already holds whole.
MAX_SCAN_BYTES = 1024 * 1024

SSE_CONTENT_TYPE = "text/event-stream"
DATA_PREFIX = b"data:"


@dataclass
class Observation:
    """What watching one reply revealed.

    Every field stays at its default when the reply did not carry it. `None` means "not found" and
    reaches the CSV as an empty cell, never as a zero — an absent token count and a real zero are
    different facts.
    """

    input_tokens: int | None = None
    output_tokens: int | None = None
    cache_read_input_tokens: int | None = None
    cache_creation_input_tokens: int | None = None
    stop_reason: str | None = None

    # From an `error` object in the reply, whichever path found it. Naming these after the error
    # rather than after the CSV's `error_code` is deliberate: what the *status* of the call was is
    # decided by the caller, which knows about HTTP codes and transport failures. This is only what
    # the body said.
    error_type: str = ""
    error_message: str = ""

    # True only when the error arrived as an SSE `error` event mid-stream. That is the case a plain
    # status code cannot express: a streamed reply returns HTTP 200 before any content exists, so
    # the failure comes down the tee rather than back in the status line.
    stream_error: bool = False


class Scanner:
    """Common shell: hold the observation, and never let a failure escape.

    Subclasses implement `_feed` and `_finish` and may raise freely; this catches on their behalf.
    """

    def __init__(self) -> None:
        self.observation = Observation()
        self.gave_up = False

    def feed(self, chunk: bytes) -> None:
        """Take a copy of one chunk of the reply."""
        if self.gave_up:
            return
        try:
            self._feed(chunk)
        except Exception as exc:  # noqa: BLE001 — watching a call must never break it
            self._give_up(exc)

    def finish(self) -> None:
        """The reply is complete. The buffered path does all its work here."""
        if self.gave_up:
            return
        try:
            self._finish()
        except Exception as exc:  # noqa: BLE001 — watching a call must never break it
            self._give_up(exc)

    def _feed(self, chunk: bytes) -> None:
        raise NotImplementedError

    def _finish(self) -> None:
        pass

    def _give_up(self, reason: object = None) -> None:
        """Stop watching. The row still gets written, with empty token columns.

        Not an error worth raising to anyone: `response_bytes` is a counter and stays accurate, and
        the `stream` column says which path came up empty. Those two are what make such a row a bug
        report rather than a dead end.
        """
        self.gave_up = True
        logger.debug("Stopped reading usage from a reply: %s", reason)


class SseScanner(Scanner):
    """The streaming path: a small line buffer, discarded as it goes.

    Every `data:` line is a complete JSON document on its own, so memory stays flat however long the
    model talks. Events are recognised by the `type` field *inside* the JSON rather than by the
    `event:` line above it — one line to look at instead of two to pair up, and it does not assume
    both backends frame their events the same way.
    """

    def __init__(self) -> None:
        super().__init__()
        self._pending = bytearray()

    def _feed(self, chunk: bytes) -> None:
        self._pending += chunk

        lines = self._pending.split(b"\n")
        # The last piece has no newline after it yet: an unfinished line, kept for the next chunk.
        self._pending = bytearray(lines.pop())
        for line in lines:
            self._read(bytes(line))

        # Checked *after* the split, on the tail alone. Before the split `_pending` is the previous
        # tail plus the whole arriving chunk, so a large chunk of ordinary short lines tripped the
        # cap and cost every token column — measured in Phase 6 at 1049671 bytes whose longest line
        # was 101. What this limit is for is one unbroken line growing without end, and the tail is
        # the only thing that can do that.
        if len(self._pending) > MAX_SCAN_BYTES:
            self._give_up("a single SSE line grew past the scan limit")

    def _finish(self) -> None:
        """Read whatever is left over without a newline after it.

        A well-behaved backend ends its last event with a blank line and this does nothing. But the
        line held back here is the *final* one, which is where `output_tokens` and `stop_reason`
        live — so a backend that simply stops after the closing brace would cost exactly the two
        numbers the stream was being watched for.
        """
        leftover = bytes(self._pending)
        self._pending = bytearray()
        self._read(leftover)

    def _read(self, line: bytes) -> None:
        if not line.startswith(DATA_PREFIX):
            return
        try:
            payload = json.loads(line[len(DATA_PREFIX) :])
        except (ValueError, UnicodeDecodeError):
            # One unreadable line is not a reason to stop reading the rest of the stream.
            return
        if not isinstance(payload, dict):
            return

        kind = payload.get("type")
        if kind == "message_start":
            self._read_start(payload)
        elif kind == "message_delta":
            self._read_delta(payload)
        elif kind == "error":
            self.observation.stream_error = True
            _read_error(payload, self.observation)

    def _read_start(self, payload: dict[str, object]) -> None:
        """`message_start` is the only place `input_tokens` is read from. See the module docstring."""
        message = payload.get("message")
        usage = message.get("usage") if isinstance(message, dict) else None
        if not isinstance(usage, dict):
            return
        self.observation.input_tokens = _count(usage.get("input_tokens"))
        self.observation.cache_read_input_tokens = _count(usage.get("cache_read_input_tokens"))
        self.observation.cache_creation_input_tokens = _count(
            usage.get("cache_creation_input_tokens")
        )

    def _read_delta(self, payload: dict[str, object]) -> None:
        """`output_tokens` and `stop_reason`, from the last `message_delta` that carries them.

        Assigned only when actually present, so an intermediate delta with a null `stop_reason`
        cannot wipe out the real one — and `input_tokens` is not read here at any price.
        """
        usage = payload.get("usage")
        if isinstance(usage, dict):
            output = _count(usage.get("output_tokens"))
            if output is not None:
                self.observation.output_tokens = output

        delta = payload.get("delta")
        if isinstance(delta, dict):
            stop_reason = delta.get("stop_reason")
            if isinstance(stop_reason, str) and stop_reason:
                self.observation.stop_reason = stop_reason


class BufferedScanner(Scanner):
    """The non-streaming path: accumulate to the cap, parse once at the end.

    `usage` sits inside one JSON object, and an object's contents are unknown until its closing
    brace, so this is the one place the "do not buffer the reply" rule cannot hold literally. A tail
    buffer was rejected for betting on field order: it works only because Anthropic happens to emit
    `usage` last, and would go silently empty the day either side reorders.
    """

    def __init__(self) -> None:
        super().__init__()
        self._body = bytearray()

    def _feed(self, chunk: bytes) -> None:
        if len(self._body) + len(chunk) > MAX_SCAN_BYTES:
            self._give_up("the reply grew past the scan limit")
            return
        self._body += chunk

    def _finish(self) -> None:
        payload = json.loads(bytes(self._body))
        if not isinstance(payload, dict):
            return

        usage = payload.get("usage")
        if isinstance(usage, dict):
            self.observation.input_tokens = _count(usage.get("input_tokens"))
            self.observation.output_tokens = _count(usage.get("output_tokens"))
            self.observation.cache_read_input_tokens = _count(usage.get("cache_read_input_tokens"))
            self.observation.cache_creation_input_tokens = _count(
                usage.get("cache_creation_input_tokens")
            )

        stop_reason = payload.get("stop_reason")
        if isinstance(stop_reason, str) and stop_reason:
            self.observation.stop_reason = stop_reason

        # An error body here came back with an HTTP status that says so, so this is not a
        # `stream_error` — only the wording, which is better than a bare status code in the CSV.
        if payload.get("type") == "error":
            _read_error(payload, self.observation)


def is_sse(content_type: str) -> bool:
    """Whether the reply is a stream of events rather than one document.

    Asked twice: once to pick the scanner, and once by `proxy.py` to decide whether a broken relay
    can be reported downstream at all. An SSE stream has a frame to put an error in; a half-written
    JSON object has nowhere to say so without corrupting itself.
    """
    return SSE_CONTENT_TYPE in content_type.lower()


def scanner_for(content_type: str) -> Scanner:
    """Pick the path from what the bytes claim to be."""
    return SseScanner() if is_sse(content_type) else BufferedScanner()


def _read_error(payload: dict[str, object], observation: Observation) -> None:
    """Anthropic's error shape, which LM Studio also uses: `{"error": {"type": …, "message": …}}`."""
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    error_type = error.get("type")
    if isinstance(error_type, str):
        observation.error_type = error_type
    message = error.get("message")
    if isinstance(message, str):
        observation.error_message = message


def _describe(error_type: str, message: str) -> str:
    """`type: message`, dropping either half the body did not carry."""
    if error_type and message:
        return f"{error_type}: {message}"
    return error_type or message


class Call:
    """One call, from the moment it arrived to the row it becomes.

    Deliberately a bag of plain attributes rather than a tidy object: each one is a CSV column, and
    each is filled in at the point it becomes known — the model once the body is peeked, the backend
    once routing has run, the timings as bytes go past.
    """

    def __init__(self, request: Request) -> None:
        # Both clocks start here, at arrival. `ttfb_ms` stops at the first byte and `duration_ms` at
        # the last, so the pair reads as "how long until it began" and "how long in total" without
        # anyone having to subtract one from the other.
        self._started = time.perf_counter()

        self.timestamp = datetime.now(UTC).isoformat(timespec="milliseconds")
        self.session_id = request.headers.get(SESSION_HEADER, "")
        self.agent_id = request.headers.get(AGENT_HEADER, "")
        # Without the query string: `?beta=true` is forwarded but says nothing about which endpoint
        # was called, and the point of this column is to name the endpoints nobody anticipated.
        self.path = request.url.path

        self.backend = ""
        self.model = ""
        self.stream: bool | None = None
        self.request_bytes = 0
        self.response_bytes = 0
        self.ttfb_ms: int | None = None
        self.error_status: ErrorStatus = "ok"
        self.error_code = ""
        self.error_message = ""

    def saw_bytes(self, count: int) -> None:
        """One chunk went downstream. The first one is what `ttfb_ms` measures.

        Measured at the first byte of the *body*, not at the response headers: headers arrive as
        soon as the backend accepts the request, which for a streamed reply says nothing about when
        the model started producing — the entire number being asked for.
        """
        if self.ttfb_ms is None:
            self.ttfb_ms = self._elapsed_ms()
        self.response_bytes += count

    def failed(self, status: ErrorStatus, code: str, message: str) -> None:
        self.error_status = status
        self.error_code = code
        self.error_message = message

    def record(self, observation: Observation | None = None) -> CallRecord:
        """The finished row. Stops the duration clock, so call it once, at the end."""
        seen = observation or Observation()

        if seen.stream_error and self.error_status == "ok":
            # A streamed reply returns HTTP 200 before any content exists, so an error arriving
            # down the tee is the only place this failure can be seen at all.
            self.failed("stream_error", seen.error_type, seen.error_message)
        elif self.error_status != "ok" and not self.error_message:
            # The backend's own wording, which beats a bare status code in the file — carrying the
            # symbolic type alongside it. On this branch `error_code` holds the HTTP status, so
            # unlike the `stream_error` case above there is nowhere else for the type to go, and it
            # was being dropped. It is the half worth keeping: a type is countable with a
            # spreadsheet filter where a message is only readable, and Anthropic answers a
            # rate-limited call with the single word "Error", which alone says nothing at all.
            self.error_message = _describe(seen.error_type, seen.error_message)

        return CallRecord(
            timestamp=self.timestamp,
            session_id=self.session_id,
            agent_id=self.agent_id,
            backend=self.backend,
            model=self.model,
            path=self.path,
            stream=self.stream,
            input_tokens=seen.input_tokens,
            output_tokens=seen.output_tokens,
            cache_read_input_tokens=seen.cache_read_input_tokens,
            cache_creation_input_tokens=seen.cache_creation_input_tokens,
            stop_reason=seen.stop_reason,
            request_bytes=self.request_bytes,
            response_bytes=self.response_bytes,
            ttfb_ms=self.ttfb_ms,
            duration_ms=self._elapsed_ms(),
            error_status=self.error_status,
            error_code=self.error_code,
            error_message=self.error_message,
        )

    def _elapsed_ms(self) -> int:
        return round((time.perf_counter() - self._started) * 1000)


def transport_error_code(exc: Exception) -> str:
    """A symbolic code for a failure that never got an HTTP status.

    Derived from the exception's class name rather than looked up in a table, so httpx's whole
    family is covered — and one it adds later still lands as something readable instead of falling
    into a catch-all. `ConnectError` becomes `connect_error`, `RemoteProtocolError` becomes
    `remote_protocol_error`, `PoolTimeout` becomes `pool_timeout`.

    LM Studio simply not running is the common failure here, and it is a `ConnectError` with no
    status code at all — which is exactly why leaving `error_code` blank was never an option.
    """
    return _snake_case(type(exc).__name__)


def describe_exception(exc: Exception) -> str:
    """`ReadError: Connection reset by peer`, or just `ReadError` when there is nothing after it.

    httpx raises several of its errors with an empty message — a connection reset mid-stream arrives
    as `ReadError("")` — and the obvious f-string then writes `ReadError: ` into the CSV and into the
    error event the caller sees, a dangling colon promising a reason that never comes. Measured on
    2026-07-31 against a stand-in backend that cut a reply off mid-answer; every unit test until then
    had supplied a message, so all of them read correctly and the real failure did not.
    """
    reason = str(exc).strip()
    return f"{type(exc).__name__}: {reason}" if reason else type(exc).__name__


def _snake_case(name: str) -> str:
    """`ConnectError` → `connect_error`, `HTTPStatusError` → `http_status_error`.

    The second pattern is what keeps an acronym together: split before a capital that follows a
    lowercase, and before the last capital of a run that starts a new word.
    """
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()


def _count(value: object) -> int | None:
    """A token count, or None if the field was absent or not a number.

    `bool` is excluded explicitly because it is a subclass of `int` in Python, and `True` arriving
    where a count belongs should read as "not a number" rather than as one token.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value
