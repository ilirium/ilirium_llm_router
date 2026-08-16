# Status

**State, not inventory.** Unscheduled work lives in `backlog.md`; this file says where the project
is and what is in flight. Three sections, most volatile first.

---

## Where we stopped

*Changes every session. If this section passes ~30 lines, or starts carrying anything that outlives
the session that wrote it, it has become a document and gets its own file.*

**2026-08-16 — the documentation restructure is in flight**, on
`docs/milestone-boundary-restructure`. Commit 12 of a fifteen-commit plan; tree clean, `main`
untouched and level with `origin/main`. This file and `backlog.md` are what commit 12 produced.

**The live detail is in `handoff-docs-restructure.md`** — what each commit found, what is repointed
and what is not, and the next action. That file is temporary and self-terminating: at commit 15 its
content becomes this section and it is deleted. Until then it is the working record and this is the
pointer, so that two files never both answer "where are we".

**Before touching this branch:** run `procedures/link-check.py` before and after anything that moves,
and `make test` must report **158** on both sides — the branch must not touch behaviour. The checker
currently reports two expected hits, both cleared by later commits.

## Where the project is

*Changes every phase.*

**Milestone 1 — core router: complete.** Six phases, all merged to `main`, 158 tests. The archive is
`milestone-1-core/`, and `milestone-1-core/README.md` reads it in order.

| Phase | Subject | Merge |
|---|---|---|
| 1 | The proxy — dispatch, byte-relay, streaming | fast-forwarded |
| 2 | Observability — the log and the 20-column CSV | `4d7d7f6` |
| 3 | Failure handling — disconnects, broken streams, transport errors | `cc65aed` |
| 4 | LM Studio parity — what the local backend accepts, honours and ignores | `50444c5` |
| 5 | Config and timeouts — credential modes, per-backend `read_timeout` | `c8401e9` |
| 6 | Review and cleanup — the first review phase | `532dc86` |

Phases 0 and 1 were fast-forwarded before the `--no-ff` convention existed; `milestone-1-core/README.md`
says why they are left that way.

**What it settles:** no protocol translation is needed, and a local model can drive a real coding
session through the router. Both halves were measured rather than argued — one session reached both
backends, and a local model handled tool use, file editing and multi-turn conversation.

**Milestone 2 is not open.** When it is, its plan goes in its own `milestone-N-<slug>/` folder, and
`README.md`'s opening playbook is the procedure.

## What is next

*Changes every phase. Two or three items lifted from `backlog.md` and cited to it — the file itself
is the full inventory.*

1. **Finish the restructure.** Commits 13 to 15: repoint the cross-references the link checker
   reports, fix the doc citations in `src/`, `tests/` and `config.yaml`, then write the closing
   playbook from what this actually cost and retire both migration documents.
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
| `docs/milestone-boundary-restructure` | `EPD-004`'s migration, fifteen commits | Commit 12 done, tree clean. Pushed but behind — the remote sits at `f473277`, before execution started |
