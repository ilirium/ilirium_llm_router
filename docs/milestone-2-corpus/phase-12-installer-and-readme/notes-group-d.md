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
