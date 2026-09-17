# Charter — reviewing the backlog item inventory

**Hand this to a fresh-context agent, verbatim, in a session of its own.** It is written to be read
by somebody who knows nothing about this repository, so it repeats what it needs rather than
pointing.

**Written 2026-09-04.** *`method/IDM-004-reviewing-unexecuted-work.md` calls this a charter and says
why one exists: **a reviewer told "review this" verifies what is easy to verify and returns a tidy
list that misses the thing that matters.** So this document decides what the review finds.*

---

## Read this first: what is going on

`docs/backlog.md` is an inventory of unscheduled work — about three dozen items, each a few
paragraphs, saying what the work is and **why it is parked**. It has no identifiers. Items are cited
today by quoting their opening phrase, and **a quoted title is not an identifier**: editing a title
silently breaks every citation of it and nothing notices.

**A phase is giving every item a permanent id, `BKL-NNNN`.** A pass over the file has produced a
proposed inventory: 36 items, each with an id, a category, a status, a date and a one-line
description. **Nothing has been applied to `backlog.md` yet.**

**Ids are permanent once applied — never reused, never renumbered.** That is why this review exists:
**a wrong boundary or a missed item freezes a wrong id into a scheme whose whole premise is that ids
never change.**

## The two files

| | |
|---|---|
| **The subject** | `docs/milestone-2-corpus/phase-13-method-and-backlog/evidence/item-inventory.md` |
| **The source it describes** | `docs/backlog.md` — **and a frozen byte-identical copy** is beside the inventory as `backlog-before-ids.txt`, if you would rather read a copy that cannot change under you |

Both are in the repository at
`/Users/ilirium/Projects/local/ilirium_llm_router/phase-13-method-and-backlog`. The inventory's line
numbers refer to `docs/backlog.md` at commit `809a422`, which is `HEAD` for that file — **verify
that before trusting a line number**, with `git diff --stat 809a422 HEAD -- docs/backlog.md`, which
should be empty.

---

## The rules

**1 · Read-only. Change nothing.** No file, no tree. **If you run any command, run `git status`
afterwards and report exactly what it printed.** This is not a formality: a sweep in this repository
once left a source file gutted while the test suite still passed.

**2 · Label every finding `VERIFIED` or `REPORTED`.** VERIFIED means you opened the file and
confirmed it. REPORTED means suspected. **A review that does not label cannot be triaged.**

**3 · Findings and questions go in separate sections.** A finding is a defect with evidence. A
question is for a person to decide.

**4 · Nothing found is a complete answer.** A reviewer required to produce findings will manufacture
them. **Say what you checked and found correct** — that section is what makes an empty result usable
rather than empty.

**5 · Rank findings by how permanent the mistake is**, not by how hard they were to find:

| Worst | a **missing item** — a real item with no id, which the scheme will never notice is absent |
| | a **wrong boundary** — two items fused, or one item split, freezing an id onto the wrong thing |
| | a **wrong status** — recoverable, but it decides which file the item lives in |
| Least | a wrong date or a description that reads poorly — correctable at any time |

---

## What to check, specifically

### 1 · Is the count right, and is anything missing?

**Derive the item count yourself, from `docs/backlog.md`, before reading the inventory's answer.**
Then compare. The inventory says **36**.

**The dangerous direction is a missed item**, not a spurious one: a spurious id is visible as a row
describing nothing, and a missing item is invisible forever.

### 2 · Are the boundaries right?

Items mostly open with a **bold sentence** at the start of a paragraph. **That signal is strong and
not reliable** — some bold paragraphs are *continuations* of the item above, and some are
*section-level advice* belonging to no item.

**The inventory flags six boundary calls it says were judgement.** Check each. **Then look for a
seventh it did not flag** — that is the more valuable finding.

### 3 · Is there a fourth item shape?

The inventory claims exactly three shapes: prose with a bold opening; **rows of one table**, in the
section *Decisions waiting on a person*; and **`###` subsections**, in *Dictionaries*. **An earlier
survey read only three of the eight sections and was explicitly a lower bound.** This pass claims to
have read all eight. **Verify that claim by looking at all eight yourself.**

### 4 · Are the statuses right?

Five are possible: `open`, `partly-done`, `done`, `refused`, `superseded`. **Only `done` items leave
`backlog.md`** — everything else stays — so a wrong status moves an item to the wrong file.

**Five items are not `open`.** Check each against what its text actually says:

- one marked **`partly-done`** — is it partly discharged, and is the remaining part real?
- two marked **`done`** — is the work actually finished?
- one marked **`refused`**
- one marked **`superseded`** — it should name what supersedes it

**And the reverse, which nothing else will catch: is any item marked `open` actually finished or
abandoned?** Its own text is the evidence — several items carry a note saying something was fixed.

### 5 · Are the dates right?

The inventory says **eleven of the thirty-six carry no `added` date**. **Check that none of the
eleven has a date stated somewhere the pass did not look**, and that the dates it does give match
what the item says.

### 6 · Do the ids run in file order?

`BKL-0001` upward, top to bottom, no gaps and no duplicates. **This is mechanical — check it
mechanically.**

### 7 · Does each one-line description describe its item?

A description that fits the wrong item, or that asserts something the item does not say, is a
finding. **These are the most-read text in the scheme** — they become a table people scan instead of
reading the file.

### 8 · One claim to verify by reading, not by trusting

The inventory says one item is **discharged by the pass itself** — an item that asked for *"an id
per item, a rule for allocating one that survives items being deleted when done, and a decision on
whether a checker verifies them."* **Check all three are genuinely answered**, and say so if only
two are.

---

## Known false positives — do not spend findings on these

- **`backlog-before-ids.txt` is a deliberate frozen copy** of `backlog.md`. It is `.txt` rather than
  `.md` on purpose, so the repository's link checker does not scan it. Not a defect.
- **The inventory cites files that do not exist yet** — `backlog-done.md` and a `backlog-index.py`
  under `procedures/`. They are built later in the same phase.
- **Table rows longer than 100 characters are fine.** The column rule is for prose.
- **`docs/backlog.md` has no ids in it today.** The inventory is a proposal; the file is untouched
  by design.
- **Several items are undated.** That is the subject of check 5, not a defect in itself.

---

## The output

**One report**, in this shape. Each finding:

```
[VERIFIED|REPORTED]  <one-line claim>
  Where:     file:line
  Evidence:  what you read, and what it said
  Permanence: missing item / wrong boundary / wrong status / correctable
```

Then, separately:

- **Questions** — numbered, each saying what it would change.
- **Your own count**, derived independently, with how you derived it.
- **A verdict on each of the six flagged boundary calls**: agree, disagree, or cannot tell from the
  text.
- **What you checked and found correct.**
- **What you did not reach.** If you run out of room, say so and name it. **An honest gap is worth
  more than a skim**, and this review's whole subject is a pass that nobody has checked.

## One thing to know about how this review is being run

**You are a single reviewer, and the protocol this repository normally uses runs two in parallel on
different questions.** That is deliberate here — it is a session-budget decision, not a claim that
one run suffices.

**So do not assume a second pass will catch what you skip.** Where you would normally leave
something for the other reviewer, do it or say you did not.
