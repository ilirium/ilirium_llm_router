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

### 2. `make format` disagreed with the whole codebase — found here, fixed at the end of the phase

Running `make format` mid-phase reformatted **twelve files, eight of them untouched by this phase**.
There is no `[tool.ruff]` section in `pyproject.toml`, so `ruff format` used its default 88 columns
while the codebase is written at 100. `make lint` passed either way, because line length is `E501`
and that is not in ruff's default rule set — so the two halves of the Makefile disagreed and only
one of them ever ran.

The reformatting was reverted at the time rather than committed, because unrelated churn in a phase
branch hides the change it is supposed to show. **Fixed afterwards, deliberately and on its own:**
`line-length = 100` in `pyproject.toml`, then one reformat commit covering the repository.

100 is measured, not picked: the widest lines in the repository are 100 characters, and the twelve
that exceed it are comments and docstrings, which `ruff format` does not rewrap.

**How the reformat was checked, since "it only changes layout" is exactly the kind of claim that
should not be taken on trust.** Every `.py` file's AST was dumped before and after and compared.
Eighteen of nineteen were byte-identical after parsing. The nineteenth was a real change and a
harmless one: a docstring in `test_logging_setup.py` began with a quote character —
`""""Did the request arrive" …` — and ruff inserted a space after the opening triple quote to
disambiguate the fourth, which alters the string's value by one leading space. Then the tests, the
linter, `make check`, and a live request through the reformatted router, which answered the probe,
returned the Anthropic-shaped 502 and wrote its row.

`make format` is now idempotent: running it a second time reports nineteen files unchanged, which is
what makes the target safe to run again.

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

## What Claude Code shows, measured 2026-07-31

A real session against a local model with LM Studio not running. Claude Code displayed:

```
✻ 502 Could not reach the lmstudio backend at http://localhost:1234: ConnectError: … ·
  Retrying in 3s · attempt 5/10
```

Three facts come out of that one line, and the second and third were not anticipated.

**The router's own wording reaches the user, and is truncated from the right.** What is on screen is
the `message` from `error_response`, cut off with an ellipsis. So the *order* of that string is a
constraint, not a style choice: the backend and its address have to come before the exception, which
is how it happens to be written. Anything that puts httpx's wording first would push the only
identifying detail off the end of the line.

**Claude Code retries a 502 — ten times, with backoff.** The status was chosen to describe what
happened, and it turns out to also decide behaviour: a 502 reads as transient, so a session survives
LM Studio being restarted without the user doing anything. Worth knowing before anyone is tempted to
"fix" the status to something more precise. A 4xx would fail the turn immediately instead.

**One user turn therefore becomes up to ten `transport_error` rows.** Each is a real call and
belongs in the file, but a row count is not a turn count when a backend is down, and the retries are
Claude Code's rather than the router's — nothing here retries anything.

## The injected error event: measured, and Claude Code ignores it

The other failure — a backend that dies *while answering* — was tested by pointing Claude Code at
the verification router on 8799, whose backend was the stand-in that resets mid-answer. Claude Code
said:

```
API Error: API returned an empty or malformed response (HTTP 200) — check for a proxy or gateway
intercepting the request
```

**The first run of this test was inconclusive and the fault was the stand-in's.** Its `message_start`
carried nothing but `usage` — no `id`, `role`, `model` or `content` — and its events mixed CRLF and
LF framing. "Empty or malformed" was as likely a complaint about that as about anything the router
did. The stand-in was rewritten to send the real sequence in the real shape (`message_start` with
every field, `content_block_start`, `ping`, seven text deltas) and the test re-run. **Same message.**

So the finding stands, and it is the one that matters:

**Claude Code does not act on a mid-stream `error` event.** The comparison that makes this
conclusive rather than suggestive is the 502 above, where it printed the router's own message
verbatim — it *does* surface backend wording when it recognises an error. Here it printed its own
generic line instead. It is reporting the absence of a completed message, which is what it would
report if nothing had been injected at all.

The event was kept regardless, deliberately, and `CLAUDE.md` now records why *and* records that it
has no measured consumer. The honest summary of the decision taken earlier that day: **right in
shape, wrong in effect.** Anthropic's documented error event is the correct thing to send; this
particular client does not read it.

Two things worth carrying forward from that:

- **A design decision agreed from the shape of a protocol is not a measurement.** This one was
  agreed in conversation, implemented, unit-tested, and verified by curl — and all of that
  established only that the bytes were correct, never that anyone consumed them.
- **The failure is not silent even so.** Claude Code's own message names the likely cause — "check
  for a proxy or gateway intercepting the request" — which is exactly right when a proxy is what
  broke. The user is not left staring at a stream that stopped.

## What is still not proven

Nothing in Phase 3's "Done when" remains unmeasured. What is *not* known is how any harness other
than Claude Code treats either error, which is a question for whenever the second one is attempted
(see "Goal" in `CLAUDE.md`) and not for this phase.
