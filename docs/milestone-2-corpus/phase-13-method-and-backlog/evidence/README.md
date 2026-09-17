# Phase 13 — evidence

**Captures are frozen. Nothing captured here is edited after it is written**, which is
`../../../README.md`'s archive rule applied at the point of capture rather than at the merge.

***This said "nothing here" until 2026-09-04, and it was wrong about its own folder.***
*`item-inventory.md` is a **proposal under review**, not a capture: the author run corrected five
line numbers in it, and task 14a's ratification then rewrote its counts, five descriptions and three
statuses. A rule that forbade both would have had to be broken to act on a review — which is the
opposite of what a review is for. **The frozen artefact here is `backlog-before-ids.txt`**, and the
distinction is now stated rather than assumed.*

| File | What it is |
|---|---|
| `backlog-before-ids.txt` | **`docs/backlog.md` exactly as it stood before any `BKL` id was applied**, captured 2026-09-04 at commit `809a422`. **859 lines, SHA-256 `08f49383…c43b37e7`**, verified byte-identical to the original with `cmp` at capture |
| `item-inventory.md` | Task 13's output, **as ratified by task 14a on 2026-09-04 — 38 items**, with proposed ids, statuses and dates, and now **seven** boundary calls. *It said 36 and six until the cold review.* **The subject of the reviews below, and the one file here that is not frozen** |
| `item-inventory-review-charter.md` | What a fresh-context agent is given in order to review the inventory. Handed over verbatim |
| `item-inventory-author-review.md` | **The author run only**, 2026-09-04, done against a session budget that would not stretch to a cold one. **It does not discharge the charter above** and says so in its first section. **Its central claim — "no item was missed" — was refuted the same day**, and it is left standing as written |

**The cold run has no file here, and that is the standing rule rather than an omission.** Raw review
reports are not kept — `../notes-review-plan.md` says why — so **task 14a's outcome lives in
`../notes-group-e.md`**, and its corrections live in `item-inventory.md` itself. *The author run is
the exception, because it is the artefact whose limits the charter's discharge depends on.*

## Why the backlog copy is `.txt` and not `.md`

**Deliberate, and it is not a formatting preference.** `../../../procedures/link-check.py` globs
`*.md` across the whole repository. A `.md` copy of an 859-line document full of **relative paths
written from `docs/`** would be scanned from this folder instead, five levels down, and **every one
of those paths would be reported broken** — dozens of findings that are
artefacts of where the copy sits rather than defects in anything.

*The glob is itself a known gap — it is `BKL-0029`'s fifth piece of evidence, that citations outside
`*.md` go unchecked. **Here that gap is the useful behaviour**, and it is worth saying so, because
the same item may one day propose closing it. If the glob widens, this file starts reporting dozens
of broken links and the fix is to exclude frozen captures, not to rename this file back.*

## Why a copy exists at all, when git holds every version

**The owner's instruction, 2026-09-04.** Git does hold it — `git show 809a422:docs/backlog.md`
returns the same bytes, and that is the more durable record.

**What the copy buys is that a reader comparing the file before and after ~36 edits does not have to
know the commit**, and that the review below can be handed to a fresh agent as **two paths** rather
than as a path and a git incantation. *That is a convenience rather than a correctness argument, and
it is written down as one.*


## The mutation fixture is not here, and that is deliberate

**Task 17 drove `backlog-index.py` against a scratch copy** — `backlog.md` with the proposed
metadata applied and one item moved to a `backlog-done.md` — and then mutated it seven times to
check each validation bites. **None of that is frozen here.**

**It is derived, entirely, from two things that are:** `backlog-before-ids.txt` above and
`item-inventory.md` beside it. *Freezing a file that can be rebuilt from frozen inputs adds a third
copy that can disagree with them.* **What is not reproducible is the outcome**, and that is written
down — the three defects the run found and the seven mutations that were killed, in
`../notes-group-e.md`.
