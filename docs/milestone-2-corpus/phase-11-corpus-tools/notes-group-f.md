# Phase 11 — Group F: verify, harvest and close

**Tasks 22–25.** The register check; mutation testing on the converter; the harvest into
`reference/`; and the merge.

**Tasks 22, 23 and 24 are complete, 2026-08-28. Task 25 — the merge — is not run.** It is the one
outward-facing, hard-to-reverse step in the phase and it waits on the owner.

---

## Task 22 — the register check, which found something on its first run

**`evidence/register-check.py`: 89 checks, 0 failed**, and it exits 1 so it can be a gate rather than
a report. It checks what a machine can — every module the register names exists, every value it
states is the value in the code, the CLI spells its subcommands and flags as written, the four struck
flags are absent, the index is 26 columns in the printed order, all five sentinels match including
`STORE_ERROR` whose constant name and disk value differ — **and that no `❓` is left in a cell.**

**It failed on its first run, and two `grep`s had said otherwise.** A `❓` survived — not a live
placeholder but a *reference* to one, in prose reading *"the `❓`'s requirement is met"*.

**Reworded rather than taught to the checker.** A symbol that sometimes means *unvalued* and
sometimes means *the thing formerly unvalued* is a symbol whose check cannot be trusted in either
direction. *This is the third instance in this phase of the same shape: `IDM-008`'s own closing task
was written against a column that does not exist, and the forward review found it. The instrument
keeps catching its own family of defect.*

**Mutated four ways** — a constant drifted from its stated value, a constant renamed, a `❓` reopened,
an SSE event dropped — and caught all four. *One of the four did not apply cleanly the first time and
was rerun rather than counted as a pass; an unapplied mutation reads exactly like a killed one.*

**What it cannot check is prose.** A row whose *description* has drifted still passes, so the closing
task is the script **and** a read, and the docstring says so where somebody will meet it.

---

## Task 23 — systematic mutation, and it is not what the per-task mutations were

**279 mutants over `transcript.py` and `jsonl.py`; 174 killed, 105 survived.** After the fixes:
**277 mutants, 202 killed, 75 survived.**

### Why the per-task mutations did not already answer this

**23 targeted mutations were run across tasks 12, 13, 16 and 17**, each aimed at a named guarantee,
each with a no-op control. **All 23 died and not one was a surprise** — every one had been chosen
*because* a test was expected to catch it.

**That is a check on the suite's responsiveness and it cannot produce a survivor.** The distinction
worth carrying: **targeted mutation tests the tests you wrote; systematic mutation tests the tests you
did not.**

### The honest denominator, because "105 survived" overstates it

| Category | Count | A defect? |
|---|---|---|
| **A** · error-message wording | ~24 | **No.** The harness mutating `"was"`/`"were"`, in text nothing asserts |
| **B** · self-referential tests | ~12 | **Yes, and systemic** |
| **C** · dead code | ~9 | **Yes** |
| **D** · missing tests | ~12 | **Yes** |

**Category A is parked in `../../backlog.md`, on the owner's decision.** A test for each would pin an
error message's grammar — churn dressed as coverage, and the message could then not be improved
without a test change. *It is recorded rather than dropped because the count also measures the
harness: an operator that rewrites every string constant will always produce these.*

### B — a test can compare the code to itself

```python
assert len(key) == CONVERSATION_KEY_CHARS   # cannot fail
```

**Twelve assertions did this** — every skip reason, both on-disk subtypes, the gap reason, the key
length. Change the constant and both sides move together. **Nothing but a mutation sweep finds
these**, because they read exactly like coverage. Where a literal is the contract, the test now
writes the literal.

### C — dead code, both kinds

**`SSE_EVENTS` is read by nothing in `src/`.** Eight mutants survived by changing names no code
consults: `_events` takes each payload's own `type` and ignores the `event:` line entirely.
**Kept, because the eight are measured** — but the comment now says plainly that it is *a record, not
a guard*, and a test pins the literals so it cannot rot. **A reader must not take it for validation:
an unlisted event is passed over, not rejected.**

**And an unreachable `default=`.** `_attach_orphans` fell back to `host.depth - 1` for an empty
`entries`, which cannot happen. **Deleted rather than kept defensive**: if the invariant ever breaks,
`max` raising is better than a silently wrong position — which is exactly what produced task 13's
duplicate `uuid5`.

### D — the one that mattered most

**`isMeta=False → True` survived on the fidelity note.** From the viewer's source, a record with
`isMeta: true` is **skipped**. That record's entire job is to say *"this is NOT a Claude Code session
record"*.

**A hidden marker is worse than no marker**: the file then reads as a real transcript with nothing to
contradict it. Nothing asserted the field until the sweep. Also added: `isSidechain`, the gap count
reaching the note, empty and non-list `messages`, an SSE stream with **no `event:` lines** — which the
module claims to tolerate and, per the mutation, quietly depended on — and the skip counters.

***And one existing test was passing for the wrong reason.*** The shrink test survived `<` → `>=`:
the first call compares against an empty spine, so the mutant counted 1 there and 0 later, reaching
the same total by a different route. **A green assertion on the right number, arrived at wrongly.**

### What is left, and why it is not alarming

**All five real logic survivors are dead.** The four logic mutants that remain are singular/plural
grammar inside error strings, and ~43 of the 75 are string mutants of the same kind. The rest are
equivalent mutants: `@dataclass(frozen=True)` where no test mutates an instance, `ensure_ascii` where
no fixture is non-ASCII, and `event.get("index", 0)` defaults that real streams always supply.

### The sweep nearly destroyed what it was measuring

**The first run was killed by a timeout, and `finally` does not run on `SIGTERM`.** It left
`transcript.py` as `ast.unparse` output: behaviour identical, **every comment stripped, 256 of 670
lines gone, and the suite passing 427/427.** Nothing raised. Nothing failed. **`git status` caught
it.**

Given this repository's comment density is deliberate and was defended by measurement in Phase 6,
that is a real loss that would have landed behind a green check.

**The harness now has three restore paths and they were tested by killing a run on purpose**: a
sidecar written before each mutation, `SIGTERM`/`SIGINT` handlers, and a refusal to start when a
stale sidecar is found. **An instrument that edits the thing it measures needs a restore that
survives being killed**, and `try/finally` is not one.

---

## Task 24 — the harvest

**`reference/measurements.md`** gains a Phase 11 section — thirteen rows, each with its slice, all
against the corpus frozen at **2026-08-26T15:16:22Z**. The rows that will be quoted most are the ones
that only make sense together: **902 + 66 + 11 = 979**, which is what demonstrates exact matching,
and **0/76, 46/76, 0/76, 65/76**, which is what shows one of the two normalisations does nothing on
its own.

**`reference/lessons.md`** gains three things, none of them a new lesson — which is the point.

- **§1 gains a sixth form**: a requirement whose *justification* stopped being true while the
  requirement stayed right. The missing-day error's stated failure mode cannot occur in the design
  that was built; the error was kept and the reason rewritten in place. **A stale justification is
  more dangerous than a stale number, because it survives the review a number would fail.**
- **§7 gains two instances**, including the sharpest form the "check that cannot fail" family takes:
  a test that compares the code to itself.
- **§8 gains a third practice**: targeted versus systematic mutation, with the numbers from this
  phase — 23 targeted, all killed, none surprising, against 5 real defects the sweep found.

*Nothing was added to §3 or §4 as a new lesson. Every one of this phase's failures was an instance of
something already written down — which is either evidence the file is complete, or evidence that
writing a hazard down does not stop it recurring. **Both readings are supported by this phase**, and
the second one is recorded in `notes-group-d.md` where three hazards repeated within 48 hours of
being logged.*
