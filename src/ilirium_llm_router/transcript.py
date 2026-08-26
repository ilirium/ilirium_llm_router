"""Reading a captured reply back into the message it was.

**The store went to some trouble never to parse a body, and this module parses every one of them.**
That is not a contradiction, it is the line Phase 11 has to keep on the right side of: **parsing
lives in the tools; the store stays opaque.** Nothing here is imported by the write path.

**Two encodings, not one.** A reply is either an **SSE stream** — `message_start`, content blocks
arriving as deltas, `message_stop` — or a **single buffered JSON object**. The plan called the
second one a third of the traffic; measured over every response blob in the corpus on 2026-08-26 it
is **one call in 979**, the rest of the non-streamed traffic being `count_tokens` replies and
errors. **Both are still built**, because a `stream=false` success is legal and position 15 filters
nothing.

**The one mechanical rule of the baseline, and it is asked of the *response*.** A call contributes
a turn **only if its response is a message**; everything else is skipped and counted. That is
lossless because requests are cumulative — anything a skipped call carried reappears in the next
real one — and it asks *"is this response a message?"*, never *"is this call a probe?"*, so no
classification is smuggled back in.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

# **All eight are observed, not assumed** — counted across the live corpus and Phase 9's gate corpus
# on 2026-08-26. `ping` is in the list because it is a real event that carries nothing: a
# reassembler that treats an unknown event as a failure would reject every stream Anthropic sends.
SSE_EVENTS = (
    "message_start",
    "content_block_start",
    "content_block_delta",
    "content_block_stop",
    "message_delta",
    "message_stop",
    "ping",
    "error",
)

# Why a reply was not a message. **These are counted and reported in-band**, per the schema note, so
# a reader of a reconstructed transcript can see what is missing rather than infer it from a gap.
SKIP_EMPTY = "empty"
SKIP_ERROR = "error"
SKIP_STREAM_ERROR = "stream-error"
SKIP_NOT_A_MESSAGE = "not-a-message"
SKIP_MALFORMED = "malformed"
SKIP_INCOMPLETE = "incomplete"


@dataclass(frozen=True)
class Reply:
    """A reassembled assistant message, in the shape the wire used."""

    message: dict[str, Any]
    streamed: bool


@dataclass(frozen=True)
class NotAMessage:
    """A response that carried no turn, and which of the six reasons applies."""

    reason: str
    streamed: bool


def reassemble(body: bytes) -> Reply | NotAMessage:
    """One captured response, read back into the message it was — or the reason it was not one.

    **Never raises on a malformed body.** A corpus is a record of what happened, and what happened
    includes truncated streams and replies that are not messages at all. A tool that threw on the
    first of those would stop at the first interesting row.
    """
    if not body.strip():
        return NotAMessage(SKIP_EMPTY, streamed=False)
    if body.lstrip()[:1] == b"{":
        return _buffered(body)
    return _streamed(body)


def _buffered(body: bytes) -> Reply | NotAMessage:
    """A single JSON object. Three shapes occur and only one of them is a turn."""
    try:
        payload = json.loads(body)
    except (ValueError, UnicodeDecodeError):
        return NotAMessage(SKIP_MALFORMED, streamed=False)
    if not isinstance(payload, dict):
        return NotAMessage(SKIP_MALFORMED, streamed=False)
    kind = payload.get("type")
    if kind == "message":
        return Reply(payload, streamed=False)
    if kind == "error":
        return NotAMessage(SKIP_ERROR, streamed=False)
    # `{"input_tokens": N}` — a `count_tokens` reply, 47 blobs in the corpus. Not an error and not a
    # turn, and the difference matters: position 20 defers errors as *work*, while this is simply
    # not a message and never will be.
    return NotAMessage(SKIP_NOT_A_MESSAGE, streamed=False)


def _streamed(body: bytes) -> Reply | NotAMessage:
    """An SSE stream, replayed into the message it was building.

    **`message_start` carries the whole message except its content**, so reassembly is: take that
    skeleton, fill `content` from the block events, then let `message_delta` overwrite `stop_reason`
    and top up `usage`. Nothing is invented.
    """
    message: dict[str, Any] | None = None
    blocks: dict[int, dict[str, Any]] = {}
    partial_json: dict[int, list[str]] = {}
    stopped = False

    for event in _events(body):
        kind = event.get("type")
        if kind == "error":
            # The router's one exception to byte-relay is ending a broken stream with an SSE
            # `error` event, so this is how a truncated capture presents. Whatever arrived before
            # it is an incomplete message, and the baseline does not emit incomplete turns.
            return NotAMessage(SKIP_STREAM_ERROR, streamed=True)
        if kind == "message_start":
            message = dict(event.get("message") or {})
            message["content"] = []
        elif kind == "content_block_start":
            index = event.get("index", 0)
            blocks[index] = dict(event.get("content_block") or {})
            partial_json[index] = []
        elif kind == "content_block_delta":
            _apply_delta(blocks, partial_json, event)
        elif kind == "content_block_stop":
            _close_block(blocks, partial_json, event.get("index", 0))
        elif kind == "message_delta":
            if message is not None:
                message.update(event.get("delta") or {})
                _merge_usage(message, event.get("usage"))
        elif kind == "message_stop":
            stopped = True

    if message is None:
        return NotAMessage(SKIP_NOT_A_MESSAGE, streamed=True)
    if not stopped:
        return NotAMessage(SKIP_INCOMPLETE, streamed=True)
    message["content"] = [blocks[index] for index in sorted(blocks)]
    return Reply(message, streamed=True)


def _events(body: bytes) -> list[dict[str, Any]]:
    """Every `data:` payload in the stream, in order, with unparseable ones dropped.

    **The `event:` line is deliberately ignored.** Every payload carries its own `type`, and the two
    always agree — so reading the `type` is one source instead of two that could disagree. A `data:`
    line may repeat within one event per the SSE spec, so they are joined rather than replaced.
    """
    events: list[dict[str, Any]] = []
    data: list[str] = []

    def flush() -> None:
        if not data:
            return
        try:
            payload = json.loads("".join(data))
        except ValueError:
            payload = None
        if isinstance(payload, dict):
            events.append(payload)
        data.clear()

    for line in body.decode("utf-8", "replace").splitlines():
        if line.startswith("data:"):
            data.append(line[5:].lstrip())
        elif not line.strip():
            flush()
    flush()
    return events


def _apply_delta(
    blocks: dict[int, dict[str, Any]],
    partial_json: dict[int, list[str]],
    event: dict[str, Any],
) -> None:
    """Four delta types, and `input_json_delta` is the only one that is not an append.

    A tool's input arrives as **JSON string fragments** — 64,260 of them across two days against
    2,071 `text_delta` — which are concatenated here and parsed once the block closes. Parsing each
    fragment would fail on every one but the last.
    """
    index = event.get("index", 0)
    block = blocks.get(index)
    if block is None:
        return
    delta = event.get("delta") or {}
    kind = delta.get("type")
    if kind == "text_delta":
        block["text"] = block.get("text", "") + delta.get("text", "")
    elif kind == "thinking_delta":
        block["thinking"] = block.get("thinking", "") + delta.get("thinking", "")
    elif kind == "signature_delta":
        block["signature"] = block.get("signature", "") + delta.get("signature", "")
    elif kind == "input_json_delta":
        partial_json.setdefault(index, []).append(delta.get("partial_json", ""))


def _close_block(
    blocks: dict[int, dict[str, Any]],
    partial_json: dict[int, list[str]],
    index: int,
) -> None:
    """Turn an accumulated `input_json_delta` run into the tool input it spells.

    **An empty run means `{}` rather than a parse of the empty string** — a tool taking no arguments
    sends `content_block_start` and `content_block_stop` with nothing between them, and that is a
    valid call rather than a broken one.
    """
    block = blocks.get(index)
    if block is None or block.get("type") != "tool_use":
        return
    raw = "".join(partial_json.get(index, []))
    if not raw:
        block["input"] = {}
        return
    try:
        block["input"] = json.loads(raw)
    except ValueError:
        # Kept as the string it was rather than dropped. A tool input that did not parse is a fact
        # about the capture, and losing it silently is the one outcome that helps nobody.
        block["input"] = raw


def _merge_usage(message: dict[str, Any], usage: dict[str, Any] | None) -> None:
    """`message_delta` carries the final output token count; `message_start` carried the input one.

    **Merged rather than replaced**, because the two halves arrive at opposite ends of the stream
    and a replace would drop `input_tokens` and both cache counters on every call.
    """
    if not usage:
        return
    merged = dict(message.get("usage") or {})
    merged.update(usage)
    message["usage"] = merged
