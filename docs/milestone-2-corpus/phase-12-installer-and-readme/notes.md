# Phase 12 — notes

**Branch:** `feat/phase-12-installer-and-readme`, forked from `main` at `5cdc1c9`.

*Entry point for the phase. Group notes split out as `notes-group-<letter>.md` once groups have work
in them, per `../../README.md`.*

**All five groups are executed. What remains is the merge itself, and the owner asked to be waited
for before it runs.** After it: fill this phase's `Merge commit` line in `plan.md`, then regenerate
the branch index on the trunk — in that order, because the index row names the merge hash.

*Two things worth carrying out of the last two groups. Quick start's re-install and uninstall lines
were driven on the owner's go-ahead **after** Group D was first marked complete, and **both were
wrong** — see `notes-group-d.md`. And the register check found the `README.md` carrying five caveats
where settled row 6 says four — see `notes-group-e.md`.*

*This line replaced "Nothing has been executed yet" on 2026-09-02, which was true when the file was
created and false after task 1 — **in the phase's entry point, the first thing the next session
reads.** It was found by the owner asking whether anything needed checking before the session
closed, not by the sweep: the grep looks for markers of work *not* done, and this was a claim that
*nothing* was done.*

## Why this branch changes `backlog.md` and `IDM-001`

**2026-09-02, on the owner's instruction, and it is a rule change rather than phase work.**

The phase's planning produced a backlog item — that the group-notes rule is invisible at the moment
it applies. It was filed on a new `docs/` branch, on `IDM-001`'s authority that work not belonging
to a phase does not ride on that phase's branch.

**The owner reversed that, and the reasoning is now in `IDM-001`:** adding a backlog item is **how a
phase declines scope**, so it belongs on the branch that declined it. The rule being applied was
about *pre-empting a later phase's work*; a backlog item is the record that work is **not** being
done, which is the opposite thing.

`docs/group-notes-visibility` was deleted unmerged, its one commit's content moved here. It was
never described in `branch-index.py` and never reached `reference/branches.md`, which is the only
shape in which a branch here may be deleted at all.

*Recorded in this phase's notes because a reader will otherwise ask why a `feat/` branch amended the
method tier. The rule itself lives in `../../method/IDM-001-git-branching.md` and is not restated
here.*

---

## The group notes

**Each task group's notes go to `notes-group-<letter>.md`**, per `../../README.md`; this file keeps
what belongs to no group and stays the entry point. The plan has five groups — **A** open the phase,
**B** establish what already works, **C** the installer, **D** the documents, **E** close.

| File | Covers | Written |
|---|---|---|
| `notes-group-a.md` | Group A — open the phase | 2026-09-02 |
| `notes-group-b.md` | Group B — establish what already works | 2026-09-02 |
| `notes-group-c.md` | Group C — the installer | 2026-09-02 |
| `notes-group-d.md` | Group D — the documents | 2026-09-02 |
| `notes-group-e.md` | Group E — the close | 2026-09-02 |

**Deliberately no placeholder rows, and this is not tidiness.** At Phase 11's merge this index
carried `| *(none yet)* | Groups D, E, F | not started |` **directly beneath two rows naming files
for two of those groups**, all marked complete. The owner found it; `IDM-001`'s sweep could not,
because its pattern required parentheses the row did not have. A row that exists before its file
does is a placeholder waiting to go stale — **so a row appears here when the file appears**, and the
groups are named in the sentence above instead, where nothing can rot.

---

## The two reviews

**This phase was reviewed twice, and neither review's record is in this file.**

| Review | Subject | Charter | Findings |
|---|---|---|---|
| Forward, before task 1 | `plan.md` at `80914a0`, unexecuted | `review-charter.md` | `notes-review-plan.md` |
| Of the executed work, before the merge | the phase as built | `review-charter-jobs-done.md` | `notes-review-jobs-done.md` |

*The forward review's account lived in this file until 2026-09-02 and was moved out whole, on the
owner's decision, when a second review made "the review" ambiguous. `review-plan-jobs-done.md` is
what the second one was planned from.*
