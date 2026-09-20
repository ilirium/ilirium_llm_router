# Measurements

Every number this project quotes, with the four things that make it usable: **when** it was measured,
**with what**, **over which slice**, and **what it is for**.

**Why the file exists.** A number quoted without its slice reads as wrong to anyone who recomputes it
— the 26× time-to-first-byte gap becomes 3.9× over the whole file, and the documentation looks wrong
by a factor of seven. A number quoted without a job survives for months and then cannot be
reproduced, because nobody knows what it was answering. Both have happened here; both are in
`lessons.md`.

**What is canonical.** A phase note is **frozen-primary**: it records what was known when it was
written and is never edited again. This register is **canonical-for-quotation**: it is what other
documents cite, and a correction lands here first, carrying a note of what the phase note said.

**The admission rule.** A number enters this register when it is **quoted outside the document that
measured it**. A measurement that only ever appears in its own phase note stays there. This keeps the
register the size of the project's actual vocabulary rather than the size of its evidence.

**The filling rule (EPD-004 decision 20).** A row that cannot fill all four columns is a number that
should not be recorded. An empty cell is not a formatting problem — it is the finding. Withdrawn
numbers are kept at the bottom with the reason, because deleting them silently is how they come back.

---

## Latency: the two backends

The most-quoted pair in the project, and the one that has already misled a reader once.

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Median time to first byte: 1426 ms Anthropic, 37136 ms LM Studio — 26.1×** | 2026-07-31, recomputed 2026-08-07 and again 2026-08-16 | `../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv` | **Successful streamed `/v1/messages` calls only** — 32 Anthropic rows, 21 LM Studio | The felt difference between backends, and the reason `ttfb_ms` is a column at all. It is what put the per-backend `read_timeout` where it is |
| Same medians over **every row**: 1252 / 4904 — **3.9×** | 2026-08-07, confirmed 2026-08-16 | as above | All 42 Anthropic and 97 LM Studio rows with a `ttfb_ms`, including `count_tokens` and warmup probes | **Kept deliberately as the counter-example.** It is the number a reader gets by recomputing the obvious way, and without it the 26× claim reads as a mistake |
| The intermediate slices: 13.5× (`/v1/messages` only), 26.6× (`/v1/messages` **and** no warmup probes) | 2026-08-07, slice corrected 2026-08-21 | as above | named in each cell — 41 Anthropic / 65 LM Studio rows for the first, 41 / 25 for the second | Shows the gap is not an artefact of one filter — it is `count_tokens` that does the damage, not streaming |

**Anthropic's `read_timeout` of 600 s rests on the first row**: ten minutes of silence against a
backend whose median first byte is 1.4 s means something is wrong rather than slow.

**Corrected 2026-08-21 — the third row's slice, not its number.** It read *"26.6× (no warmup
probes)"* and silently inherited the filter from the row above it; the slice is `/v1/messages` **and**
no warmup probes. Read as written — warmup probes excluded and nothing else — the same CSV gives
1251.5 ms against 307.0 ms, which is **0.245×**, LM Studio four times *faster* than Anthropic. The
sign reverses. Found by the fresh-context review frozen at
`../milestone-1-core/documentation-review-2026-08-16.md`, finding V1, which calls it the severest of
its five and says why it is worse than the episode it descends from: **this is the same failure
inside the register built to prevent it**, in the row whose whole job is to prove the gap survives
re-slicing. **0.245× is kept here rather than deleted**, on the reasoning the 3.9× row above already
states — the number a reader gets by recomputing the obvious way has to be visible, or the correct
one reads as a mistake.

**All four slices were re-derived independently on 2026-08-21 before this correction was written**,
and all four land on the review's figures to the digit. **What made that possible is one predicate
neither document had ever written down**, and it is recorded here because it is the whole difficulty:

> A **warmup probe** is a `/v1/messages` row that is **not streamed** (`stream` empty), returned
> `error_status` **`ok`** with **zero `output_tokens`** and `stop_reason` **`max_tokens`**. There are
> **exactly 40**, and **every one is LM Studio** — which is why excluding them moves no Anthropic
> count and takes LM Studio from 97 rows to 57, and from 65 `/v1/messages` rows to 25.

**Two plausible wrong answers came first, and that is why this is a note rather than a footnote.**
Taking *zero output tokens* alone sweeps in the 33 `count_tokens` calls and gives 23.4×; adding the
`/v1/messages` filter but not the rest still catches **two `client_disconnect` rows** — real calls
that produced no output — and gives **0.216×** instead of 0.245×. Both look like the answer. The
review says the number "took four attempts" and does not say what the fourth was; this is it.

## LM Studio: context, prefill and capability

**One model, one window.** Everything in this block is `qwen/qwen3.5-9b` (MLX 4-bit) loaded at
**44544 tokens**, "Require Authentication" off, on one machine. **The LM Studio version was not
recorded on either date** — a hole in the slice of measurements that are expected to expire with a
release, and the reason to record it next time rather than a reason to distrust these.

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Fixed preamble: 27924 input tokens** | 2026-08-06 | `probe.py replay` over `../captures/log-the-whole-request.txt`, counted by LM Studio | One captured Claude Code request, a bare `hi` turn, 27 tools | Replaces the "~30k" estimate. It is what decides the minimum usable window for a local model — 63% of 44544 before the user types |
| **Cache: `cache_read_input_tokens` 0 → 27904 on the second identical replay; 99.93%** | 2026-08-06 | two replays, frozen in `../milestone-1-core/phase-4-lmstudio-parity/evidence/` | Same bytes twice, cold then warm | Byte-relay stops being an argument and becomes a measurement. Worth ~147 s of prefill per turn |
| **Time to first byte 196789 ms cold → 49629 ms warm** | 2026-08-06 | as above | Same request, cold and cached | The cache is worth 4× on first byte, and a 99.93% hit still costs 50 s — cache reads are cheap, not free |
| **Prefill profile: 9166 → 115073 ms; 27924 → 196789 ms; 41595 → 461712 ms; ~41000 → killed at 600247 ms** | 2026-08-06 and 2026-08-07 | needle runs via `probe.py`; the last two frozen in `../milestone-1-core/phase-4-lmstudio-parity/evidence/` and `../milestone-1-core/phase-5-config-and-timeouts/evidence/` | Input tokens against first byte, cold, same model and machine | **The usable context of a local model is bounded by time, not by the window.** The last two rows are the same request size on different days — a ≥30% spread straddling the old fixed 600 s ceiling, which is the argument for configuring it |
| **9166 → 115073 ms specifically** | 2026-08-06 | `make_needle.py` control run | as above | Same job as the row above, flagged separately because it is the **one Phase 4/5 figure with no frozen artefact** — it exists in the phase note and the script only. Holds, one level weaker than its neighbours |
| **Over-window refusal in 908 ms** | 2026-08-06 | needle exceeding 44544, frozen in `../milestone-1-core/phase-4-lmstudio-parity/evidence/needle-over-window.txt` | A single over-window request | Silent trimming does not happen at the boundary; the refusal is also cheap, so it costs nothing to hit |
| **41595 tokens = 93% of the window, codeword returned** | 2026-08-07 | the same needle at `read_timeout: 1800`, frozen in `../milestone-1-core/phase-5-config-and-timeouts/evidence/` | 93% occupancy, one run | No trimming *below* the boundary either. Closes the worry standing since Phase 1 |
| **`read_timeout: 30` → death at 30343 ms** | 2026-08-07 | `../milestone-1-core/phase-5-config-and-timeouts/evidence/needle-dies-at-30.txt` | Same needle, timeout lowered | Proves the config field governs live traffic, and reproduces the ten-minute failure in thirty seconds |
| **`output_config.effort: high` costs 4 → 216 output tokens for the same four-token answer** | 2026-08-06 | `probe.py`, controlled against a baseline differing only in that field | Two prompts, `max_tokens` 128 and 2048 | ~98% of the billed output is reasoning that is never shown, on every Claude Code request. The middle case (127 tokens, no blocks) is why a warmup probe and an effort-truncated reply cannot be told apart in the CSV |
| **`thinking` budget ignored: `budget_tokens: 1024` with `max_tokens: 2048` → 2047 thinking tokens, no text** | 2026-08-06 | `probe.py` | Two shapes, `adaptive` and `enabled` | Thinking is bounded only by `max_tokens`, so a frugal `max_tokens` returns a well-formed empty reply |
| **`cache_control` does nothing at 117 input tokens** | 2026-08-06 | `probe.py`, two identical runs | A probe-sized prefix | The prefix cache has a floor. Prevents the conclusion that caching is broken from a small test |
| **Replay body 119797 bytes against the captured 118004** | 2026-08-06 | `probe.py` re-serializing the capture | JSON separator spacing only | The limit on what the replay proves: the *shape* is accepted; that Claude Code's own bytes survive is carried by the frozen session's cache hits instead |

## The frozen session, 2026-07-31

142 rows from one long Claude Code session, in `../milestone-1-core/phase-2-observability/evidence/step-6-session/calls.csv`. Every row below
was recomputed from that file on 2026-08-16; the first six were also recomputed independently on
2026-08-07.

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **142 rows, 11 distinct `session_id`** | 2026-07-31 | the frozen CSV | The whole file | The session's scale, and that one session can span both backends |
| **7 rows under 1 `agent_id`** | 2026-07-31 | as above | Rows with a non-empty `agent_id` | `x-claude-code-agent-id` does arrive, so an empty column can be read as "main conversation" rather than as missing data |
| **6 `client_disconnect` rows — 5 LM Studio, 1 Anthropic** | 2026-07-31 | as above | Rows by `error_status` | starlette reaches the disconnect path reliably on both backends. It was the least-verified of the five statuses |
| **33 streamed Anthropic rows, 32 with both token counts** | 2026-07-31 | as above | `backend=anthropic`, `stream=true` | Anthropic's streamed replies scan like LM Studio's, so one scanner covers both |
| **33 `count_tokens` rows — 32 LM Studio, 1 Anthropic** | 2026-07-31, split re-derived 2026-08-16 | as above | `path=/v1/messages/count_tokens` | Something unexpected does reach the catch-all, which is why `path` is a column. **The split is the point** — see the corrections below |
| **40 warmup probes: 20.0 of 45.6 minutes of LM Studio wall clock, 44%** | 2026-07-31 | as above | LM Studio rows with `stop_reason: max_tokens` and `output_tokens: 0` — the same signature an effort-truncated reply produces, so this is an upper bound | The strongest argument against "no special case for background traffic": 44% of local wall clock returns nothing |
| **Longest warmup probe: 111559 ms for a 1960-byte body** | 2026-07-31, corrected 2026-08-16 | as above | One row | The cost of a warmup probe is **not** proportional to its body — see the corrections below |
| **LM Studio prefix caching at scale: 24 rows with non-zero `cache_read`, maximum 40879** | 2026-07-31 | as above | `backend=lmstudio` only. Over the whole file it is 52 rows and 70692 | The prefix cache is real on ordinary traffic, which is what the probe-scale zero does not show |
| **99 rows against `qwen/qwen3.5-9b`: 95 `ok`, 0 rejections, 8 `tool_use` turns, `request_bytes` 154 → 164 KB** | 2026-07-31 | as above | One model across the session | A local model holds a real session, including tool results accumulating. It is what let a later phase delete a planned run |
| **8 Anthropic 429s, all retried successfully** | 2026-07-31 | as above | `error_code=429` | Rate limiting is ordinary and self-healing; the recorder now keeps the symbolic `rate_limit_error` so the next one is read rather than reconstructed |

## The request shape

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **118 KB request for a bare `hi`: 81 KB of tool schemas (27 tools), 28 KB of system prompt, 368 bytes of conversation** | 2026-07-28 | `../captures/log-the-whole-request.txt`, read with `jq` | One captured request from one Claude Code version | Why `request_bytes` is a weak proxy for conversation size, and why a local model needs far more than the 25k LM Studio suggests |
| **34304-token window ran a real session on `google/gemma-4-e4b`** | 2026-07-29 | a live Claude Code session | One model, tool use and multi-turn | The first evidence a local model could drive the harness at all. It worked because it fit — established two phases later |

## Failure behaviour

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Claude Code retries a 502 ten times with backoff** | 2026-07-31 | a live session with LM Studio stopped | One client, one status | A session heals itself when a backend comes back — and **one turn becomes up to ten rows**, so a row count is not a turn count when a backend is down |
| **`read` bounds silence, not duration: `/drip` ran 6.01 s against `read=2.0` and completed** | 2026-08-07 | `../procedures/read-timeout-semantics.py` | httpx at the pinned version, three timing shapes | Retires "a timeout that resets on progress" as an option — it already is one — and narrows what the 600 s ever bought to "fails if it goes quiet" |

## The first-party gate and the classifier, 2026-09-18 / 19

***CORRECTED 2026-09-20: IT WAS NOT A CONTROL.*** **A second variable moved with the first.**
*Every 2026-09-18 run also set **`CLAUDE_CODE_ATTRIBUTION_HEADER=0`**, which this repository's own
`README.md` has prescribed since 2026-08-07 for pointing Claude Code at the router — and the
2026-09-19 run did not, because with no base URL set there was no such command line to copy.*
***That variable is what decides whether the attribution block is sent at all.***

**This is a statement about the experiment's design, not a hypothesis**: two things differed between
the two halves, so neither row can attribute the outcome to either one. ***Which of them mattered is
what `for-the-owner.md` entry 22's A/B settles***, and it has not been run.

***The NUMBERS below are all good*** — they were counted off the corpus and the recorder, and
nothing about them changes. **What is withdrawn is the sentence this paragraph used to open with:**
*"the only variable is whether `ANTHROPIC_BASE_URL` names `api.anthropic.com`."*

*Quoted by `../bugs/BUG-001-non-streaming-messages-rejected-as-rate-limited.md` and
`../wiki/claude-code-first-party-gate.md`, both of which carry the same banner.*

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **125 classifier requests, 119 rejected `429`** (6 `client_disconnect`) | 2026-09-18 | `logs/corpus/2026-09-18/index.csv`, read back after the fact | Non-streamed `/v1/messages` over 100 KB, Claude Code **2.1.267**, `ANTHROPIC_BASE_URL` set to the router | The failing half of the control. **A count, not a rate** — the six disconnects are not successes |
| **9 classifier requests, 9 `ok`** | 2026-09-19 | `logs/corpus/2026-09-19/index.csv` | The same shape and build, reached through `/etc/hosts` + a local TLS terminator with `ANTHROPIC_BASE_URL` **unset** — ***and `CLAUDE_CODE_ATTRIBUTION_HEADER` unset with it*** | ***It still clears the router***, which needs only that both days used the same process, egress and TLS fingerprint — **that part is unaffected by the second variable.** *What it does NOT establish is which of the two client-side variables produced the difference* |
| **The attribution block: absent in all 125, present in all 9** | 2026-09-19 | `ilirium-llm-router extract --format bodies` over both day folders | The `system` array of those same requests | The one known content difference that survives into the success. ***Leading candidate for the cause and not shown to be it*** |
| **Verdicts returned: `<block>no` ×5, `<severity>` 10 / 15 / 18 / 25** | 2026-09-19 | the stored response blobs, **brotli** inside zstd | The nine successful replies | Separates *"the call returned 200"* from *"the classifier classified"* — `BUG-000`'s trap, closed with content rather than status |
| **12 rate-limit headers on a success, 0 on a `429`** | 2026-09-18 | the router's own recorder, `evidence/rate-limit-headers-*-2026-09-18.txt` | One connection, both outcomes | A `429` naming no exhausted bucket is not a rate limit. **The meter read `allowed` at 0.52 / 0.59, and 0.11 / 0.01 in a later run** — quota dead twice over |

## The classifier still fails after the 429 is gone, 2026-09-19

***The second defect, which the 429 was masking.*** *Established by aligning the owner's session
transcripts —
`../milestone-2-corpus/phase-14-rate-limit-headers/evidence/claude-code-sessions-to-check-safety-classifier.txt`
— against the router's own record of the same minutes.*

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Session 1: 5 classification events, 5 client-reported failures. Session 2: 2 and 2** | 2026-09-19 | the owner's transcripts against `calls.csv` and the corpus | Two sessions through the router, ~12:31 and ~12:35 UTC | ***The correspondence is exact***, and a stage-1 `<severity>` pair counts as one event. **What the client reports as a failure is what the router served successfully** |
| **0 classifier requests for every Bash call that succeeded** | 2026-09-19 | the same pair of records | The same two sessions | **Those were allowlist matches** — `echo`, `ls`, `date` never consult the classifier, so their success says nothing about it |
| **32 streamed replies plain, 13 non-streamed replies brotli** | 2026-09-19 | magic bytes of the stored blobs, `logs/corpus/2026-09-19` | Every `/v1/messages` reply of the day | **The split experiment C2a introduced**, and the classifier is always non-streamed. *The correlation behind the suspicion, not proof of it* |

## The classifier working, and what fixed it — 2026-09-19

***The after-half of the row above.*** *Session 4, `20260919-4`, 15:30–15:39 UTC, Claude Code 2.1.267,
the hosts route, and the three router experiments switched off.*

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **35 calls, 35 `ok`** | 2026-09-19 | `calls.csv` | The whole of session `20260919-4` | **No 429, no gzip 400, nothing refused.** *The first session in this phase's record with a clean sheet* |
| **16 classifier calls, 16 `ok`** | 2026-09-19 | `logs/corpus/2026-09-19/index.csv` | Non-streamed `/v1/messages` over 100 KB | ***And the client used the answers***, which the 9 of 2026-09-19 12:31 did not |
| ***16 of 16 replies PLAIN JSON*** | 2026-09-19 | magic bytes of the stored blobs | The same 16 | ***The mechanism, not the correlation.*** **Every non-streamed reply before the switch was brotli and every one after is plain**, and `relay_accept_encoding` is the only switch that can change a reply body |
| **A verdict of `<severity>68</severity><category>Auto Mode Bypass</category>`** | 2026-09-19, 15:37:47 | the stored reply | One classification | ***`BUG-000`'s trap closed from the other side.*** **A positive, discriminating decision** — eight probes allowed, the pipe-to-bash one blocked — *which no quiet session can fake* |

## The router itself

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **158 tests** | 2026-08-07 | `make test` | The suite at Milestone 1's close (139 after Phase 2, 147 after Phase 3, 157 after Phase 5) | The invariant for work that must not touch behaviour: the count is the same before and after |
| **58% of the source is prose: 1713 lines, 371 code, 1000 comment and docstring** | 2026-08-07 | line classification over `src/` | The seven modules | The density is deliberate and was kept. Recorded so it is not re-opened from the ratio alone |
| **Mean 2.8% wording overlap between docstrings and `CLAUDE.md`; highest 19.7%; zero above 30%** | 2026-08-07 | shared 5-word sequences over 49 docstrings of 25+ words | Docstrings against `CLAUDE.md` only | **The measurement that refuted the review's own plan.** The comments are not duplication, so the obvious cut was refused |
| **10 `ty` diagnostics, 0 defects** (was 12 before one fix) | 2026-08-07 | `uvx ty@0.0.14 check src tests` | One version of one checker | The reason `ty` is not adopted. A negative result, recorded so it is not re-run hopefully |
| **A 1049671-byte chunk whose longest line is 101 bytes lost all five usage columns** | 2026-08-07 | a direct feed into `SseScanner` | One synthetic chunk | The SSE scan cap was measuring the chunk, not the line, and logging a reason that was not true. Fixed the same day |

## `CLAUDE.md` structure

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Section citations: Design decisions 8, Observability 5, Observed request shape 4, Goal 1, everything else 0** | 2026-08-15, corrected 2026-08-16 | grep for section titles in quotes | Across `docs/`, `src/`, `tests/`, `README.md`, excluding `CLAUDE.md` itself, the two restructure documents, and the three files carrying replayed captures | Decides which sections a pointer can replace. **The caveat is the finding:** it counts a section used as an *authority*, never one used as a *lookup table*, so a zero can mean inert or silently used |
| **`Status` is 59 lines and 11038 bytes — 17.5% of the file by lines, 23.6% by bytes** | 2026-08-15, corrected 2026-08-16 | `CLAUDE.md` at `51b857b` | One file at one commit | The clearest cut in the file: never cited in six phases. It is *third* largest by lines and largest only by bytes — the correction is in `lessons.md` as a units error |

## Numbers from open proposals

Findings are durable; the decisions they argue for are not. These are measured, cited by `CLAUDE.md`,
and **nothing has been accepted** — see `../epd/`.

| Number | Measured | Instrument | Slice | What it is for |
|---|---|---|---|---|
| **Claude Code estimates local context against an assumed 200k window** | 2026-07-31 | a live session's `/context` display | One client, local models | `EPD-002`. On a 34304-token model a conversation at 238% of its window displays as 41% |
| **`request_bytes` cannot predict tokens: 6× ratio spread, 410% worst-case error** | 2026-07-31 | the frozen CSV | Rows carrying both a byte count and a token count | `EPD-002`. Kills the cheap version of local token counting |
| **A body corpus is ~93% repeated prefix; the step 6 session would have been 10.35 MB in 77 minutes** | 2026-07-31 | the frozen CSV plus the capture | One session | `EPD-003`. Storage is O(N²) in turns where the transcript is O(N) |
| **Compression: zstd 28.6× against gzip 2.4× across bodies; 3.1× and 2.9× on a single body** | 2026-07-31 | the capture grown across twenty turns | Synthetic growth from one real body | `EPD-003`. The storage question is a compression-window question, not a database one |
| **On real bodies: per-file 3.12×, one long-window stream 29.91×** | 2026-08-17 | `milestone-2-corpus/phase-9-corpus-gate/evidence/gate.py`, zstd 1.5.7 at level 19 | 20 held-out request bodies, 2,102,371 B, of 73 captured | **Confirms the row above transfers off synthetic data** — it predicted 3.1× and 28.6–31.3× |
| **A dictionary trained on other sessions reaches 12.10×, closing 82.8% of the gap** | 2026-08-17 | same | same held-out slice; dictionary trained on 48 bodies from three *different* sessions | `EPD-003`'s gate, and the reason per-call files survive. Per-file storage ends at **2.47×** a stream, not 9.6×. **Read as optimistic** — see the slice note below |
| **A second preamble family costs ~20%: main conversation 13.39× against subagent 10.75×** | 2026-08-17 | same | 10 main and 10 subagent bodies, one dictionary trained on traffic containing **no** subagent bodies | Whether concurrency and subagents dilute a shared dictionary. They do, boundedly — it generalises to an unseen preamble family rather than collapsing |
| **`zstd --train` is non-monotonic at 68 samples: 12.08× → 21.76× → 16.44× as `--maxdict` rises** | 2026-08-17 | same | self-trained dictionaries at 112,640 / 262,144 / 524,288 B caps | Why a retraining policy must **measure** a new dictionary before adopting it. More budget produced a worse dictionary |
| **The static preamble is 111,028 B interactive and 82,611 B headless; `--maxdict` defaults to 112,640** | 2026-08-17 | `jq` over the frozen capture and a captured body | One interactive request (2026-07-28) against one headless request | Why the gate swept `--maxdict`, and why headless figures flatter a dictionary. Corroborates `stats.py`'s "~110 KB" |
| **Through the shipping store, on disk: 12.919× dicted against 2.997× undicted** | 2026-08-20 | the router's own `--train-dict` and `--extract`, `zstandard` at store level **9**, trained at level 3 | 21 held-out request bodies (run-03, all distinct, no retries); dictionary trained on **48 bodies, 26 distinct — 46% `overloaded_error` retries** | **Confirms the mechanism works end to end**, which is all it is for. First figure measured through the code that ships rather than an offline script: bodies written by `CorpusWriter` and read back by `CorpusReader`. Agrees with the trainer's in-memory `12.920×` by two independent paths, and the undicted baseline reproduces Phase 9's 701,407 B to within 9 |
| **The same parameters on the same corpus reproduce the same dictionary, byte for byte** | 2026-08-20 | two `--train-dict` runs, `maxdict` 262,144 and `k` 8,000 | `logs/corpus-gate/`, three session directories | The **content-derived dictID** doing its one job: identical bytes give the identical `0e4d84d1`, so a dictionary's name identifies its content rather than its run. `zstd --train` stamps **1** on everything, which is why the router assigns its own |

> **The slice on the 12.10× row is doing real work.** That corpus is headless, so its static preamble
> is ~28 KB smaller than an interactive one; 70 of its 73 bodies are Anthropic; and its sessions are
> short, so more of each body is static material — which is the part a dictionary *can* capture. **All
> three flatter the dictionary.** The verdict it supports survives because the margin is large (12.10×
> against a 3.12× failure threshold), not because the biases are small. A number quoted from this row
> without that slice would overstate what a real corpus achieves.

> **Read every compression figure above as a small-sample confirmation that the mechanism works, not
> as a performance claim.** *Added 2026-08-20, on the owner's instruction at Phase 10's Task 21.*
> **There is deliberately no headline ratio.** Phase 9's number comes from 73 bodies and Phase 10's
> from 21 held out; the two were measured with different tools at different levels on different
> slices, and neither is a specification. They exist to show that compression functions and that the
> gate was passed. **A ratio quoted from here without its slice is being misused** — and quoted as a
> capability rather than as evidence, it is being misused even *with* its slice.
>
> **Two numbers this phase deliberately kept out.** `26.210×` and `26.870×` both appeared on
> 2026-08-20, by two different mechanisms, and both were **self-scoring accidents** — training and
> scoring on overlapping material. And the stub-traffic ratios from Task 18's driving check
> (`1.4×`–`5.1×`) measure synthetic bodies a few hundred bytes long; they say the plumbing works and
> nothing whatever about compression.

---

## The corpus, read back — Phase 11, 2026-08-28

*The slice for every row below is **the live corpus at 2026-08-26T15:16Z**: 979 index rows, four day
folders, nine sessions. Frozen in that phase's `evidence/`, and **it is a moving corpus** — the same
figures were 770 rows four hours earlier.*

| Number | What it is | Measured with | What it is for |
|---|---|---|---|
| **979 / 902 / 66 / 11** | index rows; `/v1/messages`; `count_tokens`; no `session_id` | `extract`'s selection over the four day indexes | **They sum: 902 + 66 + 11 = 979.** This is the arithmetic that demonstrates exact matching — a prefix match folds the 66 into the 902 and the total still looks right |
| **36 conversations in 9 sessions** | distinct root messages sharing a `session_id` | `transcript.reconstruct` | A `session_id` is **not** one conversation. Includes a **66-call subagent** carrying its parent's id |
| **67** | rows carrying an `agent_id`, one agent, all in one parent session | index | Confirms `observe.py:40` by measurement for the first time. A **partition key, not a filter** |
| **0/76, 46/76, 0/76, 65/76** | the prefix property under: raw; `cache_control` stripped; encoding canonicalised; both | one 77-call conversation | **The encoding fix scores zero alone** — the marker breakage masks it, so a session applying only that one would conclude the finding was wrong |
| **100** | messages revised by a later call, **9 changing role** | all conversations | Why turns are taken from a conversation's *latest* state. Emitting on first sight writes retracted turns down as real |
| **678 / 143 / 0** | consecutive request pairs that grew / held length / shrank | all conversations | The message array is **append-only**, which is what makes a position stable enough to key a `uuid5` on |
| **630 of 631** | assistant turns whose two sources agree on block shape | response blob vs the next request's copy | The difference is a `caller` field on `tool_use`: **47,628** request-side blocks carry none, **630** response blobs mention it. The response is the richer source |
| **45** | contiguous calls with no stored request body | `ad9392ae`, calls #225–#269 of 270 | `request_bytes` crosses 1 MiB once — 1,043,805 → 1,047,198 → **1,051,096** — and never returns. **Every long session loses its ending**, and the loss is always the tail |
| **1,615 records / 1,614 ids** | the first full conversion of the corpus | `jsonl.records` over 36 conversations | **One duplicate `uuid5`**, found by counting output against itself while 378 tests passed. The final reply and the first gap both sat at position `depth` |
| **11 of 36** | conversations legitimately opening at two messages | all conversations | Why "a conversation that starts too deep began earlier" is **not** a sound missing-day check, and the exact day-set difference is |
| **26 turns / 12 turns** | misdated; downgraded to the request-side copy | `20260825-1` converted from its later day only | What omitting a day folder actually costs. **Not truncation** — depth is 337 either way and every message is identical |
| **279 → 277** | mutants over `transcript.py` and `jsonl.py` | `evidence/mutate.py` | The two that disappeared were an unreachable `default=`, deleted as dead code — **the sweep shrank its own denominator** |
| **105 → 75 survivors** | before and after the fixes | same | **All 5 real logic survivors are dead.** The 4 logic mutants that remain are singular/plural grammar in error text, and ~43 of the 75 are string mutants of the same kind — parked in `backlog.md`, category A |
| **23 vs 279** | targeted mutations run per task vs the systematic sweep | both | **All 23 targeted died and none surprised**, each having been chosen because a test was expected to catch it. The sweep found 5 real logic defects the targeted run could not, by construction |

## Corrections this register made when it was assembled, 2026-08-16

Filling the columns is a check, and it found things. Both were slice errors of the kind this file
exists to prevent, and one of them is a number that had been quoted forward three times.

**`count_tokens`: 33 rows, or 32?** Both, and neither document said which slice it meant. The file
holds **33** rows on that path — **32 LM Studio and 1 Anthropic**. `CLAUDE.md` quotes 33 (the whole
file, answering "does anything unexpected reach the catch-all"); `handoff.md` says "all 32 such rows
are logged `ok`" (the LM Studio slice, which is the one `EPD-002` is about). Neither was wrong;
neither was readable. The split is now in the table above, and it also records a fact nobody had
stated: **the catch-all forwarded one `count_tokens` call to Anthropic**, which is the route working
as designed on a path nobody enumerated.

**The 111-second warmup probe did not carry a 31 KB body.** `CLAUDE.md` said "One took 111 seconds
for a 31 KB body". Recomputed, the longest warmup probe is **111559 ms with a 1960-byte body**, and
the 31786-byte probe took **103395 ms**. The sentence pairs the maximum of one column with a
different row's value in another — two true numbers joined into a false one.

**The correction strengthens the point it was making.** A two-kilobyte request costing 111 seconds
says the expense of a warmup probe is not proportional to what it carries, which is a better argument
against sending them to a local backend than the original sentence made. *Why* it costs that is not
established here — a model load, or contention with another call, are both plausible and neither was
recorded. **Both corrections landed at commit 11 of `../milestone-1-core/phase-7-docs-restructure/plan.md`**, where
`CLAUDE.md` was rewritten and the paragraph carrying them left for `design-decisions.md`. The same
pass found `backend-lmstudio.md` repeating both errors — a reference file contradicting this register
four commits after it was written, which is the drift this tier exists to prevent, caught only
because commit 11 went looking for every copy rather than the one the plan named.

**And one rounding slip, corrected in the same place:** the warmup probes take 20.0 of **45.6**
minutes, not the 45.5 `CLAUDE.md` had. 44% either way.

## Withdrawn

Kept, because a number deleted without its reason comes back.

| Number | Withdrawn | Why |
|---|---|---|
| **"253 mentions of the 22 moving documents"** | 2026-08-16 | It does not reproduce — the same scope gives 340, 301, ~261 or 199 depending on a recipe nobody recorded — and re-deriving it would have been the wrong fix, **because the number had no job**. It was sizing a job that files size better, and it was not the work list, which the link checker produces. The rule generalised from it is EPD-004 decision 20, which is why this register has a fourth column |
| **"~30k tokens of fixed preamble"** | 2026-08-06 | Superseded rather than wrong: measured at 27924. The estimate was good and slightly pessimistic, and it is recorded here so the older figure is recognisable when it turns up in a phase note |
| **"a rough `def test` count of 127"** | 2026-08-07 | Stale and never a real count — parametrisation means `def test` undercounts. `make test` reports the number; nothing else should |
