# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

The repository currently contains only `README.md`, `.gitignore`, and `.idea/` — **no source code, no `pyproject.toml`, no tests yet**. Everything below is the design the README commits to; treat it as the target, and update this file as real structure lands.

Note: `/Users/ilirium/Projects/code-2026/ilirium_llm_router` and the OneDrive path are the *same directory* (identical inode), not two checkouts. Editing either edits both.

## Goal

A router that lets a coding harness reach several model backends at once. Concretely: Claude Code should see Anthropic's own models (Haiku, Sonnet, Opus, Fable) **and** locally served LM Studio models simultaneously, switchable by picking a model in LM Studio.

Planned later: other harnesses (OpenAI Codex, Google Antigravity, GitHub Copilot, JetBrains Junie; Pi, Hermes, OpenCode, OpenClaw) and other cloud backends (OpenAI, Gemini, OpenRouter).

## The central architectural problem

The router sits between two *different* wire protocols, and the whole design follows from that:

- **North side (what the router must serve):** Claude Code speaks the **Anthropic Messages API** — `POST /v1/messages`, headers `x-api-key` and `anthropic-version: 2023-06-01`, streaming as SSE (`message_start` → `content_block_start` → `content_block_delta` → `content_block_stop` → `message_delta` → `message_stop`). A harness is pointed at a custom router by setting `ANTHROPIC_BASE_URL` (and an auth token). Content is a **list of typed blocks** (`text`, `thinking`, `tool_use`, `tool_result`), not a single string; `system` is a top-level field, not a message.
- **South side (what backends speak):** LM Studio serves an **OpenAI-compatible** API — `POST /v1/chat/completions`, `data: {...}` / `data: [DONE]` SSE, flat string content, `system` as `messages[0]`, tools as `tool_calls`.

So the router is: Anthropic-shaped ingress → route by model name → either **pass through** to `api.anthropic.com` for Anthropic model IDs, or **translate both directions** (request and streaming response) for OpenAI-compatible local models. The translation layer — especially streaming and tool-call round-tripping — is the hard part and the thing worth designing first.

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
- **Pydantic** models for requests/responses/messages — this is the natural place to encode the Anthropic ↔ OpenAI block translation.
- **YAML** for configuration (backends, model routing table); **`.env`** for API keys.
- **`uv`** for dependencies and project management.

Once `pyproject.toml` exists, the commands are `uv sync`, `uv run uvicorn <module>:app --reload`, `uv run pytest`, and `uv run pytest path/to/test.py::test_name` for a single test. Verify against the actual project file rather than assuming.

## Style

The README names two explicit non-negotiables: **simple configuration** and **simple, human-readable code**. Prefer an obvious explicit mapping over a clever generic one.
