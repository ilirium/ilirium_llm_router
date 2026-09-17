# Phase 13 — the review of its own finished work

**Task 23, the reconciliation.** *Two runs under `review-charter-jobs-done.md`, on
`dec7c4a..40e05bc`, 2026-09-04. **The first application of `IDM-009`, by the phase that wrote it.***

**Both runs returned `nothing to commit, working tree clean`.** Run A hit one harness refusal —
`--write` against the real tree was denied by the auto-mode classifier — and **did not retry it**;
it copied the tree and used the script's documented second argument instead, then diffed
byte-for-byte. *That is the right response to a refusal and is recorded because it is the first
one.*

---

## The merge is stopped, and by the rule this phase wrote

**`IDM-009`: one method-tier or settled-row finding stops the merge, however clean everything else
is.** There are five. *The protocol worked on its first run, against its own author.*

## R1 · Settled row 26 was applied to none of the ten items it governs

**Both runs found it independently** — Run A's F1, Run B's F3 — and Run A traced the provenance.

Row 26 says the shortened item's original sentence *"stays in the body **unbolded**"*, with the test
*"no sentence in the body restates the heading"*. `IDM-011:92-95` says the same. **Ten items in
`backlog.md` open their body with the bold sentence the heading was made from.** `BKL-0029`'s body
reads *"**`procedures/link-check.py`'s exit code carries no information.**"* under a heading saying
exactly that. Two more in `backlog-done.md` open bold with *"**Done 2026-08-17.**"*

**The cause is one line of the conversion script** — where a title was shortened it wrote
`f"**{bold}**"` back into the body. *The rule was implemented as its own opposite.*

***And the notes claim a check that was never run.*** `notes-group-e2.md:58-60` says *"the check
after each was that no body sentence restates its heading."* **No such check exists and none was
run.** Run A: *"the rule's two clauses were not applied to a single one of the items they exist
for."* **That sentence is the most serious thing in this review** — a false claim that a check ran
is worse than the defect it was claimed to catch, because it is what a later reader trusts instead
of looking.

## R2 · The heading-count assertion is vacuous — it cannot catch what it was built for

**Run A's F2, and it is the finding that justifies `IDM-009`'s vacuity pass on this run.**

The assertion was added at task 20g against a stated intent: *"a paragraph that stops looking like
an item disappears silently; this is the check the inventory pass did not have."*

**It cannot do that.** `headings += 1` sits inside the branch that builds the item, and the only
escape before `items.append` already files `NO METADATA LINE`. **So the counts can differ only in a
state that has already produced a per-item error — the assertion never fires alone.** And the case
it was written for makes *both* counters drop together: demote a `###` to `####` and `HEADING.match`
fails, so nothing is counted and nothing is said.

**Re-verified here rather than taken from the report.** Demoting `BKL-0014`'s heading and
neutralising its citations left `--check` reporting only the orphaned heading string as an unknown
citation. **The assertion printed nothing in either run.** *The citation check does all the work
that was credited to it.*

**Six documents credit this check with coverage a different check provides**, two of them
method-tier: `IDM-011:113-115` and `:180-184`, `backlog-index.py`'s docstring and its own comment,
`status.md`, `notes-group-e2.md`, `plan.md`.

***The comment I wrote above it — "exactly how `BKL-0032` and `BKL-0033` stayed invisible" — is
backwards.*** *The assertion is blind to precisely that case.*

## R3 · `IDM-011`'s "what `--check` cannot see" describes the wrong gap, in the wrong direction

**Run A's F3.** The recorded mutation says a deleted item was caught only by luck of a stale table,
and that regenerating first would leave nothing to catch it.

**Both halves are wrong.** All 38 ids are cited in `evidence/item-inventory.md` and
`notes-group-e2.md`, so **no shipped item can be deleted silently** — the protection is real, not
luck. But Run A added **a synthetic item one past the highest id**, regenerated, deleted it and its
row: **`--check` exited 0.**

> ***The id it used is deliberately not written here, and that is now a rule*** — see `IDM-011`.
> *Naming it made `--check` fail on this very file, because the checker cannot tell a mention from a
> citation. **The owner's reason is the stronger one**: the next item allocated takes that number,
> at which point this sentence stops being an unresolvable mention and silently becomes a **wrong
> citation** of a real item. **The check would go green at the moment the text became false.***

**So the gap is not "an item deleted outright" — it is "an item added after this phase and then
deleted", which is the opposite distribution to the one recorded.** *The section exists so its
silence is not misread, and it misreads its own silence.*

## R4 · The `See` column is structurally unfillable, and a settled row cites it as proof

**Run B's F1**, reached from the method tier rather than from the instrument — *`--check` cannot
fail on `See` because nothing writes it.* `grep -n 'See' backlog-index.py` returns one line: the
header string. Yet `IDM-011:127` defines `superseded` as *"replaced by another item, **which the
`See` column names**"*, and settled row 23 names `BKL-0037`→`BKL-0034` as its instance.

***The forward review already caught the shallow version*** — `notes-review-plan.md:89`, *"The
register names a `See` column that nothing defines — **fixed**"* — **and the fix was to define it in
prose without building it.** *A finding was closed by writing the claim down more firmly.*

## R5 · `IDM-009`'s own instruction was not followed on its first application

**Run B's F4.** `IDM-009:197-199` closes its question 2 with *"the charter names the subject as a
single commit hash, and each run verifies the subject is unchanged at that hash before it begins —
`git diff` against it, reported."* **The charter names a range, and asked neither run to verify.**
`plan.md:139` answers the same question as *"state the range"*, so the plan and the `IDM` disagree.

*Both runs did it unprompted and reported `HEAD` one commit ahead. The reason `IDM-009` gives is
honoured; the rule is not.*

---

## Below the merge line — confirmed, and for task 24 to sort

| | Finding | Both runs? |
|---|---|---|
| R6 | **`backlog.md`'s own preamble** describes the retired three placements *and* the deleted `opening_sentence` step | Run A F4, Run B F5 |
| R7 | **`IDM-000`'s index row for `IDM-011`** still describes the three-shape scheme | Run B F2 |
| R8 | **`prompt.md` carries five statements its own file contradicts**, written in the range's last commit — including *"the 24-row settled table"*, which has 26 | Run B F11 |
| R9 | **`status.md`'s lead sentence** says Group E is part-done and stopped; two sections below say E and E2 are complete | Run B F6 |
| R10 | **`status.md:51` cites lines 87 and 117** for the phase count; they are 103 and 133 | Run B F7 |
| R11 | **`notes.md`'s entry point is four groups stale** — the exact defect it documents four lines lower; plus "seven groups" and a missing `notes-group-e2.md` row | Run B F8 |
| R12 | **`plan.md`: "Seven groups, twenty-nine tasks"** — eight and 38 | Run B F9 |
| R13 | **The settled table's intro attributes rows 25 and 26 to the forward review**; both are the owner's, later | Run B F10 |
| R14 | **`BKL-0004` says 859 lines; the file is 1010** — stale again inside the phase that corrected it. Two more of its sentences are now false | Run B F12 |
| R15 | **`backlog-done.md` says the two EPD items "stay a table"** — Group E2 dissolved it | Run A F6 |
| R16 | **Three items say they are "struck"** and nothing is struck any more | Run B F15 |
| R17 | **`IDM-001` says `backlog.md` "still carries"** an item now in `backlog-done.md` | Run B F13 |
| R18 | **`for-the-owner.md` entry 4** tells the owner a number this phase then corrected | Run B F14 |
| R19 | **`status.md`'s "112 against 91" is not like-for-like.** Run A measured `main`'s content at **111** in an identical tree; the phase's real net effect is **+2**, and ~20 of the gap is a per-worktree `.claude/` file | Run A F5 |
| R20 | **Task 19 edited a `status.md` paragraph** that still says "Phase 11 is chosen and running" | Run B F16 |
| R21 | **Conversion residue**: `item** , under`, and two dissolved-cell paragraphs with no terminal punctuation | Run A F8, Run B F17 |
| R22 | **The register attributes `for-the-owner.md` to task 27**, which settled row 14 forbids | Run B F18 |
| R23 | **The Dictionaries preamble says "three items below"**; two are. *Pre-existing* | Run A F9 |

---

## The measurements `IDM-009` §7 requires

**This run turns n=1 into n=2.**

### Overlap

**Distinct findings: 23.** Both runs reached **3** — the row-26 breach, the `backlog.md` preamble,
and the conversion residue. **13%**, against the forward review's 17% on the same phase.

*The split held. Run A returned 9 findings, Run B 18, and only 3 are shared — so **87% of the work
came from exactly one run**, and either alone would have missed most of it.*

### Cold-run cost

| | Run A | Run B |
|---|---|---|
| Tokens | ~126,000 | ~170,000 |
| Tool calls | 63 | 53 |
| Wall clock | ~13.7 min | ~10.7 min |

*Run A cost less and took longer — it ran things.*

### Findings by how they were reachable

***This is the number `IDM-009` says decides whether the split is right.***

| Reachable only by | Count | |
|---|---|---|
| **running something** | **3** | R2, R3, R19 — **all Run A**, and R2 is the review's sharpest finding |
| **reading code** | 2 | R4 (the `grep` that returns one line), and half of R2 |
| **reading prose** | 12 | most of Run B's list |
| **holding the record** | **6** | R1's false check-claim, R5, R13, R14, R18, R22 — *findings that need the plan, the notes and the artefact side by side* |

**The split is vindicated, and not symmetrically.** *Run B's 18 findings are mostly one kind —
prose that stopped being true. Run A's 9 include every finding that required execution, and **two of
those three could not have been reached any other way**. A single-run review would have been Run B's
list, and would have shipped a vacuous check.*

### What the phase's own checks had already caught

***None of the 23.*** `--check` exits 0. `link-check.py`'s count is unchanged. Ruff is clean on the
script. **Every finding here is invisible to every instrument this phase built** — and two of them
(R2, R4) are *about* instruments that pass while testing nothing.

*That is the strongest evidence for `IDM-009` the protocol has: on its first run, against an author
who had just written it, with every mechanical check green, a two-run review returned 23 findings of
which five stop the merge.*

---

## What both runs refused to file, and were right to

**Run A refused to file R1 as a fix** — row 26 is the owner's, so the alternative reading (that the
bold openings were meant to stay, and the *rule* is what needs amending) belongs to the owner.
*Both runs said so independently.*

**Run B refused `IDM-009`'s own breach as anything but a question** (R5), because correcting it
changes a document in force.

**Neither run filed the known false positives.** *Nothing was spent on the 36 ruff findings, the
link-check count, the empty `See` cells as such, the 101–103 column widths, or the amendable
inventory.*

## What neither run reached

- **The original mutation runs and the original task 20f script.** Both destroyed with their scratch
  copies, so `IDM-009`'s batch-masking warning **cannot be discharged from the record**. Run A
  replayed each mutation individually — *which is a different thing from confirming what was done.*
- **`main`'s own worktree**, so the 91 figure stands unreproduced.
- **`notes-group-a.md` through `-d`**, unopened by either run.
- **The bodies of 20 of the 34 live items**, seen by Run A only through mechanical extraction.
- **`implementation-plan.md`**, where task 3a claims a retitle that is not in the diffstat.
- **The charter itself**, which sits one commit outside the range it defines.
