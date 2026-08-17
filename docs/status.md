# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-17 — Phase 9 is open and paused after Task 4.** `docs/phase-9-corpus-gate`, forked from
`main` at `97f6563`. **Sixteen tasks in four groups**; Group A (1–4) is done, and the phase is
deliberately stopped **before anything touches the machine**. Nothing is captured, no `src/` is
patched, and no measurement has been run.

**`EPD-003` is now partly accepted.** The owner decided its open question 1 on 2026-08-17:
**fine-tuning is dropped and the corpus is for analysis only.** Everything else in that document was
downstream of it. What stays open is per-call files against per-session streams, which its gate
decides — that is Group C.

**The opening interview found five things wrong, three of them about `EPD-003` itself**, and they are
in `milestone-2-corpus/phase-9-corpus-gate/plan.md`. Two matter beyond this phase:

- **The capture is *not* discharged.** `implementation-plan.md` hedged that it might be; it is not.
  `captures/` holds **one** body, and one body cannot exercise a cross-body dictionary. **The gate is a
  live capture session plus twenty minutes of `zstd`, not twenty minutes of `zstd`.**
- **`calls.csv` expires**, so `EPD-003`'s plan to make it the corpus's join table fails — `backup_count:
  10` discards the oldest segment, leaving bodies that outlive their own index. **Independent of the
  gate**, and marked in place in `EPD-003`.

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

**Milestone 2 is open, and its subject is `EPD-003`** — capturing bodies for a corpus, **partly
accepted 2026-08-17**. `milestone-2-corpus/` holds its `implementation-plan.md`. **Its central claim
is still deliberately not named**: the fine-tuning half is decided, but the storage question is not,
and a claim written before the gate would be a prediction wearing a measurement's clothes. It gets
written at the end of Phase 9, from what the gate returns. The plan says so in place.

**One phase of it is done: Phase 8** — the method tier and the guardrails, merged as **`22a6d20`**. It
changed no `src/` and was housekeeping that would have been worth doing under any claim, which is the
only reason it could run before the claim existed. *Recorded here in prose rather than as a per-phase
table on purpose: `backlog.md` carries a proposal to replace Milestone 1's table above with one row per
milestone, and building a second such table would pre-empt that decision.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Continue Phase 9 at Task 5** — the branch is open and paused after Group A. What remains: capture
   real bodies (Group B), run the gate (Group C), then decide and harvest (Group D). **The decision
   half is done** — fine-tuning is dropped. **The gate is no longer a twenty-minute measurement**: it
   needs a live capture first, because `captures/` holds one body and the gate is about what happens
   *between* bodies. `milestone-2-corpus/phase-9-corpus-gate/plan.md` has all sixteen tasks. **The
   milestone's central claim is written at the end of this phase.**
2. **Decide `EPD-001` or `002`.** Both are blocked on a person rather than on work, and both are argued
   on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions waiting on a person". Deciding
   one is cheaper than any measurement in the list. (`EPD-003` is item 1 now, since Phase 9 takes it.)
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

| Branch | Purpose | Tree state | Next action |
|---|---|---|---|
| `docs/phase-9-corpus-gate` | Phase 9 — decide `EPD-003`, run its gate | clean; four commits, Group A only | **Task 5.** Verify the capture directory's ignore coverage, then Task 6's capture — which needs the owner's go-ahead, since it patches `proxy.py`, runs the router and makes real API calls |

**It is a `docs/` branch although the phase is about the router**, because no `src/` change survives
it: Task 6 patches `proxy.py` and restores it, and `git diff main -- src/` must be empty at the merge.
`method/IDM-001-git-branching.md` is what makes that the right prefix — the prefix says what kind of
work it is, and `phase-N-` says it is numbered work.

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
