"""The command line surface — Phase 11 task 10.

**The CLI had no test file at all before this one.** It was reached only sideways: two tests in
`test_dictionary.py` import `_with_overrides`, and one in `test_corpus.py` shells out. So the
surface this phase restructured had never been described anywhere a change would break.

**These are parser tests, deliberately.** They assert what argparse *resolves*, not what the
commands do — `verify-archive`'s behaviour is covered end-to-end in `test_corpus.py`, and
`extract`'s is Group D's. What is worth pinning here is the shape the owner settled: bare still
serves, `--out` and `--format` are required, and a flag that cannot work is an error rather than
a no-op.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ilirium_llm_router.cli import _parse_args


def parse(*argv: str):
    """Run the real parser over an argv, with no `sys.argv` leaking in from pytest."""
    original = sys.argv
    sys.argv = ["ilirium-llm-router", *argv]
    try:
        return _parse_args()
    finally:
        sys.argv = original


def rejected(*argv: str) -> int:
    """The exit code argparse chose. Anything that parses is a failure of the test's premise."""
    with pytest.raises(SystemExit) as exit_info:
        parse(*argv)
    assert isinstance(exit_info.value.code, int)
    return exit_info.value.code


# --- bare invocation still serves ---------------------------------------------------------------


def test_a_bare_invocation_resolves_to_serve() -> None:
    """`make run` depends on it, so does habit, and Phase 12 makes the bare form the one people
    type. `command` is `None` and `main` reads `None` and `serve` as one path."""
    assert parse().command is None


def test_serve_is_the_explicit_spelling_of_the_same_thing() -> None:
    assert parse("serve").command == "serve"


def test_an_unknown_subcommand_is_rejected() -> None:
    assert rejected("srve") == 2


# --- the config flag, which is where a subparser silently shadows its parent --------------------


def test_the_config_flag_wins_from_either_side_of_the_subcommand() -> None:
    """**The regression this file exists for.** A subparser option with an ordinary default
    *overwrites* the parent's value after parsing, so `-c other.yaml serve` would have loaded
    `config.yaml` — the flag accepted, ignored, and no error raised. `argparse.SUPPRESS` sets the
    attribute only when the option actually appears.

    Both orders are asserted because only the first one fails without `SUPPRESS`, and a test that
    checked the second alone would have passed against the defect.
    """
    assert parse("-c", "other.yaml", "serve").config == Path("other.yaml")
    assert parse("serve", "-c", "other.yaml").config == Path("other.yaml")


def test_the_config_flag_falls_back_to_the_default() -> None:
    assert parse("serve").config == Path("config.yaml")
    assert parse().config == Path("config.yaml")


# --- the flags this phase deleted ----------------------------------------------------------------


@pytest.mark.parametrize("flag", ["--check", "--extract", "--train-dict", "--tune-dict"])
def test_the_old_flags_are_gone_rather_than_aliased(flag: str) -> None:
    """Removed, not aliased. They had one user, on one machine, and Phase 12 is where the spelling
    becomes a promise to strangers — renaming after the installer ships is the expensive version."""
    assert rejected(flag) == 2


@pytest.mark.parametrize("command", ["check", "train-dict", "tune-dict"])
def test_each_old_flag_has_a_subcommand(command: str) -> None:
    assert parse(command).command == command


# --- extract's surface ---------------------------------------------------------------------------


def test_out_and_format_are_both_required() -> None:
    """Position 8, the owner's: a run always states what it produces."""
    assert rejected("extract", "2026-08-25") == 2
    assert rejected("extract", "2026-08-25", "--out", "dump") == 2
    assert rejected("extract", "2026-08-25", "--format", "bodies") == 2


def test_format_is_a_selector_and_repeats() -> None:
    """Not a mode flag. `--to-jsonl` was proposed twice and replaced by the owner, because a boolean
    mode whose companion option is meaningless without it is the defect subcommands were adopted to
    fix, one level down."""
    args = parse(
        "extract", "2026-08-25", "--out", "dump", "--format", "bodies", "--format", "jsonl"
    )
    assert args.formats == ["bodies", "jsonl"]


def test_an_unknown_format_is_rejected() -> None:
    assert rejected("extract", "2026-08-25", "--out", "dump", "--format", "sse") == 2


def test_project_name_without_jsonl_is_an_error_not_a_silent_no_op() -> None:
    """argparse cannot express the dependency, so it is checked by hand — and it is checked because
    a flag that is accepted and then ignored is the failure mode this phase is about."""
    assert rejected(
        "extract", "2026-08-25", "--out", "dump", "--format", "bodies", "--project-name", "mine"
    ) == 2


def test_project_name_is_accepted_with_jsonl() -> None:
    args = parse(
        "extract", "2026-08-25", "--out", "dump", "--format", "jsonl", "--project-name", "mine"
    )
    assert args.project_name == "mine"


def test_project_name_defaults_to_none_rather_than_to_corpus() -> None:
    """**`None`, not `corpus`, and that is load-bearing rather than lazy.** The default is applied
    downstream so that *was it given?* stays answerable here — which is the only thing that makes
    the error above expressible at all."""
    args = parse("extract", "2026-08-25", "--out", "dump", "--format", "jsonl")
    assert args.project_name is None


@pytest.mark.parametrize(
    ("flag", "attribute"),
    [("--session", "sessions"), ("--model", "models"), ("--agent", "agents")],
)
def test_the_selection_filters_repeat_and_default_to_empty(flag: str, attribute: str) -> None:
    """Repeats of one kind are OR'd, so they collect into a list. Empty means "all", which is why
    the default is `[]` and not `None`."""
    base = ["extract", "2026-08-25", "--out", "dump", "--format", "bodies"]
    assert getattr(parse(*base), attribute) == []
    assert getattr(parse(*base, flag, "a", flag, "b"), attribute) == ["a", "b"]


def test_path_takes_one_value_and_is_matched_exactly_downstream() -> None:
    """Position 18. Exact, so `--path /v1/messages` does not sweep in the 66 `count_tokens` rows
    that share its prefix — measured on the frozen slice in `evidence/`."""
    base = ["extract", "2026-08-25", "--out", "dump", "--format", "bodies"]
    assert parse(*base).path is None
    assert parse(*base, "--path", "/v1/messages").path == "/v1/messages"


# --- days are positional and repeatable ----------------------------------------------------------


@pytest.mark.parametrize("command", ["verify-archive", "extract"])
def test_at_least_one_day_is_required(command: str) -> None:
    extra = ["--out", "dump", "--format", "bodies"] if command == "extract" else []
    assert rejected(command, *extra) == 2


def test_days_repeat_because_a_session_spans_them() -> None:
    """Position 7. Finding 5 measured one session with calls on two consecutive days, and the frozen
    slice has it at 276 calls — so a converter given one folder would emit a whole day of prior
    conversation as a single opening turn."""
    args = parse("verify-archive", "2026-08-25", "2026-08-26")
    assert args.days == [Path("2026-08-25"), Path("2026-08-26")]


def test_a_shell_glob_is_the_all_of_it_case() -> None:
    """Which is why there is no `--all` flag and no corpus-root concept: the shell already expands
    `logs/corpus/2026-*/` into exactly this."""
    args = parse("verify-archive", "a/2026-08-24", "a/2026-08-25", "a/2026-08-26")
    assert len(args.days) == 3


def test_verify_archive_takes_no_out_by_construction() -> None:
    """It reads, verifies, and reports. `--verify-only` on `extract` named the default and was
    struck; a destination here would re-open the same confusion from the other side."""
    assert rejected("verify-archive", "2026-08-25", "--out", "dump") == 2


# Phase 14, 2026-09-19. NOT a parser test, which is this file's stated scope -- put here anyway
# because it is the command-line *surface*, and because the thing it guards is that an experiment
# cannot run silently. A reader looking for "what does `check` print" will look here.

def test_check_says_nothing_when_no_experiment_is_on(capsys: pytest.CaptureFixture[str]) -> None:
    """Silence means the router is a plain byte-relay, which is the shipped state."""
    from conftest import make_config

    from ilirium_llm_router.cli import _print_experiments

    _print_experiments(make_config())
    assert capsys.readouterr().out == ""


def test_check_names_every_experiment_that_is_on(capsys: pytest.CaptureFixture[str]) -> None:
    """***The point of the whole block.***

    This phase has twice had an experiment running while a document said it was not. A config key
    nobody prints is a key nobody checks, so `check` says so out loud and names which.
    """
    from conftest import make_config

    from ilirium_llm_router.cli import _print_experiments

    _print_experiments(make_config(relay_accept_encoding=True, imitate_attribution_headers=True))
    out = capsys.readouterr().out
    assert "EXPERIMENTS ON:" in out
    assert "relay_accept_encoding" in out
    assert "imitate_attribution_headers" in out
    assert "http2_upstream" not in out  # off, and not listed
    assert "NOT a plain byte-relay" in out
