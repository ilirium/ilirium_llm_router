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

## Task 14 — the checkpoint. Not run

**Waiting on the owner.** *This task produces no commit*, which `../../README.md` requires its row
to say, so that a reader cannot mistake it for a task that was skipped.

**Three questions are put to them**: are the six boundaries right, what should be pruned, and are
`BKL-0002` (`partly-done`) and `BKL-0035` (`superseded`) — the only two non-obvious statuses —
correct.
