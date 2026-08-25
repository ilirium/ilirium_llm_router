# IDM-008 — The register: every name and number, in one reachable section

**In force 2026-08-21.** `CLAUDE.md` points here and does not restate the rule — see "Why this is a
pointer and not a restatement". Read this **before writing a phase plan**, and **before the phase's
closing task**, which checks the register against the code.

---

## The rule

**Before any of the work starts, the plan gains one reachable section holding every name and number
the phase will introduce.** One section, not a scatter of definitions through the prose — the point
is that they can be read *together*.

What goes in it:

| | |
|---|---|
| **New modules, classes, functions** | Every name the phase adds to `src/` |
| **Configuration keys** | With their defaults and their types |
| **Module constants** | Every one, with its value |
| **Existing names it must not collide with** | The ones already in the codebase that the new work sits beside |
| **Names that go on disk** | Files, directories, and anything a path is built from |
| **Any record or index shape** | Columns in order, fields, the schema version |
| **Sentinel values and magic numbers** | Every literal that means something |
| **CLI flags** | The exact spelling |
| **Derived numbers** | Marked as arithmetic rather than settings, so nobody makes them configurable |

**Anything the plan names and gives no value anywhere is marked `❓`.** That column is the instrument.

**The phase's closing task checks the whole section against the code**, and expects the `❓` column to
be empty. Make it a numbered task in the plan, not a habit — a check that is nobody's task is nobody's.

## Two rules that keep it from becoming a second source of truth

**The register is authoritative for the *value*; the prose is authoritative for the *why*.** A
constant that appears in both places is drift waiting to happen, and this repository has been bitten
by two-homes-for-one-fact often enough to name it. So: **change the number in the register, and leave
the prose holding only the reason.**

**Rows are struck, not deleted, when they close.** A row that vanishes cannot show that the mechanism
worked, and the record of what was open is most of what makes the register worth having next time.

## It is not a tidying exercise, and the difference is measured

This is the part worth keeping, because the register *looks* like bookkeeping and the instinct is to
skip it or to do it afterwards.

**Asking "what is the value?" of every name at once is a different instrument from reading the
prose.** Phase 10 is the evidence, and it is unusually clean: the register was compiled on 2026-08-19
against a plan that had **already been through two forward-review passes** under `IDM-004`.

**It found eight names that the plan mentioned and gave no value anywhere.** All eight closed the same
day, in one owner pass. But the count is not the finding — **three of the eight were not holes:**

| | What the register did |
|---|---|
| **Contradicted an asserted number** | The plan specified a "twenty-second shutdown". The measured drain was 0.433 ms/body, making the real value `DRAIN_TIMEOUT_S = 5` — the plan's figure was **~70× out and had survived two reviews** |
| **Refuted a stated justification** | The plan argued for one cadence symbol. The reason did not survive being read next to the values, and it became two — `RESCAN_EVERY` and `SUMMARY_EVERY` |
| **Exposed a live name collision** | The new `Call` fields collided with existing `request_bytes` / `response_bytes` integer counts, and compiling the list showed a **third** field was needed that nothing had noticed |

**And one substantive finding that two review passes had read straight past.** `TRAIN_LEVEL` was a
module constant at 9; `compress_level_zstd` was a config key defaulting to 9. Identical values, two
sources, and an operator setting the key to 19 would have silently falsified the sentence the constant
was justified by — scoring candidate dictionaries against an incumbent at a level nothing writes at.
The plan's own conclusion is the best statement of why the instrument works:

> **the defect is invisible until a constant and a config key sit in adjacent columns with the same
> number in them.**

**That is the general case.** A register does not find defects by being thorough. It finds them by
putting values that were written pages apart into adjacent rows, where a human eye does the comparison
for free. Prose review cannot do this at any level of effort, because the prose never places them
together.

## What it costs, honestly

Phase 10's register is about **340 lines in thirteen subsections** against a 1,624-line plan — roughly
a fifth of the document. It was compiled in one pass mid-phase rather than before Task 1, which is
**not** what this rule prescribes: it went in on 2026-08-19, after Group B. Written before the work
starts, as the rule says, it is cheaper — the eight `❓` rows are the plan's own gaps rather than
retrofitted questions about code that already exists.

**The 340 lines are not overhead against the alternative**, which is not "a shorter plan" but "the
same names, scattered, plus the four findings above arriving during implementation or after it."

## Why this is a pointer and not a restatement

**Considered for `CLAUDE.md` on 2026-08-21 and settled as a pointer by the owner**, who had proposed
restating it and chose the pointer when the argument below was put. Recorded with the decider named,
because the reasoning that follows is a recommendation that was *accepted* — not a conclusion this
document reached on its own, and a later session must not read it as one.

`../README.md`'s admission test: *a rule belongs in `CLAUDE.md` when a session would act confidently
and wrongly without it; **a rule you would look up before acting belongs here instead.*** Writing a
phase plan is once per phase and is a deliberate, look-it-up moment — not a reflex a session performs
before anyone can intervene. The precedent settles it: **`IDM-005` and `IDM-006` are not restated in
`CLAUDE.md` either**, and opening or closing a milestone is the same shape of task.

Compare `IDM-001`, which *is* restated, and the reason it earns it: a session merging a branch would
never discover `../reference/branches.md` on its own. That argument does not transfer — a session
writing a phase plan opens the phase template, and the phase template points here.

**So `CLAUDE.md` carries one line naming the trigger, which is what it says a pointer must do.**

## Provenance

- **Instructed by the owner, 2026-08-19**, mid-Phase-10, in the words this rule generalises: *one
  reachable section holding every constant, magic number and new name the phase would implement, so
  they can be checked against the code when the phase is ready.*
- **Generalised into this document 2026-08-21**, on `docs/branch-index`, from the instance rather than
  from the instruction. The instance is
  `../milestone-2-corpus/phase-10-body-store/plan.md`, section "The register — every name and number
  this phase introduces"; its subsections 12 and 13 carry the eight closures and the `TRAIN_LEVEL`
  finding in full.
- **`../README.md`'s phase template points here**, since the moment this applies is the moment
  somebody is writing `plan.md`.
- **n=1.** One phase has run this, and the four findings above are that phase's. The mechanism is
  argued rather than asserted — values in adjacent rows get compared, values pages apart do not — but
  a second phase has not tested it.
