# BUG-001 — Non-streamed `/v1/messages` rejected as rate-limited

***Status: RESOLVED 2026-09-22. The cause was this repository's own `README.md`.***

**`CLAUDE_CODE_ATTRIBUTION_HEADER=0`.** *Our quick start told the operator to set it, from
2026-08-07 (`7cd90f9`) until 2026-09-22, with no stated reason in any of the five documents that
carried it.* **The variable suppresses an attribution block Claude Code puts in the *body* of its
requests, and Anthropic rejects a non-streamed `POST /v1/messages` that arrives without one.**

***The router was never at fault.*** *It was faithfully carrying a client our own documentation had
told the operator to misconfigure.*

## The measurement that named it

**2026-09-21, one machine, one router process, no restart between the two halves** — the only
difference is one environment variable in the client's shell:

| | `CLAUDE_CODE_ATTRIBUTION_HEADER` | Non-streamed `/v1/messages` |
|---|---|---|
| **A** | **`=0`** | ***33 × 429*** |
| **B** | ***absent*** | **0 × 429**, five classifier calls, all `200` |

***And the mechanism was confirmed separately, by intervention rather than correlation.*** *Twenty
minutes before run A, with the variable still set, a build that put the block back **from the router
side** carried twelve non-streamed calls to `200`.* **Supply the block and the rejections stop;
withhold it and they return.**

*The day reads `ok → 429 → ok` inside one hour, which is not the shape of a recovering quota.*

## What was originally claimed here, and what of it survives

**This document said the 429 was *"a categorical rejection of one request shape"*.** ***That was
half right and the half it got wrong is the important half:*** *the rejected shape is not "non-streamed"
— it is **"non-streamed and carrying no attribution block"**, and the block was absent because we
were switching it off.*

***Everything measured below still stands.*** **The figures, the timings, the retry behaviour and
the refutation table were all taken correctly** — *they describe, accurately, a router being driven
with the variable set.*

## Where the full investigation lives

***Phase 14, on `feat/phase-14-rate-limit-headers`, which is deliberately NOT merged.*** *Three days,
thirteen eliminated hypotheses, a TLS-fingerprint comparison, a hosts-route experiment and a
working attribution injection are all kept there as an archive.* **See
`../milestone-2-corpus/phase-14-rate-limit-headers/README.md` for what it contains and why it stayed
on a branch.**

***The fix that shipped is five documents losing a line.***

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
| The router | Same process, same second, one path works and the other does not |
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

## What proved it fixed, and why the bar was set where it was

**An absence of 429s proves nothing** — see `BUG-000-about-these-documents.md`. *A quiet session looks
exactly like a fix, and this bug produced four of them before it was understood.* **What settled it
was the paired A/B above**: *not "the 429s went away" but "they returned when the variable came back,
on the same process."*

***One thing is still missing from the record and is worth naming.*** **No run has yet produced a
BLOCKED verdict from auto mode's classifier through the router** — *every classifier call measured
came back at stage 1.* **So the allow path is demonstrated and the block path is assumed.** *It is
`BUG-000`'s standing warning, and it is not a reason to keep this open.*

The original positive check, which still works:

> Send a `POST /v1/messages` with `stream: false`, a body of roughly 150 KB, to `claude-opus-5`, and
> get **HTTP 200**. Then confirm in `logs/telemetry/calls.csv` that the row shows `path=/v1/messages`,
> `stream=false`, `error_status=ok`.

Driving Claude Code with auto mode on produces exactly that request as a side effect, which is how
this was found. **Record the Claude Code version when the check is run** — if the fix turns out to be
client-side, the version is the only thing that will identify it.

## What the router can now tell you, which it could not when this was written

***This section used to say the headers were unread and that the work was Phase 13.*** **Both are
now wrong**: *the work was **Phase 14**, and it shipped.* **A reply of `400` or worse is logged with
its `retry-after` and `anthropic-ratelimit-*` values** — `RECORDED_RESPONSE_HEADERS`, an explicit
allowlist of names rather than a copy, *so the store's bodies-only-never-headers promise holds* —
**with one sampled successful reply per process as the control.**

***That control is what turns "the rejection named no bucket" into a finding rather than a guess.***
*Without it, "this rejection carried no rate-limit headers" and "this credential is never sent
them" are indistinguishable, and only the first reads like evidence.*

**Where those headers durably live beyond `router.log` is `BKL-0043`** — *`calls.csv` taking new
columns is still a Milestone 2 non-goal, and overturning it is the owner's.*

## Upstream

Two open issues stall on exactly the measurement above — distinguishing an upstream 429 relayed
through a proxy from one the proxy produced:

- [`anthropics/claude-code#82653`](https://github.com/anthropics/claude-code/issues/82653)
- [`BerriAI/litellm#30365`](https://github.com/BerriAI/litellm/issues/30365)

***Neither was told, and the report is WITHDRAWN*** — **owner's decision, 2026-09-20, and the
cause found the next day made it the right one.** *What would have been filed is our own
configuration, reported as somebody else's defect.*

**Enough detail stays in this file for anyone who wants to take the underlying behaviour upstream
later** — *that a non-streamed `/v1/messages` without an attribution block is refused with a status
code that misdescribes it is a real observation about the API, and it is not a bug in this router.*

## A correction to an earlier figure

An earlier session recorded *"66 of 232 calls"* rate-limited on 2026-08-24. The frozen slice gives
**63 for that day**, and 2026-08-21 contributes exactly **3**. `63 + 3 = 66`: the earlier count summed
the whole file and attributed it to one date. **The corrected figures are the table above**, and the
2026-08-24 total of 232 does not appear anywhere in the complete record — that day holds 317 rows.
