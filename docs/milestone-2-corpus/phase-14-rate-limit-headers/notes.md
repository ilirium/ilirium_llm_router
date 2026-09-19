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

## The capture landed, and it exonerates the HTTP request entirely

**Run 2026-09-18 12:40 UTC.** Both shapes sampled. Frozen as
`evidence/arriving-request-headers-2026-09-18.txt`.

### What Claude Code sends the two shapes

***Byte-identical except `anthropic-beta`.*** Same twenty-one headers, same order, same values.

| Shape | `anthropic-beta` |
|---|---|
| **non-streamed** (429) | **9** entries |
| **streamed** (`ok`) | **13** — the same 9, plus `mid-conversation-tool-changes`, `advisor-tool`, `effort`, `structured-outputs` |

**That difference is Claude Code's own and exists on the direct path too**, so it cannot be what the
router does — *but it is not nothing, and the reason is in the next section.*

### What the router forwards

***Nothing is dropped and nothing is added.*** Computed rather than measured — `outgoing_headers`
is a pure function, so the arriving list was fed through it and through
`httpx.build_request` without needing another session:

| | |
|---|---|
| Dropped by the router | **none** |
| Added by the router | **none** |

*`host` and `content-length` are re-derived to the correct values and `connection` is re-added by
httpx, which is what those three are for.* **Every other header arrives upstream exactly as Claude
Code wrote it, in the order it wrote it.**

### So the HTTP request is not the difference, and that is a real conclusion

**Four hypotheses have now been eliminated:** `accept-encoding`, HTTP/2, a dropped header, an added
header. **The request the router sends is the request Claude Code would have sent.**

***What is left is below HTTP.*** The leading candidate is the **TLS fingerprint** — Python/httpx
over OpenSSL against Node over BoringSSL — which cannot be changed by header work and cannot be read
off a plaintext capture.

**A rule of the shape *"this client is not the official one AND the body says `stream:false`"*
would fit every observation this phase has made**, including the one that has been hardest to
place: *why streamed calls are untouched.* **Stated as a hypothesis with no evidence behind it yet**
— it is consistent with the data rather than shown by it.

### The two things worth doing next, and neither is another header flip

1. ***Try an API key instead of the subscription token.*** `credential: inject` and `api_key_env`
   already exist in the config and need no code. **If the 429 disappears, the rule is about
   subscription credentials reaching Anthropic from something that is not Claude Code** — which is
   both the answer and a workaround. *If it persists, that whole class is out.*
2. **The throwaway capture is still worth one session**, for a reason this run created rather than
   settled: **it would show whether Claude Code sends the same `anthropic-beta` list when it talks
   to Anthropic directly.** *This phase has been assuming the client behaves identically whatever
   `ANTHROPIC_BASE_URL` points at, and that assumption has never been checked.*

## Claude Code does NOT behave identically when `ANTHROPIC_BASE_URL` is set

***The assumption this phase carried from its first session is false, and it was never checked until
2026-09-18.***

**The listener plan was wrong and is recorded as wrong.** *Pointing Claude Code at `nc` **is**
setting `ANTHROPIC_BASE_URL`, so it captures the case the router already captures perfectly. It
could never have answered the question it was proposed for.* **Seeing the genuinely direct request
needs TLS interception**, which is invasive and was not done.

**`claude --debug api --debug-file` replaced it**, and a probe cost one trivial call instead of one
of the owner's sessions. **It does not log request headers** — path, an `x-client-request-id`, and
one attribution line — *which is itself why probing first was right.*

**But the attribution line is the finding:**

| | `x-anthropic-billing-header` |
|---|---|
| **direct** | `cc_version=2.1.267.0a3; cc_entrypoint=sdk-cli; cch=00000; cc_prompt_id=<uuid>` |
| **through the router** | `cc_version=2.1.267.0a3; cc_entrypoint=sdk-cli;` |

***Same `-p` mode, same client version, ninety seconds apart, and only the base URL differs.***
**`cch` and `cc_prompt_id` are dropped when the client is not talking to Anthropic directly.**

**And `x-anthropic-billing-header` appears nowhere in the twenty-one headers the router captured
arriving** — nor does `x-client-request-id`.

### What this does and does not establish

**Established:** the client varies what it sends by base URL. *So every router-side experiment this
phase ran was answering "what does the router change", while a second variable was moving
underneath and nobody had looked.*

**Not established:** whether that header reaches the wire in either case, and whether it has
anything to do with the 429. *The router's twenty-one-header capture came from an **interactive**
session and both probes above are `-p`, so the two are not like for like.* **One restart of the
router and one `-p` probe through it closes that**, because the arrival latch is spent for the
current process.

***Recorded before it is resolved, because the assumption's falseness stands on its own*** and does
not depend on how the remaining question comes out.

## The imitation came back negative, and that closes the attribution class

**Run 2026-09-18 13:04 UTC.** *10 non-streamed `/v1/messages` rejected, 5 streamed `ok`, one
`client_disconnect` where the client gave up.* **Unchanged.**

***Verified to have actually run, rather than assumed*** — the distinction this phase has been
bitten by twice:

| | |
|---|---|
| Commit `2ecaaec` | 13:03:11 UTC |
| Router started | 13:04:15 UTC, **64 seconds later**, from this worktree's venv |
| The venv | `.pth` pointing at this worktree's `src` — an editable install, not a stale copy |
| The live module | `imitation_headers` present, `BILLING_VERSION_SUFFIX` = `0a3` |

### What is now eliminated

**Ten hypotheses, all by measurement:**

| | |
|---|---|
| `accept-encoding: identity` | relayed the caller's own — still 429 |
| HTTP/1.1 vs HTTP/2 | negotiated h2 — still 429 |
| A header the router drops | **none is dropped**, computed from the capture |
| A header the router adds | **none is added** |
| The `anthropic-beta` list | varies by session and mode; not stable enough to discriminate |
| The withheld attribution headers | supplied — still 429 |
| Quota exhaustion | `allowed` at 52% / 59%, twenty-two seconds before five rejections |
| Request size | 311 bytes rejected, 181 KB accepted |
| The model | `claude-opus-5` succeeds streamed and fails non-streamed in the same seconds |
| The router inventing it | every rejection carries a distinct Anthropic `request_id` |

### What is left, and why this phase stops here

**The TLS fingerprint, or a server-side rule neither end of this machine can see.** *Python over
OpenSSL against Node over BoringSSL — and matching it means replacing the HTTP stack, not adding a
header.*

***The remaining hypotheses have no cheap discriminator left, and that is the reason to stop rather
than impatience.*** **Each of the last four experiments eliminated something real**; this one
eliminated an entire class. **The next one would cost a dependency swap or TLS interception on the
owner's machine, for a hypothesis with no evidence behind it beyond elimination.**

**What the phase has instead is a complete evidence package**, which is worth more than a guess: a
paired direct-versus-routed control, request ids for every rejection, the meter reading `allowed`,
a proof that the router alters no header, and a measured client-side difference keyed on
`ANTHROPIC_BASE_URL`.

### The three experiments should now come out

**All three are exonerated and none is free:**

| | Why it should go |
|---|---|
| `accept-encoding` relayed | **Actively harmful** — the corpus now stores non-streamed responses brotli-compressed, so `extract` hands a reader bytes where it used to hand them JSON |
| `http2=True` and the `h2` dependency | Buys nothing measured. **`IDM-003` governs dependencies**, and "the official client uses it" is not a justification |
| The imitation headers | Fabricated attribution sent on every call for **no benefit**, and it is the one change with a terms question attached |

*The owner's call, and it is the last one this phase needs.*

## The TLS premise holds, measured rather than assumed

**Captured 2026-09-18 with `evidence/clienthello-capture.py`** — a socket with no certificate at
all. *A `ClientHello` is plaintext and arrives **before** cert validation, so the client is seen and
then fails.* **No Anthropic traffic, no credential, nothing installed on the machine.**

| | Python / httpx / OpenSSL | Claude Code 2.1.267 |
|---|---|---|
| **JA3** | `166b2ba7d17746ef6996ecbe142aa507` | `5260242a2eb12c71995767c24569bff5` |
| Cipher suites | 17, opening `4866,4867,4865` | 17, opening **`4865,4866,4867`** |
| Extensions | **11** | **12** |
| Supported groups | **8** | **4** |

***Eight of the seventeen cipher suites differ, and the shared ones are offered in a different
order.*** Python sends `encrypt_then_mac` (22) and Claude Code does not; Claude Code sends
`status_request` (5) and `signed_certificate_timestamp` (18) and Python does not.

**A server tells these two apart trivially, before a byte of HTTP is read.** *The premise the
hypothesis rested on is no longer an assumption.*

### A correction, and then a correction to the correction

**This phase said "Node → BoringSSL" twice. That was wrong** — Node bundles OpenSSL. *Said plainly
when the machine turned out to have no Node at all and `claude` turned out to be a compiled
binary.*

***And then the capture pointed back the other way.*** The absence of `encrypt_then_mac` together
with `status_request`, `SCT` and a four-group list is **BoringSSL-shaped**, and a compiled
single-file binary is consistent with a **Bun** build — Bun uses BoringSSL. **So the original guess
may have been right for the wrong reason.** *Recorded as inference; the measured fact is only that
the two hellos differ.*

### What this does not do, and it is the same limit as before

***It does not show that fingerprinting causes the 429.*** **Streamed calls still succeed on the
Python fingerprint**, so a fingerprint check alone cannot be the rule — it would have to be a
combination with the request shape, and there is still no evidence for that beyond its being the
last thing standing.

### And it is not fixable from here

**Python's `ssl` exposes cipher lists, ALPN and version bounds. It does not expose extension
ordering or the extension set**, so the router cannot be configured into that fingerprint.

***A stack swap would not close it either.*** `curl_cffi` and its relatives impersonate **browsers**
— Chrome, Firefox, Safari. **None of them ships a Claude-Code profile**, and a rule keyed on Claude
Code's own fingerprint is not satisfied by looking like Chrome. **Matching it would mean
reproducing Bun's BoringSSL build**, which is far outside what this router is.

***So this line is closed: the hypothesis is plausible, unfalsifiable from this machine, and its fix
is unavailable.***

## The BoringSSL forwarder — testing the last hypothesis at all

**`evidence/boringssl-forwarder.py`**, built 2026-09-18 on the owner's suggestion of `curl_cffi`
over a Bun sidecar. *It is the cheaper of the two and it tests a different rule.*

```
Claude Code -> router -> http://127.0.0.1:<port> (forwarder) -> TLS(chrome) -> api.anthropic.com
```

**Nothing in the router changes** — `proxy.py` is untouched and this is not on its import path. One
`base_url` line in the owner's config, and **the credential travels the localhost hop it already
travels.**

### The fingerprint gate, run before building it

***`curl_cffi` is in the same TLS family as Claude Code and the router is not.***

| vs Claude Code | `curl_cffi` chrome | the router today |
|---|---|---|
| Cipher suites shared | **15 of 17, same relative order** | 9 of 17, wrong order |
| Claude Code's extensions missing | **none — a superset** | two |
| Supported groups | **identical** | different, 8 against 4 |

**It is not Claude Code's hash and is not meant to be** — `e14cbc3e…` against `5260242a…`, because
Chrome adds cert compression, ALPS and encrypted-ClientHello that a bare BoringSSL build does not.

| It passes | It fails |
|---|---|
| a bot score against **scripted-client** stacks | an **allowlist** of Claude Code's own hash |

*Both outcomes are informative, and a negative one leaves the Bun sidecar as the only way to match
exactly.*

### And it settles the identification the earlier correction muddled

***Claude Code's hello is BoringSSL-shaped, and the first guess was right for the wrong reason.***
Same cipher ordering, the same four groups, `status_request` and `SCT` present,
`encrypt_then_mac` absent — **BoringSSL without Chrome's browser extras**, which is what a Bun build
produces. *This phase said "Node → BoringSSL", corrected itself to "Node bundles OpenSSL" — true,
and the machine has no Node — and the measurement then landed back on BoringSSL by a different
route.*

### Streaming was verified rather than assumed

***A forwarder that buffers would break every streamed call and turn `ttfb_ms` into a measurement of
itself.*** Checked against a local SSE origin emitting five events 0.4 s apart, with no Anthropic
traffic at all — `FORWARDER_UPSTREAM` exists for exactly that:

```
+0.07s data: {"n":0}   +0.47s {"n":1}   +0.87s {"n":2}   +1.27s {"n":3}   +1.67s {"n":4}
```

**Chunk for chunk, spacing preserved.** *`stream=True` on `AsyncSession.request` and
`aiter_content()` — the API was inspected rather than guessed, after this phase spent two rounds on
instruments that looked right and measured nothing.*

### Driving it: a target and a config of its own

**`make forwarder` and `make run-boringssl`**, plus **`config-boringssl.yaml`** at the worktree
root. *The owner asked for both rather than hand-editing anything.*

***The separate config is not a convenience.*** `config.yaml` is compared **byte for byte** against
the shipped starter by `test_template_matches_the_repository_config`, so **every hand-edit of it
turns that test red for as long as the edit lives** — which it had been, all afternoon. *A second
file takes the edit instead and the suite goes green: **474 passed.***

**It differs from `config.yaml` in exactly three marked places** — the egress hop, the corpus on,
and the 5 MiB body cap matching what the owner had been running. ***Log and corpus paths are
deliberately identical***, so a run through the forwarder lands in the same files as every earlier
run and the two can be read against each other.

**`curl_cffi` is its own dependency group**, not `dev`: `uv sync` does not install it, `uv run` does
not pull it in, nothing under `src/` imports it, and it is reached only through `make forwarder`.
*`IDM-003` governs what earns a dependency, and a library whose purpose is to make a client's TLS
look like a browser's has not earned a place in the router's.*

**Both were exercised rather than assumed**, against the local SSE origin with no Anthropic traffic:
`make forwarder` resolves the group and starts, the config validates with the right `base_url`, and
five events 0.4 s apart came through at `+0.07 +0.46 +0.87 +1.27 +1.67`.

## A defect this phase shipped, and what it says about the earlier result

***The imitation's billing header was malformed from the moment it was written.*** It ended
`"; "` — **a trailing space, which an HTTP header value may not have.** The owner hit it as a
**502** the first time he ran the forwarder:

```
LocalProtocolError: Illegal header value b'cc_version=2.1.267.0a3; cc_entrypoint=cli; cch=00000;
cc_prompt_id=1ee21817-...; '
```

**Why it took until now to appear.** The router spoke **HTTP/2** to Anthropic, whose header
handling accepted it; the hop to the forwarder is **plaintext HTTP/1.1**, where `h11` validates and
refuses. *The same header, legal on one transport and fatal on the other.*

### It weakens the imitation result, and the notes above are amended rather than left

**The 13:04 run reached Anthropic** — 429s with `request_id`s, so the requests went out. **But they
went out carrying a header no HTTP parser is obliged to accept**, and *nothing here knows whether
Anthropic parsed it, normalised it, or discarded it.*

***So "the attribution class is eliminated" is weaker than this file said.*** **It is eliminated
only if Anthropic read the header** — and the one run that would settle it is the next one, which
carries the corrected header **and** the BoringSSL hop together. *If that comes back positive the
two will need separating.*

### Four tests and twenty-three mutations did not see it

***Every existing test asserts against `MockTransport`, which stores what it is handed and
validates nothing.*** *So a malformed header passed four assertions about its own content, including
one that reads it back and compares a prefix.*

**The new test validates through `h11` itself** rather than through anything this repository wrote,
and **was checked against the old value** to confirm it fails on it. There is a mutation that puts
the trailing space back.

***This is `prompt.md`'s "a green check is a claim, not evidence", arriving for the third time in
one phase*** — after the allowlist that would have reported nothing on a subscription credential,
and the latch spent on `/api/hello`. **All three were instruments built to prevent a wrong
reading.** *The pattern worth naming: each one tested the thing it was pointed at and none tested
whether it was pointed at the right thing.*

## A Chrome fingerprint changes nothing either

**Run 2026-09-18 13:41 UTC, through the BoringSSL forwarder with the corrected attribution header.**
*15 non-streamed `/v1/messages` rejected, 7 streamed `ok`, one `client_disconnect`.* **Unchanged.**

***Verified to have gone through the forwarder and reached Anthropic***, not to have died locally:
the rejections carry Anthropic `request_id`s — `req_redacted0000000000000023` — and a 200 came back
through the same hop carrying the full `unified` meter.

**So the bot-score hypothesis is eliminated.** *A TLS handshake that is genuinely
indistinguishable from Chrome's — BoringSSL family, a superset of Claude Code's extensions, an
identical group list — is rejected exactly as Python's was.*

**And it clears the doubt the malformed header left**, from the other direction: this run carried a
**legal** attribution header and was rejected too, so the earlier negative was not an artefact of
the trailing space.

### Eleven hypotheses, all eliminated by measurement

`accept-encoding` · HTTP/2 · a dropped header · an added header · the `anthropic-beta` list · the
withheld attribution headers · quota exhaustion · request size · the model · the router inventing
the rejection · **a non-browser TLS fingerprint**.

### What is left is one test and one unknown

**The exact-fingerprint allowlist.** `curl_cffi` is not Claude Code's hash — it carries cert
compression, ALPS and encrypted ClientHello that a bare BoringSSL build does not. **Only Bun's own
build could match**, and *even that is not certain: Bun's `fetch` need not fingerprint identically to
the Claude Code binary.* **A second forwarder, a runtime to install, and a maybe.**

**And a possibility nothing here has touched:** *connection reuse.* Claude Code direct may put the
classifier on an HTTP/2 connection that already carried a successful conversation; the router and
the forwarder pool their own. **Named because it is untested, not because there is evidence for
it.**

***This is where the diagnosis stops being worth the owner's sessions.*** **Every earlier experiment
eliminated something; this one eliminated the last cheap thing.** *What the phase has instead is an
instrument that works, eleven eliminated hypotheses, and an evidence package neither upstream issue
has.*

## The twelfth hypothesis came from reading the client, and it was free

***Added 2026-09-18, after the section above said the diagnosis had stopped being worth the owner's
sessions.*** *That sentence was about **experiments**, and it was right about experiments. It was
wrong to read as "there is nothing left to learn cheaply" — because nothing in this phase had ever
**read the client**, and the client is the second variable the phase discovered it had on
2026-09-18 and then went straight back to router-side flips.*

**The owner proposed analysing `github.com/anthropics/claude-code`. That repository is not the
source** — it is the issue tracker, the docs, the plugins and the examples, with no implementation
in it, and its `CHANGELOG.md` carries **no dates**, so it cannot even bracket `BUG-001`'s
2026-08-21 → 2026-08-24 regression window. *Checked rather than assumed.*

**The source was already on the machine.** Claude Code ships as a **Bun-compiled single-file
executable** with its JavaScript bundle embedded in **plaintext**. `grep -a -b -o -F` plus `dd`
reads it. **No credential, no request, none of the owner's sessions** — the instrument and the nine
frozen fragments are `evidence/binary-extract.sh` and
`evidence/claude-code-first-party-gate-2026-09-18.txt`.

### What the client does with `ANTHROPIC_BASE_URL`, in its own words

    function nd(){return He()==="firstParty"&&go()}
    function go(){if(a._CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL)return!0;return CE()}
    function CE(){let e=process.env.ANTHROPIC_BASE_URL;if(!e)return!0;return NA(e)}
    function NA(e){try{let t=new URL(e).host;return["api.anthropic.com"].includes(t)}catch{return!1}}

**Set `ANTHROPIC_BASE_URL` to any host but `api.anthropic.com` and `go()` is false**, which turns
off every behaviour gated on it. ***And `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` forces it back
true*** — a declared boolean env var, listed in the client's own config table as a **companion** of
`ANTHROPIC_BASE_URL`, next to `ANTHROPIC_CUSTOM_HEADERS`.

**This is the experiment C2d was approximating by hand.** *C2d imitated the two attribution fields
that happened to be visible in `claude --debug api`. This switch restores **everything** the gate
withholds, at the client, in one variable — and the router fabricates nothing, which also disposes
of the terms question the imitation carried.*

**Three more things the same gate withholds**, none of which this phase knew to look for:

| | |
|---|---|
| `x-client-request-id` | `Jje()` — `firstParty && go()`. **Seen in `--debug api` and never in the twenty-one arriving headers**, and now there is a reason rather than a puzzle |
| `traceparent` | `r_e()` — `go()` or `CLAUDE_CODE_PROPAGATE_TRACEPARENT` |
| Two context-compaction wire headers | in the non-streamed send, both on `He()==="firstParty"&&go()` |

### The classifier is the one shape that forces the attribution header

***Both classifier stages set `forceAttributionHeader:!0`*** — stage 1 at `max_tokens:(M==="fast"?256:64)`,
stage 2 at `8192` — **and so does `auto_mode_critique`. The main loop's non-streamed path does
not.** *`qk()`, the side-query sender, takes the flag as a parameter.*

**That is a tighter fit to the symptom than "non-streamed" is**, and it is worth stating plainly
because this phase has spent four days on the wrong noun:

| | Forces the attribution header | Result through the router |
|---|---|---|
| The auto-mode classifier | **yes** | **429**, every time |
| `/v1/messages` streamed | no | 820 of 820 **ok** |
| `/v1/messages/count_tokens` | no | 66 of 66 **ok** |

***So the failing shape may not be "non-streamed" at all.*** *It may be "the request that forces the
attribution header" — which is exactly the header `go()` degrades — and the two survivors need no
special pleading, because neither forces it.*

### What this is not, and the sentence is load-bearing

***This is a reading of code. It is not a measurement of a wire, and it does not identify the
cause.*** **`x-anthropic-billing-header` appears in none of the twenty-one headers this phase
captured arriving**, so either that capture was not a classifier request, or the header is withheld
from the wire entirely when `go()` is false. **Both readings point at the same experiment and
neither has been run.**

*Written down this way deliberately.* **The phase has already made the mistake of promoting a real
measurement into a conclusion once** — `for-the-owner.md` entry 5 — and a twelfth hypothesis
arriving after eleven negatives is exactly when that happens again.

### One thing checked and cleared rather than left hanging

**The SDK posts to `/v1/messages?beta=true`** — `client.beta.messages.create`. ***The router already
forwards the query string***, `target_url()` at `proxy.py:603`, and `proxy.py:11` names `?beta=true`
by hand. **Not a miss.** *Checked because "does the router drop the query string" is the obvious
router-side reading of the same evidence, and it is worth one minute to close.*

### What is left is now one test, one unknown, and one cheap experiment

**Unchanged:** the exact-fingerprint allowlist, and connection reuse. **Added, and it is the only
cheap one:** set `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL` and run the classifier through the
router. *`for-the-owner.md` entry 10 has the procedure and what each outcome means.*

## The flag reached the wire and the 429 did not move

**Run by the owner 2026-09-18 14:52 UTC**, Claude Code **2.1.267**, `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1`
alongside `ANTHROPIC_BASE_URL`, auto mode on. *The experiment is `for-the-owner.md` entry 10.*
Frozen at `evidence/first-party-flag-run-2026-09-18.txt`.

| | |
|---|---|
| `/v1/messages` **non-streamed** | **13 × 429**, 2 `client_disconnect`, **1 ok** |
| `/v1/messages` **streamed** | **7 of 7 ok** |
| The meter, 14:52:09 | `allowed` — **5h at 0.11, 7d at 0.01** |
| Every 429 | a `request-id` and **no rate-limit header**, exactly as before |

***The flag is not inert and this is the first proof of it.*** **`x-client-request-id` arrives**,
and it appears in **neither** the 12:40 nor the 13:41 capture. *`go()` is true, `Jje()` is true, and
the binary reading is confirmed against the wire rather than against itself.*

**So hypothesis twelve is eliminated the honest way:** the absence of `x-client-request-id` is not
the cause. **It is present now and the rejection is unchanged.**

### And the measurement that would have tested the actual hypothesis was spent on the wrong request

***The sampled non-streamed request is not a classifier request.*** It is the **haiku warm-up** at
14:52:09 — **323 bytes, 8 input tokens, `max_tokens`, and it succeeded.** The classifier requests
are the **127,949-byte** ones that begin eleven seconds later, and **not one of them was sampled.**

**`arrival_sampled` is keyed on `bool(call.stream)`** and taken by the **first** request of that
shape, whatever it is. *`proxy.py:368`.*

***So whether the classifier's own request carried `x-anthropic-billing-header` is still unknown,
and the `forceAttributionHeader` reading is neither confirmed nor refuted.*** **What the log proves
is that one unrelated non-streamed request did not carry it.**

**This is the third instance of one defect, and the second after it was supposedly fixed.**
*`for-the-owner.md` entry 6 records the latch spent on `/api/hello`; the fix was to gate it on the
path, and the comment at `proxy.py:372` says so in as many words.* **Path-gating was one level too
shallow: `/v1/messages` non-streamed is not one thing.** *The warm-up and the classifier differ by
four hundred times in size and the latch cannot tell them apart.*

***Recorded before it is fixed, and the fix is not this session's to choose*** — it touches `src/`,
and `CLAUDE.md`'s first working-agreement bullet is propose before implementing. **Entry 11 puts the
options to the owner.**

### One thing not to over-read, said here because it is the obvious thing to over-read

**The `anthropic-beta` list on the sampled request is shorter than the one captured at 12:40** and
is missing `claude-code-20250219`. ***That is the warm-up being a `haiku` call, not the flag.*** *The
client's beta assembly pushes that entry only when the model name does not contain `haiku`.*
**The list was already ruled out as a discriminator and nothing here revives it.**

### What the run does settle, and it is worth more than it looks

**Quota is dead as a hypothesis, twice over.** *The earlier control had the meter at 52% and 59%;
this one has it at **0.11 and 0.01** — an all-but-empty budget — and the rejections are identical.*
**Anybody reading the upstream issues should be given this pair rather than either half.**

## The attribution header is not a header, and two sessions of this phase were spent on that

***Retraction, 2026-09-18.*** **The section above claimed the classifier "is the one request shape
that forces the attribution header".** *The name `forceAttributionHeader` is the client's own and it
is misleading; the claim built on it is withdrawn, and what replaces it is measured rather than
read.* **Evidence: `evidence/attribution-is-a-body-field-2026-09-18.txt`.**

### What `g7t` actually returns

**A string, which becomes a system-prompt text block in the request *body*:**

    x-anthropic-billing-header: cc_version=2.1.267.0a3; cc_entrypoint=sdk-cli;

***That is JSON, inside `system`. It is not an HTTP header and it never was.*** **`claude --debug
api` prints it as "an attribution line" and this phase read that as a header** — the misreading is
in the 2026-09-18 notes above, and **it survived a capture that looked for the name among
twenty-one arriving headers and correctly did not find it.** *The absence was read as "withheld" when
it meant "wrong channel".*

***So C2d could not have worked.*** **It added an HTTP header of a name the client never puts in a
header.** *The negative result was real; what it tested was not the thing.*

### What the corpus says, and it cost nothing to ask

**`ilirium-llm-router extract --format bodies` over `logs/corpus/2026-09-18`** — material already on
disk, no session driven, no request sent:

| | |
|---|---|
| Requests carrying an attribution line, **whole day** | **2** — both the `-p` probes, `cc_entrypoint=sdk-cli`, streamed |
| The classifier request at 14:52, **flag on** | `claude-sonnet-5`, `max_tokens: 64`, **`stream` absent**, 2 system blocks, ***no attribution*** |
| Any request from an **interactive** session | **none carries one**, either shape, flag or no flag |

***This is `for-the-owner.md` entry 3 paying out a second time*** — the corpus answering a question
nobody had when it was built, three weeks and one wrong hypothesis later. **`BKL-0017` should know
about it.**

### The shape of the mistake, because it is the same one twice

**Entry 5 was "Anthropic sent this" read as "Anthropic is at fault". Entry 12 was a confirmed
mechanism read as a confirmed cause. This is a confirmed *name* read as a confirmed *channel*.**

***All three are the same move: a real observation carrying a claim it does not make.*** *And this
one had a free check available from the first hour — the corpus stores bodies, the bodies were on
disk, and nobody looked because the word in the name was "header".*

### What survives, and it is less than was claimed

**The gate is real and the flag works** — `x-client-request-id` arrives, measured, and that stands.
**What does not survive is the reason the flag was worth running.** *The attribution fields it
restores go into a block the classifier does not carry at all.*

**Hypothesis thirteen is eliminated, and more cleanly than C2d eliminated it:** the attribution
content is not the cause, **because the classifier sends none in either configuration.**

## The sampler key, chosen by the owner and wider than what was offered

**2026-09-19, before the hosts experiment ran.** *`for-the-owner.md` entry 11 put three options up
and the owner took none of them whole.* **What was built is `(path, streamed?, size band)`.**

**The band is the decimal order of magnitude** — `323 -> 2`, `127_949 -> 5` — computed from the
decimal string rather than `log10`, which is exact at a power of ten where a float is not.

***The part that was not in any of the three options: the path moved into the key.*** **It had been
a gate** — `request.url.path.startswith("/v1/messages")`, which was entry 6's fix for the latch
being spent on `/api/hello`. *A gate is the same advance decision one level up: it does not choose
which request is interesting, it chooses which **path** is, and nothing had established that the
interesting request would always be on `/v1/messages`.* **`/api/hello` is now sampled in its own
right rather than excluded, and it still cannot take another shape's slot.**

### The bound, which the owner did not ask for and was told about rather than given

**`app.py` registers a catch-all `/{path:path}`**, so the path in the key is whatever a caller
types. *The old structure was a dict of two hardcoded keys and could not grow; this one accumulates
one entry per distinct shape seen, for as long as the process runs.* **It stops at
`ARRIVAL_SAMPLE_CAP = 64`.**

***And reaching the cap is announced on its own log line.*** **That line is the point, not the
cap.** *A bound that hides itself is an instrument that quietly stops looking while every line
already in the file reads as though it were still watching — which is this phase's recurring defect
and would have been its fourth instance.*

### A test of mine passed a mutation, and it is the fourth instance of the same shape

**`test_the_probe_endpoint_cannot_spend_the_messages_latch` survived a mutation that deleted the
path from the key entirely.** *Its two requests are a bodiless `GET /api/hello` and a 71-byte
`POST /v1/messages`* — **different size bands**, so with the path gone they were still two shapes
and the test still passed. ***It asserted the right thing and proved none of it.***

**Caught by the harness and by nothing else.** *The test was green, the code it was written against
was correct, and reading it would not have shown this — the flaw is in the relationship between two
fixture values, not in either the test or the code.* **`test_the_path_is_part_of_the_shape_key`
varies nothing but the path.**

*The mutation's `why` line records that it survived once and why, per the harness's own rule that a
surviving mutation is a prompt to read the mutation first and the test second.* **Here the mutation
was right.**

### What it cost and what is green

**480 tests** — five new, one rewritten — **32/32 mutations** (eight new, one replaced: the old
"one arrival latch instead of one per shape" was anchored on a line this change deleted, and an
unapplicable mutation is a failure of the harness rather than a pass of the test set). **`make lint`
clean at the pinned `0.16.1`.**

***`src/` is otherwise untouched*** — checked with `git diff --stat`. **Entry 7's three live
experiments are unaffected**, and the router is run from source, so `make run-hosts` picks this up
with no rebuild and entry 14's setup needs no change.

***Not yet driven against a running router.*** **The tests exercise the real app through
`TestClient`, which is the whole stack short of a bound port and a log file on disk** — so what is
unproven is the line reaching `logs/telemetry/router.log`, not the line itself. *`CLAUDE.md` says
ask before starting a local server, and the owner's experiment was about to bind the machine.*

## The hosts experiment ran, looped, and the guard for the loop was decorative

**2026-09-19, run by the owner. No measurement.** *Every step taken was the one the runbook asked
for.* **`logs/telemetry/router.log` holds the whole shape of it:**

| | |
|---|---|
| **12:05:00** | Step 4's `curl --resolve` → `/api/hello` → **200**, 252 ms — the real Anthropic |
| **12:07:46** | Session starts, hosts line in → **every request 502**, `transport_error connect_error`, **4–9 ms** |
| | **67 × 502, no success.** 70 calls arrived, 70 recorded, 0 lost |
| **12:12:37** | After teardown, `/api/hello` → **200** again |

***4–9 ms is a local connection.*** **The router resolved `api.anthropic.com` to `127.0.0.1`,
connected to the terminator, and rejected its mkcert certificate** — `unable to get local issuer
certificate`, Python's `certifi` bundle having no local CA. ***The loop `run-pinned.py` exists to
prevent, entered anyway.***

### uvloop does not call `socket.getaddrinfo`

**`run-pinned.py` patched `socket.getaddrinfo`.** *`uvicorn.run` takes `loop="auto"`, uvloop is
installed, and `Config(loop="auto").get_loop_factory()` returns `uvloop.Loop`.* **uvloop resolves
natively and never calls the patched function**, so the pin was inert from the first request.

***Measured, not reasoned about.*** *Patch `socket.getaddrinfo`, then call `anyio.getaddrinfo` —
which is the path `httpx` takes — under each loop in turn:*

| Loop | Patch called |
|---|---|
| plain `asyncio` | **yes** |
| `uvloop` | **no** |

**Fixed by patching `uvloop.Loop.getaddrinfo` as well.** *The class accepts attribute assignment,
checked before relying on it.* ***Forcing `loop="asyncio"` was the alternative and was not taken***
— it would change the loop the experiment runs on, and this phase has spent a fortnight removing
one variable at a time.

### The decorative guard, which is the part worth keeping

***`print(f"[pinned] ...")` ran unconditionally, before anything was resolved.*** **The runbook said
to stop if that line was missing. It was not missing. It had never meant anything.**

***And step 4 cannot test the pin at all.*** **It runs before `/etc/hosts` exists**, and until the
hosts entry is in, a pinned router and an unpinned one resolve identically and both reach Anthropic.
*The 12:05 green and the 12:12 green are the same fact as each other, and neither is the pin.*

**`verify_the_pin` resolves the name through the router's own event loop and refuses to start unless
the patch is observed returning the answer.** ***Two facts, not one*** — the address has to be right
**and the patched resolver has to have fired** — *because with no hosts entry an unpatched lookup
returns the right address too, which is step 4's blindness one level in.*

**Exercised by reintroducing the exact defect.** *Patch only `socket.getaddrinfo`, as the file did
yesterday:* ***the address came back correct — `160.79.104.10` — and the check refused anyway***,
naming the loop that ran. **An address-only check would have passed.**

*Also checked: the pin verifying for real, `main()` end to end against a missing config so nothing
binds, and the loopback guard still returning 2.*

### A documentation defect found while correcting the runbook

**Entry 14 said a plain `dig` would answer `127.0.0.1` once the hosts entry was in.** ***It would
not — `dig` does not read `/etc/hosts` at all***, it queries a nameserver directly. *Checked against
`broadcasthost`, which `/etc/hosts` maps to `255.255.255.255` and `dig` cannot see while
`dscacheutil` can.*

**`@1.1.1.1` stays**, on the other grounds: it makes the answer independent of a VPN or corporate
resolver. ***The advice held and the reason given for it did not***, which is the same shape as the
`git add -A` warning `status.md` records dropping.

### What the failed run did produce

***The sampler keyed the same morning paid for itself in the run that failed.*** **18 arrival lines
where the old code would have produced 2**, every request sampled before its 502: the **323-byte**
non-streamed warm-up, `/v1/messages` streamed at **4,168** and **118,395** bytes as two bands, and
***eleven API paths this phase had never seen*** — `/api/claude_cli/bootstrap`, `/api/oauth/usage`,
`/v1/ultrareview/quota`, `/mcp-registry/v0/servers`, `/api/claude_code_penguin_mode`, and
`/api/event_logging/v2/batch` at **435,666 bytes**. **The old path gate hid all eleven.**

***The 127 KB non-streamed classifier is still unsampled.*** **The session died before auto mode
classified anything** — so entry 11's question is open for a new reason rather than the old one.

## The hosts experiment ran and the 429 is gone — the phase's central result

***Run by the owner 2026-09-19, 12:30–12:37 UTC, Claude Code 2.1.267*** — the same build as every
run of 2026-09-18, so **no part of this is a client version difference.** *`ANTHROPIC_BASE_URL`
unset, auto mode on, the router unchanged on 8787 behind the terminator.*

**Zero `429`s.** *The single `429` a grep finds in the log is the millisecond field of a timestamp.*

### The paired control, from `logs/corpus/*/index.csv`

| | **2026-09-18** — `ANTHROPIC_BASE_URL` set | **2026-09-19** — hosts route, base URL unset |
|---|---|---|
| Non-streamed `/v1/messages` over 100 KB | **125** | **9** |
| Outcome | **119 × `http_error`**, 6 `client_disconnect` | ***9 × `ok`*** |
| System blocks in the request | **2** | **3** |
| The attribution block | ***absent in all 125*** | ***present in all 9*** |

**Same credential, same machine, same router build, same egress.** *`config-hosts.yaml` names
`https://api.anthropic.com` directly with no forwarder hop, so the router's own `httpx` made the
outbound TLS connection on **both** days.*

### `BUG-000`'s trap is satisfied rather than dodged

***A quiet session looks exactly like a fix, so the classifier was identified rather than assumed.***
**Three independent marks, all from the wire or the stored body:**

- ***`anthropic-beta` carries `auto-mode-classifier-2026-07-16`*** on those requests — the client
  naming the thing itself
- The system prompt opens **"You are a security monitor for autonomous AI coding agents"**
- `max_tokens: 64`, **`stream` absent entirely**, one message, ~128 KB

**Nine of them, each answered in about 340 bytes.** *This is auto mode classifying and being
answered, not a session that merely failed to fail.*

### What this establishes

***The router does not cause the rejection.*** **The same router, the same `httpx` egress, the same
TLS fingerprint presented to Anthropic, carried nine classifier calls successfully today and was
rejected 119 times yesterday.** *The difference lies entirely in what Claude Code put in the
request.*

***Both of entry 8's remaining hypotheses fall out of this for free, and both were named as
expensive:***

| | Why it is eliminated |
|---|---|
| **The TLS fingerprint** | **Anthropic saw the *router's* fingerprint on both days.** Same fingerprint, opposite outcomes |
| **Connection reuse** | The router pooled its own connections identically on both days |

### What this does NOT establish, said plainly because the temptation is the same one as last time

***The attribution block is the leading candidate and is NOT shown to be the cause.*** **Several
things change together when `ANTHROPIC_BASE_URL` goes away**, and this phase has already read a
confirmed mechanism as a confirmed cause once — entry 12 — and a confirmed name as a confirmed
channel — entry 13.

**What narrows it usefully is the 2026-09-18 flag run:** `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1`
**restored `x-client-request-id` and the 429 did not move**, so that field is eliminated. *The
attribution block is the one known content difference that survives into today's success.*

### Two things read out of the bodies that bear on entry 7

**The real value is `cc_version=2.1.267.608; cc_entrypoint=cli; cch=<per-request hash>`** — seven
distinct `cch` values across nine requests, so it is computed rather than static.

***The imitation experiment was fabricating a value that does not match the real one.***
`BILLING_VERSION_SUFFIX = "0a3"` against the real **`.608`**, and `cc_entrypoint=sdk-cli` against the
real **`cli`**. **So C2d was wrong in three ways at once** — wrong channel, wrong version suffix,
wrong entrypoint — *and entry 13 had already established the first.*

### How the corpus was read

***`ilirium-llm-router extract --format bodies --path /v1/messages`, over both day folders.***
*Material already on disk; no session driven and no request sent.* **This is the third time entry 3's
observation has paid out** — and the first time the tools were driven against a question the same day
it arose.

### The verdicts themselves, because "200" is not the same as "it classified"

***Nine responses, decompressed out of the corpus and read.*** **Every one carries a real
classification**, not an error with a 200 on it:

| | |
|---|---|
| `<block>no` | **five times** — `stop_sequence: </block>` |
| `<severity>10`, `15`, `18`, `25` | **four times** — `stop_sequence: </severity>` |

*Each with a distinct `msg_` id and a plausible `input_tokens` (90 for the severity calls, 158 for
the block calls).* **So the classifier ran, was answered, and returned a decision.**

***The response bodies are brotli — entry 7's standing cost, met in practice.*** *`zstandard` opens
the blob and hands back bytes that are still compressed; `brotli` is not in the venv and was
supplied in an ephemeral overlay rather than added to the project.*

## A router defect the first-party client exposed, and an observation I cannot explain

***Two requests in that run were rejected by the router itself***, `400`, with
**"The request body carries no 'model' field."** *They are the only non-`ok` outcomes of the day.*

***Both bodies are gzip-compressed.*** **Magic `1f8b0800`.** *Decompressed, they are perfectly
ordinary:*

| Stored | Decompressed | What it is |
|---|---|---|
| **2,152 B** | 4,425 B | The **title-generation** call — `claude-haiku-4-5`, and its text is the owner's own first prompt |
| **40,541 B** | 118,560 B | A **main conversation turn** — `claude-opus-5`, `max_tokens: 64000`, streamed |

***So the model peek is reading compressed bytes and finding no `model` key.*** **`routing.py`'s
prefix rule never gets a chance.** *The client retried both uncompressed — the 4,168-byte and
118,395-byte streamed arrivals twelve milliseconds later are the retries — so the session continued
and nothing was lost.*

***This is new because the client is first-party.*** **A client pointed at a custom
`ANTHROPIC_BASE_URL` has never gzipped a request body in any capture this phase holds**; one that
believes it is talking to Anthropic does. **It is a real defect in `src/` and it is not fixed here**
— `CLAUDE.md` says propose before implementing, and it is the owner's call whether it belongs in
this phase at all.

### The thing that does not add up, said rather than smoothed over

***The owner's own session transcript for that window reports the classifier FAILING*** — 
`claude-opus-5[1m] is temporarily unavailable, so auto mode cannot determine the safety of Bash` —
**four times out of ten probes, at 15:31–15:32 local, which is 12:31–12:32 UTC.**

***The router's record for that same session and those same two minutes shows six classifier calls,
all `200`, all carrying verdicts.*** **And no request naming `claude-opus-5[1m]` reached the router
at all** — zero occurrences of `1m` in the whole of `calls.csv`.

**So the failures the owner saw produced no request that this router ever received**, and the only
two requests it rejected were the gzip pair above, neither of which is a classifier call.

***I cannot close that gap from here and am not going to guess at it.*** *Three shapes it could
have — the failing attempts never leaving the client; a second session not traversing this router;
or the `[1m]` variant being genuinely unavailable upstream and unrelated to `BUG-001`* — **and
nothing on disk distinguishes them.** **Put to the owner as entry 18.**

***What it does not touch:*** **the nine successful classifications and the zero 429s are measured
and stand.** *What is now uncertain is whether auto mode was usable end to end, which is a stronger
claim than the one the paired control makes.*
