"""The whole thing, with real files.

Everywhere else the stats writer is a stand-in that keeps rows in a list, which is the right tool
for asking what the router *decided* to record. This file asks the question that stand-in cannot:
does a call actually end up as a line in a file on disk, through the writer the app builds for
itself from the config?

The two tests that could not exist anywhere else are the rotation one and the concurrency one. Both
are about what happens to a file under traffic, and both fail in ways that are invisible until
somebody opens the file weeks later and finds it unreadable.
"""

from __future__ import annotations

import asyncio
import csv
import logging
from collections.abc import AsyncIterator, Iterator
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path

import httpx
from conftest import CLAUDE_BODY, CLAUDE_CODE_HEADERS, make_config
from fastapi.testclient import TestClient

from ilirium_llm_router.app import create_app
from ilirium_llm_router.config import Config, Stats
from ilirium_llm_router.stats import COLUMNS

JSON_HEADERS = {"content-type": "application/json"}
REPLY = b'{"stop_reason":"end_turn","usage":{"input_tokens":15,"output_tokens":29}}'


def config_writing_to(path: Path, **stats: object) -> Config:
    config = make_config()
    config.stats = Stats(file=path, **stats)  # type: ignore[arg-type]
    return config


@contextmanager
def router(config: Config, dawdle: float = 0.0) -> Iterator[TestClient]:
    """The app building its own stats writer from the config, the way it does in production.

    A *fresh* reply per request, unlike the single-call stand-in in `conftest.py`: a streamed
    response can only be consumed once, so handing out the same object twice fails on the second
    call. Every test here makes several.

    `dawdle` puts a pause between the two halves of the reply. A mock backend answers instantly, so
    without it concurrent calls finish one after another and never test the thing they claim to.
    """

    def answer(request: httpx.Request) -> httpx.Response:
        async def body() -> AsyncIterator[bytes]:
            yield REPLY[:30]
            if dawdle:
                await asyncio.sleep(dawdle)
            yield REPLY[30:]

        return httpx.Response(200, headers=JSON_HEADERS, content=body())

    client = httpx.AsyncClient(transport=httpx.MockTransport(answer))
    with TestClient(create_app(config, client)) as test_client:
        yield test_client


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_a_call_becomes_a_line_in_a_file(tmp_path: Path) -> None:
    """The wiring every other test takes on trust: config → app → writer → disk."""
    path = tmp_path / "calls.csv"
    with router(config_writing_to(path)) as client:
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    written = rows(path)
    assert len(written) == 1
    row = written[0]
    assert row["backend"] == "anthropic"
    assert row["model"] == "claude-sonnet-5"
    assert (row["input_tokens"], row["output_tokens"]) == ("15", "29")
    assert row["stop_reason"] == "end_turn"
    assert row["error_status"] == "ok"
    assert row["router_version"] != ""


def test_the_file_survives_a_restart_without_a_second_header(tmp_path: Path) -> None:
    """The router restarting must not drop a header into the middle of yesterday's rows."""
    path = tmp_path / "calls.csv"
    for _ in range(3):
        with router(config_writing_to(path)) as client:
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    assert len(rows(path)) == 3
    assert path.read_text(encoding="utf-8").count("timestamp,session_id") == 1


def test_calls_finishing_at_once_do_not_interleave(tmp_path: Path) -> None:
    """The constraint the writer's lock exists for.

    Two rows spliced into one line is not a row that is slightly wrong — it is a file that no longer
    parses, and it happens only under the concurrency a single-threaded test never produces.
    """
    path = tmp_path / "calls.csv"
    calls = 60

    # Every call is mid-reply while the others finish, so the writer really is reached at once.
    with router(config_writing_to(path), dawdle=0.02) as client:

        def one_call(index: int) -> int:
            reply = client.post(
                "/v1/messages",
                content=CLAUDE_BODY,
                headers={**CLAUDE_CODE_HEADERS, "x-claude-code-session-id": f"s{index}"},
            )
            return reply.status_code

        with ThreadPoolExecutor(max_workers=12) as pool:
            assert list(pool.map(one_call, range(calls))) == [200] * calls

    written = rows(path)
    assert len(written) == calls, "a row was lost or two were spliced together"
    # Every row complete and every session id accounted for exactly once.
    assert all(row["error_status"] == "ok" for row in written)
    assert sorted(row["session_id"] for row in written) == sorted(
        f"s{index}" for index in range(calls)
    )


def test_every_rotated_segment_is_readable_on_its_own(tmp_path: Path) -> None:
    """Rotation under real traffic, not from a loop over the writer.

    A segment that lost its header is not discovered when it rotates; it is discovered weeks later,
    when the measurements it holds are the ones being asked for.
    """
    path = tmp_path / "calls.csv"
    config = config_writing_to(path, max_bytes=800, backup_count=5)

    with router(config) as client:
        for _ in range(40):
            client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    segments = sorted(tmp_path.glob("calls.csv*"))
    assert len(segments) > 1, "the file never rotated, so this test proved nothing"
    for segment in segments:
        parsed = rows(segment)
        assert parsed, f"{segment.name} has a header but no rows"
        assert all(set(row) == set(COLUMNS) for row in parsed), (
            f"{segment.name} does not parse against the header"
        )


def test_each_call_leaves_a_log_line(tmp_path: Path) -> None:
    """The other half of the promise: a human-readable trace next to the machine-readable one."""
    with (
        _capturing() as records,
        router(config_writing_to(tmp_path / "calls.csv")) as client,
    ):
        client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)

    lines = [record.getMessage() for record in records]
    assert any("claude-sonnet-5" in line and "anthropic" in line for line in lines), lines


def test_the_body_is_never_logged(tmp_path: Path) -> None:
    """It carries the whole conversation, and on the cloud side a real credential beside it."""
    secret = b'{"model":"claude-sonnet-5","messages":[{"role":"user","content":"SECRET"}]}'

    with (
        _capturing() as records,
        router(config_writing_to(tmp_path / "calls.csv")) as client,
    ):
        client.post("/v1/messages", content=secret, headers=CLAUDE_CODE_HEADERS)

    logged = " ".join(record.getMessage() for record in records)
    assert "SECRET" not in logged
    assert "sk-ant-oat01-example" not in logged
    assert "SECRET" not in (tmp_path / "calls.csv").read_text(encoding="utf-8")


def test_a_file_that_breaks_after_startup_does_not_break_the_call(tmp_path: Path) -> None:
    """A full disk must not break a conversation — the rule that outranks every column.

    Failing the *rotation* rather than the open, because that is the realistic shape of the problem:
    the file opened fine at startup and the trouble arrives later. A read-only directory means the
    rename to `calls.csv.1` cannot happen, which is what a real `StatsWriter` does here, not a
    stand-in that was told to raise.
    """
    directory = tmp_path / "logs"
    directory.mkdir()
    path = directory / "calls.csv"
    config = config_writing_to(path, max_bytes=200, backup_count=1)

    with router(config) as client:
        directory.chmod(0o500)  # readable and listable, not writable
        try:
            replies = [
                client.post("/v1/messages", content=CLAUDE_BODY, headers=CLAUDE_CODE_HEADERS)
                for _ in range(5)
            ]
        finally:
            directory.chmod(0o700)

    assert [reply.status_code for reply in replies] == [200] * 5
    assert all(reply.content == REPLY for reply in replies)


@contextmanager
def _capturing() -> Iterator[list[logging.LogRecord]]:
    """Collect the router's own log records, wherever they were headed."""
    records: list[logging.LogRecord] = []
    handler = logging.Handler()
    handler.emit = records.append  # type: ignore[method-assign]
    logger = logging.getLogger("ilirium_llm_router")
    previous_level, previous_propagate = logger.level, logger.propagate
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.addHandler(handler)
    try:
        yield records
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate
