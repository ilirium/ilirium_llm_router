# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

The repository currently contains only `README.md`, `.gitignore`, and `.idea/` — **no source code, no `pyproject.toml`, no tests yet**. Everything below is the design the README commits to; treat it as the target, and update this file as real structure lands.

Note: `/Users/ilirium/Projects/code-2026/ilirium_llm_router` and the OneDrive path are the *same directory* (identical inode), not two checkouts. Editing either edits both.

## Goal

A router that lets a coding harness reach several model backends at once. Concretely: Claude Code should see Anthropic's own models (Haiku, Sonnet, Opus, Fable) **and** locally served LM Studio models simultaneously, switchable by picking a model in LM Studio.

Planned later: other harnesses (OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie; Pi, Hermes, OpenCode, OpenClaw) and other cloud backends (OpenAI, Gemini, OpenRouter).

## The central architectural problem: dispatch, not translation

**No protocol translation is needed for LM Studio.** LM Studio (0.4.1+) natively implements the Anthropic-compatible `POST /v1/messages`, including the same SSE event sequence (`message_start` → `content_block_start` → `content_block_delta` → `content_block_stop` → `message_delta` → `message_stop`), `tools` with `input_schema`, and `tool_choice`. It accepts both `x-api-key` and `Authorization: Bearer`. Claude Code can already point straight at it:

```
ANTHROPIC_BASE_URL=http://localhost:1234
ANTHROPIC_AUTH_TOKEN=lmstudio
CLAUDE_CODE_ATTRIBUTION_HEADER=0
claude --model <lmstudio-model-id>
```

So both sides of the router speak the *same* protocol, and the router is a **model-name dispatcher / reverse proxy**, not a translator:

- `claude-*` model IDs → forward to `api.anthropic.com` with the real API key
- everything else → forward to LM Studio at `localhost:1234`

This is why the router exists at all: **Claude Code accepts exactly one `ANTHROPIC_BASE_URL`.** Pointing it at LM Studio gives up the Anthropic models; pointing it at Anthropic gives up the local ones. Something has to sit in front and route per-request to have both at once. Because the protocol matches on both sides, the request body can likely be forwarded unmodified and the response stream relayed as bytes, rather than parsed and re-emitted.

The second real job is **credential injection**: the local side wants a dummy token, the cloud side needs the real key. The router picks the right credential per route, so the developer configures one endpoint.

Known gaps to design around (not translation work — LM Studio's own surface):

- The Anthropic-compat namespace exposes **only `/v1/messages`** — there is no `/v1/models` under it. To advertise a merged model list, enumerate local models via LM Studio's native `GET /api/v1/models` (or its OpenAI-compat `GET /v1/models`).
- LM Studio publishes **no feature-parity matrix**. Its `/v1/messages` docs don't spell out handling of `system`, `tool_result`, `thinking` blocks, or images. Verify these empirically against a loaded model before assuming passthrough is lossless.
- LM Studio recommends a model with **>~25k context**, since Claude Code is context-hungry.

## Anthropic model IDs

Use exact strings; do not append date suffixes.

| Tier | ID |
|---|---|
| Fable 5 | `claude-fable-5` |
| Opus 4.8 | `claude-opus-4-8` |
| Sonnet 5 | `claude-sonnet-5` |
| Haiku 4.5 | `claude-haiku-4-5` |

Two request-shape facts that matter when proxying to current models: `thinking` is `{"type": "adaptive"}` (`budget_tokens` is rejected), and `temperature`/`top_p`/`top_k` are rejected on Opus 4.7+ / Sonnet 5 / Fable 5. A naive passthrough that injects sampling params will 400.

## Stack decisions (from README)

- Python, FastAPI, type hints throughout.
- **Pydantic** models for requests/responses/messages. Note that since the router forwards rather than translates, validation is mainly needed for the *routing-relevant* fields (`model`, `stream`) — full-body parsing is optional and costs fidelity if LM Studio or Anthropic add fields the models don't know about.
- **YAML** for configuration (backends, model routing table); **`.env`** for API keys.
- **`uv`** for dependencies and project management.

Once `pyproject.toml` exists, the commands are `uv sync`, `uv run uvicorn <module>:app --reload`, `uv run pytest`, and `uv run pytest path/to/test.py::test_name` for a single test. Verify against the actual project file rather than assuming.

## Style

The README names two explicit non-negotiables: **simple configuration** and **simple, human-readable code**. Prefer an obvious explicit mapping over a clever generic one.
