# Phase 12 — Group D: the documents

*Tasks 11 to 14. Entry point is `notes.md`. Nothing in this group touches `src/`.*

## Task 11 — the brief moves to `captures/`

**Done 2026-09-02.** `../../captures/original-project-description.md`, 52 lines: a header saying
what the file is, then the brief appended **byte for byte** from `README.md`'s "Description"
section.

**Both halves of the task are done, and the second one is the half the forward review found
missing.** The cold run reported that the plan moved a file into `captures/` and never added its
row to `../../captures/README.md`'s index table. The row is in.

### What was checked before the file was written, and it changed the header

**The brief is not "as written 2026-07-27" without a qualification.** `README.md` at `cae861d`
(2026-07-27) is the brief and **is missing its last line** — `uv` for dependencies arrived the same
day at `5895359`, in the commit that added `CLAUDE.md`. From that commit the text is **byte for byte
identical to today**, 1027 bytes, verified against both commits rather than assumed from the fact
that nobody remembers editing it.

*Why this is in the notes rather than only in the header:* "kept as written" is a claim about a file
nobody may edit afterwards, so which commit it was written at is the whole content of the claim. Had
it been taken from `cae861d` on the strength of "that is the initial commit", the capture would be
missing a line and would say it was complete.

### Three things the header carries that the plan did not ask for

- **The two trailing spaces** at the end of the first future-work bullet are a markdown hard break
  and are preserved. A capture nobody edits includes its own whitespace.
- **Three of its lines run past 100 columns.** They are the brief's own. The header says so, because
  the next session to see them will otherwise fix them — this project checks column width by hand
  and `make lint` cannot see it.
- **Two statements in the brief are already overtaken by what was built** — Pydantic validates the
  routing-relevant fields only, and "simple configuration at first" now has backends, rotation and a
  corpus store. **Named in the header as the reason not to correct them.** A brief edited to match
  the code cannot show what changed, which is the only thing the file is for.

### `captures/README.md` gained more than a row

Its opening sentence said *"several documents cite it, and the probes replay it"* — a singular
"it", written when the directory held one file. **That is this repository's named defect class**: a
sentence summarising a table it has stopped matching, which is what `fix-slop-docs/` exists to
count. Corrected in the same edit rather than left for a later branch to find.

The per-file `##` sections were **not** extended with one for the new capture, deliberately. It
explains itself in its own header; a section here would be the second copy that drifts. The file now
says that in one line, so the asymmetry reads as a decision rather than an omission.

### One thing left inconsistent on purpose

**The brief is currently in two places** — `captures/` and `README.md`'s "Description" section — and
that is the plan's sequencing, not an oversight. Task 13 rewrites `README.md` to ten sections, none
of which is the brief; task 14 sweeps what no section inherits. **If this phase stopped here the
duplication would ship**, which is why it is written down rather than left to be noticed.

## Task 12 — the Milestone 2 count, and the third instance

**Done 2026-09-02.** `../../status.md` said **four** at line 56 and **three** at lines 108 and 138.
Four is right — 8, 9, 10 and 11. Both undercounting places now say four, and the milestone row names
Phase 11's merge date rather than Phase 10's.

**The task was chartered as a fix and it is the third instance, not the end of one.** The paragraph
that undercounts is the paragraph that **describes prose going stale**, and it had already recorded
two instances of itself doing exactly that. Phase 11's merge produced the third: from 2026-08-28 to
today the file said four in one place and three in two others, disagreeing with itself for five days
while two sessions and a merge read past it.

**So the fix is recorded in place and the mechanism is filed rather than chosen.**
`../../backlog.md` gains an item under "Documentation defects found and not fixed" naming the three
candidate fixes — the table row alone, deriving the count from `../implementation-plan.md`'s `###
Phase N` headings, or keeping three copies and checking them — **and none is chosen here**, because
choosing one changes what `status.md` is and that is not this phase's decision.

*One thing the item is careful not to conclude:* this is **not** an argument for tables over prose.
The milestone table row went stale in the same edit as the paragraph. The 2026-08-17 item that
settled this file's shape already found the axis is *what goes stale invisibly*, and both of these
are invisible for the same reason — nothing re-reads them at a merge.

## Task 13 — the `README.md` rewrite

**Done 2026-09-02. Ten sections, in the settled order**, 133 lines to 304.

**`## TL;DR` is an explicit heading rather than a lead paragraph**, so the register's *"`README.md`
sections | count | 10"* is checkable by grep at task 15 instead of resting on whether a reader
counts the opening paragraph as a section.

**The `--help` is quoted verbatim from the shipped binary**, per the plan, so the two cannot drift.
Captured by running it rather than by reading `cli.py`.

**Every number in it was taken from something rather than carried across.** `make test` was **run**:
448. The version string came from `--version`, not from `pyproject.toml`. Seven Milestone 1 phases
and four in Milestone 2 replace the six and the 158 the old file carried — both were Milestone 1's,
and the 158 was stale by 290 tests.

**One claim was checked before it was written, because it would have been easy to assume.** *"One
process, one hop, no retries of its own"* — `grep -rn retry src/` returns three hits and **none is
in the proxy**; all three are `transcript.py` and `extract.py` reasoning about retries the *harness*
sends. The router does not retry.

### What went into "Bugs and caveats", and the one that is easy to get backwards

Four items, per settled row 6: `BUG-001`, the corpus being off by default, that nothing deletes an
archived body, and that a long session's later calls go **unstored** past `body_max_bytes`.

**That last one is stated as unstored and never as truncated.** `corpus.py:130` — *"a prefix
labelled as a whole body is worse than a hole"*. A README that said bodies are cut short would
describe a design the project deliberately refused.

**A fifth caveat rides in the same section without being one of the four**: a caller that
disconnects before the response generator's first step leaves no CSV row and no corpus entry. It is
named because a user reading a caveats section is exactly the reader who should know a call can
vanish, and it is written as *observed once, deliberately, and reported rather than closed* — which
is what the owner decided on 2026-08-20.

## Task 14 — the sweep, and what it found

**Done 2026-09-02, mechanically rather than by re-reading.** Thirty-eight elements of the old file
were listed and each grepped for in the new one. **Thirty-three are inherited. Five are gone, and
all five are deliberate:**

| Dropped | Why |
|---|---|
| The https repository URL, old line 3 | It points at the page the reader is already on. The `git@` clone URL **is** inherited, into Quick start, where it is a step rather than an ornament |
| The temporary corpus-tools warning | It said Phase 12 would replace the section. Phase 12 did; the content it protected is section 6 |
| The brief | Moved to `../../captures/original-project-description.md` by task 11 |
| "six phases" | Milestone 1 was **seven** |
| "158 tests" | Milestone 1's count, stale by 290 |

**The duplication the plan warned about did not happen.** Task 14 named the risk that the `docs/`
pointer lands twice, because it sits at the tail of the block task 13 moved wholesale. It appears
**once**, in section 10. Counted, not eyeballed.

## The two lines in Quick start that are not driven

**`uv tool install --force .` and `uv tool uninstall ilirium-llm-router` are written from `uv`'s own
`--help` and have not been run.** Everything else in Quick start was driven in Group B or C.

**The router is not currently installed as a `uv` tool** — `uv tool list` shows only `claude-swap`,
so Group B's install has since been removed. Driving these two would install software on the owner's
machine, which the plan required an explicit go-ahead for at task 3 and which is not a thing a
session arranges for itself.

**Raised for the owner rather than quietly shipped.** They are the two most likely lines in the file
to be wrong, because a path install is a snapshot and `uv tool upgrade` — the command a reader would
reach for first — is documented against a version specifier rather than a path.
