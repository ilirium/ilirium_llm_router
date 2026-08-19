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

    # Before the config is loaded, deliberately: reading a day folder back needs the folder and
    # nothing else, which is the self-containment rule the reader exists to demonstrate.
    if args.extract is not None:
        return _extract(args.extract)

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

    logger.info("Router %s starting on %s:%d", __version__, config.server.host, config.server.port)

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
    parser.add_argument(
        "--extract",
        type=Path,
        metavar="DAY",
        help="read every body back out of one corpus day folder, verify each against the digest "
        "in its own filename, and report; does not start the server",
    )
    return parser.parse_args()


def _extract(day: Path) -> int:
    """Read a day folder back and say whether all of it opens.

    **Minimal on purpose.** The extraction *tool* — selection by session, call or model, output
    layout, bulk verification — is Phase 11's. What this is for is making the round trip a thing
    somebody can run rather than a snippet written once, which is what a check nobody can repeat
    turns into.

    It reads the day folder and nothing above it, so it is also the self-containment rule made
    executable: `tar` a day, unpack it elsewhere, point this at it.
    """
    from .corpus import CorpusError, CorpusReader

    if not day.is_dir():
        print(f"error: {day} is not a directory", file=sys.stderr)
        return 1

    reader = CorpusReader(day)
    directions = reader.directions()
    if not directions:
        print(f"error: {day} holds no requests/ or responses/ folder", file=sys.stderr)
        return 1

    total = plaintext = compressed = failed = 0
    for direction in directions:
        for blob in reader.blobs(direction):
            total += 1
            compressed += blob.stat().st_size
            try:
                plaintext += len(reader.read(blob))
            except CorpusError as exc:
                failed += 1
                print(f"  FAILED  {direction}/{blob.name}: {exc}", file=sys.stderr)

    manifest = day / "manifest"
    if manifest.exists():
        print(manifest.read_text(encoding="utf-8").strip())
    dictionaries = sorted(p.name for p in (day / "dicts").glob("*.dict"))
    print(f"dictionaries: {', '.join(dictionaries) if dictionaries else 'none'}")
    print(f"{total} blob(s), {failed} failed")
    if total and not failed:
        print(f"{plaintext} → {compressed} bytes, {plaintext / compressed:.3f}x")
        print("every blob verified against the digest in its own filename")
    return 1 if failed else 0


def _report(config: Config, path: Path) -> None:
    """Print what was loaded, so a misconfiguration is visible before any traffic arrives."""
    print(f"ilirium-llm-router {__version__}")
    print(f"Config:   {path.resolve()}")
    print(f"Listening on {config.server.host}:{config.server.port}")
    print("\nBackends:")
    print(
        f"  anthropic  {config.backends.anthropic.base_url}   "
        f"models starting with 'claude-'   [{_credential(config.backends.anthropic)}] "
        f"[{_silence(config.backends.anthropic)}]"
    )
    print(
        f"  lmstudio   {config.backends.lmstudio.base_url}   "
        f"every other model                [{_credential(config.backends.lmstudio)}] "
        f"[{_silence(config.backends.lmstudio)}]"
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
    _report_corpus(config)


def _report_corpus(config: Config) -> None:
    """Print the corpus block, including when it is off.

    **Printed even when disabled, and that is the point of printing it.** The store is opt-in, so
    the question an operator actually has is *is it on?* — and a block that appears only when
    enabled answers that by absence, which reads the same as a version that does not have the
    feature at all.
    """
    corpus = config.corpus
    if not corpus.enabled:
        print(f"Corpus:   off  (would write to {corpus.dir})")
        return
    print(
        "Corpus:   "
        f"{corpus.dir}  (zstd level {corpus.compress_level_zstd}, "
        f"body max {_mib(corpus.body_max_bytes)}, queue max {_mib(corpus.queue_max_bytes)})"
    )
    retrain = corpus.retrain
    if retrain.window_days == 0:
        print("          retrain: off  (the newest installed dictionary keeps being used)")
        return
    print(
        f"          retrain: {retrain.window_days} day(s) minimum, "
        f"samples from {retrain.sample_min_bytes} bytes, "
        f"maxdict {retrain.maxdict}, k {retrain.k}"
    )


def _credential(backend: Backend) -> str:
    """One line per mode. This used to prefer the key over the mode, which was the display half of
    the ambiguity the config shape now refuses."""
    if backend.credential == "inject":
        return f"inject key from ${backend.api_key_env}"
    return f"{backend.credential} incoming credential"


def _silence(backend: Backend) -> str:
    """Named for what the number measures, since "timeout" reads as a budget for the whole call."""
    return f"give up after {backend.read_timeout:g}s silent"


def _mib(value: int) -> str:
    return f"{value / 1024 / 1024:.1f} MiB"


if __name__ == "__main__":
    sys.exit(main())
