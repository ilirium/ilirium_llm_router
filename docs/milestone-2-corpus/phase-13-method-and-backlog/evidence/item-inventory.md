# Phase 13 — the backlog item inventory, for ratification

**Task 13's output. Nothing has been applied to `../../../backlog.md`.** Task 14 is the owner
ratifying this and pruning it; task 15 applies it afterwards.

**36 items.** Ids are proposed in **file order**, per settled row 24. Line numbers are as
`backlog.md` reads at commit `809a422` and are given so a boundary can be checked, not because they
are part of the scheme.

**All eight sections were read in full**, not sampled. *The forward review's three-shape survey read
three of eight by grep and its result was a lower bound; it was right — no fourth shape exists, and
the three are confirmed.*

---

## The three shapes, confirmed

| Section | Items | Shape |
|---|---|---|
| Method | 4 | prose, bold opening |
| Documentation defects | 4 | prose, bold opening |
| **Decisions waiting on a person** | **3** | **rows of one table** — no prose items at all |
| Measurements left open | 6 | prose, bold opening |
| Work with an owner-shaped decision | 7 | prose, bold opening |
| Instruments and housekeeping | 8 | prose, bold opening |
| **Dictionaries** | **2** | **`###` subsections** |
| Not on this list, and why | 2 | prose, bold opening |

---

## The inventory

*`See` is left for task 17 to generate except where an item points at another item.*

### Method — 4

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0001` | 38 | 2026-08-19 | open | A forward review must classify each position by **authority**, not only correctness — an unratified position is reported as such |
| `BKL-0002` | 77 | 2026-08-19 | **partly-done** | A forward review must check the plan's numbers against the phase's own `evidence/`. *Two thirds discharged by `IDM-008`; the forward-review half is open* |
| `BKL-0003` | 121 | 2026-09-02 | open | The one-notes-file-per-task-group rule is invisible at the moment it applies |
| `BKL-0004` | 176 | 2026-08-26 | **done** · 2026-09-04 · phase 13 | Give every item here a stable, referencable index. **This inventory is its discharge** |

### Documentation defects found and not fixed — 4

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0005` | 188 | — | open | `CLAUDE.md`'s length against upstream guidance, and nobody has measured what it could lose |
| `BKL-0006` | 205 | 2026-08-17 | open | The whole of `milestone-1-core/documentation-review-2026-08-16.md` — ~30 findings and six owner questions, parked whole |
| `BKL-0007` | 265 | 2026-09-02 | open | The open milestone's phase count is stated in several places and has gone stale four times |
| `BKL-0008` | 311 | 2026-09-02 | open | Phase 11 records its largest corpus session as both 292 calls and 270 |

### Decisions waiting on a person — 3 *(table rows)*

| Id | Row | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0009` | `EPD-001` | — | open | Picking a local model mid-session, and subagents on local models — blocked on a decision only |
| `BKL-0010` | `EPD-002` | — | open | Token counting for local backends — blocked on a decision, on a case Phase 4 weakened |
| `BKL-0011` | `EPD-003` | — | **done** · 2026-08-17 | Capturing bodies for a corpus. Decided and graduated into `reference/design-decisions.md` |

### Measurements left open — 6

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0012` | 345 | — | open | Whether Claude Code shows LM Studio's context error |
| `BKL-0013` | 351 | — | open | Non-streaming replies — every Phase 4 probe ran streamed |
| `BKL-0014` | 356 | — | open | Other local models — all of Phase 4 is one model |
| `BKL-0015` | 361 | 2026-08-19 | open | What one day of real use contains, and where the training floor is |
| `BKL-0016` | 372 | 2026-08-19 | open | Whether a response dictionary pays |
| `BKL-0017` | 380 | 2026-08-21 | open | Whether archiving slows a call — **failure mode 3 of the milestone's central claim** |

### Work with an owner-shaped decision behind it — 7

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0018` | 402 | — | open | Prompt-cache warmup probes cost 44% of local wall-clock time |
| `BKL-0019` | 410 | 2026-08-26 | open | What a reconstructed session cannot contain, and the fix nobody should reach for |
| `BKL-0020` | 424 | 2026-08-18 | open | Three diagnostics reserved out of Phase 10, deliberately |
| `BKL-0021` | 438 | 2026-08-18 | open | A caller that disconnects before the generator's first step can leave no row — a race, never observed |
| `BKL-0022` | 477 | — | open | Running the router as several processes |
| `BKL-0023` | 495 | — | open | The per-backend authentication header name |
| `BKL-0024` | 500 | — | open | Extract the portable methodology — deferred with a trigger |

### Instruments and housekeeping — 8

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0025` | 518 | 2026-08-28 | open | ~24 mutation survivors are error-message wording, parked rather than tested |
| `BKL-0026` | 538 | 2026-08-28 | open | A mutation-testing tool, rather than the hand-rolled harness |
| `BKL-0027` | 557 | 2026-08-26 | open | Whether a reconstruction can be checked against the real thing |
| `BKL-0028` | 573 | 2026-08-21 | open | Nothing runs `branch-index.py --check` automatically |
| `BKL-0029` | 600 | — | open | `link-check.py`'s exit code carries no information, and six pieces of evidence about its gaps |
| `BKL-0030` | 680 | 2026-09-02 | open | `IDM-003` governs the formatter pin and says nothing about the build backend |
| `BKL-0031` | 706 | — | open | Static analysis beyond ruff |
| `BKL-0032` | 759 | 2026-08-24 | open | Record the Anthropic rate-limit response headers — **Phase 14** |

### Dictionaries — 2 *(`###` subsections)*

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0033` | 815 | 2026-08-26 | open | Dictionary commands — `list`, `show`, `install` |
| `BKL-0034` | 825 | 2026-08-26 | open | A benchmark: what a dictionary is worth against no dictionary |

### Not on this list, and why — 2

| Id | Line | Added | Status | See | What it is |
|---|---|---|---|---|---|
| `BKL-0035` | 841 | — | **superseded** | `BKL-0032` | The Anthropic 429 rate-limit headers, refused and then **overturned 2026-08-24** |
| `BKL-0036` | 856 | — | **refused** | | Everything struck through in `milestone-1-core/outstanding-work.md` |

---

## Six judgement calls, each of which the owner can overturn

**These are the boundaries that were not obvious. Everything else read as one item on sight.**

1. **`BKL-0035` is the `superseded` instance settled row 23 named**, and it is the only one in the
   file. Nothing else is superseded by anything.
2. **`BKL-0036` is one item, not a class.** It says *"everything struck through in another file"* —
   arguably a pointer rather than a piece of work. **Filed as `refused`** because it sits in the
   refusals section and reads as a decision. *If you would rather it had no id, it is the cheapest
   one to drop.*
3. **"Before planning any of these, grep the frozen artefacts first" (line 394) is not an item.** It
   is a bold-opening paragraph that closes the Measurements section and applies to all six. **It
   gets no id.**
4. **Two bold paragraphs in `Dictionaries` (lines 805, 810) are not items either** — one records
   that all three were postponed, the other points at `BKL-0016` in another section. That section
   has exactly two items, both `###`.
5. **`BKL-0021` absorbs the "What remains is a race" paragraph at line 445.** It reads like an
   opening and is a continuation — the narrowing of the same item.
6. **`BKL-0029` absorbs four bold paragraphs** at 606, 619, 646 and 661 — they are the evidence for
   the `link-check.py` item, not four items.

## Two things this pass established that were not known before

**Eleven of the thirty-three dated-or-not items carry no `added` date at all** — every one predating
the file's own habit of recording it. *This is settled row 24's evidence rather than an argument for
it: **date order was not merely a different ordering, it was unavailable**, and a third of the file
would have needed a date invented to freeze a permanent id.*

**`BKL-0004` is discharged by the pass that allocated it.** The item asked for *"an id per item, a
rule for allocating one that survives items being deleted when done, and a decision on whether a
checker verifies them"*. All three are answered — in `IDM-011`, by settled row 1, and by
`backlog-index.py --check`. *Its own text says the file is **545 lines**; it is **859**. The figure
is corrected as the item moves to `backlog-done.md`, which is where task 16 puts it.*

---

## What task 14 asks of the owner

1. **Are the boundaries right?** The six calls above are the only ones in doubt.
2. **Prune.** Any item you no longer want becomes `refused` — it keeps its id and moves to the
   refusals section, so nothing is lost and the id stays citable.
3. **Anything mis-statused?** Particularly `BKL-0002` (`partly-done`) and `BKL-0035`
   (`superseded`), which are the only two non-obvious ones.

**Nothing is applied until this returns.** A wrong boundary freezes a wrong id into a scheme whose
whole premise is that ids never change.
