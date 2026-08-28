"""The trainer: the stamped ID, the trained candidate, the score, the refusal and the install.

**The claim these tests exist for is that a dictionary can be identified by its bytes.** libzstd's
own ID cannot do it — `zstd --train` stamps `1` on everything, and the same samples at levels 3, 9
and 19 give one ID and three different files. `test_our_id_separates_what_libzstds_conflates` is the
test that makes that a check rather than a claim, and it is written to fail if the derivation is
ever quietly replaced by `ZstdCompressionDict.dict_id()`.

The refusal tests matter for a reason the numbers hide: training is **non-monotonic** in both `k`
and `maxdict`, so a candidate with better-looking parameters can be a worse dictionary. Nothing
here may assume a new dictionary is an improvement.
"""

from __future__ import annotations

import csv
import os
import threading
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest
import zstandard
from conftest import CLAUDE_BODY, Rows, Upstream, make_config
from fastapi.testclient import TestClient

from ilirium_llm_router.app import create_app
from ilirium_llm_router.config import Corpus, Retrain
from ilirium_llm_router.corpus import (
    ABSENT,
    INDEX_COLUMNS,
    NO_DICTIONARY,
    RESCAN_EVERY,
    CorpusError,
    CorpusReader,
    CorpusWriter,
    newest_dictionary,
)
from ilirium_llm_router.dictionary import (
    DICT_MAGIC,
    LOCK_STALE_S,
    MIN_SESSIONS,
    TRAIN_BUDGET_S,
    TRAIN_D,
    TRAIN_LEVEL,
    Candidate,
    DictionaryTrainer,
    _id_from_digest,
    content_dict_id,
    stamp,
)
from ilirium_llm_router.stats import CallRecord

# Small, cheap and repetitive on purpose: a dictionary only has something to learn if the samples
# share material, which is exactly what a corpus of LLM request bodies looks like -- one large
# fixed preamble in front of a little variation.
PREAMBLE = (
    b'{"model":"claude-opus-5","system":"You are a helpful assistant.",'
    b'"tools":[],"messages":['
)


def bodies(count: int = 60, seed: int = 0) -> list[bytes]:
    """`count` distinct bodies that share a preamble, as real request bodies do.

    **Each body is comfortably over `sample_min_bytes`**, which is 1,024 by default — material
    below the floor is correctly refused by the trainer, and a helper that produced it would be
    testing the floor rather than whatever the test meant to test.

    **The trailing marker is what makes them distinct**, and it is not decoration: without it the
    generator repeats every 26 payloads, and the store — which is content-addressed — collapses the
    repeats into one blob. A test that built two sessions out of colliding bodies would then find
    one session, which is how this helper was wrong the first time.
    """
    return [
        PREAMBLE
        + b'{"role":"user","content":"'
        + bytes([65 + (i + seed) % 26]) * 1200
        + f"-{seed}-{i}".encode()
        + b'"}]}'
        for i in range(count)
    ]


def trainer(
    tmp_path: Path, *, level: int = 9, maxdict: int = 16_384, k: int = 200
) -> DictionaryTrainer:
    """A trainer pointed at a temporary corpus directory.

    `maxdict` and `k` are far below the shipped defaults because these samples are far below a real
    corpus; the values under test are `TRAIN_LEVEL` and `TRAIN_D`, which are constants, not these.
    """
    return DictionaryTrainer(
        Corpus(
            enabled=True,
            dir=tmp_path,
            compress_level_zstd=level,
            retrain=Retrain(maxdict=maxdict, k=k),
        )
    )


# -- the constants the register fixes ---------------------------------------------------------


def test_the_training_constants_are_what_the_register_says() -> None:
    """**Training is 3 and archiving is 9, and conflating them is the trap of this phase.**

    Task 24 checks the register row by row; this fails first and closer to the code.
    """
    assert TRAIN_LEVEL == 3
    assert TRAIN_D == 8


def test_training_level_is_not_the_scoring_level() -> None:
    """Scoring follows the **config key**, so an operator editing it moves the comparison with it.

    A constant that merely equals the key today is a coincidence with a fuse in it: the scoring
    level would silently stop being the level anything writes at.
    """
    at_nine = trainer(Path("/nonexistent"), level=9)
    at_nineteen = trainer(Path("/nonexistent"), level=19)
    holdout = bodies(4)
    candidate = trainer(Path("/nonexistent")).train(bodies(40))

    assert at_nine.score(candidate.raw, holdout) != at_nineteen.score(candidate.raw, holdout)


# -- the ID we stamp ourselves -----------------------------------------------------------------


def test_the_id_is_derived_from_content_and_is_in_range() -> None:
    raw = zstandard.train_dictionary(16_384, bodies(), k=200, d=8, level=3).as_bytes()
    dict_id = content_dict_id(raw)

    assert 1 <= dict_id <= 0xFFFFFFFF
    assert content_dict_id(raw) == dict_id, "the derivation must be a pure function of the bytes"


def test_stamping_is_idempotent_because_the_id_field_is_zeroed_first() -> None:
    """**The property that makes the ID usable at all.**

    The ID lives inside the bytes being hashed, so without zeroing the field the derivation would
    be a self-reference: stamping would change the content, which would change the ID, which would
    no longer match what was stamped.
    """
    raw = zstandard.train_dictionary(16_384, bodies(), k=200, d=8, level=3).as_bytes()
    once = stamp(raw, content_dict_id(raw))
    twice = stamp(once, content_dict_id(once))

    assert content_dict_id(once) == content_dict_id(raw)
    assert once == twice


def test_a_stamped_dictionary_reports_the_id_we_gave_it() -> None:
    raw = zstandard.train_dictionary(16_384, bodies(), k=200, d=8, level=3).as_bytes()
    stamped = stamp(raw, content_dict_id(raw))

    assert zstandard.ZstdCompressionDict(stamped).dict_id() == content_dict_id(raw)


def test_a_frame_written_against_it_carries_that_id(tmp_path: Path) -> None:
    """The whole no-recompression rule rests on a frame naming its own dictionary."""
    candidate = trainer(tmp_path).train(bodies())
    dictionary = zstandard.ZstdCompressionDict(candidate.raw)
    frame = zstandard.ZstdCompressor(level=9, dict_data=dictionary).compress(b"a body")

    assert zstandard.get_frame_parameters(frame).dict_id == candidate.dict_id


def test_our_id_separates_what_libzstds_conflates() -> None:
    """**Measured, not theoretical: libzstd gives one ID for three different files.**

    Its ID is derived from content that `k`, `d` and the samples fix, and does not cover the
    entropy tables the level layers on top. Ours does, because it hashes the file.
    """
    samples = bodies()
    at_levels = [
        zstandard.train_dictionary(16_384, samples, k=200, d=8, level=level).as_bytes()
        for level in (3, 9, 19)
    ]

    assert len({raw for raw in at_levels}) == 3, "three levels should give three different files"
    assert len({zstandard.ZstdCompressionDict(raw).dict_id() for raw in at_levels}) == 1
    assert len({content_dict_id(raw) for raw in at_levels}) == 3


def test_stamping_refuses_bytes_that_are_not_a_dictionary() -> None:
    """Without the magic check this writes four bytes into the middle of something else and hands
    back bytes that look stamped."""
    with pytest.raises(CorpusError, match="not the bytes of a zstd dictionary"):
        stamp(b"this is not a dictionary at all", 12345)


@pytest.mark.parametrize("dict_id", [0, -1, 2**32, 2**40])
def test_stamping_refuses_an_id_libzstd_would_have_swallowed(dict_id: int) -> None:
    """**`train_dictionary(dict_id=2**32)` does not raise** — it falls back to libzstd's own ID,
    leaving a dictionary that looks stamped and is not. And 0 means *no dictionary*, so a frame
    written against one stamped 0 would claim to be undicted."""
    raw = zstandard.train_dictionary(16_384, bodies(), k=200, d=8, level=3).as_bytes()

    with pytest.raises(CorpusError, match="not a usable dictionary ID"):
        stamp(raw, dict_id)


def test_a_digest_of_all_zeroes_becomes_1_and_never_0() -> None:
    """**dictID 0 means *no dictionary***, so a hash landing there would make every frame written
    against that dictionary claim to be undicted.

    Tested against `_id_from_digest` rather than `content_dict_id`, because no dictionary can be
    constructed whose sha256 starts with four zero bytes — so through the public function this
    branch is unreachable and a test would pass with the guard deleted.
    """
    assert _id_from_digest(b"\x00" * 32) == 1
    assert _id_from_digest(b"\x00\x00\x00\x01" + b"\x00" * 28) == 1
    assert _id_from_digest(b"\xff\xff\xff\xff" + b"\x00" * 28) == 0xFFFFFFFF


def test_the_magic_number_is_what_a_real_dictionary_starts_with() -> None:
    raw = zstandard.train_dictionary(16_384, bodies(), k=200, d=8, level=3).as_bytes()

    assert int.from_bytes(raw[:4], "little") == DICT_MAGIC


# -- training ----------------------------------------------------------------------------------


def test_train_passes_k_through_rather_than_letting_the_library_choose(tmp_path: Path) -> None:
    """**The library's own `k` is a trap at this sample count** — up to 15% worse than
    `zstd --train`'s default, where an explicit one is 13% better. The tool is not the variable.

    **Asserted behaviourally, through `DictionaryTrainer.train`.** The obvious test — call
    `train_dictionary` directly and read `.k` back off the returned object — exercises the library
    rather than this module, and passes unchanged if `train` stops forwarding `k` at all. Two
    different `k` values must produce two different dictionaries; left to the optimiser both runs
    would pick the same one and the bytes would match.
    """
    narrow = trainer(tmp_path, k=200).train(bodies())
    wide = trainer(tmp_path, k=1500).train(bodies())

    assert narrow.raw != wide.raw
    assert narrow.k == 200 and wide.k == 1500


def test_train_passes_the_dmer_size_through(tmp_path: Path) -> None:
    """`TRAIN_D` is a constant, so it is varied by patching the module — which is the only way to
    tell "the constant is 8" apart from "the constant reaches libzstd"."""
    at_eight = trainer(tmp_path).train(bodies())
    monkey = pytest.MonkeyPatch()
    monkey.setattr("ilirium_llm_router.dictionary.TRAIN_D", 6)
    try:
        at_six = trainer(tmp_path).train(bodies())
    finally:
        monkey.undo()

    assert at_eight.raw != at_six.raw


def test_k_and_d_read_back_as_zero_once_a_dictionary_is_bytes(tmp_path: Path) -> None:
    """The gotcha behind the test above, pinned so nobody rewrites it into the weaker form: the
    training parameters live on the object `train_dictionary` returns and **do not survive a
    round trip through bytes**, which is the only form a dictionary has on disk."""
    trained = zstandard.train_dictionary(16_384, bodies(), k=200, d=TRAIN_D, level=TRAIN_LEVEL)

    assert (trained.k, trained.d) == (200, TRAIN_D)
    assert zstandard.ZstdCompressionDict(trained.as_bytes()).k == 0


def test_a_trained_candidate_carries_its_own_stamp_and_wall_clock(tmp_path: Path) -> None:
    candidate = trainer(tmp_path).train(bodies())

    assert candidate.dict_id == content_dict_id(candidate.raw)
    assert candidate.hex_id == f"{candidate.dict_id:08x}"
    assert len(candidate.hex_id) == 8, "a dictID is a uint32, so 8 hex characters is exact"
    assert candidate.samples == 60
    assert candidate.train_seconds > 0, "Task 14a needs this to apply TRAIN_BUDGET_S"


def test_training_on_nothing_fails_with_a_readable_message(tmp_path: Path) -> None:
    with pytest.raises(CorpusError, match="viable amount of material"):
        trainer(tmp_path).train([])


# -- scoring -----------------------------------------------------------------------------------


def test_a_dictionary_beats_no_dictionary_on_material_like_this(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    candidate = subject.train(bodies())
    holdout = bodies(10, seed=100)

    assert subject.score(candidate.raw, holdout) < subject.score(None, holdout)


# -- the refusal ---------------------------------------------------------------------------------


def test_with_no_incumbent_any_candidate_that_trained_is_installed(tmp_path: Path) -> None:
    """The ordinary first case: the store ships before the trainer does, so the first run has
    nothing to beat."""
    subject = trainer(tmp_path)
    verdict = subject.consider(subject.train(bodies()), bodies(10, seed=100), margin=0.02)

    assert verdict.installed
    assert verdict.reason == "no incumbent"
    assert verdict.incumbent_bytes is None
    assert verdict.incumbent_ratio is None
    assert verdict.improvement is None
    assert verdict.candidate_ratio > 1


def test_an_identical_candidate_is_refused(tmp_path: Path) -> None:
    """Retraining on unchanged material is **byte-identical**, so the improvement is exactly zero.

    Without the guard this is what a daily retrain does on a quiet corpus: install the same
    dictionary again under a new name, forever.
    """
    subject = trainer(tmp_path)
    subject.install(subject.train(bodies()))

    verdict = subject.consider(subject.train(bodies()), bodies(10, seed=100), margin=0.02)

    assert not verdict.installed
    assert "does not beat" in verdict.reason
    assert verdict.improvement == 0.0


def test_a_genuinely_worse_candidate_is_refused(tmp_path: Path) -> None:
    """**The case the refusal mechanism actually exists for**, and the one the identical-candidate
    test above cannot reach.

    Training is **non-monotonic** in both `k` and `maxdict`, so a candidate can be worse than the
    dictionary it would replace while nothing about its parameters looks wrong. Here the incumbent
    knows this material and the candidate does not, so the improvement is **negative** — and a
    comparison written with its operands the wrong way round would install it.
    """
    subject = trainer(tmp_path)
    subject.install(subject.train(bodies()))
    unrelated = [b"nothing whatsoever to do with the corpus " * 30 + bytes([i]) for i in range(60)]

    verdict = subject.consider(subject.train(unrelated), bodies(10, seed=100), margin=0.02)

    assert not verdict.installed
    assert verdict.improvement is not None and verdict.improvement < 0, verdict.reason
    assert verdict.candidate_ratio < verdict.incumbent_ratio  # type: ignore[operator]


def test_a_genuinely_better_candidate_is_installed(tmp_path: Path) -> None:
    """The incumbent here was trained on material unlike the holdout, so the candidate wins by a
    wide margin rather than by noise."""
    subject = trainer(tmp_path)
    unrelated = [b"nothing whatsoever to do with the corpus " * 30 + bytes([i]) for i in range(60)]
    subject.install(subject.train(unrelated))

    verdict = subject.consider(subject.train(bodies()), bodies(10, seed=100), margin=0.02)

    assert verdict.installed
    assert verdict.improvement is not None and verdict.improvement > 0.02
    assert verdict.incumbent_ratio is not None
    assert verdict.candidate_ratio > verdict.incumbent_ratio


def test_the_margin_is_strict_rather_than_inclusive(tmp_path: Path) -> None:
    """*"Must beat the incumbent by **more than** this"* — a candidate that exactly matches the
    margin is refused.

    **Built on a candidate that genuinely wins**, so the improvement under test is a real positive
    number. Run against an identical candidate the improvement is 0.0, and a `>=` comparison would
    pass a weaker version of this test for a reason that has nothing to do with strictness.
    """
    subject = trainer(tmp_path)
    unrelated = [b"nothing whatsoever to do with the corpus " * 30 + bytes([i]) for i in range(60)]
    subject.install(subject.train(unrelated))
    candidate = subject.train(bodies())
    holdout = bodies(10, seed=100)

    measured = subject.consider(candidate, holdout, margin=0.02)
    assert measured.installed and measured.improvement is not None and measured.improvement > 0

    assert not subject.consider(candidate, holdout, margin=measured.improvement).installed
    assert subject.consider(candidate, holdout, margin=measured.improvement - 0.001).installed


def test_the_verdict_records_the_level_it_scored_at(tmp_path: Path) -> None:
    """**Recorded because it is operator-editable.** Two ratios logged on different days are not
    comparable unless the line says what they were scored at."""
    subject = trainer(tmp_path, level=19)
    verdict = subject.consider(subject.train(bodies()), bodies(10, seed=100), margin=0.02)

    assert verdict.score_level == 19


# -- the install -------------------------------------------------------------------------------


def test_install_names_the_file_by_its_stamp_and_its_date(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    candidate = subject.train(bodies())

    installed = subject.install(candidate)

    assert installed.parent == tmp_path / "dicts"
    assert installed.name.startswith("req-")
    assert installed.name.endswith(f"-{candidate.hex_id}.dict")
    assert installed.read_bytes() == candidate.raw


def test_install_leaves_no_staging_file_behind(tmp_path: Path) -> None:
    """`write → fsync → rename`. A router reads this folder while a trainer writes it, so a
    dictionary must appear whole or not at all."""
    subject = trainer(tmp_path)
    subject.install(subject.train(bodies()))

    assert list((tmp_path / "dicts" / ".incoming").glob("*.tmp")) == []


def test_the_staging_folder_is_dot_prefixed_so_the_pickup_does_not_list_it(tmp_path: Path) -> None:
    """The worker relists `<dir>/dicts/` to notice a new dictionary. A half-written file picked up
    as the newest one is the failure the dot-prefix excludes."""
    subject = trainer(tmp_path)
    installed = subject.install(subject.train(bodies()))

    assert (tmp_path / "dicts" / ".incoming").is_dir()
    assert newest_dictionary(tmp_path / "dicts") == installed


def test_the_worker_and_the_trainer_agree_on_which_dictionary_is_current(tmp_path: Path) -> None:
    """**One rule, one function.** The trainer scores against the incumbent and the worker
    compresses against it; two copies of "newest by filename" that disagreed would have each half
    behaving correctly and the pair behaving wrongly, with nothing to report it."""
    subject = trainer(tmp_path)
    first = subject.install(subject.train(bodies()))
    assert subject.incumbent() == first

    second = tmp_path / "dicts" / "req-2099-01-01T000000Z-deadbeef.dict"
    second.write_bytes(first.read_bytes())

    assert subject.incumbent() == second
    assert newest_dictionary(tmp_path / "dicts") == second


def test_an_installed_dictionary_reads_back_as_the_id_it_was_named_for(tmp_path: Path) -> None:
    """The filename and the file's own field must agree, or a reader looking one up by ID finds
    the wrong version of it."""
    subject = trainer(tmp_path)
    installed = subject.install(subject.train(bodies()))

    on_disk = zstandard.ZstdCompressionDict(installed.read_bytes()).dict_id()
    assert installed.name.endswith(f"-{on_disk:08x}.dict")


def test_a_candidate_is_a_value_and_not_a_file(tmp_path: Path) -> None:
    """Training publishes nothing. **The file is the entire interface** between the trainer and a
    running router, and it appears only when `install` is called — which is what lets a refusal
    cost nothing and a `--tune-dict` sweep install nothing at all."""
    subject = trainer(tmp_path)
    candidate = subject.train(bodies())

    assert isinstance(candidate, Candidate)
    assert not (tmp_path / "dicts").exists()


# -- the window, the split, the guard and the thread (Tasks 14a and 14b) -----------------------


def day_folder(root: Path, day: str, bodies_by_session: dict[str, list[bytes]]) -> None:
    """Build a corpus day folder the way `CorpusWriter` would, with an index naming each session.

    The blobs go in through the real writer, so the layout and the digests are the ones the reader
    will meet. **The index is written here rather than by the writer** because the split reads it
    for session membership, and a test needs to say which session a body belonged to.
    """
    writer = CorpusWriter(
        directory=root, compress_level=9, body_max_bytes=1 << 20, queue_max_bytes=1 << 26
    )
    rows: list[list[str]] = []
    try:
        for session, payloads in bodies_by_session.items():
            for body in payloads:
                stored = writer.store(f"{day}T12:00:00.000+00:00", "requests", body)
                rows.append(
                    record(session_id=session).cells()
                    + [stored.digest, ABSENT, "0", "1", "0", stored.dict_id]
                )
    finally:
        writer.close()

    with open(root / day / "index.csv", "w", encoding="utf-8", newline="") as handle:
        out = csv.writer(handle, lineterminator="\r\n")
        out.writerow(INDEX_COLUMNS)
        out.writerows(rows)


TIMESTAMP = "2026-08-19T12:00:00.000+00:00"


def record(**overrides: object) -> CallRecord:
    fields: dict[str, object] = {
        "timestamp": TIMESTAMP,
        "session_id": "session-1",
        "agent_id": "",
        "backend": "anthropic",
        "model": "claude-opus-5",
        "path": "/v1/messages",
        "stream": True,
        "input_tokens": 10,
        "output_tokens": 20,
        "cache_read_input_tokens": None,
        "cache_creation_input_tokens": None,
        "stop_reason": "end_turn",
        "request_bytes": 100,
        "response_bytes": 200,
        "ttfb_ms": 30,
        "duration_ms": 100,
        "error_status": "ok",
        "error_code": "",
        "error_message": "",
    }
    fields.update(overrides)
    return CallRecord(**fields)  # type: ignore[arg-type]


def test_the_window_holds_only_complete_days(tmp_path: Path) -> None:
    """**Today is excluded.** A day still being written is material the window would see a
    different amount of on every run."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    yesterday = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    for day in (today, yesterday):
        (tmp_path / day).mkdir()

    assert trainer(tmp_path).complete_days() == [yesterday]


def test_the_window_widens_until_it_holds_two_sessions(tmp_path: Path) -> None:
    """**Most days carry one session**, and a leave-one-session-out split cannot run on one — so
    `window_days` is a minimum rather than a fixed count."""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (3, 2, 1)]
    for day in days:
        day_folder(tmp_path, day, {f"session-{day}": bodies(12)})

    subject = trainer(tmp_path)
    assert subject.window(window_days=1) == days[-2:], "one day holds one session, so it widened"
    assert len(subject._sessions_across(subject.window(window_days=1))) >= MIN_SESSIONS


def test_the_window_does_not_widen_when_one_day_already_has_two_sessions(tmp_path: Path) -> None:
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"old": bodies(12)})
    day_folder(tmp_path, days[1], {"a": bodies(12), "b": bodies(12, seed=5)})

    assert trainer(tmp_path).window(window_days=1) == [days[1]]


def test_the_holdout_is_the_largest_session_of_the_newest_day(tmp_path: Path) -> None:
    """**The newest complete day is the only material the incumbent certainly has not seen.**

    Scored on the training day the candidate always wins; scored inside a rolling window the
    incumbent always wins. Both biases are live and they run in opposite directions.
    """
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"older": bodies(10, seed=50)})
    big = bodies(14, seed=100)
    day_folder(tmp_path, days[1], {"small": bodies(4, seed=200), "big": big})

    training, holdout = trainer(tmp_path).split(days)

    assert sorted(holdout) == sorted(big), "the largest session of the newest day"
    assert not set(holdout) & set(training), "a body cannot be on both sides of the split"


def test_the_split_dedups_across_a_widened_window(tmp_path: Path) -> None:
    """The store dedups **per day**, so only a multi-day window can reintroduce duplicates — and
    there the filename *is* the digest, so it costs one `set()`."""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    shared = bodies(10)
    day_folder(tmp_path, days[0], {"older": shared})
    day_folder(tmp_path, days[1], {"newer": shared, "other": bodies(6, seed=9)})

    training, holdout = trainer(tmp_path).split(days)

    everything = training + holdout
    assert len(everything) == len(set(everything)), "the same body must not train twice"


def test_a_body_under_sample_min_bytes_is_not_a_sample(tmp_path: Path) -> None:
    day = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    day_folder(tmp_path, day, {"s": bodies(10) + [b"tiny"]})

    subject = DictionaryTrainer(
        Corpus(enabled=True, dir=tmp_path, retrain=Retrain(sample_min_bytes=1024))
    )
    assert b"tiny" not in subject.samples_in(day).values()


# -- the guard -----------------------------------------------------------------------------------


def test_a_dictionary_dated_today_stops_a_second_run(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    assert not subject.trained_today()
    subject.install(subject.train(bodies()))

    assert subject.trained_today()


def test_a_refusal_also_counts_as_having_tried_today(tmp_path: Path) -> None:
    """**The half worth stating.** Recording only installs would retrain a losing candidate from
    identical input on every restart, forever, for a verdict that cannot change."""
    subject = trainer(tmp_path)
    subject._record({"verdict": "refused"})

    assert subject.trained_today()


def test_the_guard_stops_run_before_it_trains(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    subject._record({"verdict": "refused"})

    assert subject.run() is None


def test_train_dict_bypasses_the_guard_but_not_the_margin(tmp_path: Path) -> None:
    """Typing the command is explicit consent to retrain today. **It is not consent to install a
    dictionary that loses.**"""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"older": bodies(12, seed=3)})
    day_folder(tmp_path, days[1], {"a": bodies(12), "b": bodies(12, seed=7)})
    subject = trainer(tmp_path)

    first = subject.run()
    assert first is not None and first.installed
    assert subject.run() is None, "the guard stops the second run"

    again = subject.run(bypass_guard=True)
    assert again is not None
    assert not again.installed, "identical material cannot beat the margin"


# -- the lock ------------------------------------------------------------------------------------


def test_one_training_run_at_a_time_across_processes(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    assert subject._acquire()
    try:
        assert not subject._acquire(), "a second holder must be refused"
    finally:
        subject._release()
    assert subject._acquire()
    subject._release()


def test_a_stale_lock_is_broken_by_age(tmp_path: Path) -> None:
    """`O_EXCL` rather than `flock`, because the failure guarded against is a **killed** process —
    `flock` is released by the kernel when its holder dies, which would leave nothing to break."""
    subject = trainer(tmp_path)
    subject.retrain_lock.parent.mkdir(parents=True, exist_ok=True)
    stale = time.time() - LOCK_STALE_S - 1
    subject.retrain_lock.write_text(f"pid=999999 since={stale:.0f}\n", encoding="utf-8")

    assert subject._acquire(), "a lock older than LOCK_STALE_S is broken"
    subject._release()


def test_a_fresh_lock_is_not_broken(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    subject.retrain_lock.parent.mkdir(parents=True, exist_ok=True)
    subject.retrain_lock.write_text(f"pid=999999 since={time.time():.0f}\n", encoding="utf-8")

    assert not subject._acquire()


def test_the_lock_age_comes_from_inside_the_file_not_its_mtime(tmp_path: Path) -> None:
    """An mtime is filesystem metadata anything outside this program can rewrite; `since=` is a
    fact the trainer wrote. Same reason a dictionary's name leads with a UTC stamp rather than
    being sorted by mtime."""
    subject = trainer(tmp_path)
    subject.retrain_lock.parent.mkdir(parents=True, exist_ok=True)
    stale = time.time() - LOCK_STALE_S - 1
    subject.retrain_lock.write_text(f"pid=1 since={stale:.0f}\n", encoding="utf-8")
    os.utime(subject.retrain_lock, None)  # something rewrites the mtime; the content says stale

    assert subject._acquire()
    subject._release()


def test_the_lock_is_released_even_when_the_run_fails(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    monkey = pytest.MonkeyPatch()
    monkey.setattr(DictionaryTrainer, "_attempt", lambda self, w: 1 / 0)
    try:
        assert subject.run() is None
    finally:
        monkey.undo()

    assert not subject.retrain_lock.exists(), "a failed run must not leave the lock behind"


# -- the floor -----------------------------------------------------------------------------------


def test_with_no_complete_day_it_trains_nothing_and_says_so(tmp_path: Path) -> None:
    """**A fresh install trains nothing on its first day**, which is correct: the store writes
    undicted frames meanwhile and they stay valid forever."""
    subject = trainer(tmp_path)

    assert subject.run() is None
    assert "no-complete-day" in subject.retrain_log.read_text(encoding="utf-8")


def test_a_window_too_small_to_split_is_recorded_rather_than_crashed(tmp_path: Path) -> None:
    day = (datetime.now(UTC) - timedelta(days=1)).strftime("%Y-%m-%d")
    day_folder(tmp_path, day, {"only": bodies(6)})

    subject = trainer(tmp_path)
    assert subject.run() is None
    assert "too-few-samples" in subject.retrain_log.read_text(encoding="utf-8")


def test_a_trainer_never_raises_into_its_caller(tmp_path: Path) -> None:
    """Telemetry-shaped: it logs and dies quietly. A corpus that stops filling is bad; a router
    that stops serving because the corpus stopped filling is worse."""
    subject = trainer(tmp_path)
    monkey = pytest.MonkeyPatch()
    monkey.setattr(DictionaryTrainer, "window", lambda self, **kw: 1 / 0)
    try:
        assert subject.run() is None
    finally:
        monkey.undo()

    assert "verdict=failed" in subject.retrain_log.read_text(encoding="utf-8")


# -- the retrain log ------------------------------------------------------------------------------


def test_the_retrain_log_records_the_level_the_comparison_used(tmp_path: Path) -> None:
    """It became operator-editable when scoring moved to `compress_level_zstd`, so two ratios
    logged on different days are not comparable unless the line says what they were scored at."""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"older": bodies(12, seed=3)})
    day_folder(tmp_path, days[1], {"a": bodies(12), "b": bodies(12, seed=7)})

    subject = trainer(tmp_path, level=19)
    subject.run()

    line = subject.retrain_log.read_text(encoding="utf-8").strip()
    assert "level=19" in line
    assert "verdict=installed" in line
    assert "seconds=" in line


def test_the_retrain_log_lives_at_the_corpus_root_not_in_dicts_or_a_day(tmp_path: Path) -> None:
    """`dicts/` is relisted by the worker's pickup, and a day folder would make training state
    something a day *needs* — which is the direction self-containment actually forbids."""
    subject = trainer(tmp_path)

    assert subject.retrain_log == tmp_path / "retrain.log"
    assert subject.retrain_lock == tmp_path / "retrain.lock"


# -- the budget and the triggers -------------------------------------------------------------------


def test_a_fast_run_registers_the_rollover_trigger(tmp_path: Path) -> None:
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"older": bodies(12, seed=3)})
    day_folder(tmp_path, days[1], {"a": bodies(12), "b": bodies(12, seed=7)})

    subject = trainer(tmp_path)
    subject.run()

    assert subject._budget_permits_rollover() is True


def test_a_run_over_the_budget_leaves_the_router_on_startup_only(tmp_path: Path) -> None:
    """**Applies the owner's rule; it does not choose a policy.** UTC midnight is an arbitrary
    local hour, so a long run firing unattended is what the budget exists to prevent."""
    subject = trainer(tmp_path)
    subject._apply_budget(TRAIN_BUDGET_S + 1)

    assert subject._budget_permits_rollover() is False
    subject.on_day_rollover()
    assert subject._thread is None, "no rollover thread when the budget refuses it"


def test_the_budget_decision_survives_a_restart(tmp_path: Path) -> None:
    """A router that starts at 23:00 and is guarded — because it already trained today — reaches
    midnight having measured nothing, so the trigger it is entitled to would never register."""
    trainer(tmp_path)._record({"verdict": "installed", "seconds": "0.03"})

    fresh = trainer(tmp_path)
    assert fresh._rollover_allowed is None, "nothing measured in this process"
    assert fresh._budget_permits_rollover() is True


def test_window_days_zero_starts_no_thread(tmp_path: Path) -> None:
    """The second of the block's two independent off switches; `corpus.enabled` is the first."""
    subject = DictionaryTrainer(
        Corpus(enabled=True, dir=tmp_path, retrain=Retrain(window_days=0))
    )
    subject.start()

    assert subject._thread is None


def test_a_disabled_corpus_creates_nothing_when_the_trainer_is_built(tmp_path: Path) -> None:
    """Task 18's observation 1 is *"leaves no trace: no directory, no file"*, and a trainer that
    makes `<dir>/dicts/.incoming/` would break it."""
    root = tmp_path / "corpus"
    DictionaryTrainer(Corpus(enabled=False, dir=root, retrain=Retrain(window_days=0))).start()

    assert not root.exists()


# -- the day-rollover hook (Task 14a's second trigger) ------------------------------------------


def writer_with_hook(root: Path, hook: object) -> CorpusWriter:
    return CorpusWriter(
        directory=root,
        compress_level=9,
        body_max_bytes=1 << 20,
        queue_max_bytes=1 << 26,
        on_day_rollover=hook,  # type: ignore[arg-type]
    )


def test_opening_the_first_day_is_not_a_rollover(tmp_path: Path) -> None:
    """**The startup trigger has already fired for that day.** Firing here too would train twice
    for one event, every time the router restarts."""
    fired: list[int] = []
    writer = writer_with_hook(tmp_path, lambda: fired.append(1))
    try:
        writer.store("2026-08-18T23:59:59.000+00:00", "requests", b"x" * 2000)
        assert fired == []
        writer.store("2026-08-18T10:00:00.000+00:00", "requests", b"y" * 2000)
        assert fired == [], "a second body the same day is not a rollover either"
    finally:
        writer.close()


def test_crossing_midnight_fires_the_hook_once(tmp_path: Path) -> None:
    fired: list[int] = []
    writer = writer_with_hook(tmp_path, lambda: fired.append(1))
    try:
        writer.store("2026-08-18T23:59:59.000+00:00", "requests", b"x" * 2000)
        writer.store("2026-08-19T00:00:02.000+00:00", "requests", b"z" * 2000)
        assert fired == [1]
        writer.store("2026-08-19T01:00:00.000+00:00", "requests", b"w" * 2000)
        assert fired == [1], "still the same day"
    finally:
        writer.close()


def test_a_late_body_filed_under_yesterday_is_not_a_rollover(tmp_path: Path) -> None:
    """A body submitted at 23:59:59 and written at 00:00:02 belongs to **yesterday**, so the worker
    reopens a day it already knows. That is not a new day and must not trigger training."""
    fired: list[int] = []
    writer = writer_with_hook(tmp_path, lambda: fired.append(1))
    try:
        writer.store("2026-08-18T12:00:00.000+00:00", "requests", b"x" * 2000)
        writer.store("2026-08-19T00:00:02.000+00:00", "requests", b"z" * 2000)
        writer.store("2026-08-18T23:59:59.000+00:00", "requests", b"q" * 2000)
        assert fired == [1]
    finally:
        writer.close()


def test_a_rollover_hook_that_raises_does_not_stop_the_store(tmp_path: Path) -> None:
    """The worker stands between a body and the disk. A trainer that cannot start is a corpus
    without a new dictionary; a worker that dies is a corpus that stops."""

    def boom() -> None:
        raise RuntimeError("hook exploded")

    writer = writer_with_hook(tmp_path, boom)
    try:
        writer.store("2026-08-18T12:00:00.000+00:00", "requests", b"a" * 2000)
        stored = writer.store("2026-08-19T12:00:00.000+00:00", "requests", b"b" * 2000)
        assert len(stored.digest) == 64, "the body was still stored"
    finally:
        writer.close()


def test_the_guard_is_checked_again_under_the_lock(tmp_path: Path) -> None:
    """Two processes can both pass the cheap guard and then queue on the lock — and the loser would
    otherwise wake up and retrain from exactly the material the winner just used."""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(tmp_path, days[0], {"older": bodies(12, seed=3)})
    day_folder(tmp_path, days[1], {"a": bodies(12), "b": bodies(12, seed=7)})
    subject = trainer(tmp_path)

    # Stand in for the winner: the log line lands after the first guard has already been passed.
    monkey = pytest.MonkeyPatch()
    calls: list[int] = []

    def guard_passes_once() -> bool:
        calls.append(1)
        return len(calls) > 1

    monkey.setattr(subject, "trained_today", guard_passes_once)
    try:
        assert subject.run() is None, "the second check must stop it"
    finally:
        monkey.undo()
    assert len(calls) == 2, "checked before the lock and again under it"


# -- the lifespan wiring (Task 14a's first trigger) ---------------------------------------------


def test_the_app_starts_a_trainer_when_the_corpus_is_on(tmp_path: Path) -> None:
    """**The branch tests otherwise never reach.** Every other test injects a `CorpusWriter`, so
    `app.py`'s own construction — which is what also builds the trainer and starts its thread — is
    skipped. Here nothing is injected, so the lifespan builds both.
    """
    config = make_config()
    config.corpus = Corpus(enabled=True, dir=tmp_path, retrain=Retrain(window_days=1))
    upstream = Upstream()
    client = httpx.AsyncClient(transport=httpx.MockTransport(upstream.handle))

    with TestClient(create_app(config, client, Rows())) as test_client:  # type: ignore[arg-type]
        assert test_client.post("/v1/messages", content=CLAUDE_BODY).status_code == 200

    # A fresh install has no complete day, so it records that it did not train rather than
    # silently doing nothing.
    assert "no-complete-day" in (tmp_path / "retrain.log").read_text(encoding="utf-8")
    assert not (tmp_path / "retrain.lock").exists(), "the lock is released even on a skipped run"


def test_a_disabled_corpus_starts_no_trainer_and_creates_nothing(tmp_path: Path) -> None:
    """Task 18's observation 1: *leaves no trace — no directory, no file.* A trainer that created
    `<dir>/dicts/.incoming/` at startup would break it."""
    root = tmp_path / "corpus"
    config = make_config()
    config.corpus = Corpus(enabled=False, dir=root)
    client = httpx.AsyncClient(transport=httpx.MockTransport(Upstream().handle))

    with TestClient(create_app(config, client, Rows())) as test_client:  # type: ignore[arg-type]
        assert test_client.post("/v1/messages", content=CLAUDE_BODY).status_code == 200

    assert not root.exists()


# -- the pickup (Task 14c), and the self-containment cases (Task 14f) ---------------------------


def plain_writer(root: Path) -> CorpusWriter:
    return CorpusWriter(
        directory=root, compress_level=9, body_max_bytes=1 << 20, queue_max_bytes=1 << 26
    )


def install_one(root: Path, samples: list[bytes]) -> str:
    """Install a dictionary the way another process would — because that is the only way one ever
    arrives. The trainer publishes a file and nothing else."""
    subject = DictionaryTrainer(
        Corpus(enabled=True, dir=root, retrain=Retrain(maxdict=16_384, k=200))
    )
    return subject.install(subject.train(samples)).name


def test_a_new_dictionary_is_not_picked_up_before_the_rescan_is_due(tmp_path: Path) -> None:
    """One `listdir` per 500 bodies, in the worker. **Cheap because it is rare**, and a body or two
    written undicted after an install is not a defect — the frames stay valid forever."""
    writer = plain_writer(tmp_path)
    try:
        writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1)[0])
        install_one(tmp_path, bodies())
        stored = writer.store("2026-08-19T10:00:00.000+00:00", "requests", bodies(1, seed=9)[0])
        assert stored.dict_id == NO_DICTIONARY
    finally:
        writer.close()


def test_a_new_dictionary_is_picked_up_once_the_rescan_is_due(tmp_path: Path) -> None:
    writer = plain_writer(tmp_path)
    try:
        writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1)[0])
        name = install_one(tmp_path, bodies())
        for i in range(RESCAN_EVERY):
            writer.store("2026-08-19T11:00:00.000+00:00", "requests", b"filler %d" % i + b"x" * 40)

        stored = writer.store("2026-08-19T12:00:00.000+00:00", "requests", bodies(1, seed=77)[0])
        assert writer.dictionary_name == name
        assert stored.dict_id != NO_DICTIONARY
    finally:
        writer.close()


def test_opening_a_new_day_rescans_without_waiting(tmp_path: Path) -> None:
    """Otherwise a dictionary installed overnight would not be seen until 500 more bodies had gone
    past — and the retrain that produced it fires precisely at the rollover."""
    writer = plain_writer(tmp_path)
    try:
        writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1)[0])
        name = install_one(tmp_path, bodies())
        stored = writer.store("2026-08-20T00:00:02.000+00:00", "requests", bodies(1, seed=5)[0])

        assert writer.dictionary_name == name
        assert stored.dict_id != NO_DICTIONARY
    finally:
        writer.close()


def test_a_repeat_body_after_a_swap_still_names_the_dictionary_it_was_stored_with(
    tmp_path: Path,
) -> None:
    """**Group C's rule, now exercised under a real mid-day swap.** A body first stored undicted and
    seen again after a dictionary arrives must report the dictID of the blob **on disk**, not the
    compressor's — *which bodies used which dictionary* is the entire reason the column exists."""
    writer = plain_writer(tmp_path)
    repeated = bodies(1, seed=3)[0]
    try:
        first = writer.store("2026-08-19T09:00:00.000+00:00", "requests", repeated)
        assert first.dict_id == NO_DICTIONARY
        install_one(tmp_path, bodies())
        for i in range(RESCAN_EVERY):
            writer.store("2026-08-19T11:00:00.000+00:00", "requests", b"filler %d" % i + b"x" * 40)
        assert writer.dictionary_name is not None, "the swap happened"

        again = writer.store("2026-08-19T15:00:00.000+00:00", "requests", repeated)
        assert again.dict_id == NO_DICTIONARY, "read off the blob, never from the compressor"
    finally:
        writer.close()


def test_a_mid_day_swap_leaves_every_blob_readable_from_the_day_folder_alone(
    tmp_path: Path,
) -> None:
    """**The invariant the whole layout exists for.** `tar` the day, unpack it elsewhere, and every
    blob opens — including the ones written before the swap, against no dictionary at all."""
    writer = plain_writer(tmp_path)
    try:
        for i in range(3):
            writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1, seed=i)[0])
        install_one(tmp_path, bodies())
        for i in range(RESCAN_EVERY):
            writer.store("2026-08-19T11:00:00.000+00:00", "requests", b"filler %d" % i + b"x" * 40)
        for i in range(3):
            writer.store("2026-08-19T15:00:00.000+00:00", "requests", bodies(1, seed=100 + i)[0])
    finally:
        writer.close()

    reader = CorpusReader(tmp_path / "2026-08-19")
    blobs = reader.blobs("requests")
    assert len(blobs) > RESCAN_EVERY
    for blob in blobs:
        assert reader.read(blob), f"{blob.name} did not open from the day folder alone"


def test_the_same_holds_across_a_day_rollover(tmp_path: Path) -> None:
    """**The case a mid-day test cannot reach.** One worker can be writing into two day folders
    while holding one compressor — a body stamped 23:59:59 and written at 00:00:02 belongs to
    yesterday — so the dictionary copy is a **per-write precondition**, not a per-swap step."""
    writer = plain_writer(tmp_path)
    try:
        writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1)[0])
        first = install_one(tmp_path, bodies())
        writer.store("2026-08-20T00:00:02.000+00:00", "requests", bodies(1, seed=20)[0])

        second = install_one(tmp_path, bodies(40, seed=60))
        assert second != first
        writer.store("2026-08-21T00:00:01.000+00:00", "requests", bodies(1, seed=30)[0])
        # A late body, still filed under the 20th, while the compressor holds the newer dictionary.
        writer.store("2026-08-20T23:59:59.000+00:00", "requests", bodies(1, seed=40)[0])
    finally:
        writer.close()

    for day in ("2026-08-19", "2026-08-20", "2026-08-21"):
        reader = CorpusReader(tmp_path / day)
        for blob in reader.blobs("requests"):
            assert reader.read(blob), f"{day}/{blob.name} did not open from its own folder"

    held = sorted(p.name for p in (tmp_path / "2026-08-20" / "dicts").glob("*.dict"))
    assert held == sorted({first, second}), "the day that used two dictionaries keeps both"


def test_every_frame_written_carries_a_dictionary_id(tmp_path: Path) -> None:
    """**The field the reader and the whole no-recompression rule depend on.** A frame that does not
    name its dictionary is unreadable the moment the dictionary in hand is not the right one."""
    writer = plain_writer(tmp_path)
    try:
        install_one(tmp_path, bodies())
        writer._rescan()
        for i in range(4):
            writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1, seed=i)[0])
    finally:
        writer.close()

    reader = CorpusReader(tmp_path / "2026-08-19")
    for blob in reader.blobs("requests"):
        assert zstandard.get_frame_parameters(blob.read_bytes()).dict_id != 0


def test_a_dictionary_that_will_not_load_leaves_the_current_one_in_place(tmp_path: Path) -> None:
    """**It never raises.** This runs in the worker between two bodies, and telemetry does not get
    to break a call — construction is the one place a bad dictionary stops something."""
    writer = plain_writer(tmp_path)
    try:
        name = install_one(tmp_path, bodies())
        writer._rescan()
        assert writer.dictionary_name == name

        junk = tmp_path / "dicts" / "req-2099-01-01T000000Z-deadbeef.dict"
        junk.write_bytes(b"this is not a dictionary")
        writer._rescan()

        assert writer.dictionary_name == name, "the good dictionary is kept"
        stored = writer.store("2026-08-19T09:00:00.000+00:00", "requests", bodies(1)[0])
        assert stored.dict_id != NO_DICTIONARY
    finally:
        writer.close()


def test_a_content_only_dictionary_is_refused_because_its_id_is_zero(tmp_path: Path) -> None:
    """**The defect this test was written from, and it is worth stating in full.**

    `ZstdCompressionDict` accepts *arbitrary bytes* and treats them as a content-only dictionary
    whose `dict_id()` is **0**. Nothing about that call fails. A frame compressed against one then
    reports dictID **0** — which is precisely how *"stored with no dictionary"* is spelled — while
    genuinely needing those bytes back. Measured: reading such a blob without them raises
    `Data corruption detected`, and `CorpusReader` never tries a dictionary at all, because a frame
    reporting 0 tells it not to. **Every blob written in that window is permanently unreadable**,
    with a day folder that looks complete.

    So a dictionary reporting 0 is refused before a single body is written against it.
    """
    junk = tmp_path / "dicts" / "req-2026-08-19T000000Z-00000000.dict"
    junk.parent.mkdir(parents=True)
    junk.write_bytes(b'{"model":"claude-opus-5","system":"You are helpful."}' * 40)

    assert zstandard.ZstdCompressionDict(junk.read_bytes()).dict_id() == 0, "zstd accepts it"

    with pytest.raises(CorpusError, match="reports ID 0"):
        plain_writer(tmp_path)


def test_the_frame_such_a_dictionary_would_have_written_is_unreadable(tmp_path: Path) -> None:
    """Pins *why* the refusal above exists, so nobody relaxes it as an over-cautious check."""
    shared = b'{"model":"claude-opus-5","system":"You are a helpful assistant."}'
    content_only = zstandard.ZstdCompressionDict(shared * 40)
    frame = zstandard.ZstdCompressor(level=9, dict_data=content_only).compress(shared + b" more")

    assert zstandard.get_frame_parameters(frame).dict_id == 0, "the frame claims to be undicted"
    with pytest.raises(zstandard.ZstdError):
        zstandard.ZstdDecompressor().decompress(frame)


def test_a_rescan_that_finds_nothing_new_keeps_the_compressor_it_has(tmp_path: Path) -> None:
    """**The name check is what makes the rescan cheap**, and nothing else would notice it going.

    Rebuilding produces an identical compressor, so behaviour is unchanged and no other test can
    see the difference — what changes is that every rescan pays for a fresh `_build_compressor`,
    probe compression included, and every one of them announces a switch that did not happen. The
    identity of the object is the only observable, so that is what this asserts.
    """
    writer = plain_writer(tmp_path)
    try:
        install_one(tmp_path, bodies())
        writer._rescan()
        loaded = writer._dictionary

        writer._rescan()

        assert writer._dictionary is loaded, "an unchanged dicts/ must not rebuild anything"
    finally:
        writer.close()


# -- --from, --train-dict and --tune-dict (Task 14e) --------------------------------------------


def loose_corpus(root: Path, sessions: dict[str, list[bytes]]) -> Path:
    """A directory that is **not** a corpus: one subdirectory per session, loose files inside.

    This is `logs/corpus-gate/`'s shape — the material Task 15 trains from, which has no day
    folders, no index and no content addressing.
    """
    source = root / "loose"
    for name, payloads in sessions.items():
        folder = source / name / "requests"
        folder.mkdir(parents=True)
        for i, payload in enumerate(payloads):
            (folder / f"{i:05d}.bin").write_bytes(payload)
    return source


def test_each_subdirectory_is_a_session_and_the_last_by_name_is_held_out(tmp_path: Path) -> None:
    """**Reproduces `gate.py`'s own split** — train on run-01 + run-02, score on run-03 — and
    comparability with the frozen evidence is the entire reason this rule was chosen."""
    source = loose_corpus(
        tmp_path,
        {"run-01": bodies(20), "run-02": bodies(4, seed=40), "run-03": bodies(10, seed=80)},
    )

    training, holdout = trainer(tmp_path).external_split(source)

    assert len(holdout) == 10, "run-03, the last by name"
    assert len(training) == 24, "run-01 and run-02 together"
    assert not set(training) & set(holdout)


def test_the_largest_session_is_not_what_gets_held_out(tmp_path: Path) -> None:
    """Holding out the largest would invert the intent: on the real corpus `run-01` is 46 of the 70
    usable bodies, so the majority would be held out and the minority trained on."""
    source = loose_corpus(tmp_path, {"run-01": bodies(30), "run-02": bodies(6, seed=40)})

    training, holdout = trainer(tmp_path).external_split(source)

    assert len(training) == 30 and len(holdout) == 6


def test_dictionaries_are_never_training_samples(tmp_path: Path) -> None:
    """**The leakage defect, and it was measured rather than imagined.**

    `logs/corpus-gate/dicts/` sits beside the capture directories and holds dictionaries trained on
    those very captures. Taken as a session, it fed the held-out slice's own content back in as
    training material and reported **26.210x** against a true figure near **12.9x** — the exact bias
    leave-one-session-out exists to prevent, reintroduced through a directory listing.

    Excluded **by content**, not by folder name: the name is a convention, the magic number is a
    fact, and `--from` may be pointed at any layout at all.
    """
    source = loose_corpus(tmp_path, {"run-01": bodies(20), "run-02": bodies(10, seed=40)})
    trained = zstandard.train_dictionary(16_384, bodies(60), k=200, d=8, level=3).as_bytes()
    dicts = source / "dicts"
    dicts.mkdir()
    for i in range(3):
        (dicts / f"heldout-{i}.dict").write_bytes(trained)

    training, holdout = trainer(tmp_path).external_split(source)

    assert all(not raw.startswith(b"\x37\xa4\x30\xec") for raw in training + holdout)
    assert len(training) == 20 and len(holdout) == 10, "dicts/ contributed no session at all"


def test_a_source_with_too_few_sessions_trains_nothing(tmp_path: Path) -> None:
    source = loose_corpus(tmp_path, {"only-one": bodies(20)})

    assert trainer(tmp_path).external_split(source) == ([], [])


def test_from_installs_into_the_corpus_not_into_the_source(tmp_path: Path) -> None:
    """**`--from` redirects the material and nothing else.** The lock, `retrain.log` and the install
    stay under `corpus.dir`, so a hand-run is recorded in the same log as every automatic one and
    the dictionary lands where the router will actually read it."""
    source = loose_corpus(tmp_path, {"run-01": bodies(30), "run-02": bodies(10, seed=40)})
    subject = trainer(tmp_path)

    verdict = subject.run(bypass_guard=True, source=source)

    assert verdict is not None and verdict.installed
    assert newest_dictionary(tmp_path / "dicts") is not None, "installed under corpus.dir"
    assert not (source / "dicts").exists(), "nothing written into the source"
    assert "retrain.log" in [p.name for p in tmp_path.iterdir()]


def test_the_sweep_returns_the_whole_surface_and_installs_nothing(tmp_path: Path) -> None:
    """Training is **non-monotonic in both axes**, so a tool that printed one winner would invite
    exactly the reading the measurement refuses."""
    subject = trainer(tmp_path)
    training, holdout = bodies(40), bodies(10, seed=90)

    surface = subject.tune(training, holdout, maxdicts=(8_192, 16_384), ks=(200, 400))

    assert len(surface) == 4, "one row per combination, not a winner"
    assert all(ratio > 1 for *_rest, ratio in surface)
    assert not (tmp_path / "dicts").exists(), "a sweep never installs"


def test_a_cli_override_is_revalidated_rather_than_forced_in(tmp_path: Path) -> None:
    """**`model_copy(update=)` would skip validation**, so `--maxdict 0` would sail past the `gt=0`
    the config model declares and fail much later inside libzstd. Rebuilding through
    `model_validate` keeps one set of bounds for a key and its flag."""
    import argparse

    from ilirium_llm_router.cli import _with_overrides

    corpus = Corpus(enabled=True, dir=tmp_path)
    args = argparse.Namespace(window_days=None, sample_min_bytes=None, maxdict=0, k=None)

    with pytest.raises(ValueError):
        _with_overrides(corpus, args)


def test_a_cli_override_wins_over_the_config_for_that_run(tmp_path: Path) -> None:
    import argparse

    from ilirium_llm_router.cli import _with_overrides

    corpus = Corpus(enabled=True, dir=tmp_path, retrain=Retrain(maxdict=262_144, k=8000))
    args = argparse.Namespace(window_days=None, sample_min_bytes=None, maxdict=16_384, k=None)

    overridden = _with_overrides(corpus, args)

    assert overridden.retrain.maxdict == 16_384
    assert overridden.retrain.k == 8000, "an unmentioned key keeps its configured value"
    assert corpus.retrain.maxdict == 262_144, "the original block is not mutated"


# -- the thread, the sweep and the triggers (Task 14f) ------------------------------------------


def two_session_corpus(root: Path) -> None:
    """Two complete days, one session each, so the window has to widen to find a second."""
    days = [(datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d") for n in (2, 1)]
    day_folder(root, days[0], {"older": bodies(14, seed=3)})
    day_folder(root, days[1], {"newer": bodies(14, seed=7)})


def test_startup_sweeps_a_staging_file_a_killed_run_left_behind(tmp_path: Path) -> None:
    """*"A killed run leaves no trace"* is only true if somebody sweeps.

    The **installed** path is atomic, so a run killed mid-flight publishes nothing a reader would
    load — but a thread killed between write and rename does leave its partial file, and no task
    owned cleaning it up until this one.
    """
    staging = tmp_path / "dicts" / ".incoming"
    staging.mkdir(parents=True)
    leftover = staging / "1234-abcdef.tmp"
    leftover.write_bytes(b"half a dictionary")

    DictionaryTrainer(
        Corpus(enabled=True, dir=tmp_path, retrain=Retrain(window_days=0))
    ).start()

    assert not leftover.exists()


def test_the_sweep_creates_nothing_when_there_is_nothing_to_sweep(tmp_path: Path) -> None:
    """Task 18's observation 1 again: a corpus that has never written has no staging folder, and
    looking for one must not bring it into existence."""
    root = tmp_path / "never-written"
    DictionaryTrainer(
        Corpus(enabled=True, dir=root, retrain=Retrain(window_days=0))
    ).start()

    assert not root.exists()


def test_only_one_training_thread_runs_at_a_time_in_this_process(tmp_path: Path) -> None:
    """**On top of the cross-process lock, not instead of it.** The file lock stops two *processes*
    training at once; this stops the worker spawning a second thread while the first is still going,
    which the lock would only turn into a thread that starts and immediately gives up.
    """
    subject = trainer(tmp_path)
    running, release = threading.Event(), threading.Event()
    monkey = pytest.MonkeyPatch()
    monkey.setattr(subject, "run", lambda: (running.set(), release.wait(timeout=5)))
    try:
        subject._spawn("first")
        assert running.wait(timeout=5), "the first thread started"
        first = subject._thread

        subject._spawn("second")
        assert subject._thread is first, "no second thread while the first is alive"
    finally:
        release.set()
        if subject._thread is not None:
            subject._thread.join(timeout=5)
        monkey.undo()


def test_a_new_thread_may_start_once_the_previous_one_has_finished(tmp_path: Path) -> None:
    subject = trainer(tmp_path)
    monkey = pytest.MonkeyPatch()
    monkey.setattr(subject, "run", lambda: None)
    try:
        subject._spawn("first")
        first = subject._thread
        assert first is not None
        first.join(timeout=5)

        subject._spawn("second")
        assert subject._thread is not first
        if subject._thread is not None:
            subject._thread.join(timeout=5)
    finally:
        monkey.undo()


def test_the_training_thread_never_raises_into_the_process(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """**Telemetry-shaped: it logs and dies quietly.** A corpus that stops filling is bad; a router
    that stops serving because the corpus stopped filling is worse.

    Asserted on the log rather than on survival alone — an uncaught exception in a thread also
    leaves the process alive, so "it did not crash" would pass with the handler deleted.
    """
    subject = trainer(tmp_path)
    monkey = pytest.MonkeyPatch()

    def explode() -> None:
        raise RuntimeError("training exploded")

    monkey.setattr(subject, "run", explode)
    try:
        with caplog.at_level("WARNING", logger="ilirium_llm_router"):
            subject._spawn("boom")
            assert subject._thread is not None
            subject._thread.join(timeout=5)
    finally:
        monkey.undo()

    assert "training exploded" in caplog.text
    assert "RuntimeError" in caplog.text


def test_a_rollover_inside_the_budget_starts_a_training_thread(tmp_path: Path) -> None:
    """The positive half of `TRAIN_BUDGET_S`; the refusing half is tested above."""
    two_session_corpus(tmp_path)
    subject = trainer(tmp_path)
    subject._apply_budget(0.01)

    subject.on_day_rollover()

    assert subject._thread is not None
    subject._thread.join(timeout=10)
    assert subject.incumbent() is not None, "the rollover run installed a dictionary"


def test_the_startup_trigger_trains_and_installs_on_its_own_thread(tmp_path: Path) -> None:
    """**The whole automatic path, from `start()` to a file in `dicts/`**, with nothing awaited on
    the caller's side — which is the property that keeps training off the event loop."""
    two_session_corpus(tmp_path)
    subject = trainer(tmp_path)

    subject.start()

    assert subject._thread is not None
    subject._thread.join(timeout=10)
    installed = subject.incumbent()
    assert installed is not None and installed.name.startswith("req-")
    assert "verdict=installed" in subject.retrain_log.read_text(encoding="utf-8")
    assert not subject.retrain_lock.exists(), "the lock is released by the thread that took it"
