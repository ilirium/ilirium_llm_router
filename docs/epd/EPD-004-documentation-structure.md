# EPD-004 — Documentation structure at the milestone boundary

**Status: proposal, written 2026-08-15. Nothing is decided and nothing has been moved.** The
mechanical half — which file goes where, and everything that breaks when it does — is in
`docs/docs-restructure-plan.md`. This document is the argument for the shape; that one is the
argument for the order of operations. Neither is a build order.

This is the first EPD whose subject is the repository rather than the router. `EPD-000` does not
restrict the series to the product, and the format fits: a question written up before it is
answered, with the forks left open.

## Why now

Milestone 1 is done. Six phases, 68 files under `docs/`, and a `CLAUDE.md` of 337 lines that is
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
| 68 files under `docs/`, 50 of them tracked by git | **Measured** — `git ls-files docs`, `find` |
| `CLAUDE.md` is 337 lines / 46725 bytes, loaded every session | **Measured** |
| 253 mentions of the 22 documents and directories that would move | **Measured** — grep over `docs/`, `README.md`, `CLAUDE.md`, `src/`, `tests/`, `config.yaml`, `.gitignore` |
| 8 citations of `docs/` paths from 6 code and config files | **Measured** — `config.py:62`, `proxy.py:321`, `stats.py:26`, `observe.py:12`, `tests/test_observe.py:9`, `config.yaml:24,30,44` |
| 4 `.gitignore` entries name `docs/` paths, one of them a negation | **Measured** — `.gitignore:229,231,233,237` |
| `probe.py` breaks silently if its directory changes depth | **Measured** — `ROOT = HERE.parent.parent` at `probe.py:40`, used to locate the capture and `logs/calls.csv` |
| Moving reference material out of `CLAUDE.md` costs a session the knowledge unless a pointer replaces it | **Inferred strongly** — `CLAUDE.md` is auto-loaded, nothing else in `docs/` is |
| The proposed split makes future quoting-forward errors less likely | **Unmeasured hypothesis** — it is the reason for the shape, and it is not testable in advance |

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
  status.md                  one page: milestones → phases → tasks, and where we stopped
  reference/                 durable. Survives every milestone
    README.md                the reading order and what each file answers
    architecture.md          dispatch not translation; why the router exists
    design-decisions.md      the decisions list — don't quietly reverse these
    observability.md         the CSV columns and the recorder's constraints
    configuration.md         config shape, credential modes, timeouts
    backend-lmstudio.md      the measured parity table, context and window facts
    backend-anthropic.md     model IDs, auth shape, rate-limit behaviour
    request-shape.md         what Claude Code actually sends
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
    outstanding-work.md
    phase-1-proxy/           notes.md, evidence/
    phase-2-observability/   notes.md, evidence/
    phase-3-error-handling/  notes.md, evidence/
    phase-4-lmstudio-parity/ notes.md, plan.md, evidence/
    phase-5-credentials-and-timeout/
    phase-6-review/
```

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

## What leaves `CLAUDE.md`, and the rule for deciding

`CLAUDE.md` is auto-loaded; nothing in `docs/` is. So the split cannot be "long things move out".
Anything moved is knowledge a session no longer has by default, and the one-line pointer that
replaces it is load-bearing — it has to name *when to open the file*, not merely that it exists.

**The rule: what every session must hold in its head stays. What you look up when touching one area
moves, with a pointer that names the trigger.**

| Section, today | Lines | Proposal |
|---|---|---|
| Status | 5–63 | **Leaves.** A three-line summary in `CLAUDE.md`, the board in `docs/status.md`, the detail in the milestone archive |
| Layout and commands | 64–99 | **Stays.** Every session needs it, including the ruff pin and why it is pinned |
| Goal | 100–105 | **Stays**, compressed to three lines; the long form is `reference/architecture.md` |
| The central architectural problem | 106–166 | **Leaves** to `reference/architecture.md` and `reference/backend-lmstudio.md`. A four-line summary stays: no translation, dispatch on the model name, relay bytes |
| Observed request shape | 167–178 | **Leaves** to `reference/request-shape.md` |
| Design decisions | 179–236 | **Split.** The one-line statement of each decision stays — these are the rules a session must not quietly reverse. The rationale and the measurements behind each move to `reference/design-decisions.md` |
| Open proposals — the EPDs | 237–250 | **Stays**, cut to the table plus "do not build from one" |
| Observability: log + CSV stats | 251–312 | **Leaves** to `reference/observability.md`. A pointer stays, triggered on "touching the recorder" |
| Anthropic model IDs | 313–325 | **Stays.** Short, and getting it wrong produces a 400 |
| Stack decisions, Style | 326–337 | **Stays** |

Target: roughly 100 lines. The risk to state plainly is that this trades **certainty** for **size** —
today every fact is guaranteed present; afterwards some facts depend on a pointer being followed.
The design decisions section is where that risk concentrates, which is why its statements stay and
only its reasoning leaves.

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

## Open forks — deliberately not decided here

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
`probe.py` either way.

## What this does not propose

- **No rewriting of measured content.** Every number, table and finding moves verbatim. The only
  documents *rewritten* are `CLAUDE.md`, `README.md`, and the two new `reference/` files that are
  assembled out of existing text. If a fact changes during this work, that is a defect in the work.
- **No deletion.** Nothing is dropped, including the marginalia. The archive is where a thing goes
  to stop being in the way, not to stop existing.
- **No change to `src/`, `tests/` or behaviour**, beyond updating the 8 doc paths cited in
  docstrings and comments. The test count should be 158 before and after.

## The cheapest next step, and the gate

The gate is a decision, not a measurement: **is the four-tier split (reference / procedures /
epd / milestone archive) the right cut?** If reference and archive are not worth separating, none of
the rest of this document survives, and the whole job collapses to `git mv docs/phase-* docs/milestone-1-core/`
plus link fixes — perhaps forty minutes.

If the split is accepted, the cheapest first step is **not** moving files. It is writing
`docs/reference/measurements.md` and `docs/reference/lessons.md` from the existing phase notes,
because that is the step that discovers whether the durable half separates cleanly from the process
half. If it does not — if the parity table cannot be lifted out of `phase-4-notes.md` without taking
half the phase narrative with it — then the tiers are wrong and it is better to learn that from two
files than from twenty-two.

`docs/docs-restructure-plan.md` sequences the rest, and lists the seven things that break silently.
