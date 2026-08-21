"""Phase 0 promises that a bad config stops the program with a readable message.

These tests check that promise: each failure mode raises ConfigError carrying something a person can
act on, rather than a traceback or a silently applied default.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from ilirium_llm_router.config import ConfigError, load_config

MINIMAL = """
backends:
  anthropic:
    base_url: https://api.anthropic.com
    credential: forward
  lmstudio:
    base_url: http://localhost:1234
    credential: strip
"""


def write(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "config.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_minimal_config_loads_with_defaults(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL))

    assert config.backends.anthropic.base_url == "https://api.anthropic.com"
    assert config.backends.lmstudio.credential == "strip"
    assert config.server.port == 8787
    assert config.logging.level == "INFO"


def test_relative_paths_resolve_against_the_config_file(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL))

    assert config.logging.file == tmp_path / "logs/telemetry/router.log"
    assert config.stats.file == tmp_path / "logs/telemetry/calls.csv"


def test_absolute_paths_are_left_alone(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL + "\nstats:\n  file: /var/log/calls.csv\n"))

    assert config.stats.file == Path("/var/log/calls.csv")


def test_trailing_slash_is_trimmed_from_base_url(tmp_path: Path) -> None:
    text = MINIMAL.replace("http://localhost:1234", "http://localhost:1234/")
    config = load_config(write(tmp_path, text))

    assert config.backends.lmstudio.base_url == "http://localhost:1234"


def test_missing_file_is_reported_by_name(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "absent.yaml")


def test_empty_file_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="empty"):
        load_config(write(tmp_path, ""))


def test_malformed_yaml_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not valid YAML"):
        load_config(write(tmp_path, "backends: [unclosed\n"))


def test_missing_backend_is_named_in_the_message(tmp_path: Path) -> None:
    text = """
backends:
  anthropic:
    base_url: https://api.anthropic.com
    credential: forward
"""
    with pytest.raises(ConfigError, match="backends.lmstudio"):
        load_config(write(tmp_path, text))


def test_unknown_key_is_an_error_rather_than_ignored(tmp_path: Path) -> None:
    """A typo must not leave the default quietly in place."""
    with pytest.raises(ConfigError, match="prot"):
        load_config(write(tmp_path, MINIMAL + "\nlogging:\n  prot: 9\n"))


def test_base_url_without_a_scheme_is_rejected(tmp_path: Path) -> None:
    text = MINIMAL.replace("http://localhost:1234", "localhost:1234")
    with pytest.raises(ConfigError, match="http://"):
        load_config(write(tmp_path, text))


def test_bad_credential_mode_is_rejected(tmp_path: Path) -> None:
    text = MINIMAL.replace("credential: strip", "credential: inherit")
    with pytest.raises(ConfigError, match="credential"):
        load_config(write(tmp_path, text))


INJECT = MINIMAL.replace("credential: strip", "credential: inject") + (
    "    api_key_env: LMSTUDIO_API_KEY\n"
)


def test_inject_without_a_named_variable_is_rejected(tmp_path: Path) -> None:
    """A backend that authenticates with nothing, which otherwise shows up as a 401 much later."""
    text = MINIMAL.replace("credential: strip", "credential: inject")

    with pytest.raises(ConfigError, match="api_key_env"):
        load_config(write(tmp_path, text))


def test_a_key_that_would_never_be_sent_is_rejected(tmp_path: Path) -> None:
    """The old shape read this as `strip` and ignored the key. Now it is a startup error."""
    text = MINIMAL + "    api_key_env: LMSTUDIO_API_KEY\n"

    with pytest.raises(ConfigError, match="never be sent"):
        load_config(write(tmp_path, text))


def test_the_rejection_says_how_to_fix_it(tmp_path: Path) -> None:
    """Every config message names the fix; these two are no exception."""
    text = MINIMAL + "    api_key_env: LMSTUDIO_API_KEY\n"

    with pytest.raises(ConfigError, match="credential: inject"):
        load_config(write(tmp_path, text))


def test_missing_api_key_env_var_fails_at_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Naming an unset variable is a config mistake, and must surface now, not on first request."""
    monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="LMSTUDIO_API_KEY"):
        load_config(write(tmp_path, INJECT))


def test_present_api_key_env_var_is_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")

    config = load_config(write(tmp_path, INJECT))

    assert config.backends.lmstudio.credential == "inject"
    assert config.api_keys() == {"lmstudio": "local-key"}


def test_read_timeout_defaults_to_the_old_shared_number(tmp_path: Path) -> None:
    """A config written before the field existed keeps behaving exactly as it did."""
    config = load_config(write(tmp_path, MINIMAL))

    assert config.backends.anthropic.read_timeout == 600.0
    assert config.backends.lmstudio.read_timeout == 600.0


def test_read_timeout_is_set_per_backend(tmp_path: Path) -> None:
    """The whole point: the local backend needs minutes of silence, the cloud one never has."""
    text = MINIMAL + "    read_timeout: 1800\n"

    config = load_config(write(tmp_path, text))

    assert config.backends.lmstudio.read_timeout == 1800.0
    assert config.backends.anthropic.read_timeout == 600.0


def test_a_non_positive_read_timeout_is_rejected(tmp_path: Path) -> None:
    text = MINIMAL + "    read_timeout: 0\n"

    with pytest.raises(ConfigError, match="read_timeout"):
        load_config(write(tmp_path, text))


def test_a_forwarding_backend_contributes_no_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`api_keys()` is keyed on the mode, so the two backends here contribute nothing."""
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")

    config = load_config(write(tmp_path, MINIMAL))

    assert config.api_keys() == {}


# --- the corpus block, Task 11 ------------------------------------------------------------------
#
# The store is opt-in, so the defaults matter more than usual: a machine that never turns it on
# still parses this block, and every wrong value has to be a refusal rather than a silent default.


def test_the_corpus_is_off_by_default_with_no_block_at_all(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL))

    assert config.corpus.enabled is False
    assert config.corpus.compress_level_zstd == 9
    assert config.corpus.body_max_bytes == 1_048_576
    assert config.corpus.queue_max_bytes == 67_108_864


def test_the_retrain_block_defaults_without_being_named(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL))

    assert config.corpus.retrain.window_days == 1
    assert config.corpus.retrain.sample_min_bytes == 1024
    assert config.corpus.retrain.maxdict == 262_144
    assert config.corpus.retrain.k == 8000


def test_the_corpus_dir_resolves_against_the_config_file(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL))

    assert config.corpus.dir == tmp_path / "logs/corpus"


def test_an_absolute_corpus_dir_is_left_alone(tmp_path: Path) -> None:
    config = load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  dir: /var/corpus\n"))

    assert config.corpus.dir == Path("/var/corpus")


def test_an_unknown_key_under_corpus_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError) as caught:
        load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  enable: true\n"))

    assert "enable" in str(caught.value)


def test_an_unknown_key_under_retrain_is_rejected(tmp_path: Path) -> None:
    """`extra="forbid"` has to be on the nested model too, or the whole block accepts typos."""
    with pytest.raises(ConfigError) as caught:
        load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  retrain:\n    windowdays: 2\n"))

    assert "windowdays" in str(caught.value)


def test_a_non_boolean_enabled_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  enabled: sometimes\n"))


@pytest.mark.parametrize("level", [0, -1, 23, 100])
def test_a_compression_level_outside_1_to_22_is_rejected(tmp_path: Path, level: int) -> None:
    """1-19 are the ordinary levels and 20-22 the ultra ones. Hardcoded rather than read from
    libzstd: this is a sanity check against a typo, not a contract with the library."""
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, MINIMAL + f"\ncorpus:\n  compress_level_zstd: {level}\n"))


@pytest.mark.parametrize("level", [1, 9, 19, 22])
def test_the_ordinary_and_ultra_levels_are_accepted(tmp_path: Path, level: int) -> None:
    config = load_config(write(tmp_path, MINIMAL + f"\ncorpus:\n  compress_level_zstd: {level}\n"))

    assert config.corpus.compress_level_zstd == level


@pytest.mark.parametrize("key", ["body_max_bytes", "queue_max_bytes"])
@pytest.mark.parametrize("value", [0, -1])
def test_neither_limit_can_be_disabled(tmp_path: Path, key: str, value: int) -> None:
    """An "unlimited" setting reads as *capture everything* and means *let an unknown endpoint
    decide how much memory this process uses*."""
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, MINIMAL + f"\ncorpus:\n  {key}: {value}\n"))


def test_window_days_zero_is_accepted_because_it_is_the_off_switch(tmp_path: Path) -> None:
    """The one value in the block that must be *accepted* rather than refused: it is how automatic
    retraining is switched off, and a separate `enabled` boolean would be redundant beside it."""
    config = load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  retrain:\n    window_days: 0\n"))

    assert config.corpus.retrain.window_days == 0


def test_a_negative_window_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, MINIMAL + "\ncorpus:\n  retrain:\n    window_days: -1\n"))


@pytest.mark.parametrize("key,value", [("sample_min_bytes", 0), ("maxdict", 0), ("k", 0)])
def test_the_training_parameters_refuse_zero(tmp_path: Path, key: str, value: int) -> None:
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, MINIMAL + f"\ncorpus:\n  retrain:\n    {key}: {value}\n"))


def test_the_shipped_config_file_carries_every_corpus_key(tmp_path: Path) -> None:
    """The block in `config.yaml` is documentation as much as configuration, so a key added to the
    model and not to the file would ship undocumented."""
    shipped = Path(__file__).resolve().parents[1] / "config.yaml"
    text = shipped.read_text(encoding="utf-8")

    for key in ("enabled", "dir", "compress_level_zstd", "body_max_bytes", "queue_max_bytes"):
        assert f"  {key}:" in text
    for key in ("window_days", "sample_min_bytes", "maxdict", "k"):
        assert f"    {key}:" in text
