# IDM-006 — Closing a milestone

**In force 2026-08-20.** Moved out of `../README.md`, where it was written on 2026-08-16, and repaired
on the way — the version there had become the narrative of the restructure that produced it. `E16`
below is that episode.

**To run a close, read to "End of procedure" and stop.** Everything below that line is evidence: what
each rule cost, and where the frozen record of it is. It is there to be argued with and to be extended
after the next close. It is not needed to do the work, and a session reading it in order to act is
paying for detail it cannot use.

Markers like `E4` in the procedure point into that table. Nothing in the procedure depends on them.

---

## The nine steps

### 1. Freeze the plan and the phase notes `E1`

From here they record what was believed at the time and are not revised.

→ `../README.md`, **"Editing the archive: paths yes, claims no, transcripts never"** — a path is
navigation and may be repointed; a claim records what was believed then and may not; a captured
transcript is evidence and is never touched. Read it before the first repoint, not after.

### 2. Write `milestone-N-<slug>/README.md` `E2`

What the milestone set out to prove, what happened, and what it cost.

**Write it for the finished shape of the archive, not the current one.** An index listing three of its
eventual seven files is worse than one written slightly ahead of the files it names: the first is
silently incomplete, the second is visibly early.

### 3. Harvest the durable facts into `../reference/`

The step the whole close exists for, and the one with the most ways to go wrong.

- **The work is deciding what each file does *not* take.** `E3` A first draft will pull in material
  that already has a home. Cut it, and leave a table naming where each cut thing lives **and the
  trigger that sends you there** — a pointer saying only that a file exists does not replace a section.
- **Plan the destinations before the extraction, not during it.** `E4` The hard part is not unpicking
  the narrative of a phase note. It is **destination collision**: durable facts belonging to files that
  do not exist yet.
- **Move by repairing each tier's links in the same commit as the move that breaks them.** `E5` Only
  the archive waits. A reference document that is wrong for four commits is one nobody can trust while
  the work is still running.
- **Harvest the hardest thing first, as a gate.** `E6` Take the single hardest document and pull its
  durable half out before planning the rest. If the durable half will not separate from the process
  half, the plan for the remainder is wrong, and you have spent an hour finding that out instead of a
  week.

### 4. Process the lessons into `../reference/lessons.md` `E7`

Where the project was wrong, and what caught it.

Episodes like these are recorded as asides at the foot of the phase note that produced them, **which is
exactly where they will not be read at the start of the next milestone.** The notes stay frozen; the
lesson lands here.

**Harvest the closing phase's own lessons too.** A close that harvests only its predecessors drops the
most recent thing the project learned — and the close is where the sharpest lessons are, because it is
the first time the whole body of work is read at once.

### 5. Put the numbers into `../reference/measurements.md` `E8`

One canonical row per number, whatever prose also quotes it.

**A number must have a job, and must be able to do it.** A figure no decision depends on is clutter; a
figure a decision depends on and which cannot support it is worse, because it gets quoted forward.

### 6. Move the live items into `../backlog.md` `E9`

Unscheduled work, **each item with why it is parked**, and where it applies, why the question may be
weaker than it looks.

That column is the point of the file. An inventory with no reasons attached is one nobody can prune,
because a milestone later every item in it looks equally alive.

### 7. Reset `../status.md` `E10`

State only: where the project is, what is next. **No work items.**

Mixing state and inventory makes a handoff and a work survey overlap, each drifting from the other,
each looking authoritative. A backlog item that has migrated into the status file is the first sign of
it recurring.

**Sweep for placeholders while doing it.** → `IDM-001-git-branching.md`, **"Closing out a status
placeholder is part of the merge"**: the rule covers any statement of unfinished state — a table row, a
section marker, a count in prose, a claim of absence — not only a `Merge commit` row.

### 8. Repoint every citation, then re-check

Run `../procedures/link-check.py`, repoint what it reports, **then the citations in `src/`, `tests/`
and config, which it cannot see.** `E11`

**Six things will bite here.**

- **Searching for what moves will not find what gets cut.** `E12` A grep for moving paths structurally
  cannot find a citation that names a *section title*. Those are found by reading.
- **A path can be simultaneously valid and wrong.** `E13` A file inside the archive addressing its own
  sibling by going out to `docs/` and back resolves perfectly, and is absurd.
- **A name-based rewrite cannot fix a link that broke by depth**, and will confidently make it worse.
  Repoint by depth, and read the diff.
- **Longer paths break the wrap**, and a mechanical reflow will corrupt a numbered list if it is not
  written to respect one. Check the reflow against a list before trusting it.
- **A path inside a code fence may be relative to the repository root**, not to the citing file.
  Rewriting it "correctly" makes the command wrong.
- **Check the claim you are planning against, including when it is your own.** `E14`

### 9. Rewrite this playbook, last `E15`

From what the close actually cost, rather than from what it seemed like it should be. A playbook
written before the work is an instrument that has never been run.

**Append; do not replace.** `E16` This is the step most likely to damage the document it improves. A
close that is also unusual — the first one, or one that builds the structure it files into — produces a
vivid narrative that reads like a procedure and is not one. Keep it below the line, and leave the nine
steps standing.

---

## End of procedure

*Everything below is evidence. It is not needed to run a close.*

## Why each rule is here

Every row happened in this repository. The commits are Milestone 1's close,
`../milestone-1-core/phase-7-docs-restructure/`, whose `notes.md` records what each one cost.

| | The rule it supports | What happened | Where the record is |
|---|---|---|---|
| **E1** | Freeze, and edit paths only | `b6cc74f` archived Milestone 1 and dropped two instructions that would have committed thrown-away work | `phase-7-docs-restructure/notes.md` |
| **E2** | Write it for the finished shape | `46c8321` wrote the milestone README alongside the tier indexes, before the files they index existed. The plan's separate step *"write the tier indexes for the finished shape, not the current one"* was one-time — the tiers exist now — and this is what survives of it | `phase-7-docs-restructure/plan.md`, commit 3 |
| **E3** | Decide what each file does *not* take | `a3e88bc` assembled the first four reference files out of `CLAUDE.md`. The plan's separate step *"assemble the reference tier"* was one-time; the recurring part is this rule | `../reference/README.md` |
| **E4** | Plan destinations before extracting | The plan predicted the narrative drag of phase notes would be the hard part. It was not. The hard part was destination collision, and the plan said so afterwards | `phase-7-docs-restructure/notes.md` |
| **E5** | Repair links in the moving commit | Practised across the moves; `f5b993c` is what it looks like when a move lands and the repair is a separate commit — *"fixed: what the move broke, and two things the plan did not predict"* | `phase-7-docs-restructure/notes.md` |
| **E6** | Harvest the hardest thing first | `394d910` pulled the LM Studio parity table out as a gate before the rest was planned; it passed and the plan survived. **Weaker now than it was**: the gate could once discover that the whole split was wrong, and that question is settled, so what remains is a sequencing rule | `phase-7-docs-restructure/plan.md`, commit 2 |
| **E7** | Harvest the closing phase's own lessons | `5924bcc` harvested the six phases before it; `5758a55` added lessons 6 and 7, both learned by the close itself. Without the second commit the most recent lessons would have been the ones lost | `../reference/lessons.md` |
| **E8** | A number must have a job | `ad1d5ae` settled the rule and `08280ed` deleted a number that could not do its job — found by a fresh-context review, not by the author | `../reference/measurements.md` |
| **E9** | Keep the *why parked* column | `4f67b4a` split the archived outstanding-work survey into state and inventory. The column is what makes the inventory prunable | `../backlog.md` |
| **E10** | State and inventory stay apart | Milestone 1's handoff and its outstanding-work survey overlapped, drifted, and both read as authoritative. Both are now in that milestone's archive | `../milestone-1-core/` |
| **E11** | The checker cannot see code | `da68dc6` repointed **eleven** citations in `src/`, `tests/` and `config.yaml` that no run of the checker would have reported | `../procedures/link-check.py` docstring |
| **E12** | Cut things are not found by searching | Six citations naming a *section title* were stale after the restructure. All six were found by reading | `../milestone-1-core/documentation-review-2026-08-16.md` |
| **E13** | Valid and wrong is a real class | Two paths resolved perfectly by going out to `docs/` and back. Nothing caught them but a human reading the diff, and `cd96c6d` then taught the checker to report the class | `../procedures/link-check.py` |
| **E14** | Check your own claim | The plan asserted one code citation needed no edit, four times across three documents. It was wrong, and it survived a fresh-context review that verified all eleven citations line for line — because that review checked the citations *existed*, not what they would need | `phase-7-docs-restructure/plan.md` |
| **E15** | Write the playbook last | `eae1489` filed the restructure as Phase 7 and wrote the playbook from what it had cost. `IDM-004-reviewing-unexecuted-work.md` cites this rule as the reason it did not exist until a forward review had been run once | `IDM-004-reviewing-unexecuted-work.md` |
| **E16** | Append, do not replace | The 2026-08-16 playbook replaced the generic procedure with its own narrative. Five of the seven decided steps went missing, the harvest among them — the thing `CLAUDE.md` says this pointer exists to protect. Ranked the highest-consequence gap (G1) of a fresh-context documentation review, parked unactioned for three days, and repaired on 2026-08-20 | `../milestone-1-core/documentation-review-2026-08-16.md`, `../backlog.md` |

**One correction the evidence forced, kept because it changes what the repair was.** The review read the
five absent steps as work that had never happened. **All seven were run.** `b6cc74f` froze the archive,
`46c8321` wrote the milestone README, `a3e88bc` and `394d910` harvested into `../reference/`, `5924bcc`
and `5758a55` filled `lessons.md`, `5924bcc` filled `measurements.md`, and `4f67b4a` produced
`../backlog.md` and `../status.md`. They were performed and then not written down — a different defect,
and a smaller one.

## What this playbook cannot claim yet

**It has been run once, and that once was not a normal close.** Milestone 1's close was simultaneously
the creation of `docs/`, so every step was exercised while its own destination was being built. None
has yet been run against a tier that already exists, which is the ordinary case and the one Milestone 2
will be. `E6` is the rule most likely to change shape as a result.

## What this assumes exists

The steps name destinations rather than describing them. A project adopting this tier needs five:
an **archive** of one folder per milestone, frozen once written; a **reference tier**, canonical for
quotation; a **lessons** file; a **measurements** file; and a **status** file and **backlog** file kept
apart.
