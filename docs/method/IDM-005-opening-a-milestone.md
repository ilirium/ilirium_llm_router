# IDM-005 — Opening a milestone

**In force 2026-08-20.** The playbook is **moved here unchanged** from `../README.md`, where it was
written on 2026-08-16 — this document is a relocation, not a new rule. `EPD-004` decision 12 put both
playbooks in the manual; the addendum at that decision records why they left and why the escape hatch
it named was not the one taken.

**Read this and work from it rather than improvising.** That instruction is the point of the document,
and `CLAUDE.md` carries it too: this is the one pointer whose omission costs a whole milestone's worth
of harvest. A procedure used twice a year is one nothing in a session's head will supply.

The closing half is `IDM-006-closing-a-milestone.md`.

---

## The playbook

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
4. **Spike whatever the architecture depends on**, filing each spike straight into `../procedures/` or
   `../captures/` so it is re-runnable rather than a memory.
5. **Settle the expensive-to-reverse questions as EPD forks**, and answer them explicitly.
6. **Write the spec, marking every statement measured / inferred / assumed**, and give each assumption
   the cheap check that would settle it. Milestone 1's spec was reliable where it recorded measurements
   and unreliable where it recorded predictions, with both in the same prose — several predictions
   were an hour's work to test and stood for five phases.
7. **Write `implementation-plan.md` at decreasing resolution** — the next phase in full, the one after
   in outline, the rest as a title and the question it exists to close. Plans here are wrong on
   contact often enough that detail beyond the next phase is waste. The phase written in full gets a
   numbered **task list** in its own `plan.md`; see `../README.md`'s "The unit of work inside a plan is
   a **task**".
8. **Open the folder and the branch.** → `IDM-001-git-branching.md` for the prefix, the phase number
   and the folder⇄branch slug rule.

---

## The router facts in this document, and why they are here

Steps 1, 3 and 6 quote Milestone 1 — a central claim about protocol translation, 118 KB of captured
request bytes, a spec that was right where it measured and wrong where it predicted. `IDM-000`'s
admission test says **no IDM contains a fact about the router**, and these are quotations of router
facts, so the line is worth stating rather than leaving to be noticed.

**None of the eight rules depends on one.** Delete every quotation and the playbook still reads: name a
falsifiable claim, refute it cheaply, capture the real input before specifying, spike, fork the
expensive questions, mark the spec's confidence, plan at decreasing resolution, open the folder. What
the quotations supply is `IDM-000`'s other half — *evidenced from this repository*, so that a rule can
be argued with rather than only obeyed. A capture that changed an architecture is why step 3 is ranked
highest-leverage; without it, step 3 is an assertion.
