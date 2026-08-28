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

**And a captured session is not one conversation.** Requests are cumulative — request *N* carries
turns 1..*N* — so a session is reconstructed by walking its calls in timestamp order and taking the
difference. Three facts about the real corpus decide how that is done, and all three were measured
before this code was written rather than assumed:

* **"Cumulative" is false on raw bytes.** Two normalisations make it true — `cache_control` markers
  migrate between calls, and the same message is serialised as a bare string in one call and as
  content blocks in the next. On one 77-call conversation the prefix property holds **0/76** raw,
  **46/76** with the marker stripped, **0/76** with only the encoding fixed, **65/76** with both.
* **A `session_id` holds several conversations.** The real one, subagents carrying the parent's id,
  and short probes — 36 conversations across 9 sessions. Separated **by their root message**,
  which asks *"is this the same conversation?"* and never *"is this call a probe?"*
* **The tail of a request is provisional.** 100 times in the corpus a message was revised by the
  next call, 9 of those changing role. The conversation's turns are therefore taken from its
  **latest** state, never as first seen — otherwise a retracted turn is written down as real.

**The one mechanical rule of the baseline, and it is asked of the *response*.** A call contributes
a turn **only if its response is a message**; everything else is skipped and counted. That is
lossless because requests are cumulative — anything a skipped call carried reappears in the next
real one — and it asks *"is this response a message?"*, never *"is this call a probe?"*, so no
classification is smuggled back in.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

# **All eight are observed, not assumed** — counted across the live corpus and Phase 9's gate corpus
# on 2026-08-26. `ping` is in the list because it is a real event that carries nothing: a
# reassembler that treats an unknown event as a failure would reject every stream Anthropic sends.
#
# **This is a record, not a guard, and mutation testing is what made that explicit.** Nothing below
# reads it — `_events` takes each payload's own `type` and ignores the `event:` line entirely — so
# **eight mutants survived the 2026-08-28 sweep** by changing names no code consults. It is kept
# because the eight are *measured*, and `test_transcript.py` pins the literals so the record cannot
# rot unnoticed. **Do not read it as validation:** an unlisted event is passed over, not rejected.
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

# How many hex characters of the root message's digest name a conversation on disk. A session's
# **main** conversation keeps the settled `<session_id>.jsonl`; every other one is
# `<session_id>-<key>.jsonl`. **A digest and not an ordinal**, because `-02` is stable only within
# one run: convert a growing corpus tomorrow, or pass a different set of day folders, and it
# silently names a different conversation. Measured over all 36 conversations: no within-session
# collision at 8 characters.
CONVERSATION_KEY_CHARS = 8

# Why a turn's user-side context is missing. **Not a skip reason** — a skip means a *response*
# carried no turn, while this means the *request* body is not on disk to diff against.
GAP_NO_REQUEST_BODY = "no-request-body"


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


class MissingDayError(Exception):
    """A selected session has calls in a day folder that was not passed.

    **This error is the whole defence and it is deliberately not a warning.** A cross-day session
    reconstructed from only the later folder does not look broken: it produces a plausible
    transcript whose opening turn silently contains a day of prior conversation. Nothing downstream
    can detect that, and a reader cannot either.

    *The obvious cheaper check — "a conversation whose first call is already deep did not start
    here" — was measured and refused. **11 of the corpus's 36 conversations legitimately open at
    two messages**, so a depth rule false-positives on a third of them. The exact set difference is
    the only honest form.*
    """


@dataclass(frozen=True)
class CapturedCall:
    """One call as reconstruction needs it: when, where, and the two bodies.

    `request` is `None` when no body was stored — the sentinel cases of register §11, of which only
    `too_large` occurs today. **That is not an edge case in the corpus's own terms:** request bodies
    grow monotonically, so a long enough session always crosses the cap and **the tail is always
    what is lost**. It is 45 contiguous calls at the end of the largest session here.
    """

    timestamp: str
    day: str
    request: bytes | None
    response: bytes | None


@dataclass(frozen=True)
class Turn:
    """One reconstructed turn, and which of the two sources it came from.

    **`source` is not decoration.** An assistant turn exists twice — in its own response blob and,
    one call later, inside the next request's `messages`. The two agree on block shape in 630 of 631
    cases; where they differ it is a `caller` field that the **response** carries and the request
    never does (47,628 request-side `tool_use` blocks, none with it). The response is therefore
    preferred and `source` records when that was not possible.
    """

    position: int
    role: str
    message: dict[str, Any]
    source: str
    timestamp: str


@dataclass(frozen=True)
class Gap:
    """A place where the user-side context is missing rather than empty.

    Emitted **in-band**, because the failure this phase is organised against is a transcript that
    reads as real while something is missing. A file that simply stopped early would be exactly
    that; 45 assistant turns each preceded by a gap cannot be mistaken for a complete record.
    """

    position: int
    reason: str
    timestamp: str


@dataclass(frozen=True)
class Conversation:
    """One conversation inside a session, with the facts a reader needs to distrust it.

    `unconfirmed` is the count of trailing turns that **no later call confirmed**. It is never zero
    for a live conversation: the final call's messages have nothing after them to agree, and holding
    them back would lose the last real turn of every session. Stating the number is the honest
    alternative to pretending the boundary is not there.
    """

    session_id: str
    key: str
    main: bool
    entries: tuple[Turn | Gap, ...]
    calls: int
    depth: int
    unconfirmed: int
    revised: int
    shrank: int
    skipped: Mapping[str, int] = field(default_factory=dict)

    def filename(self) -> str:
        """`<session_id>.jsonl` for the main conversation, `<session_id>-<key>.jsonl` otherwise."""
        return f"{self.session_id}.jsonl" if self.main else f"{self.session_id}-{self.key}.jsonl"


@dataclass(frozen=True)
class Reconstruction:
    """Every conversation found under one `session_id`, main first."""

    session_id: str
    conversations: tuple[Conversation, ...]
    days: tuple[str, ...]


def normalise(message: Mapping[str, Any]) -> dict[str, Any]:
    """One message, in the form two calls can be compared in.

    **Two normalisations, and neither is optional.** `cache_control` is a caching hint that Claude
    Code puts on the *last* message of each request, so it walks forward as the conversation grows
    and every comparison breaks on a turn whose content never changed. And `content` is legal both
    as a bare string and as a list of blocks, for the same message in the same session.

    **Nothing said is lost either way** — that is what makes these normalisations rather than edits.
    """
    normalised = _strip_cache_control(dict(message))
    content = normalised.get("content")
    if isinstance(content, str):
        normalised["content"] = [{"type": "text", "text": content}]
    return normalised


def _strip_cache_control(value: Any) -> Any:
    """`cache_control` removed wherever it sits — it appears on blocks, not only on messages."""
    if isinstance(value, dict):
        return {k: _strip_cache_control(v) for k, v in value.items() if k != "cache_control"}
    if isinstance(value, list):
        return [_strip_cache_control(v) for v in value]
    return value


def conversation_key(messages: Sequence[Mapping[str, Any]]) -> str:
    """A conversation's name, taken from its **normalised** root message.

    Normalised matters and is not belt-and-braces: one session sent its opening message as a bare
    string in the first call and as content blocks in every call after. Hashing raw bytes would give
    one conversation two names and split its file in half.
    """
    return hashlib.sha256(_key(normalise(messages[0])).encode("utf-8")).hexdigest()[
        :CONVERSATION_KEY_CHARS
    ]


def _key(value: Any) -> str:
    """A stable string for equality. `sort_keys` so key order cannot fake a difference."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def reconstruct(
    calls: Iterable[CapturedCall],
    session_id: str,
    *,
    days_passed: Sequence[str],
    session_days: Sequence[str] | None = None,
) -> Reconstruction:
    """Every conversation under one session, walked in timestamp order across day folders.

    `session_days` is every day the session has calls in, which the caller learns by reading the
    corpus rather than the selection. When it names a day `days_passed` does not, this raises rather
    than reconstructing what it can — see `MissingDayError`.

    **Timestamp order, not index order.** The index is written in *completion* order, so reading it
    as it lies numbers a session's calls by when each one finished.
    """
    missing = sorted(set(session_days or ()) - set(days_passed))
    if missing:
        raise MissingDayError(
            f"session {session_id} has calls in {', '.join(missing)}, which "
            f"{'was' if len(missing) == 1 else 'were'} not passed. Reconstructing without "
            f"{'it' if len(missing) == 1 else 'them'} would open the transcript part-way through a "
            f"conversation that already had turns, with nothing in the output to say so. "
            f"Pass {' '.join(missing)} as well."
        )

    ordered = sorted(calls, key=lambda call: (call.timestamp, call.day))
    stray = sorted({call.day for call in ordered} - set(days_passed))
    if stray:
        raise MissingDayError(
            f"session {session_id} was given calls from {', '.join(stray)}, which "
            f"{'is' if len(stray) == 1 else 'are'} not among the day folders passed "
            f"({', '.join(days_passed) or 'none'})."
        )

    grouped: dict[str, list[tuple[CapturedCall, list[dict[str, Any]]]]] = {}
    orphans: list[CapturedCall] = []
    for call in ordered:
        messages = _messages_of(call)
        if messages is None:
            # No request body, so no root to key on. It belongs to whichever conversation was in
            # flight, which here is always the one it trails — see `_attach_orphans`.
            orphans.append(call)
            continue
        grouped.setdefault(conversation_key(messages), []).append((call, messages))

    built = [
        _walk(session_id, key, items) for key, items in grouped.items() if items
    ]
    built = _attach_orphans(built, orphans)
    built.sort(key=lambda c: (-c.depth, -c.calls, c.key))
    conversations = tuple(
        _as_main(conversation, index == 0) for index, conversation in enumerate(built)
    )
    return Reconstruction(session_id, conversations, tuple(days_passed))


def _messages_of(call: CapturedCall) -> list[dict[str, Any]] | None:
    """A call's `messages`, normalised — or `None` when there is no body or no array to read."""
    if call.request is None:
        return None
    try:
        payload = json.loads(call.request)
    except (ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    messages = payload.get("messages")
    if not isinstance(messages, list) or not messages:
        return None
    return [normalise(m) for m in messages if isinstance(m, Mapping)]


def _walk(
    session_id: str,
    key: str,
    items: Sequence[tuple[CapturedCall, list[dict[str, Any]]]],
) -> Conversation:
    """One conversation, from its calls in order.

    **The turns are the conversation's latest state, not its first.** Because a request's tail is
    provisional, a turn emitted when first seen can be one the client retracted a call later. Taking
    the newest array each time cannot emit a retraction, and the count of positions that changed
    under us is reported as `revised` rather than being quietly right.
    """
    spine: list[dict[str, Any]] = []
    first_seen: dict[int, str] = {}
    replies: dict[int, tuple[Reply, str]] = {}
    confirmed = 0
    revised = 0
    shrank = 0
    skipped: Counter[str] = Counter()

    for call, messages in items:
        for position in range(len(messages)):
            if position < len(spine):
                if _key(spine[position]) != _key(messages[position]):
                    revised += 1
                    first_seen[position] = call.timestamp
            else:
                first_seen[position] = call.timestamp
        common = _common_prefix(spine, messages)
        confirmed = max(confirmed, common)
        if len(messages) < len(spine):
            # Never observed: 678 pairs grew, 143 held their length, none shrank. Counted rather
            # than assumed away, because the day it happens the client dropped turns and a silent
            # reconstruction would present the remainder as the whole conversation.
            shrank += 1
        spine = messages
        _record_reply(call, len(messages), replies, skipped)

    entries = _entries(spine, first_seen, replies, skipped)
    return Conversation(
        session_id=session_id,
        key=key,
        main=False,
        entries=tuple(entries),
        calls=len(items),
        depth=len(spine),
        unconfirmed=max(0, len(spine) - confirmed),
        revised=revised,
        shrank=shrank,
        skipped=dict(skipped),
    )


def _record_reply(
    call: CapturedCall,
    position: int,
    replies: dict[int, tuple[Reply, str]],
    skipped: Counter[str],
) -> None:
    """The assistant turn a call produced, filed at the position it will occupy.

    A reply to a request of *N* messages becomes message *N* of the next request, so the array
    length at the time of the call **is** its position. A retry re-sends an identical request and
    lands on a position already taken — the first reply wins and the repeat is counted, so a
    byte-identical retry never invents a second turn.
    """
    if call.response is None:
        skipped[SKIP_EMPTY] += 1
        return
    outcome = reassemble(call.response)
    if not isinstance(outcome, Reply):
        skipped[outcome.reason] += 1
        return
    if position in replies:
        skipped["repeat"] += 1
        return
    replies[position] = (outcome, call.timestamp)


def _entries(
    spine: Sequence[dict[str, Any]],
    first_seen: Mapping[int, str],
    replies: Mapping[int, tuple[Reply, str]],
    skipped: Counter[str],
) -> list[Turn | Gap]:
    """The conversation's final state, with each assistant turn taken from its own response."""
    entries: list[Turn | Gap] = []
    for position, message in enumerate(spine):
        role = str(message.get("role", ""))
        reply = replies.get(position) if role == "assistant" else None
        timestamp = first_seen.get(position, "")
        if reply is not None:
            entries.append(Turn(position, role, reply[0].message, "response", timestamp))
        else:
            # An assistant turn with no usable response — its own call errored, and the only copy
            # is the one the next request carried back. Kept, and marked as the poorer source.
            entries.append(Turn(position, role, dict(message), "request", timestamp))
            if role == "assistant":
                skipped["assistant-from-request"] += 1
    tail = replies.get(len(spine))
    if tail is not None:
        # The last call's reply, which no request carries yet. Without this every conversation
        # would end one turn before it did. It carries its own call's timestamp: it is the only
        # turn with no position in any request, so nothing else would date it.
        entries.append(Turn(len(spine), "assistant", tail[0].message, "response", tail[1]))
    return entries


def _attach_orphans(
    built: list[Conversation],
    orphans: Sequence[CapturedCall],
) -> list[Conversation]:
    """Calls with no stored request body, appended to the conversation they trail.

    **They are kept, not dropped.** All 45 in the corpus reassemble into real assistant turns; only
    the prompts are gone. Each is written as a `Gap` followed by its reply, so the hole is visible
    and labelled rather than the transcript merely stopping 17% short of the session's end.
    """
    if not orphans or not built:
        return built
    host = max(built, key=lambda c: (c.depth, c.calls))
    entries = list(host.entries)
    # **After the last entry, not after the last message.** The final call's reply already occupies
    # position `depth` — it is the one turn that no request carries — so starting the gaps there
    # collides with it. Task 13 caught this on the live corpus as a duplicate `uuid5`, one in 1,615
    # records, because ids are derived from the position and nothing else compares them.
    #
    # **No `default=`, deliberately.** A host conversation is chosen from `built`, and one only
    # exists because a call carried at least one message, so `entries` is never empty. The default
    # that used to sit here was unreachable — a survivor of the 2026-08-28 sweep — and an
    # unreachable fallback is worse than none: if the invariant ever breaks, `max` raising beats a
    # silently wrong position, which is exactly what produced the duplicate id above.
    position = max(entry.position for entry in entries) + 1
    skipped = Counter(host.skipped)
    for call in orphans:
        entries.append(Gap(position, GAP_NO_REQUEST_BODY, call.timestamp))
        position += 1
        reply: dict[int, tuple[Reply, str]] = {}
        _record_reply(call, position, reply, skipped)
        if position in reply:
            entries.append(
                Turn(position, "assistant", reply[position][0].message, "response", call.timestamp)
            )
            position += 1
    replaced = Conversation(
        session_id=host.session_id,
        key=host.key,
        main=host.main,
        entries=tuple(entries),
        calls=host.calls + len(orphans),
        depth=position,
        unconfirmed=host.unconfirmed + len(orphans),
        revised=host.revised,
        shrank=host.shrank,
        skipped=dict(skipped),
    )
    return [replaced if c is host else c for c in built]


def _as_main(conversation: Conversation, main: bool) -> Conversation:
    """The deepest conversation gets the session's own filename; the rest get a digest suffix.

    **Depth, not call count.** Both pick the same conversation in all nine sessions here and there
    are no ties, but the margins are not comparable: 111 messages against 2, where the call counts
    are 58 against 45. A chatty classifier could outnumber a short real session's calls; it cannot
    out-deepen it.
    """
    if conversation.main == main:
        return conversation
    return Conversation(
        session_id=conversation.session_id,
        key=conversation.key,
        main=main,
        entries=conversation.entries,
        calls=conversation.calls,
        depth=conversation.depth,
        unconfirmed=conversation.unconfirmed,
        revised=conversation.revised,
        shrank=conversation.shrank,
        skipped=conversation.skipped,
    )


def _common_prefix(left: Sequence[Any], right: Sequence[Any]) -> int:
    """How many leading messages two calls agree on, once both are normalised."""
    count = 0
    for first, second in zip(left, right):
        if _key(first) != _key(second):
            break
        count += 1
    return count
