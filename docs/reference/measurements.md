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
| The intermediate slices: 13.5× (`/v1/messages` only), 26.6× (no warmup probes) | 2026-08-07 | as above | named in each cell | Shows the gap is not an artefact of one filter — it is `count_tokens` that does the damage, not streaming |

**Anthropic's `read_timeout` of 600 s rests on the first row**: ten minutes of silence against a
backend whose median first byte is 1.4 s means something is wrong rather than slow.

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

---

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
recorded. **Both corrections landed at commit 11 of `../docs-restructure-plan.md`**, where
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
