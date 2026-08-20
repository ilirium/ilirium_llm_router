# IDM-006 — Closing a milestone

**In force 2026-08-20.**

A milestone ends with its knowledge in the wrong place. Everything learned is in plans and phase notes
— documents written to record how the work went, read once, and never opened again. **Closing is the
act of moving that knowledge to where the next milestone will actually look.**

Skipped, it costs the whole milestone's harvest. The facts stay in the notes, the next milestone
re-derives them at full price, and the corrections that were paid for once get paid for again.

Nine steps, in order. The order matters twice: nothing is repointed until everything has a
destination, and the playbook itself is rewritten last.

---

## 1. Freeze the plan and the phase notes

From here they record what was believed at the time and are not revised.

One distinction makes that workable rather than a slogan, and it is not a judgement call:

| | Editable | Why |
|---|---|---|
| A **path** in archived prose | **yes** | A path is navigation, not a claim. Repointing preserves what the document means; leaving it broken degrades it |
| A **claim** in archived prose | **no** | It records what was believed then. Corrections go to the reference tier, which is what other documents cite |
| Anything in a **captured transcript** | **never** | It is evidence. A stale command line inside one is *correct* — it is what was run that day, and rewriting it falsifies the record |

## 2. Write the milestone's README

What it set out to prove, what happened, and what it cost.

**Write it for the finished shape of the archive, not the current one.** An index that lists three of
its eventual seven files is worse than one written slightly ahead of the files it names, because the
first is silently incomplete and the second is visibly early.

## 3. Harvest the durable facts into the reference tier

The step the whole close exists for, and the one with the most ways to go wrong.

- **The work is deciding what each file does *not* take.** A first draft will pull in material that
  already has a home. Cut it, and leave a table naming where each cut thing lives **and the trigger
  that sends you there** — a pointer saying only that a file exists does not replace a section.
- **Plan the destinations before the extraction, not during it.** The hard part is not the narrative
  drag of unpicking a phase note. It is **destination collision**: durable facts that belong to files
  which do not exist yet.
- **Move by repairing each tier's links in the same commit as the move that breaks them.** Only the
  archive waits. A reference document that is wrong for four commits is one nobody can trust while the
  work is still running.
- **Harvest the hardest thing first, as a gate.** Take the single hardest document and pull its durable
  half out before planning the rest. If the durable half will not separate from the process half, the
  plan for the remainder is wrong, and you have spent an hour finding that out instead of a week.

## 4. Process the lessons

Where the project was wrong, and what caught it.

Episodes like these are recorded as asides at the foot of the phase note that produced them, **which is
exactly where they will not be read at the start of the next milestone.** The notes stay frozen; the
lesson lands in the durable file.

**Harvest the closing phase's own lessons too.** A close that harvests only its predecessors drops the
most recent thing the project learned — and the close is usually where the sharpest lessons are, because
it is the first time the whole body of work is read at once.

## 5. Put the numbers in one place

One canonical row per number, whatever prose also quotes it.

**A number must have a job, and must be able to do it.** A figure that no decision depends on is
clutter; a figure that a decision depends on and cannot support is worse, because it will be quoted
forward.

## 6. Move the live items to the backlog

Unscheduled work, **each item with why it is parked** — and, where it applies, why the question may be
weaker than it looks.

That column is the point of the file. An inventory of items with no reason attached is one nobody can
prune, because a milestone later every item in it looks equally alive.

## 7. Reset the status file

State only: where the project is, what is next. **No work items.**

Mixing state and inventory is what makes a handoff and a work survey overlap, each drifting from the
other, each looking authoritative. A backlog item that has migrated into the status file is the first
sign of it recurring.

**Sweep for placeholders while doing it.** Any statement of unfinished state — a table row, a section
marker, a count in prose, a claim of absence — is correct while it is true and becomes a lie the moment
the state changes. Closing them out is part of the close, not tidying afterwards.

## 8. Repoint every citation, then re-check

Run the link checker, repoint what it reports, **then the citations in code, tests and configuration,
which it cannot see.**

**Six things will bite here.**

- **Searching for what moves will not find what gets cut.** A search for moving paths structurally
  cannot find a citation that names a *section title*. Those are found by reading.
- **A path can be simultaneously valid and wrong.** A file addressing its own sibling by going out to
  the parent and back resolves perfectly, and is absurd. Nothing but a reader catches it unless the
  checker is taught to.
- **A name-based rewrite cannot fix a link that broke by depth**, and will confidently make it worse.
  Repoint by depth, and read the diff.
- **Longer paths break the wrap**, and a mechanical reflow will corrupt a numbered list if it is not
  written to respect one. Check the reflow against a list before trusting it.
- **A path inside a code fence may be relative to the repository root**, not to the citing file.
  Rewriting it "correctly" makes the command wrong.
- **Check the claim you are planning against, including when it is your own.** A plan that asserts some
  citation needs no edit will be believed by every later reader, including a fresh reviewer — who will
  verify that the citation *exists* rather than what it would need.

## 9. Rewrite this playbook, last

From what the close actually cost, rather than from what it seemed like it should be. A playbook
written before the work is an instrument that has never been run.

**Append; do not replace.** This is the step most likely to damage the document it improves: writing
from what the close cost is correct, and *substituting* that narrative for the procedure is not. A
close that is also unusual — the first one, or one that builds the structure it is filing into — will
produce a vivid narrative that reads like a procedure and is not one. Keep it, mark it as the record of
that close, and leave the nine steps standing.

---

## What this assumes exists

The steps name destinations rather than describing them, so a project adopting this needs five:

| | |
|---|---|
| An **archive** | One folder per milestone, holding its plans and phase notes, frozen once written |
| A **reference tier** | What is durably true about the subject, canonical for quotation |
| A **lessons** file | How the project has been wrong, and what caught it |
| A **measurements** file | One canonical row per number |
| A **status** file and a **backlog** file | State and inventory, kept apart |
