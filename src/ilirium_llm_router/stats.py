"""One CSV row per call, so models and backends can be compared in a spreadsheet.

The columns and the reason each one earns its place are in CLAUDE.md under "Observability: log + CSV
stats". This file owns the row's *shape* and the file it goes into; `observe.py` owns the measuring.

Constraints this file has to keep:

- Never let telemetry break a call. Any failure here is caught and dropped.
- Rotation is size-based. On rotation the CSV must re-emit its header row, or rotated segments
  cannot be parsed on their own.
- Several calls can finish at once; rows must not interleave into corrupted lines.
- Nothing derived and nothing body-shaped. Tokens per second belongs in the spreadsheet, not here,
  and prompts, message counts and tool names belong nowhere in this file at all.

Rotation rides on `logging.handlers.RotatingFileHandler` rather than a hand-rolled rename dance:
`max_bytes`/`backup_count` map straight onto `maxBytes`/`backupCount`, it is battle-tested, and its
lock is what keeps concurrent rows from interleaving. The single override is `doRollover`, to write
the header into the fresh file.

Note `request_bytes` is dominated by the fixed ~110 KB preamble of system prompt and tool schemas, so
treat it as a fallback rather than a measure of conversation size.

**The file is in completion order, not arrival order.** A row is appended when its call finishes,
while `timestamp` records when the call *arrived*, so a slow call lands after quicker ones that
started later — 14 adjacent pairs are out of order in
`docs/phase-2-step-6-session/calls.csv`, one of them by nearly two minutes. Sort by `timestamp`
before analysing.

Deliberately not fixed. Ordering the file would mean holding finished rows in memory until the calls
that started before them came back, which trades a sort in the spreadsheet for losing every buffered
row when the process stops — and "never let telemetry break a call" argues the same way about
holding telemetry hostage to a call still in flight.
"""

from __future__ import annotations

import csv
import io
import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Literal

from . import __version__
from .config import Stats
from .logging_setup import get_logger

# How a call ended. `ok` needs no error columns; the other four fill in `error_code`, and every one
# of them is a failure a spreadsheet filter should be able to count.
ErrorStatus = Literal["ok", "http_error", "stream_error", "transport_error", "client_disconnect"]

COLUMNS = (
    "timestamp",
    "session_id",
    "agent_id",
    "backend",
    "model",
    "path",
    "stream",
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
    "stop_reason",
    "request_bytes",
    "response_bytes",
    "ttfb_ms",
    "duration_ms",
    "error_status",
    "error_code",
    "error_message",
    "router_version",
)

# `error_message` is the one free-text column. Long enough to carry a backend's own wording, short
# enough that one bad call cannot dominate the file.
MAX_ERROR_MESSAGE = 200


@dataclass(frozen=True)
class CallRecord:
    """What one call did. Every field maps to exactly one column, in `COLUMNS` order.

    `None` means "not known", and is written as an empty cell rather than a zero — an absent token
    count and a genuine zero are different facts.
    """

    timestamp: str
    session_id: str
    agent_id: str
    backend: str
    model: str
    path: str
    stream: bool | None
    input_tokens: int | None
    output_tokens: int | None
    cache_read_input_tokens: int | None
    cache_creation_input_tokens: int | None
    stop_reason: str | None
    request_bytes: int
    response_bytes: int
    ttfb_ms: int | None
    duration_ms: int
    error_status: ErrorStatus
    error_code: str
    error_message: str
    router_version: str = __version__

    def cells(self) -> list[str]:
        """The row, in column order.

        Read out by name from `COLUMNS` rather than listed again here, so the header and the values
        cannot fall out of step. `test_stats.py` checks the two sets still match.
        """
        return [_cell(getattr(self, column)) for column in COLUMNS]


class StatsWriter:
    """The CSV file: one row per call, rotated by size, header re-emitted after each rollover.

    Owned by the app rather than reached for globally, so a test can point one at a temporary path.
    """

    def __init__(self, config: Stats) -> None:
        self._handler = _RotatingCsvHandler(config)
        self._logger = get_logger()

    @property
    def path(self) -> str:
        return self._handler.baseFilename

    def write(self, record: CallRecord) -> None:
        """Append one row. A failure here is reported and dropped — the call already succeeded.

        `handle` rather than `emit`: the handler's lock lives in `handle`, and it is what stops two
        calls finishing at once from interleaving into a corrupted line.
        """
        try:
            self._handler.handle(_as_log_record(_render(record.cells())))
        except Exception as exc:  # noqa: BLE001 — telemetry must never break a call
            self._logger.warning("Could not write a stats row: %s: %s", type(exc).__name__, exc)

    def close(self) -> None:
        self._handler.close()


class _RotatingCsvHandler(RotatingFileHandler):
    """`RotatingFileHandler` that keeps a header row at the top of every file it writes.

    Without this a rotated segment is a headerless block of values, which no spreadsheet can open on
    its own — and a segment that cannot be read alone is the one that gets thrown away.
    """

    def __init__(self, config: Stats) -> None:
        config.file.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(
            config.file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8",
        )
        self.setFormatter(logging.Formatter("%(message)s"))
        self._write_header_if_empty()

    def doRollover(self) -> None:
        super().doRollover()
        self._write_header_if_empty()

    def _write_header_if_empty(self) -> None:
        """Append to an existing file, start a new one with its header.

        Checked rather than assumed: the router restarting must not drop a second header into the
        middle of yesterday's rows.
        """
        if self.stream is None:
            self.stream = self._open()
        self.stream.seek(0, io.SEEK_END)
        if self.stream.tell() == 0:
            self.stream.write(_render(list(COLUMNS)) + self.terminator)
            self.flush()


def _render(cells: list[str]) -> str:
    """One CSV line, quoted and escaped by `csv` rather than by hand.

    Model IDs like `google/gemma-4-e4b` are harmless, but `error_message` is free text and a stray
    comma or quote in it would otherwise shift every column after it.
    """
    buffer = io.StringIO()
    csv.writer(buffer, lineterminator="").writerow(cells)
    return buffer.getvalue()


def _cell(value: object) -> str:
    """One value as it appears in the file. `None` is an empty cell, never a zero."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return _one_line(value)
    return str(value)


def _one_line(text: str) -> str:
    """Free text folded onto a single line and capped.

    `csv` would quote an embedded newline correctly, but a row that spans lines defeats `grep`,
    `tail` and every other tool anyone will actually reach for when reading this file.
    """
    folded = " ".join(text.split())
    if len(folded) > MAX_ERROR_MESSAGE:
        folded = folded[: MAX_ERROR_MESSAGE - 1] + "…"
    return folded


def _as_log_record(line: str) -> logging.LogRecord:
    """Wrap a finished line so the handler's rotation and lock apply to it.

    `args` is empty on purpose: with no arguments `LogRecord.getMessage` returns the message
    untouched, so a stray `%` in a model ID or an error string cannot be read as a format specifier.
    """
    return logging.LogRecord(
        name=f"{get_logger().name}.stats",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg=line,
        args=(),
        exc_info=None,
    )
