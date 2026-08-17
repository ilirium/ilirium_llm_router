# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-17 — Phase 8 is merged.** `docs/phase-8-method-and-guardrails` merged into `main` with
`--no-ff` as **`22a6d20`**, and the hash is in
`milestone-2-corpus/phase-8-method-and-guardrails/notes.md`, which is the permanent record. All
seventeen tasks are done, plus two inserted by the phase's own re-derivation (**12a** and **17a**,
lettered rather than renumbered). `docs/method/` now holds `IDM-000` through `IDM-003`; the tracked
`.claude/settings.json` exists; the local allowlist went **53 → 21** with zero overlap between the two
files. `procedures/link-check.py` reports **68 broken and 2 roundabout**, its docstring re-derived to
match, and `make test` reports **158**. `main` is ahead of `origin/main` and nothing has been pushed.

**The phase's own re-derivation found its plan wrong in four places**, which is the fifth of Milestone
1's-and-2's phases to find that. The one worth carrying forward: **nobody can predict
`link-check.py`'s hit count by reading its docstring.** The plan said 77, the re-derivation written to
catch the plan's error said 76, the tool says 68 — because the docstring partitions hits by where they
live and what resolves them is which path they name. Five of its seven "permanent" hits stopped being
permanent in one phase, and ten more copies of the same two paths resolved inside the frozen archive,
under a sentence saying they never would.

**Earlier that day — Phase 7 was merged and Milestone 1 closed.** `docs/milestone-boundary-restructure`
merged into `main` with `--no-ff` as **`9c30924`**, and the hash is recorded in
`milestone-1-core/phase-7-docs-restructure/notes.md` — the one closeout four earlier phase notes
never got. All fifteen tasks done; `docs/` has its finished shape and `CLAUDE.md` is 188 lines, down
from 337 — **203 after Phase 8**, which cut two sections to pointers and added one.
`main` is ahead of `origin/main` and nothing has been pushed.

**The documentation review is still parked whole**, findings and open questions alike, in `backlog.md`
under "Documentation defects found and not fixed". **One** cheap finding that would make a session act
wrongly remains — `reference/measurements.md:34`, a slice whose sign reverses on recomputation. The
second was `README.md`'s closing worked example, which Phase 8 took because it was already rewriting the
sentence.

**The next work is the router, not the documentation.** Phase 8 was the last of the housekeeping;
Phase 9 decides `EPD-003` and runs its gate.

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

**Milestone 2 is open, and its subject is `EPD-003`** — capturing bodies for a corpus.
`milestone-2-corpus/` holds its `implementation-plan.md`. **Its central claim is deliberately not
named yet**: EPD-003 is still a proposal, so a claim written now would be a prediction wearing a
measurement's clothes. It gets written at the end of Phase 9, from what the gate returns. The plan
says so in place.

**One phase of it is done: Phase 8** — the method tier and the guardrails, merged as **`22a6d20`**. It
changed no `src/` and was housekeeping that would have been worth doing under any claim, which is the
only reason it could run before the claim existed. *Recorded here in prose rather than as a per-phase
table on purpose: `backlog.md` carries a proposal to replace Milestone 1's table above with one row per
milestone, and building a second such table would pre-empt that decision.*

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Open `/permissions` once.** The one Phase 8 check a session cannot run for itself: tracked and local
   settings are merged by the harness, and the merge is the thing that was designed. It was verified by
   computing it from the two files — 14 + 21, overlap 0, 35 effective allow, 3 deny — which is not the
   same as reading the harness's own view. See `milestone-2-corpus/phase-8-method-and-guardrails/notes.md`,
   Task 14 check 6. Worth confirming `lms load` prompts while there; that could not be tested either.
2. **Decide `EPD-001`, `002` or `003`.** All three are blocked on a person rather than on work, and
   two of them are argued on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions
   waiting on a person". Deciding one is cheaper than any measurement in the list.
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

**None.** Phase 8 merged as `22a6d20` on 2026-08-17 and the table is empty until the next phase opens a
branch.

`docs/phase-8-method-and-guardrails` was the first branch to **carry a phase number on a `docs/`
prefix** — the form it settled: the prefix says what kind of work it is, `phase-N-` says it is a phase.
`method/IDM-001-git-branching.md` now states that as the rule, with Phase 7 as the old form and Phase 8
as the new one. `main` is ahead of `origin/main` and nothing has been pushed;
`docs/milestone-boundary-restructure` and `docs/phase-8-method-and-guardrails` both still exist locally.
