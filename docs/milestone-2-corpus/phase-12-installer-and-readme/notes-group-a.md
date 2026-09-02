# Phase 12 — Group A: open the phase

*Tasks 1 and 2. Entry point is `notes.md`.*

## Task 1 — record the branch in `status.md`

**Done 2026-09-02.** `status.md`'s "In-flight branches" now names
`feat/phase-12-installer-and-readme`, opened from `5cdc1c9`, with what the phase is and why the
prefix is `feat/` rather than `docs/` — the `.env` fix and `--version`, both defects the forward
review found rather than planned work.

**This task exists because the review found the section saying "None" while the branch was open.**
That section's own closing paragraph records the same defect happening on 2026-08-21, and
`status.md` was in that state again when the review read it.

*Checked afterwards rather than assumed:* `branch-index.py --check` exits 0, reports 23 rows
current, and prints `in flight, not tabled: feat/phase-12-installer-and-readme — see
docs/status.md`. **That
message is only correct now** — the script has been printing it, pointing at a file that said
"None", since the branch opened.

## Task 2 — `evidence/README.md`

**Already done before it was a task, and recorded that way rather than re-done.** The file was
written during the review revision on 2026-09-02, in the same pass that added the task, because the
review found the phase folder incomplete against `README.md`'s phase template.

**What it says is the part worth keeping:** this phase's output is mostly *observation* rather than
artefact, so the file names the two things that would earn a place — a listing proving the config
template shipped inside the wheel, and a transcript of an installed run that contradicts the plan —
and states that if neither happens, the file is the record that neither happened.

*A task that was already satisfied when it was written is worth noticing rather than ticking.* It
happened because the review's finding and its repair landed in one pass; the plan then carried a
task for work that had been done in the act of planning it.
