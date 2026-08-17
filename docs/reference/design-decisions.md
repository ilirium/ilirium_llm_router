# Design decisions

Decided deliberately; don't quietly reverse these. Each statement is kept with the reasoning that
produced it, because the reasoning is what a later argument has to answer — three of the four EPDs
argue with this file, and none of them is answerable from a one-line statement.

`CLAUDE.md` carries a titles-only index of this file. An accepted EPD graduates in here.

## Routing is a prefix rule in code, not a config table

`model` starting with `claude-` → Anthropic; everything else → LM Studio. No per-model YAML. New
Anthropic and local models work without touching config. YAML holds backend definitions (base URLs,
which env var carries the key), not a model list.

## No special case for background or auxiliary traffic

Whatever `model` Claude Code sends gets routed by the same rule, including the small/fast model used
for background calls. Consequence to keep in mind: a `claude-`prefixed background call leaves the
machine and costs money even when the main model is local.

**Measured 2026-07-31, and the cost is worse than this decision anticipated.** The expensive case is
not money on cloud calls — it is *minutes* on local ones. Claude Code sends **prompt-cache warmup
probes**: `max_tokens: 1` requests whose only purpose is to create a cache entry. Against Anthropic
they are nearly free. Against LM Studio each one is a full prefill that returns nothing — reproduced
directly, `content: []`, `output_tokens: 0`, `stop_reason: max_tokens`.

In the step 6 session that was **40 calls and 20.0 of 45.6 minutes — 44% of all local wall-clock time
— spent on requests that returned zero content tokens.** The longest took **111559 ms for a body of
1960 bytes**, so the cost is not proportional to what the probe carries. They are visible in the
frozen `calls.csv` as rows with `stop_reason: max_tokens` and `output_tokens: 0`.

> Two numbers in that paragraph are corrected from what `CLAUDE.md` said, both on 2026-08-16 while
> assembling `measurements.md`. It read "20.0 of 45.5 minutes" and "One took 111 seconds for a 31 KB
> body" — the latter pairing the longest probe with a different probe's size. The 31786-byte one took
> 103395 ms. The correction strengthens the argument rather than weakening it.

This is not a bug and nothing is currently done about it. It is recorded here because it is the
strongest argument yet for revisiting the decision — a routing exception for `max_tokens: 1` probes on
local backends would return nearly half the wall clock, at the price of the first special case in the
dispatch rule.

## Relay the body, log only metadata

Forward the request body byte-for-byte and stream the response through without re-encoding; peek at
`model` for routing only. Log model, backend, status, and duration — never deserialize or re-serialize
the payload. This keeps the proxy correct when either side adds fields, which is the main risk of a
parse-and-rebuild design.

**Measured end to end on 2026-08-06, so this is no longer an argument.** The same captured request
replayed twice against a local model returned `cache_read_input_tokens` of 27904 out of 27924 on the
second run, cutting time to first byte from 196789 ms to 49629 ms. A cache hit of that size is only
possible because the router changed none of the bytes — reserialization, "even key reordering that
means the same thing", would have broken the prefix match. Locally that is worth about 147 seconds of
prefill per turn on a one-word conversation.

Two EPDs argue this rule is narrower than it looks — that it protects bodies the router *relays*, and
so does not reach a body the router answers itself (`EPD-002`) or an opaque copy it never parses
(`EPD-003`).

**`EPD-003`'s version was accepted on 2026-08-17** and is the next section. It does not weaken this
rule: an archived copy is taken *off the bytes already in memory*, and what gets forwarded is
unchanged, so the prompt-cache prefix this rule exists to protect is untouched. **`EPD-002`'s has
not been accepted.** *(This paragraph read "Neither has been accepted" until then.)*

## Bodies are archived as content-addressed per-call files, compressed against a shared dictionary

**Decided 2026-08-17**, graduating `../epd/EPD-003-capturing-bodies-for-a-corpus.md`. Two halves, one
settled by a person and one by measurement.

**The corpus is for analysis, not fine-tuning.** Anthropic's terms prohibit using outputs as training
targets, and a corpus captured here is mixed. Dropping fine-tuning makes the Anthropic/LM Studio
partition **optional rather than structural** — `backend` is already a CSV column, so any export can
still filter on it. The analysis half was never restricted and is the stronger half of the
requirement.

**The storage unit is the per-call file, and the gate that could have refuted it ran.** Measured
2026-08-17 over 73 real bodies, evaluated on a **held-out session** — split by session rather than
shuffled, because within a session an earlier body is nearly a prefix of a later one:

| | Ratio |
|---|---:|
| per-file, no dictionary | **3.12x** |
| per-file, dictionary trained on *other* sessions | **12.10x** |
| one long-window stream | **29.91x** |

`EPD-003` set the test itself — near the stream figure and the sketch survives, near 3x and per-call
files are the wrong unit. **12.10x is four times the failure threshold**, closing 82.8% of the byte
gap and leaving per-file storage at **2.47x** a stream rather than 9.6x. On its own projection, ~3 GB
a year naive becomes ~250 MB rather than ~100 MB — both inside the "low hundreds of megabytes" its
conclusion rested on, so the residual does not change what the number was for. What per-call buys in
exchange is what `EPD-003` says per-session is far worse at: random access, partial writes, and a
process that stops mid-session.

**Store bytes, parse never.** The corpus holds opaque blobs; any parsing is an offline export step
against a file, never on the request path and never in the router process. This is what keeps the
reversal to one sentence of `observability.md` rather than to the whole rule.

**Three consequences that are not obvious, all measured or found while measuring:**

- **A trained dictionary is as sensitive as the bodies.** `zstd --train` output is a concatenation of
  verbatim substrings of its samples. It is not a derived artefact and **it is not committable**.
- **A dictionary must never be deleted.** A frame compressed with `-D` cannot be decompressed without
  it. Blobs may be pruned freely; dictionaries are append-only forever, at ~110–200 KB each.
- **Retraining must be measured, not assumed.** `zstd --train` was **non-monotonic** at 68 samples —
  a larger budget produced a *worse* dictionary. A retraining policy that adopts a new dictionary
  without comparing it against the one it replaces will silently make the corpus bigger.

**Not decided here, and left to Phase 10 as design detail:** what is captured by default, opt-in
versus always-on, retention, and whether headers are stored — `EPD-003`'s open questions 3–6. None of
them changes the storage unit.

**One correction this carries into Phase 10.** `EPD-003` proposed adding two ref columns to
`calls.csv` so it becomes the corpus's join table. **It cannot be**: `config.yaml` sets
`backup_count: 10`, so the CSV is a capped rolling window that discards its oldest segment and the
bodies would outlive their own index. Size rotation is correct for what that file is *for* — model and
backend comparison, a recent-window question — so the corpus carries its own durable index instead,
and `calls.csv` is not changed.

## One exception to byte-relay: a broken stream is ended with an SSE `error` event

Decided 2026-07-31. A streamed reply returns HTTP 200 before any content exists, so when the relay
breaks afterwards the failure cannot go in a status code — and a stream that simply stops is
indistinguishable from a model that finished talking. The router appends one Anthropic-shaped `error`
event to such a stream, which is the only place it writes bytes of its own into a relayed reply.

Three limits keep this from becoming a parse-and-rebuild wedge: it is **appended, never altering**
(every backend byte still goes out untouched, and the prompt-cache argument is about *request* bytes
regardless); it happens **only on SSE replies**, since the same frame stapled to a half-written JSON
object is corruption rather than a message; and the injected bytes are **not counted in
`response_bytes` and not fed to the scanner**, because both measure what the backend sent.

**Measured the same day, and it buys nothing for Claude Code.** Against a stand-in backend that sends
a complete `message_start`, a text block, seven deltas and then resets, Claude Code reports `API
returned an empty or malformed response (HTTP 200)` — its own generic wording, not ours. The
comparison that makes this conclusive: on a 502 it prints the router's message *verbatim*, so it
surfaces backend wording when it recognises an error. It does not recognise a mid-stream `error`
event; it is reporting the missing `message_stop`, which is what it would say if nothing were injected
at all.

**Kept anyway, deliberately.** The event is Anthropic's documented shape, the cost is about fifteen
lines behind one test, and the harnesses this project plans to support are not this one. But it is a
feature with **no measured consumer**, and this paragraph exists so nobody later mistakes it for
something that solved a visible problem. If a second client also ignores it, delete it.

There is a second consumer question underneath it, still open: LM Studio's over-window refusal arrives
in exactly this shape — an SSE `error` event inside an HTTP 200 — and is therefore likely invisible
too. That case differs in one way that may matter and has not been tested: it is the *sole* event in
the stream, with no `message_start` before it.

## Backend authentication is a first-class feature, not a leftover

Every backend declares how its credential is obtained, and the router is expected to hold keys for
some of them. Settled on 2026-07-29, reversing an earlier framing in which `api_key_env` was an
untested extra to consider deleting. Two reasons: LM Studio's "Require Authentication" is a setting
this machine actually uses and intends to keep using, and the planned expansion — other local runners,
other cloud APIs — makes "the router holds no secret" false as a general rule. It stays true only of
Anthropic, which is one backend's property rather than the architecture's.

**The shape: one field, three modes.** `credential:` is the only knob, and `api_key_env` is required
by `inject` and forbidden by the others.

| Mode | Meaning |
|---|---|
| `forward` | pass the caller's credential through untouched (Anthropic) |
| `strip` | remove it — a local server has no use for a real token and might log it |
| `inject` | remove it and send the key named by `api_key_env` instead |

This replaces a two-knob shape in which `credential` and `api_key_env` were independent and the key
silently won, so `credential: forward` alongside a key read as "forward the caller's token" and did
not do that. With one backend needing auth that was a wart; with several it is a trap.

**Contradictions are startup errors, not silent behaviour.** `inject` without `api_key_env`, and
`api_key_env` without `inject`, are both refused. So is an environment variable that is unset or
empty. Each message must say what is wrong *and* how to fix it, then exit — matching how the rest of
config loading already behaves. A backend that authenticates with nothing, or a key that looks
configured and is never sent, are exactly the failures that surface as a confusing 401 much later.

**Implemented on 2026-08-07**, and `inject` has carried a live request against an LM Studio requiring
authentication. The mode is the only thing consulted at request time, so the ambiguity is
unrepresentable rather than discouraged. Writing it revealed the same ambiguity in two more places
than the known one in `proxy.py`: `api_keys()` collected a key for any backend naming a variable, and
`cli.py` *displayed* injection whenever a key existed — so `--check` would have reported a forwarding
backend as injecting.

The header question remains open and deliberately unanswered: `inject` means `Authorization: Bearer`,
which suits LM Studio and OpenAI, but Anthropic's native key is `x-api-key` and Gemini's is
`x-goog-api-key`. A per-backend header name will be needed before the second cloud provider, not
before.

---

## Decisions that live in another file, and why

Three things a reader might expect here are deliberately elsewhere, each because it has one obvious
trigger that is not "I am reversing a decision".

| Decision | Home | Why there |
|---|---|---|
| `read_timeout` per backend, and what `read` actually bounds | `backend-lmstudio.md` | It is a property of the backend it exists for; the number matters when you are working on that backend |
| "Never let telemetry break a call", "don't store what a spreadsheet can derive" | `observability.md` | They are constraints on the recorder, read by whoever touches it |
| The formatter's pinned version and line length | `CLAUDE.md`, "Layout and commands" | Every session runs `make format`; a pointer would not be read in time |

## Discharged

**"First milestone is a minimal end-to-end proxy"** — uv project, FastAPI, `POST /v1/messages`
dispatching to both backends with streaming, verified by pointing Claude Code at it. Taken as a
decision, and **done**: Milestone 1 closed on 2026-08-07. It is recorded here rather than dropped,
because a decision that disappears looks like one that was reversed. What it deferred — a merged
`/v1/models` list and config polish — is in `../backlog.md`.

---

**The numbers quoted above have their canonical rows, with dates, instruments and slices, in
`measurements.md`. The episodes that produced the corrections are in `lessons.md`.**
