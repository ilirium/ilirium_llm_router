"""Reading a captured reply back into the message it was — Phase 11 task 11.

**These fixtures carry weight the corpus cannot.** The live corpus holds **one** buffered assistant
reply and **no** SSE `error` event at all, so those two paths are exercised here or nowhere. The
opposite is also true and is why this file is not the evidence on its own: `reassemble` was driven
over **all 953 response blobs** in the live corpus, and its verdict agreed with the index's
independently recorded `error_status` on all 979 rows. → `notes.md`, task 11.
"""

from __future__ import annotations

import json

import pytest

from ilirium_llm_router.transcript import (
    CONVERSATION_KEY_CHARS,
    GAP_NO_REQUEST_BODY,
    SKIP_EMPTY,
    SKIP_ERROR,
    SKIP_INCOMPLETE,
    SKIP_MALFORMED,
    SKIP_NOT_A_MESSAGE,
    SKIP_STREAM_ERROR,
    SSE_EVENTS,
    CapturedCall,
    Gap,
    MissingDayError,
    NotAMessage,
    Reply,
    Turn,
    conversation_key,
    normalise,
    reassemble,
    reconstruct,
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


def test_the_six_skip_reasons_have_the_spellings_the_register_names() -> None:
    """**Pinned to literals on purpose.** Every other assertion here compares a reason to its own
    constant, which cannot detect the constant changing — six mutants survived the 2026-08-28 sweep
    for exactly that reason. These strings are reported in-band to a reader of a transcript, so
    their spelling is a contract rather than an implementation detail."""
    assert SKIP_EMPTY == "empty"
    assert SKIP_ERROR == "error"
    assert SKIP_STREAM_ERROR == "stream-error"
    assert SKIP_NOT_A_MESSAGE == "not-a-message"
    assert SKIP_MALFORMED == "malformed"
    assert SKIP_INCOMPLETE == "incomplete"


def test_the_eight_sse_event_names_are_the_ones_that_were_observed() -> None:
    """**`SSE_EVENTS` is documentation, not a guard, and the sweep is how that became explicit.**
    Eight mutants survived because nothing in `src/` reads it: `_events` takes each payload's own
    `type` and ignores the `event:` line entirely. It is kept because the eight are *measured* — and
    pinned here so the record cannot rot unnoticed."""
    assert SSE_EVENTS == (
        "message_start",
        "content_block_start",
        "content_block_delta",
        "content_block_stop",
        "message_delta",
        "message_stop",
        "ping",
        "error",
    )


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


# --- delta reconstruction, task 12 ----------------------------------------------------------------
#
# **These fixtures carry the cases the corpus cannot make on demand**, not the ones it proves. The
# live corpus has exactly one cross-day session and never shrinks a conversation, so the missing-day
# error and the shrink counter are exercised here or nowhere. What the corpus *does* prove — 902
# calls in, 902 out, 36 conversations, 45 gaps, 0 shrinks — is in `notes-group-c.md`.


def call(
    timestamp: str,
    messages: list[dict] | None,
    reply: str | None = None,
    day: str = "2026-08-25",
) -> CapturedCall:
    """One captured call. `messages=None` is a body that was never stored — the `too_large` case."""
    request = None if messages is None else json.dumps({"messages": messages}).encode()
    response = None if reply is None else text_stream(reply)
    return CapturedCall(timestamp=timestamp, day=day, request=request, response=response)


def user(text: str) -> dict:
    return {"role": "user", "content": [{"type": "text", "text": text}]}


def assistant(text: str) -> dict:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def roles(conversation) -> list[str]:
    return [e.role if isinstance(e, Turn) else "gap" for e in conversation.entries]


def texts(conversation) -> list[str]:
    out = []
    for entry in conversation.entries:
        if isinstance(entry, Turn):
            blocks = entry.message.get("content") or []
            out.append("".join(b.get("text", "") for b in blocks if isinstance(b, dict)))
    return out


# --- the two normalisations -----------------------------------------------------------------------


def test_a_cache_control_marker_is_stripped_wherever_it_sits() -> None:
    marked = {
        "role": "user",
        "content": [{"type": "text", "text": "hi", "cache_control": {"type": "ephemeral"}}],
        "cache_control": {"type": "ephemeral"},
    }
    assert normalise(marked) == user("hi")


def test_a_bare_string_content_becomes_one_text_block() -> None:
    assert normalise({"role": "user", "content": "hi"}) == user("hi")


def test_the_two_encodings_of_one_message_key_the_same_conversation() -> None:
    """The real corpus sends a session's opening message as a string, then as blocks."""
    assert conversation_key([{"role": "user", "content": "hi"}]) == conversation_key([user("hi")])


def test_a_marker_that_migrated_does_not_split_a_conversation() -> None:
    """Claude Code marks the *last* message, so the marker walks forward as the session grows."""
    plain = user("hi")
    marked = {
        "role": "user",
        "content": [{"type": "text", "text": "hi", "cache_control": {"type": "ephemeral"}}],
    }
    result = reconstruct(
        [call("T1", [marked], "one"), call("T2", [plain, assistant("one"), user("two")], "two")],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert len(result.conversations) == 1


# --- conversations inside one session -------------------------------------------------------------


def test_a_session_holding_two_conversations_yields_two_files() -> None:
    """A probe sharing the `session_id` is a separate conversation, not a turn in this one."""
    result = reconstruct(
        [
            call("T1", [user("real")], "a"),
            call("T2", [user("probe")], "p"),
            call("T3", [user("real"), assistant("a"), user("more")], "b"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert len(result.conversations) == 2
    main, other = result.conversations
    assert main.main and not other.main
    assert main.filename() == "s1.jsonl"
    assert other.filename().startswith("s1-") and other.filename().endswith(".jsonl")
    assert "probe" not in texts(main)


def test_the_deepest_conversation_is_the_main_one_even_with_fewer_calls() -> None:
    """Depth, not call count — a classifier can out-call a real session, not out-deepen it."""
    deep = [user("deep"), assistant("a"), user("x")]
    calls = [call("T0", [user("deep")], "a"), call("T1", deep, "b")]
    calls += [call(f"T{i + 2}", [user("shallow")], "s") for i in range(8)]
    result = reconstruct(calls, "s1", days_passed=["2026-08-25"])
    main = result.conversations[0]
    assert main.calls == 2 and main.depth == 3
    assert result.conversations[1].calls == 8


def test_a_conversation_key_is_eight_characters_of_the_root_digest() -> None:
    """**The literal, not the constant.** `len(key) == CONVERSATION_KEY_CHARS` compares the code to
    itself and cannot fail — the mutation sweep proved it by changing 8 to 9 and surviving. A name
    that goes on disk is a contract, and a contract is pinned to its value."""
    key = conversation_key([user("hi")])
    assert len(key) == 8
    assert CONVERSATION_KEY_CHARS == 8
    assert all(c in "0123456789abcdef" for c in key)


# --- ordering across day folders ------------------------------------------------------------------


def test_calls_are_walked_in_timestamp_order_across_day_folders() -> None:
    """The index is in *completion* order, so file order is not the conversation's order."""
    grown = [user("one"), assistant("a"), user("two")]
    late = call("2026-08-26T09:00:00Z", grown, "b", "2026-08-26")
    early = call("2026-08-25T23:00:00Z", [user("one")], "a", "2026-08-25")
    result = reconstruct([late, early], "s1", days_passed=["2026-08-25", "2026-08-26"])
    main = result.conversations[0]
    assert texts(main)[:3] == ["one", "a", "two"]
    assert main.entries[0].timestamp == "2026-08-25T23:00:00Z"


def test_a_session_with_calls_in_a_folder_that_was_not_passed_is_an_error() -> None:
    """The whole defence. Without it the transcript is plausible and wrong about when."""
    with pytest.raises(MissingDayError) as raised:
        reconstruct(
            [call("T1", [user("one")], "a", "2026-08-26")],
            "s1",
            days_passed=["2026-08-26"],
            session_days=["2026-08-25", "2026-08-26"],
        )
    assert "2026-08-25" in str(raised.value)


def test_the_error_names_every_missing_day_not_just_the_first() -> None:
    with pytest.raises(MissingDayError) as raised:
        reconstruct(
            [call("T1", [user("one")], "a", "2026-08-26")],
            "s1",
            days_passed=["2026-08-26"],
            session_days=["2026-08-21", "2026-08-24", "2026-08-26"],
        )
    assert "2026-08-21" in str(raised.value) and "2026-08-24" in str(raised.value)


def test_a_call_from_a_day_that_was_not_passed_is_an_error() -> None:
    with pytest.raises(MissingDayError):
        stray = call("T1", [user("one")], "a", "2026-08-21")
        reconstruct([stray], "s1", days_passed=["2026-08-26"])


def test_passing_every_day_the_session_touches_is_not_an_error() -> None:
    result = reconstruct(
        [call("T1", [user("one")], "a", "2026-08-26")],
        "s1",
        days_passed=["2026-08-25", "2026-08-26"],
        session_days=["2026-08-26"],
    )
    assert result.conversations[0].depth == 1


# --- what the walk must not do --------------------------------------------------------------------


def test_a_retracted_turn_never_reaches_the_transcript() -> None:
    """100 times in the corpus a message was revised by the next call, 9 changing role."""
    result = reconstruct(
        [
            call("T1", [user("one")], "a"),
            call("T2", [user("one"), assistant("a"), user("typed then withdrawn")], "b"),
            call("T3", [user("one"), assistant("a"), user("what was really sent")], "c"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    main = result.conversations[0]
    assert "typed then withdrawn" not in texts(main)
    assert "what was really sent" in texts(main)
    assert main.revised == 1


def test_a_byte_identical_retry_does_not_invent_a_second_turn() -> None:
    """Finding 17 — retries produce byte-identical consecutive requests."""
    once = [user("one")]
    result = reconstruct(
        [call("T1", once, "a"), call("T2", list(once), "a"), call("T3", list(once), "a")],
        "s1",
        days_passed=["2026-08-25"],
    )
    main = result.conversations[0]
    assert roles(main) == ["user", "assistant"]
    assert main.skipped["repeat"] == 2


def test_an_assistant_turn_is_taken_from_its_response_not_the_next_request() -> None:
    """The response carries `caller` on `tool_use` blocks; the request never does."""
    result = reconstruct(
        [
            call("T1", [user("one")], "from the response"),
            call("T2", [user("one"), assistant("from the request"), user("two")], "b"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    main = result.conversations[0]
    assert texts(main)[1] == "from the response"
    assert main.entries[1].source == "response"


def test_an_assistant_turn_whose_own_response_failed_falls_back_to_the_request() -> None:
    result = reconstruct(
        [
            call("T1", [user("one")], None),
            call("T2", [user("one"), assistant("recovered"), user("two")], "b"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    main = result.conversations[0]
    assert texts(main)[1] == "recovered"
    assert main.entries[1].source == "request"
    assert main.skipped["assistant-from-request"] == 1


def test_the_last_calls_reply_is_kept_though_no_request_carries_it() -> None:
    last = call("T1", [user("one")], "the last word")
    result = reconstruct([last], "s1", days_passed=["2026-08-25"])
    main = result.conversations[0]
    assert texts(main) == ["one", "the last word"]


def test_a_system_role_inside_messages_is_carried_as_itself() -> None:
    """Finding 5 — `messages` has a third role, and on 14 calls it is the last message."""
    result = reconstruct(
        [
            call("T1", [user("one"), {"role": "system", "content": "note"}], "a"),
            call("T2", [user("one"), {"role": "system", "content": "note"}, assistant("a")], "b"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert roles(result.conversations[0])[:3] == ["user", "system", "assistant"]


# --- the bodiless tail ----------------------------------------------------------------------------


def test_a_call_with_no_stored_request_body_becomes_a_visible_gap() -> None:
    """Finding 1 — 45 contiguous calls at the end of the largest session, all with real replies."""
    result = reconstruct(
        [
            call("T1", [user("one")], "a"),
            call("T2", None, "reply with no prompt"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    main = result.conversations[0]
    assert roles(main) == ["user", "assistant", "gap", "assistant"]
    assert "reply with no prompt" in texts(main)
    gap = main.entries[2]
    assert isinstance(gap, Gap) and gap.reason == "no-request-body"
    assert GAP_NO_REQUEST_BODY == "no-request-body"


def test_a_bodiless_call_is_still_counted_as_a_call() -> None:
    result = reconstruct(
        [call("T1", [user("one")], "a"), call("T2", None, "b"), call("T3", None, "c")],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].calls == 3


# --- the facts a reader needs to distrust the file ------------------------------------------------


def test_the_unconfirmed_tail_is_counted_rather_than_hidden() -> None:
    """No later call agrees with the final one, so its turns are reported as unconfirmed."""
    result = reconstruct(
        [call("T1", [user("one")], "a"), call("T2", [user("one"), assistant("a"), user("x")], "b")],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].unconfirmed == 2


def test_a_conversation_that_loses_turns_is_counted_rather_than_silently_shortened() -> None:
    """Never seen — 678 grew, 143 held, none shrank. Counted so the day it happens shows."""
    result = reconstruct(
        [
            call("T1", [user("one"), assistant("a"), user("two")], "b"),
            call("T2", [user("one")], "c"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].shrank == 1


def test_a_request_whose_messages_are_empty_is_not_a_conversation() -> None:
    """`not isinstance(messages, list) or not messages` -> `and` survived the sweep. With `and`, an
    empty list reaches `conversation_key`, which indexes `messages[0]`."""
    empty = CapturedCall(timestamp="T1", day="2026-08-25",
                         request=b'{"messages": []}', response=None)
    result = reconstruct([empty], "s1", days_passed=["2026-08-25"])
    assert result.conversations == ()


def test_a_request_whose_messages_are_not_a_list_is_not_a_conversation() -> None:
    odd = CapturedCall(timestamp="T1", day="2026-08-25",
                       request=b'{"messages": {"role": "user"}}', response=None)
    result = reconstruct([odd], "s1", days_passed=["2026-08-25"])
    assert result.conversations == ()


def test_a_conversation_that_only_ever_grew_is_not_counted_as_shrinking() -> None:
    """**The existing shrink test passed for the wrong reason.** `<` -> `>=` survived it: the first
    call compares against an empty spine, so the mutant counted 1 there and 0 later, reaching the
    same total by a different route. A conversation that never shrinks must read 0."""
    result = reconstruct(
        [
            call("T1", [user("one")], "a"),
            call("T2", [user("one"), assistant("a"), user("two")], "b"),
            call("T3", [user("one"), assistant("a"), user("two"), assistant("b")], "c"),
        ],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].shrank == 0


def test_gaps_count_towards_the_unconfirmed_tail() -> None:
    """`host.unconfirmed + len(orphans)` -> `-` survived. A bodiless call is unconfirmed by
    construction: nothing later can agree with a request that was never stored."""
    result = reconstruct(
        [call("T1", [user("one")], "a"), call("T2", None, "x"), call("T3", None, "y")],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].unconfirmed == 3


def test_a_stream_with_no_event_lines_is_still_read() -> None:
    """**The module claims to ignore the `event:` line and the sweep showed it depends on one.**
    `not line.strip()` -> `line.strip()` survived every existing test, because each `event:` line
    happened to flush the previous payload. SSE permits a stream of bare `data:` lines, and this is
    the only test that sends one."""
    body = (
        b'data: {"type":"message_start","message":{"id":"m","type":"message","role":"assistant",'
        b'"model":"claude-opus-5","content":[],"usage":{"input_tokens":1}}}\n\n'
        b'data: {"type":"content_block_start","index":0,'
        b'"content_block":{"type":"text","text":""}}\n\n'
        b'data: {"type":"content_block_delta","index":0,'
        b'"delta":{"type":"text_delta","text":"hi"}}\n\n'
        b'data: {"type":"content_block_stop","index":0}\n\n'
        b'data: {"type":"message_stop"}\n\n'
    )
    got = reassemble(body)
    assert isinstance(got, Reply)
    assert got.message["content"][0]["text"] == "hi"


def test_a_call_with_no_response_is_counted_as_an_empty_skip() -> None:
    """`skipped[SKIP_EMPTY] += 1` -> `+= 2` survived: nothing read that counter back."""
    result = reconstruct(
        [call("T1", [user("one")], None), call("T2", [user("one")], None)],
        "s1",
        days_passed=["2026-08-25"],
    )
    assert result.conversations[0].skipped["empty"] == 2


def test_reconstruction_is_deterministic() -> None:
    """Task 13 tests this on bytes; here it is the walk itself that must not wander."""
    calls = [
        call("T1", [user("one")], "a"),
        call("T2", [user("probe")], "p"),
        call("T3", [user("one"), assistant("a"), user("two")], "b"),
    ]
    first = reconstruct(calls, "s1", days_passed=["2026-08-25"])
    second = reconstruct(calls, "s1", days_passed=["2026-08-25"])
    def names(result) -> list[str]:
        return [c.filename() for c in result.conversations]

    assert names(first) == names(second)
    assert [texts(c) for c in first.conversations] == [texts(c) for c in second.conversations]
