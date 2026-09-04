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
`BKL-0002` (`partly-done`) and `BKL-0037` (`superseded`) — the only two non-obvious statuses —
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
`docs/` that no lint run would ever see.* ~~**Ruff was run against it explicitly**, at the pinned
`0.16.1` with `--line-length 100`, and passes.~~

**That last sentence is wrong, and it was found on 2026-09-04 by running the command it describes.**
`uvx ruff@0.16.1 check docs/procedures/backlog-index.py` reports **`RUF007`** — prefer
`itertools.pairwise()` over `zip()` for successive pairs, at line 220, in the file-order check.
**It fires on the committed version too**, so this is not something a later edit introduced.

**And the directory has never been clean.** `ruff check docs/procedures/` reports **36 findings**:
24 in `branch-index.py`, 7 + 2 + 2 in the three `event-loop-lag` and `corpus-benchmark` scripts, and
this one. *Left unfixed rather than half-fixed — fixing one of thirty-six because it happens to sit
in this phase's file is arbitrary, and whether `docs/procedures/` is linted at all is a question
`make lint`'s scope has never been asked.* **The claim is retracted; the code is untouched.**


## Task 14a — the author half, run on the owner's request

**`evidence/item-inventory-author-review.md`. The charter is not discharged and the cold run is
still owed** — the owner's session budget would not stretch to it, and the file says so in its own
first section rather than in a footnote.

**Two verified findings, and they point opposite ways.**

**Five of thirty-three line numbers were wrong** — `BKL-0001` off by two, and `BKL-0003`,
`BKL-0004`, `BKL-0006`, `BKL-0007` each off by one, **two too high and two too low**, which rules
out a constant offset and points at the extraction having been done twice by different means. All
corrected.

**~~No item was missed.~~ Refuted the same day by the cold run below — two were.** *Left in place
rather than deleted, because the interesting fact is not that the claim was wrong but that it was
made with a reconciliation that did not balance.* The claim was: every paragraph opening in the file
was enumerated and the 33 claimed ones subtracted; **28 remained and every one is accounted for** —
four preamble, one section preamble, one the section-level advice at line 394, four the corrected
openings, and eighteen continuations. **That tally sums to 61 openings**, with the four corrected
ones double-counted inside the 33, **against a real 59.** The imbalance was the size of the gap and
nobody added it up. **The six boundary calls were right; the count of 36 was not.**

*The two findings are worth their asymmetry: **the judgement half survived and the mechanical half
did not**, which is the opposite of what the last three reviews in this repository returned.*

**Two things were reported rather than concluded, and one of them is a check that proved nothing.**
The reverse status question — *is any item marked `open` actually finished?* — ran with a boundary
list that omitted the non-`open` items, so several bodies ran into their neighbours. **At least one
hit is provably its own bug.** Nothing is concluded from it; **it is recorded because a check that
ran and proved nothing looks identical to one that ran and found nothing.**


## Task 14a — the cold half, and it found what the author half could not

**Run 2026-09-04, by a fresh-context agent handed `item-inventory-review-charter.md` verbatim and
nothing else.** Read-only; its `git status` came back clean and was re-checked here.

**Two items were missing — `backlog.md:716` and `:735`.** The inventory had 36 ids for **38 items**,
and *Instruments and housekeeping* holds **10**, not 8. This is the charter's worst permanence
category: *"a real item with no id, which the scheme will never notice is absent."*

**The mechanism is two bytes in the wrong order**, and it is the reason the author run could not see
it. The enumeration matched a paragraph opening with **bold or `###`** at the line start:

| Line | Opens | Id? |
|---|---|---|
| 337 | `\| ~~…` — a table row | `BKL-0011` |
| 841 | `**~~The Anthropic 429…` — **bold first** | `BKL-0037` |
| **716** | `~~**\`status.md\`'s shape…` — **strike first** | **none** |
| **735** | `~~**Close out the four \`Branch:\` lines…` | **none** |

`grep -n '^~~'` returns exactly those two lines in the whole file. **Both struck entries that led
with bold were caught; both that led with strike were invisible.** *Verified here rather than
relayed — the two lines, the two that did get ids, and the absence of any mention of 716 or 735 in
the inventory.*

**The file settles the intent question in its own words.** `backlog.md:753`, of the entry at 735 —
*"Kept struck rather than deleted, **like the two entries above it**."* The two above it are `:337`
and `:841`, and **both have ids**. The file's own author treats all three as one kind of thing.

**The owner ratified on 2026-09-04**: ids in file order, so `BKL-0032` and `BKL-0033` are the two,
and old `BKL-0032`–`0036` became `BKL-0034`–`0038`. **`BKL-0025`–`0031` did not move** — the
insertion points fall after line 706. *The cold report claims everything from `BKL-0025` shifts; it
does not. Recorded because a review's arithmetic is no more exempt than a plan's.*

### The other findings, and three were also verified here

- **`BKL-0022` is dated in its own text** — `backlog.md:478`, *"Raised by the owner on 2026-08-18"*.
  The author run's date regex covered Added/Proposed/Narrowed/Named/Overturned and **not "Raised"**.
- **The undated count was wrong twice over** — eleven claimed, **fifteen** actual, against a
  denominator of 33 where the claim's population is 36. With `BKL-0022` dated and the two new items
  undated it is now **16 of 38**, confirmed by counting the Added column in Python. *The argument it
  supports — that date order was unavailable, settled row 24 — gets stronger, not weaker.*
- **`BKL-0021`'s description asserted the opposite of its item.** It read *"a race, never
  observed"*;
  `backlog.md:453` retracts exactly that: *"Observed 2026-08-20, at Phase 10's Task 18a. The 'never
  been observed' clause above is spent."*
- **`BKL-0007`'s description swapped the item's two numbers** — four places and three staleness
  events, not several and four. *Mildly self-demonstrating: the item is about hand-carried counts
  going stale.*
- **`BKL-0034`'s description carried "Phase 14"**, which is scheduling state `backlog.md:3-4`
  forbids — *"Inventory, not state … nothing here says when anything happens."* Removed.
- **`BKL-0006`'s "parked whole" overstated it**; one finding has been acted on.

### What it checked and found correct

**All 33 line numbers, including the author run's five corrections.** Ids sequential, unique,
gapless, correctly formatted. **All eight sections read in full at their true line ranges.** No
fourth item shape. `BKL-0002`'s `partly-done` right and its remaining third real. `BKL-0011`'s
`done` right. **Check 8 answered in the affirmative and independently** — `BKL-0004`'s three asks
are all genuinely met, not two. **The three date suspects the author run left `REPORTED` are all
correctly `—`** — a narrowing, a fix date and an overturn, none of them an `added` date. **And the
register table inside `BKL-0002` is correctly not treated as items** — a naive rule would have
manufactured three spurious ids there.

**It agreed with all six flagged boundary calls.** *Which is the shape the charter predicted: the
six the pass doubted were the six it got right, and the value was in the seventh it never flagged.*

### What it did not reach

**Its own list, kept rather than paraphrased:** an exhaustive enumeration of sub-paragraph bold runs
behind the six boundary verdicts (spot-checked only); the `BKL-NNNN` citations elsewhere in the
repository against the proposed ids; the plan's settled rows 1, 12, 23 and 24 beyond confirming
`IDM-011` cites them; and `notes-review-plan.md`, this file and `evidence/README.md`, any of which
might already have recorded the 716/735 question.

**The second of those was closed here.** `grep -rln 'BKL-00'` over `docs/` returns eight files, and
**only two carry an id that shifted** — this file, corrected, and `procedures/backlog-index.py`.

**And the script's two are deliberately left alone.** `backlog-index.py:210-211` records that the
run reported `BKL-0004` as following `BKL-0036` — **that is what the run reported**, against a
36-item scratch copy, and rewriting it to `BKL-0038` would make the record describe a run that never
happened. *A historical record of a defect is not a citation of a live id.*

### One thing this leaves open about the evidence folder

**`evidence/README.md` says "Nothing here is edited after it is written", and `item-inventory.md`
has now been edited twice** — once by the author run and once by this ratification. **Either the
inventory is not a frozen artefact or the rule is wrong as written.** *Raised rather than worked
around; `backlog-before-ids.txt` is the artefact that genuinely cannot move.*


## Task 14 — the last two questions, and one of them moved the item

**Settled 2026-09-04, after the cold review. Neither renumbers.**

**`BKL-0007` stays `open`** — none of the deliverable shipped; its ask is to *choose* one of three
fixes and none is chosen. **But its premise has expired.** The item says the phase count is stated
in *"four places across two files"* and eliminates two of its three candidates on that basis: *"only
deriving the count works across two files."* **`CLAUDE.md` dropped its copy in this phase
(`809a422`) and "Where we stopped" dropped the other**, leaving two, both in `status.md` at lines 87
and 117. **So *"the table row alone"* is viable again**, and it is the one the item calls cheapest.
*The correction is a task-15 action, recorded in the inventory: editing prose at line 266 today
would shift every line below it and stale the Line column task 14a had just verified.*

**Its description now carries no numbers** — *"the count is duplicated and goes stale at every
merge; three candidate fixes, none chosen."* **This is the `BKL-0005` treatment**, which the cold
review singled out as better than its source: a description that states the subject cannot go stale.
*It is the obvious call here and nearly was not made — the first draft of this description said
"four places across two files and gone stale three times", which is two numbers, in the description
of the item about numbers going stale.*

**`BKL-0020` stays one `open` id**, with the refusal in its description. *A split was the faithful
reading — the `calls.csv` sequence column is `refused` and needs `implementation-plan.md`'s non-goal
overturned, while the endpoint and the per-failure detail are merely parked.* **Declined on cost:**
a split means editing `backlog.md` to make two items from one paragraph-block, and an id inserted at
line 424 shifts all eighteen below it. **The option existed only before task 15 and was not taken.**

**And `evidence/README.md`'s scoped freeze rule stands** — captures frozen, the inventory amendable
as a proposal under review.


## Task 15 — the ids applied, and it found what task 16 actually has to move

**`docs/backlog.md` now carries all 38 ids.** 35 as metadata lines under the item's opening
paragraph, 3 as leading cells in the *Decisions waiting on a person* table. **Every line number was
re-verified against the file before a single line was inserted** — all 35 sit on a
blank-line-preceded opening — and the insertion ran **bottom-up**, so no insert moved a line another
insert still needed.

**`--check` no longer reports a single unknown citation.** Every `BKL-NNNN` written across this
phase's documents now resolves to an item. *That half was waiting on the items, not the other way
round, exactly as task 17's notes predicted.*

### The table needed four leading columns, not one

**`IDM-011` says a table-row item carries "an extra leading column".** One is not enough: the parser
reads `category · status · added` from the first three cells after the id and takes the description
from the **fifth**. The three-column table became seven — `ID · Category · Status · Added · Blocked
on · What it is · Why it may be weaker` — with the EPD path moved into *What it is*, which is the
cell the generated table reads. **No content was dropped.**

### Three things task 16 inherits, and the plan names none of them

**1 · Four items are `done`, not one — and the one the plan names is not among them.** Task 16 says
to move *"the item this phase discharges"*, meaning `BKL-0004`. **`BKL-0004` is `partly-done` and
stays put.** The four that must move are **`BKL-0011`, `BKL-0032`, `BKL-0033` and `BKL-0038`**.
*Two of those are the items the cold review found, and one is the status the owner changed — so
three of the four exist because of task 14a. `BKL-0011` was `done` in the original inventory and
task 16 would have had to move it anyway; the plan was already incomplete before the review.*

**2 · `BKL-0038` has no completion date, and `validate` requires one.** Its text says the work
*"were built in Phase 5"* and *"was measured and closed the same day"*, naming no date. It is
applied as `· phase 5` with no `done` date, which is valid in `backlog.md` and **will fail the
moment task 16 moves it**, because a done item in `backlog-done.md` needs both.

**3 · `BKL-0011` is a table row, and a table row cannot carry a completion date at all.** The parser
sets `done=None, phase=None` unconditionally for row items — `backlog-index.py:177-178`. So a
`done` table-row item can never satisfy `validate` once moved. **Either `backlog-done.md` holds
prose items rather than rows, or the parser needs the row shape extended.** *Found by applying the
ids and reading what the script does with them, not by reading the script.*

### The two corrections this task carried

**`BKL-0004`'s "545-line file" is now 859**, corrected in place because `partly-done` means task 16
does not move it and nothing else would have touched it.

**`BKL-0007`'s premise is corrected and its history kept.** The paragraph that eliminated two of its
three candidate fixes now says so in the past tense and records that the constraint expired: the
count is in **two places, both in `status.md`**, since `CLAUDE.md` and "Where we stopped" both
dropped theirs. **All three candidates are live again, including the cheapest.**


## Tasks 16 and 18 — the move, the generated tables, and a second defect from the same two bytes

**`backlog-done.md` exists and holds four items** — `BKL-0011`, `BKL-0032`, `BKL-0033`, `BKL-0038`.
**`backlog.md` holds 34.** The two files interleave by gaps, which is the scheme working: a gap here
is an item finished there.

**It carries `backlog.md`'s section headings, and that is not decoration.** `validate` reads an
item's section from the nearest `## ` heading and checks it against the category on the metadata
line. **A file with no headings fails every category check** — found by building the file without
them first. Only the three sections in use appear.

**`BKL-0011` moved as prose**, per the owner's decision: a table row cannot carry a completion date,
because the parser sets `done=None, phase=None` for row items unconditionally. **`BKL-0038` took
`done 2026-08-07`**, derived from Phase 5's merge in `../../reference/branches.md` and recorded as
derived — the item itself names a phase and no date.

### The strike-before-bold shape caused a second defect, in the same instrument

**`opening_sentence` returned the whole paragraph for every struck item.**
`re.match(r"\*\*(.+?)\*\*", para)` cannot match a paragraph opening `~~**`, so the fallback returned
the entire paragraph — which put `BKL-0033`'s **four commit hashes** into one cell of the generated
table.

**This is the same two bytes that hid `BKL-0032` and `BKL-0033` from the inventory pass**, causing
an unrelated defect in a different component. *A strike is a marking on a shape, never a shape of
its own, and both defects came from code that treated it as one.* **Fixed** — the pattern is now
`(?:~~)?\*\*(.+?)\*\*`, with the reason written at the site.

**It was found by rendering the table and reading it**, not by reading the code. *Which is the third
time in this phase that opening the output beat re-reading the source.*

### One correction the generated table forced

**`BKL-0005`'s text said `CLAUDE.md` is 297 lines. It is 359.** The description column is derived
from the item's own opening sentence, **so a stale figure in an item is now published in a table
people scan** rather than buried in a paragraph. *The first attempt to fix it edited the generated
row instead of the item — the row sits earlier in the file, a single-occurrence replace found it
first, and `--write` overwrote the edit on the next run. **The generated block is not a place where
an edit can survive**, which is what the marker comment says and what this proved.*


## Tasks 19 and 20 — the citations repointed, and the sweep found far fewer than expected

**The plan said to sweep rather than enumerate, and the sweep is what found the number.** Every
item's own opening phrase was extracted from the two generated tables and searched across the live
tier with markup stripped and whitespace collapsed — **a leading-words probe first, then a sliding
window**, because the first pass found three sites and the second found nine. *The difference is
citations that quote from the middle of a title: `IDM-011` cites `BKL-0004` as "a stable,
referencable index", which no leading-word probe can see.*

**Of the nine, five were real citations and four were coincidence** — an EPD describing its own
subject in the words the backlog item borrowed from it, and this phase's own prose about the phase
count. *A phrase match is evidence of a citation, not proof of one; each was opened.*

| Repointed | Was |
|---|---|
| `method/IDM-003-development-tooling.md` → `BKL-0031` | "the backlog item below insists…" |
| `reference/observability.md` → `BKL-0021` | "That remains open in `../backlog.md`" |
| `method/IDM-011-the-backlog.md` → `BKL-0004` | "`backlog.md`'s own item asking for this" |
| `status.md` → `BKL-0017` | "is parked in `backlog.md`" |
| `status.md` → `BKL-0012` and `BKL-0017` | "both in `backlog.md` under 'Measurements left open'" |

**`CLAUDE.md` cites no item by title** — it points at `IDM-011` and stops, which is the tier rule
working.

**`procedures/corpus-benchmark/README.md` was left alone deliberately.** Its "What it does not
answer" bullets share wording with `BKL-0016` and `BKL-0017` because **the items were written from
the README**, not the other way round. *A scope statement is not a citation, and adding an id there
would point the source at its own derivative.*

**The frozen archive was not touched**, per the plan: a quoted title in a closed phase's document is
a claim about what the backlog said then.

### Task 20

**`backlog-index.py --check` exits 0.** Ids unique and in file order within each file, every item
carrying a row and every row an item, every category agreeing with its section, both `done` rules
holding, and **every `BKL-NNNN` written anywhere under `docs/` or in `CLAUDE.md` resolving to an
item.**

*It exited 1 for the whole of this phase until now, and the notes said that was correct. It was —
the citations were written before the items and were waiting on them.*

**`link-check.py` reports 112 broken, down from 117.** The five closed are the ones that named
`backlog-done.md` before it existed. *The remainder are unchanged and belong to files Group F and G
have still to create.*
