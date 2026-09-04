# Phase 13 — Group E, the refactor

*Tasks 13–20. Written while working.*

## Task 13 — the inventory, and it stops here

**`evidence/item-inventory.md`. 36 items, ids proposed in file order. Nothing applied.**

**All eight sections were read in full rather than sampled.** The forward review's three-shape
survey had read three of eight by grep and said so; **it was a lower bound and it was right** — no
fourth shape exists, and the three are confirmed:

| Shape | Sections | Items |
|---|---|---|
| prose with a bold opening | six | 29 |
| rows of one table | `Decisions waiting on a person` | 3 |
| `###` subsections | `Dictionaries` | 2 |

### Six boundaries were a judgement and the rest were obvious

**That ratio is the finding.** The pass was planned as a judgement call over ~30 items; **in
practice 30 of 36 read as one item on sight**, and the doubt concentrates in six places — all of
them either a bold paragraph that is a *continuation* or a bold paragraph that is *section-level
advice*.

**Two of the six are the same defect from opposite sides.** `BKL-0021` absorbs a paragraph at line
445 that opens like an item and is a narrowing of the one above it; `BKL-0029` absorbs **four**
paragraphs that are its evidence. **A bold opening is a strong signal and not a reliable one**,
which is what task 13 was warned about and what the checkpoint at task 14 exists for.

### Eleven items carry no `added` date, and that retires an argument rather than making one

**Settled row 24 chose file order over date order**, on the stated ground that date order is *"not
merely different but unusable"* because some items carry no date and inferring one would freeze a
permanent id on a guess.

**Counted here for the first time: eleven of thirty-six.** *Almost a third of the file. The
settled row was decided on the possibility; this is the size of it.*

### The item this phase discharges was allocated by the pass that discharges it

**`BKL-0004`** — *"Give every item here a stable, referencable index"*, added 2026-08-26 on the
owner's instruction. It named three things it would take, and all three are now answered: **an id**
(`IDM-011`), **an allocation rule that survives deletion** (settled row 1 — done items move rather
than being deleted), and **a checker** (`backlog-index.py --check` rather than `link-check.py`).

*Its own text says it touches every item in a **545-line** file. The file is **859**. The figure is
corrected as the item moves to `backlog-done.md` — which is task 16, and is the first thing that
file will hold.*

## Task 14 — the checkpoint. Returned, and extended

**The owner read the inventory and accepted it, then extended the checkpoint**: the inventory gets
**an independent review by a fresh-context agent, in a session of its own**, before task 15 applies
anything. *This task still produces no commit, which `../../README.md` requires its row to say, so
that a reader cannot mistake it for a task that was skipped.*

**Two artefacts were made for it, on the owner's instruction.**

**`evidence/backlog-before-ids.txt`** — `backlog.md` frozen before any id touches it, verified
byte-identical with `cmp` and recorded with its SHA-256. *`git show 809a422:docs/backlog.md` returns
the same bytes and is the more durable record; what the copy buys is that the review can be handed
over as **two paths** rather than as a path and a git incantation. That is a convenience argument
and `evidence/README.md` states it as one.*

**It is `.txt` and that is not a formatting preference.** `link-check.py` globs `*.md`; a `.md` copy
of an 859-line file whose paths are written from `docs/` would be scanned five levels down and
**every one of those paths reported broken**. *Confirmed: the broken count is **120 before and
after** the copy landed. **The glob's narrowness is `BKL-0029`'s own fifth piece of evidence — a
known gap — and here it is the useful behaviour**, which `evidence/README.md` records so that
closing the gap later does not silently break this.*

**`evidence/item-inventory-review-charter.md`** — written to be read by somebody who knows nothing
about this repository, so it repeats rather than points. Eight checks, and the two that matter most
are aimed at the failure that cannot be recovered from:

- **Derive the count independently *before* reading the inventory's answer.** *The dangerous
  direction is a **missed** item: a spurious id is visible as a row describing nothing, a missing
  item is invisible forever.*
- **Find a seventh boundary the pass did not flag.** *Checking the six it did flag is the easy half
  and the inventory has already argued them.*

**It also asks the reverse status question**, which nothing else would catch: not *are the five
non-`open` items right*, but **is any item marked `open` actually finished** — several carry a note
in their own text saying something was fixed.

**One deviation is named rather than hidden.** `IDM-004` runs two reviewers in parallel on different
questions; this is **one**, for session budget. The charter says so in its last section and tells
the reviewer **not to leave anything for a second pass that is not coming.**

**Three questions are put to them**: are the six boundaries right, what should be pruned, and are
`BKL-0002` (`partly-done`) and `BKL-0035` (`superseded`) — the only two non-obvious statuses —
correct.
