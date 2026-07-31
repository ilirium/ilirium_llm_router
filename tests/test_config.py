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
    text = MINIMAL.replace("credential: strip", "credential: inject")
    with pytest.raises(ConfigError, match="credential"):
        load_config(write(tmp_path, text))


def test_missing_api_key_env_var_fails_at_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Naming an unset variable is a config mistake, and must surface now, not on first request."""
    monkeypatch.delenv("LMSTUDIO_API_KEY", raising=False)
    text = MINIMAL + "    api_key_env: LMSTUDIO_API_KEY\n"

    with pytest.raises(ConfigError, match="LMSTUDIO_API_KEY"):
        load_config(write(tmp_path, text))


def test_present_api_key_env_var_is_accepted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LMSTUDIO_API_KEY", "local-key")
    text = MINIMAL + "    api_key_env: LMSTUDIO_API_KEY\n"

    config = load_config(write(tmp_path, text))

    assert config.api_keys() == {"lmstudio": "local-key"}
