"""Dictionary training: the candidate, the score, the refusal, and the install.

The store in `corpus.py` compresses bodies against a shared dictionary. This file is where that
dictionary comes from. **The two modules share only the reader**, which is why they are two modules
and not one — the store runs per body on the corpus worker, and nothing here runs on a call path at
all.

**Training is non-monotonic in both `k` and `maxdict`**, measured on both trainers and recorded in
`docs/wiki/zstandard-and-libzstd.md`. A dictionary with better-looking parameters is not a better
dictionary, so a candidate is **measured against the one it would replace** and refused if it does
not win. That refusal is the reason this module exists rather than a one-line call to
`train_dictionary`.

Three things here are easy to get wrong and each has a comment saying why:

- **There are three compression levels, not one.** Archiving and *scoring* both read
  `corpus.compress_level_zstd`; **training** uses `TRAIN_LEVEL`, which is 3. Conflating them is the
  trap of this phase — see `TRAIN_LEVEL`.
- **A dictID is not a unique key.** `zstd --train` stamps `1` on everything, and libzstd's own ID
  does not cover the entropy tables, so one ID can name several different files. **This router
  stamps its own**, derived from the dictionary's content — `content_dict_id`.
- **The ID can only be applied after training**, because it is derived from the trained bytes. See
  `train`.

**Nothing here ever raises into a call.** It is telemetry-shaped: the caller logs what went wrong
and the router carries on compressing against whatever it already had.
"""

from __future__ import annotations

import csv
import hashlib
import os
import threading
import time
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import zstandard

from .config import Corpus
from .corpus import CorpusError, CorpusReader, newest_dictionary, write_atomically
from .logging_setup import get_logger

TRAIN_LEVEL = 3
"""The zstd level a dictionary is **trained** at, and nothing else.

**Not the level bodies are stored at, and not the level a candidate is scored at** — both of those
read `corpus.compress_level_zstd`. Keeping the three apart is the whole point: scoring has to follow
the config key or an operator editing it would silently score at a level nothing writes at, while
training answers no question that the write level is relevant to.

**A constant rather than a key, on a measurement.** Across training levels 3, 6, 9, 12 and 19 the
held-out ratio moves by **0.03%** — two orders of magnitude below `INSTALL_MARGIN` — so changing this
alone can never install a dictionary, and level 19 costs eight times the wall clock for the worst
result of the five. 3 is also the library's own default.

It is **passed explicitly even so.** `zstandard` falls back to 3 only when `steps` and `threads` are
both unset, and that same branch quietly sets `steps = 4`. The discipline is the one `k` earned:
pass the parameter, do not inherit it.
"""

TRAIN_D = 8
"""COVER's dmer size. Constraint is `0 < d <= k`; Task 6 used 8 throughout and never varied it.

Fixed rather than configurable because varying it is a sweep nobody here has needed, and a constant
makes that a decision rather than an omission.
"""

DICT_MAGIC = 0xEC30A437
"""The magic number a zstd dictionary file starts with, little-endian in its first four bytes.

Checked before the ID field immediately behind it is overwritten. Without the check, `stamp` handed
something that is not a dictionary would write four bytes into the middle of it and hand back bytes
that *look* stamped — and the failure would not surface until a body compressed against it could not
be read back.
"""

INSTALL_MARGIN = 0.02
"""How much a candidate must beat the incumbent by before it is installed. **Strictly more than.**

**Provisional, and it says so.** There is no data to choose it from: the frozen sweep shows
neighbouring parameter choices differing by −15% to +14%, so anything from 1% to 10% is arguable. 2%
is above run-to-run noise and below every real improvement the sweep found. **It is revisited against
real installs, not against arithmetic.**
"""

TRAIN_BUDGET_S = 60
"""Above this measured training time, retraining is **startup-only**; at or under it, startup **and**
day-rollover.

**A gate with a branch, not a threshold to record.** The owner declined to choose the trigger in
advance, on the grounds that **UTC midnight is an arbitrary local hour**: a four-minute run is
indefensible mid-afternoon beside a local model, and a three-second one makes the question moot. The
number decides it, so this constant is applied rather than merely logged.

**Measured 2026-08-20 at 0.03 s** on the whole surviving corpus — three orders of magnitude under.
That is a corpus of 48 bodies, so it is a formality *at this size* and **re-measured rather than
inherited** once a window holds real days.
"""

WINDOW_MAX_DAYS = 30
"""The cap on widening the window in search of a second session."""

MIN_SESSIONS = 2
"""How many sessions the training window must hold before the split below can run.

**It exists because most days carry exactly one session.** One harness on one laptop produces
single-session days as the ordinary case, and a leave-one-session-out split cannot run on a window
holding one — so the window widens into older complete days until it finds a second.
"""

TUNE_MAXDICT = (112_640, 262_144, 524_288, 1_048_576)
TUNE_K = (2_000, 8_000, 16_000)
"""The grid `--tune-dict` sweeps when neither axis is pinned: **twelve trainings**.

**Task 6's grid, deliberately.** Reusing it means a sweep run today can be read against the table
frozen in this phase's `evidence/`, which is the only other measurement of this shape that exists
here. Choosing a fresh range would produce numbers nobody could compare to anything.

**It is a starting point, not a recommendation**, and the tool says so in its own output: the range
was chosen for a 48-body corpus and training is **non-monotonic in both axes**, so the surface is
printed whole rather than reduced to a winner. Pinning `--maxdict` or `--k` narrows the sweep to
that value.
"""

LOCK_STALE_S = 3600
"""When a `retrain.lock` left behind by a killed process is broken, in seconds.

**The asymmetry chose it:** breaking early runs two trainers at once, breaking late delays an event
that only happens daily. An hour is far past any real training time and far short of a day.
"""


@dataclass(frozen=True)
class Candidate:
    """A freshly trained dictionary, stamped and not yet installed."""

    raw: bytes
    """The dictionary's bytes, carrying the ID this router derived for them."""

    dict_id: int
    """`content_dict_id(raw)`. Held separately so a caller never has to re-derive it."""

    samples: int
    maxdict: int
    k: int

    train_seconds: float
    """Wall clock for the `train_dictionary` call alone.

    **Task 14a needs this**, to compare against `TRAIN_BUDGET_S` and decide whether training may
    fire on day-rollover as well as at startup. It deliberately excludes collecting and
    decompressing the samples, which is 14a's own work and is timed there.
    """

    @property
    def hex_id(self) -> str:
        """8 lowercase hex — a dictID is a `uint32`, so 8 characters is exact."""
        return f"{self.dict_id:08x}"


@dataclass(frozen=True)
class Verdict:
    """What the comparison decided, and the numbers it decided on.

    Every field here ends up on a `retrain.log` line, which is Task 14a's to write. **A refusal is
    recorded as carefully as an install** — otherwise a candidate that loses is retrained from
    identical input on every restart, forever, for a verdict that cannot change.
    """

    installed: bool
    reason: str
    plaintext_bytes: int
    candidate_bytes: int
    incumbent_bytes: int | None
    """`None` when there was no incumbent — the ordinary first case, since the store ships before
    the trainer does."""

    score_level: int
    """The level both sides were compressed at. **Recorded because it is operator-editable**: two
    ratios logged on different days are not comparable unless the line says what they were scored
    at."""

    @property
    def candidate_ratio(self) -> float:
        return self.plaintext_bytes / self.candidate_bytes if self.candidate_bytes else 0.0

    @property
    def incumbent_ratio(self) -> float | None:
        if not self.incumbent_bytes:
            return None
        return self.plaintext_bytes / self.incumbent_bytes

    @property
    def improvement(self) -> float | None:
        """How much smaller the candidate is than the incumbent, as a fraction. `None` with no
        incumbent, and **negative when the candidate is worse** — which is the case this exists to
        catch."""
        if not self.incumbent_bytes:
            return None
        return (self.incumbent_bytes - self.candidate_bytes) / self.incumbent_bytes


def content_dict_id(raw: bytes) -> int:
    """The dictionary ID this router stamps, derived from the dictionary's own content.

    sha256 of the dictionary **with its own ID field zeroed**, first four bytes big-endian, `or 1`.

    **Ours rather than libzstd's, and that is measured rather than stylistic.** libzstd's ID is
    derived from content that `k`, `d` and the samples fix, and does *not* cover the entropy tables
    the level layers on top — so the same samples trained at levels 3, 9 and 19 give **one ID and
    three different files**. A content-derived ID gives three. `zstd --train` is worse still: it
    stamps **1** on everything it produces.

    **Zeroing the field first is what makes this a fixed point.** The ID lives inside the bytes
    being hashed, so the derivation needs a canonical form; with the field zeroed, re-deriving the
    ID of an already-stamped dictionary gives the same answer, which is the property that lets a
    dictionary be identified by its content at any later moment.

    **`or 1` is not decoration.** dictID **0** means *no dictionary*, so a hash landing on zero would
    make every frame written against this dictionary claim to be undicted — a one-in-four-billion
    path to a corpus that misreports itself, and one line to close.
    """
    canonical = bytearray(raw)
    canonical[4:8] = b"\x00\x00\x00\x00"
    return _id_from_digest(hashlib.sha256(bytes(canonical)).digest())


def _id_from_digest(digest: bytes) -> int:
    """The last four lines of `content_dict_id`, split out so that they can be **tested**.

    No dictionary can be constructed whose sha256 begins with four zero bytes, so the `or 1` guard
    is unreachable through `content_dict_id` and a test that went that way would pass with the
    guard deleted — which is the shape of check this project has been bitten by. Given a digest
    directly, the zero case is one line to exercise.
    """
    # The mask is redundant while this reads four bytes -- and it is written anyway, because an
    # out-of-range `dict_id` does **not** raise: `2**32` silently yields libzstd's own ID, which is
    # indistinguishable from never having stamped one at all. The guarantee is cheap enough to make
    # locally true rather than to leave resting on the slice width above it.
    return (int.from_bytes(digest[:4], "big") & 0xFFFFFFFF) or 1


def _is_zstd_dictionary(payload: bytes) -> bool:
    """Whether these bytes are a zstd dictionary rather than a body.

    **A dictionary is never a training sample, and this is not hypothetical.**
    `logs/corpus-gate/dicts/` sits beside the capture directories and holds eight dictionaries that
    were *trained on those very captures* — so treating it as a session fed run-01's content back in
    as training material while run-01 was the held-out slice. **Measured 2026-08-20: that reported
    26.210x against a true figure near 12.9x.** It is the exact leakage the leave-one-session-out
    split exists to prevent, reintroduced through a directory listing.

    Checked by content rather than by folder name, because the name is a convention and the magic
    number is a fact — and `--from` may be pointed at any layout at all.
    """
    return len(payload) >= 4 and int.from_bytes(payload[:4], "little") == DICT_MAGIC


def stamp(raw: bytes, dict_id: int) -> bytes:
    """Return `raw` with its dictionary ID field set to `dict_id`.

    **The ID lives at bytes `[4:8]`, little-endian, straight after the magic number** — and
    rewriting it is the only way to change one after training, since `ZstdCompressionDict` takes no
    `dict_id` argument. Measured safe: the re-stamped dictionary round-trips and the compressed
    output is byte-for-byte the same size, because the ID plays no part in compression and is pure
    metadata.

    It **raises** on a value libzstd would have accepted silently. `train_dictionary(dict_id=2**32)`
    does not fail — it falls back to libzstd's own ID, leaving a dictionary that looks stamped and
    is not. Refusing here is the difference between a loud failure and a corpus that quietly
    disagrees with itself about which dictionary its blobs were written against.
    """
    if len(raw) < 8 or int.from_bytes(raw[:4], "little") != DICT_MAGIC:
        raise CorpusError(
            f"These are not the bytes of a zstd dictionary: expected magic {DICT_MAGIC:#x}, "
            f"found {int.from_bytes(raw[:4], 'little'):#x}. Stamping them would write four bytes "
            f"into the middle of something else and return it looking valid."
        )
    if not 1 <= dict_id <= 0xFFFFFFFF:
        raise CorpusError(
            f"{dict_id} is not a usable dictionary ID. It must fit in a uint32, and it must not be "
            f"0 — libzstd reads 0 as 'no dictionary', so every frame written against a dictionary "
            f"stamped 0 would claim to be undicted."
        )
    stamped = bytearray(raw)
    stamped[4:8] = dict_id.to_bytes(4, "little")
    return bytes(stamped)


class DictionaryTrainer:
    """Trains a candidate dictionary, scores it against the incumbent, and installs it if it wins.

    **It takes the whole `corpus:` config block**, where `CorpusWriter` takes plain values. The
    asymmetry is deliberate and worth stating, since the two classes otherwise mirror each other:
    the trainer reads **six of the nine keys** — `dir` and `compress_level_zstd` from the top level,
    and all four under `retrain` — so plain values would mean six arguments, and Task 14e's
    per-run CLI overrides are one `model_copy(update=…)` of the block against six threaded
    parameters. `CorpusWriter` reads four and never sees `retrain` at all.

    **What this class does not yet do**, so nobody reads its absence as a gap: the thread, the
    trigger, the single-flight lock and the `retrain.log` are Task 14a's; the leave-one-session-out
    split, `INSTALL_MARGIN` and the widening rule are Task 14b's. `consider` takes the margin as an
    argument for exactly that reason — this task builds the machinery, not the rule.
    """

    def __init__(self, corpus: Corpus) -> None:
        self._corpus = corpus
        self._retrain = corpus.retrain
        self._logger = get_logger()
        self._thread: threading.Thread | None = None
        self._thread_lock = threading.Lock()
        self._rollover_allowed: bool | None = None
        """`None` until a run has measured the training wall clock. **Not `False`**, because the
        two are different states: nothing measured yet falls back to what `retrain.log` remembers,
        while `False` is a measurement that came in over `TRAIN_BUDGET_S`."""

    @property
    def dicts_dir(self) -> Path:
        """`<dir>/dicts/` — **the source**. The trainer writes here and the router reads here, and
        that file is the entire interface between them: the trainer publishes nothing else, which
        is what lets a `--train-dict` run in a *separate process* be picked up by a router that is
        already running."""
        return self._corpus.dir / "dicts"

    def incumbent(self) -> Path | None:
        """The dictionary a candidate has to beat, or `None` if there is not one yet."""
        return newest_dictionary(self.dicts_dir)

    def train(
        self, samples: list[bytes], *, maxdict: int | None = None, k: int | None = None
    ) -> Candidate:
        """Train one dictionary from `samples` and stamp our own ID into it.

        **The order is train, then derive, then stamp — and it cannot be otherwise.** The plan
        offers two routes for the ID, `train_dictionary(dict_id=)` or a rewrite of bytes `[4:8]`,
        and both work; but a *content-derived* ID does not exist until the content does, so passing
        it to `train_dictionary` would mean training twice for a file identical to this one.
        Re-stamping is measured idempotent and the compressed output is unchanged.

        **`k` is passed explicitly and that is not tidiness.** `zstandard` trains with COVER, and
        asked to choose `k` itself on a corpus this small it picks one up to **15% worse** than
        `zstd --train`'s default — while `k=8000` is 13% *better*. The library's own optimiser is a
        trap at this sample count, and comparing the two tools at their defaults leads to the wrong
        conclusion about which tool to use. **The tool is not the variable; `k` is.**
        """
        size = maxdict if maxdict is not None else self._retrain.maxdict
        segment = k if k is not None else self._retrain.k
        started = time.monotonic()
        try:
            trained = zstandard.train_dictionary(
                size,
                samples,
                k=segment,
                d=TRAIN_D,
                level=TRAIN_LEVEL,
            )
        except zstandard.ZstdError as exc:
            raise CorpusError(
                f"Training a dictionary from {len(samples)} sample(s) failed: {exc}. "
                f"libzstd needs a viable amount of material; too few or too small samples is the "
                f"usual cause."
            ) from exc
        elapsed = time.monotonic() - started

        raw = trained.as_bytes()
        dict_id = content_dict_id(raw)
        return Candidate(
            raw=stamp(raw, dict_id),
            dict_id=dict_id,
            samples=len(samples),
            maxdict=size,
            k=segment,
            train_seconds=elapsed,
        )

    def score(self, dictionary: bytes | None, samples: list[bytes]) -> int:
        """Total compressed bytes over `samples`, at the level the write path actually stores at.

        **`corpus.compress_level_zstd`, never `TRAIN_LEVEL`.** The question a score answers is
        *which dictionary compresses better in production*, so it has to be asked at the level
        production uses — and reading the config key rather than a constant that merely equals it
        today is what keeps that sentence true when an operator edits the key.

        `None` scores the samples undicted, which is what the incumbent side looks like on a fresh
        install.
        """
        level = self._corpus.compress_level_zstd
        compressor = (
            zstandard.ZstdCompressor(level=level)
            if dictionary is None
            else zstandard.ZstdCompressor(
                level=level, dict_data=zstandard.ZstdCompressionDict(dictionary)
            )
        )
        return sum(len(compressor.compress(sample)) for sample in samples)

    def consider(
        self, candidate: Candidate, holdout: list[bytes], margin: float
    ) -> Verdict:
        """Score the candidate against the incumbent on `holdout`, and decide.

        **`holdout` must be material neither side trained on**, and choosing it is Task 14b's job,
        not this method's. Both biases are live and run in opposite directions: scored on the
        training day the candidate always wins, because it has seen those bodies and the incumbent
        has not; scored anywhere inside a rolling window the *incumbent* wins, because that is
        material it was trained on. Handing the slice in keeps this method honest about which
        question it is answering.

        **With no incumbent, any candidate that trained is installed** — the ordinary first case.

        `margin` is a parameter rather than `INSTALL_MARGIN` read from this module, because Task 14b
        owns the rule and Task 14e's `--tune-dict` never installs at all. The candidate must beat
        the incumbent by **more than** the margin, not merely match it.
        """
        plaintext = sum(len(sample) for sample in holdout)
        candidate_bytes = self.score(candidate.raw, holdout)
        incumbent = self.incumbent()

        if incumbent is None:
            return Verdict(
                installed=True,
                reason="no incumbent",
                plaintext_bytes=plaintext,
                candidate_bytes=candidate_bytes,
                incumbent_bytes=None,
                score_level=self._corpus.compress_level_zstd,
            )

        incumbent_bytes = self.score(incumbent.read_bytes(), holdout)
        improvement = (
            (incumbent_bytes - candidate_bytes) / incumbent_bytes if incumbent_bytes else 0.0
        )
        installed = improvement > margin
        return Verdict(
            installed=installed,
            reason=(
                f"beats {incumbent.name} by {improvement:.2%} (margin {margin:.2%})"
                if installed
                else f"does not beat {incumbent.name} by the margin: "
                f"{improvement:.2%} against {margin:.2%}"
            ),
            plaintext_bytes=plaintext,
            candidate_bytes=candidate_bytes,
            incumbent_bytes=incumbent_bytes,
            score_level=self._corpus.compress_level_zstd,
        )

    def install(self, candidate: Candidate) -> Path:
        """Put the candidate in `<dir>/dicts/` under a name that carries its stamp and its date.

        `req-<UTC>-<dictID>.dict`, written through `.incoming/` and renamed into place. **Atomic
        because a router reads this folder while a trainer writes it** — installed in place, a
        router starting mid-write would load a truncated dictionary. It is also what makes the
        training thread safe to abandon at shutdown: a run killed mid-flight publishes nothing.

        **The staging folder is dot-prefixed** where a day's `incoming/` is not, and the difference
        is real: this folder is *listed* by the worker's pickup rescan, so staging has to stay out
        of that listing. A day's `incoming/` sits among named siblings that nothing globs.
        """
        stamp_utc = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
        destination = self.dicts_dir / f"req-{stamp_utc}-{candidate.hex_id}.dict"
        destination.parent.mkdir(parents=True, exist_ok=True)
        write_atomically(candidate.raw, destination, self.dicts_dir / ".incoming")
        self._logger.info(
            "Corpus: installed dictionary %s (%d bytes, trained on %d sample(s) in %.2fs)",
            destination.name,
            len(candidate.raw),
            candidate.samples,
            candidate.train_seconds,
        )
        return destination

    # -- the material -----------------------------------------------------------------------

    def complete_days(self) -> list[str]:
        """Every day folder that has finished, oldest first.

        **Today is excluded and that is the point.** A day still being written is material the
        window would see a different amount of on every run, and a dictionary trained on half a day
        is scored against an incumbent that saw all of a different one.
        """
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        return sorted(
            path.name
            for path in self._corpus.dir.glob("[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
            if path.is_dir() and path.name < today
        )

    def window(self, *, window_days: int | None = None) -> list[str]:
        """The complete days to train from, oldest first.

        **`window_days` is a minimum, not a fixed count.** It is widened into older complete days
        until the window holds `MIN_SESSIONS` sessions, capped at `WINDOW_MAX_DAYS` — because the
        split below cannot run on a window carrying one session, and one harness on one laptop
        produces single-session days as the ordinary case.
        """
        available = self.complete_days()
        if not available:
            return []

        # `window_days: 0` disables *automatic* retraining rather than describing a zero-day window,
        # so a hand-run that reaches here treats it as one day. `start()` is what refuses the
        # automatic path, and it never gets this far.
        minimum = max(1, window_days if window_days is not None else self._retrain.window_days)
        chosen = available[-minimum:]

        while (
            len(chosen) < min(WINDOW_MAX_DAYS, len(available))
            and len(self._sessions_across(chosen)) < MIN_SESSIONS
        ):
            chosen = available[-(len(chosen) + 1) :]
        return chosen

    def samples_in(self, day: str, *, seen: set[str] | None = None) -> dict[str, bytes]:
        """Every request body in one day worth training on, by digest.

        **Read through `CorpusReader`**, so each blob is verified against the digest in its own
        filename on the way past — training on a corrupted body would be silent otherwise.

        **No dedup is needed within a day** — content addressing means the store holds one blob per
        distinct body. Across a widened window duplicates return, and there the filename *is* the
        digest, so `seen` costs one `set()`.
        """
        reader = CorpusReader(self._corpus.dir / day)
        found: dict[str, bytes] = {}
        for blob in reader.blobs("requests"):
            digest = blob.stem
            if seen is not None and digest in seen:
                continue
            try:
                body = reader.read(blob)
            except CorpusError as exc:
                # One unreadable blob must not cost the whole retrain. It is named, not swallowed.
                self._logger.warning("Corpus: skipping %s while sampling: %s", blob.name, exc)
                continue
            if len(body) < self._retrain.sample_min_bytes:
                continue
            found[digest] = body
            if seen is not None:
                seen.add(digest)
        return found

    def _sessions_in(self, day: str) -> dict[str, str]:
        """`request_ref` digest → `session_id`, read from one day's index.

        **The index is read for the split even though sampling does not need it.** Session
        membership is not in the blob store — a blob is bytes and a filename — so the only record
        of which call belonged to which session is the row that described it.
        """
        index = self._corpus.dir / day / "index.csv"
        if not index.exists():
            return {}
        membership: dict[str, str] = {}
        with open(index, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                digest = (row.get("request_ref") or "").strip()
                # A ref cell holds a 64-character digest or a sentinel word, and a word can never
                # be mistaken for one -- which is the whole reason the sentinels are words.
                if len(digest) == 64:
                    membership[digest] = (row.get("session_id") or "").strip()
        return membership

    def _sessions_across(self, days: list[str]) -> set[str]:
        found: set[str] = set()
        for day in days:
            found.update(session for session in self._sessions_in(day).values() if session)
        return found

    def split(self, days: list[str]) -> tuple[list[bytes], list[bytes]]:
        """Leave-one-session-out: `(training samples, held-out slice)`.

        **The held-out slice is the largest session of the newest complete day, and both halves of
        that matter.** Score on the day the candidate trained on and the candidate always wins — it
        has seen those bodies and the incumbent has not, which does not weaken the refuse-a-worse-one
        rule but **reverses** it. Score anywhere inside a rolling window and the opposite bias
        appears, because that is material the *incumbent* trained on, so good candidates are refused
        forever. **The newest complete day is the only material the incumbent certainly has not
        seen**, and the candidate excludes it by construction.

        The largest session rather than any session, so the slice is the most substantial one
        available; at the default window of one day, the window and the newest day are the same
        thing and this is the clean case.
        """
        if not days:
            return [], []

        seen: set[str] = set()
        # Newest first, so the widened older days yield to the newest on a duplicate rather than
        # the other way round -- the newest day is the one whose session membership decides.
        by_day = {day: self.samples_in(day, seen=seen) for day in reversed(days)}

        newest = days[-1]
        membership = self._sessions_in(newest)
        sessions = Counter(
            membership.get(digest, "") for digest in by_day[newest] if membership.get(digest)
        )
        holdout_session = sessions.most_common(1)[0][0] if sessions else None

        training: list[bytes] = []
        holdout: list[bytes] = []
        for day, bodies in by_day.items():
            for digest, body in bodies.items():
                on_the_slice = (
                    day == newest
                    and holdout_session is not None
                    and membership.get(digest) == holdout_session
                )
                (holdout if on_the_slice else training).append(body)
        return training, holdout

    def external_split(self, source: Path) -> tuple[list[bytes], list[bytes]]:
        """`(training samples, held-out slice)` from a directory that is **not** a corpus.

        **Each immediate subdirectory is one session.** `logs/corpus-gate/` holds `run-01-anthropic`,
        `run-02-lmstudio` and `run-03-anthropic`, so the leave-one-session-out rule runs unchanged
        and the result stays comparable with the figures already frozen in this phase's `evidence/`.
        Owner's decision, 2026-08-20.

        **A `requests/` folder inside a session is used if it is there**, and the session's own files
        otherwise. Only request bodies train a request dictionary; `responses/` is never read.

        **Nothing is deduplicated, deliberately.** `gate.py` did not, and every published ratio was
        measured on the raw list — so deduplicating here would silently stop this being the same
        measurement. The automatic path *does* dedup, because the store is content-addressed and
        cannot hold a repeat, and that difference is real rather than an inconsistency: these are
        loose files that were never content-addressed. **The distinct count is reported** so the
        training-set composition travels with the number.
        """
        sessions: dict[str, list[bytes]] = {}
        for child in sorted(p for p in source.iterdir() if p.is_dir()):
            folder = child / "requests" if (child / "requests").is_dir() else child
            bodies = [
                body
                for path in sorted(folder.iterdir())
                if path.is_file() and path.stat().st_size >= self._retrain.sample_min_bytes
                for body in [path.read_bytes()]
                if not _is_zstd_dictionary(body)
            ]
            if bodies:
                sessions[child.name] = bodies

        if len(sessions) < MIN_SESSIONS:
            self._logger.warning(
                "Corpus: %s holds %d session(s) with usable bodies; %d are needed to hold one out. "
                "Each immediate subdirectory counts as a session.",
                source,
                len(sessions),
                MIN_SESSIONS,
            )
            return [], []

        # **The last session by name is held out, not the largest.** For `logs/corpus-gate/` that is
        # `run-03-anthropic`, which reproduces `gate.py`'s own split -- train on run-01 + run-02,
        # score on run-03 -- and comparability with the figures already frozen in `evidence/` is the
        # entire reason "one subdirectory is one session" was chosen. Holding out the *largest*
        # would also invert the intent: run-01 is 46 of the 70 usable bodies, so the majority of the
        # material would be held out and the minority trained on.
        held_out_name = max(sessions)
        holdout = sessions.pop(held_out_name)
        training = [body for bodies in sessions.values() for body in bodies]
        self._logger.info(
            "Corpus: training on %d sample(s) from %s, holding out %d from %s",
            len(training),
            ", ".join(sorted(sessions)),
            len(holdout),
            held_out_name,
        )
        return training, holdout

    def tune(
        self,
        training: list[bytes],
        holdout: list[bytes],
        *,
        maxdicts: tuple[int, ...] = TUNE_MAXDICT,
        ks: tuple[int, ...] = TUNE_K,
    ) -> list[tuple[int, int, int, int, float]]:
        """Sweep `maxdict` x `k` and return the **whole surface**: one row per combination.

        **It never installs**, and the caller prints every row rather than a winner. Training is
        **non-monotonic in both axes** — measured on both trainers — so "the best cell" is a property
        of this corpus and this slice, not a recommendation. A tool that printed only the winner
        would be inviting exactly the reading the measurement refuses.

        Rows are `(maxdict, k, dictionary bytes, scored bytes, ratio)`, scored at
        `corpus.compress_level_zstd` like every other comparison here.
        """
        plaintext = sum(len(sample) for sample in holdout)
        surface: list[tuple[int, int, int, int, float]] = []
        for maxdict in maxdicts:
            for k in ks:
                try:
                    candidate = self.train(training, maxdict=maxdict, k=k)
                except CorpusError as exc:
                    self._logger.warning("Corpus: maxdict=%d k=%d did not train: %s", maxdict, k, exc)
                    continue
                scored = self.score(candidate.raw, holdout)
                surface.append((maxdict, k, len(candidate.raw), scored, plaintext / scored))
        return surface

    # -- the guard, the lock and the log ------------------------------------------------------

    @property
    def retrain_log(self) -> Path:
        """`<dir>/retrain.log` — one line per attempt.

        **It sits at the corpus root rather than in `dicts/` or in a day.** `dicts/` is relisted by
        the worker's pickup, and a day folder would make training state something a day *needs* —
        which is the direction the self-containment rule actually forbids. Nothing reads this to
        read a day.
        """
        return self._corpus.dir / "retrain.log"

    @property
    def retrain_lock(self) -> Path:
        return self._corpus.dir / "retrain.lock"

    def trained_today(self) -> bool:
        """Whether an attempt has already been made today.

        **A refusal counts, and that is the half worth stating.** Recording only installs would mean
        a candidate that loses is retrained from identical input on every restart, forever, for a
        verdict that cannot change.

        Both sources are read because they fail differently: the dictionary name survives a deleted
        log, and the log records the attempts that installed nothing.
        """
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        for path in self.dicts_dir.glob(f"req-{today}T*.dict"):
            if path.is_file():
                return True
        if self.retrain_log.exists():
            for line in self.retrain_log.read_text(encoding="utf-8").splitlines():
                if line.startswith(today):
                    return True
        return False

    def _record(self, fields: dict[str, str]) -> None:
        """Append one line to `retrain.log`. **Never raises** — a lost log line is not worth a
        crashed thread, and the caller is a daemon nobody is watching."""
        line = " ".join(f"{key}={value}" for key, value in fields.items())
        stamped = f"{datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')} {line}\n"
        try:
            self.retrain_log.parent.mkdir(parents=True, exist_ok=True)
            with open(self.retrain_log, "a", encoding="utf-8") as handle:
                handle.write(stamped)
        except OSError as exc:
            self._logger.warning("Corpus: could not write the retrain log: %s", exc)

    def _acquire(self) -> bool:
        """Take the cross-process training lock, or report that somebody else holds it.

        **Across processes, not merely across threads** — `--train-dict` is deliberately another
        process, so an in-process lock would let a hand-run and an automatic run train at once.

        `O_EXCL` rather than `flock`, because the failure being guarded is a **killed** process:
        `flock` is released by the kernel when its holder dies, which would make `LOCK_STALE_S`
        dead code and leave nothing to break. The cost of this choice is that a `kill -9` leaves the
        lock behind, which is exactly what the age check is for.

        **The age comes from inside the file, never from its mtime** — `logs/` sits in a
        cloud-synced folder here and a sync rewrites mtimes, which is the same reason a dictionary's
        name leads with a UTC stamp.
        """
        self.retrain_lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            handle = os.open(self.retrain_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            if not self._break_stale_lock():
                return False
            try:
                handle = os.open(self.retrain_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                # Somebody else won the race to re-take it. One trainer is all that was wanted.
                return False
        with os.fdopen(handle, "w") as writer:
            writer.write(f"pid={os.getpid()} since={time.time():.0f}\n")
        return True

    def _break_stale_lock(self) -> bool:
        try:
            held = self.retrain_lock.read_text(encoding="utf-8")
            since = float(held.split("since=")[1].split()[0])
        except (OSError, IndexError, ValueError):
            # An unreadable or malformed lock is itself a leftover from something that died badly.
            since = 0.0
        age = time.time() - since
        if age < LOCK_STALE_S:
            self._logger.info(
                "Corpus: another dictionary training run holds the lock (%.0fs old); skipping.", age
            )
            return False
        self._logger.warning(
            "Corpus: breaking a retrain lock %.0fs old (over %ds); its process is presumed dead.",
            age,
            LOCK_STALE_S,
        )
        self.retrain_lock.unlink(missing_ok=True)
        return True

    def _release(self) -> None:
        self.retrain_lock.unlink(missing_ok=True)

    # -- the run, and the thread it happens on -------------------------------------------------

    def run(
        self,
        *,
        bypass_guard: bool = False,
        window_days: int | None = None,
        source: Path | None = None,
    ) -> Verdict | None:
        """One training attempt, end to end. `None` when it did not get as far as a verdict.

        **Never raises.** Every exit is a log line and, where an attempt was really made, a
        `retrain.log` entry. The caller is a daemon thread nobody is watching, and a body store is
        telemetry-shaped: it does not get to break a call, and it does not get to end quietly
        either.

        `bypass_guard` is Task 14e's `--train-dict`: typing the command is explicit consent to
        retrain today. **It does not bypass the margin** — a hand-run cannot install a dictionary
        that loses.
        """
        if not bypass_guard and self.trained_today():
            self._logger.info(
                "Corpus: a dictionary or a retrain-log line already exists for today; not training."
            )
            return None

        if not self._acquire():
            return None
        try:
            # **Checked again under the lock**, and the first check is not redundant. Two processes
            # can both pass it, then queue on the lock -- and the loser would wake up and retrain
            # from exactly the material the winner has just trained on. Checking only here would
            # mean taking the lock to discover there was nothing to do; checking only above leaves
            # the race. The cheap check goes first and the correct one goes second.
            if not bypass_guard and self.trained_today():
                self._logger.info(
                    "Corpus: another run trained while this one waited for the lock; not training."
                )
                return None
            return self._attempt(window_days, source)
        except Exception as exc:  # noqa: BLE001 — a trainer never raises into the router
            self._logger.warning(
                "Corpus: dictionary training failed: %s: %s", type(exc).__name__, exc
            )
            self._record({"verdict": "failed", "error": f"{type(exc).__name__}"})
            return None
        finally:
            self._release()

    def _attempt(self, window_days: int | None, source: Path | None = None) -> Verdict | None:
        started = time.monotonic()

        if source is not None:
            # `--from`: the material comes from somewhere that is not a corpus, and **only the
            # material does.** The lock, `retrain.log` and the install all stay under `corpus.dir`,
            # so a hand-run is recorded in the same log as every automatic one and the dictionary
            # lands where the router will actually read it. Owner's decision, 2026-08-20.
            days: list[str] = []
            training, holdout = self.external_split(source)
            window = str(source)
        else:
            days = self.window(window_days=window_days)
            if not days:
                # A fresh install trains nothing on its first day, and that is correct: the store
                # writes undicted frames meanwhile, at ~3.1x, and they stay valid forever.
                self._logger.info("Corpus: no complete day to train from yet; not training.")
                self._record({"verdict": "skipped", "reason": "no-complete-day"})
                return None
            training, holdout = self.split(days)
            window = f"{days[0]}..{days[-1]}" if len(days) > 1 else days[0]
        if not training or not holdout:
            # Below a viable sample count. The floor is libzstd's own rather than a number invented
            # here -- see `train`, which reports what it refused and why.
            self._logger.info(
                "Corpus: %s holds %d training and %d held-out sample(s); not enough to train.",
                window,
                len(training),
                len(holdout),
            )
            self._record(
                {
                    "verdict": "skipped",
                    "reason": "too-few-samples",
                    "window": window,
                    "samples": str(len(training)),
                    "holdout": str(len(holdout)),
                }
            )
            return None

        candidate = self.train(training)
        verdict = self.consider(candidate, holdout, INSTALL_MARGIN)
        installed = self.install(candidate) if verdict.installed else None
        elapsed = time.monotonic() - started

        self._record(
            {
                "verdict": "installed" if verdict.installed else "refused",
                "window": window,
                "days": str(len(days)),
                "samples": str(candidate.samples),
                "holdout": str(len(holdout)),
                "candidate": f"{verdict.candidate_ratio:.3f}x",
                "incumbent": (
                    f"{verdict.incumbent_ratio:.3f}x" if verdict.incumbent_ratio else "none"
                ),
                "level": str(verdict.score_level),
                # The wall clock is on the line so `TRAIN_BUDGET_S` survives a restart -- see
                # `_budget_permits_rollover`.
                "seconds": f"{candidate.train_seconds:.2f}",
                "total_seconds": f"{elapsed:.2f}",
                "dict": installed.name if installed else "-",
            }
        )
        self._apply_budget(candidate.train_seconds)
        return verdict

    def _apply_budget(self, train_seconds: float) -> None:
        """Decide whether day-rollover may trigger training, from what training actually cost.

        **This applies the owner's rule; it does not choose a policy.** At or under
        `TRAIN_BUDGET_S`, both triggers; above it, startup only.
        """
        self._rollover_allowed = train_seconds <= TRAIN_BUDGET_S
        near = TRAIN_BUDGET_S * 0.5 <= train_seconds <= TRAIN_BUDGET_S
        self._logger.info(
            "Corpus: training took %.2fs against a %ds budget; day-rollover training is %s.%s",
            train_seconds,
            TRAIN_BUDGET_S,
            "on" if self._rollover_allowed else "off (startup only)",
            # Said out loud rather than left in a number, because the widening rule is what would
            # push this over: a window that has to reach back for a second session trains on more.
            " This is close to the budget -- widening the window could push it over."
            if near
            else "",
        )

    def _budget_permits_rollover(self) -> bool:
        """Whether a *previous* run measured a training time inside the budget.

        **Read back from `retrain.log` rather than kept only in memory.** Without it, a router that
        starts at 23:00 and is guarded — because it already trained earlier today — reaches midnight
        having measured nothing, so the rollover trigger it is entitled to would never register.
        """
        if self._rollover_allowed is not None:
            return self._rollover_allowed
        if not self.retrain_log.exists():
            return False
        try:
            lines = self.retrain_log.read_text(encoding="utf-8").splitlines()
        except OSError:
            return False
        for line in reversed(lines):
            for field in line.split():
                if field.startswith("seconds="):
                    try:
                        return float(field.removeprefix("seconds=")) <= TRAIN_BUDGET_S
                    except ValueError:
                        return False
        return False

    # -- the thread ------------------------------------------------------------------------------

    def start(self) -> None:
        """Start the startup training run, in a daemon thread of its own.

        **A plain `threading.Thread`, and the three async-shaped answers are all wrong** —
        `BackgroundTask` is awaited inside a request's ASGI cycle and is per-request,
        `run_in_threadpool` occupies a slot in the shared pool every sync offload uses, and
        `asyncio.create_task` is the one that would genuinely pause the router, CPU-bound work on
        the loop blocking every concurrent request. `docs/wiki/background-work-in-fastapi.md` has
        the reading. `lifespan` is not a mechanism at all, but it is the right *place*.

        **Daemon, and it needs no drain.** The install is `write → fsync → rename`, so a run killed
        mid-flight publishes nothing — no half-written dictionary is ever visible under a name the
        router would load. That is a different rule from the corpus worker, which drains with a
        timeout because it is holding bodies that exist nowhere else, and the difference is
        deliberate.

        **`retrain.window_days: 0` stops it here**, which is the second of the block's two
        independent off switches; `corpus.enabled` is the first, and the caller owns that one.
        """
        self._sweep_staging()
        if self._retrain.window_days == 0:
            self._logger.info(
                "Corpus: automatic dictionary retraining is off (retrain.window_days: 0); "
                "the newest installed dictionary keeps being used."
            )
            return
        self._spawn("corpus-trainer")

    def on_day_rollover(self) -> None:
        """Called by the corpus worker when it opens a day folder that is not the one it had.

        **Only if the measured wall clock permits it.** UTC midnight is an arbitrary local hour, so
        a long training run firing unattended mid-afternoon beside a local model is what
        `TRAIN_BUDGET_S` exists to prevent.
        """
        if self._retrain.window_days == 0 or not self._budget_permits_rollover():
            return
        self._spawn("corpus-trainer-rollover")

    def _spawn(self, name: str) -> None:
        """One training run at a time **inside this process**, on top of the cross-process lock.

        The file lock is what stops two *processes* training at once; this stops the worker
        spawning a second thread while the first is still going, which the lock would only turn
        into a thread that starts and immediately gives up.
        """
        with self._thread_lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._thread = threading.Thread(target=self._run_quietly, name=name, daemon=True)
            self._thread.start()

    def _run_quietly(self) -> None:
        try:
            self.run()
        except Exception as exc:  # noqa: BLE001 — a thread that dies loudly still must not raise
            self._logger.warning(
                "Corpus: the training thread stopped: %s: %s", type(exc).__name__, exc
            )

    def _sweep_staging(self) -> None:
        """Remove dictionary staging files a killed run left behind.

        A partial file in `.incoming/` is harmless and invisible to any reader — the pickup lists
        `dicts/` and a dot-prefixed folder is not in that listing — but *"a killed run leaves no
        trace"* is only true if somebody sweeps. **Nothing is created here**: a corpus that has
        never written has no staging folder to clean.
        """
        staging = self.dicts_dir / ".incoming"
        if not staging.is_dir():
            return
        for leftover in staging.glob("*.tmp"):
            try:
                leftover.unlink()
            except OSError as exc:  # one bad file must not stop the sweep
                self._logger.warning("Corpus: could not remove stale %s: %s", leftover.name, exc)
