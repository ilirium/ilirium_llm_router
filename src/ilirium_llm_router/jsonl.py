"""The record shapes the viewer will accept — Phase 11 task 13.

**This is somebody else's schema and it will move when their tool moves.** That is the whole reason
it is a file of its own: `transcript.py` answers *what was said*, and nothing in it should change
because a desktop app renamed a field.

**Settled from two sources, per position 17** — the viewer's own source, and **one** real
session file read only far enough to learn field names. *Reading a schema at design time is not
the converter reading `~/.claude/` at runtime; the second is what "oracle, never input" forbids,
and nothing here opens that directory.*

Four things the sources settled that guesswork would have got wrong:

* **A session is identified by its *filename*, not by `sessionId`.** The loader sets
  `session_id: file_path_str` and two files carrying the same `sessionId` are **not merged**. This
  is what makes task 12's one-file-per-conversation split safe, and it is the answer to the question
  that task left open — `sessionId` stays verbatim in every file.
* **Only four record types carry `uuid`/`parentUuid`** — `user`, `assistant`, `system` and
  `attachment`. The other six in a real file (`mode`, `permission-mode`, `ai-title`, `last-prompt`,
  `file-history-snapshot`, `file-history-delta`) are session-level sidecars outside the chain.
* **A `system` record is shown unless its subtype is hidden**, and the hidden list has exactly two
  entries — `stop_hook_summary` and `turn_duration`. So a subtype of our own renders, and it is
  machine-distinguishable from the three real ones (`turn_duration`, `away_summary`,
  `local_command`).
* **`type` is the only field the loader strictly requires**; `message` needs `role` and `content`.
  Everything else is optional, so the fields the corpus cannot supply are simply absent rather than
  faked.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterable, Sequence
from typing import Any

from .transcript import Conversation, Gap, Turn

# **Minted, not borrowed.** A namespace of our own means these ids cannot collide with anyone
# else's `uuid5` values, and the same corpus produces the same file forever, on any machine.
SYNTHETIC_UUID_NAMESPACE = uuid.UUID("5791f885-4f45-4b01-bbd1-5ac2631bf167")

# One bucket. `corpus-<day>` was proposed and killed by finding 5: a session spanning two days has
# no single day to file under.
PROJECT_NAME_DEFAULT = "corpus"

# **The fidelity marker's subtype, and the reason it is not a plain `system` record.** A `system`
# role occurs *inside* `messages` and reaches the transcript, so a bare `system` record announcing
# *"this is not a real record"* could not be told from a real turn. A subtype settles it both ways:
# the viewer shows it (the hidden list is `stop_hook_summary` and `turn_duration`), and a reader —
# human or machine — can see which records the tool authored.
SCHEMA_NOTE_SUBTYPE = "corpus-reconstruction"
GAP_SUBTYPE = "corpus-gap"

# The five the corpus cannot supply, named in the note rather than left to be noticed. Four are
# client state that never crossed the wire; the fifth is header-derived. **The store holds bodies
# only, and is attached to a tee of the body bytes that never sees a header at all.**
ABSENT_BY_CONSTRUCTION = ("cwd", "gitBranch", "version", "toolUseResult", "agent attribution")

JSONL_SCHEMA_NOTE = (
    "Reconstructed by ilirium-llm-router {version} from its own captured corpus on {generated}. "
    "This is NOT a Claude Code session record: it was rebuilt from the request and response bodies "
    "the router relayed, so it carries what crossed the wire and nothing else. "
    "Source: session {session}, day folder(s) {days}, {calls} call(s), of which {skipped} "
    "contributed no turn because the response was not a message. "
    "{gaps} call(s) have no stored request body and appear below as gaps — their replies are real, "
    "their prompts were never stored. "
    "{unconfirmed} trailing turn(s) were not confirmed by any later call. "
    "Absent by construction, never present in an API body: {absent}."
)


def record_uuid(session_id: str, key: str, slot: str) -> str:
    """A record's id, fixed forever by what it *is* rather than by when it was made.

    **The recipe changed at task 13 and the register says why.** It was
    `uuid5(NS, "<request-blob-digest>:<record-index-within-call>")`, which task 12's design cannot
    supply: a turn is taken from the conversation's latest state, so it belongs to no single call
    and has no one request blob. Conversation and position are what a turn actually has, and both
    are stable — the message array is append-only, so a position never shifts under a growing
    corpus.
    """
    return str(uuid.uuid5(SYNTHETIC_UUID_NAMESPACE, f"{session_id}:{key}:{slot}"))


def schema_note(
    conversation: Conversation,
    *,
    days: Sequence[str],
    version: str,
    generated: str,
) -> str:
    """The in-band fidelity note, settled against a sidecar.

    **A sidecar is not in-band.** The viewer is the only place these files get read and it would not
    show one, so a note that lives beside the file is a note nobody sees.
    """
    gaps = sum(1 for entry in conversation.entries if isinstance(entry, Gap))
    return JSONL_SCHEMA_NOTE.format(
        version=version,
        generated=generated,
        session=conversation.session_id,
        days=", ".join(days) or "none",
        calls=conversation.calls,
        skipped=sum(conversation.skipped.values()),
        gaps=gaps,
        unconfirmed=conversation.unconfirmed,
        absent=", ".join(ABSENT_BY_CONSTRUCTION),
    )


def records(
    conversation: Conversation,
    *,
    days: Sequence[str],
    version: str,
    generated: str,
) -> list[dict[str, Any]]:
    """One conversation as the viewer's records, chained through `parentUuid`.

    The chain is a straight line: every record's parent is the one before it, and the first record —
    the fidelity note — has `parentUuid: null`. **The note is first so that a reader meets it before
    anything that could be mistaken for a real transcript.**
    """
    out: list[dict[str, Any]] = []
    previous: str | None = None

    def emit(slot: str, timestamp: str, **fields: Any) -> None:
        nonlocal previous
        identifier = record_uuid(conversation.session_id, conversation.key, slot)
        record = {
            "parentUuid": previous,
            "isSidechain": False,
            "uuid": identifier,
            "sessionId": conversation.session_id,
            "timestamp": timestamp,
            **fields,
        }
        out.append(record)
        previous = identifier

    emit(
        "note",
        generated,
        type="system",
        subtype=SCHEMA_NOTE_SUBTYPE,
        isMeta=False,
        content=schema_note(conversation, days=days, version=version, generated=generated),
    )

    for entry in conversation.entries:
        if isinstance(entry, Gap):
            emit(
                str(entry.position),
                entry.timestamp,
                type="system",
                subtype=GAP_SUBTYPE,
                isMeta=False,
                content=(
                    "The request body for this call was never stored — it was over the corpus's "
                    "size cap and discarded rather than truncated. The reply that follows is real; "
                    "the turn that prompted it is not recoverable."
                ),
            )
            continue
        emit(
            str(entry.position),
            entry.timestamp,
            type="assistant" if entry.role == "assistant" else "user",
            message=_message(entry),
        )
    return out


def _message(turn: Turn) -> dict[str, Any]:
    """The `message` object, carrying `role` and `content` and whatever else survived the wire.

    **A `system` role is kept as itself inside a `user` record**, which is the honest shape: the
    viewer's record `type` describes the record, `message.role` describes the API role, and a
    `system` entry in `messages` is a *message* rather than one of the viewer's own UI notices.
    Flattening it to `"user"` would lose the distinction finding 5 exists to record.
    """
    message: dict[str, Any] = {
        "role": turn.message.get("role", turn.role),
        "content": turn.message.get("content", []),
    }
    for optional in ("id", "model", "stop_reason", "stop_sequence", "usage"):
        if optional in turn.message:
            message[optional] = turn.message[optional]
    return message


def render(records_in: Iterable[dict[str, Any]]) -> bytes:
    """JSON Lines, one record per line.

    `sort_keys` is deliberate and is what makes task 13's determinism test meaningful: without it
    two runs could differ on key order alone and the diff would say nothing about the content.
    """
    lines = [json.dumps(record, sort_keys=True, ensure_ascii=False) for record in records_in]
    return ("\n".join(lines) + "\n").encode("utf-8")
