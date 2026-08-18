# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-18 — Phase 10 is open and planned, and nothing is executed.**
`feat/phase-10-body-store`, forked at `d885b2f`. **A `feat/` branch because `src/` gains a module and
keeps it** — the case `method/IDM-001-git-branching.md` separates from Phase 9's `docs/`. Its
`plan.md` carries **twenty-four tasks in six groups**, and its `notes.md` carries the
re-derivation: **nine findings, six against Phase 9's fenced sketch**, each also written as a question
with options.

**Three interviews, and the last two changed the design.** The first settled capture **opt-in and off
by default**, **no headers ever**, `zstandard`, and a scope with no live session. The second refused
an **unverified GIL claim** the write path rested on, adding **Group B: benchmark before any store
code**. The third settled diagnostics — **one tool not two, plain dictionary copies in
self-contained day folders, a configurable level, and one arrived-against-recorded counter pair** —
and reserved three further diagnostics to `backlog.md`.

**The forward review ran, and `method/IDM-004` is written from it.** Two passes over Tasks 4–24 —
this session and one fresh-context agent, read-only, in parallel — returned **22 findings at 18%
overlap**, all now applied. The cold pass **refuted a claim this session had written into four
documents including `backlog.md`**; it is corrected there and marked in place in the phase note.
`phase-10-body-store/review-charter.md` is the worked example the IDM points at.

**Group B is done — all three tasks — and it decided four things.** `zstandard 0.25.0` is a declared
runtime dependency; **the GIL *is* released**, read off the shipped binary at Task 4 and measured at
**3.26x on four threads** at Task 6, so the negative branch was not taken and Group C proceeds.
**`compress_level_zstd` defaults to 9** — 94% of level 19's dicted ratio for an eighth of the cost.
**There is no `corpus.workers` key**: one worker carries ~500x the target peak, which resolves the
contradiction the plan flagged between that promise and Task 11's five keys. And **the two dictionary
trainers disagree** — `zstandard`'s own choice of `k` is up to 15% worse than `zstd --train`, at
`k=8000` it is 13% better, so **the tool was never the variable and Task 14 must set `k` explicitly.**

**Two cautions carried forward.** The dictionary is worth far more than the level (3.1x → 11.0x), so
tuning effort belongs there. And **the corpus has no usable validation split** — run-02 contributes
two qualifying bodies — so Task 6's best `k` was chosen with knowledge of the test slice and Task 15
must call it provisional rather than optimal. The numbers are frozen in the phase's `evidence/`;
Task 21 puts them in `reference/measurements.md` with all four columns.

The task list was **renumbered** when permission was given — an exception to `README.md`, recorded in
the plan with the one cost that cannot be undone. **No `src/` change exists yet**; `git diff main --
src/` is still empty, and Task 8 is where that changes. *(This said "Task 4 is where that changes"
until 2026-08-18. Task 4 touches `pyproject.toml` and `uv.lock`, which are neither `docs/` nor
`src/`.)*

**2026-08-17 — Phase 9 is merged** as **`b29d502`**, all sixteen tasks done. **Per-call files are the
unit**; the decision is in `reference/design-decisions.md` and the gate's numbers in
`reference/measurements.md`. **Read the 12.10× as optimistic** — three biases flatter it, and the
slice beside that number says which. Do not quote it without them.

*Cut from five paragraphs to one on 2026-08-18, for this section's own ~30-line rule. Nothing is
lost: the narrative is in that phase's `notes.md`, the closeout rule it produced is in
`method/IDM-001-git-branching.md`, and its two findings against `EPD-003` are marked in place there.*

`main` is ahead of `origin/main` and nothing has been pushed. Phases 7 and 8 are closed with nothing
outstanding; their hashes are below and in their phase notes.

**The documentation review is still parked whole** in `backlog.md`. One cheap finding that would make a
session act wrongly remains — `reference/measurements.md:34`, a slice whose sign reverses on
recomputation.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero**: **68 broken and 2 roundabout on
`main`**, re-derived by running it on 2026-08-18 — and **80 on the Phase 10 branch** *(79 before Task
4)*: five are files that plan's own tasks create, one more is this file citing the benchmark directory
Task 5 creates, and six more are `review-charter.md` **listing the known false positives** so
a reviewer does not spend findings on them. All are `backlog.md`'s recurring class rather than
breakage. **Expect it to rise before it falls** — a task citing what it is about to build adds a hit,
and creating the file removes it. **Do not predict the count from the docstring; run the tool.** Phase 8 proved
twice that reading it gives the wrong answer. *(`make test` is ~0.6 s warm. A **first** run after the
cloud folder evicts the virtualenv takes two to three minutes on hydration alone — slow, not stuck.)*

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

1. **Execute Phase 10 — the body store, from Task 7.** **Planned and reviewed 2026-08-18; Groups A and
   B are done and no `src/` change exists yet.** The branch is in the table below and the task list is in
   `milestone-2-corpus/phase-10-body-store/plan.md`. **Do not re-plan or re-review it** — its
   re-derivation and its forward review have both run, and the review's 22 findings are applied.
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
| `feat/phase-10-body-store` | Phase 10 — the body store, forked at `d885b2f` | docs, the new benchmark instrument, and `pyproject.toml` / `uv.lock`. **`git diff main -- src/` is still empty; Task 8 is where that changes** | **Task 7** — the round-trip smoke test, opening Group C. **Groups A and B are done**, the benchmark is frozen in `evidence/`, and the executor was chosen from measurement rather than argued |

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
