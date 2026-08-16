# EPD-004 — Documentation structure at the milestone boundary

**Status: decided 2026-08-15 by the repository owner, extended 2026-08-16. Nothing has been moved
yet.** Written the same day as a proposal; all six forks were answered, and the outcomes are
recorded under "Decisions taken" below, each beside the reasoning it overrode or confirmed. The
mechanical half — which file goes where, and everything that breaks when it does — is in
`docs/docs-restructure-plan.md`.

**A second round of decisions was taken on 2026-08-16**, from a discussion that ranged well past this
document's original subject — into the session memory store, the permission allowlist, branch naming,
and how a milestone is opened and closed. Two of them **revise decisions recorded here as taken**:
the reference tier grows to seven files, and `Anthropic model IDs` now leaves `CLAUDE.md` rather than
staying. Both are corrected in place above and recorded under "Decisions taken, 2026-08-16", in the
same visible style this document already uses for its own errors. **A decided document that quietly
changes its decisions is worth less than one that shows where it moved.**

**Where this decision graduates to.** `EPD-000` says a decided EPD graduates into `CLAUDE.md` under
"Design decisions". This one does not: its subject is how the documents are organised, so it
graduates into **`docs/README.md`**, the documentation manual that decision 8 creates. That manual is
the durable form of this document; what stays here is the argument and the measurements. `EPD-000`'s
vocabulary needs a small extension to cover it, recorded under "One EPD-000 convention this changes".

This is the first EPD whose subject is the repository rather than the router. `EPD-000` does not
restrict the series to the product, and the format fits: a question written up before it is
answered, with the forks left open.

**Reviewed 2026-08-15 against the tree, and revised.** The review found one wrong count, one
self-contradiction, a class of citation this document had not looked for, and a gate that would have
passed without testing what it claimed to test. All are corrected below **in place and visibly** —
each correction says what the first version said — because a proposal arguing that this repository
quotes numbers forward without checking them cannot quietly fix its own. The `CLAUDE.md` cut, which
was asserted from the file's size alone, is now measured; the measurement changed two rows of the
triage table and opened fork 5.

## Why now

Milestone 1 is done. Six phases, 65 files under `docs/`, and a `CLAUDE.md` of 337 lines that is
loaded into every session whether or not the session touches any of it. The next chunk of work —
Milestone 2 — starts from three EPDs and a handful of loose ends, none of which needs to know how
Phase 3 chose its timeout.

The trigger is not tidiness. It is that **the documents no longer distinguish what is true from how
it was found out**, and after six phases those are different sizes. `phase-4-notes.md` holds the
measured LM Studio parity table, which you need on day one of Milestone 2, in the same file as the
account of which probe was run in which order, which you will never need again. Filed whole into an
archive, the durable half goes with it.

This repository has a documented habit of exactly that failure. Phase 5 found work already
*misdescribed* — claims written once and quoted forward across four documents. Phase 6 found the 26×
time-to-first-byte figure quoted without the slice it means, which made the obvious recomputation
disagree with the documentation by a factor of seven. **A structure that gives every durable fact
exactly one home is the structural form of the fix those two phases applied by hand.**

## Documented versus measured

Per `EPD-000`'s convention, what in this proposal was counted against the tree and what is judgement.

| Claim | Confidence |
|---|---|
| 65 files under `docs/`, 50 of them tracked, before this EPD was committed; 67 / 52 after | **Measured** — `git ls-files docs`, `git ls-tree -r 9dd907e`, `find` |
| `CLAUDE.md` is 337 lines / 46725 bytes, loaded every session | **Measured** |
| ~~253 mentions of the 22 documents and directories that would move~~ | **Withdrawn 2026-08-16** — it did not reproduce, no recipe was recorded, and on examination it had no job. See "The number that was withdrawn" below |
| 11 doc citations from 7 code and config files — 8 naming a `docs/` path, 3 naming a `CLAUDE.md` section | **Measured** — `config.py:62`, `proxy.py:3,238,321`, `stats.py:3,26`, `observe.py:12`, `tests/test_observe.py:9`, `config.yaml:24,30,44` |
| 4 `.gitignore` entries name `docs/` paths, one of them a negation | **Measured** — `.gitignore:229,231,233,237` |
| `probe.py` breaks silently if its directory changes depth | **Measured** — `ROOT = HERE.parent.parent` at `probe.py:40`, used to locate the capture and `logs/calls.csv` |
| `router.yaml` writes its runs by a path relative to itself, so a move relocates them out of the ignore rule | **Measured** — `router.yaml:28,33` |
| Six `CLAUDE.md` sections have never been cited by name in Milestone 1; "Design decisions" has been cited 8 times | **Measured** — see the section below |
| Moving reference material out of `CLAUDE.md` costs a session the knowledge unless a pointer replaces it | **Inferred strongly** — `CLAUDE.md` is auto-loaded, nothing else in `docs/` is |
| The proposed split makes future quoting-forward errors less likely | **Unmeasured hypothesis** — it is the reason for the shape, and it is not testable in advance |

**The first row was wrong in this document's first version**, which claimed 68 files. Corrected in
place and left visible: an EPD whose argument rests on this repository's habit of quoting numbers
forward should not quietly fix one of its own.

**Two rows below it also need their slice, added 2026-08-16.** The file counts are measured *at
`51b857b`* and are already stale as current state — `de4e28a` added a file, so the tree holds 68 / 53
today. The citation row's per-section counts are corrected under "Which `CLAUDE.md` sections" below.

### The number that was withdrawn

**"253 mentions" was removed on 2026-08-16 after a fresh-context review could not reproduce it.**
Counting over the stated scope at `51b857b` gives 340 occurrences, 301 line-hits, ~261 excluding the
two restructure documents, or 199 restricted to `docs/*.md`, depending on whether prose references
and fenced paths count. **No recipe was recorded**, which is the failure this document warns about in
its own citation measurement.

But the more useful finding is that **re-deriving it would have been the wrong fix, because the
number had no job.** It was given two and can do neither:

- **Sizing the work.** Already carried by facts that do not need it — 68 files, 22 moving, 15
  commits, eight breakages. The count was decorative precision on a settled conclusion.
- **The commit 13 work list.** Wrong population in both directions. It **overcounts**, because a
  prose mention of "Phase 4" breaks nothing. It **undercounts**, because
  `phase-4-evidence/README.md:4` cites `../../CLAUDE.md` and needs `../../../../` — the filename
  never changes, so no grep for moving names can find it. `docs-restructure-plan.md` says exactly
  this when it calls the link checker "the only practical check for links that break by *depth*
  rather than by name."

So the plan already knew why a mention count cannot size this job, in the same document that used a
mention count to size it. **This is a different failure from the 26× episode:** that number was
correct and quoted without its slice; this one was a number measured because it was measurable, then
assigned jobs by proximity.

**What replaces it.** Nothing, for sizing. For the work list, the link checker's output — precisely
defined, produced by a tool the plan already mandates, and directly actionable. If a magnitude is
ever wanted, the useful unit is **files, not hits**: you edit files, and a file count barely moves
when the definition of "a mention" changes, while the hit count swings by tens.

Two things the repository *should* keep tracking, and does: the **11 code and config citations**,
because they rot silently, nothing tests them, and a markdown link checker cannot see inside a Python
docstring — they are the chain from a rule in code back to the measurement that established it. And
**broken links after the move**, via the checker. Re-checking the 11 is a standing item for the
review phase (decision 11), not a number to maintain.

## The central claim: this is a split, not a move

The natural reading of "archive Milestone 1" is to move its documents into a folder. That is right
for two of the four kinds of document here and wrong for the other two.

| Kind | Examples | Where it belongs |
|---|---|---|
| **Durable reference** — true regardless of which phase found it | the parity table, the CSV column spec, the credential modes, the design decisions | stays at the top, in `docs/reference/` |
| **Process and state** — how the work was sequenced | plans, phase notes, `handoff.md`, `outstanding-work.md` | archived under the milestone |
| **Evidence** — frozen artefacts a claim rests on | the step 6 session, the probe transcripts, `phase-4-evidence/` | archived beside the phase that produced it |
| **Instruments** — committed to be run again | `probe.py`, `dying_backend.py`, `lmstudio-usage-check.md`, the Claude Code test procedure | stays at the top, in `docs/procedures/` |

Two consequences that the folder-move reading gets wrong.

**The EPDs do not move.** They are the *input* to Milestone 2, not residue of Milestone 1. Filing
`EPD-002` under `milestone-1-core/` would say the opposite of what is true about it. `docs/epd/`
stays where it is, and its numbering never resets per milestone — an EPD number is an identity, and
`EPD-002` must keep meaning the same document after Milestone 4.

**Some small documents are tools, not history.** `lmstudio-usage-check.md` says in its own opening
that the procedure is written down "so it can be re-run against a different model or a newer
LM Studio", and `observe.py:12` cites it as the authority for the scanner's rule.
`phase-4-probes/` is described in `handoff.md` as "committed and meant to be re-run".
`phase-3-verification/dying_backend.py` is a reusable stub backend. Filed under
`milestone-1-core/phase-N/`, a tool acquires the appearance of a transcript, and the next person
re-derives it. They go to `docs/procedures/`; their *results* stay frozen with the phase.

## The proposed structure

```
README.md                    the front door — what it is, quick start, the original brief
CLAUDE.md                    ~100 lines: how to work in this repo, and the map
docs/
  README.md                  THE MANUAL — what each tier is for, what goes where, how to
                             decide, and how to open a milestone. The entry point to docs/
  status.md                  where the project is: done, in progress, next. No backlog
  backlog.md                 the pool of unscheduled work, each item with why it is parked
  reference/                 durable. Survives every milestone
    README.md                the reading order and what each file answers
    architecture.md          dispatch not translation; why the router exists. Opens with
                             the request shape and the Anthropic surface as sections
    design-decisions.md      the whole decisions section, statements and reasoning together
    observability.md         the CSV columns and the recorder's constraints
    backend-lmstudio.md      the measured parity table, context and window facts
    backend-anthropic.md     model IDs and the rejections, OAuth forwarding, the 429 shape
    measurements.md          every number the docs quote, with its date and its slice
    lessons.md               how this project has been wrong, and what caught it
  procedures/                re-runnable. How to check something again
    README.md                the index of checks, and when each is worth re-running
    lmstudio-usage-check.md
    lmstudio-capability-probes/    (was phase-4-probes/)
    testing-against-claude-code.md
    anthropic-auth-check.md
    read-timeout-semantics.py      (was phase-5-measurements/)
    dying-backend/                 (was phase-3-verification/, without runs/)
  captures/                  raw artefacts the reference docs are derived from
    log-the-whole-request.txt
  epd/                       open proposals — unchanged, milestone-independent
  milestone-1-core/          the archive: how Milestone 1 was built
    README.md                what it was, what it proved, the index
    closing-notes.md         (was handoff.md, frozen at the boundary)
    implementation-plan.md
    outstanding-work.md      the survey, archived; its live items became backlog.md
    docs-restructure-plan.md
    phase-1-proxy/                 notes.md, evidence/
    phase-2-observability/         notes.md, evidence/
    phase-3-failure-handling/      notes.md, evidence/
    phase-4-lmstudio-parity/       notes.md, plan.md, evidence/
    phase-5-config-and-timeouts/
    phase-6-review-and-cleanup/    every slug matches its branch (decision 15)
```

**Deferred, each with its reason** (decision 7): `configuration.md` — its material is credential
modes, which are a design decision, and timeouts, which belong to `backend-lmstudio.md`; it has no
source of its own. `request-shape.md` — 12 lines, starting as a section of `architecture.md`, and
kept there deliberately, because that is what keeps `proxy.py:3` needing no edit at all. Each becomes
a file when it has a nameable trigger *and* passes roughly 40 lines.

**`backend-anthropic.md` was on that list until 2026-08-16 and is now a file** — see the fork 6
revision below. At 13 lines it still fails the size test; the 40-line rule did not decide it and
symmetry did.

`milestone-2-*/` is created when Milestone 2 starts, with the same internal shape. That repetition is
the point: the archive layout is a template, so the second milestone costs no design.

### Two files in `reference/` that do not exist today

**`measurements.md`.** One table of every number these documents quote, each row carrying the date,
the instrument, and — the part that matters — **the exact slice the number describes**. Phase 6's
single most consequential finding was the 26× gap quoted for three phases without the slice, where
recomputing over the whole file gives 3.9×. Both figures are right; they answer different questions.
The prose fix was to write the recipe down once. The structural fix is to give every quoted number
one canonical row, so quoting forward means linking rather than restating.

**Which copy is canonical, added 2026-08-16.** Both of these files *harvest* material that also stays
in the phase notes, so the restructure creates the duplication it exists to prevent unless the
relationship is named. It is: **the archive is frozen-primary, and the harvest is
canonical-for-quotation.** A phase note is never edited again — it records what was known when it was
written. `measurements.md` and `lessons.md` are what any *other* document cites, and a correction is
applied there, carrying a note of what the phase note said. Without this sentence the first
correction after the restructure has two plausible homes, and that is exactly how the 26× figure
survived three phases.

**`lessons.md`.** Four times in six phases, a phase found its own premise wrong: Phase 3 found four
of five items already built, Phase 4 found a third of its plan already measured, Phase 5 found work
already misdescribed, and Phase 6 found its own review plan asserting something a five-minute
measurement refuted. That pattern, and the habits that caught it — grep the frozen artefacts before
planning a run; check the claim you are planning against, including when it is your own — is
arguably the most valuable thing Milestone 1 produced. It currently exists only as asides at the
bottom of six separate phase notes, which is precisely where it will not be read at the start of
Milestone 2.

## Which `CLAUDE.md` sections Milestone 1 actually consulted — measured 2026-08-15

The first version of this document proposed cutting `CLAUDE.md` from 337 lines to ~100 on the sole
grounds that it is 337 lines and auto-loaded. That is a restatement of the file's size, not evidence
of harm — and this repository has a precedent that makes the omission pointed. Phase 6 faced the
structurally identical claim about the source's 58% comment density, **measured** the overlap at a
mean 2.8%, and refused the cut. That episode is one of the two process lessons this proposal wants
to preserve in `reference/lessons.md`. Proposing an unmeasured cut in the same document was the same
mistake in a new place.

So it was measured. Every reference to `CLAUDE.md` across `docs/`, `src/`, `tests/` and `README.md`
was extracted and classified by which section it names. Replay transcripts were excluded — they
contain the captured system prompt, not a citation.

| Section | Lines | Cited by name | In how many files |
|---|---|---|---|
| Design decisions | 179–236 | **8** | 6 — including 3 of the 4 EPDs |
| Observability: log + CSV stats | 251–312 | **5** *(first written as 4)* | 4 — including `stats.py:3` |
| Observed request shape | 167–178 | **4** *(first written as 3)* | 3 — including `proxy.py:3` |
| Goal | 100–105 | 1 | 1 |
| The central architectural problem | 106–166 | **0** *(first written as 1)* | 0 |
| **Status** | **5–63** | **0** | 0 |
| **Layout and commands** | 64–99 | **0** | 0 |
| **Anthropic model IDs** | 313–325 | **0** | 0 |
| **Open proposals — the EPDs** | 237–250 | **0** | 0 |
| **Stack decisions**, **Style** | 326–337 | **0** | 0 |

**The result does not say what a first reading suggests, and the caveat is the finding.** A citation
counts a section used as an *authority* — something a document argues with, defers to, or records a
correction against. It cannot count a section used as a *lookup table*. Nobody writes "as `CLAUDE.md`
'Layout and commands' states" before running `make test`; nobody cites "Anthropic model IDs" before
typing `claude-sonnet-5`. Those two sections are almost certainly the most *used* in the file and
score zero.

So the measurement splits `CLAUDE.md` in a way the original triage did not:

- **Cited sections** — Design decisions, Observability, Observed request shape. Heavily consulted,
  and always *from a document*. A reader already going elsewhere can follow one more link, so these
  are the sections a pointer genuinely replaces.
- **Silently-used sections** — Layout and commands, Anthropic model IDs. Zero citations, constant
  use, and no link can be followed by someone who does not know they need it. **These must stay.**
  *Half of this was overridden on 2026-08-16: `Anthropic model IDs` leaves after all, because it also
  has a natural home in `backend-anthropic.md` and keeping both copies is worse than the risk of the
  pointer being missed. `Layout and commands` stays, and the argument still holds for it — it has no
  destination that would want it.*
- **Genuinely inert** — Status, at 59 lines and 11038 bytes, with **zero** citations in six phases.
  Stack decisions and Style, 12 lines, likewise.

**Three corrections to this section, made 2026-08-16 after a fresh-context review re-derived it.**

**Status is not "the single largest section in the file"**, which is what this document said. It is
*third* by lines — Observability is 62 and The central architectural problem 61 — and largest only
by **bytes** (11038 against Observability's 10877). The original sentence gave a line figure and a
superlative that holds only for bytes, and paired it with "18%", which is the line-based share; by
bytes it is 23.6%. Two units in one sentence, and the claim was false for the one it named.

**Two counts in the table were low and one was high**, corrected in place above. `EPD-003:396` names
Design decisions *and* Observability on the same line and had been counted only for the first, which
is what made 8 and 4 inconsistent under one rule. And "The central architectural problem" scores
**zero**, not one: the only near-hit is `EPD-002:258` quoting the subtitle *"dispatch, not
translation"* rather than the section title, which the recipe excludes.

**None of it changes the argument**, and that is worth saying rather than leaving implied: every
**zero** row reproduces exactly, and the zero rows are what the triage turns on. `Status` remains the
clearest case for cutting — 17.5% of an auto-loaded file by lines, 23.6% by bytes, never once cited
as an authority, and almost entirely Milestone 1 phase history. The triage table below already
proposed moving it, for the weaker reason that it was long.

Two results argue *against* parts of the original triage. **"Design decisions" is the most-cited
section in the file, and three of the four EPDs cite it** — the EPDs are precisely the documents that
argue *against* a decision, and what they need is the rationale, not the one-line statement. Cutting
rationale from the section most used for argument is the riskiest single item in this proposal.
And **"Layout and commands" scoring zero is evidence of nothing**, which is worth stating plainly so
the number is not later quoted as though it were.

The recipe, so this number is never quoted without its slice: *citations naming a section title in
quotes, across `docs/`, `src/`, `tests/` and `README.md`, excluding `CLAUDE.md` itself, this
document, `docs-restructure-plan.md`, and the three files containing replayed request captures.*

## What leaves `CLAUDE.md`, and the rule for deciding

`CLAUDE.md` is auto-loaded; nothing in `docs/` is. So the split cannot be "long things move out".
Anything moved is knowledge a session no longer has by default, and the one-line pointer that
replaces it is load-bearing — it has to name *when to open the file*, not merely that it exists.

**The rule: what every session must hold in its head stays. What you look up when touching one area
moves, with a pointer that names the trigger.**

| Section, today | Lines | Cited | Proposal |
|---|---|---|---|
| Status | 5–63 | 0 | **Leaves**, and the measurement makes this the clearest case in the table. A three-line summary in `CLAUDE.md`, the board in `docs/status.md`, the detail in the milestone archive |
| Layout and commands | 64–99 | 0 | **Stays** — silently used, not citable. Every session needs it, including the ruff pin and why it is pinned |
| Goal | 100–105 | 1 | **Stays**, compressed to three lines; the long form is `reference/architecture.md` |
| The central architectural problem | 106–166 | 1 | **Leaves** to `reference/architecture.md` and `reference/backend-lmstudio.md`. A four-line summary stays: no translation, dispatch on the model name, relay bytes |
| Observed request shape | 167–178 | 3 | **Leaves** to `reference/request-shape.md`. Repoint `proxy.py:3` |
| Design decisions | 179–236 | **8** | **Leaves whole** (decision on fork 5). All 58 lines become `reference/design-decisions.md`, statements and reasoning together, readable front to back. `CLAUDE.md` keeps a **titles-only table of contents** plus "read the file before reversing any of these" — an index, not a summary, so there is nothing to drift. Repoint `proxy.py:238` |
| Open proposals — the EPDs | 237–250 | 0 | **Stays**, cut to the table plus "do not build from one" |
| Observability: log + CSV stats | 251–312 | 4 | **Leaves** to `reference/observability.md`. A pointer stays, triggered on "touching the recorder". Repoint `stats.py:3` |
| Anthropic model IDs | 313–325 | 0 | **Leaves** to `reference/backend-anthropic.md`, decided 2026-08-16. **This document said "Stays"**, on the silently-used argument below. Overridden: the alternative was the same table in two files, and a duplicated fact is the failure this restructure exists to prevent. Mitigated by a pointer naming the trigger — *before naming an Anthropic model, read this file* — which turns a silently-used section into a cited one |
| Stack decisions, Style | 326–337 | 0 | **Stays.** 12 lines; not worth a link |

Target: roughly 100 lines — about 80 of surviving sections, plus a three-line status summary, a
four-line architecture summary, two pointers, and the twelve-line table of contents for the
decisions.

**Revised 2026-08-16, and the revision is about what that number *is*.** The target is a **result,
not a budget**. Every line earns its place by passing the admission test below, and the length is
whatever that leaves. Stated as a budget, it invites the next session to trim a load-bearing line to
reach a round number.

**The admission test, which this document had been applying without stating:** *if this were missing,
would a session do something wrong without knowing to look it up?* **Yes** — it stays. **It would
only be slower** — a pointer. **Neither** — it leaves with nothing left behind.

That test is also what the citation measurement above cannot see, and why `Layout and commands`
survives scoring zero: the ruff pin prevents a confident wrong action, and its success is silent.
Nothing cites it and nothing ever will.

Three things now push the length the other way and are accepted — the branch convention, the two
milestone playbook pointers, and **seven** rules migrating in from the session memory store
(decisions 14, 12 and 16). `Anthropic model IDs` leaving offsets part of it. And the surviving sections are to be
rewritten **as rules rather than as history**: the ruff pin currently spends five paragraphs of
narrative to state one rule and one trap, which in an auto-loaded file is four paragraphs of rent.
The narrative is not lost — it is `reference/lessons.md` material.

The risk to state plainly is that this trades **certainty** for **size** — today every fact is
guaranteed present; afterwards some facts depend on a pointer being followed. The measurement locates
that risk precisely: it is not spread across the file but concentrated in **Design decisions**, the
one section used as an authority by the documents whose whole purpose is to argue with it.

**The fork 5 decision accepts that risk deliberately**, and mitigates it with the titles-only table
of contents rather than by keeping the section. The bet is that a session which can see *that* a
decision exists will open the file before reversing it, and that a decisions document worth reading
front to back is worth more than one guaranteed to be in context but never read as a whole. It is a
bet, not a measurement, and it is the one place this restructure could make things worse.

**Its trip-wire, added 2026-08-16**, because a risk this document calls its worst had no way to be
noticed failing — decision 10 names one and this did not. **The signal is a design decision reversed,
narrowed or contradicted without `reference/design-decisions.md` appearing in the reasoning.** The
byte-relay rule and the no-special-case-for-background-traffic rule are the two most likely, both
because they cost something visible and their rationale is a paragraph away. If that happens once,
the titles-only table of contents was too thin and the statements belong back in `CLAUDE.md`. This is
a standing item for the review phase (decision 11), not a one-off check at commit 14.

## Numbering

The question is worth separating into two, because they have different answers.

**Number what needs a stable identity to be cited. Do not number what only needs an order.**

| Thing | Scheme | Why |
|---|---|---|
| EPDs | `EPD-NNN-kebab-title.md`, allocated in order written, never reused, never renumbered across milestones | Already the convention, already works, and they are cited by bare number 76 times across the repo |
| Milestones | `milestone-N-slug/` | Cited in conversation as "Milestone 1"; the slug says what it was |
| Phases | `phase-N-slug/` inside a milestone | Same. `phase-4-lmstudio-parity/` reads better than `phase-4/` and costs nothing |
| Reference docs | **no numeric prefix**; `reference/README.md` sets the reading order | They are cited by name from `src/` docstrings. A numeric prefix means inserting a seventh document renumbers the rest and churns citations in code, for an ordering that an index gives for free |
| Findings and measurements | **no ID scheme**; one canonical row in `reference/measurements.md`, linked by anchor | See the fork below |

If numeric prefixes on reference docs are wanted anyway, number **in tens** (`10-architecture.md`,
`20-design-decisions.md`) so an insertion does not renumber anything. That is the mitigation, not a
recommendation.

**Phase numbers stay globally sequential, not per-milestone.** Milestone 2 starts at Phase 7. The
alternative — restarting at Phase 1 inside each milestone — makes "Phase 3 found four of its five
items already built" ambiguous forever, and that sentence appears in five documents.

## Decisions taken, 2026-08-15

All six forks answered by the repository owner, plus two additions. Forks 5 and 6 were opened the
same day, after a review found the first four attached to the least consequential questions in the
document. The original reasoning is kept below each decision, including where it was overridden.

**Gate — accepted.** The four-tier split stands, so the rest of this document applies.

**Decision on fork 4 — `docs/captures/`.** The alternative, `reference/captures/`, is dropped.

**Decision on numbering — no prefixes on reference documents.** Order lives in
`reference/README.md`. The identity-versus-order rule below is adopted as written.

### Decision on fork 5 — `Design decisions` moves out whole

**Overrides this document's recommendation**, which was to keep the section in `CLAUDE.md` because
the measurement showed it was the most-cited section in the file. The owner's reason is better than
the objection: the decisions are worth reading *as a document*, front to back, and they cannot be
while they are one section of an auto-loaded reference file nobody reads linearly.

So `reference/design-decisions.md` holds the section entire — every statement with the reasoning and
the measurement that produced it, in the order they were taken.

**What stays in `CLAUDE.md` is a table of contents: the decision titles only, and one line saying
that reversing any of them means reading the file first.** This is deliberately not a summary. A
one-line restatement of a decision *is* duplication and would drift; a list of titles is an index and
cannot. It preserves the property the measurement was worried about — a session knows which
decisions exist and that it must not quietly reverse one — at no risk of two copies disagreeing.

The consequence for `EPD-000` is real and is recorded below: an accepted EPD now graduates into
`reference/design-decisions.md`, not into `CLAUDE.md`.

### Decision on fork 3 — split, with the backlog in its own file

`outstanding-work.md` is archived as the survey it is. Its live items move out — **but to
`docs/backlog.md`, not into `status.md`.**

The owner's distinction, and it is the right one: **status is state, backlog is inventory.** A status
file that carries the work items themselves stops being readable at a glance, which is the only
property that makes it worth having. `status.md` names what is done, what is in progress, and what
is next; the *next* items are the two or three drawn out of the backlog, cited to it.

One refinement, because `outstanding-work.md` is unusually good at something a plain to-do list
loses: **every item there carries the reason it is parked**, and several carry the reason the
question is weaker than it looks. `backlog.md` must keep that column. An item that has lost its
"why it is here and why it has not been done" has become a to-do, and a to-do that nobody has
justified in six months is indistinguishable from a to-do nobody wants.

And the backlog **points at the EPDs rather than restating them.** Three of its heaviest items are
`EPD-001`, `002` and `003`; copying their substance into the backlog would create the second copy
this whole restructure exists to prevent.

### Decision on fork 2 — freeze the handoff, and do *not* create a third file

`handoff.md` is frozen as `milestone-1-core/closing-notes.md`. Its own opening paragraph has always
said it should be deleted once the project can speak for itself; the milestone boundary is that
moment.

The owner asked whether session state needs its own document alongside `status.md`. **Recommendation:
no — one file, with a bounded volatile section.** The reasoning:

`handoff.md` does three jobs today, and only the third is genuinely ephemeral. It **indexes the
documents**, which `docs/README.md` and `CLAUDE.md`'s map now do. It **records what is complete**,
which is `status.md`. And it records **where we stopped and what to know before touching anything** —
which changes every session, where the other two change every phase.

The case for a third file is that a volatile document churning against a stable one is unpleasant.
The case against is stronger: two documents that both answer "where are we" will drift, and drift
between documents that were supposed to agree is this repository's demonstrated failure mode — Phase
5 found exactly that across four files. One file cannot disagree with itself.

So `status.md` has three parts, most volatile first:

| Part | Changes | Holds |
|---|---|---|
| **Where we stopped** | every session | The handoff: what was in flight, what to know before touching anything, the tree's state |
| **Where the project is** | every phase | Milestones → phases → tasks. Done, in progress |
| **What is next** | every phase | The two or three items drawn from `backlog.md`, cited to it |

**The split condition, so this is falsifiable rather than a preference:** if "Where we stopped"
passes ~30 lines, or if it starts carrying material that outlives the session that wrote it, it has
become a document and should be given its own file. Until then it is a section.

### Decision on fork 6 — six files, revised on 2026-08-16 to seven

**Revised from the four proposed in fork 6 below** after measuring the source material — an earlier
version of this line said "five", which matches neither the fork nor the outcome — and revised again
by fork 5, which puts
`design-decisions.md` back. The five that pass both tests plus `design-decisions.md`:
`architecture.md`, `design-decisions.md`, `observability.md`, `backend-lmstudio.md`,
`measurements.md`, `lessons.md`.

**Revised again on 2026-08-16 to seven, adding `backend-anthropic.md`.** The two tests below did not
decide it — at 13 lines it fails the size test exactly as this section says. **Symmetry decided it,
and the argument is this document's own, turned around.** The reasoning that follows warns that too
many files create ambiguous filing decisions. But a tier holding `backend-lmstudio.md` and *not*
`backend-anthropic.md` creates precisely such an ambiguity for the next backend — does Anthropic
material live in `architecture.md` or in a backend file? — and both answers are defensible, which is
this section's own definition of the expensive mistake. **Here the asymmetry is what costs, not the
extra file.**

Starting thin is safe for a reason this section already gives: a thin file is only bad when nobody
knows to open it, and its neighbour solves that completely.

What tips it is the planned expansion. `Goal` names four more cloud backends and eight more
harnesses. A convention invented at the third backend is a convention invented differently by
whoever gets there first.

**The two tests a reference file must pass.** A **nameable trigger** — a moment you would open *it*
and not its neighbour — and **enough content that grep would not find the fact faster inside a bigger
file**. `configuration.md` fails the first: "working on configuration" is not distinct from "working
on credentials" or "working on timeouts", which live in two other files. `request-shape.md` fails
the second at 12 lines.

**Why too many files is the more expensive mistake.** Every extra file is a filing decision for
future material — does "LM Studio requires auth, and here is the header" go in `configuration.md` or
`backend-lmstudio.md`? Both are defensible, so two sessions answer differently, and the fact lands in
two places where one later gets updated. That is precisely the failure this restructure exists to
prevent, and this repository has paid for it twice.

The failure modes are not symmetric, which is what decides it. **Merging two thin files later is one
commit**, and citations to either can point at the merged file with an anchor; splitting a fat file
later costs the same. **A duplicated fact discovered later is expensive** — someone has to determine
which copy is right and which documents trusted the wrong one. Over-splitting risks the expensive
failure; under-splitting risks the cheap one.

**The growth rule**, so the tier can expand without argument: a section becomes its own file when its
trigger is nameable *and* it passes roughly 40 lines. Until then it lives as a section in the nearest
file that already has a trigger. The 40 is a judgement, not a measurement — it is roughly where a
section stops being findable by grepping a file you already have open.

Note this rule keeps `proxy.py:3` working unchanged: it cites "Observed request shape" by **section
title**, and that section survives as a section of `architecture.md`.

### Decision 8 — `docs/README.md`, the manual

**New, raised by the owner, and it repairs a real gap in this proposal.** Everything above explains
*why* the tiers exist, and all of it would end up in `milestone-1-core/`, visible only to somebody
already digging through history. The rules would survive only as an archived argument, which is how
conventions get re-litigated.

So `docs/README.md` is written as a **manual, not a narrative**: what each tier is for, what belongs
in it, how to decide when a thing is ambiguous, the naming and numbering conventions, the growth
rule, and how to open a new milestone. It is the entry point to `docs/`, and it is the durable form
of this EPD.

**Widened on 2026-08-16.** It also carries the phase template, the branch convention, both milestone
playbooks, and two conventions migrating in from the session memory store — decisions 12, 13, 14 and
16 below. That is considerably more than this section scoped, and it creates a risk named there: **a
procedure used twice a year must not bury the filing rules read every week.** The mitigation is
placement plus this document's own growth rule — playbooks last, and out to
`docs/procedures/closing-a-milestone.md` if one passes 40 lines.

The test it must pass: **somebody who has never read `EPD-004` can file a new document correctly
using only `docs/README.md`.** If they must consult the archive, the manual has failed.

`reference/README.md` and `procedures/README.md` stay as they are — indexes of their own tier,
setting reading order. The manual governs; the indexes list.

## Decisions taken, 2026-08-16

A second round, from a discussion that began with *what is `CLAUDE.md` for* and ran through the
session memory store, the permission allowlist, branch naming, and how a milestone is opened and
closed. Decisions 9 and 10 revise decisions above and are corrected there in place; the rest are new
and were never in this document's scope.

**Why they are recorded here rather than in a new EPD.** All of them answer the same question this
document asks — *where does a durable fact live* — and splitting them across two documents would mean
the next reader has to find both. That is precisely the failure this document exists to prevent.

### 9 — `backend-anthropic.md` becomes the seventh reference file

Recorded under fork 6 above. `request-shape.md` stays deferred, which is what keeps `proxy.py:3`
needing no edit.

**The boundary between the two files, since the split is only worth making if it is stateable:**

| File | Answers |
|---|---|
| `architecture.md` | *How does a request flow, and why does this router exist* — the one-`ANTHROPIC_BASE_URL` problem, the prefix rule, the request path, the catch-all, and what the router deliberately does not do |
| `backend-<name>.md` | *What does this endpoint actually do* — measured behaviour, credential mode, timeout, quirks |

**And one thing `architecture.md` must now say that is written down nowhere today:** "dispatch, not
translation" holds *because both sides speak `/v1/messages`*. OpenAI and Gemini do not. Where that
premise stops is genuinely architectural, and it belongs in the architecture file rather than being
rediscovered by whoever adds the third backend.

### 10 — `Anthropic model IDs` leaves `CLAUDE.md`

Recorded in the triage table above, overriding this document's own "silently used, must stay"
finding. The replacement pointer must name the trigger, not the file.

**The residual risk, stated plainly because the measurement argued the other way:** that section
scores zero citations *because* it is a lookup table, and a pointer only helps a session that knows
it needs one. If a wrong model ID and its 400 ever appear, this decision is the first suspect.

### 11 — a review phase closes every milestone

Milestone 1 already ran one without knowing it was a template: **Phase 6**, on branch
`feat/phase-6-review-and-cleanup`, the only phase whose subject was the project rather than a
capability. It found one real defect (the SSE scan cap counting a whole chunk instead of one line),
one documentation defect that mattered (the 26× gap quoted without its slice), and one dependency
defect (`pydantic` and `starlette` imported directly and declared nowhere for five phases).

**It is specified as measurement, not as removal, and that is the whole design.** A phase chartered
to "find and cut bloat" has a built-in success condition and cannot comfortably return *there was
none*. Phase 6 is this repository's own counter-example: its plan asserted the source's 58% comment
density was redundant, a five-minute measurement put the docstrings' overlap with `CLAUDE.md` at a
mean **2.8%**, and the cut was refused. So each suspected defect is written as a claim, paired with
the measurement that would refute it, measured, and only then decided.

**Refusals are recorded as first-class outcomes.** Phase 6's two — not adopting `ty`, keeping the
comment density — are worth more than most of its fixes, because they stop the same cut being
re-proposed every milestone by the next person reading the same surface signal.

The checklist, derived from what Phase 6 did rather than invented:

| Check | Phase 6's result |
|---|---|
| Re-derive every quoted measurement from the frozen artefacts | 15 of 16 reproduced to the digit |
| Read all source and tests | 1713 + 2220 lines |
| Drive the software live | done, against local stubs |
| Reachability — dead code, unused imports, unreachable branches | none found |
| Declared dependencies against actual imports | **two undeclared** |
| The documents against each other, not only against the code | Phase 5's finding: drift across four files |
| **Did every phase complete the task list it published?** | **never done — new** |
| Close out the `Branch:` lines (decision 14) | four of six left open |
| Record refusals | two |

The seventh row is new, and there is precedent pointing straight at it: Phases 3, 4 and 5 each found
work already built or already misdescribed, and **nobody has ever checked the inverse** — a task
published as done that was not.

**The review phase and the milestone closing are one phase, in that order.** They were two separate
efforts in Milestone 1 only because no template existed, and the order is not arbitrary: had the
closing run first, `reference/measurements.md` would have canonised 26× without its slice, promoting
a known defect into the durable tier where it is far more expensive to dislodge. **Harvesting facts
into a permanent home requires first knowing which facts are true.**

Scale it. This is proportionate to a six-phase milestone; for a two-phase one the questions stay and
the depth follows what was actually touched. *Reviewed, nothing found, here is the evidence* is a
legitimate one-day outcome — a phase that must produce findings will manufacture them.

### 12 — both milestone playbooks live in `docs/README.md`

**Closing:** freeze the plan and phase notes → write `milestone-N/README.md` → harvest durable facts
into `reference/` → process lessons into `lessons.md` → numbers into `measurements.md` → live items
into `backlog.md` → reset `status.md`.

**Opening:** name the falsifiable central claim and the non-goals → run the cheapest experiment that
could refute it → capture real inputs before specifying anything → spikes for whatever the
architecture depends on, filed straight into `procedures/` or `captures/` → interview via EPD forks
and settle the expensive-to-reverse questions → write the spec with confidence markers → write
`implementation-plan.md` → open the folder and the branch.

Both are mined from Milestone 1 rather than invented. Three things in them are load-bearing:

**Capture the real input before specifying.** The highest-leverage thing Milestone 1 did at the front
was capture 118 KB of actual request bytes on 2026-07-28. It produced three body fields nobody
anticipated — `context_management`, `output_config`, `metadata.user_id` — and `CLAUDE.md` records the
consequence: a full-body Pydantic model *"would have silently dropped all three"*. The capture did
not inform the architecture, it **changed** it. Everything else in the opening was reasoning; this
was the only step able to contradict the reasoning.

**Plan at decreasing resolution, because four of six phases found their own plan wrong on contact.**
Phase 3 found four of five items already built, Phase 4 a third already measured, Phase 5 work
already misdescribed, Phase 6 its own premise refuted. So: the next phase in full, the one after in
outline, the rest as a title and the question it exists to close. And **a phase's first act is to
re-derive its own plan** against what is now known — Phase 4 did exactly that and deleted a step and
a probe.

**Mark every spec statement measured / inferred / assumed, and give each assumption the cheap check
that would settle it.** `CLAUDE.md` was Milestone 1's spec and Phase 6 found it almost entirely
right — but its errors are patterned: reliable where it recorded measurements, unreliable where it
recorded predictions, with both in the same prose. *"Almost certainly unsupported by LM Studio"* was
wrong, and `phase-4-notes.md` says it was wrong when written. Several such predictions were an hour's
work to test and stood for five phases.

**The two playbooks are written at different times, deliberately.** The **opening** playbook is
written now, because Milestone 1's opening already happened and sits in the archive to be mined. The
**closing** playbook is written *after this restructure lands, from what it actually cost* — writing
it now would commit an instrument that has never been run, in a repository whose most reliable lesson
is that plans are wrong on contact.

**`CLAUDE.md` must point at both, and the pointer carries an instruction rather than an address.** A
session opening or closing a milestone is to read the playbook and work from it rather than
improvise. This is called out separately from the ordinary pointers because it is the one case where
a missed pointer costs a whole milestone's worth of harvest.

### 13 — the phase template

`phase-N-<slug>/` holds `plan.md`, `notes.md` and `evidence/`.

- **`evidence/` gets a `README.md`** — what produced it, what it proves, what was redacted and how,
  and whether it can be regenerated. Practised throughout Milestone 1 and never written down; without
  it a frozen artefact is unreadable three milestones later.
- **`notes.md` carries a "Verified by" line** — what was run, when, what it produced. Every Milestone
  1 phase was signed off by driving the real thing, and that definition of done lived only in a
  session memory (decision 16).
- **`notes.md` states whether it was written while measuring or afterwards.** Phases 3 and 4 say so;
  Phase 2 says it did not. It changes how far a reader should trust the narrative, and this
  repository cares more than most about that distinction.
- **Milestone-root files are for work spanning phases** — the milestone's `implementation-plan.md`,
  and documents like `docs-restructure-plan.md` that belong to no single phase.

**One implementation plan per milestone, inside that milestone's folder.** This closes the gap left
open under "One EPD-000 convention this changes": `EPD-000:31` names `docs/implementation-plan.md` as
the home of the phases, and that file is being archived with no successor named.

### 14 — branch naming, and where branches are recorded

The convention already exists in the history and was never written down. Both prefixes are
established — `docs/add-claude-md` and `docs/epd-index-and-corpus-proposal` predate this branch, and
the latter was merged `--no-ff` as `acb399f`.

| Prefix | For |
|---|---|
| `feat/phase-N-<slug>` | a numbered phase; the slug matches its archive folder exactly (decision 15) |
| `docs/<slug>` | documentation work belonging to no phase — EPDs, a milestone's opening |
| `fix/<slug>` | a defect outside a phase |
| `chore/<slug>` | tooling, dependencies, formatter bumps (`d1def4f` is the precedent) |

**No suffix for planning work, because the prefix already carries it.** Measured: each phase plan's
creating commit is contained by that phase's own branch and nothing earlier — `7f68d02` on
`feat/phase-4-lmstudio-parity`, `4f7856a` on `feat/phase-5-config-and-timeouts`, `8f4a46c` on
`feat/phase-6-review-and-cleanup`. **The plan opens the phase branch**, so plan and execution share
one branch and one merge commit, which is what keeps one archive folder mapping to one branch. A
separate planning branch would give a single phase two merge commits. Planning that produces no code
goes on `docs/<slug>` — `EPD-003` was born on `docs/epd-index-and-corpus-proposal`.

The same rule settles whether a milestone's opening is a phase. It produces documents and instruments
and changes nothing in `src/`, so it is a `docs/` branch. The review phase does touch `src/` — Phase
6 fixed seven items there — so it is a numbered `feat/` phase. **One rule, opposite answers, no new
convention.**

**Work belonging to a later phase never goes on an earlier phase's branch, even documentation.** Two
spec commits were moved off the Phase 1 branch for exactly this reason. One consequence: a
`feat/phase-N+1-…` branch may sit holding only an unapproved plan, and if the plan is rejected the
branch is **deleted, not renamed**.

**Where branches are recorded**, following the one-home rule:

- **`status.md` carries only in-flight branches** — name, purpose, tree state, next action. That is
  what `handoff-docs-restructure.md` already does, generalised. Merged branches are not listed: git
  already holds that, and a hand-maintained list would drift.
- **The phase note carries the permanent record** — branch, fork point, and merge commit.

The second half needs repair, not merely recording. **Five `Branch:` lines exist across four of the
six phases** — an earlier version of this line said "five of six phases", which contradicted its own
next clause — in inconsistent places (Phase 4 in both plan and notes, Phase 5 only in the plan,
Phases 1 and 6 in neither), and **only one records the merge commit**: `phase-4-notes.md:7`, *"Merged with `--no-ff` as
`50444c5`"*. The other four say "Merge back with `--no-ff`" — written before the merge and never
closed out. That is this repository's signature failure in miniature, a document recording intent and
never updated to outcome, and closing them is a review-phase checklist item.

### 15 — the archive's phase slugs follow the branch names

Three of six disagree, and the branches win, because the folders do not exist yet while the branch
names are fixed in six merge commits and five `Branch:` lines.

| Branch | This document's earlier slug | Now |
|---|---|---|
| `feat/phase-3-failure-handling` | `phase-3-error-handling/` | `phase-3-failure-handling/` |
| `feat/phase-5-config-and-timeouts` | `phase-5-credentials-and-timeout/` | `phase-5-config-and-timeouts/` |
| `feat/phase-6-review-and-cleanup` | `phase-6-review/` | `phase-6-review-and-cleanup/` |

`phase-1-proxy`, `phase-2-observability` and `phase-4-lmstudio-parity` already agreed.

**The cost is real and worth naming:** `credentials-and-timeout` describes Phase 5 more accurately
than `config-and-timeouts` does. Accuracy loses to navigability here — *branch name equals folder
name* is worth more than a better adjective, and it is only free if adopted before the folders exist.

### 16 — the session memory store is folded into the repository

**The finding that forces it:** this restructure exists to give every durable fact one home, and a
second store of durable facts sits entirely outside it — untracked, machine-local, keyed on an
absolute path, invisible to git and to any human contributor. **All nine entries** are project
conventions or portable rules rather than facts about this machine, and **three carry paths this
restructure breaks**. One is already stale, filing EPDs at `docs/EPD-NNN-…` when they have lived in
`docs/epd/` since `8a10bc3`.

**No count over the repository could have caught any of them, because they are not in the
repository** — which is true whatever the count is, and is why this argument no longer quotes one.
And `docs-restructure-plan.md` already says "Merge `--no-ff` **per repository convention**" — a
committed document depending on a convention that exists only in machine-local memory, which would
silently not load if the repository were opened by its other path.

**The rule, as first written:** *memory holds what is true about working with an agent on this
machine; the repository holds what is true about the project*, tested by asking whether a new human
contributor would need to know it.

**That rule was wrong on one axis, corrected the same day.** It offered two categories where the
material has three, and the missing one is the interesting one:

| Category | Home |
|---|---|
| **Project-specific** — the parity table, the measurements | this repository's `docs/` |
| **Portable across this owner's projects** — how to work, and what breaks | this repository's `CLAUDE.md`, copied forward at the next project (decision 18) |
| **Genuinely local to one laptop** | session memory |

| Memory | Destination |
|---|---|
| `propose-before-implementing` | `CLAUDE.md` — the working agreement |
| `merge-with-no-ff-for-visible-boundaries` | `CLAUDE.md` — already cited as a repository convention |
| `exercise-it-before-committing` | rule to `CLAUDE.md`; the Phase 2 and 3 evidence to `lessons.md` |
| `check-prior-evidence-before-planning-a-rerun` | rule to `CLAUDE.md`; evidence to `lessons.md` |
| `document-decisions-in-separate-docs` | `docs/README.md` — it *is* the manual, written before the manual existed |
| `redact-to-stable-placeholders` | `docs/README.md` — the evidence-filing convention |
| `keep-bash-commands-statically-analyzable` | `CLAUDE.md`. **This table first said "stays — about the harness, not the router"**, which put it in the machine-local category. It is portable, not local: the harness is the same in every project this owner works on, and stepping on the rake twice is the cost of filing it as local |
| `git-merge-cannot-read-message-from-stdin` | `CLAUDE.md`, appended to the `--no-ff` rule, since that is the operation that triggers it. **Also first recorded as "stays"** |
| `ask-before-touching-the-machine` | `CLAUDE.md`, beside `propose-before-implementing` — it is a working agreement about consent. **Omitted entirely from this table until 2026-08-16; see below** |

**So all nine migrate, and the machine-local category is empty.**

**That conclusion was first written from an inventory of eight, and the ninth was the one most likely
to refute it.** `ask-before-touching-the-machine` — ask before GUI toggles, before reading `.env`,
before starting long-running local processes — is the single entry whose subject *is* the state of
this machine, and it appeared in no row of this table, no destination, and no verification item.
Found by a fresh-context review on 2026-08-16.

Recorded rather than quietly patched, because the failure is this document's own subject arriving in
the decision written to fix it: **a conclusion asserted from a count that was not re-checked.** The
conclusion survives — the owner's call is that it belongs in the project too, so nine of nine
migrate — but it survives by luck rather than by method, and the corrected version is a count of nine
actually verified against the directory rather than eight recalled.

The store's one genuinely local fact — that `~/Projects/code-2026/…` and the OneDrive path are the
same inode — is **already in `CLAUDE.md` today**, and was before this work began. So the third
category was invented by this decision and holds nothing.

Both migrating rules earn `CLAUDE.md` under the admission test rather than by association. A session
writes `cd "$(git rev-parse --show-toplevel)"` or `git merge -F -` **confidently and wrongly**, with
no reason to look anything up first. That is the definition of a rule that must be in context.

**Move, do not copy.** Each migrated memory shrinks to a pointer at its new home. A memory duplicated
into the repository is exactly the drift this exercise fights.

One clause is corrected during the move rather than carried across. `propose-before-implementing`
ends *"Commits are also opt-in — they ask for each one"*, which the permission allowlist has
contradicted for some time. **Resolved 2026-08-16 in the allowlist's favour: commits do not need a
separate ask.** The rest of that memory is untouched — a design answer is still not a build order.

### 17 — the permission allowlist is split, tracked from local

Outside this branch's scope, decided in the same discussion, and recorded here because nothing in
`docs/` currently admits the file exists.

`.claude/settings.local.json` holds 51 entries, git-ignored, accreted by clicking *allow*. Roughly a
dozen are single-use fossils — a literal PID, three separate `/tmp` scratch files, two full `curl`
lines with a fixed port. Several are much broader than the fossils suggest: `Bash(curl *)` is
arbitrary outbound network, `Bash(python3 *)` and `Bash(uv run *)` arbitrary execution.

**Split it the way the documents are split.** A tracked `.claude/settings.json` holds the durable
project policy — it encodes that `make test` is the test command and that ruff is pinned, which is
project knowledge and belongs to the project rather than to one laptop. The untracked local file
keeps machine-specific accretions and is pruned periodically. `docs/README.md` names the split in one
line so it is not re-litigated.

### 18 — the methodology is portable, and extraction is deliberately deferred

The owner asked for a **splittable artifact** — playbooks, development methodology, guardrails — that
can be lifted into the next project.

**The inventory finding is striking and worth recording even though nothing is being built from it
yet.** Sorting this project's documents by whether they would survive a change of subject:

| Portable | Project-specific |
|---|---|
| The EPD system and its conventions | Everything about LM Studio, Anthropic and the router |
| The four-tier structure | The reference tier's contents |
| The milestone and phase template | The measurements and their slices |
| Both playbooks (decision 12) | The archive |
| The review-phase spec (decision 11) | Phase 6's actual findings |
| Branch naming (decision 14) | — |
| Measured / inferred / assumed marking | — |
| Visible in-place correction | — |
| The auto-load admission test | — |
| The permission policy shape (decision 17) | — |
| All nine migrating rules (decision 16) | The dual-path note |

**Nearly the whole methodology is portable, and what is not is the reference tier and the archive** —
the same seam this restructure already cuts, one level up.

Three mechanisms were considered and **all three were declined**:

- **A `docs/method/` tier**, holding the portable documents so extraction is a directory copy.
  Declined: it splits the manual, and `docs/README.md`'s acceptance test — *file a new document
  correctly from this file alone* — would then span two files.
- **`~/.claude/CLAUDE.md`**, which is auto-loaded into every project on this machine and **does not
  currently exist**. Declined for now; the rules stay project-local. The mechanism is recorded here
  because it costs nothing to know about and remains available.
- **A separate method repository.** Declined as premature.

**Decided: one file, extract by copying when project #2 starts.** The reasoning is this document's
own, applied to itself: **a methodology extracted from n=1 is a guess about what generalises.** Which
rules survive contact with a different problem is not knowable yet, and it is exactly the shape of
argument that defers the closing playbook in decision 12 — do not commit an instrument that has never
been run.

**The cost is named rather than waved away:** the sorting work does not disappear, it moves to a
moment when the material is colder. That is accepted because the alternative pays a structural cost
now, every day, for a benefit that arrives once.

Concretely, extraction is: copy `docs/README.md`, delete the rows naming a backend, and copy the
`CLAUDE.md` rule block. Not a build step, and nothing in this plan produces it.

### 19 — the `$(...)` rule is documented, not enforced

Raised under decision 17 and **investigated before deciding**, because a `PreToolUse` hook could
reject any Bash command containing command substitution, which is stronger than a written rule: it
cannot be forgotten.

**Rejected, and the reasoning is recorded so it is not re-proposed from the appeal of enforcement
alone** — decision 11's principle that refusals are first-class outcomes, applied here.

- **The false positives are real in this repository, not hypothetical.** The `Makefile` contains six
  `$(VAR)` occurrences. Any command that greps, seds, prints or writes Makefile content carries `$(`
  as literal data. **The grep that measured this would itself have been blocked**, since it searches
  for the pattern.
- **Quoting makes it undecidable without a shell parser.** `echo '$(date)'` is inert. Separating that
  from live substitution requires parsing shell quoting — the exact capability whose absence causes
  the original problem. A hook attempting it reimplements the guardrails firewall, less well.
- **It converts a recoverable prompt into a hard block.** The firewall already handles this case by
  asking. The rule exists because that prompt is *friction*, not because anything dangerous happened,
  and a hard failure on a false positive is strictly worse than a prompt that can be approved.
- **It sits in the path of every Bash call.** A bad pattern or a crashing hook blocks all shell work
  until someone hand-edits `settings.json`.
- **The written rule is holding.** Zero occurrences of `cd "$(` across the session history since the
  rule was written. Weak evidence — one agent, one project — but it is the only evidence available
  and it points away from enforcement.
- **Enforcement cannot teach the alternative.** What changed behaviour was the rule's second half —
  *absolute paths, and prefer Read/Grep/Glob* — not the prohibition. A block with no explanation
  invites working around it rather than using the better tool.

If enforcement is ever revisited, the least-bad form is a **warning** matched to the specific reflex
(`$(git rev-parse --show-toplevel)`) rather than a **block** matched to all of `$(`.

## The original forks, as written before the decisions

Kept because the reasoning is what makes the decisions checkable later.

**1. Whether findings get IDs.** The strong version of `measurements.md` gives every measurement a
citable ID (`M-014`) so a claim in any document is a link rather than a restatement, and a
contradiction becomes findable by grep. The cost is a registry to maintain and a habit to keep. The
weak version — one canonical section per number, cited by anchor — costs nothing and catches most of
it. **Proposed: start weak.** Revisit only if a seventh phase finds another number quoted wrong.

**2. What happens to `handoff.md`.** It says in its own first paragraph that it should be deleted
once the project can speak for itself, and `outstanding-work.md` records that as its intended end.
The milestone boundary is the natural moment. Three options: freeze it as
`milestone-1-core/closing-notes.md` and let `docs/status.md` take over the role; freeze it and start
a fresh thin handoff for Milestone 2; or keep one living handoff across all milestones.
**Proposed: freeze it, and let `status.md` take the role** — but this is a genuine preference and
the archive is unaffected either way.

**3. Whether `outstanding-work.md` is Milestone 1 history or Milestone 2 input.** It is written as a
survey taken *at* the boundary, and most of its content — the three EPDs, the open measurements, the
warmup-probe cost — is live work. Archiving it buries the Milestone 2 backlog; keeping it at top
level leaves a document full of Phase 5 marginalia in the durable tier. **Proposed: split it.** The
live items become `docs/status.md`'s backlog section; the survey itself, with its record of what it
got wrong, is archived. This is the one item in this proposal that rewrites a document rather than
moving it, and it should be a commit of its own.

**4. Where the captured request lives.** `docs/captures/` above, on the grounds that it is raw data
serving both `reference/request-shape.md` and the probes. The alternative is
`reference/captures/`, next to the document derived from it. Low stakes; it changes one path in
`probe.py` either way. **This is the least consequential item in the document and it was, in the
first version, the only structural question given a fork** — which was a misallocation. Forks 5 and
6 are the ones that matter.

**5. Whether `Design decisions` should be split at all.** Opened because the measurement above
contradicts the triage: it is the most-cited section in `CLAUDE.md`, and three of the four EPDs cite
it *for its rationale*, which is the half proposed to move. An EPD exists to argue against a
decision; splitting statement from reasoning puts the reasoning one link away from every document
whose job is to weigh it.

Three options. **(a) Split as proposed** — statements stay, rationale moves; cheapest, and the risk
is that a future session reverses a decision having read only the statement. **(b) Do not split it**
— the whole 58-line section stays in `CLAUDE.md`, and the ~100-line target becomes ~150. **(c) Split
by decision rather than by layer** — the three or four decisions with a measured cost (byte-relay and
prompt caching, no special case for background traffic, the SSE `error` event with no measured
consumer) keep their reasoning inline; the rest move. **Proposed: (b).** The measurement says this
section carries its weight, and the file it would leave behind is a rules list without the reasons
anyone kept the rules — which is exactly the artefact that gets quietly reversed.

**6. Whether the `reference/` tier should start at ten files.** Ten new documents plus two index
`README.md`s, on day one, for a 371-line codebase. Six are extractions with an obvious home,
`measurements.md` and `lessons.md` earn themselves, and `backend-anthropic.md` is assembled from
three sources and may come to a page. The lighter version starts `reference/` with four files —
architecture, design-decisions, observability, measurements — and lets the rest earn a home as
material accumulates. **Proposed: start light.** If the tier split is the thing being decided, its
granularity is part of what is being decided, and a thin index is easier to grow than to prune.

## One EPD-000 convention this changes

`EPD-000:28-30` says an EPD is "not a design document": `CLAUDE.md` holds the design, and an EPD
"graduates *into* `CLAUDE.md` under 'Design decisions'" when a decision is taken.

**The decision on fork 5 makes the change mandatory.** The whole section leaves `CLAUDE.md`, so an
accepted EPD now graduates into **`reference/design-decisions.md`**. `EPD-000:28-30` must be edited
to say so; leaving it would send the next accepted proposal to a file that holds only a table of
contents.

Two further `EPD-000` edits fall out of the same decision:

- **The graduation target is per-subject, not fixed.** This EPD graduates into `docs/README.md`
  rather than into the design decisions, because its subject is the filing system rather than the
  router. `EPD-000` should say that a decided EPD graduates into *the durable document that owns its
  subject*, and name the two that exist.
- **`EPD-000:31`** names `docs/implementation-plan.md` as the home of the phases. That file is
  archived into `milestone-1-core/`, and nothing was named as Milestone 2's successor. `status.md`
  takes over `handoff.md`'s role, not the plan's. **Closed on 2026-08-16 by decision 13: one
  implementation plan per milestone, inside that milestone's folder**, recorded in `docs/README.md`
  so the answer is not invented twice.

## What this does not propose

- **No rewriting of measured content.** Every number, table and finding moves verbatim. The
  documents actually *rewritten* are **four**: `CLAUDE.md`, `README.md`, `outstanding-work.md` (split
  into `backlog.md`) and `EPD-000` (the graduation convention and its two body citations) — plus the
  new `docs/README.md`, `status.md`, `backlog.md` and the
  `reference/` files assembled out of existing text. **This said "five" and reached it by naming
  `README.md` twice**, once for the file and once for "the original brief in `README.md`" — which
  `docs-restructure-plan.md` says stays **verbatim** and is therefore not rewritten at all. Corrected
  2026-08-16, and pointedly, since this is the paragraph where the same list was already corrected
  once. The first version of this list said three and
  omitted `outstanding-work.md`, eleven lines after calling it "the one item in this proposal that
  rewrites a document rather than moving it". If a fact changes during this work, that is a defect
  in the work.

  **Amended 2026-08-16:** `CLAUDE.md` now also *gains* material — the branch convention, the two
  playbook pointers, and seven rules migrating in from the session memory store — where this document
  had only ever described it losing sections. None of that is newly invented: every rule is written
  down somewhere already, and three of the four memory rules are older than this document.
- **No deletion.** Nothing is dropped, including the marginalia. The archive is where a thing goes
  to stop being in the way, not to stop existing.
- **No change to `src/`, `tests/` or behaviour**, beyond updating the 11 doc citations in docstrings
  and comments — 7 in `src/`, 1 in `tests/`, 3 in `config.yaml`. The test count should be 158 before
  and after.

## The cheapest next step, and the gate

The gate was a decision, not a measurement: **is the four-tier split (reference / procedures /
epd / milestone archive) the right cut?** **Accepted on 2026-08-15**, so the rest of this document
applies. Had it been refused, the job would have collapsed to
`git mv docs/phase-* docs/milestone-1-core/` plus link fixes — perhaps forty minutes.

With the split accepted, the cheapest first step is **not** moving files. It is writing
`docs/reference/backend-lmstudio.md`, extracting the measured parity table out of
`phase-4-notes.md` — the one source most fused with its phase narrative. If that table cannot be
lifted without dragging half the narrative with it, the tiers are wrong, and it is better to learn
that from one file than from twenty-two.

**What "cannot be lifted" means, added 2026-08-16.** A gate with no failure criterion is not a gate,
and this repository states its other thresholds precisely — ~30 lines for "Where we stopped", ~40 for
the growth rule. So: **the gate fails if the extracted file cannot state the parity findings without
referring to Phase 4 as a phase** — its plan, its ordering, which probe ran when, what it expected
versus found. Those are process, and a reference document that needs them has not separated durable
from process, which is the whole proposition.

Two things are explicitly *not* failure. Citing `phase-4-notes.md` as the **provenance** of a
measurement is correct and expected — that is what the archive is for. And carrying the *conditions*
of a measurement (model, window size, date, that authentication was off) is not narrative; it is the
slice, and a number without it is the 26× error.

**If the gate fails**, the fallback is the one named above: abandon the tier split, and the job
collapses to `git mv docs/phase-* docs/milestone-1-core/` plus link fixes — roughly forty minutes.
Commits 2 and 3 are cheap and reversible, which is what makes running the gate first worth it.

**The first version of this document named a different first step**, writing `measurements.md` and
`lessons.md`, and justified it by the parity table — a file it did not include. Those two are
*synthesis*: they harvest asides scattered across six phase notes, and harvesting asides succeeds
whether or not the tier split is sound. They would have passed the gate without testing it. They
remain the highest-value output of this proposal and are worth writing second, whatever is decided
about the rest.

`docs/docs-restructure-plan.md` sequences the rest, and lists the eight things that break silently.
