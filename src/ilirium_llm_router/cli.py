"""Command line entry point.

**Subcommands on one entry point** — owner's decision, Phase 11 position 2. Today's surface was nine
flags on one parser, most of which apply to exactly one mode: `--maxdict` is meaningless with
`--extract`, and argparse cannot say so. A subcommand makes that structural instead of documented.

**Bare `ilirium-llm-router` still starts the server**, and that is deliberate rather than a
leftover. `make run` depends on it, so does habit, and Phase 12 makes this a `uv tool` where the
bare form is the one people type. `serve` is the explicit spelling of the same thing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

from . import __version__
from .config import Backend, Config, ConfigError, load_config
from .logging_setup import setup_logging

if TYPE_CHECKING:  # imported for typing only -- the runtime imports stay inside the functions,
    # so `--check` and a plain start never pay for loading zstandard.
    from .config import Corpus
    from .dictionary import DictionaryTrainer

DEFAULT_CONFIG_PATH = Path("config.yaml")


def main() -> int:
    args = _parse_args()

    # **Before the config is loaded, deliberately.** Reading day folders back needs the folders and
    # nothing else, which is the self-containment rule these two exist to demonstrate: `tar` a day,
    # unpack it on a machine that has no `config.yaml`, and point this at it. `init` is here for the
    # opposite reason and it is the stronger one: it exists to *create* the config, so requiring one
    # would make it useless in the only directory anybody runs it in.
    if args.command == "init":
        return _init(args.config)
    if args.command == "verify-archive":
        return _verify_archive(args.days)
    if args.command == "extract":
        return _extract(args)

    # **`.env` is read from beside the config file, not from wherever python-dotenv guesses.**
    # `load_dotenv()` with no argument walks from *this file* upward to the filesystem root, so an
    # installed router searched uv's tool directory and `$HOME` and never looked at the working
    # directory at all. In a checkout it happened to work, because walking up from
    # `src/ilirium_llm_router/` reaches the repository root on the third step -- which is why five
    # phases never noticed. Phase 12 measured it: a `.env` in the working directory was invisible
    # while the error told the user to "set it in your .env file".
    #
    # Beside the config rather than in the working directory, so that `-c /elsewhere/config.yaml`
    # picks up `/elsewhere/.env` -- the same rule `config.py` already uses for log, stats and corpus
    # paths. With the default `./config.yaml` the two are the same directory.
    load_dotenv(args.config.parent / ".env")

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    _report(config, args.config)

    if args.command == "check":
        print("\nConfiguration is valid.")
        return 0

    if args.command in ("train-dict", "tune-dict"):
        return _train_dict(config, args)

    # **Bare and `serve` are the same path, not two.** `args.command` is `None` when no subcommand
    # was given, and everything below already reads as "the server unless something returned
    # first", so the default needs no branch of its own.

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


def _config_flag(parser: argparse.ArgumentParser, *, top_level: bool) -> None:
    """Add `-c/--config` to one parser.

    **The subcommand copy uses `SUPPRESS`, and that is not a style choice.** A subparser option with
    an ordinary default *overwrites* the top-level value after parsing, so `-c other.yaml serve`
    would silently fall back to `config.yaml` — the flag accepted, ignored, and no error. With
    `SUPPRESS` the attribute is only set when the option actually appears, so both spellings work
    and neither shadows the other. Tested in task 10 rather than trusted.
    """
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH if top_level else argparse.SUPPRESS,
        help=f"path to the YAML config file (default: {DEFAULT_CONFIG_PATH})",
    )


def _retrain_flags(parser: argparse.ArgumentParser) -> None:
    """The four overrides and `--from`, shared by `train-dict` and `tune-dict`.

    **The four mirror the `retrain` config keys one-for-one**, which is the rule rather than a
    preference: it makes "the flag wins over the key for this run" a mapping a reader can see
    instead of a table they have to learn. It is why `--k` keeps its one-letter spelling.
    """
    parser.add_argument("--window-days", type=int, help="override corpus.retrain.window_days")
    parser.add_argument(
        "--sample-min-bytes", type=int, help="override corpus.retrain.sample_min_bytes"
    )
    parser.add_argument("--maxdict", type=int, help="override corpus.retrain.maxdict")
    parser.add_argument("--k", type=int, help="override corpus.retrain.k")
    parser.add_argument(
        "--from",
        dest="source",
        type=Path,
        metavar="DIR",
        help="train from a directory that is not a corpus, each subdirectory counting as one "
        "session; the lock, retrain.log and the install still use corpus.dir",
    )


def _days_argument(parser: argparse.ArgumentParser) -> None:
    """`DAY...`, positional and repeatable — position 7, the owner's.

    **A required *option* was the wrong shape and is struck.** Days are positional, so the shell's
    own glob covers "all of it" — `verify-archive logs/corpus/2026-*/` — and no `--all` flag or
    corpus-root concept is needed. Repeatable because **a session spans day folders**: finding 5
    measured one session with calls on two consecutive days.
    """
    parser.add_argument(
        "days",
        nargs="+",
        type=Path,
        metavar="DAY",
        help="one or more corpus day folders; the shell's glob is the 'all of it' case",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ilirium-llm-router",
        description="Route Claude Code to Anthropic and to locally served models at the same time.",
    )
    _config_flag(parser, top_level=True)

    # **`--version` is an argparse action, so it prints and exits during parsing** -- before the
    # config is looked for, before `.env` is read, before any subcommand dispatch. That is the whole
    # point: "did the install work?" is the first question a reader asks, and it has to be
    # answerable in a directory that holds nothing. There was no such invocation until Phase 12; the
    # only version output ran *after* `load_config` succeeded, so on a fresh machine nothing printed
    # a version and exited 0.
    parser.add_argument(
        "--version",
        action="version",
        version=f"ilirium-llm-router {__version__}",
        help="print the version and exit",
    )

    # `dest="command"` leaves `None` for the bare invocation, which `main` reads as "serve". The
    # subparsers are deliberately **not** `required=True`: bare must keep working.
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    serve = commands.add_parser(
        "serve",
        help="start the server (the same thing a bare invocation does)",
        description="Start the router. This is what a bare `ilirium-llm-router` does.",
    )
    _config_flag(serve, top_level=False)

    init = commands.add_parser(
        "init",
        help="write a starter config.yaml into the current directory, and exit",
        description="Write a starter config.yaml into the current directory. Refuses if one is "
        "already there.",
    )
    _config_flag(init, top_level=False)

    check = commands.add_parser(
        "check",
        help="validate the configuration, report it, and exit without starting the server",
    )
    _config_flag(check, top_level=False)

    train = commands.add_parser(
        "train-dict",
        help="train a dictionary now and install it if it beats the one in use; works even when "
        "automatic retraining is off, and does not start the server",
    )
    _config_flag(train, top_level=False)
    _retrain_flags(train)

    tune = commands.add_parser(
        "tune-dict",
        help="sweep maxdict x k and print the whole surface; never installs anything",
    )
    _config_flag(tune, top_level=False)
    _retrain_flags(tune)

    extract = commands.add_parser(
        "extract",
        help="read bodies out of one or more day folders, with selection, into files",
        description="Select calls out of a corpus and write them where a person can read them.",
    )
    _days_argument(extract)
    # **`--out` and `--format` are both required — position 8, the owner's.** A run always states
    # what it produces. `--format` is a *selector*, not a mode flag: the plan proposed `--to-jsonl`
    # and the owner replaced it, because a boolean mode with a companion option that is meaningless
    # without it is the exact defect subcommands were adopted to fix, one level down.
    extract.add_argument("--out", type=Path, required=True, metavar="DIR",
                         help="output root; `bodies/` and `projects/` are written under it")
    extract.add_argument("--format", dest="formats", action="append", required=True,
                         choices=("bodies", "jsonl"),
                         help="what to write; repeatable, so both can be asked for at once")
    extract.add_argument("--session", dest="sessions", action="append", default=[], metavar="ID",
                         help="only this session; repeatable, and repeats are OR'd")
    extract.add_argument("--model", dest="models", action="append", default=[], metavar="NAME",
                         help="only this model; repeatable, and repeats are OR'd")
    extract.add_argument("--agent", dest="agents", action="append", default=[], metavar="ID",
                         help="only this subagent; repeatable, and repeats are OR'd")
    extract.add_argument("--path", metavar="PATH",
                         help="only this request path, matched exactly — so `/v1/messages` does "
                              "not sweep in `/v1/messages/count_tokens`")
    # **`default=None`, not "corpus".** The default is applied downstream, so that *"was it given?"*
    # stays answerable here — which is what makes the error below possible at all.
    extract.add_argument("--project-name", metavar="NAME",
                         help="the folder under `projects/` (default: corpus); requires "
                              "--format jsonl")

    verify = commands.add_parser(
        "verify-archive",
        help="read every body back out of one or more day folders, verify each against the digest "
        "in its own filename, and report; writes nothing",
    )
    _days_argument(verify)

    args = parser.parse_args()

    # **A parse error, not a silent no-op.** `--project-name` scopes a *format*, and passing it
    # without that format is a mistake the user wants told about — argparse cannot express the
    # dependency, so it is checked here and reported through the subparser so the usage line is
    # `extract`'s rather than the program's.
    if args.command == "extract" and args.project_name is not None and "jsonl" not in args.formats:
        extract.error("--project-name is meaningless without --format jsonl")
    return args


CONFIG_TEMPLATE = "config-template.yaml"
"""The starter config shipped inside the wheel, written by `init`.

**A data file in the package, not a string in a module.** It is `config.yaml` byte for byte, and a
test pins that -- so the file a new user starts from cannot drift away from the one this repository
runs. A Python string holding YAML would ship just as reliably and would have to be kept in step by
hand, which is the second copy this project's documentation rules exist to prevent.
"""


def _init(path: Path) -> int:
    """Write a starter config next to where the router would look for one.

    **It refuses rather than overwriting, and there is no `--force`** -- owner's decision on
    2026-09-02, when the option was offered. A config is the one file in a working directory that
    may hold hours of somebody's tuning; `rm config.yaml` is not a hardship, an accidental
    `--force` is.

    **The path comes from `-c`, so `init -c other.yaml` writes `other.yaml`.** Not a feature
    invented here: `-c` already names the file every other command reads, and having `init` write
    somewhere else would make the flag mean two things.
    """
    if path.exists():
        print(f"error: {path} already exists; refusing to overwrite it", file=sys.stderr)
        return 1

    from importlib import resources

    template = resources.files(__package__).joinpath(CONFIG_TEMPLATE).read_text(encoding="utf-8")
    try:
        path.write_text(template, encoding="utf-8")
    except OSError as exc:  # a missing parent directory, or a read-only one
        print(f"error: could not write {path}: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote {path}")
    print("Edit it, then run `ilirium-llm-router check` to validate it.")
    return 0


def _verify_archive(days: list[Path]) -> int:
    """Read day folders back and say whether all of them open.

    **This is `--extract`'s read-and-check half, now its own command** — position 9, the owner's.
    The plan had carried a `--verify-only` flag on `extract`; that flag **named the default**, since
    an `extract` with no output destination cannot do anything else, and two spellings for one
    behaviour is what the register exists to catch.

    It reads the day folders it is given and **nothing above them**, so it is the self-containment
    rule made executable: `tar` a day, unpack it elsewhere, point this at it.

    **Every day is attempted even after one fails.** A run that stopped at the first bad folder
    would report the first problem and hide the rest, and the question this answers is *"does all of
    it open?"* rather than *"is there a problem?"*.
    """
    from .corpus import CorpusError, CorpusReader

    grand_total = grand_failed = grand_plaintext = grand_compressed = 0
    missing = False

    for day in days:
        print(f"=== {day}")
        if not day.is_dir():
            print(f"error: {day} is not a directory", file=sys.stderr)
            missing = True
            continue

        reader = CorpusReader(day)
        directions = reader.directions()
        if not directions:
            print(f"error: {day} holds no requests/ or responses/ folder", file=sys.stderr)
            missing = True
            continue

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
        dictionaries = sorted(path.name for path in (day / "dicts").glob("*.dict"))
        print(f"dictionaries: {', '.join(dictionaries) if dictionaries else 'none'}")
        print(f"{total} blob(s), {failed} failed")
        if total and not failed:
            print(f"{plaintext} → {compressed} bytes, {plaintext / compressed:.3f}x")
            print("every blob verified against the digest in its own filename")

        grand_total += total
        grand_failed += failed
        grand_plaintext += plaintext
        grand_compressed += compressed

    # **Only when there is more than one day**, so a single-day run prints exactly what it always
    # did and the two forms do not have to be read differently.
    if len(days) > 1:
        print(f"\n=== {len(days)} day folder(s)")
        print(f"{grand_total} blob(s), {grand_failed} failed")
        if grand_total and not grand_failed:
            ratio = grand_plaintext / grand_compressed
            print(f"{grand_plaintext} → {grand_compressed} bytes, {ratio:.3f}x")

    return 1 if (grand_failed or missing) else 0


def _extract(args: argparse.Namespace) -> int:
    """Selection over the index, output as files a person can open.

    **The flag surface is complete and the behaviour is not** — Phase 11 builds it in Group D,
    tasks 16 to 18, on top of the converter Group C writes. This exists now because task 9 is where
    the CLI is settled and task 10 tests that surface: `--out` and `--format` required,
    `--project-name` a parse error without `--format jsonl`.

    **The missing-day check runs before anything is written.** A run that wrote three files and
    then failed would leave a directory whose good files cannot be told from its abandoned ones,
    and the whole point of that error is that a half-converted transcript reads as a whole one.
    """
    from datetime import UTC, datetime

    from . import __version__
    from .corpus import CorpusReader
    from .extract import (
        ExtractError,
        Selection,
        check_days,
        read_index,
        select,
        write_bodies,
        write_jsonl,
    )

    readers: dict[Path, CorpusReader] = {}

    def read(day: Path, blob: Path) -> bytes:
        """One reader per day folder, because each carries its own `dicts/`."""
        if day not in readers:
            readers[day] = CorpusReader(day)
        return readers[day].read(blob)

    selection = Selection(
        sessions=tuple(args.sessions),
        models=tuple(args.models),
        agents=tuple(args.agents),
        path=args.path,
    )

    try:
        rows = [row for day in args.days for row in read_index(day)]
    except ExtractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    chosen = select(rows, selection)
    print(f"{len(rows)} row(s) read, {len(chosen)} selected")
    if not chosen:
        print("nothing selected — no files written", file=sys.stderr)
        return 1

    if "jsonl" in args.formats:
        short = check_days(args.days, chosen)
        if short:
            print("error: a selected session has calls in a day folder that was not passed.",
                  file=sys.stderr)
            for session, missing in sorted(short.items()):
                print(f"  {session} also has calls in {', '.join(missing)}", file=sys.stderr)
            print("Reconstructing without them would date part of the transcript wrongly with "
                  "nothing in the file to say so. Pass those folders as well.", file=sys.stderr)
            return 1

    written = []
    if "bodies" in args.formats:
        result = write_bodies(chosen, args.out, read)
        written.append(f"{result.bodies} body file(s)")
        if result.no_request_blob or result.no_response_blob:
            print(f"  {result.no_request_blob} row(s) had no stored request body and "
                  f"{result.no_response_blob} had no response; no file was written for those")
    if "jsonl" in args.formats:
        generated = datetime.now(UTC).isoformat(timespec="seconds")
        result = write_jsonl(
            chosen,
            args.out,
            project=args.project_name or "corpus",
            days=[Path(day).name for day in args.days],
            read=read,
            version=__version__,
            generated=generated,
        )
        written.append(f"{result.files} conversation file(s)")

    print(f"wrote {', '.join(written)} under {args.out}")
    return 0


def _train_dict(config: Config, args: argparse.Namespace) -> int:
    """`--train-dict` and `--tune-dict`: train by hand, from the terminal.

    **It works whether or not `corpus.enabled` is true, and whether or not automatic retraining is
    on.** Owner's decision, 2026-08-20: typing the command is explicit consent, which is the same
    reasoning that lets it bypass the once-a-day guard. The named cost is that a machine which never
    turned capture on can still end up with `<dir>/dicts/` and a `retrain.log` — but only because
    somebody asked for one.

    **It does not bypass the margin.** A hand-run cannot install a dictionary that loses to the one
    already in use; consent to retrain is not consent to make the corpus worse.
    """
    from .dictionary import DictionaryTrainer

    try:
        corpus = _with_overrides(config.corpus, args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.source is not None and not args.source.is_dir():
        print(f"error: {args.source} is not a directory", file=sys.stderr)
        return 1

    # Logging goes to the router's own file, because a training run is a real operation and the log
    # is where the router's operations are recorded. `--check` deliberately does not do this; this
    # is not a validation, it writes.
    try:
        setup_logging(config.logging)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    trainer = DictionaryTrainer(corpus)
    print()
    if args.command == "tune-dict":
        return _tune(trainer, args)

    verdict = trainer.run(
        bypass_guard=True, window_days=corpus.retrain.window_days, source=args.source
    )
    if verdict is None:
        print("Trained nothing. The reason is in the log and in the retrain log:")
        print(f"  {trainer.retrain_log}")
        return 1

    print(f"Candidate:  {verdict.candidate_ratio:.3f}x on the held-out slice")
    if verdict.incumbent_ratio is None:
        print("Incumbent:  none — any candidate that trains is installed")
    else:
        print(f"Incumbent:  {verdict.incumbent_ratio:.3f}x")
        print(f"Difference: {verdict.improvement:+.2%} (must exceed {_margin():.0%} to install)")
    print(f"Scored at:  zstd level {verdict.score_level}")
    print(f"\n{'INSTALLED' if verdict.installed else 'REFUSED'}: {verdict.reason}")
    if verdict.installed:
        print("A running router picks it up on its next rescan; nothing needs restarting.")
    return 0


def _tune(trainer: DictionaryTrainer, args: argparse.Namespace) -> int:
    """Sweep the grid and print **the whole surface**, never a winner.

    Training is non-monotonic in both axes, measured on both trainers — so the best cell here is a
    property of this corpus and this slice rather than a recommendation, and a tool that printed one
    number would invite exactly the reading the measurement refuses.
    """
    from .dictionary import TUNE_K, TUNE_MAXDICT

    if args.source is not None:
        training, holdout = trainer.external_split(args.source)
    else:
        days = trainer.window(window_days=args.window_days)
        training, holdout = trainer.split(days)
    if not training or not holdout:
        print("Not enough material to sweep. See the log for what was found.", file=sys.stderr)
        return 1

    maxdicts = (args.maxdict,) if args.maxdict else TUNE_MAXDICT
    ks = (args.k,) if args.k else TUNE_K
    print(f"Sweeping {len(maxdicts)} x {len(ks)} on {len(training)} training "
          f"({len(set(training))} distinct) and {len(holdout)} held-out sample(s).\n")

    undicted = trainer.score(None, holdout)
    plaintext = sum(len(sample) for sample in holdout)
    print(f"{'maxdict':>10}  {'k':>7}  {'dict bytes':>11}  {'ratio':>8}")
    print(f"{'-' * 10}  {'-' * 7}  {'-' * 11}  {'-' * 8}")
    print(f"{'(none)':>10}  {'':>7}  {'':>11}  {plaintext / undicted:>7.3f}x")
    surface = trainer.tune(training, holdout, maxdicts=maxdicts, ks=ks)
    for maxdict, k, size, _scored, ratio in surface:
        print(f"{maxdict:>10,}  {k:>7,}  {size:>11,}  {ratio:>7.3f}x")

    print("\nPROVISIONAL. Training is non-monotonic in both axes, so the best cell above is a")
    print("property of this corpus and this held-out slice, not a recommended setting. Nothing")
    print("was installed.")
    return 0


def _with_overrides(corpus: Corpus, args: argparse.Namespace) -> Corpus:
    """Apply the four CLI flags over the config block, **revalidating** as it goes.

    `model_copy(update=)` would skip validation, so `--maxdict 0` would sail past the `gt=0` the
    config model declares and fail much later inside libzstd. Rebuilding through `model_validate`
    keeps one set of bounds for the key and its flag.
    """
    from .config import Corpus

    overrides = {
        "window_days": args.window_days,
        "sample_min_bytes": args.sample_min_bytes,
        "maxdict": args.maxdict,
        "k": args.k,
    }
    given = {key: value for key, value in overrides.items() if value is not None}
    if not given:
        return corpus
    # **One validation, not two.** `Corpus.model_validate` revalidates the nested `retrain` block
    # as it rebuilds, so a separate `Retrain.model_validate` first was dead code -- confirmed by
    # mutation: replacing it with an unvalidated `model_copy` changed nothing.
    return Corpus.model_validate(
        {**corpus.model_dump(), "retrain": {**corpus.retrain.model_dump(), **given}}
    )


def _margin() -> float:
    from .dictionary import INSTALL_MARGIN

    return INSTALL_MARGIN


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
