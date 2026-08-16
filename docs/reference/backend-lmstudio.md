# LM Studio as a backend

What the local backend implements, what it accepts and then ignores, and the numbers that decide
whether a given model can be used at all.

LM Studio publishes **no feature-parity matrix** — its `/v1/messages` documentation does not spell out
`system`, `tool_result`, `thinking` blocks or images — so everything here was measured against a
running server rather than read. **Every answer expires with the next LM Studio release.** The
instrument is `../phase-4-probes/`, committed to be re-run.

**The slice every measurement below carries**, unless a line says otherwise: `qwen/qwen3.5-9b`
(MLX 4-bit) loaded at **44544 tokens** of context out of a 262144 maximum, on one machine, with
"Require Authentication" off. Measured 2026-08-06 (`../phase-4-notes.md`) and 2026-08-07
(`../phase-5-notes.md`). **The LM Studio version was not recorded at the time** — which is a gap in
the slice, given that these answers are expected to expire with a release. Numbers are dated and sliced here because they are part of the
finding; `measurements.md` is the register that carries each one's instrument and what it is for.

## The protocol surface

**No translation is needed.** LM Studio (0.4.1+) natively implements the Anthropic-compatible
`POST /v1/messages`, including the same SSE event sequence — `message_start` → `content_block_start` →
`content_block_delta` → `content_block_stop` → `message_delta` → `message_stop` — plus `tools` with
`input_schema` and `tool_choice`. It accepts both `x-api-key` and `Authorization: Bearer`. This is why
the router dispatches rather than translates; the argument is in `design-decisions.md`.

`usage` arrives in Anthropic's shape too, which is what lets one scanner serve both backends — with
one trap: LM Studio repeats `input_tokens` in `message_delta` where Anthropic does not. The procedure
that established this is `../lmstudio-usage-check.md`.

**Only `/v1/messages` exists under the Anthropic-compat namespace.** There is no `/v1/models` there,
and `POST /v1/messages/count_tokens` is answered with HTTP 200 and an error body rather than a count
(`../epd/EPD-002-token-counting-for-local-backends.md`). To enumerate local models, use LM Studio's
native `GET /api/v1/models` or its OpenAI-compat `GET /v1/models`; the currently loaded model is the
entry with a non-empty `loaded_instances`.

**Read the loaded window from `loaded_instances[].config.context_length`, not from
`max_context_length`.** On this machine those differ by 262144 against 44544 — the model's ceiling
versus what it was actually loaded with — and only the second one governs whether a request fits.

## What it accepts, and what it honours

**Nothing was rejected.** Every shape sent came back HTTP 200 with no error body, including the ones
the project predicted would fail. The gaps that exist are quieter than a rejection: things accepted
and then not honoured. A status code is not a verdict here — `count_tokens` answers 200 with an error
body — so the probes look for an error shape regardless of status, and none of these tripped it.

| Shape sent | Accepted | Honoured | Note |
|---|---|---|---|
| `role: "system"` message inside `messages` | **yes** | **yes** | Answered in French as the system message instructed |
| Image content block, base64 PNG | **yes** | **yes** | Named four quadrant colours in the order asked |
| `thinking: {"type": "adaptive"}` | **yes** | **yes** | Real `thinking` content blocks, Anthropic's shape |
| `thinking: {"type": "enabled", "budget_tokens": 1024}` | **yes** | **no** | The budget is ignored — see below |
| `output_config: {"effort": "high"}` | **yes** | **yes, invisibly** | Billed and never shown — see below |
| `context_management` (`clear_thinking_20251015`) | **yes** | not observable | No effect a probe can see; nothing broke |
| `metadata.user_id` | **yes** | not observable | Ignored quietly |
| `cache_control: ephemeral, 1h` | **yes** | **not on a small prefix** | Two identical 117-token runs, `cache_read` 0 both times |
| The ten-entry `anthropic-beta` header | **yes** | n/a | Sent on every probe, never objected to |

**And the whole real request works.** The captured Claude Code request
(`../log-the-whole-request.txt`) — 27 tool schemas, a system-role message, two `cache_control`
markers, `context_management`, `output_config`, `metadata`, `thinking`, and the ten-entry
`anthropic-beta` header — replays against a local model unmodified and answers correctly. There was
nothing to bisect.

One caveat on that replay: `probe.py` parses and re-serializes the captured body, so the bytes on the
wire differ from the captured ones by JSON separator spacing (119797 against 118004). It proves the
*shape* is accepted. That Claude Code's own bytes survive is a different claim, carried by the 24
cache-hit rows in `../phase-2-step-6-session/calls.csv` from real traffic.

### `thinking` is unbounded

LM Studio emits real `thinking` content blocks with `thinking_delta`s, followed by a `text` block.
**Nothing bounds them.** `budget_tokens: 1024` with `max_tokens: 2048` produced 2047 tokens of
thinking and no text at all; `{"type": "adaptive"}` with `max_tokens: 1024` did the same at 1023. The
model thinks until the *overall* budget runs out, and only what is left becomes an answer.

**The consequence:** a request asking for thinking with a small `max_tokens` returns **an empty
reply** — HTTP 200, zero content blocks, `stop_reason: max_tokens`. Not an error; a well-formed
message containing nothing. Claude Code sends `max_tokens: 64000` and has room. Anything more frugal
does not.

### `output_config: {"effort": "high"}` is billed but never shown

Controlled against a baseline differing only in this field, same prompt and same `max_tokens`:

| | `output_tokens` | blocks returned | text |
|---|---|---|---|
| baseline, twice | **4** | `text` | `PROBE OK` |
| `effort: high`, `max_tokens: 128` | **127** | **none** | *(empty)* |
| `effort: high`, `max_tokens: 2048` | **216** | `text` | `\n\nPROBE OK` |

The field switches reasoning **on** — the baseline plainly does none — and because `thinking` was not
also set, that reasoning is never emitted as a content block. It is still counted: 216 output tokens
for a four-token answer, ~98% invisible. The leading `\n\n` is the residue where the stripped
reasoning was.

Two things follow. **Every Claude Code request carries `output_config`**, so every local call pays for
hidden reasoning it does not display. And the middle row above is a `max_tokens` stop with output
tokens and nothing to show for it — **the same CSV signature as a prompt-cache warmup probe**, so the
two cannot be told apart in `calls.csv`.

## Prefix caching

**It is real and it works at scale**, and it is why the router relays request bytes untouched — the
reasoning is in `design-decisions.md`.

The same captured request sent twice:

| | first run | second run |
|---|---|---|
| `input_tokens` | 27924 | 27924 |
| `cache_read_input_tokens` | 0 | **27904** |
| time to first byte | 196789 ms | **49629 ms** |

99.93% of the prefix served from cache, and time to first byte four times lower — worth about **147
seconds of prefill per turn** on a one-word conversation, and more on a real one. A 99.93% hit still
cost 50 seconds, so cache reads are much cheaper than prefill here, not free.

**There is a floor.** Two identical 117-token runs with an `ephemeral`/`1h` marked system block read
`cache_read_input_tokens: 0` both times. The marker is accepted and does nothing at probe scale.
Anyone measuring caching with a small request will conclude it is broken. Real traffic is where it
shows: 24 rows in `../phase-2-step-6-session/calls.csv` carry a non-zero `cache_read`, the largest
40879.

## Context: what fits, and what it costs in time

**The fixed preamble is 27924 tokens** — measured by replaying the captured request, not estimated
from its 118 KB of JSON. Against a 44544-token window that is **63% of the context gone before the
user types anything**. LM Studio's own guidance of ">~25k context" is therefore optimistic: a usable
model needs meaningfully more headroom than the preamble alone.

**Above the window, requests are refused — not trimmed.** A request whose input exceeds the loaded
window comes back in under a second (908 ms, without paying for the prefill it could not fit):

```
{"type": "error", "error": {"type": "api_error", "message":
 "The number of tokens to keep from the initial prompt is greater than the context length.
  Try to load the model with a larger context length, or provide a shorter input"}}
```

The router records this as `error_status: stream_error`, `error_code: api_error`.

**Below the window, nothing is dropped either.** A prompt of **41595 tokens against the 44544 window —
93% full** — returned a codeword planted at its very front, with `input_tokens` matching what was
sent rather than a trimmed remainder. So silent trimming is ruled out at both ends: refused above,
answered in full below.

**But the refusal arrives in a form Claude Code is known not to read.** It is an SSE `error` event
inside an HTTP 200, and the client prints its own generic
`API returned an empty or malformed response (HTTP 200)` instead. LM Studio's single most actionable
message — it names the cause and both fixes — is very likely invisible to the harness. Not fully
settled: the case measured against Claude Code had an error event arriving *after* partial content,
where this one is the sole event in the stream with no `message_start` before it, and whether the
client treats those alike is unknown.

**The practical limit is time, not the window.** Prefill on this model, all cold unless marked:

| input tokens | time to first byte |
|---|---|
| 9166 | 115073 ms |
| 27924 | 196789 ms (49629 ms on a cache hit) |
| 41595 | 461712 ms |
| ~41000 | never — killed at 600247 ms by a 600 s read timeout |

The last two rows are the same size and the same machine on different days: **a spread of at least 30%
straddling what used to be a hard-coded ceiling.** Two points do not establish a curve and the middle
row is faster per token than the first, which warmup may explain — but the shape is not in doubt, and
a model loaded near 44544 needs the timeout below to reach the top of its own window.

**`max_tokens: 1` warmup probes are full prefills.** Claude Code sends them to create a cache entry;
against Anthropic they are nearly free, and against LM Studio each one pays for the whole prompt and
returns `content: []`, `output_tokens: 0`, `stop_reason: max_tokens`. In the frozen session that was
40 calls and **20.0 of 45.5 minutes — 44% of all local wall-clock time**, one of them 111 seconds for
a 31 KB body. Nothing is currently done about it; the trade is recorded in `design-decisions.md`.

**The context length cannot be changed from the CLI.** `lms load -c 8192` and `--context-length 8192`
are both silently ignored — the saved per-model configuration wins and the model reloads at its
configured size, with `lms ps` and the REST API agreeing afterwards. Only the GUI changes it, so
anything needing a specific window needs a person.

## Timeouts

`read_timeout` is per backend: **1800 s for LM Studio**, 600 for Anthropic, defaulting to 600.
LM Studio gets the larger number because **prefill is silent while it works**, and silence is the only
thing this timeout measures.

**`read` bounds the longest permitted silence between two reads, never the duration of a call.** Every
chunk that arrives restarts the clock — a backend dripping one chunk per second ran for three times
its read timeout and completed. Two consequences worth keeping straight: a silent prefill hits the
timeout and a slow stream does not; and a backend dribbling one byte just under the limit runs
forever, so this number has never bounded how long a call can take. `connect` stays short and shared,
because a backend that cannot be *reached* must still fail fast — the common LM Studio failure is that
it is not running at all.

**To reproduce the timeout failure cheaply**, lower the config rather than sending a bigger request:
at `read_timeout: 30` the same needle dies at 30343 ms with `transport_error` / `read_timeout` and no
first byte — the same signature the 600 s ceiling produced, in thirty seconds instead of ten minutes.

## Authentication

LM Studio has a **"Require Authentication"** setting, off by default on this machine and switched on
and off during measurement. With it on, an unauthenticated `GET /api/v1/models` answers **401
`invalid_api_key`**, and a `/v1/messages` call whose credential was stripped answers **401
`authentication_error`** with the message `An LM Studio API token is required…`.

To serve an authenticated LM Studio, the backend needs **two** lines — `credential: inject` **and**
`api_key_env: LMSTUDIO_API_KEY`, with the key in `.env`. Naming the variable without the mode is
refused at startup. Verified live: `inject` returned HTTP 200 with the caller's own token replaced,
against a `strip` control at the same moment that returned 401. The modes themselves are in
`design-decisions.md`.

`inject` sends `Authorization: Bearer`, which is what LM Studio wants. The header name is not yet
configurable per backend.

## What this does not cover

- **One model at one window size.** Everything above is `qwen/qwen3.5-9b` at 44544 tokens.
  `capabilities` in `GET /api/v1/models` varies per model — several have no `vision`, several no
  `reasoning` — so no row of the honoured/ignored table transfers without re-running the probes.
- **Streaming only.** Every probe ran streamed. `probe.py --no-stream` exists and has not been used;
  the recorder takes a different path for buffered replies, and LM Studio reports `usage` differently
  there.
- **Whether the context refusal ever reaches the user.** Open, above.

What has been driven end to end, for what it is worth beyond the probes: a real coding session on
`google/gemma-4-e4b` at a 34304-token window — reading and writing files, running bash commands,
running a Python script and reading its stdout — with multi-turn conversation holding together. It
worked because it fit.
