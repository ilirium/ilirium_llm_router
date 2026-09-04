# Phase 13 — evidence

**Frozen artefacts. Nothing here is edited after it is written**, which is `../../../README.md`'s
archive rule applied at the point of capture rather than at the merge.

| File | What it is |
|---|---|
| `backlog-before-ids.txt` | **`docs/backlog.md` exactly as it stood before any `BKL` id was applied**, captured 2026-09-04 at commit `809a422`. **859 lines, SHA-256 `08f49383…c43b37e7`**, verified byte-identical to the original with `cmp` at capture |
| `item-inventory.md` | Task 13's output — 36 items with proposed ids, statuses and dates, and the six boundary calls. **The subject of the review below** |
| `item-inventory-review-charter.md` | What a fresh-context agent is given in order to review the inventory. Handed over verbatim |

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
