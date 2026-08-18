# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-18 — Phase 10 is executing. Groups A and B are done; the next task is 7.**
`feat/phase-10-body-store`, forked at `d885b2f`, **twenty-five tasks in six groups**. Its `plan.md`
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
`main`**, **76 on this branch**, both re-derived by running on 2026-08-18. The excess is
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
