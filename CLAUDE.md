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

## Design decisions

Decided deliberately; don't quietly reverse these.

- **Routing is a prefix rule in code, not a config table.** `model` starting with `claude-` → Anthropic; everything else → LM Studio. No per-model YAML. New Anthropic and local models work without touching config. YAML holds backend definitions (base URLs, which env var carries the key), not a model list.
- **No special case for background/auxiliary traffic.** Whatever `model` Claude Code sends gets routed by the same rule, including the small/fast model used for background calls. Consequence to keep in mind: a `claude-`prefixed background call leaves the machine and costs money even when the main model is local.
- **Relay the body, log only metadata.** Forward the request body byte-for-byte and stream the response through without re-encoding; peek at `model` for routing only. Log model, backend, status, and duration — never deserialize or re-serialize the payload. This keeps the proxy correct when either side adds fields, which is the main risk of a parse-and-rebuild design.
- **First milestone is a minimal end-to-end proxy:** uv project + FastAPI + `POST /v1/messages` dispatching to both backends with streaming working, verified by pointing Claude Code at it. Merged `/v1/models` and config polish come later.

## Observability: log + CSV stats

Every call is logged **and** appended as one row to a CSV, so model/backend comparisons are analyzable without parsing free-text logs.

CSV columns:

| Column | Source |
|---|---|
| `timestamp` | ISO 8601, when the request arrived |
| `backend` | `anthropic` or `lmstudio` |
| `model` | peeked from the request body |
| `input_tokens` | `usage.input_tokens`, tee'd from the response |
| `output_tokens` | `usage.output_tokens` (free alongside the above) |
| `request_bytes` | raw body length — always available, even when `usage` is not |
| `duration_ms` | wall time until the response *completes* (stream fully drained), not time-to-first-byte |
| `is_error` | boolean |
| `error_code` | HTTP status, or a symbolic code for transport failures |
| `error_message` | short description, single line, no embedded newlines |

Implementation constraints that fall out of this:

- **Tee, don't parse-and-rebuild.** Relay response bytes downstream untouched while scanning a copy for `usage`. Byte-relay fidelity is preserved; observation is passive. If `usage` can't be found, write empty token columns rather than failing the request.
- **Streaming hides errors behind a 200.** A streamed response returns HTTP 200 before content exists, so a backend failure can arrive as an SSE `error` event mid-stream. Error detection must watch the tee'd stream, not just the initial status code.
- **Never let telemetry break a call.** Any failure in logging or CSV writing is caught and dropped; the proxied request always wins.
- **Transport errors matter most here.** LM Studio simply not running is the common failure. That's a connection error with no HTTP status — give it a symbolic `error_code` rather than leaving it blank.
- Rotation is size-based for both files, with sizes set in YAML. On rotation the CSV must **re-emit its header row** in the new file, or rotated segments won't parse standalone.

Config shape:

```yaml
logging:
  level: INFO
  file: logs/router.log
  max_bytes: 10485760   # 10 MiB
  backup_count: 5

stats:
  file: logs/calls.csv
  max_bytes: 5242880    # 5 MiB
  backup_count: 10
```

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
