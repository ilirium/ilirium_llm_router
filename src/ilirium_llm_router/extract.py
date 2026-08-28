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
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

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
