# IDM-006 — Closing a milestone

**In force 2026-08-20.** Moved out of `../README.md`, where it was written on 2026-08-16 — and unlike
`IDM-005-opening-a-milestone.md`, **it did not move unchanged.** It was repaired against a finding that
had been sitting unactioned in `../backlog.md` since the day it was written. What was repaired, and
what that finding was, is at the foot under "What was repaired, and why".

**Read this and work from it rather than improvising.** `CLAUDE.md` singles this pointer out above every
other, and the reason is specific: omitting it costs a whole milestone's worth of harvest. The durable
facts stay in phase notes that nobody opens again, and the next milestone pays to re-derive them.

---

## The nine steps

**Steps 1–7 are `../epd/EPD-004-documentation-structure.md` decision 12**, which is what this playbook
was decided to be. **Steps 8 and 9 are lifted from the version that landed**, because they generalise.

Every one of the nine has been run, once, during Milestone 1's close — the twenty-one commits of
`../milestone-1-core/phase-7-docs-restructure/`, whose `notes.md` records what each one actually cost.
Each step names the commit that ran it, so this is a record of what happened rather than a procedure
somebody hoped would work.

### 1. Freeze the plan and the phase notes — `b6cc74f`

Nothing in the milestone's folder is edited again except its paths. The line that makes this workable
rather than a slogan is `../README.md`'s **"Editing the archive: paths yes, claims no, transcripts
never"** — a path is navigation and may be repointed; a claim records what was believed then and may
not; a captured transcript is evidence and is never touched, even when the command inside it has since
changed. Read that section before the first repoint, not after.

### 2. Write `milestone-N-<slug>/README.md` — `46c8321`

What the milestone set out to prove, what happened, and what it cost. **Write it for the finished shape
of the archive, not the current one** — Milestone 1's was written early, alongside the tier indexes,
and an index listing three of its eventual seven files is worse than one written slightly ahead of the
files it names.

### 3. Harvest the durable facts into `../reference/` — `a3e88bc`, `394d910`

The step the whole close exists for, and the one with the most ways to go wrong. Four rules, all of
them bought:

- **The work is deciding what each file does *not* take.** Expect a first draft to pull in material
  that already has a home; cut it, and leave a table naming where each cut thing lives **and the
  trigger that sends you there**. A pointer that says only that a file exists is not a replacement for
  the section it replaced.
- **Plan the destinations before the extraction, not during it.** This is the one thing the 2026-08-16
  close got wrong in its own prediction. Its plan expected the narrative drag of phase notes to be the
  hard part; it was not. The hard part was **destination collision** — durable facts belonging to files
  that did not exist yet.
- **Move files by repairing each tier's links in the same commit as the move that breaks them.** Only
  the archive waits. A reference document that is wrong for four commits is one nobody can trust while
  the work is still running.
- **Harvest the hardest thing first, as a gate.** Take the single hardest document and pull its durable
  half out before planning the rest; if the durable half will not separate from the process half, the
  plan for the remainder is wrong and you have spent an hour instead of a week. `394d910` is that gate
  passing, on the LM Studio parity table. *This is the weakened form of a step the 2026-08-16 playbook
  stated more strongly; see "What was repaired, and why".*

### 4. Process the lessons into `../reference/lessons.md` — `5924bcc`, `5758a55`

How the project was wrong, and what caught it. Every such episode is recorded as an aside at the bottom
of the phase note that produced it, **which is exactly where it will not be read at the start of the
next milestone.** The phase notes stay frozen; the correction lands here.

**Harvest the closing phase's own lessons too.** `5758a55` added lessons 6 and 7, both learned by the
close itself, after `5924bcc` had already harvested the six phases before it. A close that harvests
only its predecessors loses the most recent thing the project learned.

### 5. Put the numbers into `../reference/measurements.md` — `5924bcc`

One canonical row per number, whatever prose also quotes it. Two commits in Milestone 1's close were
spent on a rule this step now carries: **a number must have a job, and must be able to do it**
(`ad1d5ae`, then `08280ed` deleting one that could not).

### 6. Move the live items into `../backlog.md` — `4f67b4a`

Unscheduled work, **each item with why it is parked** and why the question may be weaker than it looks.
That column is the point of the file: an inventory of items with no reason attached is one nobody can
prune, and every item in it looks equally alive a milestone later.

### 7. Reset `../status.md` — `4f67b4a`

State only — where the project is, what is next. No work items. **Mixing the two is what made
Milestone 1's handoff and its outstanding-work survey overlap**, which is the failure the whole
structure exists to fix.

Sweep for placeholders while doing it. → `IDM-001-git-branching.md`, "Closing out a status placeholder
is part of the merge": the rule covers **any statement of unfinished state**, not only a `Merge commit`
row, and it was followed narrowly once and the defect happened anyway, twice in one phase.

### 8. Repoint everything, then re-check — `b642619`, `da68dc6`, `cd96c6d`

Run `../procedures/link-check.py`, repoint what it reports, **then the citations in `src/`, `tests/`
and config, which it cannot see** — there were eleven of those, and `da68dc6` is the commit that
repointed them.

**Six things will bite here. All six did.**

- **Searching for what moves will not find what gets cut.** A grep for moving paths structurally cannot
  find a citation that names a *section title*. Six of those were stale and were found by reading, not
  grepping.
- **A path can be simultaneously valid and wrong.** A file inside the archive addressing its own sibling
  by going out and back resolves perfectly. `link-check.py` reports this class now — `cd96c6d` is the
  commit that taught it to — and did not when it happened.
- **A name-based rewrite cannot fix a link that broke by depth**, and will confidently make it worse.
  Repoint by depth, and read the diff.
- **Longer paths break the wrap**, and a mechanical reflow will corrupt a list if it is not written to
  respect one. Check the reflow against a list before trusting it.
- **A path inside a code fence may be relative to the repository root**, not to the citing file.
  Rewriting it "correctly" makes the command wrong.
- **Check the claim you are planning against, including when it is your own.** The plan asserted that
  one code citation needed no edit, four times across three documents. It was wrong, and it survived a
  fresh-context review that verified all eleven citations line for line — because that review checked
  that the citations existed, not what they would need.

### 9. Rewrite this playbook, last, from what the close cost — `eae1489`

**Last, and from what it cost rather than from what it seemed like it should be.** A playbook written
before the work is an instrument that has never been run, in a repository whose most reliable lesson is
that plans are wrong on contact.

`IDM-004-reviewing-unexecuted-work.md` cites this rule as the reason it did not exist until a forward
review had actually been run once.

**Append; do not replace.** This step is the one that produced the defect described below — writing
from what it cost is correct, and *substituting* that narrative for the procedure is not. The
distinction is the whole content of "What was repaired, and why".

---

## What the 2026-08-16 restructure cost, and what does not recur

**This section is evidence, not procedure. Do not work from it.**

Milestone 1's close was also the documentation restructure that built `docs/` — twenty-one commits from
a fifteen-task plan. Six of the nine steps the playbook was written with are that restructure's own
narrative: they describe building a structure that now exists, and they cannot happen again. They are
kept in full, verbatim, because the reasoning in them is still the best account of why the structure
looks the way it does.

1. **Write this file's rules first, before anything moves.** Every later step is then checkable
   against something. Doing it fourth in a fifteen-commit plan was right and would have been wrong
   anywhere later. *(`beddfaf`.)*
2. **Run one extraction as a gate before planning the rest.** Take the single hardest document and
   pull its durable half into `reference/`. If the durable half does not separate from the process
   half, the whole split is wrong and you have spent an hour instead of a week. Milestone 1's gate
   passed and the plan survived. *(`394d910`. The generic residue is in step 3 above, weakened: the
   tiers exist now, so a later close cannot learn that the split itself is wrong.)*
3. **Write the tier indexes for the finished shape, not the current one.** An index listing three of
   its eventual seven files is worse than one written slightly early. *(`46c8321`. The residue is in
   step 2 above.)*
4. **Assemble the reference tier.** The work is deciding what each file does *not* take. Expect a
   first draft to pull in material that already has a home; cut it, and leave a table naming where
   each cut thing lives **and the trigger that sends you there**. *(`a3e88bc`. The residue is in
   step 3 above, which is the recurring form of this.)*
5. **Then cut `CLAUDE.md`**, once every destination exists. Not before. *(`d515763`.)*
6. **Split state from inventory** — `status.md` and `backlog.md` — and keep the column that says
   *why each backlog item is parked*. *(`4f67b4a`. Splitting them was one-time; steps 6 and 7 above
   are what recurs.)*

**And one thing that will feel like a rule and is not.** The plan predicted the narrative drag of
phase notes would be the hard part of extraction. It was not; the hard part was **destination
collision** — durable facts belonging to files that did not exist yet. Plan the reference tier before
the extraction, not during it. *(That is now step 3's second rule, generalised from the reference tier
to any destination.)*

---

## What was repaired, and why

The version written on 2026-08-16 replaced the generic procedure with the narrative of the restructure
that produced it. That was faithful to its own last step — *write this playbook, last, from what it
cost* — and it is how the harvest fell out of the document that exists to protect the harvest.

**`../milestone-1-core/documentation-review-2026-08-16.md` found this the same week and ranked it its
highest-consequence gap (G1):**

> The closing playbook is a log of this restructure, not a closing procedure. […] Five of those seven
> steps are absent from the manual. The harvest — the thing `CLAUDE.md` says the pointer exists to
> protect — is not in the playbook at all.

It was parked whole on 2026-08-17, unactioned, in favour of opening Milestone 2. This document is the
repair. Three things were done to it and nothing was deleted:

| | |
|---|---|
| **Restored** | Decision 12's seven steps as the spine, each with the Phase 7 commit that ran it |
| **Lifted** | The two landed steps that generalise — move-and-repair-links-together into step 3, repoint-and-re-check as step 8 — and the six warnings, attached to the steps they warn about rather than pooled at the end |
| **Demoted** | The six one-time steps, kept verbatim above under a heading that says they are evidence |
| **Corrected** | The original called Milestone 1's close *"fifteen commits"*. It was **twenty-one commits from a fifteen-task plan** — the exact number `../README.md`'s own "a task is a unit of work, a commit is a unit of review" rule was adopted from |

**The finding said five of seven steps were absent. It was right about the document and wrong about the
work** — and the difference matters, because it is the reason the repair is a record rather than an
invention. All seven steps *were run*, in Phase 7's own commits, recovered here from `git log`:
`b6cc74f` froze the archive, `46c8321` wrote `milestone-1-core/README.md`, `a3e88bc` and `394d910`
harvested into `reference/`, `5924bcc` and `5758a55` filled `lessons.md`, `5924bcc` filled
`measurements.md`, and `4f67b4a` produced `backlog.md` and `status.md`. The steps were performed and
then not written down.

---

## What this playbook still cannot claim

**It has been run once, and the once was not a normal close.** Milestone 1's close was simultaneously
the creation of `docs/`, so every step above was exercised while its own destination was being built.
None of the eight has yet been run against a tier that already exists, which is the ordinary case and
the one Milestone 2 will be.

Two specific places where that will show:

- **Step 2 has no worked example for a second milestone.** `../milestone-2-corpus/` has no `README.md`.
  Milestone 1's was written alongside the tier indexes, at a moment that will not recur.
- **Step 3's gate is weaker than it was.** Its original strength came from being able to discover that
  the whole split was wrong. That question is settled, so what survives is a sequencing rule.

**When Milestone 2 closes, this document is rewritten from what *that* cost** — appending, not
replacing. The 2026-08-16 version replaced the generic procedure with its own narrative, and that is
the specific mistake this section exists to stop being repeated.
