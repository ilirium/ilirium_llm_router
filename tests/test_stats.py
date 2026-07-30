"""The CSV file itself: what a row looks like, and that rotated segments stay readable.

The rotation tests are the point of this file. A row that comes out slightly wrong is visible the
first time anyone opens the file; a rotated segment that lost its header is only discovered weeks
later, when the measurements it holds are the ones being asked for.
"""

from __future__ import annotations

import csv
from dataclasses import fields
from pathlib import Path

import pytest

from ilirium_llm_router.config import Stats
from ilirium_llm_router.stats import COLUMNS, CallRecord, StatsWriter


def a_record(**overrides: object) -> CallRecord:
    """A plausible successful call, with fields overridden per test."""
    defaults: dict[str, object] = {
        "timestamp": "2026-07-30T10:00:00.000+00:00",
        "session_id": "sess-1",
        "agent_id": "",
        "backend": "lmstudio",
        "model": "google/gemma-4-e4b",
        "path": "/v1/messages",
        "stream": True,
        "input_tokens": 15,
        "output_tokens": 29,
        "cache_read_input_tokens": 5,
        "cache_creation_input_tokens": None,
        "stop_reason": "end_turn",
        "request_bytes": 118_000,
        "response_bytes": 2_400,
        "ttfb_ms": 812,
        "duration_ms": 3_421,
        "error_status": "ok",
        "error_code": "",
        "error_message": "",
    }
    return CallRecord(**(defaults | overrides))  # type: ignore[arg-type]


def rows(path: Path) -> list[list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.reader(handle))


def writer_at(path: Path, **overrides: object) -> StatsWriter:
    return StatsWriter(Stats(file=path, **overrides))  # type: ignore[arg-type]


def test_the_columns_and_the_record_fields_are_the_same_set() -> None:
    """`cells()` reads values out by column name, so a field the header forgot writes nothing."""
    assert tuple(field.name for field in fields(CallRecord)) == COLUMNS


def test_a_new_file_starts_with_the_header(tmp_path: Path) -> None:
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(a_record())
    writer.close()

    written = rows(path)
    assert written[0] == list(COLUMNS)
    assert len(written) == 2


def test_reopening_appends_rather_than_writing_a_second_header(tmp_path: Path) -> None:
    """A restart must not drop a header into the middle of yesterday's rows."""
    path = tmp_path / "calls.csv"
    for _ in range(2):
        writer = writer_at(path)
        writer.write(a_record())
        writer.close()

    written = rows(path)
    assert written[0] == list(COLUMNS)
    assert [row[0] for row in written[1:]] == ["2026-07-30T10:00:00.000+00:00"] * 2


def test_every_rotated_segment_carries_its_own_header(tmp_path: Path) -> None:
    """Without this a rotated file is a headerless block of numbers that no spreadsheet can open."""
    path = tmp_path / "calls.csv"
    writer = writer_at(path, max_bytes=500, backup_count=3)
    for _ in range(12):
        writer.write(a_record())
    writer.close()

    rotated = sorted(tmp_path.glob("calls.csv*"))
    assert len(rotated) > 1, "the file never rotated, so this test proved nothing"
    for segment in rotated:
        assert rows(segment)[0] == list(COLUMNS), f"{segment.name} lost its header"


def test_rotation_keeps_only_the_configured_number_of_files(tmp_path: Path) -> None:
    path = tmp_path / "calls.csv"
    writer = writer_at(path, max_bytes=500, backup_count=2)
    for _ in range(40):
        writer.write(a_record())
    writer.close()

    assert sorted(p.name for p in tmp_path.glob("calls.csv*")) == [
        "calls.csv",
        "calls.csv.1",
        "calls.csv.2",
    ]


def test_a_missing_value_is_an_empty_cell_and_not_a_zero(tmp_path: Path) -> None:
    """An absent token count and a real zero are different facts and must stay distinguishable."""
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(a_record(input_tokens=None, output_tokens=0, stop_reason=None))
    writer.close()

    row = dict(zip(COLUMNS, rows(path)[1], strict=True))
    assert row["input_tokens"] == ""
    assert row["output_tokens"] == "0"
    assert row["stop_reason"] == ""


def test_stream_is_written_as_a_word_not_a_python_repr(tmp_path: Path) -> None:
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(a_record(stream=True))
    writer.write(a_record(stream=False))
    writer.write(a_record(stream=None))
    writer.close()

    column = COLUMNS.index("stream")
    assert [row[column] for row in rows(path)[1:]] == ["true", "false", ""]


def test_an_error_message_stays_on_one_line_and_in_one_cell(tmp_path: Path) -> None:
    """Free text with a comma, a quote and a newline in it must not shift the columns after it."""
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(
        a_record(
            error_status="stream_error",
            error_code="overloaded_error",
            error_message='Overloaded, "try again"\nlater',
        )
    )
    writer.close()

    written = rows(path)
    assert len(written) == 2, "the message broke the row across lines"
    row = dict(zip(COLUMNS, written[1], strict=True))
    assert row["error_message"] == 'Overloaded, "try again" later'
    assert row["router_version"] == a_record().router_version


def test_a_very_long_error_message_is_capped(tmp_path: Path) -> None:
    """One bad call must not be able to dominate the file."""
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(a_record(error_status="http_error", error_message="x" * 5000))
    writer.close()

    assert len(rows(path)[1][COLUMNS.index("error_message")]) <= 200


def test_a_model_id_containing_a_percent_sign_survives(tmp_path: Path) -> None:
    """Rows ride on a logging handler, whose records normally treat `%` as a format specifier."""
    path = tmp_path / "calls.csv"
    writer = writer_at(path)
    writer.write(a_record(model="weird/model-100%-local"))
    writer.close()

    assert rows(path)[1][COLUMNS.index("model")] == "weird/model-100%-local"


def test_a_failing_writer_does_not_raise(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Telemetry never breaks a call — not even when the disk is full."""
    writer = writer_at(tmp_path / "calls.csv")

    def explode(record: object) -> None:
        raise OSError("No space left on device")

    monkeypatch.setattr(writer._handler, "handle", explode)
    writer.write(a_record())
    writer.close()
