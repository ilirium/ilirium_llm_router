# BUG-001 — Non-streamed `/v1/messages` rejected as rate-limited

**Status: open. Last confirmed 2026-09-18** — reproduced unchanged on Claude Code **2.1.267**.

> ***RETRACTION, 2026-09-18. This document has been clearing the router with a circular argument
> since it was written, and the row is struck below.*** **The classifier works when Claude Code
> talks to Anthropic directly and fails through the router** — same credential, same machine, same
> client version, same afternoon. **That control had never been run.** What follows is still an
> accurate description of the responses; its attribution of cause is not settled, and the sentence
> *"the 429 is not a rate limit"* in the next paragraph is now the weakest claim in the file
> rather than its conclusion.

Every `POST /v1/messages` sent with `stream: false` to `api.anthropic.com` returns **HTTP 429**
`rate_limit_error`, while a streamed request **2.8× larger** to the same model, on the same
credential, through the same router process, succeeds **0.6 seconds later**.

The 429 is not a rate limit. It is a categorical rejection of one request shape, wearing a rate
limit's status code.

## Why it matters here

**Claude Code's auto mode is unusable while this holds.** Auto mode classifies each tool call for
safety before running it, and that classifier request is non-streaming — so every `Bash` call needs a
request of exactly the failing shape. On 2026-08-25 auto mode was switched on and failed within about
ninety seconds, on a `printenv`.

Read-only operations do not use the classifier and are unaffected, which is the available workaround:
**prefer the harness's own file tools over shelling out** while this is open. That happens to be what
`../../CLAUDE.md` already says for unrelated reasons.

## What was measured, and when

**All figures below are from 2026-08-25**, over
[`evidence/calls-2026-08-21-to-2026-08-25-redacted.csv`](evidence/calls-2026-08-21-to-2026-08-25-redacted.csv)
— 526 rows, router version `0.1.0`, the complete telemetry record for those days.

`/v1/messages` only, split by `stream`:

| Day | non-streamed | of which 429 | streamed | of which 429 |
|---|---|---|---|---|
| 2026-08-21 | 22 | 3 — **13.6%** | 16 | **0** |
| 2026-08-24 | 63 | 63 — **100%** | 230 | **0** |
| 2026-08-25 | 17 | 17 — **100%** | 145 | **0** |

**Across the whole slice, 83 of 83 rate-limited calls were non-streamed. Not one streamed call was
rate-limited, in 391 of them.**

## The control that rules out a rate limit

Three pairs in one two-minute window on 2026-08-25, times in UTC:

| Time | `stream` | Model | Request bytes | TTFB | Result |
|---|---|---|---|---|---|
| 14:01:54.474 | `false` | `claude-opus-5` | 153,139 | 527 ms | **429** |
| 14:01:55.077 | `true` | `claude-opus-5` | **428,729** | 1686 ms | **ok** |
| 14:02:29.940 | `false` | `claude-opus-5` | 153,758 | 397 ms | **429** |
| 14:02:30.365 | `true` | `claude-opus-5` | **436,208** | 1397 ms | **ok** |

**You cannot be over an input-token budget and simultaneously have a request 2.8× larger accepted, in
the same second, on the same credential.** Whatever produces the 429, it is not token accounting.

**And `count_tokens` is the second control.** On 2026-08-24 — the day 63 of 63 non-streamed
`/v1/messages` calls failed — **all 21 `POST /v1/messages/count_tokens` calls succeeded**, every one
non-streaming, the largest at **61,729 bytes**. So the defect is not "non-streaming is broken". It is
the specific combination **`/v1/messages` with `stream: false`**.

## What this rules out

| Hypothesis | Refuted by |
|---|---|
| A genuine token-rate limit | The accepted request is 2.8× larger than the rejected one, 0.6 s later |
| A genuine request-rate limit | 375 streamed calls in the same two days, zero rejected |
| ~~The router~~ | ~~Same process, same second, one path works and the other does not~~ **STRUCK 2026-09-18 — the reasoning is circular.** It compares streamed against non-streamed **inside** the router, which cannot detect a router-caused defect that only affects non-streamed requests — *which is the exact defect shape in question*. **The control that would settle it is direct versus routed at the same shape, and it was never run until 2026-09-18, when it came back against the router** |
| A model-specific limit | Identical model on both sides of each pair |
| Non-streaming generally | 21 non-streamed `count_tokens` calls succeeded on the worst day |
| Real capacity pressure | The 429 returns in **385–786 ms**, against 1274–2761 ms for successful calls — rejected at the edge, before any inference |

## The client's retry behaviour, which is worth knowing before reading anyone's logs

The failures arrive in **groups of exactly five**, with exponential backoff of roughly 1.1 s, 1.3 s,
2.4 s, 3.6 s. On 2026-08-25 the sequence was five attempts against `claude-sonnet-5` at 153,141 bytes,
then five against `claude-opus-5` at 153,139 bytes — **a two-byte difference, which is exactly the
model-name length difference.** Identical payload, retried against a fallback model.

**So one user-visible failure is fifteen rows.** A raw 429 count over-states the number of distinct
failures by an order of magnitude, and a naive count will not match a user's account of what happened.

## When it started

2026-08-21 shows non-streaming **mostly working** — 3 failures in 22. By 2026-08-24 it is total.
`calls.csv` was 91 KB with no rotated segment at the time of capture, so **the record is complete and
the boundary is real**, not an artefact of a truncated file. The regression falls between 2026-08-21
and 2026-08-24; nothing in this slice narrows it further, because no traffic was recorded on the 22nd
or 23rd.

## What would prove it fixed

**An absence of 429s proves nothing** — see `BUG-000-about-these-documents.md`. A quiet session looks
exactly like a fix. The positive check:

> Send a `POST /v1/messages` with `stream: false`, a body of roughly 150 KB, to `claude-opus-5`, and
> get **HTTP 200**. Then confirm in `logs/telemetry/calls.csv` that the row shows `path=/v1/messages`,
> `stream=false`, `error_status=ok`.

Driving Claude Code with auto mode on produces exactly that request as a side effect, which is how
this was found. **Record the Claude Code version when the check is run** — if the fix turns out to be
client-side, the version is the only thing that will identify it.

## What the router cannot tell you, and the work that would change it

A 429 writes `rate_limit_error: Error` and nothing more. **Which bucket was hit, and when it clears,
are in response headers the recorder does not read** — `retry-after` and the `anthropic-ratelimit-*`
family. That work is **Phase 13** — allocated on the Phase 11 branch and landing in
`../milestone-2-corpus/implementation-plan.md` with it, so if this document reached `main` first, look
there after Phase 11 merges. It carries two gates: `calls.csv` taking no new columns is a Milestone 2
non-goal, and the store's promise of bodies-only-never-headers means a **named header allowlist**
rather than a copy.

Until then this document rests on timing and a streaming control — **reconstruction rather than
measurement**, and honest about it.

## Upstream

Two open issues stall on exactly the measurement above — distinguishing an upstream 429 relayed
through a proxy from one the proxy produced:

- [`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653)
- [`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365)

**Neither has been told what is in this file.** The paired control — same model, same second, larger
streamed request accepted — is the thing they lack, and reporting it is an open action rather than
something already done.

## A correction to an earlier figure

An earlier session recorded *"66 of 232 calls"* rate-limited on 2026-08-24. The frozen slice gives
**63 for that day**, and 2026-08-21 contributes exactly **3**. `63 + 3 = 66`: the earlier count summed
the whole file and attributed it to one date. **The corrected figures are the table above**, and the
2026-08-24 total of 232 does not appear anywhere in the complete record — that day holds 317 rows.

## The control that was missing, run 2026-09-18

**Direct versus routed, at the same request shape.** *This is the comparison the "What this rules
out" table never made, and it is why the router row above is struck.*

| Path | Auto mode's classifier |
|---|---|
| Claude Code → **api.anthropic.com** directly | **works** |
| Claude Code → **the router** → api.anthropic.com | **429**, every time |

Same credential, same machine, **Claude Code 2.1.267**, the same afternoon. *Established by the
owner noticing that the session he was reading this in had auto mode on and working, and asking
what the difference was.*

**What any explanation has to satisfy: 820 streamed calls through the router succeeded.** So it is
not "the router" — it is the router **and** a non-streamed request together.

**The four differences between the working path and the failing one**, all of which apply to
streamed calls too:

| | |
|---|---|
| **`accept-encoding: identity`** | The router's only *deliberate* change to an outgoing request. **Being tested first**, Phase 14 |
| **HTTP/1.1 vs HTTP/2** | The router builds `httpx.AsyncClient` with no `http2=True` and carries no `h2` dependency |
| **TLS fingerprint** | Python/httpx against Node. Structural, and not cheaply changed |
| **Connection headers re-derived** | `host` and `content-length` are set fresh by the client |

**What the headers say, measured through the router on 2026-09-18** — the measurement this document
asked for under "What the router cannot tell you", now taken:

| | Rate-limit headers on the reply |
|---|---|
| A **successful** call | **12**, the whole `anthropic-ratelimit-unified-*` family |
| A **429** | **none at all** |

***Read that pair carefully, because it is easy to over-read.*** It says the rejection carries no
metering information on a connection whose successes carry plenty. **It does not by itself say
whose fault the rejection is**, and this document said it did for several hours before the direct
control was run.

*One detail for anyone chasing this upstream: the classifier request carries **no `stream` key at
all**, rather than `"stream": false`. Searching a payload for the latter will not find it.*

**Full record:** `../milestone-2-corpus/phase-14-rate-limit-headers/evidence/`.
