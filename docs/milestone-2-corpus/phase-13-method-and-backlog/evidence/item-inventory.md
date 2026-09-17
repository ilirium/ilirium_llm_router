# Phase 13 — the backlog item inventory, for ratification

**Task 13's output. Nothing has been applied to `../../../backlog.md`.** Task 14 is the owner
ratifying this and pruning it; task 15 applies it afterwards.

**38 items.** *It said 36 until the cold review of 2026-09-04 found two it had missed.* Ids are
proposed in **file order**, per settled row 24. Line numbers are as
`backlog.md` reads at commit `809a422` and are given so a boundary can be checked, not because they
are part of the scheme.

**This pass claimed all eight sections were read in full, and two items in one section were still
missed.** *The claim was not a lie about effort — it was a mechanical blind spot, and the cold
review of 2026-09-04 found it. The enumeration matched a paragraph opening with **bold or `###`** at
the line start. `backlog.md:716` and `:735` open `~~**` — **strike before bold** — and failed it,
while the two struck entries that open the other way round, `:337` and `:841`, were both caught. Two
bytes in the wrong order made two items invisible, and the pass then reported the section as holding
**8** when it holds **10**.*

***Five of the thirty-three line numbers in this table were also wrong and are corrected.***
*`BKL-0001` was at 38 and opens at **40** — found by `backlog-index.py`, whose generated row for it
described the section preamble instead of the item. **Four more were each off by one** — `BKL-0003`,
`BKL-0004`, `BKL-0006`, `BKL-0007` — found by the author review in
`item-inventory-author-review.md`. **Two too high and two too low, so not a constant offset.***
*The forward review's three-shape survey read
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
| Instruments and housekeeping | **10** | prose, bold opening — **two of them struck-through `done` entries** |
| **Dictionaries** | **2** | **`###` subsections** |
| Not on this list, and why | 2 | prose, bold opening |

---

## The inventory

*`See` is left for task 17 to generate except where an item points at another item.*

### Method — 4

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0001` | 40 | 2026-08-19 | open | A forward review must classify each position by **authority**, not only correctness — an unratified position is reported as such |
| `BKL-0002` | 77 | 2026-08-19 | **partly-done** | A forward review must check the plan's numbers against the phase's own `evidence/`. *Two thirds discharged by `IDM-008`; the forward-review half is open* |
| `BKL-0003` | 122 | 2026-09-02 | open | The one-notes-file-per-task-group rule is invisible at the moment it applies |
| `BKL-0004` | 175 | 2026-08-26 | **partly-done** | Give every item here a stable, referencable index. **This inventory is its discharge** |

### Documentation defects found and not fixed — 4

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0005` | 188 | — | open | `CLAUDE.md`'s length against upstream guidance, and nobody has measured what it could lose |
| `BKL-0006` | 206 | 2026-08-17 | open | The whole of `milestone-1-core/documentation-review-2026-08-16.md` — ~30 findings and six owner questions, parked 2026-08-17 — one finding since acted on, the rest not |
| `BKL-0007` | 266 | 2026-09-02 | open | The open milestone's phase count is duplicated and goes stale at every merge; three candidate fixes, none chosen |
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
| `BKL-0020` | 424 | 2026-08-18 | open | Three diagnostics reserved out of Phase 10 — and **one of the three, the `calls.csv` sequence column, is refused rather than parked** |
| `BKL-0021` | 438 | 2026-08-18 | open | A caller that disconnects before the generator's first step can leave no row — **observed 2026-08-20** at Phase 10's task 18a |
| `BKL-0022` | 477 | 2026-08-18 | open | Running the router as several processes |
| `BKL-0023` | 495 | — | open | The per-backend authentication header name |
| `BKL-0024` | 500 | — | open | Extract the portable methodology — deferred with a trigger |

### Instruments and housekeeping — 10

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0025` | 518 | 2026-08-28 | open | ~24 mutation survivors are error-message wording, parked rather than tested |
| `BKL-0026` | 538 | 2026-08-28 | open | A mutation-testing tool, rather than the hand-rolled harness |
| `BKL-0027` | 557 | 2026-08-26 | open | Whether a reconstruction can be checked against the real thing |
| `BKL-0028` | 573 | 2026-08-21 | open | Nothing runs `branch-index.py --check` automatically |
| `BKL-0029` | 600 | — | open | `link-check.py`'s exit code carries no information, with four pieces of evidence about its gaps and two more the item deliberately does not fold in |
| `BKL-0030` | 680 | 2026-09-02 | open | `IDM-003` governs the formatter pin and says nothing about the build backend |
| `BKL-0031` | 706 | — | open | Static analysis beyond ruff |
| `BKL-0032` | 716 | — | **done** · 2026-08-17 | `status.md`'s shape — one row per milestone rather than per phase |
| `BKL-0033` | 735 | — | **done** · 2026-08-21 | Close out the four `Branch:` lines that record intent instead of outcome |
| `BKL-0034` | 759 | 2026-08-24 | open | Record the Anthropic rate-limit response headers |

### Dictionaries — 2 *(`###` subsections)*

| Id | Line | Added | Status | What it is |
|---|---|---|---|---|
| `BKL-0035` | 815 | 2026-08-26 | open | Dictionary commands — `list`, `show`, `install` |
| `BKL-0036` | 825 | 2026-08-26 | open | A benchmark: what a dictionary is worth against no dictionary |

### Not on this list, and why — 2

| Id | Line | Added | Status | See | What it is |
|---|---|---|---|---|---|
| `BKL-0037` | 841 | — | **superseded** | `BKL-0034` | The Anthropic 429 rate-limit headers, refused and then **overturned 2026-08-24** |
| `BKL-0038` | 856 | — | **done** · phase 5 | | Everything struck through in `milestone-1-core/outstanding-work.md` |

---

## Seven judgement calls, six flagged and one not

**The first six are the boundaries this pass knew were not obvious, and the cold review of
2026-09-04 agreed with every one of them. The seventh is the one it did not flag, and it is the one
that was wrong** — which is the shape the charter predicted: *"then look for a seventh it did not
flag — that is the more valuable finding."*

1. **`BKL-0037` is the `superseded` instance settled row 23 named**, and it is the only one in the
   file. Nothing else is superseded by anything.
2. **`BKL-0038` is one item, not a class.** It says *"everything struck through in another file"* —
   arguably a pointer rather than a piece of work. **Filed as `refused`, and the owner changed it to
   `done` on 2026-09-04**, on the cold review's reading: the item's own text says the credential
   shape and the read timeout *"were built in Phase 5"* and silent trimming *"was measured and
   closed the same day"*, which is completed work rather than a declined proposal. `IDM-011` defines
   `refused` as considered and declined. **It moves to `backlog-done.md`.** *Its section is a status
   container rather than a kind of work — `IDM-011` calls that a known wrinkle, and this is the
   wrinkle biting.*
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
7. **Not flagged, and wrong: the two struck-through `done` entries at 716 and 735 were dropped
   silently.** They are now `BKL-0032` and `BKL-0033`. **Nothing in this document recorded that a
   judgement had been made**, because none had — they were excluded by a pattern, not by a decision.
   *The file settles it against the pass in its own words:* `backlog.md:753`, of the entry at 735 —
   *"Kept struck rather than deleted, **like the two entries above it**."* The two above it are
   `:337` and `:841`, which are `BKL-0011` and `BKL-0037`, **and both were given ids.** The owner
   confirmed on 2026-09-04 that they get ids in file order.

## Two things this pass established that were not known before

**Sixteen of the thirty-eight items carry no `added` date at all** — every one predating
the file's own habit of recording it. *This figure said **eleven of thirty-three** until the cold
review: the count was wrong, the
denominator counted only line-numbered items, and `BKL-0022` was dated in its own text all along —
`backlog.md:478`, "Raised by the owner on 2026-08-18". **The argument it supports gets stronger.**
This is settled row 24's evidence rather than an argument for
it: **date order was not merely a different ordering, it was unavailable**, and a third of the file
would have needed a date invented to freeze a permanent id.*

**`BKL-0004` is designed by the pass that allocated it, and not yet discharged.** The item asked
for *"an id per item, a
rule for allocating one that survives items being deleted when done, and a decision on whether a
checker verifies them"*. All three are answered — in `IDM-011`, by settled row 1, and by
`backlog-index.py --check` — and the cold review verified each of the three independently rather
than taking the claim. **But no id is in `backlog.md` yet, so the item's subject is designed and not
applied**; the owner set it `partly-done` on 2026-09-04, to flip when task 15 lands.

*Its own text says the file is **545 lines**; it is **859**. **That figure now needs correcting in
place rather than on the way out** — at `partly-done` the item stays in `backlog.md`, so task 16
does not move it and nothing else would touch the stale number.*

---

## What task 14 settled, 2026-09-04

**After task 14a — the cold review — and on the owner's word the same day.**

1. **The two missed items get ids in file order.** `BKL-0032` and `BKL-0033`; the total is 38, and
   old `BKL-0032`–`0036` became `BKL-0034`–`0038`. **`BKL-0025`–`0031` did not move**, because the
   insertion points fall after line 706. *The cold review's report says everything from `BKL-0025`
   shifts; it does not, and the error is recorded here rather than corrected silently.*
2. **`BKL-0038` is `done`, not `refused`.** It moves to `backlog-done.md`.
3. **`BKL-0004` is `partly-done`, not `done`.** It stays in `backlog.md` and flips when task 15
   applies the ids.

## The two remaining questions, settled 2026-09-04

**Both were asked aloud and both are answered. Neither renumbers anything.**

**4 · `BKL-0007` stays `open`, and its premise needs correcting in `backlog.md`.** *`open` because
none of the deliverable shipped — the item's ask is to **choose** one of three fixes, and none is
chosen.* **But the item reasons from a premise that has expired.** It says the count is *"stated in
**four places across two files**"* and then eliminates two of its three candidates because *"only
deriving the count works across two files."* **`CLAUDE.md` stopped carrying the count in this phase
(`809a422`), and the "Where we stopped" copy is gone too — leaving two copies, both in `status.md`,
at lines 87 and 117.** So the constraint that disqualified *"the table row alone"* and *"leave three
copies and check them"* no longer holds, and **the cheapest fix is live again**.

**Its description drops the two numbers rather than carrying them**, which is what the cold review
commended in `BKL-0005`: a description that states the subject does not go stale, and this item's
entire subject is numbers going stale.

**5 · `BKL-0020` stays one `open` id, with the refusal in its description.** *A split into two ids
would have been the faithful reading — the `calls.csv` sequence column is `refused`, needing
`implementation-plan.md`'s non-goal overturned, while the other two are merely parked. It was
declined on cost: a split means editing `backlog.md` to make two items from one paragraph-block, and
inserting an id at line 424 shifts all eighteen below it.* **Available only before task 15, and not
taken.**

---

## Two things task 15 must carry, beyond applying the ids

1. **Correct `BKL-0007`'s premise in `backlog.md`** — four places across two files → **two copies in
   `status.md`**, and the consequent sentence eliminating two candidate fixes. *Deliberately not
   done at task 14a: editing prose at line 266 shifts every line below it and would stale the Line
   column this review had just finished verifying.*
2. **Correct `BKL-0004`'s "545 lines" to 859** in place. *At `partly-done` the item stays in
   `backlog.md`, so task 16 does not move it and nothing else would touch the stale figure.*

**Nothing is applied to `backlog.md` yet.** A wrong boundary freezes a wrong id into a scheme whose
whole premise is that ids never change.
