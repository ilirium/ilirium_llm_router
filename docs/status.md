# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-19, later still — Task 7 has run and Group C is open.** The smoke test passed on the first
run: 40 bodies, both directions, dicted at level 9 and undicted, **all byte-identical**, sha256 of the
round trip equal to sha256 of the original. Frozen as `evidence/smoke.py` / `smoke.txt`. **Still no
`src/` change** — `git diff main -- src/` is empty and **Task 8 is where that changes.**

**It found something nobody had listed as an assumption: a dictID is not a unique key.** `zstd --train`
stamps **1** on everything, so Phase 9's eight frozen dictionaries are **six distinct files all
carrying `1`**. `zstandard`'s own trainer at `dict_id=0` is **not random per call** — identical input,
identical ID. And the same samples at levels **3 / 9 / 19** give **one ID and three different files**,
which is `plan.md`'s stated `TRAIN_LEVEL` hazard **reproduced independently**.

**Both failure modes are loud, which is the half the plan did not state.** The wrong file of a matching
ID raises `Data corruption detected`; no dictionary at all raises `Dictionary mismatch`. Neither
returns plausible wrong bytes. **So Task 13a treats the dictID as a lookup hint** — try each candidate
in the day's `dicts/`, keep the one that verifies against the digest in the blob's filename — and that
constraint is now in its row.

**`write_dict_id` was confirmed on the backend that actually runs.** Task 8's requirement cited
`backend_cffi.py`, which `wiki/zstandard-and-libzstd.md` warns is **the backend we are not on**;
measured on `cext`, the trap is real. **That wiki page was corrected**, per the rule that a
contradicting finding's measurement stays in the phase note and the correction goes to the file that
owns the fact — it had called `dict_id=0` a *random* ID, from a CFFI docstring.

**The owner then asked whether we can stamp our own dictID, and we can — so we will.** Measured:
`train_dictionary(dict_id=N)` takes **any `uint32` verbatim**, and the ID also lives at **bytes `[4:8]`
of the dictionary file** after magic `0xEC30A437`, so a trained dictionary can be **re-stamped in
place** with the compressed output byte-for-byte the same size. **Decided 2026-08-19: the router
derives its own** — sha256 of the dictionary with its own ID field zeroed, first four bytes, `or 1`,
as `content_dict_id()` in `dictionary.py`, applied by Task 14. It gives **three IDs across levels 3 /
9 / 19 where libzstd gives one**, so that hazard is closed by construction. **`TRAIN_LEVEL` is not
reversed** and stays 3 on its own measurement. Two traps are recorded: an out-of-range `dict_id`
**does not raise**, and a derived ID of **0** would make every frame claim to be undicted.

**One thing deliberately left unmeasured:** zstd's frame-format spec reserves dictionary IDs `<=
32767` and `>= 2**31` for public distribution. libzstd accepted every value tried, this corpus is
private, and the owner declined to constrain the derived ID to the non-reserved band — **recorded as a
known gap** rather than closed.

**Baselines, run not predicted: `make test` 158 (0.66 s), `link-check.py` 82 files, 86 broken, 2
roundabout — both unchanged.** 86 is correct here: this task cited nothing unbuilt, and the two files
it added are not `*.md`.

**2026-08-19, later still — Task 8 has landed and `git diff main -- src/` is no longer empty.**
`src/ilirium_llm_router/corpus.py`, the blob store: content addressing on the plaintext, the per-day
layout, `write → fsync → rename`, dedup scoped to the day, the `manifest`, and the per-day dictionary
copy. **The queue is Task 9's, the index rows Task 10's, the config Task 11's, the reader 13a's.**

**It was exercised rather than asserted, and `make test`'s 158 is not the evidence** — no test touches
the file until Task 13. What was driven against `logs/corpus-gate/run-03-anthropic/`: an undicted
first run, a byte-identical round trip whose sha256 equals the blob's filename, dedup, the stale-`.tmp`
sweep, and **a writer that stores nothing creating no directory at all** (Task 18's observation 1).
**The one that counts: `tar` the day, unpack it elsewhere, and all 40 blobs opened and verified
against their own filenames from that folder alone.**

**The `write_dict_id` assertion was checked by breaking it on purpose.** Forced onto the
`ZstdCompressionParameters` path, construction raises `CorpusError`. **An assertion nobody has seen
fail is a comment.** It raises rather than falling back to undicted: *"telemetry must never break a
call"* governs the request path, and construction is not a call.

**A gap the plan flagged is closed.** *"Which timestamp decides the folder is unspecified in Task 8"* —
it is the **call's own `timestamp`**, so a body stamped `23:59:59` lands in yesterday's folder even
when it is written after midnight. Driven across the boundary, not assumed.

**Two judgement calls, both in `notes.md`:** the index's column *names* are declared at Task 8 so the
`manifest` can write `len(INDEX_COLUMNS)` rather than a hardcoded 26 that could drift from Task 10's
tuple; and `CorpusWriter` takes a directory and a level rather than a config block, because **Task 11
is the only task that builds that block** and it runs later. No register value moved.

**Baselines, run not predicted: `make test` 158 (0.75 s), `make check` valid, and `link-check.py`
82 files, 2 roundabout, and broken down from 86 to `81`.** **The fall is the point** — five forward
citations to `src/ilirium_llm_router/corpus.py` resolved the moment the file appeared, which is the
behaviour this file and `plan.md` both describe: *it rises when a task cites what it is about to build
and falls when the file appears.* **`dictionary.py`'s citations are still outstanding and Task 14
resolves them.**

**2026-08-19, end of session — Group C is complete and the store works end to end.** Tasks 7 to 13a
all ran. `src/ilirium_llm_router/corpus.py` holds `CorpusWriter` and `CorpusReader`; `config.py` has
the nine-key block; `proxy.py`, `observe.py`, `app.py` and `cli.py` are wired. **`make test` went
158 → 218.** **Group D, from Task 14, is where the next session starts.**

**The claim this group had to make good, and did:** a body goes in through `POST /v1/messages` and
comes back out through the reader, **byte-identical, verified against the digest in its own
filename, from the day folder alone.** `tar` a day, unpack it elsewhere, and every blob opens. That
is failure mode 2 — *archiving cannot stay opaque* — discharged by construction, and the test that
makes it a check uses a body that is not UTF-8 and not JSON at all.

**Four defects were found by driving rather than by reading, and they are the session's real
output.** A repeat body after a mid-day dictionary swap named the **wrong dictionary** — and the
first test missed it because two dictionaries shared a dictID, which is *this morning's* finding
biting the instrument. The summary line reported **`→ 0 bytes`** because a counter was declared and
never incremented. A malformed timestamp made the **corpus root** the day folder, writing `manifest`
and `requests/` beside `dicts/`. And the `write_dict_id` assertion was only worth its line once it
had been **broken on purpose** and seen to fire. **None of these would have failed a test suite,
because none of them had a test until they were found.**

**Four owner decisions were taken and are in `plan.md`'s settled table with their rejected
alternatives:** the router stamps its **own content-derived dictID** (`content_dict_id()`, closing
the levels-3/9/19 collision by construction); a repeat body's dictID is **read off the blob**; the
`write_dict_id` check **refuses to start** rather than degrading quietly; and Task 8's two scope
stretches stand.

**Baselines, run not predicted: `make test` **218**, `make lint` clean, `make check` valid,
`link-check.py` 82 files, **82 broken**, 2 roundabout.** It fell 86 → 81 when `corpus.py` appeared,
then rose to 82 when the rewritten `prompt.md` cited `dictionary.py` — **the handoff file moving the
baseline it quotes, which is the recursion to expect and not a defect.** Task 14 resolves it.

**2026-08-19, later the same day — Phase 10 gained a register, and is *still* at Task 7.** **No `src/`
change exists**; four commits, all documentation. `plan.md` gained **"The register"** — one reachable
section holding **every constant, key, name and magic number the phase would build**, on the owner's
instruction, so they can be checked against the code at the close. **Task 24 now checks it row by
row.**

**Compiling it found eight values the plan named and never gave**, and **all eight were closed the same
day**. `DRAIN_TIMEOUT_S` 5, `LOCK_STALE_S` 3600, `SUMMARY_EVERY` 500 beside `RESCAN_EVERY`'s 500,
`INDEX_SCHEMA_VERSION` 1, the four CLI flag names, `Call`'s three new fields, and the class names —
**`CorpusWriter`, `CorpusReader`, `DictionaryTrainer`**. `corpus.max_body_bytes` was renamed to
**`corpus.body_max_bytes`** so the three size keys share one shape.

**Three of the eight were not holes, and that is why the register is now a `backlog.md` method item.**
The drain timeout **contradicted this phase's own frozen evidence** — *"tens of milliseconds each …
twenty-second shutdown"* against `evidence/results.txt`'s measured **0.433 ms per body**, out by ~70x.
The cadence's justification **did not survive reading**. And `Call` **already uses** `request_bytes` /
`response_bytes` for integer counts. **Two `IDM-004` passes missed all three**, because a review reads
a plan as prose and an absent value reads perfectly well in a sentence.

**`TRAIN_LEVEL` was split from `compress_level_zstd`, reversing a decision made the same morning.**
**There are three levels, not one:** archiving and **scoring** read `corpus.compress_level_zstd` (9),
**training** uses `TRAIN_LEVEL`, now **3**. Measured on the held-out slice, training levels 3 to 19 move
the ratio by **0.03%** — it is not a parameter. Binding both to the key was **refused on a hazard**:
every training level yields **one dictID**, so editing it would change dictionary bytes without
changing the ID the reader finds them by.

**2026-08-19 — Phase 10 was re-scoped, reviewed again, and is still at Task 7.** **The router now
retrains its own dictionary automatically** — the plan had said training was offline and manual,
**that was never an owner decision**, and no review had asked whose it was. **Thirty-two tasks**,
seven lettered, nothing renumbered; the config block went five keys to nine under a nested
`corpus.retrain:`.

**A second forward review ran under `method/IDM-004` and its 22 findings are applied** — charter is
`review-charter-retraining.md`, merged list is in the phase's `notes.md`. **Do not re-review it.**
**The cold run found 16 to the author run's 9, including all four that fail silently**, which is the
strongest evidence `IDM-004` has. Eight findings needed owner decisions and all eight were made.

**The correction worth carrying:** `train_dictionary` takes a `level` that changes which dictionary
you get and defaults to **3**; Task 6's **13.65×** was produced at **19**. So **13.65× is no longer
reproducible**, and Task 15 records the level-9 ratio it actually gets — **measured 2026-08-19 at
12.920×** on the provisional `maxdict`/`k`, which is where it should land.

*This paragraph read "the trainer now trains and scores at **9**" until 2026-08-19, when compiling
`plan.md`'s new **"The register"** found that one constant was doing **two jobs**. **There are three
levels, not one:** archiving and **scoring** both read `corpus.compress_level_zstd` (9), while
**training** uses `TRAIN_LEVEL`, now **3**. Scoring had to follow the key or an operator editing it
would silently score at a level nothing writes at; training was measured to be **irrelevant — 0.03%
across levels 3 to 19** on the held-out slice. Binding **both** to the key was refused on a hazard:
every training level yields **one dictID**, so an edit would change dictionary bytes without changing
the ID the reader finds them by.*

**Two new homes exist.** **`docs/wiki/`** — a tier for what was established by *reading* a dependency,
with three pages and its test in `wiki/README.md`; and **`procedures/event-loop-lag/`**, which
measured that a thread only protects the event loop when the work **releases the GIL**.
`.claude/settings.json` gained `attribution.sessionUrl: false`, the first non-permission entry in it,
with `IDM-002` amended to say what sorts anything that is not a permission.

**2026-08-18 — Phase 10 is executing. Groups A and B are done; the next task is 7.**
`feat/phase-10-body-store`, forked at `d885b2f`. Its `plan.md`
was re-derived and then forward-reviewed under `method/IDM-004`, 22 findings, all applied — **do not
re-plan or re-review it**, and do not reopen the owner decisions in its settled table. **No `src/`
change exists yet**; `git diff main -- src/` is empty and **Task 8** is where that changes.

**Group B benchmarked before any store code and decided four things Group C is written against** —
the GIL **is** released (3.34x on four threads), `compress_level_zstd` defaults to **9**, there is
**no `corpus.workers` key**, and **Task 14 must set `k` explicitly** because the two dictionary
trainers disagree by up to 15% on their defaults alone. **The reasoning and the numbers are in the
phase's `notes.md` and frozen in its `evidence/`**; restating them here is the second copy this file
exists to avoid.

**Two traps worth carrying.** The dictionary is worth far more than the level (3.1x → 11.0x), so
tuning effort belongs there. And **the corpus has no usable validation split** — the smallest run has
two qualifying bodies — so Task 6's best `k` was chosen knowing the test slice, and **Task 15 must
call it provisional rather than optimal.**

**2026-08-17 — Phase 9 is merged** as **`b29d502`**. **Per-call files are the unit**; the decision is
in `reference/design-decisions.md` and the numbers in `reference/measurements.md`. **Read the 12.10×
as optimistic** — three biases flatter it and the slice beside it says which. **Phase 10's 13.65×
does not supersede it**: same three biases plus a fourth, its parameter chosen against the slice it
is reported on.

`main` is ahead of `origin/main` and nothing has been pushed. Phases 7 and 8 are closed. **The
documentation review is still parked whole** in `backlog.md`, including one cheap finding that would
make a session act wrongly — `reference/measurements.md:34`, a slice whose sign reverses.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero**: **68 broken and 2 roundabout on
`main`** (2026-08-18), and **86 broken, 2 roundabout, 82 files on this branch**, re-derived by running
on **2026-08-19**. *(It was 83 the same day, until `plan.md`'s new "The register" cited `corpus.py` and
`dictionary.py`, then 86 when `prompt.md` cited `corpus.py` too — three forward citations that Tasks 8
and 14 resolve. **The handoff file moving the baseline it quotes is the recursion to expect here**, not
a defect.)* The excess is
`backlog.md`'s recurring false-positive class, and **it rises when a task cites what it is about to
build and falls when the file appears** — today it went 79 → 80 → 76. **Run the tool; do not predict
it from the docstring**, which Phase 8 proved twice gives the wrong answer. *(`make test` is ~0.6 s
warm; a **first** run after the cloud folder evicts the virtualenv takes two to three minutes on
hydration alone — slow, not stuck.)*

## Where the project is

*Changes every phase.*

**One row per milestone. Per-phase detail lives in the archive** — branch, fork point and merge commit
belong to the phase note, and each milestone's own index reads its phases in order.

| | Subject | Phases | State | Read it in |
|---|---|---|---|---|
| **1** | The core router — dispatch, byte-relay, observability, failure handling | 1–7 | **complete** 2026-08-07 | `milestone-1-core/README.md`, which carries every branch and merge hash with what each phase settled |
| **2** | The corpus — capturing bodies for analysis | 8– | **open**, two phases in | `milestone-2-corpus/implementation-plan.md` **until the milestone closes**; its `README.md` is a closing artefact and does not exist yet |

*Changed 2026-08-17 from a per-phase table of Milestone 1's merge commits, per the `backlog.md` item
that proposed it. **The hashes are not lost** — each one keeps two to six homes, the fewest being
`532dc86` and `9c30924` at two apiece, and `milestone-1-core/README.md`'s table is strictly richer than
the one removed. What this file kept is
the part that is **state**; a closed milestone's per-phase merge hashes are archive record, and
`status.md` says so at the top.*

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What Milestone 1 settles:** no protocol translation is needed, and a local model can drive a real
coding session through the router. Both halves were measured rather than argued — one session reached
both backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2's subject is `EPD-003`** — capturing bodies for a corpus, **decided 2026-08-17**.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**One of its three failure modes is already discharged** by Phase 9's measurement; the other two —
that archiving cannot stay opaque, and that it slows a call — are Phase 10's to test.

**Two phases done, neither touching `src/`** — Phase 8 built the method tier and the guardrails, Phase 9
decided `EPD-003` and ran the gate that named the claim above. **Phase 10 is the first of this milestone
to touch `src/`.** `milestone-2-corpus/implementation-plan.md` describes both phases; **their merge
hashes are in their phase notes**, which is where `method/IDM-001-git-branching.md` puts the permanent
record. *(This sentence first said the plan indexes both hashes. It carries Phase 8's and not Phase 9's
— the plan's Record table records the branch **that file** was created on, which was Phase 8's.)*

*This paragraph carried both merge hashes and a note deferring to the `backlog.md` item above. **That
item is now decided and this is the evidence it asked for:** the prose version said "one phase of it is
done" after Phase 9 merged, and stayed wrong until the owner noticed — while the per-phase table beside
it never went stale, because a merged phase without a row is visibly missing and a sentence that
undercounts is not. **The conclusion is not "prefer tables"** — it is that the row-versus-prose choice
is about what goes stale invisibly, which is a different axis from the duplication the item was
arguing.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Execute Phase 10 — the body store, from Task 14 (Group D).** **Planned and reviewed 2026-08-18, re-scoped
   and reviewed a second time 2026-08-19; Groups A and B are done and no `src/` change exists yet.**
   The branch is in the table below and the task list is in
   `milestone-2-corpus/phase-10-body-store/plan.md`. **Do not re-plan or re-review it** — its
   re-derivation and **two** forward reviews have run, and **all findings from both are applied**
   (22 in each; the second's charter is `review-charter-retraining.md`).
   *(The 2026-08-19 re-scope is not an exception to that: it was an **owner interview**, not a session
   re-planning work it had been handed, and what it settled is in the plan's settled table with its
   rejected alternatives.)*
   `EPD-003`'s open questions 3–6 are answered in that plan and are **not yet written back into
   `EPD-003` itself** — that is its Task 20. *(This item read "Plan and execute" and restated what the
   phase must settle; the plan now holds that, so restating it here would be the second copy this
   structure exists to prevent.)*
2. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list. (`EPD-003` is no longer among them — decided
   2026-08-17 by Phase 9.)
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

| Branch | Purpose | Tree | Next |
|---|---|---|---|
| `feat/phase-10-body-store` | Phase 10 — the body store, forked at `d885b2f` | docs, the benchmark instrument, `pyproject.toml` / `uv.lock`, and **the whole store: `corpus.py` new, `config.py`, `proxy.py`, `observe.py`, `app.py`, `cli.py` and `config.yaml` all changed, `tests/test_corpus.py` new. `make test` 218.** `plan.md` now carries **"The register"**, and every value in it is settled | **Task 14** — the trainer, opening Group D. **Groups A, B and C are done**, the benchmark is frozen in `evidence/`, and the executor was chosen from measurement rather than argued. **Re-scoped and re-reviewed 2026-08-19** to thirty-two tasks — the router retrains itself, `13a`/`14a`–`14f` are lettered because execution has begun, and `14d` is **struck and absorbed into Task 11**. The tree also now carries `docs/wiki/`, `procedures/event-loop-lag/` and an `attribution` block in `.claude/settings.json` |

*`docs/phase-9-corpus-gate` merged as **`b29d502`** on 2026-08-17 and this table was empty until Phase
10 opened.*

**It was a `docs/` branch although the phase was about the router**, because no `src/` change survived
it: Task 6 patched `proxy.py` and restored it, and `git diff main -- src/` was empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work. **Phase 10 is the opposite case**, and it is: `feat/phase-10-body-store`,
opened 2026-08-18. *(This sentence read "will be" until then.)*

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
