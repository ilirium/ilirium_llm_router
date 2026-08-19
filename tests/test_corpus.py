"""The body store: what it writes, what it refuses, and that bodies come back out unchanged.

The claim these tests exist for is the milestone's second failure mode — **that archiving cannot
stay opaque.** It is discharged by construction rather than by assertion, and
`test_a_non_utf8_non_json_body_round_trips_byte_identically` is the test that makes that a check:
the store never decodes, never parses and never re-encodes, so bytes that are not text at all
survive it exactly.

`docs/reference/observability.md` governs the index the same way it governs `calls.csv`: an absent
value is an empty cell, never a zero.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest
import zstandard

from ilirium_llm_router.corpus import (
    ABSENT,
    DROPPED,
    INDEX_COLUMNS,
    NO_DICTIONARY,
    TOO_LARGE,
    CorpusError,
    CorpusReader,
    CorpusWriter,
)
from ilirium_llm_router.stats import CallRecord

TIMESTAMP = "2026-08-19T12:00:00.000+00:00"
DAY = "2026-08-19"


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


def writer(path: Path, **overrides: int) -> CorpusWriter:
    settings: dict[str, int] = {
        "compress_level": 9,
        "body_max_bytes": 1_048_576,
        "queue_max_bytes": 67_108_864,
    }
    settings.update(overrides)
    return CorpusWriter(directory=path, **settings)  # type: ignore[arg-type]


def rows(day: Path) -> list[dict[str, str]]:
    with open(day / "index.csv", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def drain(store: CorpusWriter) -> None:
    """Stop the worker so everything submitted has certainly been written."""
    store.close()


# --- the claim ----------------------------------------------------------------------------------


def test_a_non_utf8_non_json_body_round_trips_byte_identically(tmp_path: Path) -> None:
    """**This is the test that discharges failure mode 2.**

    Every byte value 0–255, twice over, plus lone surrogatable sequences and a NUL run. None of it
    is valid UTF-8 and none of it is JSON. If the store ever decoded, parsed, normalised or
    re-encoded a body, this is what would catch it.
    """
    body = bytes(range(256)) * 2 + b"\x00\x00\xff\xfe\xc3\x28\x80\x80" + b"\xed\xa0\x80"

    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", body)
    drain(store)

    blob = tmp_path / DAY / "requests" / stored.digest[:2] / f"{stored.digest}.zst"
    assert CorpusReader(tmp_path / DAY).read(blob) == body


def test_the_digest_is_of_the_plaintext_not_the_compressed_bytes(tmp_path: Path) -> None:
    import hashlib

    body = b"the quick brown fox" * 500
    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", body)
    drain(store)

    assert stored.digest == hashlib.sha256(body).hexdigest()


# --- the layout ---------------------------------------------------------------------------------


def test_the_day_folder_comes_from_the_calls_timestamp_not_the_clock(tmp_path: Path) -> None:
    """A body that arrived at 23:59:59 belongs to that day however late it is written.

    Otherwise a day folder and the index rows inside it can disagree about which day they are, and
    the folder stops being readable as a unit.
    """
    store = writer(tmp_path)
    store.store("2026-08-19T23:59:59.500+00:00", "requests", b"a" * 2048)
    store.store("2026-08-20T00:00:02.100+00:00", "requests", b"b" * 2048)
    drain(store)

    assert (tmp_path / "2026-08-19" / "requests").exists()
    assert (tmp_path / "2026-08-20" / "requests").exists()


def test_the_manifest_records_the_schema_and_the_column_count(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.store(TIMESTAMP, "requests", b"x" * 2048)
    drain(store)

    manifest = (tmp_path / DAY / "manifest").read_text(encoding="utf-8")
    assert "index_schema_version: 1" in manifest
    assert f"index_columns: {len(INDEX_COLUMNS)}" in manifest


def test_the_same_body_twice_in_one_day_is_one_blob(tmp_path: Path) -> None:
    body = b"repeated" * 400
    store = writer(tmp_path)
    first = store.store(TIMESTAMP, "requests", body)
    second = store.store(TIMESTAMP, "requests", body)
    drain(store)

    assert first.digest == second.digest
    assert len(list((tmp_path / DAY / "requests").rglob("*.zst"))) == 1


def test_dedup_does_not_cross_a_day(tmp_path: Path) -> None:
    """Cross-day dedup would make deleting one day orphan another day's references, and deleting a
    day whole is the entire retention policy."""
    body = b"repeated" * 400
    store = writer(tmp_path)
    store.store("2026-08-19T10:00:00.000+00:00", "requests", body)
    store.store("2026-08-20T10:00:00.000+00:00", "requests", body)
    drain(store)

    assert len(list((tmp_path / "2026-08-19").rglob("*.zst"))) == 1
    assert len(list((tmp_path / "2026-08-20").rglob("*.zst"))) == 1


def test_a_writer_that_stores_nothing_creates_no_directory(tmp_path: Path) -> None:
    """Task 18's observation 1: `corpus.enabled: false` leaves no trace."""
    target = tmp_path / "corpus"
    drain(writer(target))

    assert not target.exists()


def test_staging_files_from_a_killed_run_are_swept(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.store(TIMESTAMP, "requests", b"x" * 2048)
    drain(store)
    (tmp_path / DAY / "incoming" / "999-abandoned.tmp").write_bytes(b"partial")

    second = writer(tmp_path)
    second.store(TIMESTAMP, "requests", b"y" * 2048)
    drain(second)

    assert list((tmp_path / DAY / "incoming").glob("*.tmp")) == []


# --- with and without a dictionary --------------------------------------------------------------


def test_with_no_dictionary_bodies_are_stored_undicted(tmp_path: Path) -> None:
    """The ordinary case at first run: Group C ships before Group D, so `dicts/` is empty."""
    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", b"x" * 4096)
    drain(store)

    assert stored.dict_id == NO_DICTIONARY
    assert store.dictionary_name is None


def test_an_undicted_frame_reports_dict_id_zero_and_the_index_says_none(tmp_path: Path) -> None:
    """`0` is a real dictID, so "no dictionary" gets a word. An absent value is an empty cell."""
    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", b"x" * 4096)
    drain(store)

    blob = tmp_path / DAY / "requests" / stored.digest[:2] / f"{stored.digest}.zst"
    assert zstandard.get_frame_parameters(blob.read_bytes()).dict_id == 0
    assert stored.dict_id == "none"


def install_dictionary(root: Path, name: str, samples: list[bytes]) -> None:
    data = zstandard.train_dictionary(112_640, samples, k=8000, d=8, level=3)
    (root / "dicts").mkdir(parents=True, exist_ok=True)
    (root / "dicts" / name).write_bytes(data.as_bytes())


def test_the_newest_dictionary_is_chosen_by_filename_not_mtime(tmp_path: Path) -> None:
    """`logs/` sits inside a cloud-synced folder on the machine this was built for, and a sync
    rewrites mtimes. The name leads with a UTC stamp so that sorting it is meaningful."""
    samples = [bytes([i % 251]) * 3000 for i in range(40)]
    install_dictionary(tmp_path, "req-2026-08-18T104500Z-aaaaaaaa.dict", samples)
    install_dictionary(tmp_path, "req-2026-08-17T090000Z-bbbbbbbb.dict", samples)
    # Make the OLDER name the NEWEST file, which is exactly the trap.
    (tmp_path / "dicts" / "req-2026-08-17T090000Z-bbbbbbbb.dict").touch()

    assert writer(tmp_path).dictionary_name == "req-2026-08-18T104500Z-aaaaaaaa.dict"


def test_a_day_that_uses_a_dictionary_keeps_its_own_copy(tmp_path: Path) -> None:
    samples = [bytes([i % 251]) * 3000 for i in range(40)]
    install_dictionary(tmp_path, "req-2026-08-18T104500Z-aaaaaaaa.dict", samples)

    store = writer(tmp_path)
    store.store(TIMESTAMP, "requests", b"x" * 4096)
    drain(store)

    copies = sorted(p.name for p in (tmp_path / DAY / "dicts").glob("*.dict"))
    assert copies == ["req-2026-08-18T104500Z-aaaaaaaa.dict"]


def test_a_day_folder_opens_from_itself_alone(tmp_path: Path) -> None:
    """`tar` it, unpack it elsewhere, and every blob still opens. This is what the per-day
    dictionary copy is for, and what makes `rm -rf <a-day>` the whole retention policy."""
    samples = [bytes([i % 251]) * 3000 for i in range(40)]
    install_dictionary(tmp_path, "req-2026-08-18T104500Z-aaaaaaaa.dict", samples)
    bodies = [bytes([i % 251]) * 5000 for i in range(6)]

    store = writer(tmp_path)
    stored = [store.store(TIMESTAMP, "requests", b) for b in bodies]
    drain(store)

    elsewhere = tmp_path / "far"
    elsewhere.mkdir()
    subprocess.run(["tar", "-cf", str(tmp_path / "day.tar"), "-C", str(tmp_path), DAY], check=True)
    subprocess.run(["tar", "-xf", str(tmp_path / "day.tar"), "-C", str(elsewhere)], check=True)

    reader = CorpusReader(elsewhere / DAY)
    read_back = [reader.read(b) for b in reader.blobs("requests")]
    assert sorted(read_back) == sorted(bodies)
    assert len(stored) == len(bodies)


def test_a_repeat_after_a_dictionary_swap_records_the_dictionary_on_disk(tmp_path: Path) -> None:
    """The defect this was written for: a body stored under dictionary A and seen again under B
    must keep naming A, because that is what its blob names."""
    samples = [bytes([i % 251]) * 3000 for i in range(40)]
    body = b"z" * 9000
    install_dictionary(tmp_path, "req-2026-08-17T090000Z-first.dict", samples)

    first = writer(tmp_path)
    before = first.store(TIMESTAMP, "requests", body)
    drain(first)

    install_dictionary(tmp_path, "req-2026-08-18T104500Z-second.dict", samples[:20])
    second = writer(tmp_path)
    after = second.store(TIMESTAMP, "requests", body)
    drain(second)

    blob = tmp_path / DAY / "requests" / before.digest[:2] / f"{before.digest}.zst"
    on_disk = zstandard.get_frame_parameters(blob.read_bytes()).dict_id
    assert after.dict_id == f"{on_disk:08x}"
    assert after.dict_id == before.dict_id


# --- the index ----------------------------------------------------------------------------------


def test_the_index_header_is_the_twenty_six_columns_in_order(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.submit(record(), b"x" * 2048, b"y" * 2048)
    drain(store)

    written = rows(tmp_path / DAY)
    assert list(written[0].keys()) == list(INDEX_COLUMNS)
    assert len(INDEX_COLUMNS) == 26


def test_the_first_twenty_columns_are_calls_csv_in_its_order(tmp_path: Path) -> None:
    """What lets a rotated `calls.csv` segment and a day index feed one spreadsheet."""
    from ilirium_llm_router.stats import COLUMNS

    assert INDEX_COLUMNS[:20] == COLUMNS


def test_a_stored_call_gets_digests_and_timings(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.submit(record(), b"x" * 2048, b"y" * 2048)
    drain(store)

    row = rows(tmp_path / DAY)[0]
    assert len(row["request_ref"]) == 64
    assert len(row["response_ref"]) == 64
    assert row["store_ms"] != ""
    assert row["queue_ms"] != ""
    assert row["request_dict_id"] == NO_DICTIONARY


def test_a_router_authored_body_is_absent(tmp_path: Path) -> None:
    """The 400 for a missing model, the 502, the injected SSE error event. The claim is every body
    the router *carries*, and these are ours."""
    store = writer(tmp_path)
    store.submit(record(error_status="http_error", error_code="400"), None, None)
    drain(store)

    row = rows(tmp_path / DAY)[0]
    assert row["request_ref"] == ABSENT
    assert row["response_ref"] == ABSENT
    assert row["store_ms"] == ""
    assert row["request_dict_id"] == ""


def test_a_body_over_the_ceiling_is_dropped_not_truncated(tmp_path: Path) -> None:
    """A prefix labelled as a whole body is worse than a hole."""
    store = writer(tmp_path, body_max_bytes=4096)
    store.submit(record(), b"x" * 8192, b"y" * 100)
    drain(store)

    row = rows(tmp_path / DAY)[0]
    assert row["request_ref"] == TOO_LARGE
    assert len(row["response_ref"]) == 64
    assert len(list((tmp_path / DAY / "requests").rglob("*.zst"))) == 0


def test_a_response_stopped_at_the_ceiling_is_too_large(tmp_path: Path) -> None:
    store = writer(tmp_path, body_max_bytes=4096)
    store.submit(record(), b"x" * 100, None, response_over_cap=True)
    drain(store)

    assert rows(tmp_path / DAY)[0]["response_ref"] == TOO_LARGE


def test_store_ms_is_empty_and_never_zero_when_nothing_was_stored(tmp_path: Path) -> None:
    """`docs/reference/observability.md`: an absent count and a genuine zero are different facts."""
    store = writer(tmp_path)
    store.submit(record(), None, None)
    drain(store)

    assert rows(tmp_path / DAY)[0]["store_ms"] == ""


# --- the queue ----------------------------------------------------------------------------------


def test_a_full_queue_produces_a_row_saying_dropped(tmp_path: Path) -> None:
    """`EPD-003`'s *drop the body and record that it was dropped* made literal: the hole is a row,
    not an absence."""
    store = writer(tmp_path, queue_max_bytes=1)
    for _ in range(5):
        store.submit(record(), b"x" * 4096, b"y" * 4096)
    drain(store)

    written = rows(tmp_path / DAY)
    assert len(written) == 5
    assert all(r["request_ref"] == DROPPED and r["response_ref"] == DROPPED for r in written)
    assert list((tmp_path / DAY).rglob("*.zst")) == []


def test_queue_ms_and_queue_bytes_are_still_written_on_a_dropped_row(tmp_path: Path) -> None:
    store = writer(tmp_path, queue_max_bytes=1)
    store.submit(record(), b"x" * 4096, b"y" * 4096)
    drain(store)

    row = rows(tmp_path / DAY)[0]
    assert row["queue_ms"] != ""
    assert row["queue_bytes"] != ""
    assert row["store_ms"] == ""


def test_submit_never_raises_even_on_a_malformed_timestamp(tmp_path: Path) -> None:
    """Telemetry does not get to break a call."""
    store = writer(tmp_path)
    store.submit(record(timestamp=""), b"x" * 2048, b"y" * 2048)
    store.submit(record(), b"a" * 2048, b"b" * 2048)
    drain(store)

    assert rows(tmp_path / DAY)[0]["request_ref"] != ""


def test_the_summary_counts_what_happened(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.submit(record(), b"x" * 4096, b"y" * 4096)
    drain(store)

    assert "stored 2" in store.summary()
    assert "dropped 0" in store.summary()


# --- the reader ---------------------------------------------------------------------------------


def test_the_reader_refuses_a_blob_whose_digest_does_not_match(tmp_path: Path) -> None:
    """Every read is a free integrity check, because the filename *is* the digest."""
    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", b"x" * 4096)
    drain(store)

    blob = tmp_path / DAY / "requests" / stored.digest[:2] / f"{stored.digest}.zst"
    blob.write_bytes(zstandard.ZstdCompressor(level=9).compress(b"different bytes entirely"))

    with pytest.raises(CorpusError):
        CorpusReader(tmp_path / DAY).read(blob)


def test_the_reader_tries_every_dictionary_claiming_the_frames_id(tmp_path: Path) -> None:
    """A dictID is a lookup hint, not a key: `zstd --train` stamps 1 on everything, so a day can
    hold two files answering to one ID. The one that verifies is the one that is kept."""
    samples = [bytes([i % 251]) * 3000 for i in range(40)]
    install_dictionary(tmp_path, "req-2026-08-18T104500Z-aaaaaaaa.dict", samples)
    store = writer(tmp_path)
    stored = store.store(TIMESTAMP, "requests", b"q" * 9000)
    drain(store)

    # A decoy carrying the same dictID and different bytes, dropped in beside the real one.
    real = (tmp_path / DAY / "dicts").glob("*.dict").__next__().read_bytes()
    decoy = zstandard.train_dictionary(112_640, samples[:20], k=8000, d=8, level=3).as_bytes()
    patched = bytearray(decoy)
    patched[4:8] = real[4:8]
    (tmp_path / DAY / "dicts" / "req-2026-08-01T000000Z-decoy.dict").write_bytes(bytes(patched))

    blob = tmp_path / DAY / "requests" / stored.digest[:2] / f"{stored.digest}.zst"
    assert CorpusReader(tmp_path / DAY).read(blob) == b"q" * 9000


def test_extract_reads_a_day_back_and_reports(tmp_path: Path) -> None:
    store = writer(tmp_path)
    store.store(TIMESTAMP, "requests", b"x" * 4096)
    store.store(TIMESTAMP, "responses", b"y" * 4096)
    drain(store)

    finished = subprocess.run(
        [sys.executable, "-m", "ilirium_llm_router", "--extract", str(tmp_path / DAY)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert finished.returncode == 0, finished.stderr
    assert "2 blob(s), 0 failed" in finished.stdout
    assert "every blob verified" in finished.stdout
