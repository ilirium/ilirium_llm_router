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

    assert config.logging.file == tmp_path / "logs/router.log"
    assert config.stats.file == tmp_path / "logs/calls.csv"


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
