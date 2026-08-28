"""Selection over an index — Phase 11 tasks 16 and 18.

**The numbers these assert are the live corpus's**, checked by driving the same functions over it on
2026-08-28: 979 rows, `--path /v1/messages` selecting **902** while `/v1/messages/count_tokens`
selects **66** separately, `--agent` selecting **67**, 45 sentinel rows and 11 with no session at
all. The fixtures here are small so a failure names one behaviour; the corpus is what says the
behaviour is the right one. → `notes-group-d.md`.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from ilirium_llm_router.extract import (
    NO_SESSION,
    SEQ_DIGITS,
    ExtractError,
    Row,
    Selection,
    days_of_sessions,
    read_index,
    select,
    sequence_numbers,
)

COLUMNS = ["timestamp", "session_id", "agent_id", "model", "path", "request_ref", "response_ref"]


def day(root: Path, name: str, rows: list[dict]) -> Path:
    """One day folder with an index, written in **completion order** as the real one is."""
    folder = root / name
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / "index.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in COLUMNS})
    return folder


def entry(**cells: str) -> dict:
    base = {
        "timestamp": "2026-08-25T10:00:00+00:00",
        "session_id": "s1",
        "model": "claude-opus-5",
        "path": "/v1/messages",
        "request_ref": "ab" + "0" * 62,
        "response_ref": "cd" + "0" * 62,
    }
    base.update(cells)
    return base


# --- matching is exact ----------------------------------------------------------------------------


def test_a_path_filter_does_not_sweep_in_a_longer_path(tmp_path: Path) -> None:
    """Position 18. On the corpus this is 902 against 66, and they must not merge."""
    folder = day(tmp_path, "2026-08-25", [entry(), entry(path="/v1/messages/count_tokens")])
    rows = read_index(folder)
    assert len(select(rows, Selection(path="/v1/messages"))) == 1
    assert len(select(rows, Selection(path="/v1/messages/count_tokens"))) == 1


def test_repeated_filters_of_one_kind_are_or(tmp_path: Path) -> None:
    folder = day(
        tmp_path,
        "2026-08-25",
        [entry(model="claude-opus-5"), entry(model="claude-sonnet-5"), entry(model="other")],
    )
    rows = read_index(folder)
    chosen = select(rows, Selection(models=("claude-opus-5", "claude-sonnet-5")))
    assert len(chosen) == 2


def test_filters_of_different_kinds_are_and(tmp_path: Path) -> None:
    folder = day(
        tmp_path,
        "2026-08-25",
        [
            entry(session_id="s1", model="claude-opus-5"),
            entry(session_id="s2", model="claude-opus-5"),
            entry(session_id="s1", model="claude-sonnet-5"),
        ],
    )
    rows = read_index(folder)
    chosen = select(rows, Selection(sessions=("s1",), models=("claude-opus-5",)))
    assert len(chosen) == 1


def test_an_empty_selection_means_no_opinion_not_match_nothing(tmp_path: Path) -> None:
    folder = day(tmp_path, "2026-08-25", [entry(), entry(session_id="s2")])
    assert len(select(read_index(folder), Selection())) == 2
    assert Selection().empty


def test_an_agent_filter_selects_on_the_column_that_is_usually_empty(tmp_path: Path) -> None:
    """Task 18. 67 rows carry one, all inside a parent session — a partition key, not a filter."""
    folder = day(tmp_path, "2026-08-25", [entry(agent_id="a1"), entry(), entry(agent_id="a2")])
    rows = read_index(folder)
    assert len(select(rows, Selection(agents=("a1",)))) == 1
    assert len(select(rows, Selection(agents=("a1", "a2")))) == 2


# --- ordering and numbering -----------------------------------------------------------------------


def test_rows_come_back_in_timestamp_order_across_folders(tmp_path: Path) -> None:
    """The index is in *completion* order, so file order is the wrong order."""
    late = day(tmp_path, "2026-08-26", [entry(timestamp="2026-08-26T09:00:00+00:00")])
    early = day(tmp_path, "2026-08-25", [entry(timestamp="2026-08-25T23:00:00+00:00")])
    rows = read_index(late) + read_index(early)
    ordered = select(rows, Selection())
    assert [row.day for row in ordered] == ["2026-08-25", "2026-08-26"]


def test_sequence_numbers_run_per_session_from_one(tmp_path: Path) -> None:
    folder = day(
        tmp_path,
        "2026-08-25",
        [
            entry(session_id="s1", timestamp="2026-08-25T10:00:02+00:00"),
            entry(session_id="s2", timestamp="2026-08-25T10:00:01+00:00"),
            entry(session_id="s1", timestamp="2026-08-25T10:00:00+00:00"),
        ],
    )
    rows = read_index(folder)
    numbers = sequence_numbers(rows)
    by_session = {}
    for row in rows:
        by_session.setdefault(row.session, []).append((row.timestamp, numbers[id(row)]))
    assert sorted(by_session["s1"]) == [
        ("2026-08-25T10:00:00+00:00", "00001"),
        ("2026-08-25T10:00:02+00:00", "00002"),
    ]
    assert by_session["s2"] == [("2026-08-25T10:00:01+00:00", "00001")]


def test_a_sequence_number_is_zero_padded_to_five(tmp_path: Path) -> None:
    folder = day(tmp_path, "2026-08-25", [entry()])
    number = next(iter(sequence_numbers(read_index(folder)).values()))
    assert number == "00001" and len(number) == SEQ_DIGITS


def test_a_row_with_no_session_gets_its_own_bucket(tmp_path: Path) -> None:
    """11 such rows on the corpus — `<out>/bodies//00001-request.json` is not a path."""
    folder = day(tmp_path, "2026-08-25", [entry(session_id="", path="/api/hello")])
    row = read_index(folder)[0]
    assert row.session == ""
    assert (row.session or NO_SESSION) == NO_SESSION


# --- blobs and sentinels --------------------------------------------------------------------------


def test_a_digest_becomes_a_fanned_out_blob_path(tmp_path: Path) -> None:
    folder = day(tmp_path, "2026-08-25", [entry(request_ref="ab" + "0" * 62)])
    blob = read_index(folder)[0].blob("request")
    assert blob is not None
    assert blob.parent.name == "ab"
    assert blob.name.endswith(".zst")
    assert blob.parent.parent.name == "requests"


@pytest.mark.parametrize("sentinel", ["dropped", "too_large", "absent", "error", "none"])
def test_every_sentinel_reads_as_no_blob_rather_than_a_filename(
    tmp_path: Path, sentinel: str
) -> None:
    """All five, not just the one the corpus happens to hold. Used as a name each fails at the
    filesystem, which is a worse error than the honest one."""
    folder = day(tmp_path, "2026-08-25", [entry(request_ref=sentinel)])
    assert read_index(folder)[0].blob("request") is None


def test_an_empty_reference_is_also_no_blob(tmp_path: Path) -> None:
    folder = day(tmp_path, "2026-08-25", [entry(request_ref="")])
    assert read_index(folder)[0].blob("request") is None


# --- the sibling scan, the missing-day defence's only source --------------------------------------


def test_a_session_resumed_the_next_day_is_found_from_the_later_folder(tmp_path: Path) -> None:
    """The one thing that makes task 12's error reachable from the CLI."""
    day(tmp_path, "2026-08-25", [entry(session_id="s1", timestamp="2026-08-25T16:00:00+00:00")])
    resumed = entry(session_id="s1", timestamp="2026-08-26T09:00:00+00:00")
    later = day(tmp_path, "2026-08-26", [resumed])
    assert days_of_sessions([later], ["s1"]) == {"s1": {"2026-08-25", "2026-08-26"}}


def test_a_session_living_in_one_folder_reports_only_that_folder(tmp_path: Path) -> None:
    """It must not cry wolf — a single-day session has to come back clean."""
    day(tmp_path, "2026-08-25", [entry(session_id="other")])
    only = day(tmp_path, "2026-08-26", [entry(session_id="s1")])
    assert days_of_sessions([only], ["s1"]) == {"s1": {"2026-08-26"}}


def test_an_unreadable_sibling_is_skipped_rather_than_fatal(tmp_path: Path) -> None:
    """Catching an omission is the purpose; an unreadable folder is a different problem."""
    (tmp_path / "not-a-day").mkdir()
    folder = day(tmp_path, "2026-08-26", [entry(session_id="s1")])
    assert days_of_sessions([folder], ["s1"]) == {"s1": {"2026-08-26"}}


def test_asking_about_no_sessions_reads_nothing(tmp_path: Path) -> None:
    folder = day(tmp_path, "2026-08-26", [entry()])
    assert days_of_sessions([folder], []) == {}


def test_a_day_folder_with_no_index_is_an_error_that_says_why(tmp_path: Path) -> None:
    (tmp_path / "2026-08-25").mkdir()
    with pytest.raises(ExtractError) as raised:
        read_index(tmp_path / "2026-08-25")
    assert "index.csv" in str(raised.value)


def test_the_day_folders_name_is_carried_on_every_row(tmp_path: Path) -> None:
    """It is not in the CSV, and ordering, blob lookup and the error message all need it."""
    folder = day(tmp_path, "2026-08-25", [entry()])
    row: Row = read_index(folder)[0]
    assert row.day == "2026-08-25"
