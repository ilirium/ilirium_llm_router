# Reference — the durable tier

Facts that stay true regardless of which phase found them. These files survive every milestone; the
archive under `../milestone-1-core/` records how they were found out.

**This index is the reading order.** There are no numeric prefixes on the filenames — these documents
are cited by name from `src/` docstrings, and a prefix would mean that inserting one document
renumbers the rest and churns citations in code. The order lives here instead, which costs one file
and breaks nothing.

## Reading order

Front to back, this is the argument: why the router exists, what was decided, what it records, what
is at each end of it, and how confident to be about any of it.

| # | File | What it answers |
|---|---|---|
| 1 | `architecture.md` | Why this exists at all, and why it dispatches rather than translates. Includes the observed shape of a real request |
| 2 | `design-decisions.md` | Every decision taken deliberately, with the reasoning that produced it. **Read this before reversing anything** |
| 3 | `observability.md` | The CSV's twenty columns, what each is for, and the constraints on the recorder |
| 4 | `backend-anthropic.md` | Model IDs, the two request-shape rejections, OAuth forwarding, the rate-limit shape |
| 5 | `backend-lmstudio.md` | What the local backend accepts, honours and ignores; context, prefill and timeouts |
| 6 | `measurements.md` | Every number quoted anywhere, with its date, instrument, slice, and what it is for |
| 7 | `lessons.md` | How this project has been wrong, and what caught it |

**If you are here to look one thing up**, the shortcuts: a number → `measurements.md`; a decision you
want to change → `design-decisions.md`; whether a backend supports something → its own file.

## What belongs here

A fact belongs in this tier when it would still be true if the phase that found it had never happened.
Citing a phase note as the **provenance** of a measurement is correct; needing its plan, its ordering,
or what it expected versus found means the fact has not finished being extracted.

**One file per subject, each with a nameable trigger** — a moment you would open *it* rather than its
neighbour. A section becomes its own file when its trigger is nameable *and* it passes roughly 40
lines. Until then it lives inside the nearest file that already has one.

Two files are deliberately deferred, each with its reason:

- **`configuration.md`** — its material is credential modes, which are a design decision, and
  timeouts, which belong to the backend they describe. "Working on configuration" is not a trigger
  distinct from those two.
- **`request-shape.md`** — 12 lines, and it stays a section of `architecture.md`. That is also what
  keeps `proxy.py:3` citing a section title that still resolves.

Filing rules for the whole of `docs/` are in `../README.md`.

---

*Written 2026-08-16 at commit 5 of `../docs-restructure-plan.md` and completed at commit 6. All seven
files exist, and since commit 11 none of them duplicates a `CLAUDE.md` section — the four that did
were deliberate, so that no destination was missing when the cut happened.*
