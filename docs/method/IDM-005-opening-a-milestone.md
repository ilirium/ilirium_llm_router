# IDM-005 — Opening a milestone

**In force 2026-08-20.** Moved out of `../README.md`, where it was written on 2026-08-16, and given
`IDM-006-closing-a-milestone.md`'s two-zone shape on the same day. The steps themselves are unchanged.

**To open a milestone, read to "End of procedure" and stop.** Everything below that line is evidence:
what each rule cost, and where the frozen record of it is. It is there to be argued with and to be
extended after the next opening. It is not needed to do the work.

Markers like `E3` in the procedure point into that table. Nothing in the procedure depends on them.

---

## The eight steps

The order is the point. Steps 1–3 can each refute what comes after them, and every one of them is
cheaper than the specification it would otherwise invalidate.

### 1. Name the falsifiable central claim, and the non-goals `E1`

**A sentence that could come out false.** A milestone whose claim cannot fail has no gate, and its
phases will each be judged against whatever seemed reasonable that week.

### 2. Run the cheapest experiment that could refute it `E2`

Before specifying anything.

### 3. Capture the real input `E3`

**The highest-leverage step, and the easiest to skip.** Everything else at this stage is reasoning; a
capture is the only step able to contradict the reasoning.

Take real bytes off the real client, not a reconstruction of what the protocol says they should be, and
file them in `../captures/`. Expect them to change the architecture rather than confirm it.

### 4. Spike whatever the architecture depends on `E4`

File each spike straight into `../procedures/` or `../captures/`, as it is written, so it is
re-runnable rather than a memory. A spike that lives only in a session is a measurement the next
milestone pays for twice.

### 5. Settle the expensive-to-reverse questions as EPD forks `E5`

Write them into `../epd/` and answer them explicitly. The test is not how hard the question is — it is
what reversing the answer would cost after three phases have built on it.

### 6. Write the spec, marking every statement measured / inferred / assumed `E6`

And give each assumption **the cheap check that would settle it**.

The marking is the whole of the value. A spec is reliable where it records measurements and unreliable
where it records predictions, and prose puts both in the same voice — so an unmarked prediction reads
exactly like a measured fact to every later session, including the one that wrote it.

### 7. Write `implementation-plan.md` at decreasing resolution `E7`

The next phase in full, the one after in outline, the rest as a title and the question it exists to
close. Detail beyond the next phase is waste, because the plan will be wrong on contact.

The phase written in full gets a numbered **task list** in its own `plan.md`.
→ `../README.md`, **"The unit of work inside a plan is a task"**.

### 8. Open the folder and the branch

→ `IDM-001-git-branching.md` for the prefix, the phase number, and the folder⇄branch slug rule.

---

## End of procedure

*Everything below is evidence. It is not needed to open a milestone.*

## Why each rule is here

Every row happened in this repository, during Milestone 1's opening and the phases that tested it.

| | The rule it supports | What happened | Where the record is |
|---|---|---|---|
| **E1** | The claim must be able to come out false | Milestone 1's was *"no protocol translation is needed, and a local model can drive a real coding session"*. Both halves held, and three things it did not anticipate were established as well — including that a single session reaches both backends at once | `../milestone-1-core/README.md` |
| **E2** | Refute it cheaply, before specifying | **This step is prescribed, not evidenced.** Milestone 1's opening did not isolate one; its plan goes from the claim to Phase 0's skeleton, and the claim was settled by Phase 1's first real relay — after the specification, not before it. It is the one step of the eight with nothing behind it | `../milestone-1-core/implementation-plan.md` |
| **E3** | Capture the real input first | 118,004 bytes of one real request, captured 2026-07-28 for a bare `hi`: **81 KB of tool schemas across 27 tools, 28 KB of system prompt, 368 bytes of conversation.** It carried three body fields nobody had anticipated — `context_management`, `output_config`, `metadata.user_id` — and a full-body Pydantic model would have silently dropped all three. The capture did not inform the architecture, it **changed** it | `../captures/log-the-whole-request.txt`; `../reference/measurements.md`; `../reference/architecture.md` |
| **E4** | File the spike, not the memory | The parity probes became a re-runnable instrument in `../procedures/` rather than a phase-note appendix; vendor behaviour expires, and re-establishing it is then a command rather than a project | `../procedures/README.md` |
| **E5** | Fork the expensive questions | Three were forked inside the opening week — `EPD-001` on 2026-07-30, `EPD-002` and `EPD-003` on 2026-07-31 — and none was answered on the spot. One is **partly accepted**, one is still a proposal, and one was **decided 2026-08-17, a milestone after it was written**. That last outcome is what the fork exists to make cheap: the question stayed answerable instead of being settled early by whoever was typing | `../epd/EPD-000-about-these-documents.md` |
| **E6** | Mark measured / inferred / assumed | `CLAUDE.md` was Milestone 1's spec, and Phase 6 found it almost entirely right — but its errors were patterned: reliable where it recorded measurements, unreliable where it recorded predictions, both in the same prose. It predicted a `role: "system"` message inside `messages` was *"almost certainly unsupported"*; Phase 4 measured it working, and its notes say the claim was wrong when written. Several such predictions were an hour's work to test and stood for five phases | `../milestone-1-core/phase-4-lmstudio-parity/notes.md` |
| **E7** | Plan at decreasing resolution | **Five of seven phases found their own premise wrong** — already built, already measured, or wrongly described. Phase 3 found four of five items already built; Phase 4 a third already measured; Phase 5 two of three options non-existent as described; Phase 6 its premise refuted; Phase 7 eighteen references where it predicted four | `../reference/lessons.md`, lesson 1 |

**One number to take from the table rather than from prose.** `E7` is *five of seven*, and it was
*four of four* until 2026-08-16 and *four of six* in several documents that quoted it. `lessons.md`
carries the canonical count and says why a count in a heading goes stale; anything quoting it
second-hand is worth re-checking rather than repeating.

## What this playbook cannot claim yet

**It was mined from one opening, and that opening did not run it.** The eight steps are the shape
Milestone 1's opening *had* once its archive was read back — not a procedure it followed. `E2` is the
sharp end of that: the step nothing in the record supports.

**Milestone 2's opening did not run it either, deliberately and on the record.** Steps 1–7 were
declared not-run in `../milestone-2-corpus/implementation-plan.md`, with a table saying which and why,
so that a later session would not read their absence as an oversight. Step 3 was the one re-read before
Phase 9, and re-reading it paid.

**So the first genuine test of this document is Milestone 3.** Rewrite it then, from what that opening
costs — appending below the line rather than replacing the steps above it.
