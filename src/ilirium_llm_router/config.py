"""Configuration loading and validation.

The config file is validated once at startup. Anything wrong with it stops the program with a
readable message, rather than surfacing as a confusing failure on the first request.

Relative paths in the config are resolved against the directory holding the config file, so the
router behaves the same whichever directory it is started from.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class ConfigError(Exception):
    """Raised when the configuration cannot be loaded or is invalid.

    Carries a message already written for a human reading a terminal.
    """


class Strict(BaseModel):
    """Base for config models: unknown keys are an error, not silently ignored.

    A typo in a YAML key would otherwise leave the default silently in place, which is exactly the
    kind of failure this file exists to prevent.
    """

    model_config = ConfigDict(extra="forbid")


class Backend(Strict):
    """One place requests can be sent."""

    base_url: str
    credential: Literal["forward", "strip"]
    api_key_env: str | None = None

    @field_validator("base_url")
    @classmethod
    def _clean_base_url(cls, value: str) -> str:
        value = value.strip()
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value.rstrip("/")


class Backends(Strict):
    """The two backends, named explicitly because the routing rule names them explicitly."""

    anthropic: Backend
    lmstudio: Backend


class Server(Strict):
    host: str = "127.0.0.1"
    port: int = Field(default=8787, ge=1, le=65535)


class Logging(Strict):
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    file: Path = Path("logs/router.log")
    max_bytes: int = Field(default=10_485_760, gt=0)
    backup_count: int = Field(default=5, ge=0)


class Stats(Strict):
    file: Path = Path("logs/calls.csv")
    max_bytes: int = Field(default=5_242_880, gt=0)
    backup_count: int = Field(default=10, ge=0)


class Config(Strict):
    backends: Backends
    server: Server = Field(default_factory=Server)
    logging: Logging = Field(default_factory=Logging)
    stats: Stats = Field(default_factory=Stats)

    def resolve_paths(self, base_dir: Path) -> None:
        """Make the log and stats paths absolute, relative to the config file's directory."""
        self.logging.file = _resolve(self.logging.file, base_dir)
        self.stats.file = _resolve(self.stats.file, base_dir)

    def api_keys(self) -> dict[str, str]:
        """Read the API key for every backend that asks for one.

        Returns a mapping of backend name to key. Backends that forward or strip the incoming
        credential do not appear.
        """
        keys: dict[str, str] = {}
        for name, backend in _named_backends(self.backends):
            if backend.api_key_env:
                keys[name] = os.environ[backend.api_key_env]
        return keys


def _resolve(path: Path, base_dir: Path) -> Path:
    return path if path.is_absolute() else (base_dir / path)


def _named_backends(backends: Backends) -> list[tuple[str, Backend]]:
    return [("anthropic", backends.anthropic), ("lmstudio", backends.lmstudio)]


def load_config(path: Path) -> Config:
    """Read, validate and return the configuration, or raise ConfigError with a readable message."""
    raw = _read_yaml(path)
    try:
        config = Config.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(_describe(exc, path)) from exc

    config.resolve_paths(path.parent.resolve())
    _check_api_keys(config)
    return config


def _read_yaml(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}") from None
    except OSError as exc:
        raise ConfigError(f"Could not read config file {path}: {exc}") from exc

    try:
        loaded = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Config file {path} is not valid YAML:\n{exc}") from exc

    if loaded is None:
        raise ConfigError(f"Config file {path} is empty.")
    if not isinstance(loaded, dict):
        raise ConfigError(
            f"Config file {path} must contain a mapping at the top level."
        )
    return loaded


def _check_api_keys(config: Config) -> None:
    """Fail now if a backend names an environment variable that is missing or empty.

    Waiting until the first request would turn a configuration mistake into a runtime one.
    """
    for name, backend in _named_backends(config.backends):
        variable = backend.api_key_env
        if variable and not os.environ.get(variable, "").strip():
            raise ConfigError(
                f"Backend '{name}' expects its API key in the environment variable "
                f"'{variable}', which is unset or empty.\n"
                f"Set it in your .env file, or remove 'api_key_env' from that backend to forward "
                f"or strip the incoming credential instead."
            )


def _describe(exc: ValidationError, path: Path) -> str:
    """Turn pydantic's error report into something readable in a terminal."""
    lines = [f"Config file {path} is invalid:"]
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "(top level)"
        lines.append(f"  {location}: {error['msg']}")
    return "\n".join(lines)
