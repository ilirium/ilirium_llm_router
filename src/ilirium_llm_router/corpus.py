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

import csv
import hashlib
import io
import logging
import os
import queue
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import zstandard

from .logging_setup import get_logger
from .stats import COLUMNS as STATS_COLUMNS
from .stats import CallRecord

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

BLOB_SUFFIX = ".zst"

# A zstd frame header is at most 18 bytes -- magic, the descriptor, the window byte, the dictionary
# ID and the content size. Reading that much is enough to ask a stored blob which dictionary it
# names, without decompressing it or even reading the rest of the file.
FRAME_HEADER_BYTES = 18

Direction = Literal["requests", "responses"]

DRAIN_TIMEOUT_S = 5.0
"""How long `close()` waits for the worker to finish the queue.

**From measurement, not from an estimate.** Task 6 timed the whole store path -- sha256, compress,
write, fsync, rename -- at **0.433 ms** per body, so a full 64 MiB queue of median bodies drains in
**0.28 s**, or **1.4 s** if every stage hits its p95 at once. Five seconds is ~3.5x that worst case,
which leaves the timeout bounding a hang rather than routinely cutting a drain short.

A timeout at all, rather than an unbounded wait, because **a router that will not stop is worse than
a corpus missing its last few bodies** -- and whatever is abandoned is counted and named in the
final summary, so the hole is recorded here exactly as it is anywhere else.
"""

RESCAN_EVERY = 500
"""How often the worker relists `<dir>/dicts/` looking for a newly installed dictionary, in
**bodies**.

**A separate constant from `SUMMARY_EVERY`, which happens to share its value.** They count different
things -- one call can produce two bodies, so 500 bodies is ~250 calls -- and they are emitted from
different places, `submit()` on the event loop and this in the worker. They agree at 500 and are two
decisions, either of which can move without dragging the other.

**Polling rather than a hand-off, and that is what makes the manual command work.** `--train-dict`
runs in a **separate process**, so an in-process slot published by the training thread could never
reach a router that is already running. The trainer writes a file and publishes nothing else; the
worker watching the directory serves the automatic and the manual path with one mechanism.

One `listdir` per 500 bodies, in the worker, off the request path.
"""

SUMMARY_EVERY = 500
"""How often `submit()` emits the INFO summary, in **calls**.

Emitted from **submit** rather than from the worker on purpose: a worker that has stalled emits
nothing, and a stalled worker is exactly when the line is wanted. Submits keep happening and carry
the growing `pending` with them. No timer, so an idle router says nothing, which is correct.
"""

DROPPED = "dropped"
"""The queue was over its byte bound when this call was recorded."""

TOO_LARGE = "too_large"
"""One body over `body_max_bytes`. The bytes were discarded, not truncated -- a prefix labelled as a
whole body is worse than a hole."""

ABSENT = "absent"
"""**The router authored this body** -- the 400 for a missing model, the 502 for an unreachable
backend, the injected SSE error event. The milestone's claim is every body it *carries*, and these
are ours. `error_status` in the same row already says why."""

STORE_ERROR = "error"
"""Compression or the write itself failed in the worker. Without this the one case where the store
broke is the one case the index cannot describe."""

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

    compressed: int
    """The blob's size on disk. Counted on a dedup hit too, so the summary's plaintext → compressed
    pair describes the bodies recorded rather than only the bytes newly written."""


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
class _Item:
    """One call on its way to the worker.

    **`submitted_at` and `pending_at_submit` are carried rather than read in the worker**, and that
    is the whole reason this is a record instead of a tuple of bodies. Both are values only
    `submit()` can see: by the time the worker runs, `_pending` has moved on, so a depth read there
    would be near zero at this load and therefore **indistinguishable from working**.
    """

    record: CallRecord
    request: bytes | None
    response: bytes | None
    submitted_at: float
    pending_at_submit: int
    request_note: str | None = None
    """A sentinel word if the body is not going to be stored, else `None`."""
    response_note: str | None = None


@dataclass
class _Totals:
    """What the summary line reports. Guarded by the same lock as `_pending`."""

    calls: int = 0
    stored: int = 0
    plaintext: int = 0
    compressed: int = 0
    dropped: int = 0
    too_large: int = 0
    errors: int = 0
    pending_peak: int = 0
    queue_ms_max: int = 0


@dataclass
class _Day:
    """One open day folder, and what this process has already done to it."""

    root: Path
    dictionaries: set[str]
    index: _DayIndex | None = field(default=None)
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

    def __init__(
        self,
        directory: Path,
        compress_level: int,
        body_max_bytes: int,
        queue_max_bytes: int,
        on_day_rollover: Callable[[], None] | None = None,
    ) -> None:
        self._dir = Path(directory)
        self._on_day_rollover = on_day_rollover
        self._level = compress_level
        self._body_max_bytes = body_max_bytes
        self._queue_max_bytes = queue_max_bytes
        self._logger = get_logger()
        self._days: dict[str, _Day] = {}
        self._undicted = zstandard.ZstdCompressor(level=compress_level)
        self._dictionary = self._load_newest_dictionary()

        # The queue is unbounded and the bound lives beside it, because the bound is in **bytes**
        # and no standard queue offers that. `queue.Queue(maxsize=N)` counts items, and bodies here
        # run from 2 KB to 200 KB -- so 1,000 waiting items is anywhere between 2 MB and 200 MB.
        # SimpleQueue carries none of the machinery this does not use: no maxsize, no task_done,
        # no join. `asyncio.Queue` is the tempting mistake and is **not thread-safe**: the producer
        # is the event loop and the consumer is this thread, which makes it a data race.
        self._queue: queue.SimpleQueue[_Item | None] = queue.SimpleQueue()
        self._lock = threading.Lock()
        self._pending = 0
        self._totals = _Totals()
        self._warned = False
        self._abandoned = 0
        self._since_rescan = 0
        self._worker = threading.Thread(target=self._run, name="corpus-worker", daemon=True)
        self._worker.start()

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
        self._maybe_rescan()
        day = self._open_day(self._day_of(timestamp))
        digest = hashlib.sha256(plaintext).hexdigest()

        # The invariant: whichever day folder this blob is going into must already hold this
        # dictionary. Reversed, a crash between the two steps leaves a day holding a blob whose
        # dictID names a dictionary that is not in that folder -- self-containment broken, and
        # broken silently.
        self._ensure_dictionary_in(day)

        destination = day.root / direction / digest[:FANOUT] / f"{digest}{BLOB_SUFFIX}"
        if destination.exists():
            # Dedup, scoped to this day. The same body sent eleven times in four minutes is one
            # blob and eleven index rows: the bytes collapse, the multiplicity does not.
            #
            # The dictID is read back off the blob rather than taken from the compressor, and that
            # is not fussiness. A dictionary can be installed mid-day, so a body first stored at
            # 10:00 against dictionary A and seen again at 15:00 under dictionary B would otherwise
            # get a row claiming B for a file that names A -- and telling which bodies used which
            # dictionary is the entire reason this column exists. Measured wrong before it was
            # fixed; the first test missed it because two dictionaries shared a dictID.
            return Stored(digest, _dict_id_of(destination), destination.stat().st_size)

        blob = self._compressor().compress(plaintext)
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_atomically(blob, destination, day.root / "incoming")
        return Stored(digest, self._recorded_dict_id(), len(blob))

    # -- reading back --------------------------------------------------------------------------


    def submit(
        self,
        record: CallRecord,
        request_body: bytes | None,
        response_body: bytes | None,
        response_over_cap: bool = False,
    ) -> None:
        """Hand one call to the worker. **Runs on the event loop and must not block or raise.**

        Everything expensive -- hashing, compression, `fsync`, rename, the index row -- happens in
        the worker. What happens here is a lock, an integer compare and a `put`, which is
        microseconds, and the lock is never held across I/O.

        **A full queue still records the hole.** When the bodies would push `_pending` past the byte
        bound, the record is enqueued anyway with both ref cells reading `dropped` -- a record-only
        item is a few hundred bytes and is never refused. So `EPD-003`'s *"drop the body and record
        that it was dropped"* is literally true rather than approximately: **the hole is a row, not
        an absence.**

        `None` for a body means the router authored it, which the index records as `absent`.
        """
        try:
            self._submit(record, request_body, response_body, response_over_cap)
        except Exception as exc:  # noqa: BLE001 — telemetry must never break a call
            self._logger.warning(
                "Corpus: could not queue a call: %s: %s", type(exc).__name__, exc
            )

    def _submit(
        self,
        record: CallRecord,
        request_body: bytes | None,
        response_body: bytes | None,
        response_over_cap: bool,
    ) -> None:
        request, request_note = self._admit(request_body, over_cap=False)
        response, response_note = self._admit(response_body, over_cap=response_over_cap)
        size = len(request or b"") + len(response or b"")

        with self._lock:
            self._totals.calls += 1
            if self._pending + size > self._queue_max_bytes and size:
                # Over the bound. The body is not stored and the request path does not wait --
                # waiting is the one outcome EPD-003 rules out.
                request = response = None
                request_note = response_note = DROPPED
                self._totals.dropped += 1
                dropped_now, pending = True, self._pending
            else:
                self._pending += size
                dropped_now, pending = False, self._pending
            self._totals.pending_peak = max(self._totals.pending_peak, pending)
            for note in (request_note, response_note):
                if note == TOO_LARGE:
                    self._totals.too_large += 1
            calls, warned = self._totals.calls, self._warned
            if dropped_now and not warned:
                self._warned = True

        if dropped_now and not warned:
            # Once per run, then suppressed and counted. Warning on every drop turns overload into
            # log spam, which is the moment the log most needs to stay readable.
            self._logger.warning(
                "Corpus: dropping bodies, the queue is at its %d-byte bound (%d pending). "
                "This is counted from here on and reported in the summary.",
                self._queue_max_bytes,
                pending,
            )

        self._queue.put(
            _Item(
                record=record,
                request=request,
                response=response,
                submitted_at=time.monotonic(),
                pending_at_submit=pending,
                request_note=request_note,
                response_note=response_note,
            )
        )
        if calls % SUMMARY_EVERY == 0:
            self._logger.info("%s", self.summary())

    def _admit(self, body: bytes | None, over_cap: bool) -> tuple[bytes | None, str | None]:
        """Decide whether one body is stored at all, and why not if it is not."""
        if over_cap:
            return None, TOO_LARGE
        if body is None:
            return None, ABSENT
        if len(body) > self._body_max_bytes:
            # Drop, do not store a prefix: a prefix labelled as a whole body is worse than a hole.
            return None, TOO_LARGE
        return body, None

    def summary(self) -> str:
        """The one line that answers *did this ever come close?*"""
        with self._lock:
            totals, pending = self._totals, self._pending
            return (
                f"corpus: {totals.calls} calls | stored {totals.stored} "
                f"({totals.plaintext} → {totals.compressed} bytes), "
                f"dropped {totals.dropped}, too_large {totals.too_large}, "
                f"error {totals.errors} | pending {pending}, peak {totals.pending_peak}, "
                f"queue_ms max {totals.queue_ms_max}"
                + (f", abandoned {self._abandoned}" if self._abandoned else "")
            )

    def close(self) -> None:
        """Stop the worker, giving it `DRAIN_TIMEOUT_S` to finish what it is holding.

        A sentinel rather than a kill, and a timeout rather than an unbounded wait. **Anything
        abandoned is counted and named in the final line**, so the hole is recorded here exactly as
        it is anywhere else.
        """
        self._queue.put(None)
        self._worker.join(timeout=DRAIN_TIMEOUT_S)
        if self._worker.is_alive():
            with self._lock:
                self._abandoned = self._queue.qsize()
            self._logger.warning(
                "Corpus: worker did not finish within %.1fs; %d item(s) abandoned.",
                DRAIN_TIMEOUT_S,
                self._abandoned,
            )
        for day in self._days.values():
            if day.index is not None:
                day.index.close()
        self._logger.info("%s", self.summary())

    # -- the worker ----------------------------------------------------------------------------

    def _run(self) -> None:
        """The worker loop. One body at a time, off the event loop, and it never lets an exception
        end it -- a thread that dies silently is a corpus that stops filling with nothing to say so.
        """
        while True:
            item = self._queue.get()
            if item is None:
                return
            try:
                self._process(item)
            except Exception as exc:  # noqa: BLE001 — one bad call must not stop the next
                self._logger.warning(
                    "Corpus: could not record a call: %s: %s", type(exc).__name__, exc
                )
            finally:
                with self._lock:
                    self._pending -= len(item.request or b"") + len(item.response or b"")

    def _process(self, item: _Item) -> None:
        queue_ms = int((time.monotonic() - item.submitted_at) * 1000)
        started = time.monotonic()
        stored_any = False
        refs: list[str] = []
        dict_id = ""

        for body, note, direction in (
            (item.request, item.request_note, "requests"),
            (item.response, item.response_note, "responses"),
        ):
            if note is not None:
                refs.append(note)
                continue
            try:
                stored = self.store(item.record.timestamp, direction, body or b"")
            except Exception as exc:  # noqa: BLE001 — the row must still say what happened
                self._logger.warning(
                    "Corpus: could not store a %s body: %s: %s", direction, type(exc).__name__, exc
                )
                refs.append(STORE_ERROR)
                with self._lock:
                    self._totals.errors += 1
                continue
            refs.append(stored.digest)
            stored_any = True
            if direction == "requests":
                dict_id = stored.dict_id
            with self._lock:
                self._totals.stored += 1
                self._totals.plaintext += len(body or b"")
                self._totals.compressed += stored.compressed

        store_ms = int((time.monotonic() - started) * 1000) if stored_any else None
        with self._lock:
            self._totals.queue_ms_max = max(self._totals.queue_ms_max, queue_ms)

        day = self._open_day(self._day_of(item.record.timestamp))
        if day.index is None:
            day.index = _DayIndex(day.root / "index.csv")
        day.index.append(
            item.record.cells()
            + [
                refs[0],
                refs[1],
                str(queue_ms),
                # An absent value is an empty cell, never a zero -- an absent count and a genuine
                # zero are different facts, and a body that was not stored took no time to store.
                "" if store_ms is None else str(store_ms),
                str(item.pending_at_submit),
                dict_id,
            ]
        )

    # -- days ---------------------------------------------------------------------------------

    def _day_of(self, timestamp: str) -> str:
        """`YYYY-MM-DD` from a call's timestamp, or today if that is not what it is.

        **Checked rather than sliced, because the failure is silent and lands in the wrong place.**
        An empty or malformed timestamp slices to something that is not a date, and joining that to
        the corpus directory can resolve to **the corpus root itself** — which would put `manifest`,
        `requests/` and `incoming/` beside `dicts/`, the folder the trainer writes to and this store
        reads from. Every day folder is then ambiguous.

        `observe.Call` always sets a UTC ISO timestamp, so this cannot fire in the router. It is
        here because the store is telemetry-shaped and must not turn a bad value into a bad layout.
        """
        day = timestamp[:10]
        if len(day) == 10 and day[4] == day[7] == "-" and day.replace("-", "").isdigit():
            return day
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        self._logger.warning(
            "Corpus: %r is not a usable timestamp; filing under %s instead.", timestamp, today
        )
        return today

    def _open_day(self, day: str) -> _Day:
        """Create the day folder and everything under it, once, and remember it.

        Cheap on every call after the first: the dictionary already exists in the mapping, so a
        stored body costs one dict lookup rather than five `mkdir` syscalls.
        """
        known = self._days.get(day)
        if known is not None:
            return known

        # A day folder opening is the other rescan trigger. Without it, a dictionary installed
        # overnight would not be seen until 500 more bodies had gone past.
        self._rescan()

        root = self._dir / day
        for child in ("requests", "responses", "dicts", "incoming"):
            (root / child).mkdir(parents=True, exist_ok=True)
        _sweep(root / "incoming", self._logger)
        _write_manifest(root / "manifest")

        opened = _Day(root=root, dictionaries=_names_in(root / "dicts"))
        rolled_over = bool(self._days)
        self._days[day] = opened

        # **A rollover, not the first day of the process.** Opening the first day folder after a
        # restart is not a rollover -- the startup trigger has already fired for that -- and firing
        # here too would train twice for one event. `self._days` being non-empty is what tells them
        # apart.
        if rolled_over and self._on_day_rollover is not None:
            try:
                self._on_day_rollover()
            except Exception as exc:  # noqa: BLE001 — the worker must survive its own hook
                self._logger.warning(
                    "Corpus: the day-rollover hook failed: %s: %s", type(exc).__name__, exc
                )
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
        newest = newest_dictionary(self._dir / "dicts")
        if newest is None:
            return None

        name = newest.name
        data = zstandard.ZstdCompressionDict(newest.read_bytes())
        loaded = _Dictionary(name=name, data=data, compressor=_build_compressor(data, self._level))
        self._logger.info(
            "Corpus: compressing against dictionary %s (dictID %s)", name, loaded.hex_id
        )
        return loaded

    def _maybe_rescan(self) -> None:
        """Relist `<dir>/dicts/` every `RESCAN_EVERY` bodies, and swap if a newer one has appeared.

        Counted in the worker, so the cost is one `listdir` per 500 bodies **off the request path**.
        """
        self._since_rescan += 1
        if self._since_rescan < RESCAN_EVERY:
            return
        self._since_rescan = 0
        self._rescan()

    def _rescan(self) -> None:
        """Pick up a dictionary another process installed while this router was running.

        **The trainer publishes nothing but a file**, which is the entire interface between the two
        — and it is what lets `--train-dict`, deliberately a *separate process*, reach a router that
        is already up. An in-process hand-off cannot do that.

        **Newest is by filename, never mtime**, through the same `newest_dictionary` the trainer
        uses to decide what a candidate must beat. One rule, one function: two copies that disagreed
        would have the trainer scoring against one file while this compressed against another.

        **It never raises.** A dictionary that will not load leaves the current one in place and
        writes a warning — this runs in the worker, between two bodies, and telemetry does not get
        to break a call. Construction is the one place a bad dictionary stops something, because
        that is not a call.

        The ordering invariant — *the dictionary is in the day folder before any blob referencing it
        is written there* — is **not** enforced here. It is a per-write precondition in `store()`,
        which is stricter: one worker can be writing into two day folders across a rollover while
        holding one compressor, so the check has to be per blob rather than per swap.
        """
        newest = newest_dictionary(self._dir / "dicts")
        if newest is None:
            return
        current = self._dictionary.name if self._dictionary else None
        if newest.name == current:
            return

        try:
            data = zstandard.ZstdCompressionDict(newest.read_bytes())
            swapped = _Dictionary(
                name=newest.name, data=data, compressor=_build_compressor(data, self._level)
            )
        except (OSError, ValueError, zstandard.ZstdError, CorpusError) as exc:
            self._logger.warning(
                "Corpus: could not load newly installed dictionary %s, keeping %s: %s: %s",
                newest.name,
                current or "no dictionary",
                type(exc).__name__,
                exc,
            )
            return

        self._dictionary = swapped
        self._logger.info(
            "Corpus: switched to dictionary %s (dictID %s), was %s",
            swapped.name,
            swapped.hex_id,
            current or "no dictionary",
        )

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


class CorpusReader:
    """Bodies back out of a day folder: blob → plaintext, verified as it reads.

    **It reads a day folder and nothing above it.** That is the self-containment rule from the
    reading direction: `tar` a day, unpack it anywhere, point this at it, and every blob opens. No
    index, no `<dir>/dicts/`, no configuration.

    **Every read is a free integrity check**, because the blob's filename *is* the sha256 of its
    plaintext. Nothing extra is stored to make that true and nothing has to be trusted for it to
    hold.

    Task 14's trainer cannot assemble a sample list without this, which is why the reader ships in
    this phase while the *tool* built on it is Phase 11's.
    """

    def __init__(self, day: Path) -> None:
        self._day = Path(day)
        self._by_id: dict[int, list[zstandard.ZstdCompressionDict]] | None = None

    def directions(self) -> list[str]:
        return [d for d in ("requests", "responses") if (self._day / d).is_dir()]

    def blobs(self, direction: Direction) -> list[Path]:
        """Every blob in one direction, sorted. The fan-out is an implementation detail here."""
        return sorted((self._day / direction).glob(f"*/*{BLOB_SUFFIX}"))

    def read(self, path: Path) -> bytes:
        """One blob, decompressed and checked against its own name.

        **The frame's dictID is a lookup hint, not a key.** `zstd --train` stamps `1` on every
        dictionary it produces, so more than one file in a day's `dicts/` can answer to the same
        ID — and a dictionary the router did not write can be dropped into the folder by anyone.
        So every candidate is tried and the one that *verifies* is kept.

        That is affordable because both failure modes are loud, measured 2026-08-19: the wrong
        dictionary of a matching ID raises `Data corruption detected`, and no dictionary at all
        raises `Dictionary mismatch`. Neither returns plausible wrong bytes. The digest check is
        the belt to that pair of braces.
        """
        blob = path.read_bytes()
        expected = path.name.removesuffix(BLOB_SUFFIX)
        dict_id = zstandard.get_frame_parameters(blob).dict_id

        for candidate in self._candidates(dict_id):
            try:
                plaintext = _decompress(blob, candidate)
            except zstandard.ZstdError:
                continue
            if hashlib.sha256(plaintext).hexdigest() == expected:
                return plaintext

        raise CorpusError(
            f"{path.name} did not open. Its frame names dictionary {dict_id:08x}; the day folder "
            f"holds {len(self._candidates(dict_id))} candidate(s) for that ID and none produced "
            f"bytes matching the digest in the filename."
        )

    def _candidates(self, dict_id: int) -> list[zstandard.ZstdCompressionDict | None]:
        if dict_id == 0:
            # A frame that names no dictionary, which is what the store writes before one exists.
            return [None]
        return list(self._dictionaries().get(dict_id, []))

    def _dictionaries(self) -> dict[int, list[zstandard.ZstdCompressionDict]]:
        """Every dictionary in the day's own `dicts/`, indexed by the ID it claims.

        A list per ID rather than one dictionary, because IDs are not unique — that is the whole
        reason `read` loops.

        **This glob deliberately takes more than `_is_dictionary` would, and the asymmetry is
        correct rather than an oversight.** `pathlib`'s `*` matches dotfiles, so a
        `.half-written.dict` is a candidate here while the writer's `newest_dictionary` excludes it.
        The two have opposite jobs: the **writer picks exactly one** and must never pick a partial
        file, so it is strict; the **reader tries every candidate and keeps the one that verifies
        against the digest in the blob's filename**, so an extra candidate costs a failed attempt
        and nothing else. Being permissive here is what lets a day folder be read after somebody has
        copied files into it by hand.
        """
        if self._by_id is None:
            found: dict[int, list[zstandard.ZstdCompressionDict]] = {}
            for path in sorted((self._day / "dicts").glob("*.dict")):
                data = zstandard.ZstdCompressionDict(path.read_bytes())
                found.setdefault(data.dict_id(), []).append(data)
            self._by_id = found
        return self._by_id


def _decompress(blob: bytes, dictionary: zstandard.ZstdCompressionDict | None) -> bytes:
    context = (
        zstandard.ZstdDecompressor(dict_data=dictionary)
        if dictionary is not None
        else zstandard.ZstdDecompressor()
    )
    return context.decompress(blob)


class _DayIndex:
    """`<day>/index.csv` — one row per call, header re-emitted in every day file.

    **The header is in every file on purpose.** A day folder has to be readable on its own, and a
    headerless block of values is the kind of file that gets thrown away. It is the same rule
    `stats.py` applies to a rotated segment, for the same reason.

    Opened lazily and kept open: the worker appends to one file for a whole day, and reopening per
    row would be a syscall per body for nothing.
    """

    def __init__(self, path: Path) -> None:
        self._path = path
        existed = path.exists() and path.stat().st_size > 0
        # The handle deliberately outlives this call: one file is appended to for a whole day and
        # `close()` owns it. A context manager here would reopen per row, which is a syscall per
        # body for nothing. `stats.py` keeps its handle open for the same reason.
        self._handle = open(path, "a", encoding="utf-8", newline="")  # noqa: SIM115
        if not existed:
            self._handle.write(_render_row(list(INDEX_COLUMNS)))
            self._handle.flush()

    def append(self, cells: list[str]) -> None:
        self._handle.write(_render_row(cells))
        self._handle.flush()

    def close(self) -> None:
        self._handle.close()


def _render_row(cells: list[str]) -> str:
    """One CSV line, quoted and escaped by `csv` rather than by hand.

    `error_message` is free text copied from a backend, so a stray comma or quote in it would
    otherwise shift every column after it.

    **Deliberately not `stats.py`'s `_render`.** That function is private to a module this phase
    does not otherwise touch, and `calls.csv` not changing is a milestone non-goal — four lines here
    is a cheaper price than reaching across for them.
    """
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="\r\n").writerow(cells)
    return buffer.getvalue()


def _dict_id_of(blob: Path) -> str:
    """Which dictionary a stored blob actually names, read from its own header.

    The header is self-describing and tiny, so this costs one short read rather than a
    decompression. A frame stored with no dictionary reports 0, which becomes the word `none` --
    `docs/reference/observability.md` forbids writing that 0 into a cell, since 0 is also a real
    dictID.

    A blob whose header will not parse raises, and that is deliberate: the store `fsync`ed this
    file itself, so an unparseable header means the filesystem damaged it. Task 9's worker turns
    that into a recorded failure rather than a silent one.
    """
    with open(blob, "rb") as handle:
        header = handle.read(FRAME_HEADER_BYTES)
    dict_id = zstandard.get_frame_parameters(header).dict_id
    return f"{dict_id:08x}" if dict_id else NO_DICTIONARY


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
    # **A dictionary that claims no ID is refused before anything is written against it.**
    # `ZstdCompressionDict` accepts *arbitrary bytes* -- a stray file in `dicts/` is silently taken
    # as a "content-only" dictionary, whose `dict_id()` is **0**. Frames compressed against one then
    # claim to be undicted while genuinely needing those bytes to decompress: measured 2026-08-20,
    # such a blob raises `Data corruption detected` and the reader never tries a dictionary at all,
    # because a frame reporting 0 is exactly how "stored with no dictionary" is spelled. Every blob
    # written in that window would be permanently unreadable, which is failure mode 2 in the one
    # form nothing else here can catch.
    if data.dict_id() == 0:
        raise CorpusError(
            "This dictionary reports ID 0, which zstd reads as 'no dictionary'. Bodies compressed "
            "against it would be written as frames claiming to need no dictionary while genuinely "
            "needing this file, and nothing could ever read them back. Arbitrary bytes are accepted "
            "by zstd as a content-only dictionary, so this is what a stray file in dicts/ looks "
            "like."
        )

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


def newest_dictionary(dicts_dir: Path) -> Path | None:
    """The dictionary that counts as current in a `dicts/` folder, or `None` if there is not one.

    **Newest is by filename, never by mtime.** `logs/` sits inside a cloud-synced folder on the
    machine this was built for, and a sync rewrites mtimes; the name leads with a UTC stamp
    precisely so that sorting it is meaningful.

    **Shared rather than duplicated, and that is the whole reason it is a function.** The corpus
    worker asks this to decide what to compress against, and `dictionary.py`'s trainer asks it to
    decide which dictionary a candidate has to beat. Two copies of the rule that disagreed would
    have the trainer scoring against one file while the worker wrote against another — and nothing
    would report it, because each half would be behaving correctly on its own.
    """
    candidates = sorted(name for name in _names_in(dicts_dir) if _is_dictionary(name))
    return dicts_dir / candidates[-1] if candidates else None


def write_atomically(payload: bytes, destination: Path, staging: Path) -> None:
    """`write → fsync → rename`, so a reader never sees a partial blob.

    The rename is what makes a blob's appearance atomic; the `fsync` before it is what stops a
    crash leaving a correctly-named file full of nothing. `os.replace` is atomic within a
    filesystem, which `staging` being inside the same day folder guarantees.

    **Shared with `dictionary.py`**, which installs a trained dictionary the same way and for a
    sharper reason: a router starting mid-write would otherwise load a truncated dictionary. The
    `<pid>-<uuid>.tmp` name is what makes the trainer's *"two processes cannot rename interleaved
    bytes into one valid-looking file"* true, since `--train-dict` is deliberately another process.
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
    write_atomically(source.read_bytes(), destination, staging)


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
