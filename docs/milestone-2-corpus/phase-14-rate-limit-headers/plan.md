# Phase 14 — the Anthropic rate-limit response headers

**Branch:** `feat/phase-14-rate-limit-headers`, forked from `main` at `ac2976e`.
**Merge commit:** *not yet merged.*

**A `feat/` phase: it changes `src/`.** The work is `BKL-0034`, added 2026-08-24 as the reversal of
`BKL-0037`, and the milestone plan has carried a section for it since 2026-08-25.

---

## What this phase is, and it is not what the milestone plan says

**The milestone plan scopes Phase 14 as an instrument** — record `retry-after` and the
`anthropic-ratelimit-*` family, because two upstream issues stall on that measurement. **The owner
reshaped it on 2026-09-18 around a live symptom instead:** Claude Code's auto mode cannot run its
safety classifier through the router, because the classifier's request comes back `429`.

**The instrument is unchanged; what changed is what it is for and therefore what order it is built
in.** Recording the headers is now the means of diagnosing `BUG-001`, not a deliverable that
happens to be useful later. **The consequence is the one thing to carry out of this section:** the
durable home for the headers — the question the milestone plan says this plan cannot skip — is
**deliberately deferred to Group D**, because the diagnostic form needs no schema at all and
answering it now would be choosing a shape before knowing what the values look like.

### What the session of 2026-09-18 established before any code was written

**All of it came off disk, from telemetry and corpus material already captured.** No request was
sent and no credential was used. *This section is evidence, not narrative: Group C's measurement is
designed against it and Group D's decision rests on it.*

| | |
|---|---|
| **The classifier is identified** | `max_tokens: 64`, two messages, ~140 KB, system prompt opening *"You are a security monitor for autonomous AI coding agents"*. **It omits `stream` entirely**, so it goes upstream non-streamed |
| **The quota probe is a second casualty** | `{"model":"claude-opus-5","max_tokens":1,"messages":[{"role":"user","content":"quota"}]}` — 311 bytes, rejected in ~450 ms on three separate days |
| **Anthropic answers the 429 itself** | Every rejection body carries a distinct `request_id` — `req_redacted0000000000000001` and others. **The router is not inventing it**, and no edge or WAF layer is in the way |
| **Size is not the variable** | 311 bytes rejected; 181,083 bytes accepted non-streamed on 2026-08-21, TTFB 12 s, 639 output tokens |
| **The router forwards the credential untouched** | `credential: forward`, an OAuth subscription token — `anthropic-beta: oauth-2025-04-20` |

**The shape counts, over four days of real traffic in `to-run-server/logs/telemetry/calls.csv`:**

| Shape | Calls | 429 |
|---|---|---|
| `/v1/messages` **non-streamed** | 114 | **95** |
| `/v1/messages` **streamed** | 820 | **0** |
| `/v1/messages/count_tokens`, also non-streamed | 66 | **0** |

*These extend `BUG-001`'s frozen slice by one day — 2026-08-26 — and replace its reconstruction of
which request shape fails with the captured bodies of the failing requests themselves.*

**The record is three weeks old.** Newest row 2026-08-26; today is 2026-09-18. Claude Code and the
router have both moved. **Group C re-establishes the symptom before Group D reads anything into
it**, and if it no longer reproduces that is a finding rather than a failed phase.

### The two hypotheses this phase exists to separate

**Neither can be chosen from what is on disk**, because the response headers were never recorded —
which is `BUG-001`'s own stated limit, *"reconstruction rather than measurement."*

| | What the headers would show |
|---|---|
| **H1 — Anthropic restricts non-streamed `/v1/messages` on a subscription credential** | A `rate_limit_error` carrying **no `anthropic-ratelimit-*` headers at all**, or headers showing every bucket with headroom. *A 429 that names no exhausted bucket is not a rate limit* |
| **H2 — something the router does to the request provokes it** | An exhausted bucket, naming which. The only unforced change the router makes is `accept-encoding: identity` (`proxy.py:441`); everything else it drops is a connection header |

***H1 and H2 are not exhaustive and the plan does not pretend otherwise.*** They are the two the
evidence supports; the measurement is designed to report what is there rather than to decide
between two named outcomes.

---

## What is settled, and by whom

| # | Position | Settled by |
|---|---|---|
| 1 | **Phase 14 is the rate-limit headers**, opened rather than any other candidate | Owner, 2026-09-18 |
| 2 | **The phase is reshaped around `BUG-001`'s symptom** — diagnose first, with the recorder as the instrument | Owner, 2026-09-18 |
| 3 | **The minimal form is built first**: a named allowlist logged on a non-2xx reply, no schema change | Owner, 2026-09-18 |
| 4 | **The durable home is deferred to Group D**, after the measurement | Owner, 2026-09-18 — *this is the milestone plan's "cannot skip" question, deferred rather than skipped* |
| 5 | **A named allowlist, never a copy of the response headers** | `../implementation-plan.md`, standing constraint. Not this phase's to reverse |
| 6 | **`calls.csv` taking new columns is a Milestone 2 non-goal** | `../implementation-plan.md`. **Still standing** — Group D may put it to the owner, and only the owner can overturn it |

**Unratified, and marked so rather than inherited** — per `../../method/IDM-004-reviewing-unexecuted-work.md` and `BKL-0001`:

| Position | Whose |
|---|---|
| That header **names** may be logged where values may not, so an unknown bucket becomes visible without recording its value | **This plan's own.** Group B implements it; it is the one design judgement made without the owner and it is flagged here rather than buried |

---

## The task groups

**Group C is the owner's and cannot be run by a session** — it needs a real Claude Code session
against the real credential. The plan stops at its boundary and says so.

### Group A — open the phase

| Task | |
|---|---|
| **1** | This plan, the worktree and the branch. `for-the-owner.md` opened at the same time, per `IDM-010` |
| **2** | Re-derive this plan against the code before Task 3, per `../../README.md` — *four of six Milestone 1 phases found their own plan wrong on contact* |

### Group B — the instrument, in its minimal form

| Task | |
|---|---|
| **3** | `RECORDED_RESPONSE_HEADERS` in `proxy.py` and the extraction function beside `response_headers` |
| **4** | The log line, at `WARNING`, emitted only when the reply's status is **`>= 400`** — *this row said "not 2xx" until Task 2, which is a different set: it includes 3xx, and the register said `>= 400` in the same document* |
| **5** | Tests: an allowlisted header is recorded with its value; a header outside the list has **only its name** recorded; a 2xx reply logs nothing |
| **6** | **Exercise it before committing** — make the extraction wrong and confirm each test fails. `CLAUDE.md`, and Phase 13 shipped three checks that passed while testing nothing |

### Group C — reproduce and measure *(the owner's)*

| Task | |
|---|---|
| **7** | Drive one Claude Code session through the router with auto mode on. **Record the Claude Code version** — `BUG-001` asks for it, and it is the only thing that will identify a client-side fix |
| **8** | Read the logged headers off `router.log`. **Freeze them into `evidence/`**, redacted per `../../README.md` — a measurement that lives only in one worktree's gitignored `logs/` discharges nothing, which this milestone has recorded once already |
| **9** | Decide H1 / H2 / neither, in `notes.md`, from the values rather than from the absence of a failure. ***An absence of 429s proves nothing*** — `BUG-000`, and a quiet session looks exactly like a fix |

### Group D — the durable home *(blocked on Group C)*

| Task | |
|---|---|
| **10** | Put the home question to the owner **with the measured values in hand**: a sidecar telemetry file, the corpus day index, or overturning the `calls.csv` non-goal. *Settled position 6 says only the owner can overturn it* |
| **11** | Build whatever was chosen, with its register rows and its schema version if it has one |

### Group E — close

| Task | |
|---|---|
| **12** | `BUG-001` updated with what was measured — and **reported upstream**, which is its own open action and `status.md`'s item 2 |
| **13** | The register checked against the code, `❓` column empty, per `IDM-008` |
| **14** | The review of this phase's finished work, under `IDM-009` |
| **15** | Close out: `status.md`, the milestone plan's Phase 14 section and its Record table, `branch-index.py --write` after the merge |

---

## The register — every name and number this phase introduces

*`IDM-008`. Compiled before Task 3, which is what the rule asks and what Phase 10 did not do.*

### Module constants — `src/ilirium_llm_router/proxy.py`

| Name | Value | |
|---|---|---|
| `RECORDED_RESPONSE_HEADERS` | `frozenset` of the exact lowercase names below | The allowlist. **Exact names, never a prefix match** — settled position 5 |
| `RECORDED_HEADER_PREFIX` | `"anthropic-ratelimit-"` | **Names matching this and absent from the allowlist have their name logged and their value discarded.** The unratified position above |

**The allowlist's members**, and every one is a response header Anthropic documents:

| | |
|---|---|
| `retry-after` | Seconds until the call may be retried |
| `anthropic-ratelimit-requests-limit` · `-remaining` · `-reset` | The request bucket |
| `anthropic-ratelimit-tokens-limit` · `-remaining` · `-reset` | The combined token bucket |
| `anthropic-ratelimit-input-tokens-limit` · `-remaining` · `-reset` | The input bucket |
| `anthropic-ratelimit-output-tokens-limit` · `-remaining` · `-reset` | The output bucket |
| `request-id` · `anthropic-request-id` | ~~❓~~ **In, both spellings. Closed at Task 2.** The id is in the error *body*, which is how this session identified the 429 as Anthropic's own — but **the body is only on disk when the corpus is enabled, and it is off by default.** The log line has to stand on its own, so the id is worth its row. Both spellings because which one arrives is not known from here, and neither can carry a secret |

*Seventeen names. **`authorization`, `x-api-key` and `set-cookie` are named here as the things the
list exists to exclude** — a response carries no credential today and the allowlist is what keeps
that true when one day it does.*

### Functions and classes

| Name | |
|---|---|
| `recorded_headers(reply) -> tuple[dict[str, str], list[str]]` | Beside `response_headers` in `proxy.py`. **Reads a reply it does not modify** — the relayed bytes are untouched, which is byte-relay and not negotiable. *Returns two things, not one: the allowlisted headers with values, and the names of unlisted `anthropic-ratelimit-*` ones* |
| `describe_headers(recorded, unlisted) -> str` | The log line's payload. **`(none)` when a reply carried neither**, because that is the interesting case and a blank would read as a logging failure |
| `Once` · `Once.take() -> bool` | **Added after the first measurement**, not in the original plan. A latch that is true exactly once. Mutable, held by the frozen `Proxy` the way `Counters` already is |
| `Proxy.headers_sampled: Once` | The control's latch. *Also added after the measurement — see the row below* |

### Names it must not collide with

| Existing | |
|---|---|
| `DROPPED_FROM_RESPONSE` | The **relay** allowlist's inverse — what the client does *not* receive. Unrelated to this phase's list and must not be confused with it: one governs what goes out, the other what is written down |
| `response_headers()` | The relay's header function. The new one sits beside it and shares no code |
| `CREDENTIAL_HEADERS` | Request-side. Named because the temptation is to reuse it |

### Numbers and shapes

| | Value |
|---|---|
| Log level for the failure line | `WARNING` |
| Status range that triggers it | `>= 400` — *matching `relay`'s existing `reply.status_code >= 400` branch rather than inventing a second threshold* |
| **Log level for the control line** | **`INFO`** — *nothing is wrong when it fires* |
| **How often the control fires** | **Once per process**, on the first reply that is **not** an error. *A failure must not consume the latch: the real session of 2026-09-18 opened with a burst of 429s, and a latch a failure could take would have sampled nothing* |
| New config keys | **None.** The minimal form is deliberately not configurable |
| New on-disk names | **None in Group B.** Group D may add one, and its rows are written then |
| Index schema version | **Unchanged at `1`.** Group B touches no index. *If Group D reaches the corpus index this becomes `2`, and that row is written then* |

---

## Done when

- The headers on a real 429 have been **seen, frozen into `evidence/`, and read** — Group C.
- **`BUG-001` says which of H1 / H2 / neither the values support**, or says explicitly that it no
  longer reproduces and on which versions.
- The durable home is chosen **by the owner** and built.
- The register's `❓` column is empty and Task 13 has checked it against the code.

## Not in this phase

- **Fixing whatever the diagnosis finds**, if the fix is client-side or Anthropic's. *This phase
  measures and reports; `BUG-001` is a bug the router did not cause and may not be able to fix.*
- **Changing the relay.** Nothing here alters a byte the client receives.
- **`BKL-0017`**, whether archiving slows a call — the milestone's third failure mode, and a
  separate measurement.

## Reading

- `../../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md` — the symptom, and what it
  already rules out
- `../implementation-plan.md`, Phase 14's section — the constraint and the deferred question
- `../../backlog.md` — `BKL-0034`, and `BKL-0037` for why the refusal was reversed
- `../../reference/corpus.md` — *"Bodies only. Never headers"*, the sentence this phase walks up to
- `../../method/IDM-008-the-register.md` — before Task 13
