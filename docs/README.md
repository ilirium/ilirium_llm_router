# The documentation manual

**This file says where things go.** Read it before creating a document, moving one, or recording a
fact you want to survive the milestone. It is the entry point to `docs/`; `CLAUDE.md` is the entry
point to the code.

Its acceptance test: **somebody who has never read `EPD-004` can file a new document correctly from
this file alone.** If you had to open the archive to place something, that is a defect here — fix
this file rather than remember the answer.

---

## Where does it go?

Start here. Almost every filing question is answered by one of these seven rows.

| What you have | Where it goes | The test |
|---|---|---|
| A fact that stays true regardless of which phase found it | `reference/` | Would it still be true if the phase that found it had never happened? |
| A rule about **how the work is done** rather than about the router | `method/` | Would it still be true if the subject of the project changed? |
| A check somebody should be able to run again | `procedures/` | Would you re-run this against a new model, a new release, a new backend? |
| The output of a run, frozen so a claim has something to rest on | `milestone-N-*/phase-N-*/evidence/` | Is it a transcript, a CSV, a captured reply? |
| A raw artefact several documents are derived from | `captures/` | Is it input rather than result? |
| How the work was sequenced, and what was known at the time | `milestone-N-*/` | Is it a plan, a phase note, a record of a decision's ordering? |
| A question written down before it is answered | `epd/` | Is the decision genuinely open? |

And two files at the root of `docs/` that are neither durable nor archived:

| | |
|---|---|
| `status.md` | **State.** Where we stopped, where the project is, what is next. No work items live here |
| `backlog.md` | **Inventory.** Unscheduled work, each item with why it is parked and why the question may be weaker than it looks. No state lives here |
| `prompt.md` | **The next session's opening instruction, and nothing else.** Added 2026-08-17. It names what to read and what to distrust; it must never summarise what those documents say. **It expires when the phase it opens is merged** — check `status.md` before trusting it |

**`prompt.md` is the one file here that is allowed to go stale**, which is why it carries its own
expiry rule. It exists because sessions are cleared deliberately and a fresh one starts cold; it is
*not* a handoff note, and the moment it starts carrying findings rather than pointers it has become the
second copy this structure exists to prevent. **Its paths are written from the repository root**, since
that is where a session starts — so `link-check.py`, which resolves relative to the citing file, does
not check them. They were verified by hand when it was written and must be again when it is rewritten.

**Mixing those two is what made Milestone 1's handoff and its outstanding-work survey overlap** — both
now in that milestone's archive — which is the failure this whole structure exists to fix. A backlog item that has migrated into the status file is the first
sign of it recurring.

### When two answers are defensible

That is the expensive case, because two sessions will answer differently and the fact lands in two
places, one of which later gets updated. Resolve it in this order:

1. **Does it name a backend?** Then it is `reference/backend-<name>.md`, even if it is also about
   configuration or timeouts.
2. **Is it a number?** The number's canonical row is `reference/measurements.md`, whatever prose also
   quotes it. See "Numbers" below.
3. **Is it a rule about how the work is done, rather than about the router?** Then it is `method/` if
   it is a rule with reasoning worth keeping, or **this file** if it is a filing rule — *where does a
   document go* is this file's whole subject. Either way `CLAUDE.md` may restate it, and only if a
   session would act confidently and wrongly without being told; see "What earns a place in
   `CLAUDE.md`". *(This rule named only this file and `CLAUDE.md` until 2026-08-17, when the `method/`
   tier was built.)*
4. **Still ambiguous?** Put it in the *bigger* file and leave a heading. Merging two thin files later
   is one commit; a duplicated fact discovered later costs somebody a day of deciding which copy is
   right.

---

## The tiers

### `reference/` — durable

True regardless of which phase found it, and the tier that survives every milestone. One file per
subject, each with a **nameable trigger**: a moment you would open *it* rather than its neighbour.

`reference/README.md` holds the reading order and says what each file answers. There are **no numeric
prefixes** — these files are cited by name from `src/` docstrings, and a prefix means inserting one
document renumbers the rest and churns citations in code.

**What does not belong here:** anything that needs the phase to be understood. Citing a phase note as
the *provenance* of a measurement is correct and expected; needing its plan, its ordering, or what it
expected versus found means the fact has not finished being extracted.

**The growth rule.** A section becomes its own file when its trigger is nameable **and** it passes
roughly 40 lines. Until then it lives as a section in the nearest file that already has a trigger. The
40 is a judgement, not a measurement — it is roughly where a section stops being findable by grepping
a file you already have open.

### `method/` — how the work is done

Rules about the process rather than about the router: branch naming, harness configuration, which tools
are pinned and why. **The conventions, the status vocabulary and the index are in
`method/IDM-000-about-these-documents.md`** — read it before writing one. Numbered `IDM-NNN-<slug>.md`,
and there is deliberately no `README.md` in the tier: `IDM-000` *is* the index, matching `epd/`.

That is a pointer rather than a summary, for the same reason as `epd/` below.

**The one thing about this tier that belongs here rather than there:** an IDM is **in force**, which is
the exact opposite of an EPD. The two schemes look alike on purpose — `EPD-000` had already solved
indexing and numbering — so the difference in *status* has to be stated rather than inferred.

**The admission test: would the rule still be true if the subject of the project changed?** No IDM
contains a fact about the router; a rule that needs one is not a method rule.

**This tier and this file split cleanly, and the split is what keeps this file's acceptance test
intact.** This file answers *where does a document go*; `method/` answers *how do I name this branch*.
Somebody filing a document never has to open an IDM to file it correctly — which is why the `method/`
row in the table above is load-bearing rather than decoration. `EPD-004` decision 18 declined this tier
on the ground that it would split the manual; the objection is answered in `IDM-000`, with an addendum
in place at the decision.

### `procedures/` — re-runnable

Instruments, not history. A script, or a written procedure a stranger could follow, with its
`README.md` in `procedures/` saying **when each check is worth re-running**. Vendor behaviour expires;
these are how it is re-established.

A procedure document states, in this order: **why it matters, the procedure, what was actually
observed, and an explicit list of what it does *not* answer.** The last section is not optional — it
is what stops the next reader over-reading the result.

**An instrument's output directory follows the instrument, never the archive.** `runs/` stays beside
the thing that writes it and stays gitignored; only the transcripts a milestone's claims rest on are
copied into that phase's `evidence/`. Put it the other way round and the tool writes into a closed
milestone's folder, and the ignore rule stops covering the path it actually writes to.

### `captures/` — raw input

Artefacts that several documents are derived from and that nobody edits. Redact before committing —
see "Evidence and redaction".

### `epd/` — open questions

An **EPD** is a design question written down before it is answered, so that *"we thought about this
and deferred it"* stays distinguishable from *"we never thought about it"*. **The conventions,
the status vocabulary and the index are in `epd/EPD-000-about-these-documents.md`** — read it before
writing one.

That is a pointer rather than a summary on purpose, and it is the rule this file teaches: EPD-000 is
the one home for those conventions, so restating them here would create a second copy to drift.

Two things about EPDs that belong here rather than there:

- **EPDs do not move at a milestone boundary.** They are the *input* to the next milestone, not
  residue of the last one. Numbering never resets — an EPD number is an identity.
- **A decided EPD graduates into `reference/`, per subject** — usually `design-decisions.md`. The EPD
  stays where it is and records that the decision was taken and where it went.

### `milestone-N-<slug>/` — the archive

How the work was sequenced, and what was believed while it was happening. **A phase note is never
edited again.** It is the record of what was known when it was written, including what was later shown
wrong; corrections land in `reference/`, not here.

```
milestone-N-<slug>/
  README.md              what the milestone was, what it proved, the index
  implementation-plan.md  one per milestone — the phases and their "done when"
  closing-notes.md        the handoff, frozen at the boundary
  phase-N-<slug>/
    plan.md
    notes.md
    evidence/
      README.md
```

**One implementation plan per milestone, inside that milestone's folder.** Milestone-root files are
for work spanning phases — the plan itself, and documents like a migration plan that belong to no
single phase.

---

## Naming and numbering

**Number what needs a stable identity to be cited. Do not number what only needs an order.**

| Thing | Scheme |
|---|---|
| EPDs | `EPD-NNN-kebab-title.md`, allocated in order written, never reused, never renumbered |
| Milestones | `milestone-N-<slug>/` |
| Phases | `phase-N-<slug>/`, the slug identical to the branch's |
| Reference documents | no prefix; the order lives in `reference/README.md` |
| Findings and measurements | no ID scheme; one canonical row in `reference/measurements.md`, linked by anchor |

**Phase numbers are globally sequential, not per-milestone.** **Milestone 2 starts at Phase 8**, so
"Phase 3 found four of its five items already built" never becomes ambiguous. *(This said Phase 7
until 2026-08-16, when the documentation restructure took that number as
`milestone-1-core/phase-7-docs-restructure/`.)*

**A phase's folder takes its branch's slug** — which is a rule about branches, so it lives with the
rest of them. → `method/IDM-001-git-branching.md`, "A phase's folder takes its branch's slug": it
carries Phase 7's standing exception and the fact that the check runs **one way only**. *(It was in
this section until 2026-08-17. Filing a branch rule under "Naming and numbering" is half of how this
file and `CLAUDE.md` drifted into disagreeing about seven things.)*

---

## One home per fact

The rule the whole structure serves. Two documents that both answer a question will drift, and drift
between documents that were supposed to agree is this project's demonstrated failure mode.

**Where a fact lives after it has been harvested:**

- The **archive is frozen-primary** — it says what was known at the time and is not edited.
- The **reference tier is canonical-for-quotation** — it is what every other document cites.
- **A correction lands in the reference tier**, carrying a note of what the phase note said.

Without that sentence the first correction after a harvest has two plausible homes, which is exactly
how a wrong figure survived three phases here.

**When you record a finding, sweep the other documents for claims it makes stale.** That sweep is
expected, not optional — it is half of what filing a finding means.

### Editing the archive: paths yes, claims no, transcripts never

"A phase note is never edited again" collides with "no broken links" the first time anything moves.
The distinction that resolves it, and it is not a judgement call:

| | Editable | Why |
|---|---|---|
| A **path** in archived prose | **yes** | A path is navigation, not a claim. Repointing it preserves what the document means; leaving it broken degrades it |
| A **claim** in archived prose | **no** | It records what was believed then. Corrections go to `reference/`, which is what other documents cite |
| Anything in a **captured transcript** | **never** | A `.txt` of what a command printed is evidence. A stale command line inside one is *correct* — it is what was run that day, and rewriting it falsifies the record |

So a link checker's report is a work list for prose and **not** for `evidence/`. If a moved path makes
a transcript unreadable, the fix is a line in that evidence directory's `README.md`, never an edit to
the transcript.

## Numbers

Every number quoted outside the document that measured it gets a row in
`reference/measurements.md`, carrying four things: **when** it was measured, **with what**, **over
which slice**, and **what it is for**.

**A row that cannot fill all four columns is a number that should not be recorded.** Both failure
modes have happened here and both are in `reference/lessons.md`: a number that was correct and
unusable because its slice was missing, and a number that was reproducible and pointless because it
had no job. Withdrawn numbers stay in the register with the reason — deleting one silently is how it
comes back.

## Evidence and redaction

Evidence is cited to something **committed**. `logs/` is gitignored and rotates, so a claim resting on
a session cites a frozen copy under `evidence/` instead.

**`evidence/README.md` says what produced the artefact, what it proves, what was redacted and how, and
whether it can be regenerated.** Without it a frozen file is unreadable three milestones later.

**Redact to stable placeholders, never by blanking.** Map each distinct value to a placeholder in
first-appearance order — `session-01`, `agent-01` — apply the mapping once, and do not record the raw
values. Blanking destroys the finding while protecting nothing extra: which rows shared a
`session_id` was the entire proof that one session reached both backends.

Three practical rules that come with it: redact every identifier family consistently rather than only
the one you were asked about, and say which extra ones you took; check for secrets **separately**,
because identifiers and credentials are different problems and a file with no identifiers may still
carry a token; and state plainly which files you redacted and which you did not, and why.

## What earns a place in `CLAUDE.md`

`CLAUDE.md` is auto-loaded into every session; nothing in `docs/` is. So the split is not "long things
move out".

**The admission test: what every session must hold in its head stays. What you look up when touching
one area moves — with a pointer that names the trigger.** A pointer saying only that a file exists is
not a replacement for a section; it has to say *when to open it*. The sections most at risk are the
ones nobody cites and everybody uses.

A rule belongs in `CLAUDE.md` when a session would act **confidently and wrongly** without it — that
is the whole test. A rule you would look up before acting belongs here instead.

## Where the harness configuration lives

**`method/IDM-002-harness-configuration.md`** holds all of it, and is canonical. **Open it before adding
a permission, before reaching for `/fewer-permission-prompts`, or before deciding that an entry looks
like a fossil.** The allowlist is split the way the documents are — a tracked `.claude/settings.json`
for durable project policy, an untracked `.claude/settings.local.json` for machine accretion, pruned
periodically — and `IDM-002` carries the admission test that decides which is which, the exact-match
`.env` deny and its `.env.example` trap, and why none of it reopens `epd/EPD-004`'s decision 19.

*Both halves now exist. This paragraph said the tracked half was **not yet built** until 2026-08-17,
which Phase 8's Task 9 made false.*

---

## Branches

→ **`method/IDM-001-git-branching.md`** holds all of it, and is canonical. **Open it before naming a
branch, before creating a phase folder, before rejecting a plan, or before recording where a branch
went.** In one line each, so you know whether you need it: four prefixes by kind of work, with
`<prefix>/phase-N-<slug>` as an orthogonal form any of them may take; `--no-ff` **always**; the plan
opens the phase branch; a phase folder takes its branch's slug and the check runs one way only; a
rejected plan is **merged and marked, not deleted**; and `status.md` carries in-flight branches while
the phase note carries the permanent record.

*This section held the rules until 2026-08-17, and `CLAUDE.md` held them too — the two disagreed in
**seven** places, which is the failure this whole structure exists to prevent surviving inside the
structure built to prevent it. `CLAUDE.md` keeps a labelled restatement of the five facts a session
acts on without looking anything up; everything else has exactly one home now.*

## The phase template

`phase-N-<slug>/` holds `plan.md`, `notes.md` and `evidence/` with its README.

### The unit of work inside a plan is a **task**

**Milestone → phase → task.** `milestone-N-<slug>/implementation-plan.md` sequences the phases;
`phase-N-<slug>/plan.md` publishes a numbered task list; `notes.md` records what each task found.

**A task is a unit of work. A commit is a unit of review. They are not the same thing**, and naming
one after the other is a mistake this project made once and measured. Phase 7's plan numbered its
work "commit 1" to "commit 15". Executing it produced **21 commits from 15 units** — one became
three, two became two each, and one had to be inserted as "9a" rather than 10 because renumbering
would have churned citations in three documents. Six of fifteen were not one-to-one **in the naming
scheme's own first use**.

**Each task is committed; a task may take several commits.** Split a task when the commit would
otherwise be hard for a person to review in one sitting — most usefully when it mixes a mechanical
change with a judgement, since that is where a defect hides. Both of Phase 7's worst self-inflicted
bugs, a reflow that corrupted a numbered list and a section duplicated across two commits, lived
inside large diffs that mixed the two.

**Name the task in the commit body**, on its own line before the prose:

```
moved: the instruments into procedures/

Task 7 of phase-8-<slug>/plan.md.

Twenty tracked files moved as renames, the three gitignored paths moved with
plain mv, and .gitignore was updated before the mv rather than after.
```

That line is what makes the review phase's check — *did every phase complete the task list it
published?* — answerable from `git log` instead of by reading two documents against each other.

**Task numbers are per phase and are never renumbered once published.** Insert with a letter (`9a`)
rather than shifting the rest; the plan, the notes and the commit messages all cite them, and the
same reasoning keeps numeric prefixes off this tier's filenames. **A task that produces no commit is
still a task** — Phase 7's memory migration changed only files outside the repository — and its row
says why git cannot show it.

*Adopted 2026-08-16 from Phase 7's experience, and forward-only: Phase 7's own plan and notes keep
the word "commit", because 21 commit messages in the history say "Commit N of …" and renaming the
archive would put it permanently at odds with the history that implements it. `EPD-004` decision
22.*

**A phase is numbered work with its own folder, whatever branch prefix it carried.** The usual case
is a `feat/phase-N-<slug>` branch that changes `src/`. Phase 7 — the documentation restructure — ran
on a `docs/` branch, changed no behaviour, and is still a phase: it had a plan, a fifteen-step
execution, and findings worth keeping. **The test is whether the work is a bounded unit with a plan
and a record, not which prefix its branch used.**

**`evidence/` is omitted when there is nothing to freeze**, and that is correct rather than missing.
Phase 3's instrument is re-runnable and lives in `procedures/`; Phase 7's output is a work list.
Where a phase has no `evidence/`, its `notes.md` says why.

- **`notes.md` carries a "Verified by" line** — what was run, when, and what it produced. Every phase
  here was signed off by driving the real thing; green tests are not a sign-off.
- **`notes.md` states whether it was written while measuring or afterwards.** It changes how far a
  reader should trust the narrative.
- **A phase's first act is to re-derive its own plan** against what is now known. Four of six phases
  in Milestone 1 found their own plan wrong on contact; one of them deleted a whole step by reading a
  frozen CSV first.

## The review phase

**Every milestone closes with a review phase, and it is specified as measurement, not removal.** A
phase chartered to "find and cut bloat" has a built-in success condition and cannot comfortably return
*there was none* — so each suspected defect is written as a claim, paired with the measurement that
would refute it, measured, and only then decided.

**Refusals are first-class outcomes.** Recording that a cut was considered and refused, with the
measurement, is what stops the same cut being re-proposed every milestone by the next person reading
the same surface signal.

The checklist:

| Check |
|---|
| Re-derive every quoted measurement from the frozen artefacts |
| Read all source and tests |
| Drive the software live |
| Reachability — dead code, unused imports, unreachable branches |
| Declared dependencies against actual imports |
| The documents against each other, not only against the code |
| Did every phase complete the task list it published? |
| Close out the `Branch:` lines with their merge commits |
| Record refusals |

Scale it to the milestone. *Reviewed, nothing found, here is the evidence* is a legitimate outcome; a
phase that must produce findings will manufacture them.

**The review comes before the close**, not after. Harvesting facts into a permanent home requires
first knowing which facts are true — run it the other way round and the durable tier canonises
whatever was wrong.

---

## Worked examples

Three documents that do not exist yet, filed using only this file.

**A Milestone 2 phase note.** `milestone-2-corpus/phase-9-<slug>/notes.md`, the slug identical to
its branch's — whatever prefix that branch carries. It opens with the branch and fork point, says
whether it was written while measuring, and closes with a "Verified by" line. Its plan is `plan.md`
beside it; the milestone's `implementation-plan.md` sits one level up. Durable facts it discovers do
**not** stay in it — they are harvested into `reference/` at the close, and the note is frozen.

*(This example was wrong in three ways until 2026-08-17. It said `milestone-2-<slug>/`, which is
concretely `milestone-2-corpus/`; it named the branch `feat/phase-7-<slug>`, which the orthogonality
rule makes an over-specification; and it told a filer to create a **second Phase 7**, contradicting
"Naming and numbering" above, which says Milestone 2 starts at Phase 8 because 7 is taken. Phase 9 is
used here because it does not exist yet, which keeps this a worked example rather than a description
of something real.)*

**A new re-runnable check** — say, a probe for a second local backend. The script and its README go to
`procedures/<name>/`, its `runs/` stays beside it and gitignored, and `procedures/README.md` gains a
row saying when it is worth re-running. Its *results* are frozen in the phase's `evidence/`, not in
`procedures/`. If it establishes durable facts about a backend, those go to
`reference/backend-<name>.md` and its numbers to `measurements.md`.

**A finding that contradicts something already written.** The measurement goes in the phase note that
made it. The **correction** goes to the reference file that owns the fact, and the number's row in
`measurements.md` is updated with a note of what it said before. The phase note that was wrong is
**not edited** — it recorded what was believed then. Then sweep for other documents quoting the old
claim; that sweep is part of the job.

---

## Playbooks

Read the relevant one and work from it. These are last in this file because they are used twice a year
while the filing rules above are used every week.

### Opening a milestone

Mined from Milestone 1's opening rather than invented. In order:

1. **Name the falsifiable central claim, and the non-goals.** Milestone 1's was "no protocol
   translation is needed, and a local model can drive a real coding session" — a sentence that could
   have come out false.
2. **Run the cheapest experiment that could refute it**, before specifying anything.
3. **Capture the real input.** This is the highest-leverage step and it is easy to skip. Milestone 1
   captured 118 KB of actual request bytes on day one; it turned up three body fields nobody had
   anticipated, and a full-body parse would have silently dropped all three. The capture did not
   inform the architecture, it **changed** it. Everything else at that stage was reasoning; this was
   the only step able to contradict the reasoning.
4. **Spike whatever the architecture depends on**, filing each spike straight into `procedures/` or
   `captures/` so it is re-runnable rather than a memory.
5. **Settle the expensive-to-reverse questions as EPD forks**, and answer them explicitly.
6. **Write the spec, marking every statement measured / inferred / assumed**, and give each assumption
   the cheap check that would settle it. Milestone 1's spec was reliable where it recorded measurements
   and unreliable where it recorded predictions, with both in the same prose — several predictions
   were an hour's work to test and stood for five phases.
7. **Write `implementation-plan.md` at decreasing resolution** — the next phase in full, the one after
   in outline, the rest as a title and the question it exists to close. Plans here are wrong on
   contact often enough that detail beyond the next phase is waste. The phase written in full gets a
   numbered **task list** in its own `plan.md`; see "The unit of work inside a plan is a task".
8. **Open the folder and the branch.**

### Closing a milestone

**Written 2026-08-16, from running it once.** Milestone 1's close is
`milestone-1-core/phase-7-docs-restructure/` — fifteen commits, and its `notes.md` records what each
one actually cost. The order below is the order that worked; the warnings are things that went wrong.

1. **Write this file's rules first, before anything moves.** Every later step is then checkable
   against something. Doing it fourth in a fifteen-commit plan was right and would have been wrong
   anywhere later.
2. **Run one extraction as a gate before planning the rest.** Take the single hardest document and
   pull its durable half into `reference/`. If the durable half does not separate from the process
   half, the whole split is wrong and you have spent an hour instead of a week. Milestone 1's gate
   passed and the plan survived.
3. **Write the tier indexes for the finished shape, not the current one.** An index listing three of
   its eventual seven files is worse than one written slightly early.
4. **Assemble the reference tier.** The work is deciding what each file does *not* take. Expect a
   first draft to pull in material that already has a home; cut it, and leave a table naming where
   each cut thing lives **and the trigger that sends you there**.
5. **Move the files, repairing each tier's links in the same commit as the move that breaks them.**
   Only the archive waits. A reference document that is wrong for four commits is one nobody can
   trust while the work runs.
6. **Then cut `CLAUDE.md`**, once every destination exists. Not before.
7. **Split state from inventory** — `status.md` and `backlog.md` — and keep the column that says
   *why each backlog item is parked*.
8. **Repoint everything the link checker reports**, then the citations in `src/`, `tests/` and config,
   which the checker cannot see.
9. **Write this playbook**, last, from what it cost.

**Six things that will bite, all of which did:**

- **Searching for what moves will not find what gets cut.** A grep for moving paths structurally
  cannot find a citation that names a *section title*. Six of those were stale and were found by
  reading, not grepping.
- **A path can be simultaneously valid and wrong.** A file inside the archive addressing its own
  sibling by going out and back resolves perfectly. `procedures/link-check.py` now reports this class;
  it did not when it happened.
- **A name-based rewrite cannot fix a link that broke by depth**, and will confidently make it worse.
  Repoint by depth, and read the diff.
- **Longer paths break the wrap**, and a mechanical reflow will corrupt a list if it is not written to
  respect one. Check the reflow against a list before trusting it.
- **A path inside a code fence may be relative to the repository root**, not to the citing file.
  Rewriting it "correctly" makes the command wrong.
- **Check the claim you are planning against, including when it is your own.** The plan asserted that
  one code citation needed no edit, four times across three documents. It was wrong, and it survived a
  fresh-context review that verified all eleven citations line for line — because that review checked
  the citations existed, not what they would need.

**And one thing that will feel like a rule and is not.** The plan predicted the narrative drag of
phase notes would be the hard part of extraction. It was not; the hard part was **destination
collision** — durable facts belonging to files that did not exist yet. Plan the reference tier before
the extraction, not during it.
