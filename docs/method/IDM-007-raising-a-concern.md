# IDM-007 — Raising a concern where it will be read

**In force 2026-08-21.** `CLAUDE.md` restates the rule in its Working agreement — see "The
restatement" below; this file is canonical and a change goes here first.

---

## The rule

**A question, a concern, or something found wrong goes in its own sentence, where it will be read
first.** Not inside a long description, not in paragraph nine of a report, not as a subordinate clause
in a sentence about something else.

Three parts, and they fail independently:

| | The rule | The failure it names |
|---|---|---|
| **Placement** | It goes where the reader arrives, not where it happens to fit the narrative | A concern in the middle of a long report reads as commentary and gets skimmed |
| **Plainness** | If something is wrong, say it is wrong — do not work around it | Silently routing around a defect leaves the defect, and hides that a decision was made |
| **Answerability** | An question carries the detail needed to answer it and the options visible from here, each stated so it can be chosen between without reconstructing the problem | A question that requires the reader to re-derive the situation is a second task, not a question |

**A concern raised where it will not be read has not been raised.** That sentence is the whole rule;
the rest of this document is why it needs saying and what it does not license.

## Placement is the rule, not the polish

The instinct is that raising a concern is about *content* — did you mention it or not — and that
placement is presentation. **This project has already established the opposite, in writing, about its
own documents**, and this rule is that finding applied to the report rather than the file.

`IDM-000`'s two-zone section names the hazard in its own tier:

> **A caveat that qualifies a rule is invisible if it lives only in that rule's evidence row.**
> `IDM-005`'s step 2 was exactly that — the one step with nothing behind it, and its disclaimer sat
> below the line where a session following the stop instruction would never reach it. **A rule that
> needs a caveat gets it above the line, or it stops being a rule.**

The disclaimer was written. It was accurate. It was in the file. **And it did not function**, because
it sat where the reader who obeyed the document's own instruction would never arrive. Nothing about
its content was at fault.

The same shape is recorded twice more here, both times about prose rather than about a person:

- `../status.md` records that **a sentence that undercounts goes stale invisibly, where a missing
  table row would be visible.** Twice — the second time to the very paragraph that described the
  first.
- `IDM-001-git-branching.md` records Phase 9 filling in three `Merge commit` rows and
  **leaving the prose four lines above one of them saying the work was unfinished.** The owner found
  it. The session had read the rule during the phase.

**Three independent instances, one mechanism: something true, written down, in a place that does not
reach the reader.** A concern buried in a long description is the same defect with a person in the
place of a document.

## "Say it is wrong" — the part that is about nerve, not format

Working around a defect is the tempting move, because it produces a result and the result looks
finished. It costs two things at once: **the defect survives**, and **a decision was made without
anyone noticing it was a decision.** The second is the expensive half — a workaround is a choice about
the shape of the work, and choosing it silently takes it away from whoever should have made it.

This is `../README.md`'s existing principle pointed at the report rather than at the archive:

> **Refusals are first-class outcomes.** Recording that a cut was considered and refused, with the
> measurement, is what stops the same cut being re-proposed every milestone by the next person
> reading the same surface signal.

A found-and-worked-around defect is a refusal that nobody recorded.

**Stating a disagreement is inside this rule, not an exception to it.** Where a recommendation runs
against what was asked for, the disagreement is stated as a disagreement and the reasoning given,
and then — if the instruction is repeated — the instruction wins and the work is done in full. The
rule is about the concern being *visible*, never about it being *obeyed*.

## What this does not license

**It is not "ask about everything".** `CLAUDE.md`'s working agreement is unchanged: routine judgement
calls are made, not escalated, and a question is worth asking when different readings would lead to
materially different work. **This document governs *how* a concern is raised, not *whether* an
uncertainty becomes one.** A rule that turned every uncertainty into a question would make the reports
unreadable and would bury the real concerns among the manufactured ones — which is this rule's own
failure mode, arrived at from the other direction.

**It is not a licence to stop.** Everything that does not depend on the answer gets done while the
question is open. Blocking — delivering nothing until an answer arrives — is for the case where
proceeding under any assumption would be unsafe or would waste the work if wrong.

**It does not make length a defect.** A long report is fine. What is not fine is a long report whose
one load-bearing concern is discoverable only by reading all of it. The fix is placement, not
brevity — the same conclusion `../wiki/claude-code-context-budget.md` reaches about reading:
*the fix is reading it by section, not reading less of it.*

## The restatement

`CLAUDE.md`'s Working agreement carries this as a fourth bullet, because it governs behaviour from
the first message of a session and there is no moment at which someone would look it up first — the
moment it applies is the moment they are already writing.

**That is a second copy of a fact, and the direction of truth is written into it**: `CLAUDE.md` says
it is restated from here. `IDM-000` accepts a restatement on exactly this test and requires exactly
that label.

## Provenance

- **Instructed by the owner, 2026-08-21**, on `docs/branch-index`, as one of four method items added
  together. The wording of the rule is the owner's; the evidence tying it to `IDM-000`'s two-zone
  hazard and to the two `status.md` instances was assembled here.
- **The three instances cited above predate it** and were found by looking, not supplied. That is the
  argument for the rule being in force rather than proposed: the failure it names has already happened
  three times in this repository, each time to a document rather than to a person, and each time it
  was found by the owner rather than by any check.
