"""The body store: every body the router carries, compressed and content-addressed.

`docs/reference/design-decisions.md` decided that bodies are archived as content-addressed per-call
files compressed against a shared dictionary. This file is the write half of that. The queue and the
worker thread that call it are Task 9's, the day index is Task 10's, and the reader is Task 13a's.

**Nothing here is on the request path.** Everything in this module runs in the corpus worker thread,
which is what lets it hash, compress and `fsync` without the event loop noticing. `docs/wiki/
background-work-in-fastapi.md` says why that thread is a thread and not an `asyncio` task.

What the layout guarantees, and why each part of it earns its place:

- **A day folder is self-contained.** `tar` one, unpack it elsewhere, and every blob in it opens —
  which is what makes `rm -rf <a-day>` the whole retention policy. So each day keeps its own copy of
  every dictionary its blobs reference. `logs/corpus/dicts/` is the *source* a trainer writes to and
  this store reads from; it is never needed to read a day back.
- **The digest is of the plaintext, never of the compressed bytes.** Compressed output depends on
  the dictionary and the level, so hashing it would make one body two different files the day
  either changes. Hashing the plaintext also makes every read a free integrity check, which is
  what the reader uses.
- **Dedup is scoped to the day, deliberately.** Cross-day dedup would make deleting one day orphan
  another day's references, and that is the whole retention answer. Within a day it is free: the
  destination path *is* the digest, so an existing file is a duplicate.
- **Blobs are immutable and never recompressed.** A zstd frame names its own dictionary, so a new
  dictionary applies to new bodies only and old blobs stay readable forever.
- **The store works with no dictionary at all**, which is the ordinary case at first run: bodies are
  written as plain zstd frames at ~3.17x instead of ~12.9x, and they stay valid forever.

The one field the whole design rests on is the dictionary ID that zstd writes into each frame. It is
asserted here rather than assumed — see `_build_compressor`.
"""

from __future__ import annotations

import hashlib
import logging
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import zstandard

from .logging_setup import get_logger
from .stats import COLUMNS as STATS_COLUMNS

INDEX_SCHEMA_VERSION = 1
"""Written into each day's `manifest`. Bumped when the index's columns change meaning."""

INDEX_EXTRA_COLUMNS = (
    "request_ref",
    "response_ref",
    "queue_ms",
    "store_ms",
    "queue_bytes",
    "request_dict_id",
)
"""What the day index appends after `stats.COLUMNS`. **Task 10 writes the rows; this file only
needs the count**, because the `manifest` records it — and a hardcoded 26 that disagreed with the
real tuple is exactly the drift a manifest exists to prevent."""

INDEX_COLUMNS = STATS_COLUMNS + INDEX_EXTRA_COLUMNS
"""The index's 26 columns. The first twenty are `calls.csv`'s, in its order, so a rotated segment
and a day index can feed one spreadsheet."""

# A blob's directory fan-out. Two hex characters is 256 buckets, which keeps a day's busiest
# direction off the pathological single-huge-directory case without inventing a deeper tree.
FANOUT = 2

Direction = Literal["requests", "responses"]

NO_DICTIONARY = "none"
"""What the index records when a body was stored with no dictionary at all.

A **word**, not `0`. libzstd's "no dictionary" genuinely *is* dictID 0, and
`docs/reference/observability.md` rules that an absent value is an empty cell and never a zero — so
"stored undicted" needs to be distinguishable from both, and a word can never be mistaken for a
digest or for an empty cell.
"""


class CorpusError(Exception):
    """The store cannot be trusted to write readable blobs.

    Raised at construction only, never per body. A failure writing one body is that body's problem
    and Task 9's worker records it in the row; a failure that would make *every* blob unreadable is
    a different thing and has to stop something.
    """


@dataclass(frozen=True)
class Stored:
    """What the index needs to know about one stored body."""

    digest: str
    """sha256 of the plaintext, 64 lowercase hex. This is also the blob's filename."""

    dict_id: str
    """The dictionary the frame names: 8 lowercase hex, or `none` if it was stored undicted."""


@dataclass
class _Dictionary:
    """The dictionary currently in use, and the compressor built from it.

    The compressor is built **once** rather than per body: Task 6 measured that building it per call
    is the difference between a dictionary being nearly free and being the dominant cost.
    """

    name: str
    data: zstandard.ZstdCompressionDict
    compressor: zstandard.ZstdCompressor

    @property
    def hex_id(self) -> str:
        return f"{self.data.dict_id():08x}"


@dataclass
class _Day:
    """One open day folder, and what this process has already done to it."""

    root: Path
    dictionaries: set[str]
    """Names already copied into `<day>/dicts/`. A set because the copy is a **per-write
    precondition**, not a per-swap step: one worker can be writing into two day folders across a
    rollover while holding one compressor, so "the dictionary is in the folder" is checked for every
    blob and has to be cheap after the first time."""


class CorpusWriter:
    """The blob store: bodies in, content-addressed compressed files out.

    Owned by the app rather than reached for globally, so a test can point one at a temporary path —
    the same shape as `stats.StatsWriter`, and for the same reason.

    Takes its directory and level as plain values for now; Task 11 builds the `corpus:` config block
    and Task 12 is where the app passes `config.corpus` in.
    """

    def __init__(self, directory: Path, compress_level: int) -> None:
        self._dir = Path(directory)
        self._level = compress_level
        self._logger = get_logger()
        self._days: dict[str, _Day] = {}
        self._undicted = zstandard.ZstdCompressor(level=compress_level)
        self._dictionary = self._load_newest_dictionary()

    @property
    def directory(self) -> Path:
        return self._dir

    @property
    def dictionary_name(self) -> str | None:
        """The dictionary in use, by filename, or `None` when writing undicted."""
        return self._dictionary.name if self._dictionary else None

    def store(self, timestamp: str, direction: Direction, plaintext: bytes) -> Stored:
        """Compress and store one body; return what the index should record about it.

        **The day comes from the call's own timestamp, not from the clock at write time.** A body
        that arrived at 23:59:59 and reaches this method at 00:00:02 belongs to *yesterday* — the
        same day as the index row describing it, which is the only thing that keeps a day folder
        readable as a unit. `timestamp` is `observe.Call`'s, which is already UTC.

        This may raise: a full disk is a real thing. Task 9's worker is what catches it and writes
        `error` into the row, because one body failing must not stop the next.
        """
        day = self._open_day(timestamp[:10])
        digest = hashlib.sha256(plaintext).hexdigest()

        # The invariant: whichever day folder this blob is going into must already hold this
        # dictionary. Reversed, a crash between the two steps leaves a day holding a blob whose
        # dictID names a dictionary that is not in that folder -- self-containment broken, and
        # broken silently.
        self._ensure_dictionary_in(day)

        destination = day.root / direction / digest[:FANOUT] / f"{digest}.zst"
        if destination.exists():
            # Dedup, scoped to this day. The same body sent eleven times in four minutes is one
            # blob and eleven index rows: the bytes collapse, the multiplicity does not.
            return Stored(digest, self._recorded_dict_id())

        blob = self._compressor().compress(plaintext)
        destination.parent.mkdir(parents=True, exist_ok=True)
        _write_atomically(blob, destination, day.root / "incoming")
        return Stored(digest, self._recorded_dict_id())

    def close(self) -> None:
        """Nothing to flush: every blob is already `fsync`ed and renamed by the time `store`
        returns. Present so the app can own this the way it owns `StatsWriter`."""

    # -- days ---------------------------------------------------------------------------------

    def _open_day(self, day: str) -> _Day:
        """Create the day folder and everything under it, once, and remember it.

        Cheap on every call after the first: the dictionary already exists in the mapping, so a
        stored body costs one dict lookup rather than five `mkdir` syscalls.
        """
        known = self._days.get(day)
        if known is not None:
            return known

        root = self._dir / day
        for child in ("requests", "responses", "dicts", "incoming"):
            (root / child).mkdir(parents=True, exist_ok=True)
        _sweep(root / "incoming", self._logger)
        _write_manifest(root / "manifest")

        opened = _Day(root=root, dictionaries=_names_in(root / "dicts"))
        self._days[day] = opened
        return opened

    # -- dictionaries -------------------------------------------------------------------------

    def _load_newest_dictionary(self) -> _Dictionary | None:
        """The newest dictionary in `<dir>/dicts/`, or `None` if there is not one yet.

        **Newest is by filename, never by mtime.** `logs/` sits inside a cloud-synced folder on the
        machine this was built for, and a sync rewrites mtimes; the name leads with a UTC stamp
        precisely so that sorting it is meaningful.

        Returning `None` is the ordinary case at first run, not a failure: the store ships before
        the trainer does, so the first day's bodies are written undicted and stay valid forever.
        """
        candidates = sorted(name for name in _names_in(self._dir / "dicts") if _is_dictionary(name))
        if not candidates:
            return None

        name = candidates[-1]
        data = zstandard.ZstdCompressionDict((self._dir / "dicts" / name).read_bytes())
        loaded = _Dictionary(name=name, data=data, compressor=_build_compressor(data, self._level))
        self._logger.info(
            "Corpus: compressing against dictionary %s (dictID %s)", name, loaded.hex_id
        )
        return loaded

    def _ensure_dictionary_in(self, day: _Day) -> None:
        """Put a plain copy of the dictionary in the day folder, if it is not there already."""
        if self._dictionary is None or self._dictionary.name in day.dictionaries:
            return
        name = self._dictionary.name
        _copy_atomically(
            self._dir / "dicts" / name, day.root / "dicts" / name, day.root / "incoming"
        )
        day.dictionaries.add(name)

    def _compressor(self) -> zstandard.ZstdCompressor:
        return self._dictionary.compressor if self._dictionary else self._undicted

    def _recorded_dict_id(self) -> str:
        return self._dictionary.hex_id if self._dictionary else NO_DICTIONARY


def _build_compressor(
    data: zstandard.ZstdCompressionDict, level: int
) -> zstandard.ZstdCompressor:
    """A compressor that provably writes the dictionary ID into every frame.

    **This assertion is the point of the function.** `ZstdCompressor(level=, dict_data=)` defaults
    `write_dict_id` on, but `ZstdCompressionParameters` defaults it to **0**, and the two arguments
    are mutually exclusive — so a later edit reaching for the tuning path would silently stop frames
    naming their dictionary and make every blob written after it unreadable. Nothing else would
    notice: the frames compress, decompress in-process, and fail only when somebody reads them back
    months later without the dictionary already in hand.

    Measured 2026-08-19 rather than read off the source, because the documented default belongs to
    the CFFI backend and CPython runs the C one — `docs/milestone-2-corpus/phase-10-body-store/
    evidence/smoke.txt`, section 3.

    It raises rather than falling back to undicted, and that is deliberate. This runs at startup,
    which is not a call, so "telemetry must never break a call" does not reach it — and a store
    quietly writing blobs nobody can read is worse than one that refuses to start.
    """
    compressor = zstandard.ZstdCompressor(level=level, dict_data=data)
    written = zstandard.get_frame_parameters(compressor.compress(b"dictID probe")).dict_id
    if written != data.dict_id():
        raise CorpusError(
            f"The compressor is not writing the dictionary ID into its frames "
            f"(frame says {written}, dictionary is {data.dict_id()}). Every blob written this way "
            f"would be unreadable without knowing its dictionary by other means. This happens when "
            f"a ZstdCompressionParameters is passed without write_dict_id=1."
        )
    return compressor


def _write_manifest(path: Path) -> None:
    """The day's schema note, written once when the folder opens.

    Two lines and nothing else. Key-and-colon because that is what `config.yaml` already reads
    like, and because it greps. It exists so a day folder found on its own says what its index is,
    rather than leaving a reader to count columns and guess.
    """
    if path.exists():
        return
    path.write_text(
        f"index_schema_version: {INDEX_SCHEMA_VERSION}\nindex_columns: {len(INDEX_COLUMNS)}\n",
        encoding="utf-8",
    )


def _write_atomically(payload: bytes, destination: Path, staging: Path) -> None:
    """`write → fsync → rename`, so a reader never sees a partial blob.

    The rename is what makes a blob's appearance atomic; the `fsync` before it is what stops a
    crash leaving a correctly-named file full of nothing. `os.replace` is atomic within a
    filesystem, which `staging` being inside the same day folder guarantees.
    """
    staging.mkdir(parents=True, exist_ok=True)
    temporary = staging / f"{os.getpid()}-{uuid.uuid4().hex}.tmp"
    try:
        with open(temporary, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def _copy_atomically(source: Path, destination: Path, staging: Path) -> None:
    """A plain copy of a dictionary into a day folder, appearing all at once.

    Plain copies rather than hard links: links were considered and declined, because a day folder
    that is `tar`red and unpacked elsewhere has to carry its dictionaries with it, and ~150 MB a
    year is a cost the owner accepted for one fewer concept.
    """
    if destination.exists():
        return
    _write_atomically(source.read_bytes(), destination, staging)


def _sweep(staging: Path, logger: logging.Logger) -> None:
    """Remove staging files a killed process left behind.

    A partial file in `incoming/` is harmless and invisible to any reader — nothing globs it and
    nothing links to it — but "a killed run leaves no trace" is only true if somebody sweeps.
    """
    for leftover in staging.glob("*.tmp"):
        try:
            leftover.unlink()
        except OSError as exc:  # one bad file must not stop the sweep
            logger.warning("Corpus: could not remove stale %s: %s", leftover.name, exc)


def _names_in(directory: Path) -> set[str]:
    try:
        return {entry.name for entry in directory.iterdir() if entry.is_file()}
    except FileNotFoundError:
        return set()


def _is_dictionary(name: str) -> bool:
    """`.dict` files only, and never a dotfile — `<dir>/dicts/.incoming/` is staging, and a
    half-written dictionary picked up as the newest one is the failure this excludes."""
    return name.endswith(".dict") and not name.startswith(".")
