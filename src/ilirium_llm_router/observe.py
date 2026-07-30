"""Watching a reply go past without touching it.

The bytes going downstream are the bytes that arrived. These scanners are fed a *copy* of each chunk
and pick the numbers out of it; nothing here can change what the caller receives. Kept out of
`proxy.py` so the forwarding path stays readable.

Which path runs is decided by the response `content-type`, not by the request's `stream` flag. The
content-type describes what the bytes *are*; the flag describes what was *asked for*. They are also
separate columns in the CSV, so a disagreement between them is visible rather than invisible.

The trap this file exists to avoid, verified against LM Studio on 2026-07-29
(`docs/lmstudio-usage-check.md`): a streamed reply carries `input_tokens` in `message_start` and
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
from dataclasses import dataclass

logger = logging.getLogger(__name__)

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
        # Only ever holds the tail after the last newline, so passing the cap means one line did.
        if len(self._pending) > MAX_SCAN_BYTES:
            self._give_up("a single SSE line grew past the scan limit")
            return

        lines = self._pending.split(b"\n")
        # The last piece has no newline after it yet: an unfinished line, kept for the next chunk.
        self._pending = bytearray(lines.pop())
        for line in lines:
            self._read(bytes(line))

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
        self.observation.cache_read_input_tokens = _count(
            usage.get("cache_read_input_tokens")
        )
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
            self.observation.cache_read_input_tokens = _count(
                usage.get("cache_read_input_tokens")
            )
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


def scanner_for(content_type: str) -> Scanner:
    """Pick the path from what the bytes claim to be."""
    if SSE_CONTENT_TYPE in content_type.lower():
        return SseScanner()
    return BufferedScanner()


def _read_error(payload: dict[str, object], observation: Observation) -> None:
    """Anthropic's error shape, which LM Studio also uses: `{"error": {"type": …, "message": …}}`."""
    error = payload.get("error")
    if not isinstance(error, dict):
        return
    if isinstance(error.get("type"), str):
        observation.error_type = str(error["type"])
    if isinstance(error.get("message"), str):
        observation.error_message = str(error["message"])


def _count(value: object) -> int | None:
    """A token count, or None if the field was absent or not a number.

    `bool` is excluded explicitly because it is a subclass of `int` in Python, and `True` arriving
    where a count belongs should read as "not a number" rather than as one token.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value
