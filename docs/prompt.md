# The next session's prompt

*The one file in `docs/` allowed to go stale, per `README.md` — which is why it is rewritten at each
handoff rather than left. **Replaced 2026-09-04** at task 3a and **updated the same day** at the end
of Group D. The version it replaced described Phase 12's close and said nothing was in flight, which
stopped being true the moment this branch opened. Whatever comes next replaces it again.*

---

**Phase 13 is open. Groups A through D are complete — all three method documents are written and in
force.** Branch `docs/phase-13-method-and-backlog`, worktree of the same name, forked from `main` at
`dec7c4a`. **Milestone 2 has five phases merged and this one in flight.**

**What remains is Group E — the backlog refactor — then Group F, which is this phase reviewed under
the `IDM-009` it just wrote, then the close.**

**Start in the phase worktree**, not in `main`:
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-13-method-and-backlog`. It has **no venv**,
so `uv run` does not work there until one is made — and nothing in this phase needs one, because
**Phase 13 changes no `src/` and no `tests/`.** The trunk's **448 tests** stand by construction.

## What Phase 13 is

**Four deliverables, set by the owner on 2026-09-03.** Three write down a practice the repository
already has and has already failed to keep; the fourth applies one of them.

| | |
|---|---|
| **`IDM-009`** | Reviewing **executed** work, written from what Phase 12's run cost |
| **`IDM-010`** | The per-phase `for-the-owner.md` — Phase 11 invented it, Phase 12 wrote none |
| **`IDM-011`** | The backlog — ids, statuses, categories, and **who may file an item** |
| **The refactor** | Every item gains a `BKL-NNNN` id, a metadata line, and a row in a generated table |

**Twenty-four settled rows, twenty-nine tasks, seven groups.** B, C and D are **done**. **Group E
stops at task 14 for the owner.**

**One rule of `IDM-011` is in force now and changes what you do:** **ask the owner before filing a
backlog item.** If the answer is no, the decline goes in the phase's `notes.md`. `IDM-001` and
`backlog.md` said for two days that filing was the phase's own act; both are amended.

## Read these, in this order

1. **`docs/status.md`** — first, every session. The only file that holds state.
2. **`.../phase-13-method-and-backlog/plan.md`** — the settled table and the register, at minimum.
   Grep the headings.
3. **`notes.md`**, then the group notes you need. **`notes-review-plan.md`** holds what the forward
   review found; **`notes-group-d.md`** holds the `IDM-001` amendment and why it is the second in
   three days.
4. **`for-the-owner.md`** if you are the owner. Five entries, written during the phase.

**`review-charter.md` is spent** — do not read it unless you are writing the task-21 charter, which
is modelled on it.

## What Group A settled that changes the rest

- **A rule two days older than the phase is being amended.** Settled row 9: **a session asks before
  filing a backlog item**, and if the owner declines, the decline goes in `notes.md`. `IDM-001`
  currently says filing *is* how a phase declines scope. Task 11 changes it. **This is in force
  now** — do not file a backlog item during this phase without asking.
- **Ids are allocated in file order** (row 24), **metadata is placed per shape** (row 21), and
  **`backlog.md` has three item shapes, not one** — prose with a bold opening, three table rows in
  *Decisions waiting on a person*, and two `###` subsections in *Dictionaries*.
- **`for-the-owner.md` is one-way** (row 20). Nothing formally closes an entry, and an unanswered
  `ASK` is not a defect.

## Five things a session will get wrong here

- **A number in a document is unverified until you open the thing it describes.** This phase has
  been wrong about counts **three times in four commits** — twice about Phase 11's
  `for-the-owner.md`, once relaying a figure from 2026-08-26. Every one was caught by opening the
  file, none by rereading the prose.
- **`review-plan-jobs-done.md` leaves ONE question open, not four.** The plan said four; one of
  the four is **settled row 1 of that same file**, decided by the owner. Answering it would
  re-decide an owner row. See `notes-review-plan.md`, finding C1.
- **`make lint` cannot see column width.** `E501` is not in ruff's default set. Count characters by
  hand and **re-measure after every fix**. `status.md` carries **15** over-width prose lines that
  predate this branch — do not read them as this phase's.
- **`link-check.py`'s count is a property of the worktree.** Compare against a run in the *same*
  tree or not at all.
- **Push state cannot be checked from here.** `origin` is configured but this clone holds **no
  remote-tracking refs** — `git branch -r` is empty. Ask the owner; do not infer.

## What is next

**Group E, the backlog refactor — and task 13 is the one to be careful with.**

**Task 13 compiles the item inventory and then stops.** Ids in **file order**; metadata placed **per
shape**, because `backlog.md` holds **three item shapes** and two of its eight sections have no bold
opening at all — *Decisions waiting on a person* is three table rows, *Dictionaries* holds two items
as `###` subsections.

**Task 14 is the owner's checkpoint and produces no commit.** They ratify the inventory and prune
it. **Nothing is applied before it returns**, because a wrong boundary freezes a wrong id into a
scheme whose whole premise is that ids never change.

*The forward review's three-shape survey read three of eight sections by grep only, so it is a lower
bound. **Re-survey all eight before compiling the inventory.***

## Open, and none of it blocks

- **Nobody has driven the corpus tools by hand.** Named as the owner's first job at Phase 11's
  handoff; still not done.
- **`BUG-001` is still unreported** to either upstream issue.
- **Failure mode 3 is undischarged** — whether archiving *slows* a call.
- **A call can still vanish**, and closing it needs a guarantee a row is never written twice.
- **The `uv_build` pin bump to `<0.13` has no rule behind it.** An owner decision, in `backlog.md`.
- **The Milestone 2 phase count has gone stale four times.** Filed in `backlog.md` with three
  candidate fixes and none chosen.

**One item that was here is discharged.** *`status.md`'s "Where we stopped" was 154 lines against
its own ~30-line limit. It was cut to the current session on 2026-09-04 — **not moved to a new
file**, because every fact in the four removed entries was checked and found to have a durable home
already. A new file would have been a fifth home for facts that had four.*

## The working agreement still applies

`CLAUDE.md`, in full. Three earned their place in Group A: **propose before implementing** — the
plan was interviewed over four rounds before a line was written; **exercise it before committing** —
the re-derivation found the plan wrong twice in the commit before it; and **raise it, do not bury
it**, which is now settled row 9's whole subject.

To which Group A adds one: **the charter decides what the review finds, and a refuted claim can
improve a finding rather than kill it.** The cold reader refuted the evidence behind settled row 13.
The rule stood; what changed is that Phase 11's file turned out to show something better — that
`ERRAND` was missing, which is *why* two errands were filed as questions.
