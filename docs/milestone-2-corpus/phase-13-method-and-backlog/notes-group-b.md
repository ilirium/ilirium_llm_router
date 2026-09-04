# Phase 13 — Group B, `IDM-009`

*Tasks 4–6. Written while working.*

## Task 4 — the document, 336 lines

**`../../method/IDM-009-reviewing-executed-work.md`, in force 2026-09-04.** Written from Phase 12's
run rather than from what the protocol seemed like it should be, which is `IDM-006` step 9 and the
reason `review-plan-jobs-done.md` was deliberately not written as an `IDM` in the first place.

**It states only what differs from `IDM-004`.** Everything inherited is named and not restated, so
that a change to the shared method lands in one file. The one place that rule bites is the rules
list, which `IDM-004` says must be **copied into a charter, not cited** — that is about charters,
not about the two `IDM`s, and the distinction is kept.

### The shape decision, made here because task 4 was told to make it

**`IDM-000`'s two-zone split was considered and not used.** It is recommended for a document whose
evidence outweighs its rules; here they are comparable. **The deciding argument is different: this
document's reader arrives holding `IDM-004`, which has no split.** A different shape for the sibling
of a document you are meant to read alongside costs more than the split buys. Recorded in the
provenance section so the next person does not re-decide it silently.

### The admission test was checked, not asserted

`IDM-000`: **no `IDM` contains a fact about the router.** Grepped for the obvious tells. Two hits,
both fine — the phrase *stating* the admission test, and a folder path in the provenance list, which
is what `IDM-004` does too.

**So the first run's findings are described abstractly**: "a defect in existing code that reading a
dependency predicted and only running settled", not the defect itself. A reader who wants the
instance follows the provenance.

## Task 5 — the three questions, closed from their true sources

**This is the task the forward review saved.** It said four questions, all sourced to one file; that
file leaves one open and settles another. See `notes-review-plan.md`, finding C1.

| | Answer |
|---|---|
| **Who "the author" is across sessions** | **Whoever holds the phase's record, declaring its gap by group** — an author run for groups it executed, a **warm read** for groups it did not, labelled per group **in the charter** rather than discovered in the findings. Where no session executed any of it, **there is no author run**, and the two-cold-runs alternative is named as **untried** rather than prescribed |
| **When the subject commit is named** | **The charter names a single commit hash, and each run verifies the subject is unchanged at it before starting.** Not a range in a document written beforehand — that is the defect A5 refused to paper over. Anything landing later is out of scope and named in the reconciliation |
| **What one measurement is worth** | A rule about evidence, not a number. Three runs now: forward **18%** and **17%**, backward **11%**. **What would change the document is a run at materially higher overlap** — half the findings in common would mean one run suffices, and the section would need rewriting rather than defending |

**And the fourth is inherited, not decided.** *The review runs before the merge* is
`review-plan-jobs-done.md` settled row 1, the owner's on 2026-09-02. `IDM-009` records **whose
decision it was** and the argument that was overruled — that the phase stays open longer.

*This phase supplied the third overlap figure while the document was being written, which is why the
table has three rows rather than the two the plan anticipated.*

## Task 6 — the index row and two pointers

- **`IDM-000` index row**, written in the tier's house style: what it adds, what it was measured on,
  and the three questions it answers that `IDM-004` never had to.
- **`CLAUDE.md`**, one line, beside the existing `IDM-004` sentence — **a pointer, not a
  restatement**, per `IDM-000`'s test. It names the trigger and the one thing a session would
  otherwise get wrong: **the review comes before the merge**, so a phase is not merged and then
  reviewed.
- **`../../README.md`'s "The review phase"** gained a three-row table naming all three protocols.
  *The checklist there is the **milestone-scale** one, and the pointer exists to stop it being
  reached for at the wrong scale — which is the confusion `IDM-004` was already written to prevent
  and which a third protocol makes worse.*

### One real broken link, found by running the checker rather than by reading

`notes-review-plan.md` cited `../../CLAUDE.md`, which from a phase folder resolves to
`docs/CLAUDE.md` and does not exist. **Repo-root-relative `CLAUDE.md` is the form that resolves**,
which `link-check.py` supports and which the plan's register already relies on.

**`link-check.py` reports 118 broken on this branch against 91 on `main`.** *Every one of the delta
is a file this phase will create — `IDM-010`, `IDM-011`, `backlog-done.md`, `backlog-index.py` — the
false positive the charter names and `backlog.md` records. The count is also a property of the
worktree, so it is written here with the tree named and is not comparable to a figure taken
elsewhere.*
