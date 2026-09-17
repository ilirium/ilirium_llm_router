# Phase 13 — the forward review of the plan

**Run 2026-09-04, before task 3a**, per `../../method/IDM-004-reviewing-unexecuted-work.md` and
`review-charter.md` beside this file. Two runs in parallel — this session as author, one
fresh-context agent as cold reader — read-only, against `plan.md` at `6345eb8`. This file is the
reconciliation.

*The record lives here rather than in `notes.md`, which is what Phase 12 settled when a second
review made "the review" ambiguous. This phase will have two reviews for the same reason: task 21
runs one against the finished work.*

**The two runs' raw reports are not kept, and that is the protocol rather than a gap.** `IDM-004`
specifies *one report per run, then a reconciliation*, and says the merged work list goes in the
phase's notes — which is this file. Phase 12 did the same. **What is lost is the cold run's own
wording and its line-by-line citations**; what is kept is every finding, its disposition, the four
owner answers, and the measurement. *Recorded so a reader looking for the original reports stops
looking.*

---

## The headline

**Eighteen distinct findings. The two runs overlapped on three — 17%.**

`IDM-004`'s own forward run overlapped at **18%**, and Phase 12's backward run at **11%**. **This is
the second forward measurement and it lands within a point of the first**, which is worth more than
either number alone: `IDM-004` says outright that a second run returning 60% would mean one run is
enough and the document would need rewriting rather than defending. It returned 17%.

| | Author | Cold | Both |
|---|---|---|---|
| Distinct findings | 3 | 12 | 3 |

**The split fell along the predicted line.** All three author-unique findings were about **the
record** — a decision the owner made in interview that never reached the plan, a task that produces
no commit, a status with no stated home. **Every one of the cold reader's twelve was about what the
author could not un-know**, including the two that would have done real damage.

**The cold run's read-only compliance was checked, not assumed.** `git status` at its start and end
both printed a clean tree, and `plan.md` was byte-identical at `HEAD` and `6345eb8` afterwards.

---

## The finding that justifies the protocol on its own

**Task 5 told the next session to close four questions "named in `review-plan-jobs-done.md` as
deliberately unanswered". That file leaves exactly one open — and question 3 is one the owner
settled.**

Verified line by line in `../phase-12-installer-and-readme/review-plan-jobs-done.md`:

| Question as the plan stated it | What the file actually says |
|---|---|
| 1 · what "the author run" means across sessions | **Open.** Line 177, *"Left open deliberately"* — the only such marker in the file |
| 2 · when the commit range is named | **Not in that file at all.** `grep -ci 'commit range'` returns **0**. It is finding A5 in `notes-review-jobs-done.md`, deferred there to the `IDM` |
| 3 · whether "before the merge" generalises | **Settled by the owner 2026-09-02.** Settled row 1, line 228. Line 246 then reads *"Nothing else in this document is settled"* — the file draws the line explicitly |
| 4 · what one measurement is worth | A **result** of the run (11%, `notes-review-jobs-done.md:15`), not a question that file poses |

**Why this is the one worth its cost.** `IDM-009` goes into force the moment it is written. A
session executing task 5 as written would have opened that file, found one question where the plan
promised four, and had to guess — and the most available guess is to answer question 3 anyway,
**which re-decides a row the owner settled two days earlier.** Phase 12's own settled row 6 makes a
finding that reverses an owner decision a *merge-stopper*. So the defect, left in, produces the
exact class of failure that would have blocked this phase's merge, in the tier that is in force on
writing.

**All four subjects remain real things `IDM-009` must handle.** Only their sourcing was wrong, and
question 3 changes from *decide this* to *inherit this, and say whose decision it was*.

---

## Findings, in cost order

*`C` = cold run, `A` = author, `AC` = both. All `VERIFIED`. **Fixed** unless the row says
otherwise.*

| | Finding | Disposition |
|---|---|---|
| **C1** | Task 5 misattributes four open questions to a file that leaves one; question 3 is owner-settled | **fixed** — task 5 now names three questions with their true sources, and records that "before the merge" is inherited, not decided |
| **C2** | Task 8's claim that all three of Phase 11's `ASK`s are the shape settled row 13 forbids is refuted by the file — and contradicts this plan's own settled row 16 | **question for the owner.** Under the new taxonomy two are `ERRAND`s and one is a *conforming* `ASK` |
| **AC3** | `backlog.md` has **three item shapes**, not one. Two of eight sections have no bold opening for settled row 7's metadata line | **question for the owner** — it touches settled rows 4, 6 and 7 |
| **C4** | `BKL` allocation order is undefined for a bulk pass: "in order written" reads as file order or as `added`-date order, and they differ | **question for the owner** — it freezes ~30 permanent ids |
| **C5** | Task 15 says "Move nothing", settled row 1 says a done item moves, and no task removes the seeded item from `backlog.md` | **fixed** |
| **AC6** | The register omits `review-charter.md` and `notes-review-plan.md`, which task 3 creates | **fixed** |
| **C7** | Task 26 says fix Phase 13 cross-references in `backlog.md`; that file names Phase 13 **zero** times | **fixed** — struck |
| **AC8** | Tasks 3a and 26 are the same edit to the same file; the plan disambiguates 3a from task 27 instead | **fixed** |
| **C9** | `IDM-010` and `IDM-011` get no `CLAUDE.md` pointer, and settled row 9 is precisely a rule that fails without one | **fixed** — tasks 9 and 12 now add one |
| **C10** | Task 19's citation sweep reaches the frozen archive and the plan gives no rule for it | **fixed by decision** — see below |
| **C11** | The register names a `See` column that nothing defines | **fixed** |
| **A2 / C12** | `partly-done` and `superseded` have no stated home, and `superseded` has no named instance | **question for the owner** |
| **C13** | **Three** `backlog.md` items propose `IDM-004` amendments, not two — and the third says the three must be decided together | **fixed** — the count; the owner's decision to leave them parked stands |
| **C14** | Task 9 says "pointer" where `README.md:360`'s contents sentence itself becomes wrong under settled row 11 | **fixed** |
| **C15** | "Seven groups, twenty-eight tasks" is **29** since task 3a was inserted | **fixed** |
| **A3** | A decision the owner made in interview round 1 never reached the settled table: **nothing formally closes a `for-the-owner.md` entry** | **fixed** — restored as settled row 20 |
| **A6** | Task 14 produces no commit and does not say so, which `README.md` requires | **fixed** |

---

## Decided rather than asked

**C10 — the frozen archive is out of task 19's sweep.** `../../README.md`'s archive rule is *paths
yes, claims no*. **A quoted backlog title inside an archived phase document is a claim** — it
records what the backlog said at the time — so repointing it to a `BKL` id would edit a claim in a
frozen document. The sweep covers the live tier only: `../../status.md`, `../../backlog.md`,
`CLAUDE.md`, `../../method/`, `../../reference/`, `../implementation-plan.md`, and any
**open** phase folder.

**The cost of that decision is stated rather than hidden:** the scheme's promise — *nothing cites a
backlog item by title any more* — is true of the live tier and false of the archive, and task 20's
`--check` cannot see the difference, because it validates `BKL` citations that exist and never title
citations that remain. **`IDM-011` says so in as many words**, so no later reader mistakes the
archive's title citations for a gap nobody noticed.

---

## Questions for the owner — raised, not decided

**Four, and each touches a settled row. `IDM-004` rule 5: a settled decision may be questioned,
never filed as a defect.** They are put to the owner in the session rather than left here, which is
settled row 13 applied to this phase.

1. **Settled row 7's metadata line has nowhere to go in two sections** — `Decisions waiting on a
   person` is three table rows, `Dictionaries` holds two items as `###` subsections.
2. **Settled row 13's stated evidence is refuted.** The rule may well stand; what does not is the
   claim that Phase 11's three `ASK`s violate it. Two are `ERRAND`s by this plan's own row 16, and
   the third — *"raised in every recent phase"* — is a **conforming** `ASK`.
3. **`partly-done` and `superseded` have no home, and `superseded` has no instance.**
4. **`BKL` allocation order** — file order or `added`-date order. It differs, and ids are permanent.

### Answered 2026-09-04, the same session — settled rows 21–24

**All four were put to the owner in the session and answered there.** *That is settled row 13
applied to the phase that wrote it: a question needing a decision is asked out loud, not left in a
file for somebody to find.*

| | Answer | What it turned on |
|---|---|---|
| 1 | **Metadata per shape** — a line under the bold opening, an extra leading column for the table rows, a line under the heading for `###` items | Settled rows 4 and 7 both survive and nothing moves. The cost lands on `backlog-index.py`, which learns three shapes |
| 2 | **Row 13 stands; the evidence is re-sourced** | **The refutation improved the finding rather than killing it.** Phase 11's file does not show a rule being broken — it shows **`ERRAND` was missing**, which is why two errands were filed as `ASK`s. `IDM-010` now carries that instead |
| 3 | **`partly-done` and `superseded` stay live; `superseded` gets its instance** — the struck 429 entry, overturned by the live rate-limit item, with `See` carrying the link | Keeps `backlog-done.md` meaning exactly one thing, which settled row 6 gave it |
| 4 | **File order** | Not a preference between two workable schemes: **date order is unusable**, because several older items carry no `added` date and inferring one would freeze a permanent id on a guess |

**Question 2 is the one worth carrying.** A refuted claim is normally a subtraction; here the file
that was supposed to prove the rule turned out to prove something better about it, and **the review
could not have reached that** — it takes the taxonomy the plan itself introduces to see that two of
the three `ASK`s were `ERRAND`s all along.

*Three more the cold run raised are recorded and not escalated, because each is answerable inside a
later task:* whether `IDM-009` takes `IDM-000`'s two-zone shape (task 4's own call), where an
entry's date goes in the new `for-the-owner.md` heading (task 7), and whether Phase 13's
`register-check.py` is written or adapted from Phase 12's (task 25 — it is written, against this
phase's own register).

**And one against this charter, which is correct.** It puts itself out of scope and then asks the
reviewer, in claim 10, to check that *"task 3 and this document"* match `IDM-004`. The cold reader
resolved it by checking task 3 and reporting the conflict rather than auditing its own
instructions — the right call, and the defect belongs to the charter. **Recorded for `IDM-009`**,
which will specify a charter's shape.

---

## What was checked and found correct

**This section is what makes *nothing found* usable rather than empty.**

- **All fifteen charter claims were re-verified against the source**, fourteen correct and one —
  claim 14, the four open questions — refuted. That refutation is C1.
- **The two figures task 2 corrected are right the second time.** 11 entries, 3 `ASK` / 5 `IDEA` /
  3 `REGRET`, none marked answered, confirmed independently by the cold run.
- **`IDM-001`, `backlog.md`'s preamble, `IDM-000`'s numbering rule, `IDM-008`'s two requirements,
  `branch-index.py`'s `--write`/`--check`/0/1 shape, `link-check.py`'s root-relative resolution,
  `README.md`'s archive rule, and `implementation-plan.md`'s Phase 13 allocation** — all as the
  plan describes them.
- **Task 3 matches `IDM-004` on all four counts** — charter, two parallel runs, read-only,
  `VERIFIED`/`REPORTED`. **Task 28's three merge steps match `IDM-001`.**
- **The group-independence claim holds.** No group depends on a later one; the phase can stop at any
  group boundary, as the plan says.
- **`notes.md` and `notes-group-a.md` contradict nothing in the plan**, and findings A1–A3 of task 2
  are independently correct.
- **Nothing was filed on the seven known false positives.**

**What the cold run did not reach, in its own words:** three of `backlog.md`'s eight sections read
only by grep — so **the three-shape survey is a lower bound** — Phase 12's
`review-charter-jobs-done.md`, and `IDM-004` in full. *Given C1, that first gap matters: a fourth
item shape in the ~500 unread lines would land in task 13 with the checkpoint already spent.*
