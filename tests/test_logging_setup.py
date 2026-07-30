"""The router's own log file.

A small surface, but the claims worth testing are the ones that fail *quietly*: a second call to
`setup_logging` doubling every line, a child logger's records never arriving, a level that silently
discards what someone went looking for. None of those raise; all of them produce a log that is
wrong in a way you only notice when you need it.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from ilirium_llm_router.config import ConfigError, Logging
from ilirium_llm_router.logging_setup import (
    LOGGER_NAME,
    UVICORN_LOGGER_NAME,
    get_logger,
    setup_logging,
)


@pytest.fixture(autouse=True)
def _restore_logging() -> Iterator[None]:
    """These loggers are process-wide state, so put them back the way they were found.

    Without this a test that configures logging leaks its handlers into every test after it, and
    into whichever file pytest happens to run next.
    """
    names = (LOGGER_NAME, UVICORN_LOGGER_NAME)
    saved = {
        name: (
            list(logging.getLogger(name).handlers),
            logging.getLogger(name).level,
            logging.getLogger(name).propagate,
        )
        for name in names
    }
    yield
    closed: set[logging.Handler] = set()
    for name in names:
        logger = logging.getLogger(name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            if handler not in closed:  # one object can sit on both loggers
                handler.close()
                closed.add(handler)
        handlers, level, propagate = saved[name]
        logger.handlers[:] = handlers
        logger.setLevel(level)
        logger.propagate = propagate


def lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def test_a_line_reaches_the_configured_file(tmp_path: Path) -> None:
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path)).info("Router starting")

    assert len(lines(path)) == 1
    assert lines(path)[0].endswith("Router starting")


def test_the_directory_is_created_if_it_is_missing(tmp_path: Path) -> None:
    """The configured default is `logs/router.log`, and `make clean` leaves `logs/` alone."""
    path = tmp_path / "logs" / "nested" / "router.log"
    setup_logging(Logging(file=path)).info("Router starting")

    assert path.exists()


def test_a_child_logger_writes_to_the_same_file(tmp_path: Path) -> None:
    """Other modules use a plain `logging.getLogger(__name__)`; those records must arrive here."""
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path))

    logging.getLogger(f"{LOGGER_NAME}.proxy").info("relayed to lmstudio")

    assert lines(path)[0].endswith("relayed to lmstudio")


def test_the_configured_level_is_applied(tmp_path: Path) -> None:
    path = tmp_path / "router.log"
    logger = setup_logging(Logging(file=path, level="WARNING"))

    logger.info("routine call")
    logger.warning("lm studio is not running")

    assert len(lines(path)) == 1
    assert lines(path)[0].endswith("lm studio is not running")


def test_each_line_carries_the_time_to_the_millisecond(tmp_path: Path) -> None:
    """Phase 2 exists to measure durations; its own log rounding to the second would be a joke."""
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path)).info("Router starting")

    assert re.fullmatch(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}\s+INFO\s+Router starting",
        lines(path)[0],
    ), f"unexpected line shape: {lines(path)[0]!r}"


def test_calling_setup_twice_does_not_double_every_line(tmp_path: Path) -> None:
    """A restart-in-place, or a second entry point, must not quietly write everything twice."""
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path))
    setup_logging(Logging(file=path)).info("Router starting")

    assert len(lines(path)) == 1


def test_the_file_rotates_and_keeps_the_configured_backups(tmp_path: Path) -> None:
    path = tmp_path / "router.log"
    logger = setup_logging(Logging(file=path, max_bytes=300, backup_count=2))

    for index in range(60):
        logger.info("a call that took a while and said so at length, number %d", index)

    assert sorted(p.name for p in tmp_path.glob("router.log*")) == [
        "router.log",
        "router.log.1",
        "router.log.2",
    ]


def test_records_do_not_escape_to_the_root_logger(tmp_path: Path) -> None:
    """What lands where is decided by our config, not by whatever uvicorn does to the root logger."""
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path))

    caught: list[logging.LogRecord] = []
    collector = logging.Handler()
    collector.emit = caught.append  # type: ignore[method-assign]
    root = logging.getLogger()
    root.addHandler(collector)
    try:
        get_logger().info("Router starting")
    finally:
        root.removeHandler(collector)

    assert caught == []


def test_the_line_also_goes_to_the_console(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A router started in a terminal that says nothing looks broken."""
    setup_logging(Logging(file=tmp_path / "router.log")).info("Router starting")

    assert "Router starting" in capsys.readouterr().err


def test_uvicorns_own_lines_land_in_the_router_log(tmp_path: Path) -> None:
    """"Did the request arrive" and "was the server up" are answered by the lines either side."""
    path = tmp_path / "router.log"
    setup_logging(Logging(file=path))

    logging.getLogger("uvicorn.error").info("Application startup complete.")
    logging.getLogger("uvicorn.access").info(
        '%s - "%s %s HTTP/%s" %d', "127.0.0.1:54321", "POST", "/v1/messages", "1.1", 200
    )

    written = lines(path)
    assert written[0].endswith("Application startup complete.")
    # Uvicorn's access records carry their arguments unformatted, so a plain `Formatter` has to be
    # the thing that fills them in. Written out here because the alternative is a row of raw `%s`.
    assert written[1].endswith('127.0.0.1:54321 - "POST /v1/messages HTTP/1.1" 200')


def test_uvicorn_and_the_router_share_one_file_handler(tmp_path: Path) -> None:
    """Two handlers open on one file would each count its size and rotate over the other's rename."""
    setup_logging(Logging(file=tmp_path / "router.log"))

    ours = {id(handler) for handler in get_logger().handlers}
    theirs = {id(handler) for handler in logging.getLogger(UVICORN_LOGGER_NAME).handlers}
    assert ours == theirs


def test_an_unusable_log_path_is_reported_as_a_config_error(tmp_path: Path) -> None:
    """A startup problem, so it stops the program the way a bad config value does — not a traceback.

    This is the opposite of the rule that governs logging *while* serving, where a failure is caught
    and dropped so telemetry can never break a call. Here nothing is being proxied yet, and a log
    that silently goes nowhere is worse than a refusal to start.
    """
    blocked = tmp_path / "blocked"
    blocked.write_text("not a directory")

    with pytest.raises(ConfigError) as raised:
        setup_logging(Logging(file=blocked / "router.log"))

    assert "blocked" in str(raised.value)
