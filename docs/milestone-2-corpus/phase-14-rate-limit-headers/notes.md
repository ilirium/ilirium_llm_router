# Phase 14 — notes

**Written while the work ran**, not reconstructed afterwards. *`../../README.md` asks for that line
because it changes how far a reader should trust the narrative.*

**Index of group files:** none yet. Groups A and B are small enough to sit here; the split happens
if a group earns it, per `../../README.md`.

---

## Before Task 1 — the diagnosis, from material already on disk

**The phase was reshaped before it opened.** The owner's subject was not "build the instrument" but
*"Claude cannot use the safety classifier because of a rate limit — how do we debug the cause and
fix it?"* **The whole of the answer's first half came out of `to-run-server/logs/`**, three weeks
after the traffic that produced it, with no request sent and no credential used.

**What that cost: four reads.** `calls.csv`, the corpus day indexes, and two blobs.

| | |
|---|---|
| **`calls.csv`, four days** | 114 non-streamed `/v1/messages`, **95 rejected 429**; 820 streamed, **none**; 66 non-streamed `count_tokens`, **none** |
| **The 311-byte request body** | `{"model":"claude-opus-5","max_tokens":1,"messages":[{"role":"user","content":"quota"}], "metadata":{…}}` — **Claude Code's quota probe**, not the classifier |
| **The ~140 KB request body** | `max_tokens: 64`, two messages, system prompt opening *"You are a security monitor for autonomous AI coding agents"* — **the classifier**, and **it omits `stream` entirely** |
| **The 114-byte response body** | `{"type":"error","error":{"type":"rate_limit_error","message":"Error"},"request_id":"req_redacted0000000000000001"}` |

***The `request_id` is the finding that mattered most, and it is the one nobody had.*** Every
rejection carries a distinct one. **Anthropic answered each of these calls itself** — the router is
not synthesising the 429, and no edge or WAF layer intercepted it. `BUG-001` ruled the router out by
arguing from same-process timing; this is the same conclusion reached by a different and stronger
route.

**Two figures that kill the size hypothesis from both ends.** A **311-byte** request rejected in
~450 ms; a **181,083-byte** non-streamed request to the same model **accepted** on 2026-08-21, TTFB
12 s, 639 output tokens. *`BUG-001`'s control was a 2.8× pair; this is 580× and in the opposite
direction to what a token budget would produce.*

**What is still not known, and it is the whole of Group C:** the response headers. They were never
recorded. Everything above is about the request; nothing here says which bucket Anthropic thought
was exhausted, or whether it named one at all.

### One correction to `BUG-001`, to be made at Task 12

**`BUG-001` says the classifier request is *"non-streaming"*, which is true of its effect and not of
its bytes.** The body carries **no `stream` key at all** — `peek()` records `stream=false` for an
absent key, which is correct, but a reader chasing the bug upstream would look for `"stream": false`
in a payload and not find it. *Worth a sentence in that document rather than a silent fix.*

## Task 2 — re-deriving the plan against the code

***The plan contradicted itself and the register is what caught it***, which is `IDM-008`'s whole
claim. Two findings, both in the plan before any code existed:

| | |
|---|---|
| **The trigger was written twice, differently** | The task list said *"not 2xx"*; the register said **`>= 400`**. They differ on 3xx. Reconciled to `>= 400`, which is the branch `relay` already has — *inventing a second threshold was the alternative and it was not noticed until the two sat in one document* |
| **`request-id` was `❓` and is now closed** | The argument for leaving it out was that the id is already in the error body. **It is — but the body only reaches disk when the corpus is enabled, and the corpus is off by default.** A log line that cannot stand alone is not an instrument. Both spellings are in, since which one arrives is not knowable from here |

**Nothing else in the plan survived contact wrongly.** The `>= 400` branch in `relay` already exists
and already calls `call.failed`, so the hook needed no new control flow, and every route funnels
through `relay` — so one hook covers all four.

## Tasks 3–5 — the instrument

**`RECORDED_RESPONSE_HEADERS`, plus a prefix catch that records names only.** *It opened at
seventeen names and is twenty-eight now; the count lives in the plan's register, not here.*

***The prefix catch is this plan's own judgement and is marked unratified in the settled table.***
The tension it resolves: an allowlist of exact names is the safe thing, and it is also **silently
wrong the day Anthropic adds a bucket** — the new header is dropped and nothing says so. Logging the
*name* of an unlisted `anthropic-ratelimit-*` header and discarding its *value* makes the new bucket
visible without writing anything unnamed.

**A name cannot carry a credential; a value can.** That asymmetry is the entire safety argument, and
it is why the prefix is `anthropic-ratelimit-` and not the broader `anthropic-`.

**`(none)` rather than a blank tail**, because the most likely finding of this phase is a
`rate_limit_error` that names **no exhausted bucket at all** — and a blank would read as the logging
having failed rather than as the measurement it is.

## Task 6 — exercising it, and what the harness is built against

**Six mutations, six caught.** `evidence/mutation-check.py`.

***The harness reports "mutation applied" and "check failed" as two separate lines, deliberately.***
*`prompt.md` carried this as one of five things a session gets wrong here:* Phase 13's mutation
harness **silently never applied its mutations**, which is indistinguishable from a clean pass. So a
mutation whose text does not match exactly once is reported as a **failure of this script**, never
as a pass of the test set.

The six: the allowlist stops filtering; nothing is recorded; an unlisted bucket is logged with its
value; the prefix catch stops catching; an empty set logs blank instead of `(none)`; the log fires
on success. **The credential test is the one that matters** — it asserts the secret is absent *and*
that an allowlisted value is present, so it cannot pass by logging nothing.

## Verified by

***This section has gone stale twice in one day, both times within hours of being written, and both
times because the work moved rather than because it was written carelessly.*** *It is the section
that is read as the phase's sign-off, so it is rewritten rather than appended to. The two superseded
readings are named at the bottom rather than deleted.*

- **`uv run pytest`** — **460 passed**, 2026-09-18, against the committed `config.yaml`. *The
  trunk's count was 448; this phase adds 12.*
- **`make lint`** — clean at the pinned `0.16.1`. *Five `SIM117` nested-`with` findings were fixed
  rather than ignored, and the mutation check was re-run afterwards.*
- **`evidence/mutation-check.py`** — **12/12, exit 0.**
- **Driven against the real thing twice, 2026-09-18**, by the owner — **Claude Code 2.1.267**. The
  first run produced the failure measurement; the second produced the control. **Both are frozen in
  `evidence/`, and together they are the finding.**
- **One value is deliberately not measured**, and that is a decision rather than a gap:
  `anthropic-ratelimit-unified-representative-claim`. It is recorded by name only until somebody
  establishes what it holds.
- **`config.yaml` carries an uncommitted local override in this worktree** — the corpus switched on,
  which is how the two runs above captured bodies. **`test_template_matches_the_repository_config`
  is red while it is in place**, by design: that test compares the shipped starter against the
  repository's own config, and it is the only thing stopping a new user's template drifting. *The
  460 above is measured against the committed file.*

*What this section said before, kept because the corrections are the interesting part:* it read
**"Not yet driven against the real thing"** until the first session ran, and then **"One control is
still not run"** until the second did. *Both were true when written and false within hours. The
second is the one worth noticing — it named the missing control precisely enough that running it was
obvious, which is the only reason the control exists.*

## Tasks 7–9 — the measurement, and what it does and does not settle

**The owner ran it on 2026-09-18**, 11:02–11:05 UTC, Claude Code **2.1.267**, router 0.1.0, auto
mode on. Frozen as `evidence/rate-limit-headers-2026-09-18.txt` and
`evidence/calls-2026-09-18-redacted.csv`.

### It reproduces, on current versions, unchanged

**12 non-streamed `/v1/messages`, all 429. 8 streamed, all `ok`. Same three minutes, same
credential.** `BUG-001` was last confirmed 2026-08-25 and its record ended 2026-08-26; **24 days
later nothing about it has moved.**

***And the retry signature `BUG-001` predicted is there, to the byte.*** Five attempts at
`claude-sonnet-5` and **128,250** bytes, then five at `claude-opus-5` and **128,248** — *a two-byte
difference, which is exactly the model-name length difference.* **One user-visible classifier
failure is ten rows**, plus two 311-byte `quota` probes. A raw 429 count overstates distinct
failures by an order of magnitude, exactly as that document warns.

**The failing body is the classifier**, confirmed from the corpus rather than inferred: `max_tokens:
64`, `stream` absent, system prompt opening *"You are a security monitor for autonomous AI coding
agents"*.

### The finding

**Every one of the twelve 429s carried `request-id` and nothing else.**

```
anthropic replied 429 to /v1/messages: request-id=req_redacted0000000000000002
```

**No `retry-after`. No `anthropic-ratelimit-*` header of any kind.** *And not merely none that the
allowlist knew: an unlisted one would have rendered as `name=<unlisted>`, and none did. The
allowlist is not what made them absent.*

***A `rate_limit_error` that names no exhausted bucket is not a rate limit.*** That is the sentence
`BUG-001` has wanted for three weeks, and it is now measured rather than reconstructed — **the
header line is the measurement the two upstream issues stall on.**

### The control that is missing, and it is the honest limit of the above

***Whether a successful reply on this credential carries `anthropic-ratelimit-*` headers at all is
unmeasured.*** **The instrument fires only at `>= 400`** — deliberately, so that every call does not
log its buckets and drown the file — and that decision is precisely what leaves this open.

| | |
|---|---|
| **If a 200 carries them** | Anthropic returned `rate_limit_error` while declining to name a bucket **on a credential that normally names one.** The finding is damning |
| **If a 200 carries none either** | These headers are simply not sent on an OAuth subscription credential, and **their absence on the 429 says nothing at all** |

**Until that is run, "the 429 names no bucket" is a fact and "Anthropic normally names one" is an
assumption.** *Written down rather than left implicit, because a green instrument and a real finding
together are exactly the conditions under which an untested premise gets carried into an upstream
report.*

**The control is small and is not yet built:** log the rate-limit headers of the **first successful
reply per process**, once, at `INFO`. One short run then answers it, and the file is not drowned.
*Proposed to the owner on 2026-09-18 rather than built — `CLAUDE.md`, propose before implementing.*

## The control ran, and it closes the gap the section above left open

**Second run, 2026-09-18 11:19:50 UTC, same versions.** One successful call was enough. Frozen as
`evidence/rate-limit-headers-success-control-2026-09-18.txt`.

**A successful reply carries twelve rate-limit headers. The 429s carried none.** Same credential,
same afternoon, minutes apart.

| | Rate-limit headers |
|---|---|
| `200` on `/v1/messages` | **12**, the whole `anthropic-ratelimit-unified-*` family |
| `429` on `/v1/messages`, twelve of them | **0** |

***So the assumption named in the section above is now measured, and it held.*** Anthropic does
meter this credential, does report the meter on every successful call, and **said `rate_limit_error`
while reporting nothing at all.** *`BUG-001` can stop hedging: it is not reconstruction any more.*

### The allowlist was wrong and the prefix catch is the only reason anyone knows

***Not one of the twelve documented bucket names arrived.*** `anthropic-ratelimit-requests-*`,
`-tokens-*`, `-input-tokens-*`, `-output-tokens-*` — **zero of them, on a successful call.** A
subscription credential is metered by a different family entirely: `anthropic-ratelimit-unified-*`,
with a 5-hour and a 7-day window, a utilization percentage, an overage status and a fallback
percentage.

**An allowlist built from the documentation would have recorded nothing and looked correct doing
it.** The control line would have read `request-id=…` and stopped, and the conclusion drawn from it
would have been *"a successful reply carries no rate-limit headers either, so the 429's silence
means nothing"* — **the exact opposite of the truth, reached through a green instrument.**

***This is the unratified position from the settled table earning its place.*** It was argued for on
the grounds that *"an exact list is silently wrong the day Anthropic adds a bucket"*. **It was
already wrong on the day it was written**, and the catch is what said so. *The argument was right
for a reason weaker than the real one: the risk is not that the list goes stale, it is that a list
copied from documentation never matched this credential at all.*

### What was added, and the one thing deliberately not added

**Eleven of the twelve are now named and will be recorded with their values.** The twelfth,
`anthropic-ratelimit-unified-representative-claim`, is **held back on purpose**: *"claim" is the
vocabulary of tokens and assertions, not of counters*, and nobody here has established what it
holds. **It keeps being reported by name**, so it is neither lost nor forgotten — it is waiting for
somebody to find out. *Adding a name to the list is one line; taking a value back out of a log file
is not.*

**Twelve mutations, twelve caught**, including one that adds `representative-claim` to the list and
one that drops the unified family back out of it.

## The finding above is wrong about cause, and the owner found it by asking a question

***Do not read the two sections above without this one.*** They establish what the responses
contain. **They do not establish whose fault the rejection is, and for a few hours this phase said
they did.**

**The owner asked: if the classifier is broken, how is auto mode working in the session we are
having right now?** *That session is not connected to the router. His was.*

| Path | The classifier |
|---|---|
| Claude Code → Anthropic **directly** | **works** |
| Claude Code → **the router** → Anthropic | **429** |

**Same credential, same machine, Claude Code 2.1.267, the same afternoon.** *This is the control
that was never run, and `BUG-001` is retracted accordingly — its "What this rules out" table clears
the router by comparing streamed against non-streamed **inside** the router, which cannot see a
router-caused defect specific to non-streamed requests.* **The document has been assuming its
conclusion since 2026-08-25.**

***The lesson is not that the measurement was bad.*** The headers are real and the 429 genuinely
carries no metering. **What was bad was the inference**: "Anthropic sent this" was read as
"Anthropic is at fault", and the one experiment that separates them was sitting unrun while a
session with the answer in it was open on the same screen.

### The constraint that makes this hard, and it is worth keeping in view

**820 streamed calls through the router succeeded.** Whatever the cause is, it is the router **and**
a non-streamed request *together* — which rules out anything that would apply to every call the
router makes, and that is most of the obvious candidates.

### The experiment now in the tree

**`accept-encoding` is no longer forced to `identity` for non-streamed requests** — the caller's own
value is relayed. It is the router's only *deliberate* difference from the direct path. Streamed
requests are unchanged, because the SSE scanner reads raw bytes and that half is not in question.

**Two consequences, named in the code rather than discovered later:** a non-streamed reply may
arrive gzipped, so `usage` will not be found and the token columns go empty — which is
`reference/observability.md`'s documented fallback, not a new failure mode — and **the corpus will
store those bytes compressed**, so a stored non-streamed response blob stops being readable JSON.

**And one thing the change cannot do, found by a test that asserted otherwise and failed.** httpx
supplies its own `accept-encoding` when the caller sends none, so the router can relay a *value* but
not an *absence*. It does not matter here — Claude Code always sends one — but the test now records
it rather than claiming transparency the code does not have.

**Fourteen mutations, fourteen caught**, including one that silently reverts the experiment while
leaving it looking live.

### If it comes back negative

**HTTP/2 is next** — the router builds `httpx.AsyncClient` with no `http2=True` and carries no `h2`
dependency, so it speaks HTTP/1.1 where Claude Code direct almost certainly speaks HTTP/2. After
that the remaining suspects are the TLS fingerprint and the re-derived connection headers, and the
cheaper move at that point is to capture both requests byte for byte rather than keep guessing —
`procedures/anthropic-auth-check.md` already establishes the technique.

## The `accept-encoding` experiment came back negative

**Run 2026-09-18 11:50 UTC. 16 non-streamed `/v1/messages`, all 429. 7 streamed, all `ok`.**
Unchanged.

***And the change genuinely ran*** — checked rather than assumed, which matters because "the
experiment silently did not happen" and "the experiment disproved the hypothesis" look identical
from the log. **The stored 429 bodies are no longer JSON:** they open `83 38 00 00`, which is not
gzip, zlib, deflate or zstd, leaving **brotli** — the `br` in Claude Code's own `accept-encoding`
list. So the router relayed the caller's header, Anthropic compressed the reply, and the rejection
happened anyway.

**That also demonstrates the second consequence this phase predicted in advance:** the corpus now
holds those bodies compressed. *`extract` would hand a reader brotli where it used to hand them
JSON.* **The owner chose to keep the change in place** while the next variable is tested, so the
cost stands for now and is recorded rather than absorbed.

### And the control had a defect that nearly reversed the conclusion a second time

**The latch was spent on `/api/hello`.** Claude Code probes it before its first real call, the
router forwards it, it returns 200 — and it meters nothing, so the line read:

```
anthropic replied 200 to /api/hello, sampling rate-limit headers once: (none)
```

***`(none)` is the exact string the failure lines print.*** Read at speed that says *"successes
carry no buckets either"*, which is the opposite of what the 11:19 run measured and would have
un-done the finding. **So no real control sample was taken on that run at all.**

**Fixed by gating the sample to `/v1/messages`**, with a regression test named for the endpoint and
a mutation that puts the bug back.

***This is the second time an instrument built to prevent a wrong reading has nearly produced
one.*** *The first was the allowlist that would have reported nothing on a subscription credential
and looked correct. Both were caught by comparing a line against a measurement taken minutes
earlier, and neither by a test — which is worth saying plainly, since sixteen mutations pass.*

## Both variables now flipped together, at the owner's instruction

**`accept-encoding` stays relayed AND the client now offers HTTP/2** — `h2` declared in
`pyproject.toml`, `http2=True` in `create_client`. *Two variables at once, to be bisected only if
the pair comes back positive.* **`http2=True` negotiates rather than demands**, offering h2 over
ALPN and falling back to 1.1, so LM Studio is untouched.

**The test asserts on httpx private attributes** — `client._transport._pool._http2` — and says so
in its own docstring. *Accepted deliberately: the alternative is asserting nothing, and "an
experiment nobody can confirm is running" is precisely the failure this phase has now hit twice.*

**What is left if the pair comes back negative:** the TLS fingerprint and the re-derived connection
headers. **At that point the cheaper move is to stop guessing and capture both requests byte for
byte** — one throwaway Claude Code session pointed at a listener, which shows the request and then
fails, against the router's own upstream. *That settles headers and HTTP version factually and
leaves TLS, which sits below HTTP and cannot be read this way.*

## Both variables came back negative, and the meter's values arrived

**Run 2026-09-18 12:13 UTC, HTTP/2 on and `accept-encoding` relayed.** *Both exonerated.*

***And the run is the cleanest statement of the defect yet, because one model does both things in
the same seconds:***

| `claude-opus-5`, same session | |
|---|---|
| **streamed** — 5 calls, up to 212 KB | **all `ok`** |
| **non-streamed** — 6 calls | **all `429`** |

*So it is not the model, not the size, not the credential, not the moment. `claude-sonnet-5`
contributes five more non-streamed 429s at 128 KB.*

### The meter had headroom, and this is the sentence the upstream issues need

**The control fired on a `/v1/messages` 200 at 12:13:39 — twenty-two seconds before five
rejections on the same connection** — and the buckets read:

| | |
|---|---|
| `unified-status` | **`allowed`** |
| `5h-utilization` · `5h-status` | **0.52** · `allowed` |
| `7d-utilization` · `7d-status` | **0.59** · `allowed` |
| `fallback-percentage` | 0.5 |
| `overage-status` · `-disabled-reason` | `rejected` · `org_level_disabled_until` |

***Every bucket says `allowed`, at 52% and 59%.*** **So the 429 is not quota exhaustion, and that
is now measured rather than argued.** *Frozen as `evidence/unified-meter-values-2026-09-18.txt`,
with the five rejections that followed it in the same file.*

**`overage-status=rejected` is noted and not leaned on.** *Overage is spending beyond the
subscription allowance and it is disabled at org level — but utilization is nowhere near a limit,
so nothing yet connects it to a rejection. Recorded because it is the only value in the set that
reads like a refusal.*

### The prefix catch earned its place a second time

**`anthropic-ratelimit-unified-fallback` appeared at 12:13 and was not in the 11:19 sample of the
same account.** *A list frozen an hour earlier was already one short.* Added on the same test as
the other eleven — it sits in the metering family beside `-fallback-percentage` and its name says
what kind of thing it is, which is exactly what `-representative-claim` still does not.

### What is left

**`accept-encoding` and HTTP/2 are both out.** Remaining: **the TLS fingerprint** — Python/httpx
against Node, which sits below HTTP and cannot be read off a plaintext capture — **the re-derived
`host` and `content-length`**, and ***whatever Claude Code itself does differently when
`ANTHROPIC_BASE_URL` points somewhere that is not Anthropic***, which this phase has not considered
until now and which no amount of router-side flipping can reach.

***That last one is the reason to stop flipping variables.*** Four hypotheses have cost four
sessions and eliminated two. **The byte capture replaces the rest with a diff**, and it can be done
in two halves: the router already *receives* what Claude Code sends it, so that half costs a log
line; the direct half needs one throwaway session pointed at a listener.

## The arriving-request sampler — the byte capture's cheap half

**The router receives exactly what Claude Code sends it**, so half the "what differs between the
direct path and the routed one" question costs a log line rather than one of the owner's sessions.

**Two latches, one per shape.** *The pair is the measurement:* the streamed request succeeds and the
non-streamed one is rejected, so **what the client sends differently between them** is the thing
being looked for. A single latch would sample whichever arrived first and never the other.

**Safe to point at a request that carries the credential**, and by the rule rather than by a special
case: `RECORDED_REQUEST_HEADERS` holds seven names whose values may be logged, and **everything
else is logged by name with `<unlisted>` in place of its value** — `authorization` and `x-api-key`
included. *A name cannot carry a credential; the same asymmetry the response side already rests on.*

**Order is preserved and duplicates are kept**, which is the one place this differs from
`describe_headers`. *Header order is exactly the kind of thing that could differ between two
clients, and sorting it away would hide the quarry.* The HTTP version the client used is logged
beside it.

### Two things this cost that are worth recording

**An assertion in an existing test was over-broad and the new line exposed it.**
`test_the_sample_obeys_the_same_allowlist` asserted `"authorization" not in` **every** captured
message. That passed only because nothing else logged a header name; the arriving sampler prints
`authorization=<unlisted>`, which is the name with no value and is precisely what it should print.
**Scoped to the line it is actually about.** *The test was checking the right thing against the
wrong surface.*

***And the mutation harness refused a mutation instead of passing it, which is the first time its
central design has fired in anger.*** `return " ".join(parts) if parts else "(none)"` now exists in
**two** functions, so the anchor matched twice — and the harness reported **"mutation applied: NO —
matched 2 times"** and a **script failure**, not a caught mutation and not a silent pass. *This is
the exact defect Phase 13 shipped: its harness never applied its mutations and looked identical to
a clean run.* Re-anchored on the line above it.

**Nineteen mutations, nineteen caught.**
