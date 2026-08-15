# Documentation restructure — the migration plan

Written 2026-08-15 on `docs/milestone-boundary-restructure`. **Nothing here has been executed.**

The shape and the argument for it are in `docs/epd/EPD-004-documentation-structure.md`. This file is
the mechanical half: what moves where, what breaks when it does, and in which order to do it so that
a mistake is recoverable.

Read the seven silent breakages first. Five of them fail without an error message, and two of those
have already fired once in this repository.

## Scale

| | |
|---|---|
| Files under `docs/` | 68, of which **50 are tracked** by git |
| Untracked-but-present | `phase-3-verification/runs/`, `phase-4-probes/runs/`, `phase-4-probes/bodies/needle.json`, `.DS_Store` — all gitignored local scratch |
| Mentions of the 22 documents and directories that move | **253**, across `docs/`, `README.md`, `CLAUDE.md`, `src/`, `tests/`, `config.yaml`, `.gitignore` |
| Doc paths cited from code and config | **8**, in 6 files |
| `.gitignore` entries naming `docs/` paths | **4**, one of them a negation |
| Documents rewritten rather than moved | 4 — `CLAUDE.md`, `README.md`, `outstanding-work.md`, and the new `status.md` |

The mention count is why this is not a forty-minute job. Roughly a quarter of them are inside the
documents being moved, referring to each other.

---

## The seven things that break silently

**1. `probe.py` computes the repository root from its own depth.** `probe.py:40` is
`ROOT = HERE.parent.parent`, used at `:43` for `docs/log-the-whole-request.txt` and at `:44` for
`logs/calls.csv`. Moving `docs/phase-4-probes/` to `docs/procedures/lmstudio-capability-probes/`
takes it from two levels below the root to three. It will not raise on import — it fails later, when
`replay` cannot find the capture. **Both lines need editing, and `CAPTURE` needs editing twice** if
the capture also moves to `docs/captures/`.

**2. The `.gitignore` negation for `router.log`.** `.gitignore:59` is a blanket `*.log`;
`.gitignore:229` is `!docs/phase-2-step-6-session/router.log`, the exception that lets the frozen
session's log be committed. Move the directory without updating line 229 and the negation silently
stops applying. **This trap has already fired once** — `handoff.md` records that the original
`git add` on that directory skipped `router.log` for exactly this reason, and shipped a document
citing a file that was not in the repository.

**3. The two gitignored `runs/` directories.** `.gitignore:231` and `:233` ignore
`docs/phase-3-verification/runs/` and `docs/phase-4-probes/runs/`. If the directories move and those
lines do not, the next `git add -A` sweeps in a dozen local run transcripts that were deliberately
never committed. Fails in the wrong direction — nothing errors, the repository just grows.

**4. `docs/phase-4-probes/bodies/needle.json` is gitignored and regenerated.** `.gitignore:237`.
`handoff.md` records that it was regenerated to 41000 tokens for the Phase 5 runs and **put back** to
its committed 12000 default afterwards. It is local scratch; it moves with `mv`, not `git mv`, and
its ignore line moves with it.

**5. Docstring citations in `src/` are not tested.** Eight of them, and nothing fails if they rot:

| File | Line | Cites |
|---|---|---|
| `src/ilirium_llm_router/config.py` | 62 | `docs/phase-5-measurements/` |
| `src/ilirium_llm_router/proxy.py` | 321 | `docs/phase-2-step-6-session/calls.csv` |
| `src/ilirium_llm_router/stats.py` | 26 | `docs/phase-2-step-6-session/calls.csv` |
| `src/ilirium_llm_router/observe.py` | 12 | `docs/lmstudio-usage-check.md` |
| `tests/test_observe.py` | 9 | `docs/lmstudio-usage-check.md` |
| `config.yaml` | 24 | `docs/phase-5-measurements/` |
| `config.yaml` | 30 | `docs/anthropic-auth-check.md` |
| `config.yaml` | 44 | `docs/phase-4-notes.md` |

Phase 6 measured the source at 58% prose and kept it deliberately, on the grounds that the docstrings
carry measurements recorded nowhere else. That decision is what makes these citations load-bearing
rather than decorative — a dead path in `observe.py:12` breaks the chain from the scanner's rule back
to the run that established it.

**6. `probe.py`'s own header cites sibling documents by relative path.** `probe.py:6` names
`../log-the-whole-request.txt`, `:12` names `../epd/EPD-002-…`, `:26` names `../phase-4-notes.md`.
All three relative paths change. Its usage examples at `:20-23` print the old absolute path too.
The same applies to the `README.md` inside each evidence directory — several use `../` links.

**7. Rename detection degrades if a move and an edit share a commit.** `git log --follow` and
`git blame` track a rename through a pure `git mv`; a move plus a rewrite in one commit can drop
below git's similarity threshold and the file's history ends there. Given that the whole point of
this repository's documents is that they record when a thing was learned, **losing the history of
`phase-4-notes.md` would cost more than the restructure gains.** Hence the commit order below:
every move is its own commit, and no move commit changes a file's contents.

---

## File-by-file mapping

`git mv` throughout unless the row says otherwise.

### Tier 1 — reference (durable, assembled from existing text)

These are the only files whose *content* is composed rather than moved. Every fact is lifted
verbatim; the work is deciding which paragraph belongs to which file.

| New file | Assembled from |
|---|---|
| `docs/reference/architecture.md` | `CLAUDE.md` "Goal" + "The central architectural problem", long form |
| `docs/reference/design-decisions.md` | `CLAUDE.md` "Design decisions", rationale and measurements (statements stay in `CLAUDE.md`) |
| `docs/reference/observability.md` | `CLAUDE.md` "Observability: log + CSV stats" entire |
| `docs/reference/configuration.md` | `CLAUDE.md` credential modes + timeout semantics; `phase-5-notes.md` durable half |
| `docs/reference/backend-lmstudio.md` | `CLAUDE.md` LM Studio bullets; the parity table and context facts from `phase-4-notes.md` |
| `docs/reference/backend-anthropic.md` | `CLAUDE.md` "Anthropic model IDs"; the Result section of `anthropic-auth-check.md`; the 429 findings from `handoff.md` |
| `docs/reference/request-shape.md` | `CLAUDE.md` "Observed request shape" |
| `docs/reference/measurements.md` | **new** — every quoted number, its date, its instrument, its slice |
| `docs/reference/lessons.md` | **new** — the four "phase found its premise wrong" episodes, from the six phase notes |
| `docs/reference/README.md` | **new** — reading order and what each file answers |

### Tier 2 — procedures (re-runnable instruments)

| From | To | Note |
|---|---|---|
| `docs/lmstudio-usage-check.md` | `docs/procedures/lmstudio-usage-check.md` | cited by `observe.py:12` and `tests/test_observe.py:9` |
| `docs/anthropic-auth-check.md` | `docs/procedures/anthropic-auth-check.md` | cited by `config.yaml:30`; its *Result* is also lifted into `reference/backend-anthropic.md` |
| `docs/testing-against-claude-code.md` | `docs/procedures/testing-against-claude-code.md` | the procedure is reusable for any milestone |
| `docs/testing-against-claude-code--results.md` | `docs/milestone-1-core/phase-1-proxy/evidence/session-results.md` | results are Phase 1 history, not a procedure |
| `docs/phase-4-probes/{probe,make_needle,make_image}.py`, `README.md`, `bodies/` | `docs/procedures/lmstudio-capability-probes/` | **edit `probe.py:40,43` after the move** |
| `docs/phase-4-probes/bodies/needle.json` | same directory | gitignored — plain `mv`, and update `.gitignore:237` |
| `docs/phase-4-probes/runs/` | `docs/milestone-1-core/phase-4-lmstudio-parity/evidence/probe-runs/` | gitignored — plain `mv`, update `.gitignore:233`. Also update `RUNS` in `probe.py:42` if runs are to keep landing beside the phase rather than beside the probe |
| `docs/phase-3-verification/{dying_backend.py,router.yaml,README.md}` | `docs/procedures/dying-backend/` | the stub is a tool |
| `docs/phase-3-verification/runs/` | `docs/milestone-1-core/phase-3-error-handling/evidence/runs/` | gitignored — plain `mv`, update `.gitignore:231` |
| `docs/phase-5-measurements/read_timeout_semantics.py` | `docs/procedures/read-timeout-semantics.py` | a twenty-minute measurement that settled two wrong claims; worth keeping runnable |
| — | `docs/procedures/README.md` | **new** — the index, and when each check is worth re-running |

**On the `probe.py` `RUNS` question.** Its transcripts currently land next to the probe. If runs move
to the phase archive, the probe would be writing into a milestone folder, which is wrong for
Milestone 2. Proposed: `RUNS` stays beside the probe (`procedures/lmstudio-capability-probes/runs/`,
gitignored), and only the *Milestone 1* transcripts are copied into the phase evidence directory.

### Tier 3 — captures

| From | To |
|---|---|
| `docs/log-the-whole-request.txt` | `docs/captures/log-the-whole-request.txt` |

18 mentions across 11 files, plus `probe.py:6` and `probe.py:43`. See EPD-004 fork 4 — this is the
one path with a live alternative (`reference/captures/`).

### Tier 4 — EPDs

**Nothing moves.** `docs/epd/` stays, numbering untouched, `EPD-000`'s index gains a row for
`EPD-004` and its "Related documents that are not EPDs" closing section is rewritten to point at the
new tiers rather than at the old flat `docs/`.

### Tier 5 — the Milestone 1 archive

| From | To |
|---|---|
| `docs/handoff.md` | `docs/milestone-1-core/closing-notes.md` |
| `docs/implementation-plan.md` | `docs/milestone-1-core/implementation-plan.md` |
| `docs/outstanding-work.md` | `docs/milestone-1-core/outstanding-work.md` — **and its live items are lifted into `docs/status.md` first** (EPD-004 fork 3) |
| `docs/phase-1-notes.md` | `docs/milestone-1-core/phase-1-proxy/notes.md` |
| `docs/phase-2-notes.md` | `docs/milestone-1-core/phase-2-observability/notes.md` |
| `docs/phase-2-step-6-session/` | `docs/milestone-1-core/phase-2-observability/evidence/step-6-session/` — **update `.gitignore:229`** |
| `docs/phase-3-notes.md` | `docs/milestone-1-core/phase-3-error-handling/notes.md` |
| `docs/phase-4-notes.md` | `docs/milestone-1-core/phase-4-lmstudio-parity/notes.md` |
| `docs/phase-4-plan.md` | `docs/milestone-1-core/phase-4-lmstudio-parity/plan.md` |
| `docs/phase-4-evidence/` | `docs/milestone-1-core/phase-4-lmstudio-parity/evidence/` |
| `docs/phase-5-notes.md` | `docs/milestone-1-core/phase-5-credentials-and-timeout/notes.md` |
| `docs/phase-5-plan.md` | `docs/milestone-1-core/phase-5-credentials-and-timeout/plan.md` |
| `docs/phase-5-measurements/*.txt`, `README.md` | `docs/milestone-1-core/phase-5-credentials-and-timeout/evidence/` — cited by `config.py:62` and `config.yaml:24` |
| `docs/phase-6-notes.md` | `docs/milestone-1-core/phase-6-review/notes.md` |
| `docs/phase-6-plan.md` | `docs/milestone-1-core/phase-6-review/plan.md` |
| — | `docs/milestone-1-core/README.md` — **new**: what the milestone was, what it proved, the index |

Phase 0 has no notes file; it exists only as a section of `implementation-plan.md` and needs no
directory.

### Tier 6 — rewritten at the root

| File | What happens |
|---|---|
| `CLAUDE.md` | Cut to ~100 lines per EPD-004's table. Sections leave; one-line pointers naming their trigger replace them |
| `README.md` | "What it does today" gains the Milestone 1 result in two sentences; the pointer to `CLAUDE.md` becomes a pointer to `docs/reference/` for facts and `docs/status.md` for state. The "Description" brief stays verbatim |
| `docs/status.md` | **new** — milestones → phases → tasks, one page, plus "where we stopped". Takes over `handoff.md`'s live role |

---

## Commit order

Twelve commits. The principle: **no commit both moves a file and edits it**, so rename detection
survives (breakage 7), and any single step can be reverted without unpicking the rest.

| # | Commit | Why here |
|---|---|---|
| 1 | `EPD-004` + this plan | Already on the branch. The decision record precedes the work |
| 2 | Write `reference/measurements.md` and `reference/lessons.md` | **The gate.** EPD-004's cheapest next step: if the durable half will not separate from the process half, stop here having touched nothing |
| 3 | Create empty tier directories with their `README.md` index files | Gives every later move a destination that already explains itself |
| 4 | Assemble the remaining `reference/` files from `CLAUDE.md` and the phase notes | Content composition, no moves. `CLAUDE.md` is not yet cut — text is duplicated for one commit, deliberately |
| 5 | `git mv` the procedures, **including the gitignored `runs/` and `needle.json` by plain `mv`**, and update `.gitignore` in the same commit | The ignore rules must never be out of step with the paths, not even for one commit |
| 6 | Fix `probe.py` (`ROOT`, `CAPTURE`, `RUNS`, header paths, usage examples) and the moved `README.md` links | Separate from the move, so the move stays a clean rename |
| 7 | `git mv` the capture to `docs/captures/`, fix `probe.py:43` | Small, isolated, easy to revert if the fork is decided the other way |
| 8 | `git mv` the milestone archive; update `.gitignore:229` in the same commit | The `router.log` negation and its path move together (breakage 2) |
| 9 | Rewrite `CLAUDE.md` — cut the moved sections, insert the pointers | Only now, once every destination exists |
| 10 | Split `outstanding-work.md`; write `docs/status.md` | EPD-004 fork 3. Its own commit because it rewrites rather than moves |
| 11 | Rewrite the 253 cross-references, `README.md`, `EPD-000`'s index and closing section | The bulk edit, in one reviewable commit |
| 12 | Fix the 8 doc paths in `src/`, `tests/` and `config.yaml`; run `make test` and `make lint` | Code last, so a test failure has one obvious cause |

Merge `--no-ff` per repository convention, so the boundary stays visible.

## Verification

Green tests prove nothing about documents, so the checks are separate.

- **Link check.** A throwaway script over every `.md` in the repository: resolve each relative link
  and each backticked path that looks like a file, report the ones that do not exist. Run it before
  commit 11 to size the job and after commit 12 to close it. Worth writing — 253 references is well
  past what a careful read catches.
- **`git log --follow`** on `phase-4-notes.md`, `handoff.md` and `probe.py` after commit 12. Each
  must still reach its original commit. If one does not, the move and an edit shared a commit.
- **`git status --ignored`** after commits 5 and 8: the same four ignored paths as today, at their
  new locations, and nothing newly tracked.
- **Run the instruments.** `python3 docs/procedures/lmstudio-capability-probes/probe.py --list`, and
  `probe.py baseline` if LM Studio is up. This is the only check that catches breakage 1, and
  `--list` alone will not — it has to be a run that reads the capture.
- **`make test` and `make lint`.** 158 tests, before and after. Any change in the count means this
  work touched behaviour, which it must not.
- **Read `CLAUDE.md` end to end** and ask of each removed section whether the pointer that replaced
  it names *when to open the file*. A pointer that only says the file exists is not a replacement.

## Rollback

Each commit is revertible in isolation except 5 and 8, which pair a move with its `.gitignore`
update by design. The branch is `docs/milestone-boundary-restructure`; `main` is untouched until the
merge, and no commit here changes anything under `src/` except eight comment lines in commit 12.

## What this plan does not cover

- **Milestone 2's own contents.** `docs/status.md` gains a backlog section; what goes in it is a
  separate decision, informed by the three EPDs and by `outstanding-work.md`'s live items.
- **Whether `EPD-001`, `002` or `003` are accepted.** Untouched by this work. They keep their
  numbers, their status lines, and their place.
- **Any change to router behaviour.** If this branch changes what the router does, that is a defect
  in the branch.
