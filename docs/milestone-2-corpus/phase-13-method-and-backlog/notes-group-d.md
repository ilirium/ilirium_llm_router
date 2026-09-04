# Phase 13 — Group D, `IDM-011`

*Tasks 10–12. Written while working.*

## Task 10 — the document, 176 lines

**`../../method/IDM-011-the-backlog.md`, in force 2026-09-04.**

### It opens by saying which of its own rules is actually in force

**An `IDM` is normally something you can act on entirely, and this one is not yet.** `IDM-000` is
explicit that an `IDM` *"is in force now and you are expected to act on it"* — but `IDM-011`
describes an identifier, a metadata line, a generated table and a second file that **Group E has not
built.**

**So the document says so in a table at the top**: the filing rule is in force the moment it is
read; everything else describes what this same phase builds. *Writing the rules before the refactor
is the plan's own ordering and it is the right one — the alternative is a refactor that invents its
rules as it applies them. What would have been wrong is letting a reader assume all of it is live.*

### The one rule that changes behaviour today

**A session asks the owner before filing a backlog item.** Declined items are recorded in the
phase's `notes.md`.

**The owner's reason is recorded because it is the load-bearing part:** *a large backlog is not
itself a good outcome.* A file whose items are added by whoever notices something becomes a list
nobody chose.

### What the document says its own checker cannot see

**`--check` validates the `BKL` citations that exist and never the title citations that remain**, so
the archive's quoted titles are outside it — by decision, since a quoted title in a closed phase's
document is a *claim* and the archive rule is paths yes, claims no.

**Written into the document rather than left implicit**, because a green check would otherwise be
read as proof of a promise it does not test. *That is `IDM-009`'s vacuity question applied to an
instrument before the instrument exists.*

## Task 11 — the amendment, and it is the second in three days

**`IDM-001`'s backlog paragraph was amended 2026-09-02 and is amended again here.** The two
amendments are about different things, which the new text says explicitly:

| | 2026-09-02 | 2026-09-04 |
|---|---|---|
| Changed | **where** the record goes — an item never opens its own branch | **whose** act it is — a session asks, the owner decides |
| Left alone | the authority, which was the session's | the branch rule, which is untouched |

**The old sentence read as a session's own act to perform** — *"adding a backlog item is how a phase
declines scope … it is the phase's own act"*. That is now split: **declining scope** is still the
phase's act and still happens during the phase; **filing** is the owner's word. `IDM-001` keeps only
the branch rule and points at `IDM-011` for the rest.

### `backlog.md`'s preamble now points rather than restates

It carried two rules that `IDM-011` owns, plus the "deleted when done" sentence that settled row 1
replaces. **Two things are still restated there, deliberately**, with the direction of truth written
in — the asking rule and the branch rule — because a session acts on both **without looking anything
up**, which is `../../README.md`'s test for a second copy.

## Task 12 — the index row and the pointer

- **`IDM-000` index row.**
- **`CLAUDE.md`, one pointer.** *Its justification is the sharpest of the three added this phase:*
  **the rule reverses a reflex a session already has.** `IDM-001` and `backlog.md`'s preamble both
  said, for two days, that filing an item was the phase's own act — so a session that learned the
  old rule **will file confidently and wrongly**, which is precisely `../../README.md`'s admission
  test for `CLAUDE.md`.

**`CLAUDE.md` is now 352 lines**, from 338 when this branch opened. *Three pointers, no
restatements. The backlog item recording its length says **297**, and entry 4 of `for-the-owner.md`
tells the owner that number is stale and that this phase is one of the reasons.*

## `link-check.py`: 120 broken on this branch

**Against 91 on `main`, and every one of the delta is a file this phase will create** —
`backlog-done.md` and `procedures/backlog-index.py` account for the two added by this group, cited
from `IDM-011` before Group E builds them. *The count is a property of the worktree; it is recorded
with the tree named and is not comparable to a figure taken elsewhere.*
