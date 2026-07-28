"""The routing rule is small enough to read, but it decides where every request goes."""

from __future__ import annotations

import pytest

from ilirium_llm_router.config import Backend, Backends
from ilirium_llm_router.routing import backend_for_model, backend_name_for_model


@pytest.mark.parametrize(
    "model",
    [
        "claude-fable-5",
        "claude-opus-4-8",
        "claude-sonnet-5",
        "claude-haiku-4-5",
        "claude-something-not-released-yet",
    ],
)
def test_claude_models_go_to_anthropic(model: str) -> None:
    assert backend_name_for_model(model) == "anthropic"


@pytest.mark.parametrize(
    "model",
    [
        "qwen3-coder-30b",
        "gpt-oss-20b",
        "llama-3.3-70b",
        "mistral-small",
        "",
    ],
)
def test_everything_else_goes_to_lmstudio(model: str) -> None:
    assert backend_name_for_model(model) == "lmstudio"


def test_the_prefix_must_be_at_the_start() -> None:
    """A name merely containing `claude-` is a local model, not an Anthropic one."""
    assert backend_name_for_model("my-claude-clone") == "lmstudio"


def test_the_prefix_is_case_sensitive() -> None:
    assert backend_name_for_model("Claude-sonnet-5") == "lmstudio"


def test_backend_for_model_returns_the_matching_config() -> None:
    backends = Backends(
        anthropic=Backend(base_url="https://api.anthropic.com", credential="forward"),
        lmstudio=Backend(base_url="http://localhost:1234", credential="strip"),
    )

    name, backend = backend_for_model("claude-sonnet-5", backends)
    assert (name, backend.credential) == ("anthropic", "forward")

    name, backend = backend_for_model("qwen3-coder-30b", backends)
    assert (name, backend.credential) == ("lmstudio", "strip")
