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

from pathlib import Path

import pytest
import zstandard

from ilirium_llm_router.config import Corpus, Retrain
from ilirium_llm_router.corpus import CorpusError, newest_dictionary
from ilirium_llm_router.dictionary import (
    DICT_MAGIC,
    TRAIN_D,
    TRAIN_LEVEL,
    Candidate,
    DictionaryTrainer,
    _id_from_digest,
    content_dict_id,
    stamp,
)

# Small, cheap and repetitive on purpose: a dictionary only has something to learn if the samples
# share material, which is exactly what a corpus of LLM request bodies looks like -- one large
# fixed preamble in front of a little variation.
PREAMBLE = (
    b'{"model":"claude-opus-5","system":"You are a helpful assistant.",'
    b'"tools":[],"messages":['
)


def bodies(count: int = 60, seed: int = 0) -> list[bytes]:
    return [
        PREAMBLE + b'{"role":"user","content":"' + bytes([65 + (i + seed) % 26]) * 300 + b'"}]}'
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
