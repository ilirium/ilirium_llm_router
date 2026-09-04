# Phase 13 — Group E2, one item shape

**Added 2026-09-04, after Group E finished and the owner read the result.** *Settled rows 25 and 26
are the decision; this is the work. Its own group and its own notes file, per settled row 3 — which
`BKL-0003` says is the rule nobody notices at the moment it applies.*

**Nothing here changed an id.** Task 27 proves it rather than asserting it.

---

## What the owner found, and it was four things with three causes

**Items were not headings.** `IDM-011` defined an item as *"something carrying a metadata line"* — a
deliberate choice so the parser never guesses a boundary, but it meant **fitting the scheme to the
file** and inventing three shapes to cover what was already there.

**`Decisions waiting on a person` was a table.** Written 2026-08-16 as a *comparison* of three EPDs,
before ids existed. **Task 15 made it worse**, adding four metadata columns so it stood seven wide —
while `BKL-0011` had already moved to `backlog-done.md` **as prose**, so the two files disagreed
about one item type.

**Paragraphs belonged to no item — three kinds, and only one was a defect.** File preamble and
section preambles are legitimate and headings make them visibly non-items for free. **The defect was
the trailing advice at the end of `Measurements left open`** — *"Before planning any of these, grep
the frozen artefacts first"* — which is about all six items and sat **after the last one**, so it
read as part of `BKL-0017`. **Moved to that section's preamble.**

## The retired shapes are the ones that hid two items

**Two of the three shapes had no structural marker at all**, so an item opening with a bold sentence
was indistinguishable from a continuation paragraph opening with one. That is why `~~**` versus
`**~~` decided whether the compile pass could see an item, and why `BKL-0032` and `BKL-0033`
survived a compile, an author review and two forward-review passes.

***The shape was not a presentation choice that happened to have a defect. It was the defect.***
*Settled row 21 is struck rather than deleted for that reason: the row states the cost as "the
script learns three shapes rather than one", which was true and was not the price actually paid.*

## What was done

| Task | |
|---|---|
| 22 | **`IDM-011` rewritten first**, before a single file was converted — so the files were edited against a written rule rather than a habit |
| 23 | **34 items converted.** Titles lifted out of the bold openings; the EPD table dissolved into `BKL-0009` and `BKL-0010` as prose; the trailing advice moved |
| 24 | **4 items in `backlog-done.md`**, the same way |
| 25 | **Parser rewritten** — `HEADING` keys detection, `ROW` deleted, `opening_sentence` deleted, `META` lost its id group |
| 26 | **Both tables regenerated**; `--check` exits 0 |
| 27 | **The id set proved unchanged** |
| 28 | **The heading-count assertion added** |
| 29 | **Register and pointers swept** |

**Ten titles were shortened and twenty-four were taken verbatim** from the item's own bold opening.
*Where a title was shortened the original sentence stays in the body, unbolded, so no words were
lost — settled row 26's rule, and the check after each was that no body sentence restates its
heading.* **The shortened ones are mostly numbers coming out**: `BKL-0005` loses "359 lines",
`BKL-0007` loses "four places" and "three times". *That is the treatment the cold review commended
in the inventory — a title that states its subject cannot go stale, and both of those items are
**about** numbers going stale.*

## Task 27 — the check that mattered most, and it is cheap

**38 ids in the inventory, 38 in the files, identical sets, and no status disagreement.** *A shape
change that silently renumbered would have been the one unrecoverable outcome of this group, and it
costs four lines of Python to rule out. It was run rather than reasoned about.*

## Three mutations, all killed — and the third is the honest one

| | Mutation | Caught by |
|---|---|---|
| 1 | a metadata line removed | **both** the per-item error and the new heading-count assertion |
| 2 | a heading written `### BKL-0014: …` instead of `— ` | the malformed-heading check, plus the citation check |
| 3 | an item cut out entirely | **the citation check — and only by luck** |

**Mutation 3 is recorded as a gap rather than a pass.** It was caught because the generated table
had not been regenerated and still cited the deleted id. **Regenerate first and nothing catches
it** — the heading goes with the item, so there is nothing left to count. *Written into `IDM-011`'s
"what `--check` cannot see" section, with the trade named: closing it needs a manifest of every id
ever issued, which is a second copy of what the ids already are.*

## Two things this group did not do

**`docs/procedures/`'s 36 ruff findings.** Older than this phase and not its subject. **The rewrite
added none** — `backlog-index.py` still reports exactly the one pre-existing `RUF007`.

**The section order, the categories, the statuses, or any id.** Settled rows 4 and 24 stand.
