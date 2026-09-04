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


## Task 17 — the script, written and driven before it was committed

**`../../procedures/backlog-index.py`, 296 lines**, in the shape `branch-index.py` established:
`--print` / `--write` / `--check` off `sys.argv[1]`, HTML splice markers, **refuse to render at
all** rather than splice a half-written table, and exit 0 current / 1 stale-or-invalid / 2 misuse.

**Taken out of order — 15 and 16 wait on the task-14a review, and this does not.** The script is
indifferent to which items exist.

### Two design decisions, both of which remove a second copy of a fact

**It does not detect item boundaries.** An item *is* something carrying a metadata line. A boundary
the script gets wrong is then a boundary somebody wrote wrong, visible in a diff — rather than a
parser's opinion, which is not. *This also keeps the instrument from confirming the judgement that
built it, which is the vacuity `IDM-009` asks about.*

**The description column is the item's own opening sentence**, extracted, not authored. A
hand-written one-line summary would be a second copy of a fact, and this repository has four
recorded instances of exactly that going stale.

### It was driven against a scratch copy, and that found three defects reading would not

**A fixture was built in the scratchpad** — `backlog.md` with the proposed metadata applied and
`BKL-0004` moved to a `backlog-done.md` — so the whole path ran end to end **without touching the
real files while the review of the inventory is outstanding.**

| | Defect | How it surfaced |
|---|---|---|
| 1 | **File order was checked across both files as one sequence.** A done item moves and leaves a gap, so the two interleave by construction | reported `BKL-0004`, the first item ever moved, as following `BKL-0036` |
| 2 | **The generated table's own rows parsed back as items.** A generated row and a table-row *item* are the same shape | `--write` then `--check` reported all 33 ids as duplicates of themselves. **Only that order shows it** |
| 3 | **The inventory had a wrong line number.** `BKL-0001` is at 40, not 38 | its generated row described the **section preamble** instead of the item |

**The third is not the script's defect but the inventory's**, and it is the one worth carrying: *a
wrong line number is invisible in a table of numbers and obvious the moment something renders the
text it points at.* Corrected in `evidence/item-inventory.md`, which says so in place.

### Then the checks were mutation-tested, one at a time

**Seven mutations, isolated rather than batched** — the batch-masking finding from Phase 12 is why.
**All seven were killed:** an invalid status, an id out of order, a category disagreeing with its
section, a citation of an id no item carries, a `done` item left in `backlog.md`, a non-`done` item
in `backlog-done.md`, and a `done` item missing its completion date.

*An eighth attempt failed because the mutation script errored rather than the check passing —
recorded because "the mutation did not apply" and "the test did not fail" are the same output at a
glance, and this repository has already been caught by an instrument that reported something untrue
without failing.*

### Two register rows closed

**`❓` is down to one.** The flags are `--print` / `--write` / `--check` plus an optional root path,
and the eight category tokens are **written out in the script rather than derived** — deriving them
produced `documentation-defects-found-and-not-fixed`, which nobody would type into a citation. *An
explicit mapping is also the project's stated preference, and it has a second use: a heading the
table does not know is refused, so renaming a section cannot silently invent a ninth category.*

**The one `❓` left is the highest id allocated**, which task 15 fixes.

### Two things about running it on the real tree, before task 15

**`--check` exits 1 there, and that is correct.** No id has been applied, so every `BKL-NNNN` this
phase's own documents cite resolves to nothing. **It will exit 0 the moment task 15 lands** — the
citations are already written and are waiting for the items, not the other way round.

**`make lint` does not reach this script.** It runs `ruff check src tests`; `docs/procedures/` is
outside it. *That is Phase 12's finding C9 arriving again — five over-width lines in a `.py` under
`docs/` that no lint run would ever see.* **Ruff was run against it explicitly**, at the pinned
`0.16.1` with `--line-length 100`, and passes.


## Task 14a — the author half, run on the owner's request

**`evidence/item-inventory-author-review.md`. The charter is not discharged and the cold run is
still owed** — the owner's session budget would not stretch to it, and the file says so in its own
first section rather than in a footnote.

**Two verified findings, and they point opposite ways.**

**Five of thirty-three line numbers were wrong** — `BKL-0001` off by two, and `BKL-0003`,
`BKL-0004`, `BKL-0006`, `BKL-0007` each off by one, **two too high and two too low**, which rules
out a constant offset and points at the extraction having been done twice by different means. All
corrected.

**No item was missed.** Every paragraph opening in the file was enumerated and the 33 claimed ones
subtracted; **28 remained and every one is accounted for** — four preamble, one section preamble,
one the section-level advice at line 394, four the corrected openings, and eighteen continuations.
**The count of 36 holds and the six boundary calls are right.**

*The two findings are worth their asymmetry: **the judgement half survived and the mechanical half
did not**, which is the opposite of what the last three reviews in this repository returned.*

**Two things were reported rather than concluded, and one of them is a check that proved nothing.**
The reverse status question — *is any item marked `open` actually finished?* — ran with a boundary
list that omitted the non-`open` items, so several bodies ran into their neighbours. **At least one
hit is provably its own bug.** Nothing is concluded from it; **it is recorded because a check that
ran and proved nothing looks identical to one that ran and found nothing.**
