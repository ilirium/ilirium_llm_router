# Phase 3 notes — behaving well when things go wrong

Written 2026-07-31, **while building**, unlike `phase-2-notes.md`, which was written before its
phase started. The reason for the difference is the phase's central finding, below: there was much
less to build than the plan expected, so there was no plan worth writing in advance.

Branch: `feat/phase-3-failure-handling`, off `main` at `acb399f`. Merge back with `--no-ff`.

## The finding that shaped the phase: four of the five items were already built

Phase 3 in `implementation-plan.md` lists five pieces of work. Read against the tree at `acb399f`,
four of them already existed, with tests, because Phase 2's `error_status` column could not be
written without them. Phase 2 was specified as observability and quietly delivered most of the
error handling as a consequence.

| Phase 3 item | Where it already was |
|---|---|
| LM Studio not running | `proxy.py` catches `httpx.HTTPError` around `client.send` → `transport_error` row, Anthropic-shaped 502 |
| Sensible timeouts | `proxy.TIMEOUT` — connect 5 s, read 600 s, so a model may think for ten minutes but a dead port fails fast |
| Failures mid-stream | `observe.SseScanner` reads an SSE `error` event → `stream_error` |
| Claude Code disconnecting | `proxy.watch` catches `CancelledError`/`GeneratorExit` → `client_disconnect`, and the step 6 session produced six real rows |
| Backend errors passed through | `test_a_backend_error_is_passed_through_unchanged` — status, body and rate-limit headers all survive |

This is worth recording because it changes what a phase *is* for. The remaining work was not "build
Phase 3" but "find what Phase 2 missed while it was busy being right about something else", plus the
verification the phase's own "Done when" asks for and no unit test can supply.

## The four gaps that were left

Each was found by reading the failure paths against the plan, not by a failing test — there were no
failing tests, which is the point.

### 1. A caller that leaves while its request body is still arriving

`await request.body()` raises starlette's `ClientDisconnect` (`starlette/requests.py`), and nothing
caught it: the call left **no CSV row at all** and a traceback in the log.

It is the same failure the relay already handles, one step earlier, and it is not theoretical. Every
call re-sends the whole conversation, so even a one-word turn arrives as ~118 KB (`CLAUDE.md`,
"Observed request shape") — there is a real window in which the caller can go away mid-upload.

Now recorded as `client_disconnect` with `backend` empty, because routing needs a body and there
was never one to route on. The exception still propagates, because there is nothing to answer on.

### 2. Closing the upstream connection was version-luck

`reply.aclose()` rode on a starlette `BackgroundTask`. Starlette runs that task after the response
completes — but on the ASGI **spec 2.4** branch a client disconnect raises `ClientDisconnect` out of
`StreamingResponse.__call__` and the background task is **skipped**. That is precisely the case
where closing matters: nobody else is left to end the upstream connection.

uvicorn 0.51's HTTP protocols advertise `spec_version: 2.3` (`h11_impl.py`, `httptools_impl.py`), so
starlette takes the older task-group branch and the close does happen today. The phase's job was to
stop that being luck. The relay now closes from its own `finally`, which runs on every path; the
background task stays for the opposite gap, a generator that never runs at all and so never reaches
its `finally`. `httpx.Response.aclose` is guarded by its own `is_closed`, so the two cannot
double-close.

**The general lesson, which outlives this fix:** the correctness of that line depended on a version
number in a dependency of a dependency. Nothing in the code said so, and no test would have failed
when it changed.

### 3. Anything unanticipated came back as a framework 500

Plain text, no error shape, nothing Claude Code can display usefully. Both handlers now answer in
Anthropic's shape. Starlette re-raises after the `Exception` handler returns, so uvicorn still logs
the traceback into the router's own rotating log — the two halves of the job stay separate: the
traceback is for us, the error object is for the caller.

`ClientDisconnect` gets its own handler answering **499**, nginx's code for a caller that left.
Nothing is delivered — there is no connection left — so the status is chosen for how it reads in a
log rather than for a reader.

### 4. A stream that broke after its 200 was silent

Covered below, because it is a decision rather than a gap.

## Decisions taken

### 1. A broken stream is ended with an SSE `error` event

**Agreed in conversation on 2026-07-31, deliberately, because it is an exception to byte-relay.**

A streamed reply returns HTTP 200 before any content exists. When the relay then breaks — LM Studio
killed mid-answer, a connection reset — the failure cannot be put in a status code that has already
gone out. Until now the caller simply saw the stream stop, which is **indistinguishable from a model
that finished talking**.

The router now appends one Anthropic-shaped `error` event to such a stream:

```
event: error
data: {"type":"error","error":{"type":"api_error","message":"The lmstudio backend's reply broke off mid-stream: ReadError: …"}}
```

Three constraints keep this from being the thin end of a parse-and-rebuild wedge:

- **Only ever appended, never altering.** The injected event follows bytes that have already gone
  out untouched. No byte the backend sent is changed, dropped or reordered, so the prompt-cache
  argument for byte-relay is not affected — that argument is about *request* bytes anyway.
- **Only on SSE replies.** A buffered reply that breaks is left truncated. An SSE frame stapled to a
  half-written JSON object is not a message, it is corruption — and the caller gets unparseable JSON
  either way, so the only thing injection would add is the appearance that the router did it.
- **Not counted in `response_bytes`, not fed to the scanner.** Both measure what the backend sent.
  A row whose byte count included the router's own apology would be describing a reply that never
  arrived.

The alternative — stay silent, let the CSV row be the only record — was rejected because the row is
visible to *us* and the failure happens to *the user*, mid-answer, with no indication that anything
went wrong.

### 2. `make format` disagrees with the whole codebase, and was not obeyed

Running `make format` reformatted **twelve files, eight of them untouched by this phase**. There is
no `[tool.ruff]` section in `pyproject.toml`, so `ruff format` uses its default 88 columns while the
codebase is written at ~100. `make lint` passes either way, because ruff's default rule set does not
include line length.

The reformatting was reverted rather than committed: unrelated churn in a phase branch hides the
change it is supposed to show. **This is unresolved** — `make format` is currently a target that
cannot be run safely, and the fix is one line (`[tool.ruff] line-length = 100`) plus one deliberate
reformat commit of its own. Left for the repository owner to decide, since it touches every file.

## Verified against a running server, 2026-07-31

Half of the "Done when" needs a real Claude Code session and is still open (below). The other half —
does the router behave correctly when a backend fails — was checked against a **live server through
real uvicorn**, not the test client, because the test client cannot exercise a caller that hangs up
or a socket that resets.

Setup, kept out of the way of the working router on 8787 and the real LM Studio on 1234: a second
instance on **8799** from a scratchpad config whose `lmstudio` backend points at **1299**, which was
either dead or held by a stand-in that answers with SSE headers and one `message_start`, then resets
the connection with the answer half-written.

| Case | Result |
|---|---|
| Backend not running | `502`, Anthropic-shaped: `Could not reach the lmstudio backend at http://127.0.0.1:1299: ConnectError: All connection attempts failed`. Row: `transport_error` / `connect_error`, `response_bytes` 0, `ttfb_ms` empty |
| Backend dies mid-stream | The `message_start` that had arrived, then the injected `event: error`. Row: `transport_error` / `read_error`, `input_tokens: 11` captured before the break, `response_bytes: 122` — the backend's bytes only, injected event excluded as designed |
| Caller hangs up mid-stream | Row: `client_disconnect`, `input_tokens: 11`, `response_bytes: 306`, `duration_ms: 105`. **And the stand-in backend printed `caller went away`** — its next write failed because the router had closed the upstream connection. The disconnect propagated rather than leaving the backend talking to nothing |
| Service wedged? | No. After five consecutive failures, `HEAD /` and `/health` both still answered 200 |

The log and the CSV lined up as intended: uvicorn's `"POST /v1/messages HTTP/1.1" 200` sits directly
above the router's own line for the same call, on the same clock.

### The defect the live run found, that 146 passing tests did not

The injected event came back reading:

```
The lmstudio backend's reply broke off mid-stream: ReadError:
```

**httpx raises a mid-stream reset as `ReadError("")` — an exception with no message.** The obvious
`f"{type(exc).__name__}: {exc}"` then writes a dangling colon promising a reason that never comes,
into the CSV's `error_message` *and* into the event the user sees. Every unit test had supplied a
message, so all of them read correctly and only the real failure was wrong.

Now `observe.describe_exception`, which drops the separator when there is nothing after it, used at
all three sites. Re-verified live: the event and the row both read `ReadError`.

This is the same lesson as Phase 2 step 6, and it is now two for two: **the tests confirm the code
does what it was written to do; only real traffic shows what it was written to do being wrong.**

## What is still not proven

The other half of the "Done when":

> Stopping LM Studio mid-session produces a clear message in Claude Code and a correct CSV row.

The row is proven. **What Claude Code displays is not** — the 502 and the SSE `error` event are
both in the shape Anthropic uses, which is the reason to expect it renders them, but expecting is
not measuring. It needs a session with a local model where LM Studio is stopped mid-answer.
