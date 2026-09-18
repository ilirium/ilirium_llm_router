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
