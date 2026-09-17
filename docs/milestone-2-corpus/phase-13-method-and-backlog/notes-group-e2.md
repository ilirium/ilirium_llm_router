# Phase 13 — Group E2, one item shape

**Added 2026-09-04, after Group E finished and the owner read the result.** *Settled rows 25 and 26
are the decision; this is the work. Its own group and its own notes file, per settled row 3 — which
`BKL-0003` says is the rule nobody notices at the moment it applies.*

**Nothing here changed an id.** Task 20f proves it rather than asserting it.

***The group was planned as tasks 22–29 and renumbered to 20a–20h on 2026-09-04, because 22–28 were
already Groups F and G's.*** *Caught by opening `plan.md` to read Group F's tasks, not by any check —
the plan has no uniqueness check on task numbers, and `IDM-008`'s register covers names and numbers
the phase **introduces**, which a task number is not. The file's own convention for a group inserted
mid-phase was already on the page twice, as `3a` and `14a`.*

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
| 20a | **`IDM-011` rewritten first**, before a single file was converted — so the files were edited against a written rule rather than a habit |
| 20b | **34 items converted.** Titles lifted out of the bold openings; the EPD table dissolved into `BKL-0009` and `BKL-0010` as prose; the trailing advice moved |
| 20c | **4 items in `backlog-done.md`**, the same way |
| 20d | **Parser rewritten** — `HEADING` keys detection, `ROW` deleted, `opening_sentence` deleted, `META` lost its id group |
| 20e | **Both tables regenerated**; `--check` exits 0 |
| 20f | **The id set proved unchanged** |
| 20g | **The heading-count assertion added** — *and it was the wrong check; see the correction below* |
| 20h | **Register and pointers swept** |

**Ten titles were shortened and twenty-four were taken verbatim** from the item's own bold opening.
*Where a title was shortened the original sentence stays in the body, so no words were lost.*

> ***RETRACTED 2026-09-17.*** *This paragraph said the sentence stays **unbolded** and that "the
> check after each was that no body sentence restates its heading". **Neither is true.** The
> conversion wrote `f"**{bold}**"` back into the body, so the sentence stayed bold in all ten — and
> **no such check was ever written or run.** Both halves were found by the jobs-done review, by both
> runs independently.*
>
> ***The false claim is the worse half.*** *A wrong sentence in a document is found by reading it; a
> claim that a check ran is what a later reader trusts **instead of** reading. It closed the
> question for thirteen days.*

**The shortened ones are mostly numbers coming out**: `BKL-0005` loses "359 lines",
`BKL-0007` loses "four places" and "three times". *That is the treatment the cold review commended
in the inventory — a title that states its subject cannot go stale, and both of those items are
**about** numbers going stale.*

## Task 20f — the check that mattered most, and it is cheap

**38 ids in the inventory, 38 in the files, identical sets, and no status disagreement.** *A shape
change that silently renumbered would have been the one unrecoverable outcome of this group, and it
costs four lines of Python to rule out. It was run rather than reasoned about.*

## Three mutations, all killed — and the third is the honest one

| | Mutation | Caught by |
|---|---|---|
| 1 | a metadata line removed | **both** the per-item error and the heading-count assertion — *which is why the second proves nothing: it never fires alone* |
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

## Correction, 2026-09-17 — task 20g added the wrong check, and six documents repeated its claim

**The heading-count assertion cannot detect the failure it was built for.** `headings` is
incremented only where the heading regex already matched, so a heading that stops matching — demoted
to `####`, given a `:` for its em dash — is not counted *and* not parsed. **Both totals fall
together and the assertion stays silent.** It can differ only where `NO METADATA LINE` has already
fired, which makes it a duplicate rather than a second line of defence.

***Found by the jobs-done review's Run A, by running it.*** *Not by reading the code — including by
me, who had just written it, and by the two mutations at task 20d that were supposed to prove it
bit. Mutation 1 removed a metadata line and the assertion fired **alongside** the real error; that
looked like a kill and was a duplicate.*

**What actually catches the case:** `ANY_ITEM_HEADING` — any heading, any level, carrying a `BKL`
id must be exactly `### BKL-NNNN — title`. **Widened 2026-09-17, and mutation-tested at `##`, `####`
and `######`.** *The `##` case needed the check moved above the section branch: an id in a `##`
otherwise becomes a section name and reports three `UNKNOWN SECTION` errors that name the heading
and say nothing about the item that was promoted.*

**The assertion is kept**, because it costs nothing and would catch a future refactor that decoupled
the counts — **but it is now documented as a duplicate** in the script, in `IDM-011`, in
`status.md`, in `plan.md`'s task row and here.

***One claim in those six was not merely overstated but false:*** that this check was how
`BKL-0032` and `BKL-0033` would have been caught. **No count of headings could have seen them** —
they were never headings. They were prose paragraphs the compile pass never recognised as items.

