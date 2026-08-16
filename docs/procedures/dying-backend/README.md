# Phase 3 verification — the backend that fails on purpose

The instrument behind every measurement in `../../milestone-1-core/phase-3-failure-handling/notes.md`. A backend cannot be asked politely
to die halfway through a reply, so this is one that always does.

**Meant to be re-run**, which is the opposite of `../../milestone-1-core/phase-2-observability/evidence/step-6-session/`. That directory is
frozen evidence and regenerating it would break the row numbers cited elsewhere; this one is a tool,
and running it is the point. Phase 4 is about finding where a local backend falls short, so expect
to want it again.

## What is here

| | |
|---|---|
| `dying_backend.py` | Answers with a complete, correct SSE opening and then resets the connection mid-answer. Also serves `/slow`, which keeps talking for a minute so the *caller* can be the one to go away |
| `router.yaml` | The router on **8799**, its `lmstudio` backend pointed at **1299**. Deliberately not 8787 and 1234, so this runs alongside a working router and a real LM Studio without touching either |
| `runs/` | Where the log and CSV land. Gitignored — the artefacts of a run are not evidence worth keeping, unlike Phase 2's |

## Running it

From the repository root, in two terminals:

```
python3 docs/procedures/dying-backend/dying_backend.py
make run CONFIG=docs/procedures/dying-backend/router.yaml
```

Then the four cases. Any model name that is not `claude-…` routes to the failing backend.

**A backend that is not running** — stop `dying_backend.py` first:

```
curl -s -X POST http://127.0.0.1:8799/v1/messages -H 'content-type: application/json' \
  -d '{"model":"local-test","stream":true,"messages":[]}'
```

Expect HTTP 502 and `Could not reach the lmstudio backend at http://127.0.0.1:1299: ConnectError:
All connection attempts failed`, with a row reading `transport_error` / `connect_error`, no
`ttfb_ms`, and `response_bytes` of 0.

**A backend that dies mid-answer** — same request with `dying_backend.py` running. Expect the events
it sent, then the router's own `event: error`, and a row reading `transport_error` / `read_error`
that carries `input_tokens: 11` — captured before the break — and counts only the *backend's* bytes,
excluding the injected event.

**A caller that hangs up** — `--max-time` gives up while the reply is still coming:

```
curl -s -N --max-time 2 -X POST http://127.0.0.1:8799/slow -H 'content-type: application/json' \
  -d '{"model":"local-test","stream":true,"messages":[]}'
```

Expect a `client_disconnect` row, and — the part worth watching for — `caller went away` printed by
`dying_backend.py`, which is its next write failing because the router closed the upstream
connection rather than leaving it talking to nobody.

**What Claude Code shows.** Point a real session at it, in a scratch directory:

```
ANTHROPIC_BASE_URL=http://127.0.0.1:8799 ANTHROPIC_AUTH_TOKEN=x \
  CLAUDE_CODE_ATTRIBUTION_HEADER=0 claude --model local-test
```

Measured 2026-07-31: for the unreachable backend Claude Code prints the router's own message and
**retries ten times with backoff**; for the mid-stream break it prints `API returned an empty or
malformed response (HTTP 200)` — its own wording, not ours, because **it does not act on a
mid-stream `error` event**. Both results are discussed in `../../milestone-1-core/phase-3-failure-handling/notes.md`.

## The warning worth reading before trusting a result

The first version of `dying_backend.py` sent a stub `message_start` carrying nothing but `usage`,
and framed its events with a mix of CRLF and LF. Claude Code answered "empty or malformed response",
and **that answer was worthless**: it was as likely a complaint about this file as about anything the
router did. The opening below is now the real event sequence in the real shape — `message_start` with
every field, `content_block_start`, `ping`, then text deltas — and the finding only counts because
the confound was removed and the test re-run.

If a result from this directory is surprising, suspect the instrument first.
