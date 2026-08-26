"""Reading a captured reply back into the message it was — Phase 11 task 11.

**These fixtures carry weight the corpus cannot.** The live corpus holds **one** buffered assistant
reply and **no** SSE `error` event at all, so those two paths are exercised here or nowhere. The
opposite is also true and is why this file is not the evidence on its own: `reassemble` was driven
over **all 953 response blobs** in the live corpus, and its verdict agreed with the index's
independently recorded `error_status` on all 979 rows. → `notes.md`, task 11.
"""

from __future__ import annotations

import json

from ilirium_llm_router.transcript import (
    SKIP_EMPTY,
    SKIP_ERROR,
    SKIP_INCOMPLETE,
    SKIP_MALFORMED,
    SKIP_NOT_A_MESSAGE,
    SKIP_STREAM_ERROR,
    NotAMessage,
    Reply,
    reassemble,
)

START = {
    "type": "message_start",
    "message": {
        "id": "msg_01",
        "type": "message",
        "role": "assistant",
        "model": "claude-opus-5",
        "content": [],
        "stop_reason": None,
        "usage": {"input_tokens": 7, "cache_read_input_tokens": 100, "output_tokens": 1},
    },
}
STOP = {"type": "message_stop"}


def sse(*events: dict) -> bytes:
    """The wire format as the router relays it — `event:`, `data:`, and a blank line."""
    out = []
    for event in events:
        out.append(f"event: {event['type']}\ndata: {json.dumps(event)}\n\n")
    return "".join(out).encode("utf-8")


def text_stream(*chunks: str) -> bytes:
    return sse(
        START,
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        *({"type": "content_block_delta", "index": 0,
           "delta": {"type": "text_delta", "text": chunk}} for chunk in chunks),
        {"type": "content_block_stop", "index": 0},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn"},
         "usage": {"output_tokens": 42}},
        STOP,
    )


# --- the streamed path ---------------------------------------------------------------------------


def test_a_streamed_text_reply_is_reassembled_whole() -> None:
    got = reassemble(text_stream("Hel", "lo, ", "world"))
    assert isinstance(got, Reply)
    assert got.streamed is True
    assert got.message["content"] == [{"type": "text", "text": "Hello, world"}]
    assert got.message["stop_reason"] == "end_turn"


def test_usage_is_merged_across_the_two_ends_of_the_stream() -> None:
    """`message_start` carries the input counts and `message_delta` the output one. A replace rather
    than a merge would drop `input_tokens` and both cache counters on **every** call — and the row
    would still look plausible, which is what makes it worth a test."""
    got = reassemble(text_stream("hi"))
    assert isinstance(got, Reply)
    assert got.message["usage"] == {
        "input_tokens": 7,
        "cache_read_input_tokens": 100,
        "output_tokens": 42,
    }


def test_a_ping_carries_nothing_and_is_ignored() -> None:
    """648 of them across two days. A reassembler that treated an unrecognised event as a failure
    would reject every stream Anthropic sends."""
    with_ping = sse(
        START,
        {"type": "ping"},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "ping"},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "text_delta", "text": "ok"}},
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(with_ping)
    assert isinstance(got, Reply)
    assert got.message["content"] == [{"type": "text", "text": "ok"}]


def test_a_tool_input_arrives_as_json_fragments_and_is_parsed_once() -> None:
    """**The one piece of real work in reassembly.** A tool's input arrives as `input_json_delta`
    string fragments — 64,260 across two days against 2,071 `text_delta` — concatenated and parsed
    *after* the block closes. Parsing each fragment would fail on all but the last."""
    stream = sse(
        START,
        {"type": "content_block_start", "index": 0,
         "content_block": {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {}}},
        *({"type": "content_block_delta", "index": 0,
           "delta": {"type": "input_json_delta", "partial_json": part}}
          for part in ('{"file', '_path": "/a', '/b.py"}')),
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(stream)
    assert isinstance(got, Reply)
    assert got.message["content"][0]["input"] == {"file_path": "/a/b.py"}


def test_a_tool_taking_no_arguments_yields_an_empty_object() -> None:
    """`content_block_start` then `content_block_stop` with nothing between them is a **valid
    call**, not a broken one — and `json.loads("")` would raise."""
    stream = sse(
        START,
        {"type": "content_block_start", "index": 0,
         "content_block": {"type": "tool_use", "id": "tu_1", "name": "Now", "input": {}}},
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(stream)
    assert isinstance(got, Reply)
    assert got.message["content"][0]["input"] == {}


def test_an_unparseable_tool_input_is_kept_as_the_string_it_was() -> None:
    """A tool input that did not parse is a fact about the capture. Dropping it silently helps
    nobody, and raising would stop the run at the first interesting row."""
    stream = sse(
        START,
        {"type": "content_block_start", "index": 0,
         "content_block": {"type": "tool_use", "id": "tu_1", "name": "Read", "input": {}}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "input_json_delta", "partial_json": '{"truncated'}},
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(stream)
    assert isinstance(got, Reply)
    assert got.message["content"][0]["input"] == '{"truncated'


def test_thinking_and_its_signature_both_accumulate() -> None:
    """461 thinking blocks in the corpus, each with exactly one `signature_delta`. The plan's model
    of a reply had one block type; the wire has five."""
    stream = sse(
        START,
        {"type": "content_block_start", "index": 0,
         "content_block": {"type": "thinking", "thinking": ""}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "thinking_delta", "thinking": "step one, "}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "thinking_delta", "thinking": "step two"}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "signature_delta", "signature": "sig123"}},
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(stream)
    assert isinstance(got, Reply)
    assert got.message["content"][0]["thinking"] == "step one, step two"
    assert got.message["content"][0]["signature"] == "sig123"


def test_blocks_come_back_in_index_order() -> None:
    """Ordered by the `index` the wire gives, not by arrival. Blocks can interleave, and a reply
    whose text and tool call swapped places would read as a different turn."""
    stream = sse(
        START,
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_start", "index": 1,
         "content_block": {"type": "tool_use", "id": "t", "name": "Read", "input": {}}},
        {"type": "content_block_delta", "index": 1,
         "delta": {"type": "input_json_delta", "partial_json": "{}"}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "text_delta", "text": "let me look"}},
        {"type": "content_block_stop", "index": 1},
        {"type": "content_block_stop", "index": 0},
        STOP,
    )
    got = reassemble(stream)
    assert isinstance(got, Reply)
    assert [block["type"] for block in got.message["content"]] == ["text", "tool_use"]


def test_a_data_field_split_over_several_lines_is_joined() -> None:
    """The SSE spec allows it. Anthropic does not do it today, and a reassembler that assumed so
    would break on the day it does — for a reason no capture would explain."""
    payload = json.dumps(START)
    half = len(payload) // 2
    body = (
        f"event: message_start\ndata: {payload[:half]}\ndata: {payload[half:]}\n\n"
        f"event: message_stop\ndata: {json.dumps(STOP)}\n\n"
    ).encode()
    got = reassemble(body)
    assert isinstance(got, Reply)
    assert got.message["id"] == "msg_01"


# --- streams that are not a turn -----------------------------------------------------------------


def test_a_stream_carrying_an_error_event_is_not_a_message() -> None:
    """**Not present in the live corpus at all** — seven occur in Phase 9's gate corpus. The
    router's one exception to byte-relay is ending a broken stream with an SSE `error` event, so
    this is how an upstream break presents, and whatever arrived before it is incomplete."""
    body = sse(
        START,
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "error", "error": {"type": "overloaded_error"}},
    )
    got = reassemble(body)
    assert isinstance(got, NotAMessage)
    assert (got.reason, got.streamed) == (SKIP_STREAM_ERROR, True)


def test_a_stream_that_simply_stops_is_incomplete_rather_than_an_error() -> None:
    """**One in the corpus, and it is the one `client_disconnect` row** — identified by joining the
    blob back to its index row. The caller went away, so no error was ever authored and the stream
    just ends mid-delta. Distinct from the case above, and the distinction is not academic: nothing
    went wrong upstream."""
    body = sse(
        START,
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "text_delta", "text": "you're plan"}},
    )
    got = reassemble(body)
    assert isinstance(got, NotAMessage)
    assert (got.reason, got.streamed) == (SKIP_INCOMPLETE, True)


def test_a_stream_with_no_message_start_is_not_a_message() -> None:
    body = sse({"type": "ping"}, STOP)
    got = reassemble(body)
    assert isinstance(got, NotAMessage)
    assert got.reason == SKIP_NOT_A_MESSAGE


# --- the buffered path, which one real call exercises --------------------------------------------


def test_a_buffered_reply_is_the_message_itself() -> None:
    """**The whole live corpus holds one of these.** It is built because a `stream=false` success is
    legal and position 15 filters nothing — and it is tested here because it is tested nowhere
    else."""
    body = json.dumps(
        {"type": "message", "role": "assistant", "content": [{"type": "text", "text": "hi"}],
         "stop_reason": "end_turn"}
    ).encode("utf-8")
    got = reassemble(body)
    assert isinstance(got, Reply)
    assert got.streamed is False
    assert got.message["content"] == [{"type": "text", "text": "hi"}]


def test_an_error_body_is_skipped_with_its_own_reason() -> None:
    """93 of these. Deferred by position 20 — skipped and counted, not converted."""
    body = b'{"type":"error","error":{"type":"rate_limit_error"},"request_id":"req_1"}'
    got = reassemble(body)
    assert isinstance(got, NotAMessage)
    assert (got.reason, got.streamed) == (SKIP_ERROR, False)


def test_a_count_tokens_reply_is_not_an_error_and_is_not_a_turn() -> None:
    """`{"input_tokens": N}`, 47 blobs. **The distinction from an error is deliberate**: position 20
    defers errors as *work*, while this is simply not a message and never will be."""
    got = reassemble(b'{"input_tokens":32502}')
    assert isinstance(got, NotAMessage)
    assert got.reason == SKIP_NOT_A_MESSAGE


def test_an_empty_body_is_skipped() -> None:
    """Four in the corpus — nine `ok` rows with zero-length bodies are router-authored replies."""
    for body in (b"", b"   ", b"\n"):
        got = reassemble(body)
        assert isinstance(got, NotAMessage)
        assert got.reason == SKIP_EMPTY


def test_a_malformed_body_never_raises() -> None:
    """A corpus records what happened, and what happened includes bodies that do not parse. A tool
    that threw here would stop at the first interesting row."""
    got = reassemble(b'{"type":"message", "content": [')
    assert isinstance(got, NotAMessage)
    assert got.reason == SKIP_MALFORMED


def test_a_json_scalar_is_malformed_rather_than_not_a_message() -> None:
    got = reassemble(b'{"a": 1}')
    assert isinstance(got, NotAMessage)
    assert got.reason == SKIP_NOT_A_MESSAGE
