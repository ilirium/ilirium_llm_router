# Milestone 2 — the corpus: implementation plan

**Opened 2026-08-17 on `docs/phase-8-method-and-guardrails`, forked from `main` at `6253cbc`.**

Written at **decreasing resolution**, per the opening playbook's step 7 in `../README.md`: the next
phase in full, the one after in outline, the rest as a title and the question it exists to close.
Plans here are wrong on contact often enough that detail beyond the next phase is waste — four of
Milestone 1's six phases found their own plan wrong on contact.

---

## The central claim is NOT YET NAMED, deliberately

The opening playbook's first step is to name a falsifiable central claim. **It is not written here,
and the blank is the honest state rather than an omission.**

Milestone 2's subject is `../epd/EPD-003-capturing-bodies-for-a-corpus.md`, which was still a
**proposal** when this was written. A central claim written then would have been written against a
document that may not survive its own gate.

*Updated 2026-08-17, Phase 9 Task 4. `EPD-003` is now **partly accepted**: fine-tuning is dropped and
the corpus is for analysis only. **The blank still stands**, because the half that was decided is not
the half a central claim would rest on — the storage question is open until the gate runs, and that is
exactly the document-may-not-survive risk this section was written about.* Milestone 1's spec is the precedent and the warning: it was *"reliable where it recorded
measurements and unreliable where it recorded predictions, with both in the same prose"*, and
several of those predictions stood unchallenged for five phases.

**When it is named:** after EPD-003 is decided and its gate has been run. That is Phase 9.

**What this costs, named rather than waved away:** Phase 8 runs without a milestone-level claim to
serve. That is acceptable only because Phase 8 is housekeeping which would be worth doing under any
claim — it changes no `src/` and settles conventions the milestone will use whatever it decides. **A
phase that shapes the router must not start before the claim exists.**

**Non-goals:** not yet named, for the same reason.

---

## The phases

### Phase 8 — the method tier and the guardrails *(in full)*

`phase-8-method-and-guardrails/plan.md`, beside this file. **Seventeen tasks in three groups** of
housekeeping, each of which blocks cheap work later and none of which depends on EPD-003:

1. **The Git branching rules are in two documents and they disagree** — seven differences. Unified into
   one numbered method document, `docs/method/IDM-001-git-branching.md`, cited from both. This also
   establishes the `docs/method/` tier and the **IDM-NNN** numbering scheme in `IDM-000`.
2. **A tracked `.claude/settings.json`.** `EPD-004` decision 17 split the permission allowlist into
   a tracked policy half and an untracked local half, and only the local half existed. Interviewed and
   settled 2026-08-17; `IDM-002` holds the reasoning.
3. **Two tooling decisions with no home** — the ruff pin, and `ty`, which was tried and refused with the
   refusal recorded nowhere. `IDM-003`. This group emerged from group B's review rather than being
   planned.

**Done when:** the tier holds `IDM-000` through `IDM-003` and no `README.md`; the branching rules have
exactly one home, with `CLAUDE.md`'s restatement labelled as one; the tracked settings file exists with
an exact-match `.env` deny and its sibling ignored by *this* repository's `.gitignore`;
`procedures/link-check.py` reports only its known-permanent hits, re-derived by running it; and
`make test` still reports 158.

*This section said "two small pieces of housekeeping", that the settings half was "not yet specified —
the owner has not been interviewed on it", and that Phase 8 was done when "both documents exist". All
three were true when written on 2026-08-17 and false by the end of the same day. Corrected in place at
Task 17a, which the plan did not contain — the phase's own re-derivation found it.*

### Phase 9 — decide EPD-003, and run its gate *(in full)*

`phase-9-corpus-gate/plan.md`, beside this file. **Sixteen tasks in four groups**, on
`docs/phase-9-corpus-gate` — a `docs/` prefix because no `src/` change survives the phase.

**The question it closes:** does the corpus proposal survive its own cheapest test?

*Raised from outline to full on 2026-08-17, when the phase opened. The two halves below are what this
file said then, and both still hold — but the outline **understated the first**, which is Finding 1 of
the phase's re-derivation.*

Two halves, in this order:

- **The gate — a twenty-minute measurement.** Whether a trained zstd dictionary recovers the
  cross-body compression ratio for per-file storage. **If it does not, per-call files are the wrong
  unit and the sketch does not survive.** Stated in `../backlog.md` and argued in EPD-003.
- **The decision the gate cannot make.** Whether the fine-tuning half of the goal survives
  Anthropic's terms. That is a person's call, not a measurement's, and the corpus may be worth
  building for analysis alone even if fine-tuning is cut. **Taken 2026-08-17: fine-tuning is dropped,
  analysis only.** The last clause of that sentence is what happened.

**The milestone's central claim is written at the end of this phase**, from what the gate returned.

*Everything below Phase 9 is a title and a question. Nothing about it is planned.*

### Phase 10 — *unnamed*

**The question it exists to close:** what does the router store, and where. Only answerable once
Phase 9 has said whether per-call files are the unit.

### The closing review phase — *unnamed, number unallocated*

Every milestone closes with one, specified as measurement rather than removal; the checklist is in
`../README.md`. It touches `src/`, so it is a numbered `feat/` phase. **Its number is not allocated
here** — phase numbers are globally sequential and how many phases sit between Phase 9 and the close
is not known.

---

## What is deliberately not done yet

The opening playbook has eight steps. **Steps 1–7 are not run**, and this section exists so that a
later session does not read their absence as an oversight.

| Step | State |
|---|---|
| 1. Name the falsifiable central claim, and the non-goals | **deferred to Phase 9** — see above |
| 2. Run the cheapest experiment that could refute it | deferred; it *is* Phase 9's gate |
| 3. Capture the real input | **NOT discharged** — settled 2026-08-17 by Phase 9's re-derivation. `docs/captures/` holds **one** body, and one body cannot exercise a cross-body dictionary. Phase 9's Group B spends it |
| 4. Spike whatever the architecture depends on | not started |
| 5. Settle the expensive-to-reverse questions as EPD forks | **EPD-003 already is one.** Whether it needs a sibling is unknown |
| 6. Write the spec, marking every statement measured / inferred / assumed | not started |
| 7. Write `implementation-plan.md` at decreasing resolution | **this file, partially** — Phase 8 in full, Phase 9 in outline, the rest as titles |
| 8. Open the folder and the branch | **done** — this folder, and `docs/phase-8-method-and-guardrails` |

**Step 3 was the one worth re-reading before Phase 9**, and re-reading it paid. The playbook calls it
the highest-leverage step and the easiest to skip, and Milestone 1's capture *changed* the
architecture rather than informing it.

*Settled 2026-08-17. It is **not** discharged, and the hedge above was right to exist. `docs/captures/`
holds one 119 KB request; the frozen CSV holds body lengths and no bodies; the probe bodies are
synthetic and under a kilobyte. **The consequence is that the gate is not the twenty-minute measurement
this plan and `EPD-003` both call it** — it is a live capture session plus twenty minutes of `zstd`.*

---

## Record

| | |
|---|---|
| Branch | `docs/phase-8-method-and-guardrails` |
| Fork point | `6253cbc` |
| Merge commit | `22a6d20` — merged 2026-08-17 with `--no-ff` |

*A `Merge commit` row that still says "not yet merged" after the branch is gone is this
repository's signature failure — four of Milestone 1's six phase notes did exactly that. **Closed out at
the merge, 2026-08-17.** The permanent record is the phase note, per
`../method/IDM-001-git-branching.md`; this row and the plan's repeat it because a merge hash is immutable
and therefore cannot drift, which is what the one-home rule is protecting against.*

*This table records the branch **this file** was created on. Milestone 2's opening shared Phase 8's
branch, which is why the two Record tables carry the same three values.*
