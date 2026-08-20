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

import hashlib
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import zstandard

from .config import Corpus
from .corpus import CorpusError, newest_dictionary, write_atomically
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

    def train(self, samples: list[bytes]) -> Candidate:
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
        started = time.monotonic()
        try:
            trained = zstandard.train_dictionary(
                self._retrain.maxdict,
                samples,
                k=self._retrain.k,
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
            maxdict=self._retrain.maxdict,
            k=self._retrain.k,
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
