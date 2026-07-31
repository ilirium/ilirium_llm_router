"""Setting up the rotating log file.

Every call gets a human-readable line carrying the time, the model, the chosen backend, the outcome
and the duration. Rotation is size-based, with the size and number of kept files taken from config.

Log metadata only. The request body is never logged: it carries the whole conversation, and on the
cloud side it arrives alongside a real credential.

Called from `cli.py` rather than `create_app`, so importing the app in a test does not reconfigure
the process's logging.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler

from .config import ConfigError, Logging

LOGGER_NAME = "ilirium_llm_router"

# Uvicorn's own logger, parent of `uvicorn.error` and `uvicorn.access`. Its lines go into the same
# file as ours: when a call went wrong, "did the request even arrive" and "was the server still up"
# are answered by the lines either side of it, and interleaving is only possible in one file.
#
# This works only because `cli.py` starts uvicorn with `log_config=None`. Left to itself uvicorn
# installs its own handlers here and sets `propagate = False` on the children, and the lines would
# go to the console alone.
UVICORN_LOGGER_NAME = "uvicorn"

# Fixed-width level and a millisecond timestamp, so a column of these lines reads as a table.
LINE_FORMAT = "%(asctime)s  %(levelname)-7s  %(message)s"


class UtcFormatter(logging.Formatter):
    """The router's line format, timestamped in UTC exactly as the CSV timestamps a row.

    The two files are meant to be read side by side — that is the whole reason uvicorn's lines are
    pointed at this one — and correlating them only works if a log line and its CSV row carry the
    same string. They did not: the log wrote naive *local* time and the CSV writes UTC, so on
    2026-07-31 the same call appeared at `11:46:47` in one file and `08:46:47+00:00` in the other,
    and lining them up meant remembering an offset neither file records.

    `formatTime` is overridden rather than a `datefmt` passed, because `datefmt` truncates to whole
    seconds — and a phase whose subject is measuring durations should not round its own clock.
    """

    def formatTime(
        self, record: logging.LogRecord, datefmt: str | None = None
    ) -> str:
        stamped = datetime.fromtimestamp(record.created, UTC)
        return stamped.isoformat(timespec="milliseconds")


def get_logger() -> logging.Logger:
    """The one logger the router writes to. Usable before `setup_logging` — it just goes nowhere."""
    return logging.getLogger(LOGGER_NAME)


def setup_logging(config: Logging) -> logging.Logger:
    """Point the router's logger at its rotating file, and at the console alongside it.

    Called once at startup. Calling it again replaces the handlers rather than adding a second set,
    so a repeated call cannot silently double every line.

    Raises ConfigError if the file cannot be opened, stopping the program with a readable message
    the way a bad config value does. That is the opposite of the rule that governs logging once the
    router is serving, where a failure is caught and dropped so telemetry can never break a call —
    here nothing is being proxied yet, and a log that silently goes nowhere is worse than a refusal
    to start.
    """
    formatter = UtcFormatter(LINE_FORMAT)

    try:
        config.file.parent.mkdir(parents=True, exist_ok=True)
        to_file = RotatingFileHandler(
            config.file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8",
        )
    except OSError as exc:
        raise ConfigError(
            f"Could not open the log file {config.file}: {exc}\n"
            f"Check 'logging.file' in the config, or the permissions on the directory holding it."
        ) from exc
    to_file.setFormatter(formatter)

    # The console too: a router started in a terminal that says nothing looks broken, and the
    # interesting failure — LM Studio not running — should not need a second window to notice.
    to_console = logging.StreamHandler()
    to_console.setFormatter(formatter)

    handlers = [to_file, to_console]
    # The same two handler *objects* are shared with uvicorn's logger rather than a second pair
    # built for it. Two `RotatingFileHandler`s open on one file would each hold their own size
    # count and roll over independently, renaming the file out from under the other one.
    _attach(get_logger(), handlers, config.level)
    _attach(logging.getLogger(UVICORN_LOGGER_NAME), handlers, config.level)

    return get_logger()


def _attach(
    logger: logging.Logger, handlers: list[logging.Handler], level: str
) -> None:
    """Give `logger` exactly these handlers, replacing whatever it had."""
    for existing in list(logger.handlers):
        logger.removeHandler(existing)
        # Closed so a repeated call does not leak the previous file handle. The `in` guard is for
        # the shared objects: `handlers` is attached to two loggers, and closing one here would
        # leave the other writing to a shut file.
        if existing not in handlers:
            existing.close()
    for handler in handlers:
        logger.addHandler(handler)
    logger.setLevel(level)
    # Ours alone: the root logger belongs to whoever is embedding us.
    logger.propagate = False
