"""Selection over an index, and the files it becomes — Phase 11 group D.

**The store never parses a body and this module never opens one it was not asked for.** Selection
happens entirely on the index, which is 26 columns of metadata; a blob is read only once a row has
been chosen.

**Matching is exact on every field** (position 18). `--path /v1/messages` does **not** sweep in
`/v1/messages/count_tokens`, because a filter that quietly matches more than it says is worse
than one that matches nothing — the second is visible. Repeated filters of one kind are **OR**,
different kinds are **AND**.

**One place this reads a folder it was not given, and it is deliberate.** A Claude Code session
is resumed the next morning under the same id, so one conversation lands in two day folders — the
corpus has such a session and it is 253 calls. Converting only the later folder produces a
transcript that is *complete* (requests are cumulative, so the last call carries everything) and
**wrong about when a quarter of it happened**: 26 turns misdated, and nothing in the file to say
so. To notice, this looks at the **`index.csv` of sibling day folders and nothing else** — never a
blob, never a dictionary, never a folder that is not a sibling of one it was given.

*`reference/corpus.md`'s self-containment guarantee is untouched by that: it promises a day
folder's **blobs open** standalone, which they still do. The plan's stronger phrasing — "the day
folders it is given and nothing above them" — is what gains a qualified exception, on the owner's
decision of 2026-08-28.*
"""

from __future__ import annotations

import csv
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

# `(day folder, blob path) -> plaintext`. Passed in rather than imported so this module never has to
# know about `zstandard`, and so a test can drive the layout without a compressor at all.
BlobReader = Callable[[Path, Path], bytes]

# The five of register §11. **All of them mean "no blob here"** and none is a digest — used as a
# filename each fails at the filesystem, which is a worse error than the honest one.
SENTINELS = frozenset({"dropped", "too_large", "absent", "error", "none"})

INDEX_NAME = "index.csv"

# Five digits, zero-padded, per session, **in timestamp order**. The index is written in
# *completion* order, so numbering it as it lies would label a session's bodies by when each call
# finished rather than by when it was made.
SEQ_DIGITS = 5

# A row with no `session_id` still has bodies worth extracting — 11 of them at the last count, all
# `/api/hello`, `/` or `/favicon.ico`. `<out>/bodies//00001-request.json` is not a path.
NO_SESSION = "_no-session"


class ExtractError(Exception):
    """A selection that cannot be honoured, said out loud rather than worked around."""


@dataclass(frozen=True)
class Selection:
    """What the user asked for. Empty means "no opinion", never "match nothing"."""

    sessions: tuple[str, ...] = ()
    models: tuple[str, ...] = ()
    agents: tuple[str, ...] = ()
    path: str | None = None

    def matches(self, row: Mapping[str, str]) -> bool:
        return (
            _any_of(self.sessions, row.get("session_id"))
            and _any_of(self.models, row.get("model"))
            and _any_of(self.agents, row.get("agent_id"))
            and (self.path is None or row.get("path") == self.path)
        )

    @property
    def empty(self) -> bool:
        return not (self.sessions or self.models or self.agents or self.path)


def _any_of(wanted: Sequence[str], value: str | None) -> bool:
    """One kind of filter, OR-ed across its repeats. **Exact, never a prefix or substring.**"""
    return not wanted or value in wanted


@dataclass(frozen=True)
class Row:
    """One index row, plus the day folder it was read from.

    The day is not in the CSV — it is the folder's name — and every later step needs it: to order
    across folders, to find the blob, and to name a day in an error.
    """

    day: str
    directory: Path
    cells: Mapping[str, str]

    @property
    def timestamp(self) -> str:
        return self.cells.get("timestamp", "")

    @property
    def session(self) -> str:
        return self.cells.get("session_id", "") or ""

    def blob(self, which: str) -> Path | None:
        """`<day>/<direction>/<digest[:2]>/<digest>.zst`, or `None` when there is no blob.

        **A sentinel is not a digest.** All five read as "no blob here"; the caller gets `None`
        and can say so, rather than a path that fails to open for a reason resembling corruption.
        """
        reference = self.cells.get(f"{which}_ref", "")
        if not reference or reference in SENTINELS:
            return None
        direction = "requests" if which == "request" else "responses"
        return self.directory / direction / reference[:2] / f"{reference}.zst"


@dataclass
class Report:
    """What a run did, in the terms a reader would check it in."""

    days: list[str] = field(default_factory=list)
    rows_read: int = 0
    rows_selected: int = 0
    sessions: set[str] = field(default_factory=set)
    missing_days: dict[str, list[str]] = field(default_factory=dict)


def read_index(day: Path) -> list[Row]:
    """One day folder's index, in the order it lies on disk.

    **Completion order, not timestamp order** — `stats.py` writes a row when a call finishes.
    Sorting is the caller's job and every caller here does it, because sorting per folder would
    still interleave wrongly across folders.
    """
    index = day / INDEX_NAME
    if not index.is_file():
        raise ExtractError(
            f"{day} holds no {INDEX_NAME}. A day folder without its index cannot be selected "
            f"over — `verify-archive` reads blobs and needs no index, but `extract` selects on "
            f"columns."
        )
    with index.open(newline="", encoding="utf-8") as handle:
        return [Row(day.name, day, dict(cells)) for cells in csv.DictReader(handle)]


def select(rows: Iterable[Row], selection: Selection) -> list[Row]:
    """The rows a selection asks for, in **timestamp order across every folder given**."""
    chosen = [row for row in rows if selection.matches(row.cells)]
    chosen.sort(key=lambda row: (row.timestamp, row.day))
    return chosen


def sequence_numbers(rows: Sequence[Row]) -> dict[int, str]:
    """`<seq>` per session, in timestamp order, from `00001`.

    Keyed by `id()` of the row rather than by anything inside it: two calls can share a timestamp
    *and* a session, and the corpus holds byte-identical retries that share nearly everything else.
    """
    counters: dict[str, int] = {}
    numbers: dict[int, str] = {}
    for row in sorted(rows, key=lambda r: (r.session, r.timestamp, r.day)):
        session = row.session or NO_SESSION
        counters[session] = counters.get(session, 0) + 1
        numbers[id(row)] = str(counters[session]).zfill(SEQ_DIGITS)
    return numbers


def days_of_sessions(given: Sequence[Path], sessions: Iterable[str]) -> dict[str, set[str]]:
    """Which day folders each session touches, **including folders that were not passed**.

    This is the one place the extractor looks sideways, and it looks at **`index.csv` and nothing
    else** — no blob, no dictionary, no folder that is not a sibling of one it was given. It
    exists so a session resumed the next morning cannot be converted from half its calls quietly.

    A sibling that cannot be read is **skipped, not fatal**. The purpose is to catch an omission;
    a folder that is unreadable is a different problem, and failing here would turn a warning into
    an outage.
    """
    wanted = {session for session in sessions if session}
    if not wanted:
        return {}
    found: dict[str, set[str]] = {session: set() for session in wanted}
    for folder in _candidate_folders(given):
        try:
            rows = read_index(folder)
        except (ExtractError, OSError):
            continue
        for row in rows:
            if row.session in found:
                found[row.session].add(folder.name)
    return found


def _candidate_folders(given: Sequence[Path]) -> list[Path]:
    """The folders passed, plus every sibling of them carrying an `index.csv`.

    Deduplicated by resolved path, so passing a folder and its own glob does not read it twice.
    """
    seen: dict[Path, None] = {}
    for day in given:
        day = Path(day)
        for candidate in (day, *sorted(day.parent.glob("*"))):
            if not candidate.is_dir() or not (candidate / INDEX_NAME).is_file():
                continue
            seen.setdefault(candidate.resolve(), None)
    return [Path(path) for path in seen]


@dataclass(frozen=True)
class Written:
    """What a run put on disk, counted so the CLI can say it without recounting."""

    bodies: int = 0
    files: int = 0
    conversations: int = 0
    no_request_blob: int = 0
    no_response_blob: int = 0


def write_bodies(rows: Sequence[Row], out: Path, read: BlobReader) -> Written:
    """`<out>/bodies/<session>/<seq>-request.json` and `<seq>-response.{sse,json}`.

    **The response's extension is read off the body itself**, not off the index's `stream` column.
    `observe.py` decides the column by *content-type* and the design deliberately allows the two to
    disagree; asking the bytes is one source instead of two that could. It is the same question
    `reassemble` asks, so the extractor and the converter cannot disagree either.

    A row whose reference is a sentinel gets **no file at all** rather than an empty one. An empty
    file is indistinguishable from a body that was genuinely empty, and the corpus holds four of
    those.
    """
    numbers = sequence_numbers(rows)
    bodies = missing_request = missing_response = 0
    for row in rows:
        folder = out / "bodies" / (row.session or NO_SESSION)
        for which, suffix in (("request", ".json"), ("response", None)):
            blob = row.blob(which)
            if blob is None:
                if which == "request":
                    missing_request += 1
                else:
                    missing_response += 1
                continue
            payload = read(row.directory, blob)
            extension = suffix if suffix is not None else _response_suffix(payload)
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{numbers[id(row)]}-{which}{extension}").write_bytes(payload)
            bodies += 1
    return Written(
        bodies=bodies, no_request_blob=missing_request, no_response_blob=missing_response
    )


def _response_suffix(payload: bytes) -> str:
    """`.json` for a buffered reply, `.sse` for a stream — legible without opening the file.

    An empty body is `.json`: it is not a stream, and calling it one would be the only reading that
    is definitely wrong.
    """
    return ".json" if payload.lstrip()[:1] in (b"{", b"") else ".sse"


def check_days(given: Sequence[Path], rows: Sequence[Row]) -> dict[str, list[str]]:
    """Which selected sessions have calls in a folder that was not passed.

    **Checked for every session before anything is written**, which is stronger than letting
    `reconstruct` raise mid-run. A run that wrote three files and then failed would leave a
    half-converted directory whose good files are indistinguishable from its abandoned ones.
    """
    passed = {Path(day).name for day in given}
    sessions = {row.session for row in rows if row.session}
    short: dict[str, list[str]] = {}
    for session, days in days_of_sessions(given, sessions).items():
        missing = sorted(days - passed)
        if missing:
            short[session] = missing
    return short


def write_jsonl(
    rows: Sequence[Row],
    out: Path,
    *,
    project: str,
    days: Sequence[str],
    read: BlobReader,
    version: str,
    generated: str,
) -> Written:
    """`<out>/projects/<project>/<session>.jsonl`, one file per **conversation**.

    `projects/` sits at the output root so the viewer's Custom Claude Directory can be pointed at
    `<out>` itself, with `bodies/` beside it and ignored. **Never `~/.claude/projects/`** — position
    12, and writing lossy reconstructions into the real history directory is not reversible.
    """
    from .jsonl import records, render
    from .transcript import CapturedCall, reconstruct

    folder = out / "projects" / project
    by_session: dict[str, list[Row]] = {}
    for row in rows:
        if row.session:
            by_session.setdefault(row.session, []).append(row)

    files = conversations = 0
    for session, session_rows in sorted(by_session.items()):
        calls = [
            CapturedCall(
                timestamp=row.timestamp,
                day=row.day,
                request=_maybe(read, row, "request"),
                response=_maybe(read, row, "response"),
            )
            for row in session_rows
        ]
        result = reconstruct(calls, session, days_passed=days)
        for conversation in result.conversations:
            payload = render(
                records(conversation, days=days, version=version, generated=generated)
            )
            folder.mkdir(parents=True, exist_ok=True)
            (folder / conversation.filename()).write_bytes(payload)
            files += 1
            conversations += 1
    return Written(files=files, conversations=conversations)


def _maybe(read: BlobReader, row: Row, which: str) -> bytes | None:
    """A blob's bytes, or `None` when the row has no blob to read."""
    blob = row.blob(which)
    return None if blob is None else read(row.directory, blob)
