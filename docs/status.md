# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-17 — Phase 9's gate has passed and `EPD-003` is decided.** `docs/phase-9-corpus-gate`,
forked from `main` at `97f6563`. **Fifteen of sixteen tasks done**; only the close-out and merge
remain. `src/` is unchanged — the capture patch was applied, used and restored.

**The corpus proposal survives its own cheapest test.** On a held-out session of 20 real bodies:
per-file with no dictionary **3.12×**, per-file with a dictionary trained on *other* sessions
**12.10×**, one long-window stream **29.91×**. `EPD-003` set the test as "near the stream" against
"near the 3×"; 12.10× is four times the failure threshold. **Per-call files are the unit**, and the
decision is in `reference/design-decisions.md`.

**Read the 12.10× as optimistic.** The corpus is headless — its static preamble is ~28 KB smaller than
an interactive one — 70 of 73 bodies are Anthropic, and the sessions are short. All three flatter a
dictionary. `reference/measurements.md` carries the slice with the number.

**Two findings against `EPD-003` are independent of the gate** and hold whatever the numbers said:
**`calls.csv` expires** (`backup_count: 10`), so it cannot be the corpus's join table as the sketch
proposed; and **the capture missed 9 of 158 calls in testing**, all error paths — the rows `EPD-003`
calls the interesting ones. Both are marked in place and carried into Phase 10.

**Phase 8 merged as `22a6d20` and Phase 7 as `9c30924`, both 2026-08-17**; their permanent records are
their phase notes, and nothing about either is outstanding. `main` is ahead of `origin/main` and
nothing has been pushed.

**The documentation review is still parked whole** in `backlog.md`. One cheap finding that would make a
session act wrongly remains — `reference/measurements.md:34`, a slice whose sign reverses on
recomputation.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero** — its docstring says which hits are
correct and permanent, and the count it states was re-derived on 2026-08-17. **Do not predict that count
by reading the docstring; run the tool.** Phase 8 proved twice that reading it gives the wrong answer.

## Where the project is

*Changes every phase.*

**Milestone 1 — core router: complete.** Seven phases, 158 tests. The archive is
`milestone-1-core/`, and `milestone-1-core/README.md` reads it in order.

| Phase | Subject | Merge |
|---|---|---|
| 1 | The proxy — dispatch, byte-relay, streaming | fast-forwarded |
| 2 | Observability — the log and the 20-column CSV | `4d7d7f6` |
| 3 | Failure handling — disconnects, broken streams, transport errors | `cc65aed` |
| 4 | LM Studio parity — what the local backend accepts, honours and ignores | `50444c5` |
| 5 | Config and timeouts — credential modes, per-backend `read_timeout` | `c8401e9` |
| 6 | Review and cleanup — the first review phase | `532dc86` |
| 7 | The documentation restructure — this file, the reference tier, the manual | `9c30924` |

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed;
`milestone-1-core/README.md` says why they are left that way. **Milestone 2 starts at Phase 8**,
since 7 is taken.

**What it settles:** no protocol translation is needed, and a local model can drive a real coding
session through the router. Both halves were measured rather than argued — one session reached both
backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2 is open, and its subject is `EPD-003`** — capturing bodies for a corpus, **decided
2026-08-17**. `milestone-2-corpus/` holds its `implementation-plan.md`.

**Its central claim is now named**, at the end of Phase 9 and from what the gate returned:

> *The router can archive every body it carries — as opaque, content-addressed, per-call files
> compressed against a shared dictionary — without parsing a payload, without slowing a call, and
> without special storage infrastructure.*

**One of its three failure modes is already discharged** by Phase 9's measurement; the other two —
that archiving cannot stay opaque, and that it slows a call — are Phase 10's to test.

**One phase of it is done: Phase 8** — the method tier and the guardrails, merged as **`22a6d20`**. It
changed no `src/` and was housekeeping that would have been worth doing under any claim, which is the
only reason it could run before the claim existed. *Recorded here in prose rather than as a per-phase
table on purpose: `backlog.md` carries a proposal to replace Milestone 1's table above with one row per
milestone, and building a second such table would pre-empt that decision.*

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
   one is cheaper than any measurement in the list. (`EPD-003` is item 1 now, since Phase 9 takes it.)
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
