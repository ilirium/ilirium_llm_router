# The documentation manual

**This file says where things go.** Read it before creating a document, moving one, or recording a
fact you want to survive the milestone. It is the entry point to `docs/`; `CLAUDE.md` is the entry
point to the code.

Its acceptance test: **somebody who has never read `EPD-004` can file a new document correctly from
this file alone.** If you had to open the archive to place something, that is a defect here — fix
this file rather than remember the answer.

> *Written 2026-08-16 at commit 4 of `docs-restructure-plan.md`, before any file moved. It describes
> the target structure; several directories below arrive over the following commits. This note is
> deleted at commit 15.*

---

## Where does it go?

Start here. Almost every filing question is answered by one of these six rows.

| What you have | Where it goes | The test |
|---|---|---|
| A fact that stays true regardless of which phase found it | `reference/` | Would it still be true if the phase that found it had never happened? |
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
3. **Is it a rule about how the work is done, rather than about the router?** Then it is this file, or
   `CLAUDE.md` if a session would act on it wrongly without being told. See "What earns a place in
   `CLAUDE.md`".
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

**Phase numbers are globally sequential, not per-milestone.** Milestone 2 starts at Phase 7, so
"Phase 3 found four of its five items already built" never becomes ambiguous.

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

`.claude/settings.json` is **tracked** and holds durable project policy: it encodes things like which
command runs the tests and that the formatter is pinned, which is project knowledge.
`.claude/settings.local.json` is untracked, holds machine-specific permission accretions, and is
pruned periodically.

---

## Branches

| Prefix | For |
|---|---|
| `feat/phase-N-<slug>` | a numbered phase; the slug matches its archive folder exactly |
| `docs/<slug>` | documentation work belonging to no phase — EPDs, a milestone's opening |
| `fix/<slug>` | a defect outside a phase |
| `chore/<slug>` | tooling, dependencies, formatter bumps |

**No suffix for planning work: the plan opens the phase branch.** Plan and execution share one branch
and one merge commit, which is what keeps one archive folder mapping to one branch. Planning that
produces no code goes on a `docs/` branch.

The same rule settles what a milestone's opening is: it produces documents and instruments and touches
no source, so it is a `docs/` branch. The closing review *does* touch source, so it is a numbered
`feat/` phase.

**Work belonging to a later phase never goes on an earlier phase's branch, even documentation.** A
`feat/phase-N+1-…` branch may sit holding only an unapproved plan; if the plan is rejected the branch
is deleted, not renamed.

**Merge every phase and feature branch with `--no-ff`**, so the boundary stays visible in the log.

**Where branches are recorded:** `status.md` lists only **in-flight** branches — name, purpose, tree
state, next action. Merged branches are not listed; git already holds that and a hand-maintained list
would drift. **The phase note carries the permanent record**: branch, fork point, and merge commit.
Write the merge commit in when the merge happens — four of Milestone 1's six phase notes still say
"merge back with `--no-ff`" and never recorded what happened.

## The phase template

`phase-N-<slug>/` holds `plan.md`, `notes.md` and `evidence/` with its README.

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

**A Milestone 2 phase note.** `milestone-2-<slug>/phase-7-<slug>/notes.md`, the slug identical to
`feat/phase-7-<slug>`. It opens with the branch and fork point, says whether it was written while
measuring, and closes with a "Verified by" line. Its plan is `plan.md` beside it; the milestone's
`implementation-plan.md` sits one level up. Durable facts it discovers do **not** stay in it — they
are harvested into `reference/` at the close, and the note is frozen.

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
   contact often enough that detail beyond the next phase is waste.
8. **Open the folder and the branch.**

### Closing a milestone

**Not yet written, deliberately.** It is written from what a milestone close actually costs, and this
project's first one — the restructure that produced this file — is still in flight. Committing the
procedure before running it once would be exactly the failure this repository keeps recording: an
instrument published before it was used.

The shape it will take is known: freeze the plan and phase notes, write the milestone README, harvest
durable facts into `reference/`, process lessons into `lessons.md`, numbers into `measurements.md`,
live items into `backlog.md`, and reset `status.md`. It arrives at commit 15 of
`docs-restructure-plan.md`.
