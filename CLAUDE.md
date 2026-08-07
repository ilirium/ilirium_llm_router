# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

**Phase 1 is done, verified in a real session on 2026-07-29** (see `docs/implementation-plan.md` for the phases, and `docs/testing-against-claude-code.md` for the procedure and the full results). The router forwards: it answers the `HEAD /` probe, dispatches `POST /v1/messages` by the model named in the body, and has a catch-all for every other path. Bodies are relayed byte for byte and replies streamed back untouched.

**Phase 2 is done, all six steps, proven in a real session on 2026-07-31.** Built on `feat/phase-2-observability` and merged to `main` the same day as `4d7d7f6`; 139 tests pass. Every call leaves two traces: a line in a rotating log — which uvicorn's own lines join, so "did the request arrive" and "was the server up" sit next to it — and a row in `logs/calls.csv` with all 20 columns. Usage is read off a tee of the passing bytes, never by parsing and rebuilding them.

The step 6 session — long, switching models mid-conversation, subagents, an interrupted response, tool use and file editing on a local model — produced **142 rows across eleven sessions**, frozen in `docs/phase-2-step-6-session/` because `logs/` is gitignored and rotates. It answered all four questions Phase 2 existed to settle:

| Question | Answer |
|---|---|
| Does `x-claude-code-agent-id` arrive? | **Yes** — 7 rows under one agent ID, covering the subagent's own background calls as well as its main one |
| Does starlette reach `client_disconnect`? | **Yes** — 6 rows, both backends. Some captured partial usage before the drop, some nothing |
| Do Anthropic's streamed replies scan like LM Studio's? | **Yes** — 32 streamed Anthropic rows fully populated. Their `input_tokens: 2` is the `message_start`-only rule earning itself |
| Does anything unexpected reach the catch-all? | **Yes** — `/v1/messages/count_tokens`, 33 rows. See `EPD-002` |

It also exposed four defects in the recorder, all since fixed: `stream` written blank where Claude Code omits the field, the log and CSV timestamping on different clocks, the backend's symbolic `error.type` being discarded, and completion-ordered rows going undocumented.

Two facts worth carrying forward. **A single session reached both backends** — `session-03` and `session-06` in the frozen CSV — which is the project's central claim measured rather than argued. And **median time to first byte was 1426 ms against Anthropic and 37136 ms against LM Studio**, a 26× gap that `duration_ms` alone would have blurred.

Both halves work. `claude-sonnet-5` through the router behaves as a normal session. `google/gemma-4-e4b` in LM Studio handles tool use — reading and writing files, running bash commands, running a Python script and reading its stdout — with multi-turn conversation holding together. Streaming was confirmed incrementally in a curl smoke test rather than inferred from the display.

This settles the project's central claim: **no protocol translation is needed, and a local model can drive a real coding session through the router.**

**Phase 3 is done, verified on 2026-07-31** against a live server and a real Claude Code session; 147 tests. Its central finding is about the plan rather than the code: **four of its five work items were already built by Phase 2**, which was specified as observability and delivered most of the error handling as a by-product of needing an `error_status` column. What was left were four gaps nobody had written down — a caller that left while its body was still arriving raised instead of recording; the upstream close rode on a starlette `BackgroundTask` that is skipped on ASGI spec 2.4, so it worked by luck; a broken stream told the caller nothing; and unhandled exceptions came back as plain-text 500s. See `docs/phase-3-notes.md`.

Two measurements from it are worth carrying: **Claude Code retries a 502 ten times with backoff**, so a session heals itself if LM Studio comes back — and one turn becomes up to ten `transport_error` rows, which means a row count is not a turn count when a backend is down. And **Claude Code ignores a mid-stream `error` event**, which is recorded under "Design decisions" below as the exception to byte-relay that has no measured consumer.

**Phase 4 is done, measured on 2026-08-06** against `qwen/qwen3.5-9b` loaded at 44544 tokens; the instrument is `docs/phase-4-probes/` and the findings are in `docs/phase-4-notes.md`. Its headline is that **nothing was rejected** — every shape this file predicted would fail was accepted, including a system-role message inside `messages`, and the whole captured 118 KB request replays unmodified. The gaps are quieter than rejections: `thinking.budget_tokens` ignored, and `output_config.effort` billing reasoning it never shows. Details in the LM Studio bullets below.

Three results reach beyond parity. **Prompt caching is now measured end to end** — the same replay twice gave `cache_read_input_tokens` 27904 of 27924 and cut time to first byte from 196789 ms to 49629 ms, which is the byte-relay decision paying for itself rather than being argued for. **Silent truncation does not happen**; an over-window request is refused in under a second with an actionable message, though in a form Claude Code may not display. And **the router's own 600 s read timeout is reachable by ordinary traffic**, which is a defect this phase found and deliberately did not fix.

A third of Phase 4 turned out to be already measured by Phase 2's frozen session — the second time in a row a phase has found its work partly done, after Phase 3 found four of its five items already built.

**Phase 5 is done, verified against live traffic on 2026-08-07**; 157 tests. Two items, both configuration, chosen in `docs/outstanding-work.md` as the only two things left that were work rather than a decision waiting on a person. Findings in `docs/phase-5-notes.md`, measurements in `docs/phase-5-measurements/`.

**The credential shape agreed on 2026-07-29 is built**, and `inject` has now carried a live request against an authenticated LM Studio — the first time that path has ever seen real traffic. Writing it found the same ambiguity in two more places than the known one: `api_keys()` collected a key regardless of mode, and `--check` would have *displayed* a forwarding backend as injecting.

**The read timeout is per backend**, which retires Phase 4's one real defect and unblocks the measurement it was blocking: **there is no silent trimming below the context boundary** — 41595 tokens against a 44544 window, 93% full, codeword returned from the very front.

Its process lesson is a variant of the previous three. Phase 3 and Phase 4 each found work already *built*; Phase 5 found work already *misdescribed*. Two of the three timeout options in the handoff did not exist as stated, and "a wedged backend fails in bounded time" was never true of duration. **The notes about the code had drifted from the code, and only a measurement caught it.**

**LM Studio's "Require Authentication" has been on and off, and the key path now works against it.** On 2026-07-29 a forwarded local request came back `401 authentication_error` from LM Studio itself; the setting was then turned off, which is why for months the key path was covered by a unit test and nothing more. **On 2026-08-07 it was switched back on and `credential: inject` carried a real request** — HTTP 200 with the caller's own (fake) Anthropic token replaced by the configured key, against a `strip` control at the same moment that returned 401. Details in `docs/phase-5-notes.md`.

To use it: set `credential: inject` **and** `api_key_env: LMSTUDIO_API_KEY` on the `lmstudio` backend in `config.yaml`, and put the key in `.env`. It takes both lines now — naming the variable alone is refused at startup rather than silently overriding the mode.

Note: `/Users/ilirium/Projects/code-2026/ilirium_llm_router` and the OneDrive path are the *same directory* (identical inode), not two checkouts. Editing either edits both.

## Layout and commands

```
config.yaml                 backend definitions, server, log/stats rotation — no model list
.env.example                normally empty; the router holds no secret (see auth note below)
src/ilirium_llm_router/
  config.py                 YAML → validated Config; raises ConfigError with a readable message
  routing.py                the `claude-` prefix rule
  proxy.py                  forwarding: peek the body, rebuild headers, tee the reply back
  observe.py                the two usage scanners, and `Call` — one call from arrival to row
  stats.py                  the CSV: one row per call, size-rotated, header re-emitted
  logging_setup.py          the rotating log; uvicorn's loggers are pointed at it too
  app.py                    FastAPI app factory; the four routes, HTTP client and stats writer
  cli.py                    entry point; `--check` validates config and exits
tests/
```

`make` on its own lists the targets. The useful ones:

| | |
|---|---|
| `make run` | start the server (`uv run ilirium-llm-router`) |
| `make check` | validate and print the config without starting |
| `make test` | run the tests; `make test ARGS="tests/test_config.py::test_empty_file_is_rejected"` for one |
| `make lint` / `make format` | ruff, fetched on demand via `uvx` — not a project dependency, but **pinned** in the Makefile |
| `make sync` | install |
| `make clean` | caches and build artefacts; leaves `logs/` alone |

`make run CONFIG=other.yaml` overrides the config path on any target that takes one. There is no reload target: the app is built by a factory, which `uvicorn --reload` cannot import.

Config models set `extra="forbid"`, so a mistyped YAML key is an error rather than a silently ignored default. Relative log/stats paths resolve against the config file's directory, not the working directory.

**Formatting is fixed in two places, and both are there because it went wrong once.** `pyproject.toml` sets `line-length = 100`, and the Makefile pins `RUFF ?= ruff@0.16.1`. Before either existed, `make format` used ruff's default 88 columns against a codebase written at 100 and rewrote every file it touched — so the target could not be run without burying whatever change was in progress, and `make lint` never objected, because line length is `E501` and that is not in ruff's default rule set.

The pin is the other half of the same problem: an unpinned formatter reformats the repository the day it changes its mind, and the bump then arrives disguised as somebody's feature branch. **Bump it deliberately.** `make format RUFF=ruff@x.y.z` tries a version without committing to it, and the diff that produces is the argument for or against taking it. When a bump is accepted, it belongs in its own commit — `d1def4f` is the precedent, and the way to check such a commit is to compare every file's AST before and after rather than to trust that formatting only moves whitespace.

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
- LM Studio publishes **no feature-parity matrix**. Its `/v1/messages` docs don't spell out handling of `system`, `tool_result`, `thinking` blocks, or images. **Phase 4 measured it instead, on 2026-08-06 against `qwen/qwen3.5-9b`** — see `docs/phase-4-notes.md`, and re-run `docs/phase-4-probes/` to check it again, because these answers expire with each LM Studio release.

  **Nothing was rejected.** Every shape sent came back HTTP 200 with no error body, including the ones this file predicted would fail. The gaps that exist are quieter than a rejection — things accepted and then not honoured.

  | Shape | Accepted | Honoured |
  |---|---|---|
  | `role: "system"` message inside `messages` | yes | **yes** — obeyed an instruction given only there |
  | Image content block (base64 PNG) | yes | **yes** — named four quadrant colours in the order asked |
  | `thinking: {"type": "adaptive"}` | yes | **yes** — real `thinking` blocks in Anthropic's shape |
  | `thinking.budget_tokens` | yes | **no** — the budget is ignored; thinking runs until `max_tokens` |
  | `output_config: {"effort": "high"}` | yes | **yes, invisibly** — see below |
  | `context_management`, `metadata.user_id` | yes | no observable effect |
  | `cache_control` | yes | not on a small prefix; works at scale |
  | the ten-entry `anthropic-beta` header | yes | n/a — never objected to |

  Two of those deserve carrying. **`output_config.effort` turns reasoning on and bills it without showing it**: the same prompt costs 4 output tokens without the field and 216 with it, ~98% of them invisible, because reasoning is only emitted as a content block when `thinking` is also set. Claude Code sends `output_config` on every request. And **thinking is unbounded**, so a request combining it with a small `max_tokens` returns a well-formed message containing *nothing* — HTTP 200, no content blocks, `stop_reason: max_tokens`. Claude Code's own `max_tokens: 64000` leaves room, so this does not bite in practice; anything more frugal does. Note the failure signature is indistinguishable in the CSV from a prompt-cache warmup probe.

  **The whole real request works.** `docs/log-the-whole-request.txt` — 27 tools, a system-role message, two `cache_control` markers, `context_management`, `output_config`, `metadata`, `thinking` — replays against a local model unmodified and answers correctly. There was nothing to bisect.
- LM Studio recommends a model with **>~25k context**. Measured against a real request, that is optimistic: a bare `hi` turn arrived as **118 KB** of JSON — 81 KB of tool schemas (27 tools), 28 KB of system prompt, and 368 bytes of actual conversation. Call it ~30k tokens of fixed preamble before the user types anything, so a usable local model needs meaningfully more headroom than 25k.

  **The preamble is now measured rather than estimated: 27924 tokens**, from replaying that exact request against `qwen/qwen3.5-9b` on 2026-08-06. The ~30k estimate was good and slightly pessimistic. Against a 44544-token window that is **63% of the context gone before the user types anything**.

  **And the silent-trimming worry is settled: there is none at the boundary.** A request whose input exceeds the loaded window is **refused**, in under a second, with `api_error` and the message `The number of tokens to keep from the initial prompt is greater than the context length. Try to load the model with a larger context length, or provide a shorter input`. Nothing is quietly dropped. The 34304-token `google/gemma-4-e4b` session worked because it fit, not because anything was trimmed.

  **And there is none below the boundary either, measured in Phase 5 on 2026-08-07** once the read timeout stopped preventing the run. A prompt of **41595 tokens against a 44544 window — 93% full** — returned the codeword planted at its very front, with `input_tokens` matching what was sent. So the worry is closed at both ends: refused above the window, answered in full below it.

  One caveat still keeps this from being a clean all-clear. The refusal arrives as an **SSE `error` event inside an HTTP 200** — the shape Phase 3 measured Claude Code ignoring — so the most actionable message LM Studio produces may never reach the user. And all of it is one model at one window size.

- **The router's 600-second read timeout is reachable by ordinary local traffic**, found 2026-08-06. A ~41000-token request against a 44544-token window was killed at exactly `read=600.0` while LM Studio was still healthily prefilling — `transport_error` / `read_timeout`. Measured times to first byte on that model: 9166 tokens → 115 s, 27924 tokens → 197 s, ~41000 tokens → never.

  **Fixed in Phase 5 on 2026-08-07: `read_timeout` is now per backend**, 600 s for Anthropic and 1800 s for LM Studio, defaulting to 600 so an older config is unchanged. A model loaded at 44544 can now be driven to 93% of its window through the router — measured, 41595 input tokens answered in full.

  Two corrections Phase 5 owes this bullet, both measured (`docs/phase-5-measurements/`). **"Resets on progress" was never one of the three options — it is already the behaviour**: `read` bounds the silence between two reads and every chunk restarts it, which is why a silent prefill hits it and a slow stream does not. And **"a wedged backend fails in bounded time" was never true of duration**, only of silence: a backend dribbling one byte every 599 s would have run forever under the old setting too. Raising the number gave up less than this paragraph used to imply.

  The honest limit on the verification: the completing run's first byte arrived at 461712 ms, *under* the old 600 s ceiling, so it did not reproduce the failure Phase 4 measured at 600247 ms. The same request straddles the old threshold across runs, which is the argument for configuring the number rather than hard-coding it. What proves the field governs live traffic is the companion run at `read_timeout: 30`, which dies at 30343 ms with Phase 4's exact signature.

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

  **Measured 2026-07-31, and the cost is worse than this decision anticipated.** The expensive case is not money on cloud calls — it is *minutes* on local ones. Claude Code sends **prompt-cache warmup probes**: `max_tokens: 1` requests whose only purpose is to create a cache entry. Against Anthropic they are nearly free. Against LM Studio each one is a full prefill that returns nothing — reproduced directly, `content: []`, `output_tokens: 0`, `stop_reason: max_tokens`.

  In the step 6 session that was **40 calls and 20.0 of 45.5 minutes — 44% of all local wall-clock time — spent on requests that returned zero content tokens.** One took 111 seconds for a 31 KB body. They are visible in `docs/phase-2-step-6-session/calls.csv` as rows with `stop_reason: max_tokens` and `output_tokens: 0`.

  This is not a bug and nothing is currently done about it. It is recorded here because it is the strongest argument yet for revisiting the decision — a routing exception for `max_tokens: 1` probes on local backends would return nearly half the wall clock, at the price of the first special case in the dispatch rule. That trade belongs to a later phase, not to Phase 2.
- **Relay the body, log only metadata.** Forward the request body byte-for-byte and stream the response through without re-encoding; peek at `model` for routing only. Log model, backend, status, and duration — never deserialize or re-serialize the payload. This keeps the proxy correct when either side adds fields, which is the main risk of a parse-and-rebuild design.
- **One exception to byte-relay: a broken stream is ended with an SSE `error` event.** Decided
  2026-07-31 in Phase 3. A streamed reply returns HTTP 200 before any content exists, so when the
  relay breaks afterwards the failure cannot go in a status code — and a stream that simply stops is
  indistinguishable from a model that finished talking. The router appends one Anthropic-shaped
  `error` event to such a stream, which is the only place it writes bytes of its own into a relayed
  reply.

  Three limits keep this from becoming a parse-and-rebuild wedge: it is **appended, never altering**
  (every backend byte still goes out untouched, and the prompt-cache argument is about *request*
  bytes regardless); it happens **only on SSE replies**, since the same frame stapled to a
  half-written JSON object is corruption rather than a message; and the injected bytes are **not
  counted in `response_bytes` and not fed to the scanner**, because both measure what the backend
  sent. Rationale and the rejected alternative are in `docs/phase-3-notes.md`.

  **Measured the same day, and it buys nothing for Claude Code.** Against a stand-in backend that
  sends a complete `message_start`, a text block, seven deltas and then resets, Claude Code reports
  `API returned an empty or malformed response (HTTP 200)` — its own generic wording, not ours. The
  comparison that makes this conclusive: on a 502 it prints the router's message *verbatim*, so it
  surfaces backend wording when it recognises an error. It does not recognise a mid-stream `error`
  event; it is reporting the missing `message_stop`, which is what it would say if nothing were
  injected at all.

  **Kept anyway, deliberately, on 2026-07-31.** The event is Anthropic's documented shape, the cost
  is about fifteen lines behind one test, and the harnesses named under "Goal" are not this one. But
  it is a feature with **no measured consumer**, and this paragraph exists so nobody later mistakes
  it for something that solved a visible problem. If a second client also ignores it, delete it.
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

  **Implemented in Phase 5 on 2026-08-07**, and `inject` has carried a live request against an LM Studio requiring authentication. The mode is the only thing consulted at request time, so the ambiguity is unrepresentable rather than discouraged. Writing it revealed the same ambiguity in two more places than the known one in `proxy.py`: `api_keys()` collected a key for any backend naming a variable, and `cli.py` *displayed* injection whenever a key existed — so `--check` would have reported a forwarding backend as injecting. See `docs/phase-5-notes.md`.

  The header question remains open and deliberately unanswered: `inject` means `Authorization: Bearer`, which suits LM Studio and OpenAI, but Anthropic's native key is `x-api-key` and Gemini's is `x-goog-api-key`. A per-backend header name will be needed before the second cloud provider, not before — and Phase 5 deliberately did not settle it while editing the same function.

## Open proposals — the EPDs

The section above holds decisions. Questions that are **written up and deliberately not decided** live in `docs/epd/` as **EPDs — Enhancement Proposal Documents**, indexed by `docs/epd/EPD-000-about-these-documents.md`, which also records the conventions they follow. Read that first; it is short.

Nothing in an EPD is implemented unless the document names the date it was accepted. Do not build from one. The rule that makes them useful: an EPD separates a **finding**, which is measured and durable, from the **decision** it implies, which usually is not.

| | Waiting on | In one line |
|---|---|---|
| `EPD-001` | **a decision** — its Phase 4 gate is met | Picking a local model mid-session with `/model`, and subagents on local models. Per-request dispatch already satisfies the second with no code. Its one accepted piece is the CSV's `session_id` / `agent_id` columns. Phase 4 discharged the reason for waiting: a local model *can* hold a real session |
| `EPD-002` | **a decision, on a weakened case** | LM Studio does not implement `count_tokens` and answers HTTP 200 with an error body, so Claude Code estimates against an assumed 200k window. Phase 4 measured the harm it was organised around and **found none** — the boundary refuses rather than trimming silently — and also found the proposal reading `max_context_length` where it needs the loaded `context_length`. Both in its addendum |
| `EPD-003` | a decision on the fine-tuning goal | Storing every request and response body as a corpus. The corpus is ~93% repeated prefix; the storage question is a compression-window question, not a database one; and Anthropic's terms bear on the fine-tuning half |

Two of them argue that "Relay the body, log only metadata" above is narrower than it looks — that it protects bodies the router *relays*, and so does not reach a body the router answers itself (`EPD-002`) or an opaque copy it never parses (`EPD-003`). `EPD-003` additionally asks to reverse one sentence of the section below, the one ruling out anything body-shaped. **None of that has been accepted**, and reversing either rule quietly is exactly what these documents exist to prevent.

## Observability: log + CSV stats

Every call is logged **and** appended as one row to a CSV, so model/backend comparisons are analyzable without parsing free-text logs.

CSV columns:

| Column | Source |
|---|---|
| `timestamp` | ISO 8601, when the request arrived |
| `session_id` | `x-claude-code-session-id`, copied from the request headers. Groups a session's calls without parsing bodies. Empty when the header is absent, since a non-Claude-Code caller has no reason to send it |
| `agent_id` | `x-claude-code-agent-id`. **Present only on requests from a subagent**, so an empty value means the main conversation — that emptiness is the signal, not missing data. Without this column a mixed-model session collapses into an indistinguishable pile of rows, and it is far cheaper to write now than to retrofit into a working CSV writer. See `docs/epd/EPD-001-model-selection-and-mixed-model-sessions.md` for why mixed-model sessions are expected at all |
| `backend` | `anthropic` or `lmstudio` |
| `model` | peeked from the request body |
| `path` | the request path, without the query string. Almost always `/v1/messages`, and that is the point: the catch-all route forwards endpoints we did not anticipate, and without this column those rows are indistinguishable from ordinary ones. Turns the plan's standing "other endpoints" worry into a list of facts |
| `stream` | boolean, peeked from the request body alongside `model` — it is already a routing-relevant field, so it costs nothing extra. Its real value is diagnosing the recorder rather than the call: empty token columns with `stream` true means the SSE scanner failed, empty with `stream` false means the non-streaming path failed. Two different bugs that are otherwise indistinguishable in the file. **An absent `stream` field is written as `false`**, because the API defaults it so and Claude Code omits it rather than sending it — reading absence as unknown left 83 of 142 rows blank on 2026-07-31 and made the diagnosis above impossible. An empty cell now means only that the body did not parse, or said something non-boolean |
| `input_tokens` | `usage.input_tokens`, tee'd from the response |
| `output_tokens` | `usage.output_tokens` (free alongside the above) |
| `cache_read_input_tokens` | `usage.cache_read_input_tokens`. Reported by both backends and free alongside the other two. It is here because prompt-cache behaviour is *why* the body is relayed byte for byte: without this column the project's most expensive constraint stays an assumption instead of a measurement. Empty when a backend omits it |
| `cache_creation_input_tokens` | `usage.cache_creation_input_tokens`, free alongside the read count. It is what makes the read count interpretable: without it a low `cache_read` cannot be told apart from a legitimate first write on a new prefix, which is the difference between "nothing is wrong" and "something upstream is rewriting our bytes". Empty when a backend omits it |
| `stop_reason` | from the final `message_delta`, or the top level of a non-streaming reply. `max_tokens` where `end_turn` was expected is truncation made visible — the exact failure the 34304-token context question worries about, which otherwise degrades answers without ever failing loudly |
| `request_bytes` | raw body length — always available, even when `usage` is not. Note it is dominated by the ~110 KB fixed preamble, so it is a weak proxy for conversation size; keep it as the fallback it is, not the comparison metric |
| `response_bytes` | bytes relayed downstream, counted on the tee that is there anyway. Unlike `request_bytes` it carries no fixed preamble, so it is a fair measure of how much came back — but it counts SSE framing as well as content, so treat it as a volume signal rather than a token proxy. Its steadiest use is the case `usage` doesn't cover: a reply that arrived empty or stopped early still leaves a number here |
| `ttfb_ms` | time to first byte of the response. The only column that captures the *felt* difference between backends: a local model that stalls for seconds and then streams quickly is a different experience from a cloud model that starts at once, and `duration_ms` averages that distinction away |
| `duration_ms` | wall time until the response *completes* (stream fully drained), not time-to-first-byte |
| `error_status` | how the call ended: `ok`, `http_error`, `stream_error`, `transport_error`, `client_disconnect`. Replaces an earlier `is_error` boolean, which could not express a client that disconnected mid-stream — neither a success nor a backend failure. Same width, and it makes the common failure modes countable with a spreadsheet filter instead of a judgement call |
| `error_code` | HTTP status, or a symbolic code for transport failures. `error_status` says what *kind* of failure it was, this says *which* one; both are empty when `error_status` is `ok` |
| `error_message` | short description, single line, no embedded newlines. Written as `type: message` when the backend's error body carried both — on an HTTP error `error_code` holds the status, so this column is the only place the symbolic type survives, and it is the countable half. Anthropic answers a rate-limited call with the bare word `Error`, which alone says nothing; the same call now reads `rate_limit_error: Error` |
| `router_version` | the router's own version. Measurements taken weeks apart across a changing router are otherwise hard to compare, and the cost is one short string per row |

A note on the cache column, since it is the one that needs justifying: LM Studio does real prefix caching, observed rising from 5 to 15 tokens across two runs of the same prompt (`docs/lmstudio-usage-check.md`). A cache-hit rate that collapses is the signal that something upstream has started rewriting request bytes — which is exactly the failure byte-relay exists to prevent, and is otherwise invisible.

Implementation constraints that fall out of this:

- **The two identifier columns come from headers, not the body.** Copying `x-claude-code-session-id` and `x-claude-code-agent-id` costs a dictionary lookup and needs no parsing, which is the whole reason they are affordable. `session_id` is measured — it is in the captured request, which is why `handoff.md` records redacting an `X-Claude-Code-Session-Id`. `agent_id` is documented only; the capture predates any subagent use here, so expect to confirm it arrives before trusting an empty column to mean "main conversation". Neither is a user identifier: an agent ID identifies a spawn, and subagent IDs are generated fresh each time.
- **Tee, don't parse-and-rebuild.** Relay response bytes downstream untouched while scanning a copy for `usage`. Byte-relay fidelity is preserved; observation is passive. If `usage` can't be found, write empty token columns rather than failing the request.
- **Take `input_tokens` from `message_start` and `output_tokens` from the final `message_delta`.** Verified against LM Studio 2026-07-29 (`docs/lmstudio-usage-check.md`); both backends carry usage in Anthropic's shape, so one rule covers both. Resist the obvious simplification: LM Studio repeats `input_tokens` in `message_delta`, so a scanner keyed on that event alone would look correct locally and silently record empty input counts for every Anthropic call. Non-streaming replies put `usage` at the top level instead, so that form needs its own path.
- **`stop_reason` shares the scanner with `usage`, and shares its trap.** It rides the final `message_delta` streaming and the top level otherwise, so it is nearly free once the usage scanner exists — but only if that scanner already handles both forms. Build them together rather than bolting one on afterwards.
- **`stream` and `response_bytes` are the recorder's own instruments.** Both are nearly free — `stream` is peeked for routing already, `response_bytes` is a counter on an existing tee — and both earn their place mainly by making a *failed* row interpretable. A row with no tokens is a dead end on its own; the same row saying which code path ran and how many bytes went past is a bug report.
- **Two clocks, not one.** `ttfb_ms` stops at the first response byte and `duration_ms` at the last. Start both when the request arrives, so the pair reads as "how long until it began" and "how long in total" rather than needing subtraction to interpret. Time to first byte is the more interesting of the two when comparing a local model against a cloud one.
- **Streaming hides errors behind a 200.** A streamed response returns HTTP 200 before content exists, so a backend failure can arrive as an SSE `error` event mid-stream. Error detection must watch the tee'd stream, not just the initial status code — that case is `error_status: stream_error`, and it is exactly why the boolean was not enough.
- **Never let telemetry break a call.** Any failure in logging or CSV writing is caught and dropped; the proxied request always wins.
- **The CSV is in completion order; sort before analysing.** A row is appended when its call finishes, while `timestamp` records when it *arrived*, so a slow call lands after quicker ones that started later — 14 adjacent pairs are out of order in the 2026-07-31 session. Deliberately not fixed: ordering the file would mean holding finished rows until the calls that started before them came back, which trades a spreadsheet sort for losing every buffered row when the process stops.
- **Both files timestamp in UTC, in the same format.** The log writes `2026-07-31T08:46:47.339+00:00`, character-for-character what the CSV's `timestamp` column holds, so a log line and its row merge-sort together. The log used to write naive local time, which meant correlating the two files — the whole reason uvicorn's lines share the router's log — required remembering an offset that appeared in neither.
- **Transport errors matter most here.** LM Studio simply not running is the common failure. That's a connection error with no HTTP status — `error_status: transport_error` with a symbolic `error_code`, rather than leaving both blank.
- **Don't store what a spreadsheet can derive.** Tokens per second is the headline comparison, and precisely for that reason it stays out of the file: a stored derivation can drift out of agreement with the columns it came from. Same for anything body-shaped — no prompts, no message counts, no tool names. Those are steps toward parsing what the router promised only to relay.
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
