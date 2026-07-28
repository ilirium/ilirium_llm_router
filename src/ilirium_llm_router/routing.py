"""Deciding which backend a request goes to.

The rule is a prefix check in code, deliberately not a config table: a model named `claude-…` is an
Anthropic model, anything else is served locally. New models on either side work without touching
configuration.

This applies to every request, including the small fast model used for background work. A
`claude-` prefixed background call therefore leaves the machine and costs money even when the main
model is local.
"""

from __future__ import annotations

from typing import Literal

from .config import Backend, Backends

BackendName = Literal["anthropic", "lmstudio"]

ANTHROPIC_MODEL_PREFIX = "claude-"


def backend_name_for_model(model: str) -> BackendName:
    """Return which backend serves this model."""
    return "anthropic" if model.startswith(ANTHROPIC_MODEL_PREFIX) else "lmstudio"


def backend_for_model(model: str, backends: Backends) -> tuple[BackendName, Backend]:
    """Return the name and configuration of the backend serving this model."""
    name = backend_name_for_model(model)
    return name, getattr(backends, name)
