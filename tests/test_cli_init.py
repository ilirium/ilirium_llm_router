"""`init`, `--version`, and where `.env` is read from — Phase 12 task 10.

**Three of these pin defects rather than features.** `--version` did not exist, `.env` was read from
a directory nobody chose, and `init` had to be placed so that it runs *without* a config — the
command that creates one would otherwise have required one. All three were found by driving an
installed tool, not by the suite, which is why the suite gains them here.

**The load-bearing test is `test_written_config_passes_check_unmodified`.** An `init` that writes a
file the router then rejects is worse than no `init` at all, and nothing else in this file would
catch it.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from ilirium_llm_router import __version__
from ilirium_llm_router.cli import CONFIG_TEMPLATE, _init, main
from ilirium_llm_router.config import load_config

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(*argv: str) -> int:
    """Run `main()` over an argv, with no `sys.argv` leaking in from pytest."""
    original = sys.argv
    sys.argv = ["ilirium-llm-router", *argv]
    try:
        return main()
    finally:
        sys.argv = original


def test_init_writes_a_config_into_an_empty_directory(tmp_path: Path) -> None:
    target = tmp_path / "config.yaml"
    assert _init(target) == 0
    assert target.exists()


def test_init_refuses_rather_than_overwriting(tmp_path: Path) -> None:
    """**No `--force` exists, so refusal is the only behaviour** — owner's decision, 2026-09-02."""
    target = tmp_path / "config.yaml"
    target.write_text("theirs: not ours\n", encoding="utf-8")

    assert _init(target) == 1
    assert target.read_text(encoding="utf-8") == "theirs: not ours\n", "it overwrote the file"


def test_written_config_passes_check_unmodified(tmp_path: Path) -> None:
    """The one that matters: `init` then `check`, with no editing in between.

    A starter config the router rejects would send every new user to the same error before they had
    done anything wrong.
    """
    target = tmp_path / "config.yaml"
    assert _init(target) == 0

    config = load_config(target)  # raises ConfigError if the template has drifted out of validity
    assert config.backends, "the starter config declares no backends"


def test_template_matches_the_repository_config(tmp_path: Path) -> None:
    """The shipped starter and the config this repository runs are the same bytes.

    **This is the only thing stopping the two drifting.** The template is a data file inside the
    package precisely so it can be compared; without this test a change to `config.yaml` would
    leave new users starting from a stale copy, silently and for as long as nobody looked.
    """
    shipped = (REPO_ROOT / "src" / "ilirium_llm_router" / CONFIG_TEMPLATE).read_bytes()
    ours = (REPO_ROOT / "config.yaml").read_bytes()
    assert shipped == ours


def test_init_needs_no_config_to_exist(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`init` must return before `load_config`, or it fails in the only directory it is used in.

    Every command except `extract` and `verify-archive` reaches `load_config`. An `init` added as an
    ordinary subcommand would report `Config file not found: config.yaml` in an empty directory —
    which is exactly where somebody runs it.
    """
    monkeypatch.chdir(tmp_path)
    assert run("init") == 0
    assert (tmp_path / "config.yaml").exists()


def test_version_prints_and_exits_zero_with_no_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """`--version` is an argparse action, so it answers before anything can fail.

    "Did the install work?" has to be answerable in a directory holding nothing. Until Phase 12 it
    was not: the only version output ran after `load_config` succeeded.
    """
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exit_info:
        run("--version")
    assert exit_info.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_dotenv_is_read_from_beside_the_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The defect this phase measured: `.env` was searched for from the *package*, not from here.

    `load_dotenv()` with no argument walks up from `cli.py`, which in a checkout happens to reach
    the repository root and in an installed tool reaches `$HOME`. A `.env` in the working directory
    was invisible while the error told the user to set the variable in it.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("PHASE12_PROBE", raising=False)
    assert run("init") == 0

    config = (tmp_path / "config.yaml").read_text(encoding="utf-8")
    config = config.replace(
        "    credential: strip",
        "    credential: inject\n    api_key_env: PHASE12_PROBE",
        1,
    )
    (tmp_path / "config.yaml").write_text(config, encoding="utf-8")
    (tmp_path / ".env").write_text("PHASE12_PROBE=probe-value\n", encoding="utf-8")

    assert run("check") == 0, "the .env beside the config was not read"
