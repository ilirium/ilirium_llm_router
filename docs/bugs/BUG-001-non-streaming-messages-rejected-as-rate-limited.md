# BUG-001 — Non-streamed `/v1/messages` rejected as rate-limited

**Status: open, with a working workaround and the cause narrowed to the client.**
**Last reproduced 2026-09-18; NOT reproduced 2026-09-19 under the hosts route** — both on Claude
Code **2.1.267**.

> ***2026-09-19: the rejection does not happen when Claude Code believes it is talking to
> Anthropic directly, even though every byte still goes through the router.*** **Nine classifier
> requests, nine `ok`, zero 429s** — against **119 rejections** on the same build the day before.
> **The router is cleared by measurement**: same router process, same `httpx` egress, same TLS
> fingerprint presented to Anthropic on both days. *See "The experiment that moved it" at the
> foot of this file.*

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

***Amended 2026-09-18.*** **The 429 is not quota exhaustion** — that half is now measured rather
than inferred: a reply twenty-two seconds earlier on the same connection reported every bucket
`allowed`, at 52% of the five-hour window.

**What this paragraph said next was *"a categorical rejection of one request shape"*, and that is
incomplete in a way that matters.** *The same request shape **succeeds** when Claude Code talks to
Anthropic directly.* **The rejection needs the shape AND this router**, and a sentence naming only
the shape reads as a statement about Anthropic's API that the evidence does not carry.

## Where the diagnosis stands — the one-page answer, 2026-09-19

***Why the router could not run the safety classifier is NOT settled. What changed is that the
question now has one box left in it instead of a field.*** *This section is the synthesis; the
sections below are how it was arrived at, in order.*

### Ruled out by measurement, not by argument

**Everything the router does to the bytes.** *The same router process, the same `httpx` egress, the
same TLS fingerprint and the same connection pool carried nine classifier calls on 2026-09-19 and
were refused 119 times on 2026-09-18.* **So `accept-encoding`, HTTP/2, header rewriting, the TLS
fingerprint and connection reuse are all dead** — the last two having been the expensive ones nobody
wanted to test.

**And it is not Anthropic refusing the request *shape*:** the identical shape, on the identical
credential, succeeds. **Nor quota** — dead twice over, at 0.52 / 0.59 and again at 0.11 / 0.01.

### What is left, and it is one thing

***The discriminator is whether `ANTHROPIC_BASE_URL` names `api.anthropic.com`.*** **When it names
anything else the client changes what it sends, and the rejection follows.** *That much is measured.*

***Which of those changes triggers it is not.*** **One candidate is already eliminated**: the
2026-09-18 run with `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1` put `x-client-request-id` on the
wire and **the 429 did not move.** **The one that survives into the success is the attribution
block** — absent in all 125 rejections, present in all 9 successes.

*What the client does and does not withhold is `../wiki/claude-code-first-party-gate.md`'s to say;
the counts are `../reference/measurements.md`'s. Neither is restated here.*

### A hypothesis that fits, and it is labelled as one

**The rejection says `rate_limit_error` and names no bucket, no `retry-after`, no metering at all**,
on a connection whose successes carry twelve. ***A 429 that names no exhausted bucket is not really
a rate limit*** — it is some other refusal wearing one.

**The withheld block is a *billing* header.** *A subscription credential arriving without attribution
plausibly cannot be billed to the subscription, falls to some default entitlement with no allowance,
and is refused as `rate_limit_error` — which would explain both the refusal and why it is shaped
like a quota error while every real bucket reads healthy.*

***This is a story that fits the evidence and is not a finding.*** **This document has three
retractions in it for exactly that move.**

### What would settle it, in one session

***A subtractive test, which the hosts route is what makes possible.*** **Run first-party as on
2026-09-19, but have the router strip the attribution block on the way out.** *Everything else stays
identical — same client, same credential, same first-party posture, same egress.*

| | |
|---|---|
| **The 429 returns** | ***The block is the cause***, and this document gets a one-line answer |
| **The 429 stays away** | **The block is exonerated** and the cause is something else the gate changes |

**The cost is honest: it rewrites a request body**, which breaks byte-relay and the prompt-cache
prefix for that run — *so it is experiment-only.* ***The additive version — injecting the block when
the client is gated — is the same test from the other side and would be a workaround if it worked***,
but it fabricates billing attribution, so **the subtractive one answers the question without
fabricating anything and should go first.**

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
family. ***That work is Phase 14 and it is done — this paragraph is kept because its prediction was
exact.*** *It said "Phase 13" until 2026-09-18; the number moved on 2026-09-04 and this file was not
among the three named to be brought true.*

**Both gates it names held.** `calls.csv` took no new column — *the headers went to the log, and
where they durably live is still deferred* — and the allowlist is **named, never a copy**: 28 exact
names, with an unknown `anthropic-ratelimit-*` header reported **by name and never by value**.

**What the recorder now reads is in
`../milestone-2-corpus/phase-14-rate-limit-headers/evidence/`**, and the section below is what it
returned.

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

## The experiment that moved it, run 2026-09-19

***The client was made fully first-party while every byte still went through the router.***
`/etc/hosts` points `api.anthropic.com` at `127.0.0.1`, a local TLS terminator holds an `mkcert`
certificate for that name, and the router's own process pins the name to Anthropic's real address so
it does not forward to itself. **`ANTHROPIC_BASE_URL` is unset**, which is what the client's gate
actually reads.

| | **2026-09-18**, `ANTHROPIC_BASE_URL` set | **2026-09-19**, hosts route |
|---|---|---|
| Non-streamed `/v1/messages` over 100 KB | **125** | **9** |
| Outcome | **119 × `429`**, 6 `client_disconnect` | ***9 × `ok`*** |
| System blocks in the request | **2** | **3** |
| The attribution block in `system` | ***absent in all 125*** | ***present in all 9*** |

**Claude Code 2.1.267 on both days**, same credential, same machine, same router build.

*The canonical rows for these counts are `../reference/measurements.md`, "The first-party gate and the classifier" — a correction lands there first.*

***This satisfies the positive check this document asks for above*** — a non-streamed
`/v1/messages` of roughly 130 KB to `claude-sonnet-5` and `claude-opus-5` returning **200**, with
`calls.csv` rows reading `path=/v1/messages`, `stream=false`, `error_status=ok`. **And `BUG-000`'s
trap does not apply:** the requests carry `anthropic-beta: …,auto-mode-classifier-2026-07-16,…` and
a system prompt opening *"You are a security monitor for autonomous AI coding agents"*, so the
classifier demonstrably ran rather than merely failing to fail.

### What this settles

***The router does not cause the rejection.*** **The same router process, the same `httpx` egress
and the same TLS fingerprint presented to Anthropic carried nine classifier calls on 2026-09-19 that
were rejected 119 times on 2026-09-18.**

**Two entries in the four-differences table above are therefore dead, and both were the expensive
ones:**

| | |
|---|---|
| **TLS fingerprint** | *Anthropic saw the **router's** fingerprint on both days.* **Same fingerprint, opposite outcomes** |
| **HTTP/1.1 vs HTTP/2, connection reuse** | The router pooled its own connections identically on both days |

***What is left is client-side: content Claude Code withholds when `ANTHROPIC_BASE_URL` names any
host but `api.anthropic.com`.***

### What it does NOT settle, and the distinction is the whole history of this file

***The attribution block is the leading candidate and is not shown to be the cause.*** **Several
behaviours change together when the base URL goes away.** *One of them is already eliminated: on
2026-09-18 `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1` restored `x-client-request-id` to the wire
and **the 429 did not move**.* **The attribution block is the one known content difference that
survives into the 2026-09-19 success.**

### The workaround, which this document has never had

**Leave `ANTHROPIC_BASE_URL` unset and reach the router through a hosts entry and a local TLS
terminator.** *The full runbook is
`../milestone-2-corpus/phase-14-rate-limit-headers/for-the-owner.md`, entry 14.* **It needs `sudo`,
a local CA in the system trust store, and a machine-wide redirect** — *so it is a workaround for a
person who wants auto mode through a router, not a fix.*

### The 429 was hiding a second defect, and auto mode still does not work

***"The 429 is gone" is not "auto mode is usable end to end", and it is now known not to be.***

**Aligning the owner's session transcripts against the router's record of the same minutes** —
`../milestone-2-corpus/phase-14-rate-limit-headers/evidence/claude-code-sessions-to-check-safety-classifier.txt`
— **gives an exact correspondence: every Bash call that succeeded sent no classifier request at all
(those are allowlist matches), and every classifier request that reached the router corresponds to a
call the client reported as `claude-opus-5[1m] is temporarily unavailable`.**

***And none of those requests failed at the router.*** **Each returned `200` with a real verdict,
including `<block>no` — which means *allow*.** *So the client asked whether a command was safe, the
router carried the question to Anthropic, Anthropic answered "allow", the router carried it back,
and the client reported the classifier unavailable.* ***The failure is downstream of a correct 200.***

**The prime suspect is the router's own `accept-encoding` experiment**, which is the only change
that alters what a non-streamed reply looks like to the client — and the classifier is always
non-streamed. ***Suspicion, not finding***, and the test is one line: force `identity` for
non-streamed and re-run. → `for-the-owner.md` entry 19.

***None of this touches the 429 result above.*** **Two defects were stacked and the first hid the
second**: while every classifier request was rejected outright, nothing ever reached a `200` body
for this to show on. *Counts in `../reference/measurements.md`, "The classifier still fails after
the 429 is gone".*

***And a first-party client gzips some request bodies, which this router cannot route.*** **Two
requests that run were rejected by the router with `400` — "The request body carries no 'model'
field" — because the model peek reads the compressed bytes.** *The client retried uncompressed and
recovered.* **Anyone adopting the workaround above will meet it.**

### For the upstream issues

**This is the thing both of them stall on**, and it is stronger than the streamed/non-streamed pair
this file has carried since 2026-08-25: ***one client build, one credential, one machine, and the
only variable is whether the client believes its base URL is Anthropic's.*** **Reporting it is still
an open action.**
