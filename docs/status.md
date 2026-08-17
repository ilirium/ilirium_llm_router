# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-17 — Phase 7 is merged and Milestone 1 is closed.** `docs/milestone-boundary-restructure`
merged into `main` with `--no-ff` as **`9c30924`**, and the hash is recorded in
`milestone-1-core/phase-7-docs-restructure/notes.md` — the one closeout four earlier phase notes
never got. All fifteen tasks done; `docs/` has its finished shape and `CLAUDE.md` is 188 lines, down
from 337. `main` is ahead of `origin/main` and nothing has been pushed.

**The documentation review was parked whole**, findings and open questions alike, and lives in
`backlog.md` under "Documentation defects found and not fixed". Nothing in it has been acted on and
nothing is scheduled — including two cheap findings that would make a session act wrongly, which are
named there.

**The next work is the router, not the documentation:** open Milestone 2, starting at Phase 8.

**Before touching anything:** `procedures/link-check.py` before and after anything that moves, and
`make test` must report **158**. The checker **does not report zero** — its docstring says which hits
are correct and permanent, and the count it states is current.

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

**Milestone 2 is not open.** When it is, its plan goes in its own `milestone-N-<slug>/` folder, and
`README.md`'s opening playbook is the procedure.

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Open Milestone 2 — features in the router, not in the documentation.** Its subject is functions
   the router still lacks; which ones is named when it opens. `README.md`'s opening playbook is the
   procedure, and its first step is the one that matters: name a central claim that could come out
   false. Phase 8 is the first phase number available.
2. **Decide `EPD-001`, `002` or `003`.** All three are blocked on a person rather than on work, and
   two of them are argued on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions
   waiting on a person". Deciding one is cheaper than any measurement in the list.
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

**None.** Phase 7 merged as `9c30924` on 2026-08-17 and the table is empty until Milestone 2 opens a
branch. `main` is ahead of `origin/main`; `docs/milestone-boundary-restructure` still exists locally
and its remote is stale at `f473277`, from before execution started.
