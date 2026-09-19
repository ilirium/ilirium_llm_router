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
from ilirium_llm_router.cli import CONFIG_TEMPLATE, ENV_EXAMPLE, ENV_TEMPLATE, _init, main
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


def test_init_writes_both_files_into_an_empty_directory(tmp_path: Path) -> None:
    target = tmp_path / "config.yaml"
    assert _init(target) == 0
    assert target.exists()
    assert (tmp_path / ENV_EXAMPLE).exists(), "the .env.example was not written"


def test_env_example_lands_beside_the_config_not_in_the_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`init -c sub/other.yaml` puts `.env.example` in `sub/`, because that is where `.env` is read.

    The two have to agree. `main()` reads `args.config.parent / ".env"`, so an `.env.example`
    written to the working directory instead would sit where nothing looks for it.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sub").mkdir()

    assert _init(Path("sub/other.yaml")) == 0
    assert (tmp_path / "sub" / ENV_EXAMPLE).exists()
    assert not (tmp_path / ENV_EXAMPLE).exists(), "it landed in the cwd instead"


def test_an_existing_env_example_refuses_the_whole_command(tmp_path: Path) -> None:
    """One existing target refuses both writes, rather than filling in the gap.

    **Deliberate, and the friendlier alternative was considered.** Writing what is missing would
    leave a directory half-populated by two different runs, with nothing saying which file came
    from where. Refusing whole is what "it refuses rather than overwriting" predicts.
    """
    (tmp_path / ENV_EXAMPLE).write_text("theirs\n", encoding="utf-8")
    target = tmp_path / "config.yaml"

    assert _init(target) == 1
    assert not target.exists(), "it wrote the config despite refusing"
    assert (tmp_path / ENV_EXAMPLE).read_text(encoding="utf-8") == "theirs\n"


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


def test_env_template_matches_the_repository_env_example() -> None:
    """Same rule for the second template, and it is the one with a foot-gun.

    `.env.example` cites a path under `docs/`, which an installed user does not have. The wording
    was changed to say "in the project repository" so that a byte-identical copy is honest for both
    readers -- an installed tool telling somebody to open a file they cannot have is the same defect
    as the `.env` error message this phase fixed.
    """
    shipped = (REPO_ROOT / "src" / "ilirium_llm_router" / ENV_TEMPLATE).read_bytes()
    ours = (REPO_ROOT / ENV_EXAMPLE).read_bytes()
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


# Phase 14, 2026-09-19. The experiment configs are CONTROLS, and a control that can quietly stop
# being one is this phase's recurring failure -- four instruments so far that measured something
# other than what they claimed.

@pytest.mark.parametrize("name", ["config.yaml", "config-hosts.yaml", "config-boringssl.yaml"])
def test_every_committed_config_keeps_the_experiments_off(name: str) -> None:
    """***Every config in this repository ships the router as a plain byte-relay.***

    `config-hosts.yaml` is the one that matters most: it exists to answer *"does the safety
    classifier work when the router alters nothing discretionary?"*, and an experiment left on in it
    would answer a different question while looking like an answer to that one.

    Asserted on the loaded config rather than on the file's text, so pinning a key to `false` and
    pinning it by omission are both accepted -- what is being guarded is the behaviour, not the
    spelling.
    """
    config = load_config(REPO_ROOT / name)
    on = [key for key, value in vars(config.experiments).items() if value]
    assert on == [], f"{name} would run the router with {on} on"


def test_the_experiment_configs_pin_the_keys_rather_than_inheriting_them() -> None:
    """The two experiment configs say it out loud, because that is the point of them.

    A default can be changed in one commit and every config that relied on it moves with it,
    silently. These two are controls, so they carry the value rather than inherit it -- and this
    test is what stops the block being dropped as noise later.
    """
    for name in ("config-hosts.yaml", "config-boringssl.yaml"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        assert "experiments:" in text, f"{name} inherits the defaults instead of pinning them"
        for key in ("relay_accept_encoding", "http2_upstream", "imitate_attribution_headers"):
            assert f"{key}: false" in text, f"{name} does not pin {key}"
