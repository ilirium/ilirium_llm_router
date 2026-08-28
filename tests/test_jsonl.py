"""The record shapes the viewer will accept — Phase 11 task 13.

**These assertions are the viewer's rules, not our preferences**, and each one is traceable to the
source read on 2026-08-28: `type` is the only strictly required field, `message` needs `role` and
`content`, a `system` record is shown unless its subtype is one of the two hidden ones, and a
session is identified by its *filename* rather than by `sessionId`.

*The strongest check here is not a test either. Every conversation in the live corpus was emitted
and run against those rules — 1,615 records over 36 files — which is how the duplicate `uuid5` that
`test_a_gap_never_collides_with_the_last_reply` now guards was found. → `notes-group-c.md`.*
"""

from __future__ import annotations

import json

from ilirium_llm_router.jsonl import (
    GAP_SUBTYPE,
    SCHEMA_NOTE_SUBTYPE,
    SYNTHETIC_UUID_NAMESPACE,
    record_uuid,
    records,
    render,
    schema_note,
)
from ilirium_llm_router.transcript import CapturedCall, reconstruct

DAYS = ["2026-08-25"]
WHEN = "2026-08-28T00:00:00Z"

# Deliberately defined here rather than imported from `test_transcript.py`. `tests/` is not a
# package, and a test file that leans on another test file's fixtures breaks the moment either is
# reorganised — for a saving of nine lines.
REPLY = {
    "id": "msg_01",
    "type": "message",
    "role": "assistant",
    "model": "claude-opus-5",
    "content": [],
    "stop_reason": None,
    "usage": {"input_tokens": 7, "cache_read_input_tokens": 100, "output_tokens": 1},
}


def stream(text: str) -> bytes:
    events = [
        {"type": "message_start", "message": REPLY},
        {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "text_delta", "text": text}},
        {"type": "content_block_stop", "index": 0},
        {"type": "message_stop"},
    ]
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()


def user(text: str) -> dict:
    return {"role": "user", "content": [{"type": "text", "text": text}]}


def assistant(text: str) -> dict:
    return {"role": "assistant", "content": [{"type": "text", "text": text}]}


def call(timestamp: str, messages: list[dict] | None, reply: str | None) -> CapturedCall:
    request = None if messages is None else json.dumps({"messages": messages}).encode()
    return CapturedCall(
        timestamp=timestamp,
        day="2026-08-25",
        request=request,
        response=None if reply is None else stream(reply),
    )


def convert(calls: list[CapturedCall], session: str = "s1") -> list[dict]:
    result = reconstruct(calls, session, days_passed=DAYS)
    return records(result.conversations[0], days=DAYS, version="9.9.9", generated=WHEN)


def simple() -> list[dict]:
    return convert(
        [
            call("T1", [user("one")], "a"),
            call("T2", [user("one"), assistant("a"), user("two")], "b"),
        ]
    )


# --- the chain ------------------------------------------------------------------------------------


def test_the_first_record_is_the_fidelity_note_and_opens_the_chain() -> None:
    """It is first so a reader meets it before anything mistakable for a real transcript."""
    first = simple()[0]
    assert first["parentUuid"] is None
    assert first["type"] == "system"
    assert first["subtype"] == SCHEMA_NOTE_SUBTYPE


def test_every_record_names_the_one_before_it() -> None:
    out = simple()
    parents = [r["parentUuid"] for r in out[1:]]
    assert parents == [r["uuid"] for r in out[:-1]]


def test_every_record_carries_the_fields_the_loader_requires() -> None:
    """`type` is the only strictly required field; the loader drops a record with neither
    `sessionId` nor `timestamp`."""
    for record in simple():
        assert record["type"]
        assert record["sessionId"] == "s1"
        assert record["timestamp"]


def test_a_message_record_carries_role_and_content() -> None:
    for record in simple():
        if record["type"] in ("user", "assistant"):
            assert "role" in record["message"] and "content" in record["message"]


# --- identity -------------------------------------------------------------------------------------


def test_a_record_id_is_the_same_on_any_machine_forever() -> None:
    assert record_uuid("s1", "abcd1234", "7") == record_uuid("s1", "abcd1234", "7")
    assert str(SYNTHETIC_UUID_NAMESPACE) == "5791f885-4f45-4b01-bbd1-5ac2631bf167"


def test_ids_differ_by_slot_by_conversation_and_by_session() -> None:
    base = record_uuid("s1", "abcd1234", "7")
    assert base != record_uuid("s1", "abcd1234", "8")
    assert base != record_uuid("s1", "ffff0000", "7")
    assert base != record_uuid("s2", "abcd1234", "7")


def test_every_id_in_a_file_is_distinct() -> None:
    out = simple()
    assert len({r["uuid"] for r in out}) == len(out)


def test_a_gap_never_collides_with_the_last_reply() -> None:
    """The final call's reply sits at `depth` — the one turn no request carries — so gaps that
    started numbering there produced a duplicate `uuid5`. Found on the live corpus, not here."""
    out = convert(
        [
            call("T1", [user("one")], "a"),
            call("T2", None, "reply with no prompt"),
            call("T3", None, "another"),
        ]
    )
    assert len({r["uuid"] for r in out}) == len(out)
    assert sum(1 for r in out if r.get("subtype") == GAP_SUBTYPE) == 2


# --- what the records say -------------------------------------------------------------------------


def test_a_gap_is_a_visible_system_record_not_a_hidden_one() -> None:
    """`HIDDEN_SYSTEM_SUBTYPES` is exactly `stop_hook_summary` and `turn_duration`."""
    out = convert([call("T1", [user("one")], "a"), call("T2", None, "orphan")])
    gap = next(r for r in out if r.get("subtype") == GAP_SUBTYPE)
    assert gap["subtype"] not in ("stop_hook_summary", "turn_duration")
    assert gap["isMeta"] is False
    assert "never stored" in gap["content"]


def test_the_marker_is_not_a_plain_system_record() -> None:
    """A `system` role occurs inside `messages`, so a bare `system` record could not be told from
    a real turn. The subtype is what separates them."""
    note = simple()[0]
    assert note["subtype"] == SCHEMA_NOTE_SUBTYPE
    assert note["subtype"] not in ("turn_duration", "away_summary", "local_command")


def test_a_system_role_inside_messages_keeps_its_role() -> None:
    """Finding 5. The record type describes the record; `message.role` describes the API role."""
    out = convert(
        [
            call("T1", [user("one"), {"role": "system", "content": "note"}], "a"),
            call("T2", [user("one"), {"role": "system", "content": "note"}, assistant("a")], "b"),
        ]
    )
    roles = [r["message"]["role"] for r in out if "message" in r]
    assert "system" in roles
    carrier = next(r for r in out if r.get("message", {}).get("role") == "system")
    assert carrier["type"] == "user"


def test_an_assistant_record_keeps_what_the_wire_carried() -> None:
    out = simple()
    reply = next(r for r in out if r["type"] == "assistant")
    assert reply["message"]["role"] == "assistant"
    assert reply["message"]["model"] == "claude-opus-5"
    assert reply["message"]["usage"]["input_tokens"] == 7


def test_the_note_names_everything_the_register_requires() -> None:
    result = reconstruct(
        [call("T1", [user("one")], "a"), call("T2", None, "orphan")], "s1", days_passed=DAYS
    )
    note = schema_note(result.conversations[0], days=DAYS, version="9.9.9", generated=WHEN)
    for required in ("9.9.9", WHEN, "s1", "2026-08-25", "cwd", "gitBranch", "version",
                     "toolUseResult", "agent attribution", "NOT a Claude Code session record"):
        assert required in note


# --- the bytes ------------------------------------------------------------------------------------


def test_render_is_one_json_object_per_line() -> None:
    blob = render(simple())
    lines = blob.decode().splitlines()
    assert len(lines) == len(simple())
    assert all(json.loads(line)["sessionId"] == "s1" for line in lines)
    assert blob.endswith(b"\n")


def test_converting_twice_produces_identical_bytes() -> None:
    """Determinism is a test, not an aspiration — the task says so in those words."""
    assert render(simple()) == render(simple())


def test_key_order_cannot_make_two_runs_differ() -> None:
    line = render(simple()).decode().splitlines()[0]
    assert list(json.loads(line)) == sorted(json.loads(line))
