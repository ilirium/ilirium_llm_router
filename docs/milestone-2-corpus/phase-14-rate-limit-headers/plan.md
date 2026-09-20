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

***Resolved 2026-09-18, and not the way the measurement first suggested — H2.*** *The headers came
back matching H1's signature exactly: a `rate_limit_error` naming no exhausted bucket, on a
connection whose successful calls carry twelve. **That was read as H1 and it was the wrong
reading.*** The owner then supplied the control nobody had run: **the classifier works when Claude
Code talks to Anthropic directly and fails through the router**, on the same credential, machine,
client version and afternoon.

**So H1's evidence is real and H1's conclusion does not follow.** *"Anthropic sent this rejection"
and "Anthropic is at fault for it" are different claims, and only the first was measured.*
`BUG-001`'s own dismissal of the router turns out to be circular — it compares streamed against
non-streamed **inside** the router — and is retracted on this branch.

**The constraint any explanation must satisfy: 820 streamed calls through the router succeeded.**
So it is the router **and** a non-streamed request together, which rules out everything that would
apply to every call the router makes.

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
| **7** | ***Done 2026-09-18, five times.*** Drive one Claude Code session through the router with auto mode on. **Record the Claude Code version** — `BUG-001` asks for it, and it is the only thing that will identify a client-side fix. *It is **2.1.267** throughout* |
| **8** | Read the logged headers off `router.log`. **Freeze them into `evidence/`**, redacted per `../../README.md` — a measurement that lives only in one worktree's gitignored `logs/` discharges nothing, which this milestone has recorded once already |
| **9** | Decide H1 / H2 / neither, in `notes.md`, from the values rather than from the absence of a failure. ***An absence of 429s proves nothing*** — `BUG-000`, and a quiet session looks exactly like a fix |

### Group C2 — thirteen hypotheses, eliminated one at a time *(not planned; it happened)*

***This group was not in the plan and is written down after the fact.*** *The phase was chartered
to record the headers; recording them produced a finding, the finding turned out to rest on an
unrun control, and the owner ran it. What follows is what that cost.*

| Task | | Result |
|---|---|---|
| **C2a** | Relay the caller's `accept-encoding` instead of forcing `identity` | **negative** — and it left the corpus storing non-streamed bodies **brotli-compressed** |
| **C2b** | Offer HTTP/2 — `h2` declared, `http2=True` | **negative** |
| **C2c** | Capture what Claude Code sends the router, per shape | **the router alters nothing** — nothing dropped, nothing added |
| **C2d** | Supply the attribution headers Claude Code withholds from a custom base URL | **negative**, twice — the second time with a legal header |
| **C2e** | Capture both TLS `ClientHello`s — `evidence/clienthello-capture.py` | **the premise holds**: the two are trivially distinguishable |
| **C2f** | A BoringSSL egress hop — `evidence/boringssl-forwarder.py`, `make forwarder` | **negative** — a Chrome fingerprint is rejected exactly as Python's is |

| **C2g** | `_CLAUDE_CODE_ASSUME_FIRST_PARTY_BASE_URL=1`, the client's own first-party override | **the flag reaches the wire** — `x-client-request-id` arrives for the first time — **and the 429 does not move** |
| **C2h** | Read the **client** instead of the router — `evidence/binary-extract.sh` | ***the "attribution header" is a body field***, so `C2d` tested the wrong channel entirely |

***Nothing from C2a, C2b or C2d is reverted.*** **Owner's decision, 2026-09-18: they stay for
further experiments on this branch.** *Their costs are real and are recorded in `notes.md` —
`accept-encoding` most of all.*

***REVERSED 2026-09-20, and the reason is different from the one that put them here.*** **All three
come out before the merge** — owner's decision: *an experiment that failed is dead code on the
trunk, and dead code does not improve readability.* **The 2026-09-18 reason was reproducibility**,
and it is met a different way: **once this branch is merged the switches live in history**, so a
negative result can be re-run from `git show` without any of it sitting in `src/`. *Merging is what
makes deleting them safe, which is why the two decisions arrived together.* → Group E, task **16**.

### Group C3 — the hosts experiment *(BUILT 2026-09-18, NOT RUN; the owner's)*

***Added after the fact, like C2.*** *The owner chose it over patching the client binary; `CE()`
reads `ANTHROPIC_BASE_URL` directly, so leaving it unset is what makes the client first-party and a
hosts entry does that with nothing modified.*

| Task | | |
|---|---|---|
| **C3a** | `evidence/tls-terminator.py` — the router has **no TLS**, and 443 is privileged | built, **not run** |
| **C3b** | `evidence/run-pinned.py` — `/etc/hosts` is machine-wide, so the router would resolve `api.anthropic.com` to **itself** | built, **guards exercised** |
| **C3c** | `config-hosts.yaml` and `make run-hosts` — *the egress hop removed and **the corpus ON***, without which the run captures no bodies | built |
| **C3d** | Run it. ***`for-the-owner.md` entry 14 is the runbook*** — and **the hosts line redirects the owner's own session**, so `curl --resolve` proves the chain first | ***RAN 2026-09-19 and LOOPED.*** **67 × 502, no measurement** — `run-pinned.py` patched `socket.getaddrinfo` and the router runs under **uvloop**, which never calls it. Entry 16 |
| **C3f** | ***Fix the pin and give it a check that can fail.*** `uvloop.Loop.getaddrinfo` patched too, and `verify_the_pin` refuses to start unless the patched resolver is **observed** returning the answer | **done**, exercised by reintroducing the defect: **the address came back correct and the check still refused** |
| **C3g** | Re-run it | ***RAN 2026-09-19 12:30 UTC. **The `429` is gone** — 9 classifier requests, **9 × `ok`**, zero 429s on the same client build that produced 119 rejections the day before*** |
| **C3l** | ***Re-run with the experiments off.*** **The classifier works** — 35 calls, 16 classifier calls, all `ok`, and a **blocked** probe carried through the router | **done 2026-09-19.** *The second defect was `accept-encoding`, ours, and "exonerated" was a clearance against the 429 allowed to stand for the component* |
| **C3k** | ***Fix the gzip `400`.*** A first-party client compresses some request bodies; the model peek was reading compressed bytes and refusing valid requests for a field they carry | **done.** *Decode a throwaway copy, relay the original, cap the inflation, and say which failure it was* |
| **C3j** | ***The 429 was masking a second defect.*** The owner's three transcripts, aligned against the router's record, show **every classifier request the router answered `200` matching a call the client called unavailable** | **recorded, not fixed.** *Entry 19; the suspect is C2a and the test is one line of `src/`* |
| **C3i** | ***Two things the run turned up that the plan did not ask for*** — a **gzip-encoded request body the router `400`s** because the model peek reads compressed bytes, and the owner's transcript reporting the classifier unavailable while the router logged six successful classifications | **raised, not fixed.** *Entry 18; the first changes `src/` and the second is unexplained* |
| **C3h** | ***Read the result against 2026-09-18, from the corpus*** — same credential, same router, same egress, and the attribution block **absent in all 125** rejections and **present in all 9** successes | **done.** *Entry 17; and entry 8's two expensive hypotheses fall out free — Anthropic saw the **router's** fingerprint on both days* |
| **C3e** | ***The sampler key, so this run can be read at all.*** `(path, streamed?, size band)`, bounded at 64 shapes with the stop announced. **Chosen by the owner 2026-09-19** from entry 11's three options, in a shape better than any of them — *the path became part of the key rather than a gate* | **done**, 480 tests, **32/32** mutations |

***If the 429 survives this, the entire client-side variable is eliminated*** and what remains is
the TLS fingerprint and connection reuse.

***It did not survive, so this sentence never came due.*** **C3g answered it — the 429 is gone** —
and *the two hypotheses it names were eliminated as a side effect rather than by a test*: Anthropic
saw the **router's own** TLS fingerprint on both days, and the router pooled its own connections on
both. **Neither needed the Bun build, and neither needed another session.** → `for-the-owner.md`
entry 17.

### Group C4 — supply what the client withholds *(not planned; it happened)*

***A child of C rather than a new letter, and the reason is precedent.*** **C2 and C3 were both
unplanned groups that grew out of the measurement, and both took their parent's letter and a
digit.** *This grows out of C3 in the same way — the hosts route is what made the block visible, and
this supplies it — so `C4` keeps every group's letter in execution order.* **`E` is already `close`
and a new top-level letter would have to run before it**, which is the thing the lettering exists to
prevent. *Tasks carry letter suffixes for the same reason C2's and C3's do: they were not numbered
in advance.*

***The goal is the product, not the diagnosis.*** **Owner's decision 2026-09-20: the router is to
work with `ANTHROPIC_BASE_URL` set**, which is how a person points a client at a proxy, and the
hosts route is a machine-wide edit that no user should need. *The subtractive test `BUG-001` asks
for — strip the block and see the 429 return — **is not run**: the additive version answers the same
question from the other side and leaves a working router if it succeeds.*

| Task | | |
|---|---|---|
| **C4a** | ***`src/ilirium_llm_router/backend_anthropic.py`*** — the block's constants and the one function that builds it. **A new module rather than more of `proxy.py`**, owner's decision 2026-09-20: *`proxy.py` is protocol-neutral and these are one backend's facts, hardcoded, with the docstrings carrying what was measured* |
| **C4b** | **`experiments.add_claude_code_hidden_attribution_block`**, `false` by default, named by `check` like the other three |
| **C4c** | ***Inject on non-streamed Anthropic requests that LACK the block, and on nothing else.*** *Streamed requests keep byte-relay and their prompt cache untouched; a request that already carries one is never touched* |
| **C4d** | Tests, **exercised by mutation** — `CLAUDE.md`, and this phase has now shipped five checks aimed at something other than what they claimed |
| **C4e** | ***Drive a session — the owner's, and it cannot be run by a session.*** **Condition A: no `cch`.** *Condition B, only if A fails: a `cch` as well.* **`BUG-000` applies — the run needs a probe that is genuinely BLOCKED**, not an absence of failures |
| **C4f** | Record the result in `notes.md` and `for-the-owner.md`, and say which condition answered it |

#### What goes in the block, and what deliberately does not

***Every row is measured, over 99 blocks on two corpus days.*** *Instrument:
`evidence/attribution-block-anatomy.sh`.*

| Field | | |
|---|---|---|
| `cc_version` | ***`2.1.267.608`, hardcoded*** | **The suffix is a call site, not a build number** — five values on one install in one day, and `.608` is every classifier request and nothing else. **It is in no header, no body field and no handshake**, so it cannot be derived. ***It is knowingly wrong for the haiku auxiliaries***, which send `.daa` and are also non-streamed; the docstring has to say so. *A model-to-suffix table would look like knowledge and be a guess from one day* |
| `cc_entrypoint` | ***`cli`, hardcoded*** | `sdk-cli` under `-p`, `cli` interactively. **The `-p` path is not the one that is broken** |
| `cch` | ***OMITTED in condition A*** | **Per conversation turn, not per request** — the classifier's two stages share one, and so do two main-conversation calls in one turn. **It cannot be computed.** *A hardcoded one would repeat on every request, which is visibly unlike a client that sent 74 distinct values in 97 blocks — so a stale `cch` is worse than none.* ***The two-field form is a shape the client itself sends***: the `-p` blocks carry no `cch` at all |
| `cc_prompt_id` | ***NEVER injected*** | **Neither kind of request this touches ever carries one** — 0 of 25 classifier, 0 of 14 haiku auxiliaries. *Adding one would make the request look **less** like the real thing, not more* |
| `cc_prev_req` | ***NEVER injected*** | The same, and worse: **it is a real `req_011C…` id Anthropic issued for the previous reply.** *Fabricating it invents an identifier that refers to something, which is the one kind of invention with no honest version* |

***So the injected block is two fields, and that is a shape the client sends.*** **Nothing here is
fabricated; the two hardcoded values are Claude Code's own, and the three fields we cannot know are
left out rather than guessed.**

### Group D — the durable home *(NOT STARTED, and still the milestone plan's "cannot skip")*

| Task | |
|---|---|
| **10** | Put the home question to the owner **with the measured values in hand**: a sidecar telemetry file, the corpus day index, or overturning the `calls.csv` non-goal. *Settled position 6 says only the owner can overturn it* |
| **11** | Build whatever was chosen, with its register rows and its schema version if it has one |

### Group E — close

| Task | |
|---|---|
| **12** | `BUG-001` updated with what was measured — ~~and **reported upstream**~~. ***The upstream report is WITHDRAWN, 2026-09-20***, owner's decision: **the bug is that the router cannot carry Claude Code's non-streamed requests**, and a cause that is client-side does not make it somebody else's to fix. *Enough detail stays in the document for anyone who wants to take it upstream later.* **Consequence: the isolation test is not worth a session**, so `relay_accept_encoding`'s authorship of the second defect stays an inference and the document must say so rather than state it as a finding |
| **12a** | ***Bring the durable tiers true — added 2026-09-18, because Group E did not have this task and a closing check that is nobody's task is nobody's.*** `reference/observability.md` describes a recorder that now reads response headers; `reference/corpus.md`'s *"bodies only, never headers"* is still true and **worth re-reading against what shipped rather than assumed to be**; `CLAUDE.md` and the root `README.md` carry the commands and the caveats. ***Only for what actually survives the merge*** — an experiment that is reverted changes none of them, and documenting a temporary state in `reference/` is worse than leaving it alone |
| **16** | ***Remove the three failed experiments*** — `relay_accept_encoding`, `http2_upstream`, `imitate_attribution_headers` — **and everything that exists only to serve them**: `config-boringssl.yaml`, `make forwarder`, `make run-boringssl`, and **five tests plus a `conftest.py` helper** (`test_cli_init.py:179` and `:195`, `test_cli.py:196` and `:206`, `test_proxy.py:169`, `conftest.py:115`). *Reversal of the 2026-09-18 position; see Group C2* |
| **17** | ***Graduate the survivor out of `experiments`*** into the Anthropic backend's own config, **if C4e answered yes**. *If it answered no it is removed with the other three and this row records that instead* — **either way the `experiments` block itself goes**, and with it `check`'s `EXPERIMENTS ON` line. ***Something at startup must still say the router is modifying requests***, because the survivor breaks byte-relay exactly as the experiments did, and `reference/design-decisions.md` has to record that exception |
| **18** | ***Promote the hosts-route tools rather than deleting them*** — `tools/tls-terminator/`, a `make` target, and the root `README.md` saying **why it exists and how to use it**: *the fallback for when the attribution trick stops working, and the instrument for finding out what replaced it.* **It is a pair, not a script** — the terminator needs `escape-the-hosts-file.py` beside it, or the loop closes and the router forwards to itself. *Renames: `evidence/run-pinned.py` → `escape-the-hosts-file.py`, `make run-hosts` → `make run-in-the-middle`* |
| **19** | ***Fix `branch-index.py` before task 15 needs it.*** **A branch fast-forwarded to trunk's tip and a branch cut from trunk's head with no commits are topologically identical**, so `resolve()` cannot tell `temp/to-run-server` from work in flight and `--write` drops its row — *the only record that the branch is not work.* **The fix is declarative**: the descriptions file already names branches by hand, so a branch is *declared* a worktree pin there and the tool honours it. → `for-the-owner.md` entry 4. *The never-delete guard is **`BKL-0041`** and is not this phase's* |
| **13** | The register checked against the code, `❓` column empty, per `IDM-008`. **`anthropic-ratelimit-unified-representative-claim` is expected to still carry its `❓`** — it closes when somebody establishes what the header holds, not when the phase ends |
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
| `PEEK_MAX_DECOMPRESSED` | `4 * 1024 * 1024` | **Added 2026-09-19.** How far a compressed request body may be inflated **to read `model` out of a throwaway copy**. *Real bodies are ~140 KB and the largest seen is 671 KB, so it is generous by six and still bounded — inflating caller-supplied bytes is the one place this router can be made to spend memory out of proportion to what arrived* |
| `PEEKABLE_ENCODINGS` | `frozenset({"gzip", "deflate", "x-gzip"})` | **Added 2026-09-19.** ***`br` and `zstd` are deliberately absent*** — neither is a dependency, Claude Code sends `gzip`, and **a wrong guess about a compression format looks exactly like a corrupt body**. An encoding outside this set is refused by name |
| `ARRIVAL_SAMPLE_CAP` | `64` | **Added 2026-09-19.** How many distinct arriving shapes are sampled before the sampler stops. *The shape key carries the request path and `app.py` has a catch-all route, so the key space is caller-chosen; the old two-key dict could not grow at all.* **Reaching it is announced on its own line, never silent** |

**The allowlist's members**, and every one is a response header Anthropic documents:

| | |
|---|---|
| `retry-after` | Seconds until the call may be retried |
| `anthropic-ratelimit-requests-limit` · `-remaining` · `-reset` | The request bucket |
| `anthropic-ratelimit-tokens-limit` · `-remaining` · `-reset` | The combined token bucket |
| `anthropic-ratelimit-input-tokens-limit` · `-remaining` · `-reset` | The input bucket |
| `anthropic-ratelimit-output-tokens-limit` · `-remaining` · `-reset` | The output bucket |
| `request-id` · `anthropic-request-id` | ~~❓~~ **In, both spellings. Closed at Task 2.** The id is in the error *body*, which is how this session identified the 429 as Anthropic's own — but **the body is only on disk when the corpus is enabled, and it is off by default.** The log line has to stand on its own, so the id is worth its row. Both spellings because which one arrives is not known from here, and neither can carry a secret |

**And the family that is actually used — added 2026-09-18, after the control measured it.**

| | |
|---|---|
| `anthropic-ratelimit-unified-status` · `-reset` | The overall meter |
| `anthropic-ratelimit-unified-5h-status` · `-5h-reset` · `-5h-utilization` | The 5-hour window |
| `anthropic-ratelimit-unified-7d-status` · `-7d-reset` · `-7d-utilization` | The 7-day window |
| `anthropic-ratelimit-unified-fallback-percentage` | |
| `anthropic-ratelimit-unified-overage-status` · `-overage-disabled-reason` | |
| `anthropic-ratelimit-unified-representative-claim` | ❓ **and deliberately left open.** Seen on every successful reply and **not added** — *"claim" is the vocabulary of tokens and assertions, not of counters*, and nobody here has established what it holds. **It is reported by name through the prefix catch**, so it is neither lost nor forgotten. *Adding a name is one line; taking a value back out of a log file is not.* **This `❓` closes when somebody finds out, not when the phase ends** |

***Twenty-eight names, and the first seventeen were the wrong ones.*** **Not one of the documented
API-key buckets arrives on a subscription credential** — measured 2026-09-18, on a successful reply
carrying twelve `unified` headers and zero of the documented ones. *An allowlist built from the
documentation would have recorded nothing and looked correct doing it; the prefix catch is the only
reason anybody knows.*

***`authorization`, `x-api-key` and `set-cookie` are named here as the things the list exists to
exclude*** — a response carries no credential today and the allowlist is what keeps that true when
one day it does.*

### Functions and classes

| Name | |
|---|---|
| `recorded_headers(reply) -> tuple[dict[str, str], list[str]]` | Beside `response_headers` in `proxy.py`. **Reads a reply it does not modify** — the relayed bytes are untouched, which is byte-relay and not negotiable. *Returns two things, not one: the allowlisted headers with values, and the names of unlisted `anthropic-ratelimit-*` ones* |
| `describe_headers(recorded, unlisted) -> str` | The log line's payload. **`(none)` when a reply carried neither**, because that is the interesting case and a blank would read as a logging failure |
| `Once` · `Once.take() -> bool` | **Added after the first measurement**, not in the original plan. A latch that is true exactly once. Mutable, held by the frozen `Proxy` the way `Counters` already is |
| `Proxy.headers_sampled: Once` | The control's latch. *Also added after the measurement — see the row below* |
| `decoded_for_peek(body, content_encoding) -> bytes` | **Added 2026-09-19.** A copy inflated far enough to route, or `body` itself when it is not encoded. ***The original is never replaced*** — `relay` forwards and the corpus stores what arrived, which is what prompt caching rests on |
| `BodyUnreadable` | **Added 2026-09-19.** Raised by the above, carrying a reason fit to show a caller. *It exists so a `400` can say **which** of two things went wrong: the body says nothing about a model, or the body could not be read at all* |
| `size_band(length) -> int` | **Added 2026-09-19.** A body's size as an order of magnitude — the count of its decimal digits less one, so `323 -> 2` and `127_949 -> 5`. *Computed from the decimal string rather than `log10`, which is **exact at a power of ten** where a float is not* |
| `OncePerKey` · `.take(key) -> bool` · `.full` · `.note_full() -> bool` | **Added 2026-09-19.** `Once`'s shape for keys that are **not known in advance**. `take` is true the first time each key arrives and never once `full`; **`note_full` is true exactly once, so the stop is said out loud.** *Separate methods because an instrument that quietly gives up looking is this phase's own recurring defect* |
| `verify_the_pin(target, fired) -> bool` | **Added 2026-09-19**, in `evidence/run-pinned.py`. Resolves `api.anthropic.com` through the loop `uvicorn` will pick and **refuses to start the router unless the patched resolver fired**. *Two facts, not one: an unpatched lookup returns the right address too whenever no hosts entry is in* |
| `Proxy.arrival_sampled: OncePerKey` | ***Was `dict[bool, Once]` until 2026-09-19.*** Now keyed on `(path, streamed?, size band)` — `for-the-owner.md` entry 11, the owner's choice, and **the path is part of the key rather than a gate** |

### Module constants — `src/ilirium_llm_router/backend_anthropic.py` *(added 2026-09-20, Group C4)*

***A new module, owner's decision.*** *`proxy.py` is protocol-neutral; these are one backend's
facts, and hardcoding them means the docstrings carry the measurement that justifies each one.*

| Name | Value | |
|---|---|---|
| `ATTRIBUTION_PREFIX` | `"x-anthropic-billing-header: "` | **The literal text that opens the block.** *It looks like an HTTP header and is not one — it is the start of a string inside the `system` array, and reading it as a header cost this phase two sessions* |
| `CC_VERSION` | `"2.1.267.608"` | ***Claude Code 2.1.267, and `.608` is the auto-mode safety classifier's call site*** — not a build number. **Knowingly wrong for the haiku auxiliaries**, which send `.daa` |
| `CC_ENTRYPOINT` | `"cli"` | Interactive. *`sdk-cli` is the `-p` path and is not the one that fails* |

***No `cch`, no `cc_prompt_id`, no `cc_prev_req` constants exist***, and that is deliberate — see
Group C4's field table for what each omission costs and why it is cheaper than the alternative.

### Functions and classes — `backend_anthropic.py` *(added 2026-09-20, Group C4)*

| Name | |
|---|---|
| `attribution_block() -> str` | The two-field block, built from the constants above. **Takes no argument**, because nothing in the request can inform any field it carries |
| `carries_attribution(body) -> bool` | **Whether a parsed body's `system` array already holds a block.** *A request that has one is never touched* |
| `with_attribution(body) -> bytes` | **Parse, prepend the block to `system`, re-serialise.** ***The one place this router does not relay a request byte for byte*** — confined to non-streamed Anthropic requests that lack the block, behind a key that is off by default |

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
| **The arriving sampler's key** | **`(path, streamed?, size band)`** — *`(streamed?)` alone until 2026-09-19, with every path but `/v1/messages` refused* |
| **The size-band ladder** | **Decimal order of magnitude**, one band per power of ten. *Coarse deliberately: it tells shapes apart rather than measuring them, and the two this phase confused sit three bands apart. A finer ladder costs a log line per band and separates nothing more* |
| **Arriving lines per run** | **Five to a dozen** in a real session, bounded at **64**. *Exactly two before 2026-09-19, which is how the 14:52 run sampled a warm-up and no classifier* |
| New config keys | ***AMENDED 2026-09-20: four are introduced and one survives.*** **`experiments.add_claude_code_hidden_attribution_block` is added by Group C4**, and at task 17 it **moves out of `experiments` into the Anthropic backend's own config** while the other three are deleted. ***The `experiments` block itself does not survive the merge***, so this row's count is a count of what the phase *introduced*, never of what ships. *The reason given below — switches over deletion, so a negative result stays reproducible — was reversed on 2026-09-20: a merged branch keeps them in history, which serves the same end without dead code on the trunk.* |
| New config keys *(as written 2026-09-18)* | ***Three, and this reverses a stated position.*** **`experiments.relay_accept_encoding` · `.http2_upstream` · `.imitate_attribution_headers`, every one defaulting to `false`.** *This row said **None** — "the minimal form is deliberately not configurable" — and that was right for the **instrument**, which is still not configurable. **It is wrong for the experiments**, which are not the minimal form: they are three deliberate modifications to the relay, and on 2026-09-19 the owner chose switches over deleting them so a negative result stays reproducible.* **`ARRIVAL_SAMPLE_CAP` is still a bound rather than a knob and stays out** |
| New on-disk names | **None in Group B.** *Group D may add one, and its rows are written then.* ***Groups C2 and C3 added six, all of which come out with the experiments*** — see the two rows below |
| **Experiment files — C2 and C3** | `evidence/clienthello-capture.py` · `evidence/boringssl-forwarder.py` · `evidence/binary-extract.sh` · `evidence/clienthello-capture.py` · `evidence/binary-extract.sh` · **`evidence/escape-the-hosts-file.py`** *(named `run-pinned.py` until 2026-09-20)* · `evidence/tls-terminator.py` · `config-hosts.yaml`. ***None is on the router's import path.*** ~~**and none ships**~~ — ***that stops being true at task 18***: the terminator and the escape script **are promoted to `tools/tls-terminator/`** as the documented fallback, with `config-boringssl.yaml` and the forwarder deleted instead |
| **`make` targets** | `forwarder` · `run-boringssl` · **`run-hosts`**. ~~*All three come out with the experiments*~~ — ***amended 2026-09-20: two come out and one is kept.*** **`forwarder` and `run-boringssl` are deleted at task 16**; **`run-hosts` is renamed `run-in-the-middle` and stays**, because the hosts route remains the fallback for when the attribution trick stops working. *A target for the promoted tool is added at task 18* |
| **Environment variables** | `FORWARDER_UPSTREAM` · `FORWARDER_IMPERSONATE` · **`PINNED_ANTHROPIC_IP`**. ***Read by the experiment scripts only; the router reads none of them*** |
| Index schema version | **Unchanged at `1`.** Group B touches no index. *If Group D reaches the corpus index this becomes `2`, and that row is written then* |

---

## Done when

- The headers on a real 429 have been **seen, frozen into `evidence/`, and read** — Group C. ***Done.***
- **`BUG-001` says which of H1 / H2 / neither the values support**, or says explicitly that it no
  longer reproduces and on which versions. ***Answered 2026-09-19: neither, and the reason is now
  measured.*** **H2 is dead** — the same router, egress and TLS fingerprint carried nine classifier
  calls successfully. **H1 is dead** — Anthropic accepts the identical request shape on the identical
  credential. ***What is left is client-side content withheld from a custom base URL***, which was
  not among the two this plan set out to separate.
- The durable home is chosen **by the owner** and built.
- The register's `❓` column is empty and Task 13 has checked it against the code.

## Not in this phase

- ~~**Fixing whatever the diagnosis finds**, if the fix is client-side or Anthropic's.~~ ***STRUCK
  2026-09-20.*** **The phase fixes it** — Group C4 — *and the framing that made this a non-goal is
  withdrawn with it: the cause being client-side does not make the router's inability to carry the
  request somebody else's problem.*
- ~~**Changing the relay.** Nothing here alters a byte the client receives.~~ ***STRUCK, and it had
  already stopped being true before today.*** **C2a changed what the client received** — non-streamed
  replies arrived brotli for a day — **and C3k changed the peek.** *Group C4 goes further and rewrites
  a request body, which is the first deliberate exception to byte-relay this router has.* **It is
  opt-in, off by default, and confined to non-streamed Anthropic requests that lack the block**;
  `reference/design-decisions.md` records the exception at task 17.
- **The subtractive attribution test** — stripping the block to watch the 429 return. *`BUG-001` asks
  for it and Group C4 answers the same question additively, leaving a working router if it succeeds.*
- **The `relay_accept_encoding` isolation test.** *Worth a session only if the report goes upstream,
  and it no longer does — see task 12.*
- **`BKL-0017`**, whether archiving slows a call — the milestone's third failure mode, and a
  separate measurement.

## Reading

- `../../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md` — the symptom, and what it
  already rules out
- `../implementation-plan.md`, Phase 14's section — the constraint and the deferred question
- `../../backlog.md` — `BKL-0034`, and `BKL-0037` for why the refusal was reversed
- `../../reference/corpus.md` — *"Bodies only. Never headers"*, the sentence this phase walks up to
- `../../method/IDM-008-the-register.md` — before Task 13
