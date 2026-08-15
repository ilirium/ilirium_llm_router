# EPD-004 — Documentation structure at the milestone boundary

**Status: decided 2026-08-15 by the repository owner. Nothing has been moved yet.** Written the same
day as a proposal; all six forks were answered, and the outcomes are recorded under "Decisions
taken" below, each beside the reasoning it overrode or confirmed. The mechanical half — which file
goes where, and everything that breaks when it does — is in `docs/docs-restructure-plan.md`.

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
| 253 mentions of the 22 documents and directories that would move | **Measured** — grep over `docs/`, `README.md`, `CLAUDE.md`, `src/`, `tests/`, `config.yaml`, `.gitignore` |
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
    measurements.md          every number the docs quote, with its date and its slice
    lessons.md               how this project has been wrong, and what caught it
  procedures/                re-runnable. How to check something again
    README.md                the index of checks, and when each is worth re-running
    lmstudio-usage-check.md
    lmstudio-capability-probes/    (was phase-4-probes/)
    testing-against-claude-code.md
    anthropic-auth-check.md
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
    phase-1-proxy/           notes.md, evidence/
    phase-2-observability/   notes.md, evidence/
    phase-3-error-handling/  notes.md, evidence/
    phase-4-lmstudio-parity/ notes.md, plan.md, evidence/
    phase-5-credentials-and-timeout/
    phase-6-review/
```

**Deferred, each with its reason** (decision 7): `configuration.md` — its material is credential
modes, which are a design decision, and timeouts, which belong to `backend-lmstudio.md`; it has no
source of its own. `backend-anthropic.md` and `request-shape.md` — 13 and 12 lines respectively,
starting as sections of `architecture.md`. Each becomes a file when it has a nameable trigger *and*
passes roughly 40 lines.

`milestone-2-*/` is created when Milestone 2 starts, with the same internal shape. That repetition is
the point: the archive layout is a template, so the second milestone costs no design.

### Two files in `reference/` that do not exist today

**`measurements.md`.** One table of every number these documents quote, each row carrying the date,
the instrument, and — the part that matters — **the exact slice the number describes**. Phase 6's
single most consequential finding was the 26× gap quoted for three phases without the slice, where
recomputing over the whole file gives 3.9×. Both figures are right; they answer different questions.
The prose fix was to write the recipe down once. The structural fix is to give every quoted number
one canonical row, so quoting forward means linking rather than restating.

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
| Observability: log + CSV stats | 251–312 | **4** | 4 — including `stats.py:3` |
| Observed request shape | 167–178 | **3** | 2 — including `proxy.py:3` |
| Goal | 100–105 | 1 | 1 |
| The central architectural problem | 106–166 | 1 | 1 |
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
- **Genuinely inert** — Status, at 59 lines the single largest section in the file, with **zero**
  citations in six phases. Stack decisions and Style, 12 lines, likewise.

**The strongest measured argument for cutting is `Status`**, and it is a stronger one than this
document originally made: 18% of an auto-loaded file, never once cited as an authority, consisting
almost entirely of Milestone 1 phase history. The triage table below already proposed moving it, for
the weaker reason that it was long.

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
| Anthropic model IDs | 313–325 | 0 | **Stays** — silently used. Short, and getting it wrong produces a 400 |
| Stack decisions, Style | 326–337 | 0 | **Stays.** 12 lines; not worth a link |

Target: roughly 100 lines — about 80 of surviving sections, plus a three-line status summary, a
four-line architecture summary, two pointers, and the twelve-line table of contents for the
decisions.

The risk to state plainly is that this trades **certainty** for **size** — today every fact is
guaranteed present; afterwards some facts depend on a pointer being followed. The measurement locates
that risk precisely: it is not spread across the file but concentrated in **Design decisions**, the
one section used as an authority by the documents whose whole purpose is to argue with it.

**The fork 5 decision accepts that risk deliberately**, and mitigates it with the titles-only table
of contents rather than by keeping the section. The bet is that a session which can see *that* a
decision exists will open the file before reversing it, and that a decisions document worth reading
front to back is worth more than one guaranteed to be in context but never read as a whole. It is a
bet, not a measurement, and it is the one place this restructure could make things worse.

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

### Decision on fork 6 — the reference tier starts at six files

**Revised from "five" after measuring the source material**, and revised again by fork 5, which puts
`design-decisions.md` back. The five that pass both tests plus `design-decisions.md`:
`architecture.md`, `design-decisions.md`, `observability.md`, `backend-lmstudio.md`,
`measurements.md`, `lessons.md`.

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

The test it must pass: **somebody who has never read `EPD-004` can file a new document correctly
using only `docs/README.md`.** If they must consult the archive, the manual has failed.

`reference/README.md` and `procedures/README.md` stay as they are — indexes of their own tier,
setting reading order. The manual governs; the indexes list.

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
  archived into `milestone-1-core/`, and **nothing is named as Milestone 2's successor.**
  `status.md` takes over `handoff.md`'s role, not the plan's. **This gap is still open** and belongs
  to whoever writes Milestone 2's plan; `docs/README.md` should record the convention — one
  implementation plan per milestone, inside that milestone's folder — so the answer is not invented
  twice.

## What this does not propose

- **No rewriting of measured content.** Every number, table and finding moves verbatim. The
  documents actually *rewritten* are five: `CLAUDE.md`, `README.md`, `outstanding-work.md` (split
  into `backlog.md`), `EPD-000` (the graduation convention and its two body citations), and the
  original brief in `README.md` — plus the new `docs/README.md`, `status.md`, `backlog.md` and the
  `reference/` files assembled out of existing text. The first version of this list said three and
  omitted `outstanding-work.md`, eleven lines after calling it "the one item in this proposal that
  rewrites a document rather than moving it". If a fact changes during this work, that is a defect
  in the work.
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

**The first version of this document named a different first step**, writing `measurements.md` and
`lessons.md`, and justified it by the parity table — a file it did not include. Those two are
*synthesis*: they harvest asides scattered across six phase notes, and harvesting asides succeeds
whether or not the tier split is sound. They would have passed the gate without testing it. They
remain the highest-value output of this proposal and are worth writing second, whatever is decided
about the rest.

`docs/docs-restructure-plan.md` sequences the rest, and lists the eight things that break silently.
