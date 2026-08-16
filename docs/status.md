# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-16 — the documentation restructure is complete**, on
`docs/milestone-boundary-restructure`. All fifteen commits done; tree clean, `main` untouched and
level with `origin/main`. **The branch is not merged**, and merging it is the next action — with
`--no-ff`, and the merge hash written into
`milestone-1-core/phase-7-docs-restructure/notes.md`, which is the one thing four earlier phase notes
failed to do.

`docs/` has its finished shape and every citation in the repository resolves, including the eleven in
`src/`, `tests/` and `config.yaml`. `CLAUDE.md` is 188 lines, down from 337, and all nine session
memories are pointers into it.

**What the restructure cost is now a procedure**, not a memory: `README.md`'s closing playbook, mined
from the fifteen commits. The full record is `milestone-1-core/phase-7-docs-restructure/` —
`plan.md` for what was intended, `notes.md` for what each commit actually found.

**Before touching anything:** `procedures/link-check.py` must be run before and after anything that
moves, and `make test` must report **158**. The checker **does not report zero** — seven hits are
correct and permanent, plus 71 inside the archived restructure documents, which name old paths as
their subject. Its own docstring lists both classes and gives the invocation that skips the second.

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
| 7 | The documentation restructure — this file, the reference tier, the manual | **unmerged** |

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed; `milestone-1-core/README.md`
says why they are left that way. **Milestone 2 starts at Phase 8**, since 7 is taken.

**What it settles:** no protocol translation is needed, and a local model can drive a real coding
session through the router. Both halves were measured rather than argued — one session reached both
backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2 is not open.** When it is, its plan goes in its own `milestone-N-<slug>/` folder, and
`README.md`'s opening playbook is the procedure.

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Merge `docs/milestone-boundary-restructure`** with `--no-ff`, and write the merge hash into
   `milestone-1-core/phase-7-docs-restructure/notes.md`. The branch is complete and unmerged, and
   leaving the hash unrecorded is the exact defect `backlog.md` carries against four earlier phase
   notes.
2. **Decide `EPD-001`, `002` or `003`.** All three are blocked on a person rather than on work, and
   two of them are argued on a case Phase 4 measurably weakened — see `backlog.md`, "Decisions
   waiting on a person". Deciding one is cheaper than any measurement in the list.
3. **Measure whether Claude Code shows LM Studio's context error.** The strongest of the open
   measurements: it decides whether the most actionable message the local backend produces is ever
   seen. `backlog.md`, "Measurements left open".

## In-flight branches

*Merged branches are not listed — git already holds that, and a hand-maintained list would drift.
The permanent record of a phase's branch, fork point and merge commit belongs in its phase note.*

| Branch | Purpose | State |
|---|---|---|
| `docs/milestone-boundary-restructure` | `EPD-004`'s migration — Phase 7 | **Complete, all fifteen commits, tree clean. Waiting to be merged.** Pushed but well behind: the remote sits at `f473277`, before execution started |
