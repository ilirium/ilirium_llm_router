# The item inventory — the author run

**Run 2026-09-04, by the session that wrote the inventory.** *At the owner's request, against a
session budget that would not stretch to a fresh-context run.*

---

## Read this before the findings: what this run structurally cannot do

**This is an author run. It is not the review `item-inventory-review-charter.md` was written for**,
and that charter is **not** discharged by this file.

`IDM-004`'s split is that the author asks *is this consistent with what was decided, and is what it
claims true*, and the cold reader asks what the author **cannot un-know**. The charter's two
highest-value checks are both on the cold side:

| Check | Why an author cannot do it |
|---|---|
| **Derive the count independently *before* reading the inventory's answer** | I cannot unsee 36 |
| **Find a seventh boundary the pass did not flag** | The six flagged are the six I found doubtful; a seventh is by definition one I read straight past |

**What an author run can do is everything mechanical**, and that is what follows. *The mechanical
half turned out to hold most of the defects — which is a fact about this artefact, not a general
claim, and is the opposite of what the last three reviews here found.*

---

## Findings

```
[VERIFIED]  Four more line numbers are wrong, each off by one. Five of thirty-three in total.
  Where:    item-inventory.md, rows BKL-0003, BKL-0004, BKL-0006, BKL-0007
  Evidence: Checked every cited line in `backlog-before-ids.txt` for two properties an item
            opening must have — a blank line above it, and a bold or `###` start.
            Four failed: BKL-0003 cited 121, opens at 122. BKL-0004 cited 176, opens at 175.
            BKL-0006 cited 205, opens at 206. BKL-0007 cited 265, opens at 266.
            **Two are one too high and two are one too low**, which rules out a constant offset
            and points at the extraction being done twice by different means.
  Permanence: correctable. Corrected in place, and the inventory now says five rather than one.
```

```
[VERIFIED]  No item was missed. The count of 36 holds and the six boundary calls are right.
  Where:    backlog-before-ids.txt, all eight sections
  Evidence: Enumerated every paragraph opening in the file — bold or `###`, preceded by a blank
            line — and subtracted the 33 the inventory claims. **28 remained.** Every one is
            accounted for: four are the file's own preamble, one is a section preamble, one is
            the section-level advice at line 394, four are the corrected openings above, and
            **eighteen are continuations** of items already claimed — the four evidence
            paragraphs under `BKL-0029` and the rest singly.
  Permanence: this is the finding that matters most, and it is the one an author is least
            entitled to be believed on. **A cold run should redo exactly this.**
```

```
[REPORTED]  Three of the eleven "undated" items may carry a date the pass did not look for.
  Where:    item-inventory.md, rows BKL-0024, BKL-0029, BKL-0035
  Evidence: A regex for Added/Proposed/Narrowed/Named/Overturned over each item's body found
            `Narrowed 2026-08-17` near BKL-0024, `Added 2026-09-02` near BKL-0029, and
            `Overturned 2026-08-24` in BKL-0035. **None is confirmed to belong to the item it
            sits near** — the scan's item boundaries were approximate, and two of the three
            plausibly belong to a neighbouring paragraph.
            BKL-0035 is the interesting one: its own text says *overturned* 2026-08-24, which is
            when it stopped being a refusal, **not when it was added.** Recording `—` may be
            right and is at least defensible.
  Permanence: correctable, and it does not touch an id.
```

```
[REPORTED]  The reverse status check ran with a faulty boundary set and its result is unusable.
  Where:    this run's own method
  Evidence: The check asks the charter's best status question — *is any item marked `open`
            actually finished?* It returned seven hits. On inspection the item-boundary list it
            used omitted the non-`open` items, so several bodies ran into the following item and
            matched language belonging to a neighbour. **At least one hit is provably its own
            bug**: `BKL-0001`'s body swallowed `BKL-0002` and matched the word "discharged" in
            it.
  Permanence: **nothing is concluded from it.** The question is open and the cold run must ask
            it properly. *Recorded rather than dropped, because a check that ran and proved
            nothing looks identical to one that ran and found nothing.*
```

## Questions

**1 · Is `BKL-0004` `done`, or `partly-done`?**

It asked for three things and all three exist — an id scheme, an allocation rule surviving deletion,
a checker. **But no id has been applied to `backlog.md`**, and the item's subject is the file, not
the scheme. *`done` is a claim about the work; today the work is designed and not applied.* It
becomes unambiguously `done` when task 15 lands, which is days away at most. **What it would change:
one status, and whether the item sits in `backlog.md` or `backlog-done.md` when the refactor runs.**

**2 · Does `BKL-0036` deserve an id at all?**

Raised in the inventory and unchanged by this run — *"everything struck through in another file"* is
a pointer rather than a piece of work. **It remains the cheapest id to drop.**

## What was checked and found correct

- **Ids ascend, are unique, are correctly formatted, and no id is reused.** Mechanical, and clean.
- **Eight of the eleven undated items are confirmed undated** — no date string of any recognised
  form appears in their bodies.
- **The three item shapes are confirmed** across all eight sections, and no fourth exists.
- **The section→category mapping is total**: every item's section is one of the eight, and the eight
  are exactly the file's `##` headings.

## What this run did not reach

- **The one-line descriptions were not checked against their items.** The script generates them from
  the item's own opening sentence, so the failure mode is a wrong *line number* rather than a wrong
  description — and that is finding 1, now corrected. But nobody has read the 36 descriptions
  against the 36 items.
- **The three table-row items in `Decisions waiting on a person` were not re-read.** They were taken
  from the inventory as given.
- **Everything on the cold side of the table at the top.**

**So the charter still stands and should still be run.** *This run found five wrong line numbers and
proved nothing about the question those numbers exist to support.*
