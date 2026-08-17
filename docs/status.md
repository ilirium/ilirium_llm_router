# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-17 — Phase 9 is merged.** `docs/phase-9-corpus-gate` merged into `main` with `--no-ff` as
**`b29d502`**, and the hash is in `milestone-2-corpus/phase-9-corpus-gate/notes.md`, which is the
permanent record. **All sixteen tasks done**, no letters inserted. `git diff main -- src/` is empty —
the capture patch was applied, used and restored — and `make test` reports **158**.

**The corpus proposal survives its own cheapest test.** On a held-out session of 20 real bodies:
**3.12×** per-file, **12.10×** per-file with a dictionary trained on *other* sessions, **29.91×**
streamed. **Per-call files are the unit**; the decision and the test it had to beat are in
`reference/design-decisions.md`.

**Read the 12.10× as optimistic** — three biases flatter it, and `reference/measurements.md` carries
them in the slice beside the number. Do not quote it without them.

**`IDM-001` gained a rule afterwards, from two defects the owner found in this session's own output:**
status placeholders — `*(not started)*`, "fifteen of sixteen", "not yet merged" — are closed out **as
part of the merge**, in every form and not just the `Merge commit` row. Both misses happened *after*
reading `IDM-001`, because it named a row and so got obeyed as a row.

**Two findings against `EPD-003` are independent of the gate** and hold whatever the numbers said:
**`calls.csv` expires** (`backup_count: 10`), so it cannot be the corpus's join table as the sketch
proposed; and **the capture missed 9 of 158 calls in testing**, all error paths — the rows `EPD-003`
calls the interesting ones. Both are marked in place and carried into Phase 10.

`main` is ahead of `origin/main` and nothing has been pushed. Phases 7 and 8 are closed with nothing
outstanding; their hashes are below and in their phase notes.

**The documentation review is still parked whole** in `backlog.md`. One cheap finding that would make a
session act wrongly remains — `reference/measurements.md:34`, a slice whose sign reverses on
recomputation.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero** — its docstring says which hits are
correct and permanent, and the count it states was re-derived on 2026-08-17. **Do not predict that count
by reading the docstring; run the tool.** Phase 8 proved twice that reading it gives the wrong answer.

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

1. **Plan and execute Phase 10 — the body store.** The first `feat/` phase of this milestone and the
   first to touch `src/`. `implementation-plan.md` has it in outline, and
   `phase-9-corpus-gate/plan.md` carries a fenced design sketch written before the gate ran — **input
   to be re-derived, not a specification.** It must settle the write path (a bounded off-thread queue
   and a drop policy), `EPD-003`'s open questions 3–6, capture at the point of failure, a dictionary
   bootstrap and retraining policy, and the `logs/telemetry/` move.
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

**None.** `docs/phase-9-corpus-gate` merged as **`b29d502`** on 2026-08-17 and the table is empty until
the next phase opens a branch.

**It was a `docs/` branch although the phase was about the router**, because no `src/` change survived
it: Task 6 patched `proxy.py` and restored it, and `git diff main -- src/` was empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work. **Phase 10 will be the opposite case**: it builds
the store, so it is `feat/`.

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
