"""Command line entry point.

`--check` validates the configuration and exits, which is also what Phase 0 delivers. Without it the
server starts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from . import __version__
from .config import Backend, Config, ConfigError, load_config
from .logging_setup import setup_logging

DEFAULT_CONFIG_PATH = Path("config.yaml")


def main() -> int:
    args = _parse_args()
    load_dotenv()

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _report(config, args.config)

    if args.check:
        print("\nConfiguration is valid.")
        return 0

    import uvicorn

    from .app import create_app

    # Logging is configured here rather than in `create_app`, so building the app in a test does not
    # reconfigure the whole process's logging. It is done after the `--check` return, so validating
    # a config does not create a log file as a side effect.
    try:
        logger = setup_logging(config.logging)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    logger.info(
        "Router %s starting on %s:%d", __version__, config.server.host, config.server.port
    )

    print(f"\nStarting on http://{config.server.host}:{config.server.port}")
    uvicorn.run(
        create_app(config),
        host=config.server.host,
        port=config.server.port,
        # `log_config=None` leaves uvicorn's loggers alone, so the handlers `setup_logging` put on
        # them stand. Uvicorn's default config would replace those and set `propagate = False`,
        # and its startup lines and access log would never reach the router's file.
        log_config=None,
    )
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ilirium-llm-router",
        description="Route Claude Code to Anthropic and to locally served models at the same time.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"path to the YAML config file (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the configuration, report it, and exit without starting the server",
    )
    return parser.parse_args()


def _report(config: Config, path: Path) -> None:
    """Print what was loaded, so a misconfiguration is visible before any traffic arrives."""
    print(f"ilirium-llm-router {__version__}")
    print(f"Config:   {path.resolve()}")
    print(f"Listening on {config.server.host}:{config.server.port}")
    print("\nBackends:")
    print(
        f"  anthropic  {config.backends.anthropic.base_url}   "
        f"models starting with 'claude-'   [{_credential(config.backends.anthropic)}]"
    )
    print(
        f"  lmstudio   {config.backends.lmstudio.base_url}   "
        f"every other model                [{_credential(config.backends.lmstudio)}]"
    )
    print(
        "\nLog:      "
        f"{config.logging.file}  ({config.logging.level}, "
        f"rotate at {_mib(config.logging.max_bytes)}, keep {config.logging.backup_count})"
    )
    print(
        "Stats:    "
        f"{config.stats.file}  (rotate at {_mib(config.stats.max_bytes)}, "
        f"keep {config.stats.backup_count})"
    )


def _credential(backend: Backend) -> str:
    if backend.api_key_env:
        return f"key from ${backend.api_key_env}"
    return f"{backend.credential} incoming credential"


def _mib(value: int) -> str:
    return f"{value / 1024 / 1024:.1f} MiB"


if __name__ == "__main__":
    sys.exit(main())
