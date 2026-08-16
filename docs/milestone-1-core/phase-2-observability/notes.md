# Phase 2 notes — logging and per-call statistics

Written 2026-07-30, **before any code**, so that a fresh session can pick the work up without the
conversation that produced the plan. The design is agreed; the implementation is not started.

Companion to `phase-1-notes.md`, which records decisions taken *while* writing the proxy. Add to
this file as Phase 2 is built, especially where reality disagrees with what is written below.

Branch: `feat/phase-2-observability`, off `main` at `8d335ab`. Merge back with `--no-ff` — phase
boundaries stay visible in the log.

## What Phase 2 must produce

Every call leaves two traces: a human-readable line in a rotating log, and one CSV row that can be
opened in a spreadsheet and compared across models. The columns and their justifications are in
`CLAUDE.md` under "Observability: log + CSV stats"; the phase's own description is Phase 2 of
`implementation-plan.md`. **Neither is restated here** — read them, and treat this file as the
implementation plan that sits under them.

The 20 columns, in order, for quick reference only:

`timestamp` `session_id` `agent_id` `backend` `model` `path` `stream` `input_tokens`
`output_tokens` `cache_read_input_tokens` `cache_creation_input_tokens` `stop_reason`
`request_bytes` `response_bytes` `ttfb_ms` `duration_ms` `error_status` `error_code`
`error_message` `router_version`

## Shape of the code

| File | State | Job |
|---|---|---|
| `logging_setup.py` | stub | Configure a `RotatingFileHandler` from `config.logging`; one logger named for the package |
| `stats.py` | stub | `StatsWriter` owning the CSV: one row per call, size-based rotation, header re-emitted after each rollover |
| `observe.py` | **new** | The tee and the two scanners. Kept out of `proxy.py` so the forwarding path stays readable |
| `proxy.py` | exists | `relay` wraps the response iterator; the existing transport-error branch gains a row |
| `cli.py` | exists | Calls `logging_setup` at startup |
| `config.py` | **done already** | `Logging` and `Stats` models exist with the right fields, and `resolve_paths` already makes both absolute against the config file's directory. Phase 2 needs no config change |

`logging_setup` is called from `cli.py` rather than `create_app`, so tests are not forced to touch
global logging state. The stats writer is owned by the app, so a test can point it at a temporary
path.

## Decisions taken on 2026-07-30, before implementation

Approved in conversation. Each was a real fork, not a formality.

### 1. Non-streaming replies are buffered to a 1 MiB cap

`usage` in a non-streaming reply sits inside one JSON object, and an object's contents are unknown
until its closing brace. So the "do not buffer the whole reply" constraint cannot hold literally for
that path. Options considered:

| Approach | Why not |
|---|---|
| Tail buffer, keep the last ~8 KB | **Bets on field order.** Works only because Anthropic happens to emit `usage` last. JSON guarantees no ordering and LM Studio is a separate implementation, so this looks correct today and goes silently empty the day either side reorders. Same species of mistake as the `message_delta` trap below |
| Incremental JSON parser | A dependency, or a hand-written parser, against the stated non-negotiable of simple, human-readable code |
| Don't scan non-streaming at all | Throws away the numbers for a call shape Claude Code actually uses |

Chosen: accumulate up to **1 MiB**, parse once at the end, give up beyond it.

Why a cap exists at all is *not* about Anthropic's replies — it is about **the catch-all route**.
`anything_else` forwards any path, so the reply to an unanticipated endpoint could be anything at
all. The cap turns "memory decided by an endpoint nobody has enumerated" into a known ceiling.

Why 1 MiB: 64k output tokens at roughly 4 bytes each is about 256 KB, plus JSON overhead, thinking
blocks and tool-use inputs — so roughly four times the worst realistic reply. The comparative
argument is stronger: `proxy.py` already does `body = await request.body()`, so the router **already
holds the whole request in memory**, and the captured request is 118 KB. A 1 MiB response ceiling is
the same order as what Phase 1 already accepted.

At the cap: stop accumulating, write the row with empty token and `stop_reason` columns.
`response_bytes` is a counter, so it stays accurate regardless. **The relay is never affected** —
bytes go downstream as they arrive whether or not the scanner is still listening. The cap can cost
observation, never fidelity.

Not a YAML setting. It is a number nobody will tune, and simple configuration is a stated
non-negotiable. A module constant in the style of `TIMEOUT`, with the reasoning in its comment.

### 2. The `model`-less 400 gets a row too

`Proxy.messages` refuses a body with no `model` before any backend is chosen. That row is written
with `backend` empty and `error_status: http_error`. It never reached a backend, but it is a call
the router refused, and a silent gap in the file is worse than a row with blanks.

### 3. `ttfb_ms` is measured at the first byte of the body

Not at the response headers. Headers arrive as soon as the backend accepts the request, which for a
streaming reply says nothing about when the model started producing — which is the entire number
being asked for.

## Decisions taken while building

Added as the phase was built, in the spirit of the note at the top of this file.

### 4. The log goes to the console as well as the file (step 1)

Not just the file. A router started in a terminal that prints nothing looks broken, and the failure
this project expects most — LM Studio not running — should not need a second window to notice. Both
handlers carry the same format, and `logging.level` governs both; there is no second knob.

### 5. Uvicorn's logs join the router's file (step 1)

Settled, having been listed as open. They go into the same file rather than staying on the console.
When a call went wrong, *did the request arrive* and *was the server still up* are answered by the
lines either side of it, and lines can only sit either side of each other in one file.

Mechanically this is two pieces that must stay together: `setup_logging` attaches its handlers to
the `uvicorn` logger (parent of `uvicorn.error` and `uvicorn.access`), **and** `cli.py` starts
uvicorn with `log_config=None`. Left to itself uvicorn replaces those handlers and sets
`propagate = False` on the children, and its lines never reach the file. Changing one without the
other silently loses the access log.

The handler *objects* are shared between the two loggers rather than built twice. Two
`RotatingFileHandler`s open on one file would each keep their own size count and roll over on top of
each other's rename.

Verified against a live server, not just unit tests — startup, `Uvicorn running on…`, the access
line for Claude Code's `HEAD /` probe, and the full shutdown sequence all land in `router.log`.

### 6. Two defects found by writing step 1's tests

Both were in code that already looked finished, and neither would have raised:

- **Milliseconds were being discarded.** A `datefmt` of our own overrode the default `asctime`
  format, so lines read `17:31:13` while the comment above them promised otherwise. In the phase
  whose subject is `ttfb_ms` and `duration_ms`, the router's own log was rounding to the second.
- **An unusable log path crashed with a traceback.** `mkdir` and the handler open were unguarded.
  Now a `ConfigError`, matching how every other startup problem behaves. Note this is the *opposite*
  of the rule that governs logging while serving: nothing is being proxied yet, and a log that
  silently goes nowhere is worse than a refusal to start.

### 7. The SSE scanner flushes its last line at `finish` (step 3)

Found by a test written on a wrong premise, which is the best kind. The line buffer holds back the
tail after the last newline, waiting for the next chunk — correct while bytes are still arriving,
and wrong at the end. A backend that stops after the closing brace rather than sending a final blank
line would have left that line unread.

It matters more than it sounds: the line held back is the *last* one, which is exactly where
`output_tokens` and `stop_reason` live. The failure would have been a stream that looks perfectly
healthy and records its two most interesting numbers as empty, only against backends that frame
their last event that way. `SseScanner._finish` now reads the leftover.

### 8. Events are recognised by the JSON's `type`, not the `event:` line (step 3)

Anthropic sends both — `event: message_start` above `data: {"type":"message_start",…}`. Reading the
`type` inside the document means one line to look at instead of two to pair up across chunk
boundaries, and it does not assume both backends frame their event lines identically. LM Studio is a
separate implementation, and the SSE spec does not require an `event:` line at all.

### 9. Transport error codes are derived from the httpx exception class (step 4)

Settled, having been listed as open. `transport_error_code` snake-cases the exception's class name:
`ConnectError` → `connect_error`, `RemoteProtocolError` → `remote_protocol_error`, `PoolTimeout` →
`pool_timeout`. Derived rather than tabulated, so httpx's whole family is covered today and one it
adds later still lands as something readable instead of collapsing into a catch-all.

LM Studio not running is the common failure and it is a `ConnectError` with no status code at all,
which is why leaving `error_code` blank was never an option.

### 10. `peek_model` becomes `peek`, returning model *and* stream (step 4)

One `json.loads` of a 118 KB body instead of two. `stream` was always meant to be "free alongside
`model`", and calling a second peeking function would have quietly made it not free.

### 11. `client_disconnect` is tested by driving the generator directly (step 4)

There is no way to provoke it through `TestClient`: a request there always reads its reply to the
end, so the caller can never be the one who stops listening. The test builds the `watch` generator,
pulls one chunk, and calls `aclose()` — which throws `GeneratorExit` in at the yield, the same thing
starlette does when a connection drops.

Worth knowing this is the *least* verified of the five statuses. The unit test proves the branch
does what it says; whether starlette reliably lands there for a real dropped connection is a step 6
question.

### 12. Shared test scaffolding moved to `conftest.py` (step 4)

`test_proxy.py` (what the router forwards) and `test_recording.py` (what it writes down about the
forwarding) describe the same call from two angles, and neither should own the stand-in backend both
need. `Rows` — a `StatsWriter` stand-in that keeps records in a list — lives there too, because
these tests are about what the router *decided* to record; `test_stats.py` already covers how a row
reaches disk.

### 13. Step 5 is a gap audit, not a second copy of step 4's tests (step 5)

`test_recording.py` already goes through the app, so writing "integration tests" from scratch would
have produced a parallel set asserting the same things against the same stand-in. What it could not
cover is anything involving a *real file*, so `test_integration.py` is scoped to exactly that: the
config → app → writer → disk wiring, rotation under traffic, concurrent calls, and a file that
breaks after startup rather than at open.

Two gaps found by looking rather than by writing more of the same:

- **The mid-stream transport failure was untested.** `proxy.py` has two `except httpx.HTTPError`
  branches — the `send()` that never connects, and the one that breaks *while relaying*. Only the
  first had a test. The second is the more interesting one, because the 200 status line has already
  gone out and the row is the only place the failure is visible at all.
- **Nothing used the real `StatsWriter` through the app.** Every recording test used the `Rows`
  stand-in, so the wiring in `create_app` was carried entirely by the manual live check.

### 14. Two traps in the test scaffolding itself (step 5)

Both were mine, and both are the kind that make a test quieter than it looks:

- **A streamed `httpx.Response` can only be consumed once.** The `Upstream` stand-in hands out one
  response object, which is invisible while every test makes a single call and fails immediately on
  the second. `test_integration.py` builds a fresh reply per request instead.
- **A mock backend answers instantly, so "concurrent" calls are not concurrent.** The first version
  of the interleaving test passed without ever putting two writes near each other. It now holds each
  reply open for 20 ms between chunks, which makes 60 calls across 12 threads genuinely overlap —
  visible in the timing: serialized they would take 1.2 s, and the whole file runs in under 0.3 s.

## The scanner

**Which path runs is decided by the response `content-type`**, not by the request's `stream` flag:
`text/event-stream` means SSE, anything else means the buffered path. The content-type describes
what the bytes *are*; the request flag describes what was *asked for*.

Bonus from keeping them separate: `stream` is its own CSV column, so a row with `stream` true that
was scanned by the buffered path is a visible disagreement between the two — worth knowing, and
invisible if one signal drove both.

**SSE path.** Keep a small line buffer and discard as you go; every `data:` line is a complete JSON
document on its own, so memory stays constant however long the model talks.

- `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` from **`message_start`**
- `output_tokens` and `stop_reason` from the **final `message_delta`**
- an `event: error` sets `error_status: stream_error`

**The trap, verified 2026-07-29 (`lmstudio-usage-check.md`):** LM Studio repeats `input_tokens` in
`message_delta`; Anthropic does not. A scanner keyed on `message_delta` alone would look correct
against the local backend and silently record empty input counts for **every** Anthropic call.

**Buffered path.** Accumulate to the cap, `json.loads` once, read `usage` and `stop_reason` from the
top level.

`stop_reason` rides the same two places as `usage`, so it is free *only if* both forms are handled.
Build them together rather than bolting one on afterwards.

## The CSV writer

Rotation is built on `logging.handlers.RotatingFileHandler` rather than a hand-rolled rename dance:
`max_bytes`/`backup_count` map 1:1 onto `maxBytes`/`backupCount`, it is battle-tested, and its lock
satisfies the "rows must not interleave into corrupted lines" constraint for free. The single
override is `doRollover`, to re-emit the header row into the fresh file — without it, rotated
segments cannot be parsed standalone.

Rows go through `csv.writer` rather than manual joining. Model IDs like `google/gemma-4-e4b` are
harmless, but `error_message` is free text and must stay on one line with no embedded newlines.

## Build order

Each step is verifiable on its own.

1. `logging_setup.py` and the `cli.py` wiring — smallest piece, proves the config plumbing.
2. `stats.py`: the writer and rotation. Tests for header re-emission after rollover and for escaping.
3. The scanners, tested against captured SSE shapes, including the `message_delta` trap and the
   non-streaming form.
4. The tee in `relay`; the transport-error row and the client-disconnect row.
5. Integration tests through the app. Prove "never let telemetry break a call" with a writer that
   raises.
6. **Run a real session and read the CSV.** The only step that confirms anything about the world.

## Constraints that must not be broken

Restated because they are the ones a plausible-looking implementation quietly violates:

- **Telemetry never breaks a call.** Any failure in logging or CSV writing is caught and dropped.
  The proxied request always wins, including when the disk is full.
- **The body is never logged.** It carries the whole conversation, and on the cloud side it arrives
  alongside a real credential.
- **Nothing derived, nothing body-shaped.** Tokens per second belongs in the spreadsheet, where it
  cannot drift out of agreement with the columns it came from.
- **Tee, don't parse-and-rebuild.** Observation stays passive; the bytes going downstream are the
  bytes that arrived.
- **A streamed response returns HTTP 200 before content exists**, so error detection must watch the
  tee'd stream, not just the initial status code.

## Still open

Nothing. Both questions this section held were settled by step 6 on 2026-07-31 — see below.

Two things the session raised that are *not* Phase 2's to answer, recorded so they are not lost:

- **Claude Code's context accounting for local models is an estimate against an assumed 200k
  window.** LM Studio does not implement `count_tokens` and answers HTTP 200 with an error body.
  Harmless on a large-context model, silent truncation on a small one. Written up as
  `docs/epd/EPD-002-token-counting-for-local-backends.md`; no decision taken.
- **Prompt-cache warmup probes cost 44% of local wall-clock time** — 40 calls returning zero content
  tokens, 20.0 of 45.5 minutes. Recorded in `CLAUDE.md` under the design decision it argues against,
  "No special case for background/auxiliary traffic".

Closed by step 6 (2026-07-31), against the frozen session in `phase-2-step-6-session/`:

- ~~**`x-claude-code-agent-id` has never been observed here**~~ — **it arrives.** Seven rows carry
  one agent ID, spanning the subagent's own background calls as well as its main call. An empty
  `agent_id` can be read as "main conversation".
- ~~**`client_disconnect` is the least verified of the five statuses**~~ — **starlette reaches it
  reliably.** Six rows, both backends, in two shapes: partial usage captured before the drop
  (`message_start` seen, `message_delta` not), and nothing captured at all.

Closed since this file was written:

- ~~**Symbolic `error_code` values are unnamed**~~ — settled in step 4. Derived from the httpx
  exception class name rather than tabulated. See decision 9.

- ~~**`router_version` is duplicated**~~ — fixed in step 2. `__init__.py` reads it from installed
  metadata via `importlib.metadata.version`, so `pyproject.toml` is the only place it lives. A
  source tree that was never installed reports `0.0.0+unknown` rather than guessing.
- ~~**Whether uvicorn's own logs should join the router's log file**~~ — they do. See decision 5.
- The credential config reshape (one `credential` field, three modes) is agreed and unimplemented,
  and is *not* part of Phase 2. `config.py` still has the two-knob shape.
