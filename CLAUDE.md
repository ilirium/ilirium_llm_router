# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

**Phase 1 is done, verified in a real session on 2026-07-29** (see `docs/implementation-plan.md` for the phases, and `docs/testing-against-claude-code.md` for the procedure and the full results). The router forwards: it answers the `HEAD /` probe, dispatches `POST /v1/messages` by the model named in the body, and has a catch-all for every other path. Bodies are relayed byte for byte and replies streamed back untouched. **Next is Phase 2** — `stats.py` and `logging_setup.py` are still documented stubs, so nothing yet records what a call did.

Both halves work. `claude-sonnet-5` through the router behaves as a normal session. `google/gemma-4-e4b` in LM Studio handles tool use — reading and writing files, running bash commands, running a Python script and reading its stdout — with multi-turn conversation holding together. Streaming was confirmed incrementally in a curl smoke test rather than inferred from the display.

This settles the project's central claim: **no protocol translation is needed, and a local model can drive a real coding session through the router.**

**LM Studio's "Require Authentication" was switched on and has since been turned off.** Earlier on 2026-07-29 a forwarded local request came back `401 authentication_error` from LM Studio itself; later the same day LM Studio answered unauthenticated, and there is no `.env`. So the current working setup needs no local credential. If the setting is switched back on, uncomment `lmstudio.api_key_env: LMSTUDIO_API_KEY` in `config.yaml` and put the key in `.env`.

The auth setting is expected to go back on, and is the reason backend authentication is now a design decision rather than an untested extra — see "Design decisions" below. Note that the key path has still never carried a live request: the setting was turned off rather than configured around, so it is covered by a unit test and nothing more. The agreed config shape (one `credential` field, three modes, contradictions refused at startup) is **not implemented yet**; `config.py` still has the two-knob shape.

Note: `/Users/ilirium/Projects/code-2026/ilirium_llm_router` and the OneDrive path are the *same directory* (identical inode), not two checkouts. Editing either edits both.

## Layout and commands

```
config.yaml                 backend definitions, server, log/stats rotation — no model list
.env.example                normally empty; the router holds no secret (see auth note below)
src/ilirium_llm_router/
  config.py                 YAML → validated Config; raises ConfigError with a readable message
  routing.py                the `claude-` prefix rule
  proxy.py                  forwarding: peek the model, rebuild headers, stream the reply back
  stats.py                  Phase 2 — CSV rows (stub)
  logging_setup.py          Phase 2 — rotating log (stub)
  app.py                    FastAPI app factory; the four routes and the shared HTTP client
  cli.py                    entry point; `--check` validates config and exits
tests/
```

`make` on its own lists the targets. The useful ones:

| | |
|---|---|
| `make run` | start the server (`uv run ilirium-llm-router`) |
| `make check` | validate and print the config without starting |
| `make test` | run the tests; `make test ARGS="tests/test_config.py::test_empty_file_is_rejected"` for one |
| `make lint` / `make format` | ruff, fetched on demand via `uvx` — not a project dependency |
| `make sync` | install |
| `make clean` | caches and build artefacts; leaves `logs/` alone |

`make run CONFIG=other.yaml` overrides the config path on any target that takes one. There is no reload target: the app is built by a factory, which `uvicorn --reload` cannot import.

Config models set `extra="forbid"`, so a mistyped YAML key is an error rather than a silently ignored default. Relative log/stats paths resolve against the config file's directory, not the working directory.

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

The second real job is **credential handling**: *forward for cloud, strip for local*. Verified 2026-07-28 (see `docs/anthropic-auth-check.md`): Claude Code sends an OAuth subscription token as `Authorization: Bearer sk-ant-oat01-…`, and Anthropic accepts it as forwarded. So the router injects nothing and holds no secret — it passes the arriving credential through to Anthropic and removes it from LM Studio-bound requests, which have no use for it and might log it.

The `anthropic-beta` header must reach Anthropic verbatim. It arrives as a ten-entry comma-separated list, and one entry (`oauth-2025-04-20`) is what makes the bearer token acceptable; trimming the list turns a working request into a 401.

Known gaps to design around (not translation work — LM Studio's own surface):

- The Anthropic-compat namespace exposes **only `/v1/messages`** — there is no `/v1/models` under it. To advertise a merged model list, enumerate local models via LM Studio's native `GET /api/v1/models` (or its OpenAI-compat `GET /v1/models`). That endpoint is also how to find which model is currently loaded: look for a non-empty `loaded_instances`.
- LM Studio publishes **no feature-parity matrix**. Its `/v1/messages` docs don't spell out handling of `system`, `tool_result`, `thinking` blocks, or images. Verify these empirically against a loaded model before assuming passthrough is lossless. Measured so far: **tool calls work** (Phase 1 session) and **token usage is reported** in Anthropic's exact shape, streaming and not (`docs/lmstudio-usage-check.md`). Still unmeasured: a `role: "system"` message inside `messages`, `thinking` blocks, images.
- LM Studio recommends a model with **>~25k context**. Measured against a real request, that is optimistic: a bare `hi` turn arrived as **118 KB** of JSON — 81 KB of tool schemas (27 tools), 28 KB of system prompt, and 368 bytes of actual conversation. Call it ~30k tokens of fixed preamble before the user types anything, so a usable local model needs meaningfully more headroom than 25k.

  One data point against that estimate: the 2026-07-29 session ran `google/gemma-4-e4b` at a context length of **34304 tokens** and worked, tools and multi-turn included. That is only ~4k above the estimated preamble, which is less headroom than the estimate predicts a working session needs. Either the ~30k figure is pessimistic for this tokenizer, or context is being silently trimmed somewhere. Worth resolving in Phase 4, because silent truncation would degrade answers invisibly rather than failing loudly.

## Observed request shape

From one captured request (`docs/log-the-whole-request.txt` — token and account/device/session identifiers redacted; it is one 120 KB line, so read it with `jq`). Concrete facts that constrain the proxy:

- **Claude Code probes with `HEAD /` first**, from a separate client (`User-Agent: Bun/1.4.0`), before any `/v1/messages` call. The router must answer it or it looks like a dead endpoint at startup.
- **The path carries a query string**: `POST /v1/messages?beta=true`. Forward path *and* query.
- **`Accept-Encoding: gzip, deflate, br, zstd`** comes in, so requesting an uncompressed response upstream must be a deliberate override — otherwise `usage` can't be read from the passing bytes.
- **Body fields beyond the base API**: `context_management`, `output_config` (`{"effort":"high"}`), `metadata.user_id`. None were anticipated when this file was first written. This is the concrete case for byte-relay: a Pydantic full-body model would have silently dropped all three.
- **`cache_control: {"type":"ephemeral","ttl":"1h"}`** on the system blocks. Prompt caching matches on exact prefix bytes, so any reserialization — even key reordering that means the same thing — breaks cache hits and costs real money. Byte-relay is not just about forward-compatibility.
- **A `role: "system"` message inside `messages`** (the `mid-conversation-system-2026-04-07` beta). Almost certainly unsupported by LM Studio; a specific Phase 4 test item rather than a vague parity worry.
- Confirms two claims below: `thinking` is `{"type":"adaptive","display":"omitted"}`, and no `temperature`/`top_p`/`top_k` is sent at all.

## Design decisions

Decided deliberately; don't quietly reverse these.

- **Routing is a prefix rule in code, not a config table.** `model` starting with `claude-` → Anthropic; everything else → LM Studio. No per-model YAML. New Anthropic and local models work without touching config. YAML holds backend definitions (base URLs, which env var carries the key), not a model list.
- **No special case for background/auxiliary traffic.** Whatever `model` Claude Code sends gets routed by the same rule, including the small/fast model used for background calls. Consequence to keep in mind: a `claude-`prefixed background call leaves the machine and costs money even when the main model is local.
- **Relay the body, log only metadata.** Forward the request body byte-for-byte and stream the response through without re-encoding; peek at `model` for routing only. Log model, backend, status, and duration — never deserialize or re-serialize the payload. This keeps the proxy correct when either side adds fields, which is the main risk of a parse-and-rebuild design.
- **First milestone is a minimal end-to-end proxy:** uv project + FastAPI + `POST /v1/messages` dispatching to both backends with streaming working, verified by pointing Claude Code at it. Merged `/v1/models` and config polish come later.
- **Backend authentication is a first-class feature, not a leftover.** Every backend declares how its credential is obtained, and the router is expected to hold keys for some of them. This was settled on 2026-07-29 and reverses the earlier framing in which `api_key_env` was an untested extra to consider deleting. Two reasons: LM Studio's "Require Authentication" is a setting this machine actually uses and intends to keep using, and the planned expansion — other local runners, other cloud APIs — makes "the router holds no secret" false as a general rule. It stays true only of Anthropic, which is one backend's property rather than the architecture's.

  **The shape: one field, three modes.** `credential:` is the only knob, and `api_key_env` is required by `inject` and forbidden by the others.

  | Mode | Meaning |
  |---|---|
  | `forward` | pass the caller's credential through untouched (Anthropic) |
  | `strip` | remove it — a local server has no use for a real token and might log it |
  | `inject` | remove it and send the key named by `api_key_env` instead |

  This replaces a two-knob shape in which `credential` and `api_key_env` were independent and the key silently won, so `credential: forward` alongside a key read as "forward the caller's token" and did not do that. With one backend needing auth that was a wart; with several it is a trap.

  **Contradictions are startup errors, not silent behaviour.** `inject` without `api_key_env`, and `api_key_env` without `inject`, are both refused. So is an environment variable that is unset or empty. Each message must say what is wrong *and* how to fix it, then exit — matching how the rest of config loading already behaves. A backend that authenticates with nothing, or a key that looks configured and is never sent, are exactly the failures that surface as a confusing 401 much later.

  **Not yet implemented.** `config.py` still has the two-knob shape; this is a decision, not a description. The header question is also open and deliberately unanswered: `inject` currently means `Authorization: Bearer`, which suits LM Studio and OpenAI, but Anthropic's native key is `x-api-key` and Gemini's is `x-goog-api-key`. A per-backend header name will be needed before the second cloud provider, not before.

## Observability: log + CSV stats

Every call is logged **and** appended as one row to a CSV, so model/backend comparisons are analyzable without parsing free-text logs.

CSV columns:

| Column | Source |
|---|---|
| `timestamp` | ISO 8601, when the request arrived |
| `session_id` | `x-claude-code-session-id`, copied from the request headers. Groups a session's calls without parsing bodies. Empty when the header is absent, since a non-Claude-Code caller has no reason to send it |
| `agent_id` | `x-claude-code-agent-id`. **Present only on requests from a subagent**, so an empty value means the main conversation — that emptiness is the signal, not missing data. Without this column a mixed-model session collapses into an indistinguishable pile of rows, and it is far cheaper to write now than to retrofit into a working CSV writer. See `EPD-001-model-selection-and-mixed-model-sessions.md` for why mixed-model sessions are expected at all |
| `backend` | `anthropic` or `lmstudio` |
| `model` | peeked from the request body |
| `input_tokens` | `usage.input_tokens`, tee'd from the response |
| `output_tokens` | `usage.output_tokens` (free alongside the above) |
| `cache_read_input_tokens` | `usage.cache_read_input_tokens`. Reported by both backends and free alongside the other two. It is here because prompt-cache behaviour is *why* the body is relayed byte for byte: without this column the project's most expensive constraint stays an assumption instead of a measurement. Empty when a backend omits it |
| `request_bytes` | raw body length — always available, even when `usage` is not. Note it is dominated by the ~110 KB fixed preamble, so it is a weak proxy for conversation size; keep it as the fallback it is, not the comparison metric |
| `duration_ms` | wall time until the response *completes* (stream fully drained), not time-to-first-byte |
| `is_error` | boolean |
| `error_code` | HTTP status, or a symbolic code for transport failures |
| `error_message` | short description, single line, no embedded newlines |

A note on the cache column, since it is the one that needs justifying: LM Studio does real prefix caching, observed rising from 5 to 15 tokens across two runs of the same prompt (`docs/lmstudio-usage-check.md`). A cache-hit rate that collapses is the signal that something upstream has started rewriting request bytes — which is exactly the failure byte-relay exists to prevent, and is otherwise invisible.

Implementation constraints that fall out of this:

- **The two identifier columns come from headers, not the body.** Copying `x-claude-code-session-id` and `x-claude-code-agent-id` costs a dictionary lookup and needs no parsing, which is the whole reason they are affordable. `session_id` is measured — it is in the captured request, which is why `handoff.md` records redacting an `X-Claude-Code-Session-Id`. `agent_id` is documented only; the capture predates any subagent use here, so expect to confirm it arrives before trusting an empty column to mean "main conversation". Neither is a user identifier: an agent ID identifies a spawn, and subagent IDs are generated fresh each time.
- **Tee, don't parse-and-rebuild.** Relay response bytes downstream untouched while scanning a copy for `usage`. Byte-relay fidelity is preserved; observation is passive. If `usage` can't be found, write empty token columns rather than failing the request.
- **Take `input_tokens` from `message_start` and `output_tokens` from the final `message_delta`.** Verified against LM Studio 2026-07-29 (`docs/lmstudio-usage-check.md`); both backends carry usage in Anthropic's shape, so one rule covers both. Resist the obvious simplification: LM Studio repeats `input_tokens` in `message_delta`, so a scanner keyed on that event alone would look correct locally and silently record empty input counts for every Anthropic call. Non-streaming replies put `usage` at the top level instead, so that form needs its own path.
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

Commands are listed under "Layout and commands" above. Python 3.13; the app is created by a factory (`app.create_app(config)`) rather than a module-level `app`, so `uvicorn <module>:app` does not apply — start it through the CLI.

## Style

The README names two explicit non-negotiables: **simple configuration** and **simple, human-readable code**. Prefer an obvious explicit mapping over a clever generic one.
