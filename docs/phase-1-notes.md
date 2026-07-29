# Phase 1 implementation notes

Written 2026-07-29, when the proxy was first written.

This is the record of decisions taken *while writing the code* and of what running it taught us —
the things that are not derivable from the diff. The surrounding documents cover the rest: the
design and its reasoning live in `CLAUDE.md`, the phases in `implementation-plan.md`, the
constraints the proxy has to satisfy in `proxy.py`'s own docstring, and session state in
`handoff.md`.

## What was built

| Route | Behaviour |
|---|---|
| `HEAD /` | Answered locally, 200. Claude Code probes here before its first real call. |
| `GET /health` | Answered locally. Not part of the plan; useful for knowing the thing is up. |
| `POST /v1/messages` | The model name in the body picks the backend. No model is a 400. |
| everything else | Forwarded. Routed on the model if the body carries one, Anthropic otherwise. |

The catch-all is registered last, because the first matching route wins and it would otherwise
shadow the three above it.

`app.py` owns one `httpx.AsyncClient` for the process, created in the lifespan and closed on
shutdown, so connections are reused across requests rather than rebuilt per call.

## Decisions taken while writing it

**`peek_model` parses the body with `json.loads`.** The plan says to look inside the body "just far
enough to find the model name. Do not deserialize the whole thing." This deviates from the letter of
that, deliberately. The reason the plan gives for not deserializing is fidelity, and fidelity is
already guaranteed by a different mechanism: the original bytes are what gets forwarded, so nothing
`peek_model` does to its copy can affect what the backend receives. What the wording would buy
instead is speed, and the saving is around a millisecond on a 118 KB body against a call that takes
seconds. What it would cost is correctness: a byte scan for `"model"` finds the *first* occurrence
anywhere in the body, and the observed request carries 81 KB of tool schemas and 28 KB of system
prompt, any of which may contain that string. Revisit if profiling ever says otherwise.

**The reply is streamed with `aiter_raw()`, not `aiter_bytes()`.** `aiter_raw` skips httpx's own
content decoding, so the bytes leaving the router are the bytes that arrived. Closing the upstream
response is attached as a Starlette `BackgroundTask`, which runs after the last chunk has gone out —
returning a `StreamingResponse` means we cannot close it before returning.

**Response headers are assigned to `raw_headers` rather than passed as `headers=`.** Starlette's
`headers=` takes a mapping, which silently collapses repeated header names. Assigning the raw list
keeps them.

**`date` and `server` are dropped from the backend's reply.** See "What running it taught us".

**Timeouts were set now rather than left to Phase 3.** httpx defaults to 5 seconds for everything,
which would cut off essentially every model reply, so Phase 1 could not be exercised without this.
`connect=5s` stays short on purpose — LM Studio not running should fail fast, not hang.

**Connection failures are caught now rather than left to Phase 3 as well**, for the same practical
reason: verifying Phase 1 by hand means hitting a stopped LM Studio repeatedly, and a traceback is a
poor way to find that out. It is deliberately minimal — one `except httpx.HTTPError` producing a 502
in Anthropic's error shape. Phase 3 owns the real taxonomy, including errors that arrive mid-stream
behind a 200, which this does not catch.

**The catch-all sends bodiless requests to Anthropic.** There is nothing to route on, and the client
believes it is talking to Anthropic, so that is the least surprising destination.

**`create_app` takes an optional HTTP client.** Tests pass one wired to a stand-in backend. The
alternative — a real server on a port — would make the suite slow and flaky for no gain, and the
thing worth testing here is which address a request went to and exactly what it carried, which a
recording transport answers directly.

## What running it taught us

Both of these came from starting the router and reading real replies, not from the tests.

**LM Studio has "Require Authentication" switched on** on this machine. A forwarded local request
comes back `401 authentication_error` from LM Studio itself. Local models will not work until that
setting is turned off, or `lmstudio.api_key_env` is set in `config.yaml` with the key in `.env`.

This settles a question left open at the end of Phase 0. `api_key_env` was added speculatively, and
`handoff.md` suggested removing it if nothing ever used it. It is needed.

An incidental trap worth recording: probing `GET /api/v1/models` to check whether LM Studio was
running returned an empty body, which read as "not running". It was running and refusing to answer
unauthenticated. A quiet empty reply is not evidence of a dead server.

**The backend's `date` and `server` headers must not be relayed.** uvicorn writes its own, so
passing the backend's through gave the client two of each, which RFC 9110 forbids. This is the kind
of thing that is invisible in a proxy's tests — both header sets look fine individually — and
obvious the first time you read `curl -D -` output. There is now a test pinning it.

## A trap for whoever writes the next tests

`httpx.Response(200, json={...})` and `httpx.Response(200, content=b"...")` are *already fully
read*. Handing one back from a `MockTransport` and then streaming it raises `httpx.StreamConsumed`,
because the router — correctly — will not read a response twice. Fifteen tests failed this way
before the stand-in backend was changed to reply with an async iterator, which is what a real
backend does. `tests/test_proxy.py` has a `streamed()` helper for this; use it rather than building
`httpx.Response` directly.

## What is still unverified

Phase 1's "done when" has **not** been met. It asks for a real `claude` session against a cloud and
a local model, and no conversation has been held through the router.

More specifically: **the router has never sent a request to Anthropic.** That the forwarded
credential and the `anthropic-beta` list work through it is inference from the captured request in
`log-the-whole-request.txt`, not something anyone has watched happen. The tests assert that those
headers arrive at the backend unchanged, which is the part we can check without a live token; they
cannot tell us Anthropic accepts them.

Streaming is likewise verified only against a stand-in. Real SSE from either backend, tools, and
multi-turn conversation are all untested.

And LM Studio's actual parity with the Anthropic API — system prompts, `tool_result`, `thinking`
blocks, images, whether it reports `usage` at all — remains exactly as unknown as it was before
Phase 1. That is Phase 4's job, and nothing here brought it forward.
